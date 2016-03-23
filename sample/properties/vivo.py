from graphdata import ResourceData
from graphdatatypes import URI, objectProperty, dataProperty

@dataProperty
def preferredTitle(res=None, val=None):
	return ResourceData(res,URI('http://vivoweb.org/ontology/core#preferredTitle'), val)

@objectProperty
def trainingAtOrganization(res, val):
	return ResourceData(res,URI('http://vivoweb.org/ontology/core#trainingAtOrganization'), val)

@objectProperty
def educationalTrainingOf(res, val):
	return ResourceData(res,URI('http://vivoweb.org/ontology/core#educationalTrainingOf'), val)
