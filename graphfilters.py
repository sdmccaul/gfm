from collections import namedtuple

def match_tuple(t1, pattern):
	if t1 == pattern:
		return t1

def key_subject(t1):
	return (t1[0], t1)

def filter_subject(tset, pattern):
	return {t for t in tset if t[0] == pattern[0]}

def filter_subject_predicates(tset, pattern):
	return {t for t in tsest
				if (t[0], t[1]) == (pattern[0], pattern[1])}

def get_objects(tset):
	return { t[2] for t in tset }

def transform_tuple(t1, pattern):
	for pos, v in enum(pattern):
		if v is None:
			t1[pos]

def fiter_set(tset, pattern=(None,None,None)):
	matcher = [ val for val in pattern if val ]
	return { t for t in matcher }

class Triple(namedtuple('Triple',['sbj', 'prd', 'obj'])):
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