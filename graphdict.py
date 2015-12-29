from collections import MutableMapping
import types

TruthType = (types.NoneType, types.BooleanType)

SingleType = (types.StringType, types.UnicodeType,
                types.IntType, types.LongType,
                types.FloatType, types.ComplexType)

ListType = types.ListType



def filter_subject(tset, pattern):
	return {t for t in tset if t[0] == pattern[0]}

def filter_subject_predicates(tset, pattern):
	return {t for t in tset
				if (t[0], t[1]) == (pattern[0], pattern[1])}

def get_predicates(tset):
	return { t[1] for t in tset }

def get_objects(tset):
	return { t[2] for t in tset }

def make_triple(s,p,o):
	return (s,p,o)

class GraphDict(MutableMapping):
    """A dictionary interface
       for graph data"""

    def __init__(self, graph, uid, *args, **kwargs):
        self.graph = graph
        self.uid = uid
        pattern = (uid, None, None)
        for p in get_predicates(filter_subject(graph, pattern)):
        	self.__dict__.setdefault(p)

    def __getitem__(self, key):
    	pattern = (self.uid, key, None)
        return get_objects(
        		filter_subject_predicates(self.graph, pattern)
        		)

    def __setitem__(self, key, value):
        self.__delitem__(key)
        if not value or isinstance(value, TruthType):
            return
        elif isinstance(value, SingleType):
            add = { make_triple(self.uid, key, value) }
        elif isinstance(value, ListType):
            add = { make_triple(self.uid, key, v)
                        for v in value }
        else:
            raise Exception(
                "expected iterable, string or num")
        self.graph.update(add)

    def __delitem__(self, key):
    	pattern = (self.uid, key, None)
    	rmv = filter_subject_predicates(self.graph, pattern)
    	self.graph.difference_update(rmv)

    def keys(self):
    	return self.__dict__.keys()

    def values(self):
    	return self.__dict__.values()

    def items(self):
    	return self.__dict__.items()

    def __iter__(self):
        return iter(filter_subject(self.graph, self.uid))

    def __len__(self):
        return len(filter_subject(self.graph, self.uid))