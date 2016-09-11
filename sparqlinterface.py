from collections import defaultdict

import rdflib

import requests
import re
import StringIO
import contextlib
import xml.etree.ElementTree as ET
import json
import urllib


def variableGenerator(r):
	vals = range(r)
	for v in vals:
		yield "?"+str(v)

def _variabalize_value(val, var):
	if val is None:
		return var
	else:
		return val

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

def update_triple(triple, pos, func, *params):
	tlist = list(triple)
	mapped = func(tlist.pop(pos), *params)
	tlist.insert(pos,mapped)
	return tuple(tlist)

class SPARQLRequest(object):
	def __init__(self, resource):
		self.XSD_formats = {
			'uri': _XSD_encode_uri,
			'anyURI': _XSD_encode_uri,
			'string': _XSD_encode_string,
			'dateTime': _XSD_encode_dateTime,
			'datetime': _XSD_encode_dateTime
		}
		self.triples = resource.to_triples()
		self.named_graph = _XSD_encode_uri(
								resource.collection.named_graph)
		self.schema = resource.schema
		self.required = self.schema.required
		self.optional = self.schema.optional
		self.XSD_mappings = { uri: self.XSD_formats[datatype]
								for uri, datatype
									in self.schema.datatypes.items() }
		self.sparql_variables = variableGenerator(100)

	def write_construct_triples(self, predicateFilter):
		triples = [ t for t in self.triples
					if t[1] in predicateFilter ]
		triples = [ update_triple(t, 2, self.XSD_mappings[t[1]])
						if t[2] else t for t in triples ]
		triples = [ update_triple(t, 0, _XSD_encode_uri)
						if t[0] else t for t in triples ]
		triples = [ update_triple(t, 1, _XSD_encode_uri)
						for t in triples ]
		triples = [ update_triple(t, 0, _variabalize_value, "?sbj")
						for t in triples ]
		triples = [ update_triple(t, 2, _variabalize_value,
						self.sparql_variables.next())
							for t in triples ]
		return triples

	def write_update_triples(self):
		triples = [ update_triple(t, 2, self.XSD_mappings[t[1]])
						if t[2] else t for t in self.triples ]
		triples = [ update_triple(t, 0, _XSD_encode_uri)
						if t[0] else t for t in triples ]
		triples = [ update_triple(t, 1, _XSD_encode_uri)
						for t in triples ]
		return triples


def take_no_action(val):
	return val

def convert_datetime_to_string(val):
	return val.isoformat()

class RdfLibSparqlApi(object):
	def __init__(self, query_endpoint, update_endpoint):
		qgraph = rdflib.ConjunctiveGraph('SPARQLquery')
		qgraph.open(query_endpoint)
		ugraph = rdflib.ConjunctiveGraph('SPARQLupdate')
		ugraph.open(update_endpoint)
		self.query_endpoint = qgraph
		self.update_endpoint = ugraph
		self.result_mappings = {
			'uri': take_no_action,
			'string': take_no_action,
			'dateTime': convert_datetime_to_string,
			'date': convert_datetime_to_string
		}

	def query(self, queryText):
		return self.query_graph.query(queryText)

	def close(self):
		self.query_graph.close()
		self.update_endpoint.close()

	def convert_results_to_triples(self, rdflibResults, datatypeMap):
		mappings = { uri: self.result_mappings[datatype]
						for uri, datatype in datatypeMap.items() }
		triples = [ ( t[0].toPython(), t[1].toPython(), t[2].toPython() )
					for t in rdflibResults ]
		converted = [ update_triple(triple, 2, mappings[triple[1]])
						for triple in triples ]
		return converted

def parseRDFXMLString(stringData):
	# Ugly braces due to namespaced data
	# A better fix out there; ie, request options?
	root = ET.fromstring(stringData) 
	triples = [ (sbj.get(
					'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about'
				),
				prd.tag.replace('{','').replace('}',''),
				prd.get(
					'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource'
				)
				if
					'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource'
						in prd.attrib
				else prd.text)
					for sbj in root
						for prd in sbj ]
	return triples

# def parseNTriplesString(stringData):
# 	triples = []
# 	for line in f:
# 		s, p, o = re.findall(
# 			"<[^>\"]*>\W|\".*\"\^\^<.*>\W\.\n|\".*\"\W\.\n", line)
		
