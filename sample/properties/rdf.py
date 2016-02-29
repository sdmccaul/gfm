from datasets import Datum
from graphdatatypes import URI, objectProperty

@objectProperty
def rdfType(res, val):
	return Datum(res,URI('http://www.w3.org/1999/02/22-rdf-syntax-ns#type'), val)