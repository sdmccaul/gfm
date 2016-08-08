import rdflib
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

	def json_to_dict(self, jdata):
		data = json.dumps(jdata)
		args = dict( (self.schema.names[key].uri, self.schema.names[key].toPython(value)) for key, value in data.items())
		inst = Resource(**args)
		return inst

	def register_endpoint(endpoint):
		self.endpoint = endpoint

	def mint_resource(self, uri, data=None):
		res = Resource(uri=uri, collection=self, data=data)
		return res

	def create(self, data=None):
		uri = self.newURI(self.prefix)
		valid = self.schema.validateDict(data)
		res = Resource(collection=self, uri=uri, data=valid)
		resp = self.endpoint.insert(self.graph, res.toTriples())
		if resp:
			return res

	def search(self, **params):
		pass

	def find(self, rabid):
		uri = self.parseRabid(rabid)
		res = Resource(uri=uri, collection=self)
		resp = self.endpoint.construct(res.toQuery())
		if resp == 200:
			results = self.triplesToDict(resp.body)
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

	def triplesToDicts(triples):
		out = []
		for tset in triples:
			data = defaultdict(list)
			uriSet = set()
			for triple in tset:
				uriSet.add(triple[0])
				data[triple[1]].append(triple[2])
			if len(uriSet) > 1:
				raise ValueError("too many uris!")
			out.append({'uri': uriSet[0], 'data': data})
		return out

#class Subject?
class Resource(object):
	def __init__(self, collection, uri, data=None):
		self.collection = collection
		self.schema = collection.schema
		if uri:
			self.uri = uri
		else:
			try:
				uri = data['uri']
			except KeyError:
				raise Exception("Resoource requires URI")
		if data:
			self.update(data)

	def __setattr__(self, name, value):
		domain = self.schema[name]
		setattr(self, name, domain(value))

	def toTriples(self):
		return [(self.uri, k, v) for k,v in self.__dict__.items() ]

	def toJSON(self):
		pass

	def toQuery(self):
		required = [(self.uri, k, v) for k,v in self.__dict__.items() if k.required ]
		optional = [(self.uri, k, v) for k,v in self.__dict__.items() if k.optional ]
		return {'required': required, 'optional': optional}

	def overwrite(self, data):
		valid = self.collection.json_to_dict(data)
		old = self.toTriples()
		self.update(valid)
		new = self.toTriples()
		resp = self.collection.add_and_remove(old, new)
		if resp:
			return True
		else:
			raise ValueError("Overwrite rejected")

	def update(self, data):
		for k, v in data.items():
			self[k] = v

	def save(self):
		resp = self.collection.add(self.toTriples())
		return resp

	def remove(self):
		resp = self.collection.remove(self.toTriples())

class Schema(object):
	def __init__(self, attvals):
		self.labels = { attval.label: attval for attval in attvals}
		self.uris = { attval.uri: attval for attval in attvals}

	def convertNames(namesDict):
		out = dict()
		for name, vals in namesDict:
			try:
				predicate = self.labels[name]
			except KeyError:
				raise Exception("Unrecognized field")
			if not isinstance(vals, list):
				raise Exception("Attribute values must be list")
			out[predicate] = vals
		return out

	def convertTriples(triples):
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
			if predicate in self.uris:
				out[predicate].append(triple[2])
			else:
				raise Exception("Unrecognized field")
		if len(subject) > 1:
			raise Exception("Too many subjects in graph!")
		else:
			out["uri"]=subject
			return out

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

	def check(self, inVals):
		if self.required and len(inVals) == 0:
			raise ValueError("Value is required")
		if self.unique and len(inVals) > 1:
			raise ValueError("Only one value permitted")
		self.predicate.validate(inVals)


class Predicate(object):	
	def __init__(self, uri, domain):
		self.uri = uri
		self.domain = domain

	def toPython(self, vals):
		if type(vals) != list:
			raise ValueError("Expected list")
		return [ self.domain(val) for val in vals ]


rdfLabel = Predicate(
				uri='http://www.w3.org/2000/01/rdf-schema#label',
				domain=domains.xsdString)

fisUpdated = Predicate(
				uri='http://vivo.brown.edu/ontology/vivo-brown/fisUpdated',
				domain=domains.xsdDate
	)


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