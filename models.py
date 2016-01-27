from graphattributes import Attribute
import properties

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

def alias_namespace(fnc):
    mod = prop.__module__
    nme = prop.__name__
    return mod+":"+name

def get_func_from_attr(attr):
    pass

class Resource(object):
    def __init__(self, uri, graph=set()):
        # self._init_graph = graph
        # self.graph = self._init_graph.copy()
        self.graph = graph
        self.uri = uri
        self.node = self.uri
        self.edges = {
            getattr(self.__class__,k).att: k
                for k, v in self.__class__.__dict__.items()
                    if isinstance(v, Attribute)
        }
        # self.node = node
        # for k in cls.__dict__.keys():
        #     if not startswith(k, '__'):
        #         _ , edge, _ = k()
        #         self[edge] = None

    def __getitem__(self, key):
        attr = self.edges.__getitem__(key)
        return getattr(self,attr)

    def __setitem__(self, key, value):
        attr = self.edges.__getitem__(key)
        setattr(self, attr, value)

    def __delitem__(self, key):
        attr = self.edges.__getitem__(key)
        delattr(self, attr)
    # def update(self, update_dict):
    #     for k, v in update_dict.items():


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
    rdfType = Attribute(properties.rdfType)
    rdfsLabel = Attribute(properties.rdfsLabel)
    foafFirstName = Attribute(properties.foafFirstName)
    foafLastName = Attribute(properties.foafLastName)
    vivoPreferredTitle = Attribute(properties.vivoPreferredTitle)
    blocalShortId = Attribute(properties.blocalShortId)