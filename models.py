from rdflib import Graph
import rdflib

from vdm.namespaces import VIVO, TMP, BLOCAL
from vdm.models import BaseResource, VResource, FacultyMember

import logging

class Faculty(FacultyMember):
    """
    For faculty in dataservice.
    """

    def init_query(self):
        """
        A SPARQL construct query to pull out the data fo
        """
        rq = """
        CONSTRUCT {
            ?subject a vivo:FacultyMember ;
                #label, first, last, email required
                rdfs:label ?name ;
                foaf:firstName ?first ;
                foaf:lastName ?last ;
                vivo:middleName ?middle ;
                vivo:preferredTitle ?title ;
                tmp:email ?email ;
                vivo:overview ?overview ;
                blocal:hasAffiliation ?org ;
                vivo:hasResearchArea ?ra ;
                tmp:image ?photo ;
                tmp:fullImage ?miURL ;
                blocal:hasGeographicResearchArea ?country .
            #affils
            ?org rdfs:label ?orgName .
            #research areas
            ?ra rdfs:label ?raName .
            #country research areas
            ?country rdfs:label ?countryName .
        }
        WHERE {
            #required - label, first, last
            {
            ?subject a vivo:FacultyMember ;
                rdfs:label ?name ;
                foaf:firstName ?first ;
                foaf:lastName ?last .
            }
            #optional - middle name
            UNION {
                ?subject vivo:middleName ?middle .
            }
            #optional - title
            UNION {
                ?subject vivo:preferredTitle ?title .
            }
            #optional - email
            UNION {
                ?subject vivo:primaryEmail ?email .
            }
            #optional - overview
            UNION {
                ?subject vivo:overview ?overview .
            }
            #optional - affiliations
            UNION {
                ?subject blocal:hasAffiliation ?org .
                ?org rdfs:label ?orgName .
            }
            #optional - research areas
            UNION {
                ?subject vivo:hasResearchArea ?ra .
                ?ra a blocal:ResearchArea ;
                    rdfs:label ?raName .
            }
            #optional - research country
            UNION {
                ?subject blocal:hasGeographicResearchArea ?country .
                ?country a blocal:Country ;
                    rdfs:label ?countryName .
            }
            #optional - photos
            UNION {
                ?subject vitropublic:mainImage ?mi .
                #main image
                ?mi vitropublic:downloadLocation ?miDl .
                ?miDl vitropublic:directDownloadUrl ?miURL .
                #thumbnail
                ?mi vitropublic:thumbnailImage ?ti .
                ?ti vitropublic:downloadLocation ?dl .
                ?dl vitropublic:directDownloadUrl ?photo .
            }
        }
        """
        return rq

    def countries(self):
        return self.get_related(BLOCAL.hasGeographicResearchArea)


class Topic(VResource):
    """
    Research areas.
    """
    def init_query(self):
        return """
        CONSTRUCT {
            ?subject a blocal:ResearchArea ;
                rdfs:label ?label ;
                vivo:researchAreaOf ?fac .
            ?fac rdfs:label ?facName .
        }
        WHERE {
            {
              ?subject a blocal:ResearchArea ;
                rdfs:label ?label .
            }
            UNION {
                ?subject vivo:researchAreaOf ?fac .
                ?fac rdfs:label ?facName .
            }
        }
        """

    def researchers(self):
        return self.get_related(VIVO.researchAreaOf)


class Country(VResource):
    """
    Countries.
    """
    def init_query(self):
        return """
        CONSTRUCT {
            ?subject a blocal:Country ;
                rdfs:label ?label ;
                blocal:countryCode ?code ;
                blocal:geographicResearchAreaOf ?fac .
            ?fac rdfs:label ?facName .
        }
        WHERE {
            {
              ?subject a blocal:Country ;
                rdfs:label ?label ;
                blocal:countryCode ?code .
            }
            UNION {
                ?subject blocal:geographicResearchAreaOf ?fac .
                ?fac rdfs:label ?facName .
            }
        }
        """

    def researchers(self):
        return self.get_related(BLOCAL.geographicResearchAreaOf)

    def get_code(self):
        return self.get_first_literal(BLOCAL.countryCode)

