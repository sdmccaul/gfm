import rdflib
from rdflib import RDFS, ConjunctiveGraph
from rdflib.query import ResultException

from vdm.backend import FusekiGraph


vstore = FusekiGraph('http://localhost:8082/VIVO/query')

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
		self.construct_template = u"CONSTRUCT {{ {construct_pattern} }} WHERE {{ {where_pattern} }} LIMIT 20"

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
		return vstore.query(rq)