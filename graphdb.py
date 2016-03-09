import requests
import contextlib
from collections import defaultdict

import csv
# the lineterminator doesn't do anthing,
# but we can dream...
csv.register_dialect('nt', delimiter=' ', lineterminator='.\n')
from StringIO import StringIO

import graphdatatypes
from resourcegraphs import ResourceData, DataGraph
from graphattributes import Required, Optional, Linked


class SPARQLVariable(str):
	def __init__(self, val):
		self.rdf = "?"+str(val)

def mapJsonDataType(dtype):
	mapper = {
		"http://www.w3.org/2001/XMLSchema#string":
			graphdatatypes.XSDString,
		"http://www.w3.org/2001/XMLSchema#boolean":
			graphdatatypes.XSDBoolean,
		"http://www.w3.org/2001/XMLSchema#decimal":
			graphdatatypes.XSDDecimal,
		"http://www.w3.org/2001/XMLSchema#float":
			graphdatatypes.XSDFloat,
		"http://www.w3.org/2001/XMLSchema#double":
			graphdatatypes.XSDDouble,
		"http://www.w3.org/2001/XMLSchema#duration":
			graphdatatypes.XSDDuration,
		"http://www.w3.org/2001/XMLSchema#dateTime":
			graphdatatypes.XSDDatime,
		"http://www.w3.org/2001/XMLSchema#time":
			graphdatatypes.XSDTime,
		"http://www.w3.org/2001/XMLSchema#date":
			graphdatatypes.XSDDate,
		"http://www.w3.org/2001/XMLSchema#gYearMonth":
			graphdatatypes.XSDYearMonth,
		"http://www.w3.org/2001/XMLSchema#gYear":
			graphdatatypes.XSDYear,
		"http://www.w3.org/2001/XMLSchema#gMonthDay":
			graphdatatypes.XSDMonthDay,
		"http://www.w3.org/2001/XMLSchema#gDay":
			graphdatatypes.XSDDay,
		"http://www.w3.org/2001/XMLSchema#gMonth":
			graphdatatypes.XSDMonth,
		"http://www.w3.org/2001/XMLSchema#hexBinary":
			graphdatatypes.XSDHexBinary,
		"http://www.w3.org/2001/XMLSchema#base64Binary":
			graphdatatypes.XSDBase64Binary,
		"http://www.w3.org/2001/XMLSchema#anyURI":
			graphdatatypes.XSDAnyURI,
		"http://www.w3.org/2001/XMLSchema#QName":
			graphdatatypes.XSDQName,
		"http://www.w3.org/2001/XMLSchema#NOTATION":
			graphdatatypes.XSDNOTATION,
	}


def variableGenerator(r):
	vals = range(r)
	for v in vals:
		yield v

def make_subject_variable(q,var):
	if q.res is None:
		return q._replace(res=SPARQLVariable(var))
	else:
		return q

def make_object_variable(q,var):
	if q.val is None:
		return q._replace(val=SPARQLVariable(var))
	else:
		return q

def variablize_values(qset):
	out = DataGraph()
	varJar = variableGenerator(100)
	for q in qset:
		var  = varJar.next()
		if (isinstance(q,Required) or isinstance(q,Optional)):
			out.add(make_object_variable(q, var))
		elif isinstance(q,Linked):
			out.add(make_subject_variable(q, var))
		else:
			continue
	return out

def variablize_resource(qset):
	out = DataGraph()
	for q in qset:
		var  = "sbj"
		if (isinstance(q,Required) or isinstance(q,Optional)):
			out.add(make_subject_variable(q, var))
		elif isinstance(q,Linked):
			out.add(make_object_variable(q, var))
		else:
			continue
	return out

def write_statement(pattern):
	return "{0}{1}{2}.".format(
		pattern.res.rdf,pattern.att.rdf,pattern.val.rdf)

def optionalize_rule(rule):
	return "OPTIONAL{{{0}}}".format(rule)

def write_optional(pattern):
	return optionalize_rule(write_statement(pattern))

def jsonToTriples(sbj, stmts):
	"""pattern out. This is a better implementation
	of setify()."""
	triples = []
	for prd, obj_list in stmts.items():
		for obj_dict in obj_list:
			if obj_dict["type"] == "uri":
				addResourceData = ResourceData(
					graphdatatypes.URI(sbj),
					graphdatatypes.URI(prd),
					graphdatatypes.URI(obj_dict['value'])
					)
			else:
				if "datatype" in obj_dict:
					dtype = mapJsonDataType(obj_dict['datatype'])
				else:
					dtype = graphdatatypes.XSDString
				addResourceData = ResourceData(
					graphdatatypes.URI(sbj),
					graphdatatypes.URI(prd),
					dtype(obj_dict["value"])
					)
			triples.append(addResourceData)
	return DataGraph(triples)

