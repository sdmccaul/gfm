from graphdata import ResourceData
from graphdatatypes import URI, objectProperty, dataProperty

@dataProperty
def firstName(res=None, val=None):
	return ResourceData(res,URI('http://xmlns.com/foaf/0.1/firstName'), val)

@dataProperty
def lastName(res=None, val=None):
	return ResourceData(res,URI('http://xmlns.com/foaf/0.1/lastName'), val)