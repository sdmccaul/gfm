from expression import Schema, Collection, Attribute
from samples import rdfsLabel, rdfType

fullName = Attribute(predicate=rdfsLabel, alias='fullName',
						required=True, unique=True)
rdfClass = Attribute(predicate=rdfType, alias='class',
						required=True,
						values=[
							'http://vivoweb.org/ontology/core#FacultyMember',
							'http://vivo.brown.edu/ontology/vivo-brown/BrownThing'
							])
fisFacultySchema = Schema([fullName,rdfClass])
fisFaculty = Collection(
				name='fisFaculty',
				schema=fisFacultySchema,
				named_graph='http://fakenamedgraph',
				namespace='http://vivo.brown.edu/individual/',
				prefix='faculty')