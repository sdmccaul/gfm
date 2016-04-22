from collections import defaultdict

from graphset import GraphSet
from graphstatements import Statement, Required, URI
from graphdb import GraphInterface

class Session(object):

	def __init__(self, graphInt, initGraph=GraphSet()):
		self.graphStore = graphInt
		self.initGraph = initGraph
		self.views = []
		self.resources = defaultdict(GraphSet)

	def mergeDataGraphs(self, gsetList):
		return GraphSet([stmt for gset in gsetList
							for stmt in gset])

	def prepDataGraphs(self, gsetList):
		return GraphSet(
			[Statement(stmt.sbj, stmt.prp, stmt.obj)
				for gset in gsetList
					for stmt in gset])

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

	def fetch(self, model):
		"""fetch reflects current state of datastore"""
		found = self.graphStore.fetch(model.querySet())
		if found:
			res = URI(found.keys()[0])
			self.resources[res].update(found[res])
			self.initGraph.update(found[res])
			return res
		else:
			return None

	def fetchAll(self, model):
		found = self.graphStore.fetchAll(model.querySet())
		if found:
			res = [ URI(f) for f in found.keys() ]
			for r in res:
				self.resources[r].update(found[r])
				self.initGraph.update(found[r])
			return res
		else:
			return None

	def commit(self):
		workingGraph = self.prepDataGraphs(self.resources.values())
		if self.initGraph != workingGraph:
			remove = self.initGraph - workingGraph
			add = workingGraph - self.initGraph
			rmvResp = self.graphStore.update(data=remove, action="remove")
			addResp = self.graphStore.update(data=add, action="add")
			if (addResp.status_code != 200 or rmvResp.status_code != 200) :
				raise "Bad update!"
			self.initGraph.clear()
		self.close()

	def rollback(self):
		self.workingGraph = self.initGraph

	def close(self):
		for view in self.views:
			del view