from collections import MutableSequence
from graphfilters import Triple
import types

TruthType = (types.NoneType, types.BooleanType)

SingleType = (types.StringType, types.UnicodeType,
                types.IntType, types.LongType,
                types.FloatType, types.ComplexType)

ListType = types.ListType

def get_objects(tset):
    return { t[2] for t in tset }

def make_triple(s,p,o):
	return Triple(s,p,o)

def set_filter(tset, pattern):
    return {t for t in tset if t == pattern}

class GraphList(MutableSequence):
    """A list interface
       for graph data"""

    def __init__(self, graph, edge, **kwargs):
        self.edge = edge
        self.graph = graph

    def __getitem__(self, key):
        pattern = Triple(key, self.edge, None)
        return get_objects(set_filter(self.graph, pattern))

    def __setitem__(self, key, value):
        if not value or isinstance(value, TruthType):
            self.__delitem__(key)
            return
        elif isinstance(value, SingleType):
            self.__delitem__(key)
            add = { make_triple(key, self.edge, value) }
        elif isinstance(value, ListType):
            self.__delitem__(key)
            add = { make_triple(key, self.edge, v)
                        for v in value }
        else:
            raise Exception(
                "expected iterable, string or num")
        self.graph.update(add)

    def __delitem__(self, key):
        pattern = Triple(key, self.edge, None)
        rmv = set_filter(self.graph, pattern)
        self.graph.difference_update(rmv)

    def __len__(self):
        pattern = Triple(None, self.edge, None)
        return len(set_filter(self.graph, pattern))

    def insert(self, key, value):
        pattern = Triple(key, self.edge, value)
        self.graph.add(pattern)