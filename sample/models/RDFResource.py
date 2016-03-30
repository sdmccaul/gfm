from graphview import ResourceView
from graphattributes import Edge, Required
from properties import rdfs, rdf

class RDFResource(ResourceView):
    rdfType = Edge(rdf.rdfType, Required)
    label = Edge(rdfs.label, Required)