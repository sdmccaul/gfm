from datasets import Datum

def rdfType(res=None, val=None):
	return Datum(res,'<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>', val)

def rdfsLabel(res=None, val=None):
	return Datum(res,'<http://www.w3.org/2000/01/rdf-schema#label>', val)

def foafFirstName(res=None, val=None):
	return Datum(res,'<http://xmlns.com/foaf/0.1/firstName>', val)

def foafLastName(res=None, val=None):
	return Datum(res,'<http://xmlns.com/foaf/0.1/lastName>', val)

def vivoPreferredTitle(res=None, val=None):
	return Datum(res,'<http://vivoweb.org/ontology/core#preferredTitle>', val)

def blocalShortId(res=None, val=None):
	return Datum(res,'<http://vivo.brown.edu/ontology/vivo-brown/shortId>', val)