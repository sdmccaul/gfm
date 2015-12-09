import rdflib
from rdflib import RDFS, ConjunctiveGraph
from rdflib.query import ResultException

from vdm.backend import FusekiGraph

sparql = FusekiGraph('http://localhost:8082/VIVO/query')
