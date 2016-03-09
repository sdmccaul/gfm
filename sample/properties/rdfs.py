from resourcegraphs import ResourceData
from graphdatatypes import URI, objectProperty, dataProperty

@dataProperty
def label(res=None, val=None):
	return ResourceData(res,URI('http://www.w3.org/2000/01/rdf-schema#label'), val)