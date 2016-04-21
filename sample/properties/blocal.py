from graphstatements import Statement, URI, objectProperty, dataProperty

@dataProperty
def shortId(sbj=None, obj=None):
	return Statement(sbj,URI('http://vivo.brown.edu/ontology/vivo-brown/shortId'), obj)

@dataProperty
def degreeDate(sbj=None, obj=None):
	return Statement(sbj,URI('http://vivo.brown.edu/ontology/vivo-brown/degreeDate'), obj)