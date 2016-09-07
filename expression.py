import os
import uuid

class Collection(object):
	def __init__(self, name, schema, named_graph, namespace, prefix):
		self.name = name
		self.schema = schema
		self.named_graph = named_graph
		self.namespace = namespace
		self.prefix = prefix

	def register_endpoint(self, endpoint):
		self.endpoint = endpoint

	def mint_new_uri(self):
		#does a prefix for resource hash even make sense?
		data_hash = self.resource_hash(self.prefix)
		return self.namespace_uri(data_hash)

	def resource_hash(self, prefix):
		return uuid.uuid4().hex

	def namespace_uri(self, suffix):
		return os.path.join(self.namespace, suffix)

	def create(self, data=dict(), aliased=False):
		uri = self.mint_new_uri()
		if aliased:
			data = self.schema.unalias_data(data)
		res = Resource(collection=self, uri=uri, incoming=data)
		resp = self.endpoint.update(insert=res)
		return resp

	def search(self, params=dict(), aliased=True):
		## IMPORTANT
		## should not be able to search on an optional term
		## or perhaps, not without required term present
		## leads to SPARQL weirdness
		if aliased:
			params = self.schema.unalias_data(params)
		query = Resource(collection=self, query=params)
		resp = self.endpoint.construct(query)
		resList = [ Resource(uri=data.keys()[0],
					collection=self, stored=data.values()[0])
					for data in resp ]
		return resList

	def find(self, rabid):
		uri = self.namespace_uri(rabid)
		query = Resource(uri=uri, collection=self, query={})
		resp = self.endpoint.construct(query)
		resList = [ Resource(uri=data.keys()[0],
					collection=self, stored=data.values()[0])
					for data in resp ]
		# Validate len(resList) == 1 ?
		return resList[0]

	def overwrite(self, existing, data, aliased=True):
		uri, data = data.items()[0]
		assert uri == existing.uri
		if aliased:
			data = self.schema.unalias_data(data)
		pending = Resource(
					uri=existing.uri, collection=self, incoming=data)
		resp = self.endpoint.update(insert=pending, delete=existing)
		return resp

	def modify(self, existing, data, aliased=True):
		uri, data = data.items()[0]
		assert uri == existing.uri
		if aliased:
			data = self.schema.unalias_data(data)
		uri, existing_data = existing.to_dict(alias=False).items()[0]
		pending = Resource(uri=existing.uri,
							collection=self, stored=existing_data)
		pending.update(data, validate_partial=True)
		resp = self.endpoint.update(insert=pending, delete=existing)
		return resp

	def remove(self, existing):
		resp = self.endpoint.update(delete=existing)
		return resp

class Resource(object):
	def __init__(self, collection, uri=None,
					incoming=None, stored=None,
					query=None):
		self.data = dict()
		self.collection = collection
		self.schema = collection.schema
		self.uri = uri
		if isinstance(incoming, dict):
			self.update(incoming, validate_full=True)
		elif isinstance(stored, dict):
			self.update(stored, validate_full=False)
		elif isinstance(query, dict):
			self.update(query, validate_query=True)

	def to_triples(self):
		return [(self.uri, k, val) for k,v in self.data.items()
					for val in v ]

	def to_dict(self, alias=True):
		if alias:
			data = self.schema.alias_data(self.data)
		else:
			data = self.data
		out = { self.uri: data }
		return out

	def update(self, data, validate_full=False,
				validate_partial=False,
				validate_query=False):
		if validate_full or validate_query:
			data = self.schema.validate_structure(data)
		if validate_full or validate_partial:
			data = self.schema.validate_resource(data)
		elif validate_query:
			data = self.schema.validate_query(data)
		self.data.update(data)

def rename_dictionary_keys(newKeyMap, dct):
	return { newKeyMap[k]: v for k,v in dct.items() }

def filter_unrecognized_keys(keyList, dct):
	return { k: v for k,v in dct.items() if k in keyList }

def add_missing_keys(keyList, dct):
	out = dct.copy()
	out.update({ k: list() for k in keyList if k not in dct })
	return out

def set_default_list_value(lst, val):
	if not lst:
		return [val]
	else:
		return lst 

def noneify_empty_dictionary_lists(dct):
	noned = { k:set_default_list_value(v, None)
				for k,v in dct.items() }
	return noned

class Schema(object):
	def __init__(self, attrs):
		self.attributes = attrs
		self.aliases = { attr.alias: attr.uri for attr in attrs }
		self.uris = { attr.uri: attr.alias for attr in attrs }
		self.attr_validators = { attr.uri: attr.validators for attr in attrs }
		self.data_validators = { attr.uri: attr.predicate.validator for attr in attrs }
		self.presets = { attr.uri: attr.presets for attr in attrs if hasattr(attr,'presets') }
		self.required = [ attr.uri for attr in attrs if hasattr(attr,'required') ]
		self.optional = [ attr.uri for attr in attrs if not hasattr(attr,'required') ]
		self.datatypes = { attr.uri: attr.predicate.datatype for attr in attrs }

	def unalias_data(self, data):
		return rename_dictionary_keys(self.aliases, data)

	def alias_data(self, data):
		return rename_dictionary_keys(self.uris, data)

	def assign_preset_values(self, data):
		data.update(self.presets)
		return data

	def validate_attributes(self, data):
		out = dict()
		for k, v in data.items():
			validators = self.attr_validators[k]
			filtered = v
			for validator in validators:
				filtered = validator(filtered)
			out[k] = filtered
		return out

	def validate_data(self, data):
		out = dict()
		for k, v in data.items():
			validator = self.data_validators[k]
			out[k] = [validator(d) for d in v] 
		return out

	def validate_structure(self, data):
		# Only include recognized attribute/values
		data = filter_unrecognized_keys(self.uris.keys(), data)
		# Ensure all attributes are present
		data = add_missing_keys(self.uris.keys(), data)
		return data

	def validate_resource(self, data):
		data = self.assign_preset_values(data)
		data = self.validate_attributes(data)
		data = self.validate_data(data)
		return data

	def validate_query(self, params):
		params = self.assign_preset_values(params)
		params = self.validate_data(params)
		params = noneify_empty_dictionary_lists(params)
		return params

def _validate_list(values):
	if not isinstance(values, list):
		raise TypeError('Data must be in list format')
	return values

def _validate_required(values):
	if len(values) == 0:
		raise ValueError("Value is required")
	return values

def _validate_unique(values):
	if len(values) > 1:
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
		if required:
			self.required = True
			self.validators.append(_validate_required)
		if unique:
			self.unique = True
			self.validators.append(_validate_unique)