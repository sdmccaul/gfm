from datasets import DataSet, Datum
import types

TruthType = (types.NoneType, types.BooleanType)
ListType = types.ListType

def get_values(dset):
	return [ d[2] for d in dset ]

class Attribute(object):
	def __init__(self, attr):
		self.attr = attr

	def __get__(self, instance, cls):
		if instance:
			pattern = self.attr(
				res=instance.node, val=None)
			return get_values(instance.graph.find(pattern))
		else:
			return self.attr(res=None, val=None)
		

	def __set__(self, instance, value):
		if not value or isinstance(value, TruthType):
			self.__delete__(instance)
			return
		elif isinstance(value, ListType):
			self.__delete__(instance)
			add = { self.attr(
						res=instance.node, val=v)
							for v in value }
			instance.graph.update(add)
		else:
			raise Exception("expected list value")

	def __delete__(self, instance):
		pattern = self.attr(res=instance.node, val=None)
		instance.graph.find_and_remove(pattern)