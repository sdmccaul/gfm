from rdflib import Graph
import rdflib

from vdm.namespaces import VIVO, TMP, BLOCAL
from vdm.models import BaseResource, VResource, FacultyMember

from sparqldb import sparql

import logging


class Thing(object):
    def __init__(self):
        self.rdfClass="owl:Thing"

    def new(self, prefix=None):
        generate_uri(self, prefix)

    def all(self,p=None,o=None):
        format_params = dict(rdfClass=self.rdfClass,rdfFilter='')
        if (p and o):
            format_params['rdfFilter'] = "?thing {0} {1} .".format(p,o)            
        q = u"""
        CONSTRUCT {{
            ?thing rdf:type {rdfClass} ;
                rdfs:label ?label .
        }}
        WHERE {{
            ?thing rdf:type {rdfClass} ;
                rdfs:label ?label .
            {rdfFilter}
        }}
        LIMIT 20
        """.format(**format_params)
        results = sparql.query(q).graph
        for s,p,o in results.triples( (None, None, None)):
            print s,p,o

    def find(self, uri=None):
        q = u"""
        CONSTRUCT {{
            <{uri}> ?p ?o .
            ?o rdfs:label ?label .
        }}
        WHERE {{ 
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
        pass

    def update(self):
        pass

    def save(self):
        pass

    def destroy(self):
        pass

    def create(self):
        pass