from expression import Schema, Collection, Attribute
from samples import rdfsLabel, rdfType, preferredTitle

fullName = Attribute(predicate=rdfsLabel, alias='fullName',
						required=True, unique=True)
rdfClass = Attribute(predicate=rdfType, alias='class',
						required=True,
						presets=[
							'http://vivoweb.org/ontology/core#FacultyMember',
							'http://vivo.brown.edu/ontology/vivo-brown/BrownThing'
							]
						)
title = Attribute(predicate=preferredTitle, alias='title',
					required=False, unique=True)
fisFacultySchema = Schema([fullName,rdfClass,title])
fisFaculty = Collection(
				name='fisFaculty',
				schema=fisFacultySchema,
				named_graph='http://fakenamedgraph',
				namespace='http://vivo.brown.edu/individual/',
				prefix='faculty')