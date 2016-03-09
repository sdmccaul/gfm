from resourcegraphs import ResourceData
from graphdatatypes import URI, objectProperty

@objectProperty
def rdfType(res, val):
	return ResourceData(res,URI('http://www.w3.org/1999/02/22-rdf-syntax-ns#type'), val)