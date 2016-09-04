import requests
import rdflib
import contextlib
from collections import defaultdict

class RDFLibData(object):
	def __init__(self, resource):
		self.triples = resource.to_triples()
		self.schema = resource.schema
		self.required = self.schema.required
		self.optional = self.schema.optional
		self.conversions = {
			'uri': take_no_action,
			'string': take_no_action,
			'dateTime': convert_datetime_to_string,
			'date': convert_datetime_to_string
		}
		self.mapper = { uri: self.conversions[self.schema.datatypes[uri]] 
						for uri in self.schema.datatypes }

	def construct_triples(self, sublist):
		triples = [ t for t in self.triples if t[1] in sublist ]
		triples = [ update_triple(
					t, 2, self.schema.XSD_encodings[t[1]])
				if t[2] else t for t in triples ]
		triples = [ bracket_uris(t, 0)
				if t[0] else t for t in triples ]
		triples = [ bracket_uris(t, 1) for t in triples ]
		triples = variablize_resource(triples)
		triples = variablize_values(triples)
		return triples

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

def variablize_values(triples):
	out = list()
	varJar = variableGenerator(100)
	for triple in triples:
		var  = varJar.next()
		out.append(make_object_variable(triple, var))
	return out

def variablize_resource(triples):
	out = list()
	for triple in triples:
		var  = "?sbj"
		out.append(make_subject_variable(triple, var))
	return out

def bracket_subjects(triples):
	return [ bracket_uris(t, 0) if t[0] else t for t in triples]

def bracket_predicates(triples):
	return [ bracket_uris(t, 1) if t[1] else t for t in triples]

def bracket_objects(triples, datatypes):
	return [ bracket_uris(t, 2) if t[2] and t[1] in datatypes else t for t in triples]

def update_triple(triple, pos, func):
	tlist = list(triple)
	mapped = func(tlist.pop(pos))
	tlist.insert(pos,mapped)
	return tuple(tlist)

def bracket_uris(triple, pos):
	tlist = list(triple)
	mapped = "<" + tlist.pop(pos) + ">"
	tlist.insert(pos,mapped)
	return tuple(tlist)

def write_statement(triple):
	return "{0}{1}{2}.".format(*triple)

def optionalize_statement(triple):
	return "OPTIONAL{{{0}}}".format(triple)

def write_optional(triple):
	return optionalize_statement(write_statement(triple))

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

def convert_rdflib_to_triples(response, conversion_map):
	triples = [ ( t[0].toPython(), t[1].toPython(), t[2].toPython() )
				for t in response ]
	# for t in triples:
	# 	print t, type(t)
	# 	for a in t:
	# 		print "\t",a, type(a)
	converted = [ update_triple(triple, 2, conversion_map[triple[1]])
					for triple in triples ]
	return converted

def take_no_action(val):
	return val

def convert_datetime_to_string(val):
	return val.isoformat()

# class RDFLibSchema(object):
# 	def __init__(self):


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
	def __init__(self, endpoint):
		graph = rdflib.ConjunctiveGraph('SPARQLStore')
		graph.open(endpoint)
		self.graph = graph
		self.insertTemplate = u"INSERTDATA{{GRAPH{0}{{{1}}}}}"
		self.deleteTemplate = u"DELETEDATA{{GRAPH{0}{{{1}}}}}"
		self.XSD_formats = {
			'uri': _XSD_encode_uri,
			'anyURI': _XSD_encode_uri,
			'string': _XSD_encode_string,
			'dateTime': _XSD_encode_dateTime,
			'datetime': _XSD_encode_dateTime
		}

	def close(self):
		self.graph.close()

	def construct(self, resource, optional=True):
		qres = RDFLibData(resource)
		required = qres.construct_triples(qres.required)
		if optional:
			optional = qres.construct_triples(qres.optional)
		else:
			optional = None
		qbody = build_construct_query(required, optional)
		results = self.graph.query(qbody)
		triples = convert_rdflib_to_triples(results, qres.mapper)
		dictified = convert_triples_to_dicts(triples)
		return dictified