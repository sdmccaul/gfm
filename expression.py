import os
import uuid

class Collection(object):
	def __init__(self, name, schema, named_graph, namespace, prefix):
		self.name = name
		self.schema = schema
		self.named_graph = named_graph
		self.namespace = namespace
		self.prefix = prefix

	# def _triples_to_dict(triples):
	# 	out = defaultdict(list)
	# 	for triple in triples:
	# 		out[triple[1]].append(triple[2])
	# 	return out

	def register_endpoint(self, endpoint):
		self.endpoint = endpoint

	def mint_new_uri(self):
		#does a prefix for resource hash even make sense?
		data_hash = self.resource_hash(self.prefix)
		return self.namespace_uri(data_hash)

	def namespace_uri(self, suffix):
		return os.path.join(self.namespace, suffix)

	def create(self, data=dict(), aliased=False):
		uri = self.mint_new_uri()
		if aliased:
			data = self.schema.unalias_data(data)
		res = Resource(collection=self, uri=uri, data=data)
		# resp = res.save()
		# if resp:
		# 	return res
		return res

	def search(self, params=dict(), aliased=True, identity=False):
		## IMPORTANT
		## should not be able to search on an optional term
		## or perhaps, not without required term present
		## leads to SPARQL weirdness
		if aliased:
			params = self.schema.unalias_data(params)
		query = Resource(collection=self, query=params)
		if identity:
			resp = self.endpoint.identity(query)
		else:
			resp = self.endpoint.construct(query)
		resList = [ Resource(collection=self, data=data)
					for data in resp ]
		return resList

	def resource_hash(self, prefix):
		return uuid.uuid4().hex

	def find(self, rabid):
		uri = self.namespace_uri(rabid)
		query = Resource(uri=uri, collection=self, query={})
		resp = self.endpoint.construct(query)
		resList = [ Resource(collection=self, data=data)
					for data in resp ]
		# Validate len(resList) == 1 ?
		return resList

	def add_and_remove(self, add, remove):
		resp = self.endpoint.insert_and_delete(
				self.named_graph, add, remove)
		return resp

	def add(self, add):
		resp = self.endpoint.insert(
				self.named_graph, add)
		return resp

	def remove(self, remove):
		resp = self.endpoint.delete(
				self.named_graph, remove)
		return resp

class Resource(object):
	def __init__(self, collection, uri=None,
					data=None, query=None):
		# self.stored = dict()
		self.data = dict()
		self.collection = collection
		self.schema = collection.schema
		if uri:
			self.uri = uri
		elif data:
			self.uri = data.get('@uri',None)
		else:
			self.uri = None
		if isinstance(data, dict):
			self.update(data, validate=False)
		elif isinstance(query, dict):
			self.data = self.schema.validate_query(query)

	def to_triples(self):
		return [(self.uri, k, val) for k,v in self.data.items()
					for val in v ]

	def to_dict(self, alias=True):
		if alias:
			out = self.schema.alias_data(self.data)
		else:
			out = self.data
		out['@uri'] = self.uri
		return out

	def overwrite(self, data):
		revert = self.data.copy()
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

	def update(self, data, aliased=False, validate=False):
		if aliased:
			data = self.schema.unalias_data(data)
		if validate:
			data = self.schema.validate(data)
		self.data.update(data)

	def save(self):
		resp = self.collection.add(self.to_triples())
		return resp

	def remove(self):
		resp = self.collection.remove(self.to_triples())

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

	def validate(self, data):
		# Only include recognized attribute/values
		data = filter_unrecognized_keys(self.uris.keys(), data)
		# Ensure all attributes are present
		data = add_missing_keys(self.uris.keys(), data)
		data = self.assign_preset_values(data)
		data = self.validate_attributes(data)
		data = self.validate_data(data)
		return data

	def validate_query(self, params):
		params = filter_unrecognized_keys(self.uris.keys(), params)
		params = add_missing_keys(self.uris.keys(), params)
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