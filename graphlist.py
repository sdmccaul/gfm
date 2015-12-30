from collections import MutableSequence
import types

TruthType = (types.NoneType, types.BooleanType)

SingleType = (types.StringType, types.UnicodeType,
                types.IntType, types.LongType,
                types.FloatType, types.ComplexType)

ListType = types.ListType

def filter_set(tset, pattern):
	return [ t[2] for t in tset
                if (t[0], t[1]) == (pattern[0], pattern[1])]

def filter_subject_predicates(tset, pattern):
	return {t for t in tset
				if (t[0], t[1]) == (pattern[0], pattern[1])}

def get_predicates(tset):
	return { t[1] for t in tset }

def get_objects(tset):
	return { t[2] for t in tset }

def make_triple(s,p,o):
	return (s,p,o)

class GraphList(MutableSequence):
    """A list interface
       for graph data"""

    def __init__(self, graph, edge, **kwargs):
        self.edge = edge
        self.graph = graph

    def __getitem__(self, key):
        pattern = (key, self.edge, None)
        return filter_set(self.graph, pattern)

    def __setitem__(self, key, value):
        pass

    def __delitem__(self, key):
    	pass

    def insert(self):
        pass

    def __len__(self):
        pass