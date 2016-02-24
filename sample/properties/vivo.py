from datasets import Datum

def preferredTitle(res=None, val=None):
	return Datum(res,'<http://vivoweb.org/ontology/core#preferredTitle>', val)

def trainingAtOrganization(res=None, val=None):
	return Datum(res,'<http://vivoweb.org/ontology/core#trainingAtOrganization>', val)

def educationalTrainingOf(res=None, val=None):
	return Datum(res,'<http://vivoweb.org/ontology/core#educationalTrainingOf>', val)
