from graphstatements import Statement, URI
from collections import MutableSet

def graphFilter(graph, key, value): 
	return GraphSet([d for d in graph
							if getattr(d,key) == value])

class GraphSet(MutableSet):
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

	def add(self, stmt):
		if isinstance(stmt, Statement):
			self.data.add(stmt)
		else:
			raise TypeError("Expecting Statement object")

	def discard(self, stmt):
		if isinstance(stmt, Statement):
			self.data.discard(stmt)
		else:
			raise TypeError("Expecting Statement object")

	# END REQUIRED MutableSet DEFINITIONS

	def sample(self):
		"""Copied from pop(), but no discard."""
		it = iter(self)
		try:
			value = next(it)
		except StopIteration:
			raise KeyError
		return value

	def query(self, **stmt):
		reply = self.data
		for val in stmt:
			if stmt[val]:
				reply = graphFilter(reply, val, stmt[val])
		return reply

	def query_and_remove(self, **kwargs):
		rmv = self.query(**kwargs)
		self -= rmv

	def update(self, other):
		self |= other

	def copy(self):
		data = [ d for d in self.data ]
		return GraphSet(data)