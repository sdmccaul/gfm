def match(triple, place, pattern):
	if pattern:
		if triple[place]==pattern:
			return triple
	else:
		return triple

def search(triples, pattern):
	s, p, o = pattern
	for t in triples:
		if match(match(match(t,0,s),1,p),2,o):
			yield t

def get_triple_objects(triples):
	for t in triples:
		yield t[2]