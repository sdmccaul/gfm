from expression import Schema, Collection, Attribute
from samples import rdfsLabel, rdfType, preferredTitle, trainingAtOrganization, lastName


fisFacultySchema = Schema({
	'class'		: 	Attribute(rdfType, required=True,
						presets=[
						'http://vivoweb.org/ontology/core#FacultyMember',
						'http://vivo.brown.edu/ontology/vivo-brown/BrownThing'
						]),
	'fullName'	:	Attribute(rdfsLabel, required=True, unique=True),
	'last'		:	Attribute(lastName, required=True, unique=True),
	'title'		:	Attribute(preferredTitle, optional=True, unique=True),
	'training'	: 	Attribute(trainingAtOrganization, optional=True),
})

fisFaculty = Collection(
				name='fisFaculty',
				schema=fisFacultySchema,
				named_graph='http://vitro.mannlib.cornell.edu/default/vitro-kb-2',
				namespace='http://vivo.brown.edu/individual/',
				prefix='faculty')