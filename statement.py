import rdflib


class Statement(object):

	def __init__(self, sbj, uri, objValidator):
		self.uri = uri
		self.subject = sbj
		self.verb = rdflib.URIRef(uri)
		self.objValidator = objValidator

	def _validate_obj_value(self, obj):
		return self.objValidator(obj).toPython()

class RdfType(Statement):

	def __init__(self, sbj, uri):
		self.uri = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'
		self.subject = sbj
		self.verb = rdflib.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type')
		self.objType = uri.URIRef