from predicates import Predicate

rdfType = Predicate('http://www.w3.org/1999/02/22-rdf-syntax-ns#type','uri')
rdfsLabel = Predicate('http://www.w3.org/2000/01/rdf-schema#label','string')
firstName = Predicate('http://xmlns.com/foaf/0.1/firstName','string')
lastName = Predicate('http://xmlns.com/foaf/0.1/lastName','string')
shortId = Predicate('http://vivo.brown.edu/ontology/vivo-brown/shortId','string')
degreeDate = Predicate('http://vivo.brown.edu/ontology/vivo-brown/degreeDate','year')
preferredTitle = Predicate('http://vivoweb.org/ontology/core#preferredTitle', 'string')