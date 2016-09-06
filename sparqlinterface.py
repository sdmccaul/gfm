import requests
import rdflib
import contextlib
from collections import defaultdict

def variableGenerator(r):
	vals = range(r)
	for v in vals:
		yield "?"+str(v)

def make_subject_variable(triple,var):
	if triple[0] is None:
		return (var, triple[1], triple[2])
	else:
		return triple

def make_object_variable(triple,var):
	if triple[2] is None:
		return (triple[0], triple[1], var)
	else:
		return triple

def variablize_resource(triples):
	out = list()
	for triple in triples:
		var  = "?sbj"
		out.append(make_subject_variable(triple, var))
	return out

def variablize_values(triples):
	out = list()
	varJar = variableGenerator(100)
	for triple in triples:
		var  = varJar.next()
		out.append(make_object_variable(triple, var))
	return out

def write_statement(triple):
	return "{0}{1}{2}.".format(*triple)

def optionalize_statement(triple):
	return "OPTIONAL{{{0}}}".format(triple)

def write_optional(triple):
	return optionalize_statement(write_statement(triple))

def _XSD_encode_uri(value):
	try:
		return "<"+ value +">"
	except:
		raise ValueError("XSD encoding of URI failed")

def _XSD_encode_string(value):
	try:
		# escaped_quotes = value.replace('"', '\"')
		return '"'+ value +'"'
	except:
		raise ValueError("XSD encoding of string failed")

def _XSD_encode_dateTime(value):
	try:
		return '"'+ value +'"^^<http://www.w3.org/2001/XMLSchema#dateTime>'
	except:
		raise ValueError("XSD encoding of dateTime failed")

def update_triple(triple, pos, func):
	tlist = list(triple)
	mapped = func(tlist.pop(pos))
	tlist.insert(pos,mapped)
	return tuple(tlist)

class SPARQLQuery(object):
	def __init__(self, resource):
		self.XSD_formats = {
			'uri': _XSD_encode_uri,
			'anyURI': _XSD_encode_uri,
			'string': _XSD_encode_string,
			'dateTime': _XSD_encode_dateTime,
			'datetime': _XSD_encode_dateTime
		}
		self.triples = resource.to_triples()
		self.schema = resource.schema
		self.required = self.schema.required
		self.optional = self.schema.optional
		self.XSD_mappings = { uri: self.XSD_formats[datatype]
								for uri, datatype
									in self.schema.datatypes.items() }

	def write_query_triples(self, predicateFilter):
		triples = [ t for t in self.triples
					if t[1] in predicateFilter ]
		triples = [ update_triple(t, 2, self.XSD_mappings[t[1]])
						if t[2] else t for t in triples ]
		triples = [ update_triple(t, 0, _XSD_encode_uri)
						if t[0] else t for t in triples ]
		triples = [ update_triple(t, 1, _XSD_encode_uri)
						for t in triples ]
		triples = variablize_resource(triples)
		triples = variablize_values(triples)
		return triples


def take_no_action(val):
	return val

def convert_datetime_to_string(val):
	return val.isoformat()

class RDFLibEndpoint(object):
	def __init__(self, endpoint):
		graph = rdflib.ConjunctiveGraph('SPARQLStore')
		graph.open(endpoint)
		self.graph = graph
		self.result_mappings = {
			'uri': take_no_action,
			'string': take_no_action,
			'dateTime': convert_datetime_to_string,
			'date': convert_datetime_to_string
		}

	def query(self, queryText):
		return self.graph.query(queryText)

	def close(self):
		self.graph.close()

	def convert_results_to_triples(self, rdflibResults, datatypeMap):
		mappings = { uri: self.result_mappings[datatype]
						for uri, datatype in datatypeMap.items() }
		triples = [ ( t[0].toPython(), t[1].toPython(), t[2].toPython() )
					for t in rdflibResults ]
		converted = [ update_triple(triple, 2, mappings[triple[1]])
						for triple in triples ]
		return converted


def build_construct_query(required, optional):
	constructTemplate = u"CONSTRUCT{{{0}}}WHERE{{{1}}}"
	construct = ""
	where = ""
	for triple in required:
		stmt = write_statement(triple)
		construct += stmt
		where += stmt
	if optional:
		for triple in optional:
			stmt = write_statement(triple)
			construct += stmt
			optl = write_optional(triple)
			where += optl
	qbody = constructTemplate.format(construct, where)
	return qbody

def convert_triples_to_dicts(triples):
	dict_of_dicts = defaultdict(lambda : defaultdict(list))
	for triple in triples:
		dict_of_dicts[triple[0]][triple[1]].append(triple[2])
	out = []
	for uri, data in dict_of_dicts.items():
		res = {}
		res.update(data)
		res['@uri'] = uri
		out.append(res)
	return out

class SPARQLInterface(object):
	def __init__(self, endpoint_address, queryLib):
		if queryLib == 'rdflib':
			self.endpoint = RDFLibEndpoint(endpoint_address)
		self.endpoint_address = endpoint_address

	def construct(self, resource, optional=True):
		query = SPARQLQuery(resource)
		required = query.write_query_triples(query.required)
		if optional:
			optional = query.write_query_triples(query.optional)
		else:
			optional = None
		qbody = build_construct_query(required, optional)
		results = self.endpoint.query(qbody)
		triples = self.endpoint.convert_results_to_triples(
					results, query.schema.datatypes)
		dataList = convert_triples_to_dicts(triples)
		return dataList