# 		triples.append(
# 			(s.rstrip(), p.rstrip(), o.rstrip(' .\n'))
# 			)
# 	return triples

def parseJSONString(stringData):
	jdata = json.loads(stringData)
	triples = [ (s, p, o['value'])
				for s, v in jdata.items()
					for p, z in v.items()
						for o in z ]
	return triples

class HttpSparqlApi(object):
	def __init__(self, query_endpoint, update_endpoint):
		self.query_endpoint = query_endpoint
		self.update_endpoint = update_endpoint

	def query(self, qbody):
		# Output options:
		# 'nt', 'xml', 'json'
		payload = {
			'output': 'json',
			'query': qbody
		}
		resp = requests.get(self.query_endpoint, params=payload)
		if resp.status_code == 200:
			return resp
		else:
			raise Exception("Failed get! {0}".format(resp.text))

	def update(self, pbody):
		payload = {
			'email': "vivo_root@brown.edu",
			'password': "goVivo",
			'update': pbody
		}
		data = urllib.urlencode(payload)
		with contextlib.closing(
			urllib.urlopen(self.update_endpoint, data)) as resp:
			return resp.code

	def convert_results_to_triples(self, requestsResp, datatypeMap):
		triples = parseJSONString(requestsResp.text)
		return triples

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

def build_insert_delete_query(insert=None,insert_graph=None,
								delete=None,delete_graph=None):
	delete_template = u"DELETEDATA{{GRAPH{0}{{{1}}}}}"
	insert_template = u"INSERTDATA{{GRAPH{0}{{{1}}}}}"
	pbody = ""
	if delete and delete_graph:
		delete_triples = ""
		for triple in delete:
			delete_triples += write_statement(triple)
		delete_body = delete_template.format(
										delete_graph, delete_triples)
		pbody += delete_body
		if insert and insert_graph:
			pbody += ";"
	if insert and insert_graph:
		insert_triples = ""
		for triple in insert:
			insert_triples += write_statement(triple)
		insert_body = insert_template.format(
										insert_graph, insert_triples)
		pbody += insert_body
	return pbody

def convert_triples_to_dicts(triples):
	dict_of_dicts = defaultdict(lambda : defaultdict(list))
	for triple in triples:
		dict_of_dicts[triple[0]][triple[1]].append(triple[2])
	return [ { uri: data }
				for uri, data in dict_of_dicts.items() ]

def set_difference(list1, list2):
	s1 = set(list1)
	s2 = set(list2)
	out1 = s1 - s2
	out2 = s2 - s1
	return (out1, out2)

class SPARQLInterface(object):
	def __init__(self, query_endpoint, update_endpoint, sparql_api):
		if sparql_api == 'rdflib':
			self.endpoint = RdfLibSparqlApi(
								query_endpoint, update_endpoint)
		elif sparql_api == 'http' or sparql_api == 'HTTP':
			self.endpoint = HttpSparqlApi(
								query_endpoint, update_endpoint)

	def construct(self, resource, optional=True):
		query = SPARQLRequest(resource)
		required = query.write_construct_triples(query.required)
		if optional:
			optional = query.write_construct_triples(query.optional)
		else:
			optional = None
		qbody = build_construct_query(required, optional)
		results = self.endpoint.query(qbody)
		triples = self.endpoint.convert_results_to_triples(
					results, query.schema.datatypes)
		dataList = convert_triples_to_dicts(triples)
		return dataList

	def update(self, insert=None, delete=None):
		# https://wiki.duraspace.org/display/VIVOARC/The+SPARQL+Update+API#TheSPARQLUpdateAPI-EnablingtheAPI
		if insert:
			insert_query = SPARQLRequest(insert)
			insert_data = insert_query.write_update_triples()
			insert_graph = insert_query.named_graph
		else:
			insert_data = None
			insert_graph = None
		if delete:
			delete_query = SPARQLRequest(delete)
			delete_data = delete_query.write_update_triples()
			delete_graph = delete_query.named_graph
		else:
			delete_data = None
			delete_graph = None
		if insert_data and delete_data:
			insert_data, delete_data = set_difference(
										insert_data, delete_data)
		pbody = build_insert_delete_query(
					insert_data, insert_graph,
					delete_data, delete_graph)
		resp = self.endpoint.update(pbody)
		return resp