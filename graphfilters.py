from collections import namedtuple

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

def set_filter(tset, pattern):
    return {t for t in tset if t == pattern}

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