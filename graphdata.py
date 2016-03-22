from graphdatatypes import URI
from collections import MutableSet, Iterable, namedtuple

def graphFilter(graph, key, value): 
	return DataGraph([d for d in graph
							if getattr(d,key) == value])

class DataGraph(MutableSet):
	def __init__(self, iterable=None):
		self.data = set()
		if iterable is not None:
			self |= iterable				

	#Getters and setters for Resource Graph properties
	@property
	def node(self):
		return self._node

	@node.setter
	def node(self, uri):
		self._node = URI(uri)

	@property
	def arrows(self):
		return { d.att for d in self.data }

	@property
	def successors(self):
		return { d.val for d in self.data if isinstance(d, URI)}

	# BEGIN REQUIRED MutableSet DEFINITIONS
	def __contains__(self, key):
		for d in self:
			if d == key:
				return True
		return False

	def __iter__(self):
		return self.data.__iter__()

	def __len__(self):
		return len(self.data)

	def add(self, gdata):
		if isinstance(gdata, ResourceData):
			self.data.add(gdata)
		else:
			raise TypeError("Expecting ResourceData object")

	def discard(self, gdata):
		if isinstance(gdata, ResourceData):
			self.data.discard(gdata)
		else:
			raise TypeError("Expecting ResourceData object")

	# END REQUIRED MutableSet DEFINITIONS

	def sample(self):
		"""Copied from pop(), but no discard."""
		it = iter(self)
		try:
			value = next(it)
		except StopIteration:
			raise KeyError
		return value

	def query(self, **kwargs):
		reply = self.data
		for kwarg in kwargs:
			if kwargs[kwarg]:
				reply = graphFilter(reply, kwarg, kwargs[kwarg])
		return reply

	def query_and_remove(self, **kwargs):
		rmv = self.query(**kwargs)
		self -= rmv

	def update(self, other):
		self |= other

	def copy(self):
		data = [ d for d in self.data ]
		return DataGraph(data)

ResourceData = namedtuple('ResourceData',['res', 'att', 'val'])

class QueryGraph(DataGraph):

	def __init__(self):
		self.filters = {}
		super(QueryGraph, self).__init__()

	def transform(self, other):
		out = DataGraph()
		for e in self:
			resp = other.query(**e)
			if resp:
				mapped = e.attr(resp.res, resp.val)
				out.add(mapped)
		return out