from graphdict import GraphDict
from collections import defaultdict

def get_property_object(triples):
    for stmt in triples:
        yield stmt[2]

def match_property(triples, ppty):
    for stmt in triples:
        if stmt[1] == ppty:
            yield stmt

def property_lookup(triples, ppty):
    out = [ obj for obj in get_property_object(
                match_property(triples, ppty)) ]
    if len(out) == 1:
        return out[0]
    else:
        return out

def set_to_dict(sin, din):
    for s in sin:
        din[s[1]].append(s[2])

def dict_to_set(din,sin):
    sin.clear()
    s = din['@id'][0]
    for p, v in din.items():
        if p == '@id':
            continue
        for o in v:
            sin.add((s,p,o))

class GraphEditor(object):
    def __init__(self, node=None):
        self._init_graph = None
        self.graph = None
        self.node = node

    def load(self, graph):
        self._init_graph = graph
        self.graph = self._init_graph.copy()
        set_to_dict(self._init_graph, self._dict)

    def unload(self):
        dict_to_set(self._dict, self.graph)

    def __getitem__(self, key):
        pattern = Triple(self.node, key, None)
        return get_objects(set_filter(self.graph, pattern))

    def __setitem__(self, key, value):
        if not value or isinstance(value, TruthType):
            self.__delitem__(key)
            return
        elif isinstance(value, SingleType):
            self.__delitem__(key)
            add = { make_triple(self.node, key, value) }
        elif isinstance(value, ListType):
            self.__delitem__(key)
            add = { make_triple(self.node, key, v)
                        for v in value }
        else:
            raise Exception(
                "expected iterable, string or num")
        self.graph.update(add)

    def __delitem__(self, key):
        pattern = Triple(self.node, key, None)
        rmv = set_filter(self.graph, pattern)
        self.graph.difference_update(rmv)

    def __len__(self):
        return len(self.graph)

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

from graphproperties import MultiValued
import properties

class FisFaculty(object):
    rdfType = MultiValued(properties.rdfType)
    # rdfClass = "http://vivoweb.org/ontology/core#FacultyMember"

    # predicates = [
    #     '<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>',
    #     '<http://www.w3.org/2000/01/rdf-schema#label>',
    #     '<http://xmlns.com/foaf/0.1/firstName>',
    #     '<http://xmlns.com/foaf/0.1/lastName>',
    #     '<http://vivoweb.org/ontology/core#preferredTitle>',
    #     '<http://vivo.brown.edu/ontology/vivo-brown/shortId>',
    # ]

    def __init__(self, graph, uri):
        self.graph = graph
        self.node = uri