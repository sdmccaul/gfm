from collections import defaultdict

from datasets import DataSet, Required
from graphdb import QueryInterface

class Session(object):

	def __init__(self, dbInt, initGraph=DataSet([])):
		self.dbInt = dbInt
		self.initGraph = initGraph
		self.workingGraph = initGraph.copy()
		self.views = []
		self.viewIndex = defaultdict(list)

	def register(self, view):
		if view.pattern(res=view.uri) in self.workingGraph:
			view.setGraph(self.workingGraph)
			self.views.append(view)
			self.viewIndex[view.__class__.__name__].append(view.uri)
		else:
			raise ("Pattern not found!")

	def unregister(self, view):
		if view.pattern(res=view.uri) in self.workingGraph:
			view.unsetGraph()
			self.views.remove(view)
			self.viewIndex[view.__class__.__name__].remove(view.uri)
		else:
			raise ("Pattern not found!")

	def notify_views(self):
		pass

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

	def commit(self):
		pass

	def rollback(self):
		pass

	def close(self):
		pass