import rdflib
from rdflib import RDFS, ConjunctiveGraph
from rdflib.query import ResultException

from vdm.backend import FusekiGraph
from datasets import Datum, DataSet

vstore = FusekiGraph('http://localhost:8082/VIVO/query')

def write_object_query(s,p,o):
	outstr = "<{0}> <{1}> {2} .".format(s,p,o)
	return outstr

def write_subject_object_query(s,p,o):
	outstr = "{0} <{1}> {2} .".format(s,p,o)
	return outstr

def write_rule(s,p,o):
	outstr = "<{0}> <{1}> <{2}> .".format(s,p,o)
	return outstr

def write_query_triple(s, p, o):
		if s is None:
			s="?subject"
		if p is None:
			p="?predicate"
		if o is None:
			o="?object"
		outstr = "{0} <{1}> <{2}> .".format(s,p,o)
		return outstr

def convert_rdflib_to_data(results):
	data = [ Datum(s.toPython(), p.toPython(), o.toPython())
				for s,p,o in results ]
	return data

def make_subject_variable(query):
	return ("?sbj", query[1], query[2])

def make_object_variable(query, var):
	if query[2] is None:
		return (query[0], query[1], var)
	else:
		return (*query)

def make_all_query_from_dataset(dset):
	out = [ make_subject_variable(make_object_variable(d, e))
				for e,d in enumerate(dset) ]

def write_required(query):
	return "<> <> <> ."

class SparqlInterface(object):
	def __init__(self):
		self.construct_template = u"""
			CONSTRUCT {{ {construct_pattern} }}
			WHERE {{ 
				{where_pattern}
			}}
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
		self.find_template= u"""
			CONSTRUCT {{ <{uri}> ?p ?o . }}
			WHERE {{ 
				<{uri}> ?p ?o .
			}}
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
		out = [ (s.toPython(), p.toPython(), o.toPython())
					for s,p,o in results ]
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

	def find(self, queryset):
		pattern = ""
		for e, q in enumerate(queryset):
			if q[2] is None:
				qvar = "?" + str(e)
				pattern += write_object_query(q[0], q[1], qvar)
			else:
				pattern += write_rule(*q)
		rq = self.construct_template.format(
				construct_pattern=pattern,
				where_pattern=pattern)
		data = self.query_endpoint(rq)
		return data

	def all(self, queryset):
		pattern = ""
		for e, q in enumerate(queryset):
			if q[2] is None:
				qvar = "?" + str(e)
				pattern += write_subject_object_query("?sbj", q[1], qvar)
			else:
				pattern += write_rule("?sbj", q[1], q[2])
		rq = self.construct_template.format(
				construct_pattern=pattern,
				where_pattern=pattern)
		data = self.query_endpoint(rq)
		return data

	def query_endpoint(self, request):
		try:
			results = vstore.query(request)
			return DataSet(convert_rdflib_to_data(results))
		except ResultException:
			return DataSet()