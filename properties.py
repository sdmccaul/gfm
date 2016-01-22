from graphfilters import Datum

def rdfType(sbj=None, obj=None):
	return Datum(sbj,'<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>', obj)

def rdfsLabel(sbj=None, obj=None):
	return Datum(sbj,'<http://www.w3.org/2000/01/rdf-schema#label>', obj)

def foafFirstName(sbj=None, obj=None):
	return Datum(sbj,'<http://xmlns.com/foaf/0.1/firstName>', obj)

def foafLastName(sbj=None, obj=None):
	return Datum(sbj,'<http://xmlns.com/foaf/0.1/lastName>', obj)

def vivoPreferredTitle(sbj=None, obj=None):
	return Datum(sbj,'<http://vivoweb.org/ontology/core#preferredTitle>', obj)

def blocalShortId(sbj=None, obj=None):
	return Datum(sbj,'<http://vivo.brown.edu/ontology/vivo-brown/shortId>', obj)