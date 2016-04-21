from graphstatements import Statement, URI, objectProperty, dataProperty

@dataProperty
def preferredTitle(sbj=None, obj=None):
	return Statement(sbj,URI('http://vivoweb.org/ontology/core#preferredTitle'), obj)

@objectProperty
def trainingAtOrganization(sbj=None, obj=None):
	return Statement(sbj,URI('http://vivoweb.org/ontology/core#trainingAtOrganization'), obj)

@objectProperty
def educationalTrainingOf(sbj=None, obj=None):
	return Statement(sbj,URI('http://vivoweb.org/ontology/core#educationalTrainingOf'), obj)
