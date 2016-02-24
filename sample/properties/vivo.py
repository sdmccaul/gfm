from datasets import Datum

def preferredTitle(res=None, val=None):
	return Datum(res,'<http://vivoweb.org/ontology/core#preferredTitle>', val)