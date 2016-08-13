import domains

class Expression(object):

	def __init__(self, schema):
		self.schema = schema


	def mint_new_uri(self):
		pass

	def dictionaryToObject(dikt):
		pass

class Collection(object):
	def __init__(self, name, schema, graph, prefix):
		self.name = name
		self.schema = schema
		self.graph = graph
		self.prefix = prefix

	def map_data_to_res(self, data):
		mapped = dict()
		for name, vals in data:
			try:
				uri = self.schema[name].uri
			except KeyError:
				raise Exception("Unrecognized field")
			if not isinstance(vals, list):
				raise Exception("Attribute values must be list")
			mapped[uri] = vals
		return mapped
		# mapped = dict( (self.mappings['uris'][key], value) for key, value in data.items())
		# return mapped

	def map_triples_to_res(triples):
		out = defaultdict(list)
		subject = set()
		for triple in triples:
			try:
				subject.add(triple[0].geturl())
			except AttributeError:
				raise Exception("Expecting urlparse url")
			try:
				predicate = triple[1].geturl()
			except AttributeError:
				raise Exception("Expecting urparse url")
			if predicate in self.schema:
				out[predicate].append(triple[2])
			else:
				raise Exception("Unrecognized field")
		if len(subject) > 1:
			raise Exception("Too many subjects in graph!")
		else:
			out["@uri"]=subject
			return out

	def register_endpoint(endpoint):
		self.endpoint = endpoint

	def mint_resource(self, uri, data=None):
		res = Resource(uri=uri, collection=self, data=data)
		return res

	def create(self, data=None):
		uri = self.new_uri(self.prefix)
		mapped = self.map_data_to_res(data)
		res = Resource(collection=self, uri=uri, data=mapped)
		resp = self.endpoint.insert(self.graph, res.toTriples())
		if resp:
			return res

	def search(self, **params):
		pass

	def find(self, rabid):
		uri = self.parse_rabid(rabid)
		res = Resource(uri=uri, collection=self)
		resp = self.endpoint.construct(res.toQuery())
		if resp == 200:
			results = self.map_triples_to_res(resp.body)
			return Resource(
					collection=self, uri=results['uri'], data=results['data'])

	def add_and_remove(self, add, remove):
		resp = self.endpoint.insert_and_delete(self.graph, add, remove)
		return resp

	def add(self, add):
		resp = self.endpoint.insert(self.graph, add)
		return resp

	def remove(self, remove):
		resp = self.endpoint.delete(self.graph, remove)
		return resp


#class Subject?
class Resource(object):
	def __init__(self, collection, uri=None, data=None):
		self.collection = collection
		self.schema = collection.schema
		if uri:
			self.uri = uri
		else:
			try:
				uri = data['@uri']
			except KeyError:
				raise Exception("Resource requires URI")
		if data:
			self.update(data)

	def __getitem__(self, name):
		return attribute_to_primitive(getattr(name))

	def __setitem__(self, name, value):
		predicate = self.schema[name]
		setattr(self, name, predicate(value))

	def attribute_to_primitive(self, value):
		if isinstance(value, urlparse.ParseResult):
			return value.geturl()
		elif isinstance(value, datetime.date):
			return value.isoformat()
		else:
			return value

	def to_triples(self):
		return [(self.uri, k, v) for k,v in self.__dict__.items() ]

	def to_dict(self):
		pass

	def to_query(self):
		required = [(self.uri, k, v) for k,v in self.__dict__.items() if k in self.schema.required ]
		optional = [(self.uri, k, v) for k,v in self.__dict__.items() if k in self.schema.optional ]
		return {'required': required, 'optional': optional}

	def overwrite(self, data):
		mapped = self.collection.map_data_to_res(data)
		revert = self.__dict__.items()
		old = self.to_triples()
		try:
			self.update(mapped)
		except:
			self.update(revert)
			raise ValueError("bad update: ", data)
		new = self.to_triples()
		resp = self.collection.add_and_remove(self, new, old)
		if resp:
			return True
		else:
			self.update(revert)
			raise ValueError("Overwrite rejected")

	def update(self, data):
		for k, v in data.items():
			self[k] = v

	def save(self):
		resp = self.collection.add(self.to_triples())
		return resp

	def remove(self):
		resp = self.collection.remove(self.to_triples())

