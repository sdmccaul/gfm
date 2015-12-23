import rdflib
from rdflib import RDFS, ConjunctiveGraph
from rdflib.query import ResultException

from vdm.backend import FusekiGraph


vstore = FusekiGraph('http://localhost:8082/VIVO/query')


class Construct(object):
	def __init__(c_clause, w_clause):
		self.template = u"""
			CONSTRUCT {{ {0} }}
			WHERE {{ 
				{1}
			}}"""
		self.construct_pattern = c_clause
		self.where_pattern = w_clause
		self.body = self.template.format(c_clause,w_clause)

class Select(object):
	def __init__(s_clause, w_clause):
		self.template = u"""
			SELECT {{ {0} }}
			WHERE {{ 
				{1}
			}}"""
		self.select_pattern = s_clause
		self.where_pattern = w_clause
		self.body = self.template.format(s_clause,w_clause)

class Insert(object):
	def __init__(i_data):
		self.template = u"""
			INSERT DATA {{
				{{ {0} }}
			}}"""
		self.select_pattern = s_clause
		self.where_pattern = w_clause
		self.body = self.template.format(s_clause,w_clause)

class Delete(object):
	pass

def write_query_triple(s, p, o):
		if s is None:
			s="?subject"
		if p is None:
			p="?predicate"
		if o is None:
			o="?object"
		outstr = "{0} {1} {2} .".format(s,p,o)
		return outstr

class SparqlInterface(object):
	def __init__(self):
		self.construct_template = u"""
			CONSTRUCT {{ {construct_pattern} }}
			WHERE {{ 
				{where_pattern}
			}}
			LIMIT 20
			"""
		self.describe_template= u"""
			CONSTRUCT {{ <{uri}> ?p ?o . }}
			WHERE {{ 
				<{uri}> ?p ?o .
			}}
			"""
		self.all_template = u"""
			CONSTRUCT {{ ?subj rdf:type {rdfClass} . }}
			WHERE {{ 
				?subj rdf:type {rdfClass} .
			}}
			LIMIT 20
			"""

	def construct(self, construct_triples, where_triples):
		construct_pattern = ""
		where_pattern = ""
		for c in construct_triples:
			construct_pattern += write_query_triple(*c)
		for w in where_triples:
			where_pattern += write_query_triple(*w)
		rq = self.construct_template.format(
				construct_pattern=construct_pattern,
				where_pattern=where_pattern)
		try:
			results = vstore.query(rq)
		except ResultException:
			return list()
		out = [ r for r in results ]
		return out

	def describe(self, uri):
		rq = self.describe_template.format(uri=uri)
		try:
			results = vstore.query(rq)
		except ResultException:
			return list()
		out = [ r for r in results ]
		return out

	def all(self, rdfClass):
		rq = self.all_template.format(rdfClass=rdfClass)
		try:
			results = vstore.query(rq)
		except ResultException:
			return list()
		out = [ r for r in results ]
		return out
