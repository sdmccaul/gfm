from collections import defaultdict

from datasets import DataSet, Required
from graphdb import QueryInterface

class Session(object):

	def __init__(self, dbInt, initGraph=DataSet([])):
		self.dbInt = dbInt
		self.initGraph = initGraph
		self.workingGraph = initGraph.copy()
		self.views = []

	def register(self, view):
		if view.pattern(res=view.uri) in self.workingGraph:
			self.views.append(view)
		else:
			raise ("Pattern not found!")

	def unregister(self, view):
		if view.pattern(res=view.uri) in self.workingGraph:
			self.views.remove(view)
		else:
			raise ("Pattern not found!")

	def notify_views(self):
		pass

	def fetch(self, pattern):
		"""fetch reflects current state of datastore"""
		found = self.dbInt.fetch(pattern)
		if found:
			self.initGraph.update(found)
			self.workingGraph.update(found)
			res = found.sample().res
			return res
		else:
			return None

	def fetchAll(self, pattern):
		found = self.dbInt.fetchAll(pattern)
		if found:
			self.initGraph.update(found)
			self.workingGraph.update(found)
			res = { f.res for f in found}
			return res
		else:
			return None

	def commit(self):
		if self.initGraph != self.workingGraph:
			remove = self.initGraph - self.workingGraph
			add = self.workingGraph - self.initGraph
			self.dbInt.executeUpdate(add=add, remove=remove)
			self.initGraph.clear()
			self.workingGraph.clear()
		self.close()

	def rollback(self):
		self.workingGraph = self.initGraph

	def close(self):
		if self.initGraph != self.workingGraph:
			raise "Uncommited changes!"
		else:
			for view in self.views:
				del view