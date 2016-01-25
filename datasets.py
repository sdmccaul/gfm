from collections import MutableSet, namedtuple

class DataSet(MutableSet):
	def __init__(self, iterable=None):
		self.data = set()
		if iterable is not None:
			self |= iterable

	def __contains__(self, key):
		if isinstance(key, Datum):
			for d in self.data:
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

	def add(self, key):
		self.data.add(key)

	def discard(self, key):
		self.data.discard(key)

	def find(self, pattern):
		if isinstance(pattern, DataSet):
			if pattern <= self: #Warning!! ORDER MATTERS
				return pattern & self # != self & pattern
		elif isinstance(pattern, Datum):
			if pattern in self:
				ds = DataSet() #DataSet().add(pattern) returns NoneType?
				ds.add(pattern)
				return ds & self #call to self.find(ds) not working
		else:
			raise TypeError("expected data or dataset")
		return DataSet()

	def difference(self, pattern):
		if pattern in self:
			remove = pattern & self
			return self - remove

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