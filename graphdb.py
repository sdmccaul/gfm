import requests
import contextlib
from collections import defaultdict

import re
from StringIO import StringIO

import graphdatatypes
from graphdata import ResourceData, DataGraph
from graphattributes import Required, Optional, Linked


def write_statement(pattern):
	return "{0}{1}{2}.".format(
		pattern.res,pattern.att,pattern.val)

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
				triples.append(
					tuple([qualifyURI(sbj),
						qualifyURI(prd),
						qualifyURI(obj_dict['value'])
						])
					)
			else:
				datatype = obj_dict.get("datatype")
				if datatype:
					val = qualifyData(obj_dict["value"], datatype)
				else:
					val = obj_dict["value"]
				triples.append(
					tuple([graphdatatypes.URI(sbj),
						graphdatatypes.URI(prd),
						val
						])
					)
	return set(triples)

def parseNTriples(queryResults):
	resultGraphs = defaultdict(DataGraph)
	f = StringIO(queryResults)
	for line in f:
		res, att, val = re.findall(
			"<[^>\"]*>\W|\".*\"\^\^<.*>\W\.\n|\".*\"\W\.\n", line)
		resultGraphs[res.rstrip()].add(ResourceData(
			res.rstrip(), att.rstrip(), val.rstrip(' .\n')))
	return resultGraphs

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

	def fetch(self, query):
		rqrd_cnst = ""
		rqrd_where = ""
		optl_cnst = ""
		optl_where = ""
		for q in query:
			if isinstance(q,Required):
				stmt = write_statement(q)
				rqrd_cnst += stmt
				rqrd_where += stmt
			elif isinstance(q, Optional):
				stmt = write_statement(q)
				optl_cnst += stmt
				optl = write_optional(q)
				optl_where += optl
		construct_pattern = rqrd_cnst + optl_cnst
		where_pattern = rqrd_where + optl_where
		qbody = self.constructTemplate.format(construct_pattern, where_pattern)
		resp = self.get(qbody)
		return resp

	def fetchAll(self, query):
		"""
		Currently does not support optional queries,
		due to performance concerns.
		"""
		rqrd_cnst = ""
		rqrd_where = ""
		for q in query:
			if isinstance(q,Required):
				stmt = write_statement(q)
				rqrd_cnst += stmt
				rqrd_where += stmt
		construct_pattern = rqrd_cnst
		where_pattern = rqrd_where
		qbody = self.constructTemplate.format(construct_pattern, where_pattern)
		resp = self.get(qbody)
		return resp

	def identifyAll(self, query):
		rqrd_cnst = "?sbj<http://www.w3.org/2000/01/rdf-schema#label>?label."
		rqrd_where = "?sbj<http://www.w3.org/2000/01/rdf-schema#label>?label."
		for q in query:
			if isinstance(q,Required):
				stmt = write_statement(q)
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
				return parseNTriples(resp.text)
			else:
				raise Exception("Failed get! {0}".format(resp.text))

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
				raise Exception("Failed post! {0}".format(resp.text))

