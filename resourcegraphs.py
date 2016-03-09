from graphdatatypes import URI
from collections import MutableSet, Iterable, namedtuple

def graphFilter(graph, key, value): 
	return ResourceGraph([d for d in graph
							if getattr(d,key) == value])

class ResourceGraph(MutableSet):
	def __init__(self, iterable=None):
		self.data = set()
		self._node = None
		if iterable is not None:
			self.node = URI(
				next(iter(iterable)).res)
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
			if self.node:
				if gdata.res == self.node:
					self.data.add(gdata)
				else:
					raise ValueError("Bad resource value")
			else:
				self.data.add(gdata)
		else:
			raise TypeError("Expecting ResourceData object")

	def discard(self, gdata):
		if isinstance(gdata, ResourceData):			
			if self.node:
				if gdata.res == self.node:
					self.data.discard(gdata)
				else:
					raise ValueError("Bad resource value")
			else:
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
		rmv = self.query(kwargs)
		self -= rmv

	def update(self, other):
		self |= other

	def copy(self):
		data = [ d for d in self.data ]
		return ResourceGraph(data)

ResourceData = namedtuple('ResourceData',['res', 'att', 'val'])