from graphdatatypes import URI
from collections import MutableSet, Iterable, namedtuple

def graphFilter(graph, key, value): 
	return ResourceGraph([d for d in graph
							if getattr(d,key) == value])

class ResourceGraph(MutableSet):

	# Defining an iterable input is essential for certain functions
	# https://github.com/python-git/python/blob/master/Lib/_abcoll.py
	# 
	# Considered allowing singleton init values, but decided against.
	# This preserves standard interface for Python sets
	# ie: set('cat') => {'c','a','t'}
	# ie: set(3) => TypeError: 'int' object is not iterable
	def __init__(self, iterable=None):
		self.data = set()
		self._node = None
		if iterable is not None:
			self.node = URI(
				next(iter(iterable)).res)
			self |= iterable				

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

	def sample(self):
		"""Copied from pop(), but no discard."""
		it = iter(self)
		try:
			value = next(it)
		except StopIteration:
			raise KeyError
		return value

	def add(self, gdata):
		if gdata.res == self.node:
			self.data.add(gdata)
		else:
			raise TypeError("Expecting Datum object")

	def discard(self, gdata):
		if gdata.res == self.node:
			self.data.discard(gdata)
		else:
			raise TypeError("Expecting Datum object")

	# END REQUIRED MutableSet DEFINITIONS

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