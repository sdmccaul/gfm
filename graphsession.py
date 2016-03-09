from collections import defaultdict

from resourcegraphs import ResourceGraph
from graphattributes import Required
from graphdb import GraphInterface

class Session(object):

	def __init__(self, graphInt, initGraph=ResourceGraph()):
		self.graphStore = graphInt
		self.initGraph = initGraph
		self.views = []
		self.resources = defaultdict(ResourceGraph)

	def mergeResourceGraphs(self, dsetList):
		return ResourceGraph([dtm for dset in dsetList
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
		found = self.graphStore.fetch(pattern)
		if found:
			res = found.keys()[0]
			self.resources[res].update(found[res])
			self.initGraph.update(
				self.mergeResourceGraphs(found.values()
					))
			return res
		else:
			return None

	def fetchAll(self, pattern):
		found = self.graphStore.fetchAll(pattern)
		if found:
			res = [ f for f in found.keys() ]
			for r in res:
				self.resources[r].update(found[r])
			self.initGraph.update(
				self.mergeResourceGraphs(found.values()
					))
			return res
		else:
			return None

	def commit(self):
		workingGraph = self.mergeResourceGraphs(self.resources.values())
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