from collections import MutableSet, Iterable, namedtuple

class DataSet(MutableSet):

	# Defining an iterable input is essential for certain functions
	# https://github.com/python-git/python/blob/master/Lib/_abcoll.py
	# 
	# Considered allowing singleton init values, but decided against.
	# This preserves standard interface for Python sets
	# ie: set('cat') => {'c','a','t'}
	# ie: set(3) => TypeError: 'int' object is not iterable
	def __init__(self, iterable=None):
		self.data = set()
		if iterable is not None:
			self |= iterable				

	# BEGIN REQUIRED MutableSet DEFINITIONS
	def __contains__(self, key):
		if isinstance(key, Datum):
			for d in self:
				if d == key:
					return True
			return False
		elif isinstance(key, DataSet):
			for k in key:
				if k in self:
					continue
				return False
			return True
		else:
			raise TypeError("expected data or dataset")

	def __iter__(self):
		return self.data.__iter__()

	def __len__(self):
		return len(self.data)

	def sample(self):
		"""Copied from pop(), but no discard."""
		it = iter(self)
		try:
			value = next(it)
		except StopIteration:
			raise KeyError
		return value

	def add(self, key):
		if isinstance(key, Datum):
			self.data.add(key)
		else:
			raise TypeError("Expecting Datum object")

	def discard(self, key):
		if isinstance(key, Datum):
			self.data.discard(key)
		else:
			raise TypeError("Expecting Datum object")

	# END REQUIRED MutableSet DEFINITIONS

	def query(self, pattern):
		# Ordering matters due to abc __and__ implementation
		# pattern & self != self & pattern
		# Query datum must be in first position
		if pattern in self:
			if isinstance(pattern, DataSet):
				return pattern & self
			elif isinstance(pattern, Datum):
				return DataSet({pattern}) & self
		else:
			return DataSet()

	def query_and_remove(self, pattern):
		rmv = self.query(pattern)
		self -= rmv

	def update(self, other):
		self |= other

	def copy(self):
		data = [ d for d in self.data ]
		return DataSet(data)

	# def find(self, pattern):
	# 	pass
		

class Datum(namedtuple('Datum',['res', 'att', 'val'])):
	def __eq__(self, other):
		eqs = { (a == b) if (a is not None and b is not None)
					else True
						for a,b in zip(self, other) }
		if False in eqs:
			return False
		else:
			return True

	def __ne__(self, other):
		eqs = { (a == b) if (a is not None and b is not None)
					else True
						for a,b in zip(self, other) }
		if False in eqs:
			return True
		else:
			return False