from graphstatements import Statement, URI, objectProperty, dataProperty

@dataProperty
def label(sbj=None, obj=None):
	return Statement(sbj,URI('http://www.w3.org/2000/01/rdf-schema#label'), obj)