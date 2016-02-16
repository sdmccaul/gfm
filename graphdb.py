import requests
import contextlib

from datasets import Datum, DataSet


def variableGenerator(r):
	vals = range(r)
	for v in vals:
		yield v

def qualify(inStr):
	if inStr is None or inStr.startswith("?"):
		return inStr
	else:
		return "<"+ inStr + ">"

def sparvar(inStr):
	return "?" + inStr

def qualify_rule(s,p,o):
	return qualify(s), qualify(p), qualify(o)

def make_subject_variable(var,s,p,o):
	if s is None:
		return sparvar(var),p,o
	else:
		return s,p,o

def make_object_variable(var,s,p,o):
	if o is None:
		return s,p,sparvar(var)
	else:
		return s,p,o

def write_rule(s,p,o):
	return "{0}{1}{2}.".format(s,p,o)

def optionalize_rule(rule):
	return "OPTIONAL{{{0}}}".format(rule)

def sparqlify(qset):
	if isinstance(qset, FindQuery):
		pass
	elif isinstance(qset, AllQuery):
		pass
	else:
		raise "Unrecognized query"

class QueryInterface(object):
	def __init__(self):
		self.construct_template = u"CONSTRUCT{{{construct_pattern}}}WHERE{{{where_pattern}}}"
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

	def find(self, required, filters=None, optional=None):
		construct_pattern = ""
		where_pattern = ""
		if filters:
			for e, f in enumerate(filters):
				where_pattern += write_rule(
					*(qualify_rule(*(make_subject_variable(str(e), *f))))
					)
		for e, r in enumerate(required):
			pattern = write_rule(
				*(qualify_rule(*(make_object_variable(str(e), *r))))
				)
			construct_pattern += pattern
			where_pattern += pattern
		if optional:
			for e, o in enumerate(optional):
				pattern = write_rule(
					*(qualify_rule(*(make_object_variable(str(e), *o))))
				)
				construct_pattern += pattern
				where_pattern += optionalize_rule(pattern)
		return construct_pattern, where_pattern

	def all(self, required, filters=None, optional=None):
		construct_pattern = ""
		where_pattern = ""
		if filters:
			for e, f in enumerate(filters):
				where_pattern += write_rule(
					*(qualify_rule(*(make_object_variable("sbj",
						*(make_subject_variable(str(e), *f)))))
					))
		for e, r in enumerate(required):
			pattern = write_rule(
				*(qualify_rule(*(make_subject_variable("sbj",
					*(make_object_variable(str(e), *r)))))
				))
			construct_pattern += pattern
			where_pattern += pattern
		if optional:
			for e, o in enumerate(optional):
				pattern = write_rule(
					*(qualify_rule(*(make_subject_variable("sbj",
						*(make_object_variable(str(e), *o)))))
				))
				construct_pattern += pattern
				where_pattern += optionalize_rule(pattern)
		return construct_pattern, where_pattern


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

	def query(qset):
		endpoint = "http://localhost:8082/VIVO/query"
		payload = {'output': 'json'}
		qbody = sparqlify(qset)
		payload['query'] = qbody
		with contextlib.closing(requests.get(endpoint, params=payload)) as resp:
			if resp.status_code == 200:
				return resp.json()
			else:
				raise "Fuseki endpoint returned error!"