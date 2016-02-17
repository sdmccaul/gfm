from datasets import DataSet, Required
from graphdb import QueryInterface

class Session(object):

	def __init__(self, dbInt, initGraph=DataSet([])):
		self.dbInt = dbInt
		self.initGraph = initGraph
		self.workingGraph = initGraph.copy()

	def find(self, pattern):
		found = self.dbInt.find(pattern)
		if found:
			self.initGraph.update(found)
			self.workingGraph.update(found)
			res = found[0].res
			return res
		else:
			return None

	def find_all(self, pattern):
		found = self.dbInt.find_all(pattern)
		if found:
			self.initGraph.update(found)
			self.workingGraph.update(found)
			res = { f.res for f in found}
			return res
		else:
			return None