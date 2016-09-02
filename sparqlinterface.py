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


def querify(res):
	triples = res.to_query()
	uri_props = [ uri for uri in res.schema.query if res.schema.query[uri]['datatype'] == 'uri' ]
	print uri_props
	out = bracket_subjects(triples)
	out = bracket_objects(out, uri_props)
	out = bracket_predicates(out)
	out = variablize_resource(out)
	out = variablize_values(out)
	return out

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

class SPARQLInterface(object):
	def __init__(self, endpoint):
		graph = ConjunctiveGraph('SPARQLStore')
		graph.open(endpoint)
		self.graph = graph
		self.insertTemplate = u"INSERTDATA{{GRAPH{0}{{{1}}}}}"
		self.deleteTemplate = u"DELETEDATA{{GRAPH{0}{{{1}}}}}"

	def construct(self, qres, optional=True):
		required = qres.required
		if optional:
			optional = qres.optional
		else:
			optional = None
		qbody = build_construct_query(required, optional)
		results = self.graph.query(qbody)
		triples = convert_rdflib_to_triples(results)
		dictified = convert_triples_to_dicts(triples)
		return dictified

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

	def get(self, query):
	    results = self.graph.query(query)
	    resp = defaultdict(lambda : defaultdict(list))
	    for row in results:
	    	resp[row[0].toPython()][row[1].toPython()].append(row[2].toPython())
	    return ou

	def update(self, data, action):
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