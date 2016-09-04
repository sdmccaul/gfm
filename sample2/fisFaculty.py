from expression import Schema, Collection, Attribute
from samples import rdfsLabel, rdfType, preferredTitle, trainingAtOrganization, lastName

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
training = Attribute(predicate=trainingAtOrganization, alias='training',
					required=False)
last = Attribute(predicate=lastName, required=True, alias='last')
fisFacultySchema = Schema([fullName,rdfClass,title,training,last])
fisFaculty = Collection(
				name='fisFaculty',
				schema=fisFacultySchema,
				named_graph='http://fakenamedgraph',
				namespace='http://vivo.brown.edu/individual/',
				prefix='faculty')