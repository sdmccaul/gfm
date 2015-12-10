from rdflib import Graph
import rdflib

from vdm.namespaces import VIVO, TMP, BLOCAL
from vdm.models import BaseResource, VResource, FacultyMember

from sparqldb import SparqlInterface

import logging

sparql = SparqlInterface()

# class TripleInterface(object):
#     def __init__(self):
#         self.rdfClass = None
#         self.subject = None
#         self.label = None
#         self.statements = None

#     def new(self):
#         pass

#     def all(self, filter_map):
#         pass

#     def find(self, find_by_map):
#         pass

#     def update(self, property_map):
#         pass

#     def save(self):
#         pass

#     def destroy(self):
#         pass

#     def create(self):
#         pass

class Thing(object):
    def __init__(self):
        self.rdfClass="owl:Thing"

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
    def __init__(self):
        self.rdfClass="bprofile:Credential"

    def new(self):
        pass

    def all(self, p=None, o=None):
        if not p:
            p = "bprofile:credentialFor"
        super(Credential, self).all(p,o)

    def find(self):
        if not p:
            p = "bprofile:credentialFor"
        super(Credential, self).find(p,o)

    def update(self):
        pass

    def save(self):
        pass

    def destroy(self):
        pass

    def create(self):
        pass