def parseNTriples(queryResults):
	rdr = csv.reader(StringIO(queryResults), 'nt')
	resultGraphs = defaultdict(DataGraph)
	for row in rdr:
		resultGraphs[row[0]].add(ResourceData(*row[:3]))

def parseSubGraphs(queryResults):
	resultGraphs = dict()
	for sbj in queryResults:
		resultGraphs[sbj] = jsonToTriples(sbj, queryResults[sbj])
	return resultGraphs

defaultGraph = "<http://vitro.mannlib.cornell.edu/default/vitro-kb-2>"

class GraphInterface(object):
	def __init__(self):
		self.constructTemplate = u"CONSTRUCT{{{0}}}WHERE{{{1}}}"
		self.insertTemplate = u"INSERTDATA{{GRAPH{0}{{{1}}}}}"
		self.deleteTemplate = u"DELETEDATA{{GRAPH{0}{{{1}}}}}"

	def fetch(self, pattern):
		rqrd_cnst = ""
		rqrd_where = ""
		optl_cnst = ""
		optl_where = ""
		pattern = variablize_values(pattern)
		for p in pattern:
			if isinstance(p,Required):
				stmt = write_statement(p)
				rqrd_cnst += stmt
				rqrd_where += stmt
			elif isinstance(p, Optional):
				stmt = write_statement(p)
				optl_cnst += stmt
				optl = write_optional(p)
				optl_where += optl
		construct_pattern = rqrd_cnst + optl_cnst
		where_pattern = rqrd_where + optl_where
		qbody = self.constructTemplate.format(construct_pattern, where_pattern)
		resp = self.get(qbody)
		return resp

	def fetchAll(self, pattern):
		"""
		Currently does not support optional queries,
		due to performance concerns.
		"""
		rqrd_cnst = ""
		rqrd_where = ""
		pattern = variablize_values(pattern)
		pattern = variablize_resource(pattern)
		for p in pattern:
			if isinstance(p,Required):
				stmt = write_statement(p)
				rqrd_cnst += stmt
				rqrd_where += stmt
		construct_pattern = rqrd_cnst
		where_pattern = rqrd_where
		qbody = self.constructTemplate.format(construct_pattern, where_pattern)
		resp = self.get(qbody)
		return resp

	def identifyAll(self,pattern):
		rqrd_cnst = "?sbj<http://www.w3.org/2000/01/rdf-schema#label>?label."
		rqrd_where = "?sbj<http://www.w3.org/2000/01/rdf-schema#label>?label."
		pattern = variablize_values(pattern)
		pattern = variablize_resource(pattern)
		for p in pattern:
			if isinstance(p,Required):
				stmt = write_statement(p)
				rqrd_where += stmt
		construct_pattern = rqrd_cnst
		where_pattern = rqrd_where
		qbody = self.constructTemplate.format(construct_pattern,where_pattern)
		resp = self.get(qbody)
		return resp

	def get(self,qbody):
		endpoint = "http://localhost:8082/VIVO/query"
		payload = {'output': 'nt'}
		payload['query'] = qbody
		with contextlib.closing(requests.get(endpoint, params=payload)) as resp:
			if resp.status_code == 200:
				return parseSubGraphs(resp.json())
			else:
				return None

	def update(self, data, action, graph=defaultGraph):
		postPattern = ""
		for triple in data:
			postPattern += write_statement(triple)
		if action == "add":
			pbody = self.insertTemplate.format(graph,postPattern)
		elif action == "remove":
			pbody = self.deleteTemplate.format(graph,postPattern)
		else:
			raise Exception("Unrecognized action")
		resp = self.post(pbody)
		return resp

	def post(self,pbody):
		endpoint ="http://localhost:8080/rab/api/sparqlUpdate"
		payload = {
					'email': "vivo_root@brown.edu",
					'password': "goVivo"
					}
		payload['update'] = pbody
		with contextlib.closing(requests.post(endpoint, data=payload)) as resp:
			if resp.status_code == 200:
				return resp
			else:
				return None