class Schema(object):
	def __init__(self, predicates):
		self.fields = dict()
		self.fields.update({ predicate.uri: predicate for predicate in predicates })
		self.fields.update({ predicate.alias: predicate for predicate in predicates })
		self.required = [ predicate.uri for predicate in predicates if predicate.required ]
		self.optional = [ predicate.uri for predicate in predicates if predicate.optional ]

	def __getitem__(self, key):
		return self.fields[key]

class Attribute(object):
	def __init__(self, alias, predicate, required=True,
					optional=False, unique=False, values=list()):
		self.predicate = predicate
		self.uri = predicate.uri
		self.label = alias
		self.required = required
		self.optional = optional
		self.unique = unique
		self.values = values

	def __call__(self, vals=None):
		if vals is None:
			vals = self.values
		if self.required and len(vals) == 0:
			raise ValueError("Value is required")
		if self.unique and len(vals) > 1:
			raise ValueError("Only one value permitted")
		if self.optional and len(vals) == 0:
			return list()
		self.predicate.validate(vals)





rdfLabel = domains.StringProperty(
				uri='http://www.w3.org/2000/01/rdf-schema#label')

fisUpdated = domains.DateProperty(
				uri='http://vivo.brown.edu/ontology/vivo-brown/fisUpdated')


# class FisFaculty(object):
# 	expression = 'FisFaculty'
# 	schema = {
# 			'type': 'type: URI',
# 			'shortId': 'shortId: string',
# 			'label': 'label: string',
# 			'first': 'first: string',
# 			'last': 'last: string',
# 			'title': 'title: string'}

# 	def __init__(self, dataDict=None):
# 		if dataDict:
# 			self.update(dataDict)

# 	def update(self, updDict):
# 		for k, v in updDict.items():
# 			if k in self.schema.keys():
# 				setattr(self, k, v)

# 	def query(self, queryDict):
# 		pass

# 	def create(self, dataDict):
# 		return Resource(self.schema, dataDict)

# 	def find(self, rabid=rabid):
# 		query = Query(self.schema(rabid=rabid))
# 		resp = self.db.construct(query)
# 		if resp:
# 			found = self.create(resp)

# 	def save(self):
# 		pass

# 	def delete(self):
# 		pass

# 	def mint_uri(self):
# 		pass


# fisFacultySchema = Schema('FisFaculty',
# 							{'type': 'type: URI',
# 							'shortId': 'shortId: string',
# 							'label': 'label: string',
# 							'first': 'first: string',
# 							'last': 'last: string',
# 							'title': 'title: string'})

# class Stub(object):

# 	name_mappings =	{
# 					'type': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type',
# 					'shortId': 'http://vivo.brown.edu/ontology/vivo-brown/shortId',
# 					'label': 'http://www.w3.org/2000/01/rdf-schema#label'
# 					}

# 	validators = {
# 					'http://www.w3.org/1999/02/22-rdf-syntax-ns#type': {'range': 'object'},
# 					'http://vivo.brown.edu/ontology/vivo-brown/shortId':
# 					'http://www.w3.org/2000/01/rdf-schema#label':
# 				}

# 	def __init__(self):

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

class FisFaculty(Resource):

	def __init__(self, uri, schema):
	 	self.uri = uri
	 	self.shortId = list()
	 	self.type = 

	def builtin_to_date(self, value):
		if isinstance(value, datetime.date):
			return value
		else:
			try:
				return datetime.datetime.strptime(value, '%Y-%m-%dT%H:%M:%S.%fZ').date()
			except:	
				raise ValueError("Bad date: ", value)

	def date_to_builtin(self, value):
		try:
			return value.isoformat()
		except AttributeError:
			return value.decode("UTF-8")
		except:
			raise ValueError
