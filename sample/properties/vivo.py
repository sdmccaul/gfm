from datasets import Datum
from graphdatatypes import URI, objectProperty, dataProperty

@dataProperty
def preferredTitle(res=None, val=None):
	return Datum(res,URI('http://vivoweb.org/ontology/core#preferredTitle'), val)

@objectProperty
def trainingAtOrganization(res, val):
	return Datum(res,URI('http://vivoweb.org/ontology/core#trainingAtOrganization'), val)

@objectProperty
def educationalTrainingOf(res, val):
	return Datum(res,URI('http://vivoweb.org/ontology/core#educationalTrainingOf'), val)
