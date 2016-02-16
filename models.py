from collections import defaultdict
from graphattributes import Edge
from datasets import DataSet, Datum, Required, Linked, Optional
import properties


class Resource(object):
    def __init__(self, uri, graph=set()):
        self.graph = graph
        self.uri = uri
        self.node = self.uri
        self.edges = {
            getattr(self.__class__,k).att: k
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
        for k in cls.__dict__.keys():
            att = getattr(cls,k)
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
    def find(dset, cls, uri):
        res = dset.find(cls.pattern(uri))
        if res:
            rsc = cls(res, dset)
            dset.register(rsc)
            return rsc
        else:
            raise "Resource not found"

    @classmethod
    def all(cls, session):
        res = session.query(cls.pattern())
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

class Thing(object):
    def __init__(self):
        self.rdfClass="owl:Thing"
        self.uri = None

    def set_uri(rabid=None,prefix="http://vivo.brown.individual/"):
        if rabid is None:
            raise Exception("rabid need for uri creation")
        self.uri = prefix + rabid

    def new(self, prefix=None):
        generate_uri(self, prefix)

    def all(self, filters=None):
        construct = [
            (None, 'rdf:type', self.rdfClass),
            (None, 'rdfs:label', None)
            ]
        where =     [
            (None, 'rdf:type', self.rdfClass),
            (None, 'rdfs:label', None)
            ]
        if filters:
            for p,o in filters.items():
                where.append((None,p,o))
        results = sparql.construct(construct,where)
        for s,p,o in results.graph.triples( (None, None, None)):
            print s,p,o

    def find(self, uri=None):
        q = u"""
        CONSTRUCT {{
            <{uri}> ?p ?o .
            ?o rdfs:label ?label .
        }}
        WHERE {{
            <uri> rdf:type {rdfClass} .
            <{uri}> ?p ?o .
            OPTIONAL {{ ?o rdfs:label ?label . }}
        }}
        """.format(uri=uri)
        results = sparql.query(q).graph
        for s,p,o in results.triples( (None, None, None)):
            print s,p,o

class Credential(Thing):
    rdfClass = "bprofile:Credential"
    
    @classmethod
    def all(cls):
        result = sparql.all(rdfClass=cls.rdfClass)
        for r in result:
            print r

    def __init__(self, uri=None, stmts=None):
        self.rdfClass = 'bprofile:Credential'
        self.rabid = None
        self.uri = uri
        self.triples = [
            ('foo','rdf:type',self.rdfClass),
            ('foo','bprofile:credentialFor','bar')
        ]
        if stmts:
            self.triples = [s for s in stmts]


    def rdfType(self):
        return properties.rdfType(obj=self.rdfClass)

    def credentialFor(self):
        return property_lookup(
            self.triples,
            'http://vivo.brown.edu/ontology/profile#credentialFor')

    @classmethod
    def new(cls):
        pass

    @classmethod
    def create(cls):
        pass

    @classmethod
    def find(cls, rabid=None):
        if rabid is None:
            raise Exception("No rabid provided")
        uri = "http://vivo.brown.edu/individual/" + rabid
        stmts = sparql.describe(uri)
        if stmts:
            return Credential(uri=uri,stmts=stmts)

    def update(self):
        pass

    def save(self):
        pass

    def destroy(self):
        pass

class FisFaculty(Resource):
    rdfType = Edge(properties.rdfType,Required,
        values=[
            'http://vivoweb.org/ontology/core#FacultyMember',
            'http://vivo.brown.edu/ontology/vivo-brown/BrownThing'
            ])
    shortId = Edge(properties.blocalShortId, Required) 
    label = Edge(properties.rdfsLabel, Optional)
    first = Edge(properties.foafFirstName, Optional)
    last = Edge(properties.foafLastName, Optional)
    title = Edge(properties.vivoPreferredTitle, Optional)
