import types

ListType = types.ListType

def get_values(dset):
	return [ d[2] for d in dset ]

class Edge(object):
	def __init__(self, stmtFunc, stmtType, values=[None]):
		self.stmtFunc = stmtFunc
		self.prp = stmtFunc().prp
		self.stmtType = stmtType
		self.objs = values

	def __get__(self, instance, cls):
		if instance:
			stmt = self.stmtFunc(
				sbj=instance.uri, obj=None)
			return get_values(
					instance.graph.query(**stmt._asdict()))
		else:
			return [ self.stmtType(
							*(self.stmtFunc(sbj=None, obj=o))
						)
						for o in self.objs ]

	def __set__(self, instance, objs):
		if isinstance(objs, ListType):
			self.__delete__(instance)
			add = { self.stmtFunc(
						sbj=instance.uri, obj=o)
							for o in objs }
			instance.graph.update(add)
		else:
			raise Exception("expected list value")

	def __delete__(self, instance):
		stmt = self.stmtFunc(sbj=instance.uri, obj=None)
		instance.graph.query_and_remove(**stmt._asdict())