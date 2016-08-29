import os
import uuid

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

	def mint_new_uri(self):
		#does a prefix for resource hash even make sense?
		data_hash = self.resource_hash(self.prefix)
		return self.namespace_uri(data_hash)

	def namespace_uri(self, suffix):
		return os.path.join(self.namespace, suffix)

	def create(self, data=None):
		uri = self.mint_new_uri()
		res = Resource(collection=self, uri=uri, data=data)
		# resp = res.save()
		# if resp:
		# 	return res
		return res

	def search(self, **params):
		res = Resource(collection=self, data=params)
		resp = self.endpoint.construct(res.to_query())
		# if resp == 200:
		# 	for tripleset in resp:

	def resource_hash(self, prefix):
		return uuid.uuid4().hex

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

	def unalias_attributes(self, data):
		return { self.aliases[k]: v for k,v in data.items() }

	def validate(self, data):
		valid_atts = self.validate_attributes(data)
		valid_data = self.validate_data(valid_atts)
		return valid_data

	def validate_attributes(self, data):
		data = { k: v for k,v in data.items() if k in self.uris }
		data.update({ k: list() for k in self.uris if k not in data })
		for k, v in data.items():
			validators = self.validators[k]['attributes']
			filtered = v
			for validator in validators:
				filtered = validator(filtered)
			data[k] = filtered
		return data

	def validate_data(self, data):
		for k, v in data.items():
			validator = self.validators[k]['data']
			filtered = [validator(d) for d in v] 
			data[k] = filtered
		return data

class Schema(object):
	def __init__(self, attrs):
		self.attributes = attrs
		self.aliases = { attr.alias: attr.uri for attr in attrs }
		self.uris = { attr.uri: attr.alias for attr in attrs }
		self.attr_validators = { attr.uri: attr.validators for attr in attrs }
		self.data_validators = { attr.uri: attr.predicate.validator for attr in attrs }
		self.required_attrs = [ attr.uri for attr in attrs if attr.required ]
		self.optional_attrs = [ attr.uri for attr in attrs if not attr.required ]

def _validate_list(values):
	if not isinstance(values, list):
		raise TypeError('Data must be in list format')
	return values

def _validate_required(values):
	if len(values) == 0:
		raise ValueError("Value is required")
	return values

def _validate_unique(values):
	if len(values) == 0:
		raise ValueError("Only one value permitted")
	return values

class Attribute(object):
	def __init__(self, alias, predicate, required=False,
					unique=False, presets=None):
		self.predicate = predicate
		self.uri = predicate.uri
		self.alias = alias
		self.validators = [_validate_list]
		if presets:
			self.presets = presets
			self.validators.append(self._assign_presets)
		if required:
			self.required = True
			self.validators.append(_validate_required)
		if unique:
			self.unique = True
			self.validators.append(_validate_unique)

		def _assign_presets(self, values):
			return self.presets