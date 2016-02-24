from graphattributes import Edge, Required, Linked, Optional
from datasets import DataSet

class Resource(object):
    def __init__(self, uri, graph=None):
        self.graph = graph
        self.uri = uri
        # [0] index needed because Edges now return Datum lists
        # in order to accommodate prerequisite property values
        # consider side effects, alternatives
        self.edges = {
            getattr(self.__class__,k)[0].att: k
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
    def pattern(cls, res=None):
        qset = DataSet([])
        for k,v in cls.__dict__.items():
            if isinstance(v, Edge):
                attValList = getattr(cls,k)
                for att in attValList:
                    if isinstance(att, Required):
                        qset.add(att._replace(res=res))
                    elif isinstance(att, Optional):
                        qset.add(att._replace(res=res))
                    elif isinstance(att, Linked):
                        qset.add(att._replace(val=res))
                    else:
                        continue
        return qset

    @classmethod
    def find(cls, uri, session):
        res = session.fetch(cls.pattern(uri))
        if res:
            rsc = cls(res)
            session.register(rsc)
            return rsc
        else:
            raise "Resource not found"

    @classmethod
    def findAll(cls, session):
        res = session.fetchAll(cls.pattern())
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