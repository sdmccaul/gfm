from collections import MutableMapping
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
    return { t for t in tset if t == pattern }

class GraphDict(MutableMapping):
    """A dictionary interface
       for graph data"""

    def __init__(self, node, graph, **kwargs):
        self.node = node
        self.graph = graph

    def __getitem__(self, key):
        pattern = (self.node, key, None)
        return list(get_objects(
            filter_subject_predicates(self.graph, pattern)
            ))

    def __setitem__(self, key, value):
        self.__delitem__(key)
        if not value or isinstance(value, TruthType):
            return
        elif isinstance(value, SingleType):
            add = { make_triple(self.node, key, value) }
        elif isinstance(value, ListType):
            add = { make_triple(self.node, key, v)
                        for v in value }
        else:
            raise Exception(
                "expected iterable, string or num")
        self.graph.update(add)

    def __delitem__(self, key):
    	pattern = (self.node, key, None)
    	rmv = filter_subject_predicates(self.graph, pattern)
    	self.graph.difference_update(rmv)

    def keys(self):
        pattern = (self.node, None, None)
    	return list(get_predicates(
                filter_subject(self.graph, pattern)))

    def values(self):
        pattern = (self.node, None, None)
    	return list(get_objects(
                filter_subject(self.graph, pattern)))

    def items(self):
        pattern = (self.node, None, None)
        return [ (p, self.__getitem__(p))
                    for p in get_predicates(
                        filter_subject(self.graph, pattern))
                ]
    def __iter__(self):
        pattern = (self.node, None, None)
        return iter(filter_subject(self.graph, pattern))

    def __len__(self):
        pattern = (self.node, None, None)
        return len(filter_subject(self.graph, pattern))