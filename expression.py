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
		# if resp == 200:
		# 	for tripleset in resp:


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
		self.data = dict()
		self.aliases = collection.schema.aliases
		self.uris = collection.schema.uris
		self.validators = collection.schema.validators
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
			out = { self.uris[k]: v for k,v in self.data.items() }
		else:
			out = self.data
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

	def update(self, data, aliased=True, validate=True):
		if aliased:
			data = self.unalias_attributes(data)
		if validate:
			data = self.validate(data)
		self.data.update(data)

	def save(self):
		resp = self.collection.add(self.to_triples())
		return resp

	def remove(self):
		resp = self.collection.remove(self.to_triples())

	def unalias_attributes(data):
		return { self.aliases[k]: v for k,v in data.items() }

	def validate(data):
		valid_atts = validate_attributes(data)
		valid_data = validate_data(valid_atts)
		return valid_data

	def validate_attributes(data):
		no_other_attrs = { k: v for k,v in data.items() if k in self.uris }
		all_attrs_present = { k: list() for k in self.uris if k not in no_other_attrs }
		return all_attrs_present

	def validate_data(data):
		out = {}
		for k, v in data():
			validators = self.validators[k]
			filtered = v
			for validate in validators:
				filtered = validate(filtered)
			out[uri] = filtered
		return out

class Schema(object):
	def __init__(self, attrs):
		self.aliases = { attr.alias: attr.uri for attr in attrs }
		self.uris = { attr.uri: attr.alias for attr in attrs }
		self.validators = { attr.uri: attr.validators for attr in attrs }

class Attribute(object):
	def __init__(self, alias, predicate, required=True,
					unique=False, values=list()):
		self.uri = predicate.uri
		self.alias = alias
		self.defaults = values
		self.validators = [predicate.validator]
		if values:
			self.validators.insert(self._validate_defaults,0)
		if unique:
			self.validators.insert(self._validate_unique,0)
		if required:
			self.validators.insert(self._validate_required,0)

	def _validate_required(self, values):
		if len(values) == 0:
			raise ValueError("Value is required")
		return values

	def _validate_unique(self, values):
		if len(vals) == 0:
			raise ValueError("Only one value permitted")
		return values

	def _validate_defaults(self, values):
		return self.defaults