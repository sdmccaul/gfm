def match_tuple(t1, pattern):
	if t1 == pattern:
		return t1

def key_subject(t1):
	return (t1[0], t1)

def filter_subject(tset, pattern):
	return {t for t in tset if t[0] == pattern[0]}

def filter_subject_predicates(tset, pattern):
	return {t for t in tsest
				if t[0], t[1] == pattern[0], pattern[1]}

def get_objects(tset):
	return { t[2] for t in tset }

def transform_tuple(t1, pattern):
	for pos, v in enum(pattern):
		if v is None:
			t1[pos]