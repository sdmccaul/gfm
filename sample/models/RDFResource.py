from graphview import ResourceView
from graphedges import Edge
from graphstatements import Required
from properties import rdfs, rdf

class RDFResource(ResourceView):
    rdfType = Edge(rdf.rdfType, Required)
    label = Edge(rdfs.label, Required)