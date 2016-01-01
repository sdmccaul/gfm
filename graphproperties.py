from graphfilters import Triple, set_filter, get_objects
import types

TruthType = (types.NoneType, types.BooleanType)

SingleType = (types.StringType, types.UnicodeType,
                types.IntType, types.LongType,
                types.FloatType, types.ComplexType)

ListType = types.ListType

class MultiValued(object):
	def __init__(self, predicate):
		self.predicate = predicate
		self.uri = predicate()[1]

	def __get__(self, instance, cls):
		pattern = self.predicate(sbj=instance.node, obj=None)
		return get_objects(set_filter(instance.graph, pattern))

	def __set__(self, instance, value):
		if not value or isinstance(value, TruthType):
			self.__delete__(instance)
			return
		elif isinstance(value, SingleType):
			self.__delete__(instance)
			add = { self.predicate(
            			sbj=instance.node, obj=value) }
		elif isinstance(value, ListType):
			self.__delete__(instance)
			add = { self.predicate(
						sbj=instance.node, obj=v)
							for v in value }
		else:
			raise Exception(
					"expected iterable, string or num")
		instance.graph.update(add)

	def __delete__(self, instance):
		pattern = self.predicate(sbj=instance.node, obj=None)
		rmv = set_filter(instance.graph, pattern)
		instance.graph.difference_update(rmv)