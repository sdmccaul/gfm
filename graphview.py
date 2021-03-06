from graphattributes import Edge, Required, Linked, Optional
from graphdatatypes import URI
from graphdata import DataGraph, ResourceData
from graphquery import QueryGraph

class Resource(object):
    def __init__(self, uri, graph=None):
        self.graph = graph
        self.uri = URI(uri)
        # [0] index needed because Edges now return Datum lists
        # in order to accommodate prerequisite property values
        # consider side effects, alternatives
        # [0][1] index now necessary for .model() functions
        # getting pretty ugly
        self.edges = {
            getattr(self.__class__,k)[0][1].att: k
                for k, v in self.__class__.__dict__.items()
                    if isinstance(v, Edge)
        }

    def __getitem__(self, key):
        return getattr(self, self.edges.__getitem__(key))

    def __setitem__(self, key, value):
        setattr(self, self.edges.__getitem__(key), value)

    def __delitem__(self, key):
        delattr(self, self.edges.__getitem__(key))

    def update(self):
        pass

    def destroy(self):
        pass

    @classmethod
    def model(cls, res=None):
        qset = QueryGraph()
        for k,v in cls.__dict__.items():
            if isinstance(v, Edge):
                edges = getattr(cls,k)
                for func, rdata in edges:
                    if res:
                        qset.resource = res.rdf
                        rdata = rdata._replace(res=res)
                    qualified = rdata._replace(**(
                        { k: getattr(rdata,k).rdf
                            for k in rdata._fields
                                if getattr(rdata,k) }
                             ))
                    qset.add(qualified)
                    qset.filters[qualified] = func
        return qset

    @classmethod
    def find(cls, uri, session):
        res = session.fetch(cls.model(URI(uri)))
        if res:
            rsc = cls(res)
            session.register(rsc)
            return rsc
        else:
            raise "Resource not found"

    @classmethod
    def findAll(cls, session):
        res = session.fetchAll(cls.model())
        if res:
            rscs = [ cls(r) for r in res ]
            for rsc in rscs:
                session.register(rsc)
            return rscs
        else:
            raise "Resources not found"

    @classmethod
    def new(cls, session, **params):
        uri = session.mint_new_uri(cls.prefix)
        rsc = cls(uri)
        session.register(rsc)
        rsc.update(**params)
        return rsc

    @classmethod
    def destroy(session, cls, uri):
        rsc = cls.find(uri)
        for k in rsc:
            del k
        graph.register(rsc)
        return rsc

    def to_dict(self):
        out = {"@id": self.uri}
        for e in self.edges:
            out[e] = self[e]
        return out

    # def __len__(self):
    #     return len(self.graph)   