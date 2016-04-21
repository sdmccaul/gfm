from graphstatements import Statement, URI, objectProperty

@objectProperty
def rdfType(sbj=None, obj=None):
	return Statement(sbj, URI('http://www.w3.org/1999/02/22-rdf-syntax-ns#type'), obj)