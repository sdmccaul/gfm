from graphview import ResourceView
from graphstatements import Required, Optional, Linked
from graphedges import Edge
from properties import blocal, rdfs, rdf, foaf, vivo

class FisFaculty(ResourceView):
    rdfType = Edge(rdf.rdfType, Required,
        values=[
            'http://vivoweb.org/ontology/core#FacultyMember',
            'http://vivo.brown.edu/ontology/vivo-brown/BrownThing'
            ])
    shortId = Edge(blocal.shortId, Required) 
    label = Edge(rdfs.label, Required)
    first = Edge(foaf.firstName, Optional)
    last = Edge(foaf.lastName, Optional)
    title = Edge(vivo.preferredTitle, Optional)
