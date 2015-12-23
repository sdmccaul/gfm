from rdflib import Graph
import rdflib

from vdm.namespaces import VIVO, TMP, BLOCAL
from vdm.models import BaseResource, VResource, FacultyMember

from sparqldb import SparqlInterface
from triplemanager import Paragraph, unique

import edges

import logging

sparql = SparqlInterface()

mgmt = Paragraph()

# def get_property_object(triples):
#     for stmt in triples:
#         yield stmt[2]

# def match_property(triples, ppty):
#     for stmt in triples:
#         if stmt[1] == ppty:
#             yield stmt

# def property_lookup(triples, ppty):
#     out = [ obj for obj in get_property_object(
#                 match_property(triples, ppty)) ]
#     if len(out) == 1:
#         return out[0]
#     else:
#         return out

# class Thing(object):
#     def __init__(self):
#         self.rdfClass="owl:Thing"
#         self.uri = None

#     def set_uri(rabid=None,prefix="http://vivo.brown.individual/"):
#         if rabid is None:
#             raise Exception("rabid need for uri creation")
#         self.uri = prefix + rabid

#     def new(self, prefix=None):
#         generate_uri(self, prefix)

#     def all(self, filters=None):
#         construct = [
#             (None, 'rdf:type', self.rdfClass),
#             (None, 'rdfs:label', None)
#             ]
#         where =     [
#             (None, 'rdf:type', self.rdfClass),
#             (None, 'rdfs:label', None)
#             ]
#         if filters:
#             for p,o in filters.items():
#                 where.append((None,p,o))
#         results = sparql.construct(construct,where)
#         for s,p,o in results.graph.triples( (None, None, None)):
#             print s,p,o

#     def find(self, uri=None):
#         q = u"""
#         CONSTRUCT {{
#             <{uri}> ?p ?o .
#             ?o rdfs:label ?label .
#         }}
#         WHERE {{
#             <uri> rdf:type {rdfClass} .
#             <{uri}> ?p ?o .
#             OPTIONAL {{ ?o rdfs:label ?label . }}
#         }}
#         """.format(uri=uri)
#         results = sparql.query(q).graph
#         for s,p,o in results.triples( (None, None, None)):
#             print s,p,o

class Credential(object):
    def __init__(self, statements, uri=None):
        self.ref = uri
        self.statements = statements
        self.statements.attach(self)

    def _notify(self):
        print self.ref
        for s in self.statements.keep:
            if s[0] == self.ref:
                print "\t",s

    def credentialFor(self, obj):
        verb = edges.bprofile_credentialFor
        sbj = self.ref
        self.statements.add(verb(sbj, obj))

    def credentialGrantedBy(self, obj):
        verb = edges.bprofile_credentialGrantedBy
        sbj = self.ref
        self.statements.add(verb(sbj, obj))
    # def new(cls):
    #     pass

    # def create(self, label):
    #     print 'create {0}!'.format(label)

    # @classmethod
    # def find(cls, rabid=None):
    #     if rabid is None:
    #         raise Exception("No rabid provided")
    #     uri = "http://vivo.brown.edu/individual/" + rabid
    #     stmts = sparql.describe(uri)
    #     if stmts:
    #         return Credential(uri=uri,stmts=stmts)

    # def update_attr(self, params):
    #     if not isinstance(params, dict):
    #         raise("Malformed params!")
    #     for k, v in params.items():
    #         if k in property_list:
    #             getattr(self, k)(v)
    #         else:
    #             pass

    # def save(self):
    #     pass

    # def destroy(self):
    #     pass