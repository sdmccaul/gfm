from graphstatements import Statement, URI, objectProperty, dataProperty

@objectProperty
def broader(sbj=None, obj=None):
	return Statement(sbj,URI('http://www.w3.org/2004/02/skos/core#broader'), obj)

@objectProperty
def narrower(sbj=None, obj=None):
	return Statement(sbj,URI('http://www.w3.org/2004/02/skos/core#narrower'), obj)

@objectProperty
def related(sbj=None, obj=None):
	return Statement(sbj,URI('http://www.w3.org/2004/02/skos/core#related'), obj)

@dataProperty
def prefLabel(sbj=None, obj=None):
	return Statement(sbj,URI('http://www.w3.org/2004/02/skos/core#prefLabel'), obj)


@dataProperty
def altLabel(sbj=None, obj=None):
	return Statement(sbj,URI('http://www.w3.org/2004/02/skos/core#altLabel'), obj)


@dataProperty
def hiddenLabel(sbj=None, obj=None):
	return Statement(sbj,URI('http://www.w3.org/2004/02/skos/core#hiddenLabel'), obj)