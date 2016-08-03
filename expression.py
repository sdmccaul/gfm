import rdflib

class Expression(object):

	def __init__(self, schema):
		self.schema = schema


	def mint_new_uri(self):
		pass

	def dictionaryToObject(dikt):
		pass

class Document(object):

	def __init__(self, schema):



class Collection(object):
	def __init__(self, name, schema, graph, prefix):
		self.name = name
		self.schema = schema
		self.graph = graph
		self.prefix = prefix

	def store(endpoint):
		self.endpoint = endpoint

	def mintResource(self, uri, data=None):
		res = Resource(uri=uri, collection=self, data=data)
		return res

	def create(self, data=None):
		uri = self.newURI(self.prefix)
		mapped = self.schema.validate(data)
		res = Resource(uri=uri, collection=self, data=mapped)
		resp = self.endpoint.insert(self.graph, res.toTriples())
		if resp == 201: 
			return res

	def find(self, rabid, data=None):
		uri = self.parseRabid(rabid)
		# if data:
		# 	mapped = self.schema.validate(data)
		# else:
		# 	mapped = None
		query = Resource(uri=uri, collection=self)
		resp = self.endpoint.query(query.toTriples())
		if resp == 200:
			results = self.schema.triplesToDict(resp.body)
			return Resource(uri=uri, collection=self, data=results)


	def commit(self, add, remove):
		resp = self.endpoint.insertAndDelete(self.graph, add, remove)
		return resp


class Resource(object):
	def __init__(self, collection, data=None):
		self._collection = collection
		if data:
			for k,v in data.items():
				self.setattr(k,v)

	def overwrite(self, data):
		past = self.toTriples()
		mapped = self.collection.schema.validate(data)
		for k,v in mapped.items():
			self.setattr(k,v)
		current = self.toTriples()
		resp = self.collection.commit(current, past)
		return resp

	def save(self):
		resp = self.collection.commit(self.toTriples(), set())
		return resp

	def remove(self):
		resp = self.collection.commit(set(), self.toTriples())
		return resp

class Schema(object):
	def __init__(self, rulesDict):
		self.rules = rulesDict
		self.required = [ rule for rule in rulesDict
							if (rulesDict[rule].required==True and rulesDict[rule].optional==False) ]

	def validate(self, inputData):
		out = dict()
		for field in self.rules:
			# try:
			# 	data = inputData[field]
			# except KeyError:
			# 	if field in self.required:
			# 		raise Exception("Missing required data field: "+field)
			# 	else:
			# 		data = []
			data = inputData.get(field, list())
			rule = self.rules[field]
			valid = rule.check(data)
			out[rule.uri] = valid
		return out

class Statement(object):
	def __init__(self, uri=None, required=True, optional=False,
					unique=False, values=list()):
		self.uri = uri
		self.required = required
		self.optional = optional
		self.unique = unique
		self.values = values

	def check(self, inVals):
		if type(inVals) != list:
			raise ValueError("Expected list")
		if self.required and len(inVals) == 0:
			raise ValueError("Value is required")
		if self.unique and len(inVals) > 1:
			raise ValueError("Only one value permitted")

class FisFaculty(object):
	expression = 'FisFaculty'
	schema = {
			'type': 'type: URI',
			'shortId': 'shortId: string',
			'label': 'label: string',
			'first': 'first: string',
			'last': 'last: string',
			'title': 'title: string'}

	def __init__(self, dataDict=None):
		if dataDict:
			self.update(dataDict)

	def update(self, updDict):
		for k, v in updDict.items():
			if k in self.schema.keys():
				setattr(self, k, v)

	def query(self, queryDict):
		pass

	def create(self, dataDict):
		return Resource(self.schema, dataDict)

	def find(self, rabid=rabid):
		query = Query(self.schema(rabid=rabid))
		resp = self.db.construct(query)
		if resp:
			found = self.create(resp)

	def save(self):
		pass

	def delete(self):
		pass

	def mint_uri(self):
		pass


fisFacultySchema = Schema('FisFaculty',
							{'type': 'type: URI',
							'shortId': 'shortId: string',
							'label': 'label: string',
							'first': 'first: string',
							'last': 'last: string',
							'title': 'title: string'}


# class FisFaculty(Schema):

# 	attributes = {
# 		'type': Statement(
# 					{
# 					'verb': rdf.RdfType,
# 					'values': [
# 						'http://vivoweb.org/ontology/core#FacultyMember',
# 						'http://vivo.brown.edu/ontology/vivo-brown/BrownThing'
# 						],
# 					}),
# 		'shortId': Statement({'verb': blocal.ShortId}),
# 		'label': Statement({'verb': rdfs.Label),
#     	'first': Statement(
#     				{'verb': foaf.FirstName,
#     				'required': False,
#     				'unique': True}),
#     	'last': Statement({'verb': foaf.LastName,
#     				'required': False,
#     				'unique': True}),
#     	'title': Statement({'verb': vivo.preferredTitle
#     				'required': False})
# 	}