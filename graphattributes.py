from datasets import DataSet, Datum
import types

TruthType = (types.NoneType, types.BooleanType)

SingleType = (types.StringType, types.UnicodeType,
                types.IntType, types.LongType,
                types.FloatType, types.ComplexType)

ListType = types.ListType

def get_values(dset):
	return [ d[2] for d in dset ]

class MultiValued(object):
	def __init__(self, attr):
		self.attr = attr

	def __get__(self, instance, cls):
		if instance:
			pattern = self.attr(
				res=instance.node, val=None)
			return get_values(instance.graph.find(
								DataSet({pattern})))
		else:
			return self.attr(res=None, val=None)
		

	def __set__(self, instance, value):
		if not value or isinstance(value, TruthType):
			self.__delete__(instance)
			return
		# elif isinstance(value, SingleType):
		# 	self.__delete__(instance)
		# 	add = { self.attr(
  #           			res=instance.node, val=value) }
		elif isinstance(value, ListType):
			self.__delete__(instance)
			add = { self.attr(
						res=instance.node, val=v)
							for v in value }
			instance.graph |= add
		else:
			raise Exception("expected list value")
		# instance.graph.update(add)

	def __delete__(self, instance):
		rmv = self.attr(res=instance.node, val=None)
		instance.graph -= {rmv}

	# def add(self, instance, value):
	# 	instance.graph.add(self.attr(res=instance.node, val=value))

	# def remove(self, instance, value):
	# 	instance.graph.discard(self.attr(res=instance.node, val=value))