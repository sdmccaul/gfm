from graphdata import ResourceData
from graphdatatypes import URI, objectProperty, dataProperty

@objectProperty
def broader(res=None, val=None):
	return ResourceData(res,URI('http://www.w3.org/2004/02/skos/core#broader'), val)

@objectProperty
def narrower(res=None, val=None):
	return ResourceData(res,URI('http://www.w3.org/2004/02/skos/core#narrower'), val)

@objectProperty
def related(res=None, val=None):
	return ResourceData(res,URI('http://www.w3.org/2004/02/skos/core#related'), val)

@dataProperty
def prefLabel(res=None, val=None):
	return ResourceData(res,URI('http://www.w3.org/2004/02/skos/core#prefLabel'), val)


@dataProperty
def altLabel(res=None, val=None):
	return ResourceData(res,URI('http://www.w3.org/2004/02/skos/core#altLabel'), val)


@dataProperty
def hiddenLabel(res=None, val=None):
	return ResourceData(res,URI('http://www.w3.org/2004/02/skos/core#hiddenLabel'), val)