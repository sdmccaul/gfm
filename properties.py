from graphfilters import Triple

def rdfType(sbj=None, obj=None):
	return Triple(sbj,'<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>', obj)