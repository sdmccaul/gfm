from expression import Schema, Collection, Attribute
from samples import rdfsLabel, rdfType, preferredTitle, trainingAtOrganization, lastName

fisFacultySchema = Schema({
	'class': {	rdfType: ['required'],
				'presets': [
					'http://vivoweb.org/ontology/core#FacultyMember',
					'http://vivo.brown.edu/ontology/vivo-brown/BrownThing'
					]
				},
	'fullName': { rdfsLabel: ['required', 'unique'] },
	'last': { lastName: ['required', 'unique'] },
	'title': { preferredTitle: ['optional', 'unique'] },
	'training': { trainingAtOrganization: ['optional'] },
})

fisFaculty = Collection(
				name='fisFaculty',
				schema=fisFacultySchema,
				named_graph='http://vitro.mannlib.cornell.edu/default/vitro-kb-2',
				namespace='http://vivo.brown.edu/individual/',
				prefix='faculty')