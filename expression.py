import domains

class Collection(object):
	def __init__(self, name, schema, named_graph, namespace, prefix):
		self.name = name
		self.schema = schema
		self.named_graph = named_graph
		self.namespace = namespace
		self.prefix = prefix

	def _triples_to_dict(triples):
		out = defaultdict(list)
		for triple in triples:
			out[triple[1]].append(triple[2])
		return out

	def register_endpoint(endpoint):
		self.endpoint = endpoint

	def mint_new_uri():
		data_hash = self.resource_hash(self.prefix)
		return namespace_uri(data_hash)

	def namespace_uri(suffix):
		return os.path.join(self.namespace, suffix)

	def create(self, data=None):
		uri = self.mint_new_uri()
		res = Resource(collection=self, uri=uri, data=data)
		resp = res.save()
		if resp:
			return res

	def search(self, **params):
		res = Resource(collection=self, data=params)
		resp = self.endpoint.construct(res.to_query())
		if resp == 200:
			for tripleset in resp:


	def find(self, rabid):
		uri = self.namespace_uri(rabid)
		res = Resource(uri=uri, collection=self)
		resp = self.endpoint.construct(res.to_query())
		if resp == 200:
			assert(uri == resp.body['@uri'])
			data = self._triples_to_dict(resp.body['triples'])
			res.update(data)
			return res

	def add_and_remove(self, add, remove):
		resp = self.endpoint.insert_and_delete(self.graph, add, remove)
		return resp

	def add(self, add):
		resp = self.endpoint.insert(self.graph, add)
		return resp

	def remove(self, remove):
		resp = self.endpoint.delete(self.graph, remove)
		return resp

class Resource(object):
	def __init__(self, collection, uri=None, data=None):
		self.collection = collection
		self.graph_data = dict()
		self.optional = collection.schema.optional
		self.required = collection.schema.required
		self.unique = collection.schema.unique
		self.aliases = collection.schema.aliases
		self.uri_aliases = collection.schema.uri_aliases
		self.validators = self.schema.validators
		if uri:
			self.uri = uri
		elif data:
			self.uri = data.get('@uri',None)
		else:
			self.uri = None
		if data:
			self.update(data)

	def to_triples(self):
		return [(self.uri, k, v) for val in v
					for k,v in self.graph_data.items() ]

	def to_dict(self, alias=True):
		if alias:
			out = { self.aliases[k]: v for k,v in self.graph_data.items() }
		else:
			out = self.graph_data
		out['@uri'] = self.uri
		return out

	def to_query(self):
		# Needs val conversion to None
		# where appropriate
		required = [(self.uri, k, val) for val in v
						for k,v in self.graph.items()
							if k in self.required ]
		optional = [(self.uri, k, val) for val in v
						for k,v in self.graph.items()
							if k in self.optional ]
		return {'required': required, 'optional': optional}

	def overwrite(self, data):
		revert = self.graph.copy()
		old = self.to_triples()
		try:
			self.update(data)
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
		verified = self.verify_attribute_keys(data)
		validatts = self.validate_attributes(data)
		validdata = self.validate_data(validatts)
		self.graph.update(validdata)

	def save(self):
		resp = self.collection.add(self.to_triples())
		return resp

	def remove(self):
		resp = self.collection.remove(self.to_triples())

	def verify_attribute_keys(data):
		return [ self.aliases[k] for ]

class Schema(object):
	def __init__(self, predicates):
		self.aliases = { predicate.uri: predicate for predicate in predicates })
		self.uri_aliases = { predicate.alias: predicate for predicate in predicates }
		self.required = [ predicate.uri for predicate in predicates if predicate.required ]
		self.optional = [ predicate.uri for predicate in predicates if predicate.optional ]


	def validate_date(self, key):
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
