from graphdata import ResourceData
import types

TruthType = (types.NoneType, types.BooleanType)
ListType = types.ListType

def get_values(dset):
	return [ d[2] for d in dset ]

class Edge(object):
	def __init__(self, attr, restriction, values=[None]):
		self.attr = attr
		self.restriction = restriction
		self.values = values

	def __get__(self, instance, cls):
		if instance:
			pattern = self.attr(
				res=instance.uri, val=None)
			return get_values(
					instance.graph.query(**pattern._asdict()))
		else:
			return [ (self.attr, self.restriction(
						*(self.attr(res=None, val=v))))
						for v in self.values ]

	def __set__(self, instance, value):
		if not value or isinstance(value, TruthType):
			self.__delete__(instance)
			return
		elif isinstance(value, ListType):
			self.__delete__(instance)
			add = { self.attr(
						res=instance.uri, val=v)
							for v in value }
			instance.graph.update(add)
		else:
			raise Exception("expected list value")

	def __delete__(self, instance):
		pattern = self.attr(res=instance.uri, val=None)
		instance.graph.query_and_remove(**pattern._asdict())

class Required(ResourceData):
	pass

class Linked(ResourceData):
	pass

class Optional(ResourceData):
	pass

class Exclude(ResourceData):
	pass

class Only(ResourceData):
	pass