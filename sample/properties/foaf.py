from graphstatements import Statement, URI, dataProperty

@dataProperty
def firstName(sbj=None, obj=None):
	return Statement(sbj,URI('http://xmlns.com/foaf/0.1/firstName'), obj)

@dataProperty
def lastName(sbj=None, obj=None):
	return Statement(sbj,URI('http://xmlns.com/foaf/0.1/lastName'), obj)