from graphview import Resource
from graphattributes import Edge, Required, Optional, Linked
from properties import blocal, rdfs, rdf, foaf, vivo

class FisDegrees(Resource):
    rdfType = Edge(rdf.rdfType, Required,
        values=[
            'http://vivoweb.org/ontology/core#EducationalTraining'
            ])
    label = Edge(rdfs.label, Required)
    faculty = Edge(vivo.educationalTrainingOf, Required)
    org = Edge(vivo.trainingAtOrganization, Optional)
    date = Edge(blocal.degreeDate, Optional)