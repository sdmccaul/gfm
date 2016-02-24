from collections import defaultdict

from datasets import DataSet
from graphattributes import Required
from graphdb import QueryInterface

class Session(object):

	def __init__(self, dbInt, initGraph=DataSet([])):
		self.dbInt = dbInt
		self.initGraph = initGraph
		self.views = []
		self.resources = defaultdict(DataSet)

	def mergeDataSets(self, dsetList):
		return DataSet([dtm for dset in dsetList
							for dtm in dset])

	def register(self, view):
		if view.uri in self.resources:
			view.graph = self.resources[view.uri]
			self.views.append(view)
		else:
			raise ("Pattern not found!")

	def unregister(self, view):
		if view.uri in self.resources:
			view.graph = None
			self.views.remove(view)
		else:
			raise ("Pattern not found!")

	def notify_views(self):
		pass

	def fetch(self, pattern):
		"""fetch reflects current state of datastore"""
		found = self.dbInt.fetch(pattern)
		if found:
			res = found.keys()[0]
			self.resources[res].update(found[res])
			self.initGraph.update(
				self.mergeDataSets(found.values()
					))
			return res
		else:
			return None

	def fetchAll(self, pattern):
		found = self.dbInt.fetchAll(pattern)
		if found:
			res = [ f for f in found.keys() ]
			for r in res:
				self.resources[r].update(found[r])
			self.initGraph.update(
				self.mergeDataSets(found.values()
					))
			return res
		else:
			return None

	def commit(self):
		workingGraph = self.mergeDataSets(self.resources.values())
		if self.initGraph != workingGraph:
			remove = self.initGraph - workingGraph
			add = workingGraph - self.initGraph
			self.dbInt.executeUpdate(add=add, remove=remove)
			self.initGraph.clear()
		self.close()

	def rollback(self):
		self.workingGraph = self.initGraph

	def close(self):
		if self.initGraph != self.workingGraph:
			raise "Uncommited changes!"
		else:
			for view in self.views:
				del view