class Organization(BaseResource):
    """
    We are overriding the default query setup here.
    Fuseki and RDFLib aren't performing well with
    departments with large membership. To get
    affiliates we will execute multiple smaller construct
    queries.  For the largest department - ~600 - this
    takes about 1 to 2 seconds.  If run without limits and
    offsets the queries can take about two minutes or fail
    completely.

    v2 can support pagination.

    """

    def __init__(self, uri=None, store=None):
        if store is None:
            raise Exception("store must be an RDFLib Graph")
        self.uri = uri
        self.store = store
        graph = self.assemble_graph()
        super(Organization, self).__init__(uri=uri, graph=graph)

    def assemble_graph(self):
        g = self.get_dept_graph()
        g += self.get_affil_graph()
        return g

    def get_dept_graph(self, photos=True):
        rq = """
        CONSTRUCT {
            ?subject a foaf:Organization ;
                rdfs:label ?label ;
                tmp:image ?photo ;
                tmp:fullImage ?miURL .
        }
        WHERE {
            {
              ?subject a foaf:Organization ;
                rdfs:label ?label .
            }
            #optional - orgs have photos too
            UNION {
                ?subject vitropublic:mainImage ?mi .
                #main image
                ?mi vitropublic:downloadLocation ?miDl .
                ?miDl vitropublic:directDownloadUrl ?miURL .
                #thumbnail
                ?mi vitropublic:thumbnailImage ?ti .
                ?ti vitropublic:downloadLocation ?dl .
                ?dl vitropublic:directDownloadUrl ?photo .
            }
        }
        """.replace("?subject", self.uri.n3())
        logging.debug("Org query: {}".format(rq))
        try:
            rsp = self.store.query(rq)
            return rsp.graph
        except rdflib.query.ResultException:
            return Graph()

    def get_affil_graph(self):
        limit = 75
        offset = 0
        queries = 1
        outg = Graph()
        while True:
            if queries == 1:
                offset = 0
            rq = """
            CONSTRUCT {
                ?subject tmp:member ?fac .
                ?fac tmp:memberOf ?subject ;
                     rdfs:label ?facName .
            }
            WHERE {
               ?subject a foaf:Organization .
               ?fac blocal:hasAffiliation ?subject ;
                    rdfs:label ?facName .
            }
            ORDER BY ?fac
            LIMIT ?limit
            OFFSET ?offset
            """.replace("?subject", self.uri.n3())\
                .replace("?limit", str(limit))\
                .replace("?offset", str(offset))
            logging.debug("Org query: {}".format(rq))
            try:
                rsp = self.store.query(rq)
                outg += rsp.graph
            except rdflib.query.ResultException:
                break
            queries += 1
            offset = queries * limit
        return outg


    def affiliates(self):
        return self.get_related(TMP.member)

    def overview(self):
        return self.get_first_literal(VIVO.overview)

    def thumbnail(self):
        return self.get_first_literal(TMP.image)

    def full_image(self):
        return self.get_first_literal(TMP.fullImage)


class Resource(object):
    def __init__(self):
        pass

    def new(self):
        generate_uri(self, prefix)

    def all(self):
        retrieve_all(resource_class)

class Credential(object):
    def __init__(self):
        pass

    def new(self):
        pass

    def all(self):
        pass

    def find(self):
        pass

    def update(self):
        pass

    def save(self):
        pass

    def destroy(self):
        pass


if __name__ == '__main__':
    import os
    from vdm.namespaces import D
    from vdm.backend import FusekiGraph
    vstore = FusekiGraph(os.environ['VIVO_ENDPOINT'])
    uri = D['org-brown-univ-dept84']
    print uri
    org = Organization(uri=uri, store=vstore)
    print org.affiliates()
    print len(org.affiliates())