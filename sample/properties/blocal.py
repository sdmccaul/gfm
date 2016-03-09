from resourcegraphs import ResourceData
from graphdatatypes import URI, objectProperty, dataProperty

@dataProperty
def shortId(res=None, val=None):
	return ResourceData(res,URI('http://vivo.brown.edu/ontology/vivo-brown/shortId'), val)

@dataProperty
def degreeDate(res=None, val=None):
	return ResourceData(res,URI('http://vivo.brown.edu/ontology/vivo-brown/degreeDate'), val)