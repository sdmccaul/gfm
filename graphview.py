from graphedges import Edge
from graphstatements import URI
from graphset import GraphSet
from graphquery import QueryGraph

class ResourceView(object):
    def __init__(self, uri, graph=None):
        self.graph = graph
        self.uri = URI(uri)
        self.edges = {
            v.prp: k
                for k, v in self.__class__.__dict__.items()
                    if isinstance(v, Edge)
        }

    def __getitem__(self, key):
        return getattr(self, self.edges.__getitem__(key))

    def __setitem__(self, key, value):
        setattr(self, self.edges.__getitem__(key), value)

    def __delitem__(self, key):
        delattr(self, self.edges.__getitem__(key))

    def update(self, data):
        for k, v in data.items():
            self.__setitem__(k, v)
        return True

    def destroy(self):
        pass

    def save(self, session):
        session.commit()

    @classmethod
    def model(cls, res=None):
        qset = QueryGraph()
        for k,v in cls.__dict__.items():
            if isinstance(v, Edge):
                stmts = getattr(cls,k)
                for stmt in stmts:
                    if res:
                        qset.resource = res
                        stmt = stmt._replace(sbj=res)
                    qset.add(stmt)
        return qset

    @classmethod
    def find(cls, uri, session):
        res = session.fetch(cls.model(URI(uri)))
        if res:
            rsc = cls(res)
            session.register(rsc)
            return rsc
        else:
            raise Exception("Resource not found: {0}".format(uri))

    @classmethod
    def findAll(cls, session):
        res = session.fetchAll(cls.model())
        if res:
            rscs = [ cls(r) for r in res ]
            for rsc in rscs:
                session.register(rsc)
            return rscs
        else:
            raise Exception("Resources not found")

    @classmethod
    def new(cls, session, params):
        uri = session.mintNewUri(cls.prefix)
        rsc = cls(uri)
        session.register(rsc)
        rsc.update(params)
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