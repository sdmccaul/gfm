from collections import MutableSet, namedtuple
from itertools import ifilter

def match_tuple(t1, pattern):
	if t1 == pattern:
		return t1

def key_subject(t1):
	return (t1[0], t1)

def filter_subject(tset, pattern):
	return {t for t in tset if t[0] == pattern[0]}

def transform_tuple(t1, pattern):
	for pos, v in enum(pattern):
		if v is None:
			t1[pos]

def filter_predicates(tset, pattern):
	return { t for t in tset if t[1] == pattern[1] }

def filter_subject_predicates(tset, pattern):
	return {t for t in tset
				if (t[0], t[1]) == (pattern[0], pattern[1])}

def get_predicates(tset):
	return { t[1] for t in tset }

def get_objects(tset):
	return [ t[2] for t in tset ]

def get_resources(tset):
	return { t.res for t in tset }

def map_resource(resource, pattern):
	_, a, v = pattern
	return Datum(resource, a, v)

def set_resources(pattern, resource_list):
	return [ map_resource(r, pattern) for r in resource_list ]

def match_data(graph, pattern_list):
	return [ set_filter(graph, p) for p in pattern_list ]

def match_resource(graph, pattern):
	return get_resources(set_filter(graph, pattern))

def match_resource_list(graph, pattern, resources = [None]):
	matches = []
	for r in resources:
		set_pattern = set_resource(r, pattern)
		matched = match_resource(graph, set_pattern)
		if matched:
			matches.extend(matched)
	return matches

def match_multiple_patterns(graph, pattern_list):
	out = [ set_filter(graph, p) for p in pattern_list ]
	return out

def match_all_resources(graph, pattern, resource_list):
	mapped_data = [ map_resource(r, pattern) for r in resource_list]
	return match_multiple_patterns(graph, mapped_data)

def set_filter(tset, pattern):
	return {t for t in tset if t == pattern}

def match_resources(graph, dataset):
	resource_list = get_resources(pattern_list)
	for pattern in pattern_list:
		mapped_data = [ map_resource(r, pattern) for r in resource_list ]


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
		if isinstance(pattern, Datum):
			if pattern in self:
				ds = DataSet() #DataSet().add(pattern) returns NoneType
				ds.add(pattern)
				return ds & self
		elif isinstance(pattern, DataSet):
			if pattern <= self:
				return pattern & self
		else:
			raise TypeError("expected data or dataset")
		return DataSet()

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