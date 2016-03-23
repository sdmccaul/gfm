from collections import defaultdict

from graphdata import DataGraph, ResourceData
from graphattributes import Required
from graphdb import GraphInterface
from graphdatatypes import URI

class Session(object):

	def __init__(self, graphInt, initGraph=DataGraph()):
		self.graphStore = graphInt
		self.initGraph = initGraph
		self.views = []
		self.resources = defaultdict(DataGraph)

	def mergeDataGraphs(self, dsetList):
		return DataGraph([dtm for dset in dsetList
							for dtm in dset])

	def prepDataGraphs(self, dsetList):
		return DataGraph(
			[ResourceData(dtm.res.rdf, dtm.att.rdf, dtm.val.rdf)
				for dset in dsetList
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

	def fetch(self, model):
		"""fetch reflects current state of datastore"""
		found = self.graphStore.fetch(model.querySet())
		if found:
			res = URI(found.keys()[0])
			self.resources[res].update(
				model.transform(found[res.rdf]))
			self.initGraph.update(
				self.mergeDataGraphs(found.values()
					))
			return res
		else:
			return None

	def fetchAll(self, model):
		found = self.graphStore.fetchAll(model.querySet())
		if found:
			res = [ URI(f) for f in found.keys() ]
			for r in res:
				self.resources[r].update(
					model.transform(found[r.rdf]))
			self.initGraph.update(
				self.mergeDataGraphs(found.values()
					))
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