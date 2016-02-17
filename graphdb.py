import requests
import contextlib

from datasets import Datum, DataSet, Required, Optional, Linked


def variableGenerator(r):
	vals = range(r)
	for v in vals:
		yield "?"+str(v)

def qualify(inStr):
	if inStr is None or inStr.startswith("?"):
		return inStr
	else:
		return "<"+ inStr + ">"

def sparvar(inStr):
	return "?" + inStr

def qualify_rule(s,p,o):
	return qualify(s), qualify(p), qualify(o)

def make_subject_variable(q,var):
	if q.res is None:
		return q._replace(res=var)
	else:
		return q

def make_object_variable(q,var):
	if q.val is None:
		return q._replace(val=var)
	else:
		return q

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

def variablize(qset):
	out = DataSet([])
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

def write_statement(rule):
	return write_rule(*(qualify_rule(*(rule))))

def write_optional(rule):
	return optionalize_rule(write_statement(rule))

class QueryInterface(object):
	def __init__(self):
		self.construct_template = u"CONSTRUCT{{{0}}}WHERE{{{1}}}"
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

	def find(self, pattern):
		rqrd_cnst = ""
		rqrd_where = ""
		optl_cnst = ""
		optl_where = ""
		pattern = variablize(pattern)
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
		qbody = self.construct_template.format(construct_pattern, where_pattern)

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

	def query(qbody):
		endpoint = "http://localhost:8082/VIVO/query"
		payload = {'output': 'json'}
		payload['query'] = qbody
		with contextlib.closing(requests.get(endpoint, params=payload)) as resp:
			if resp.status_code == 200:
				return resp.json()
			else:
				raise "Fuseki endpoint returned error!"