from datasets import Datum

def firstName(res=None, val=None):
	return Datum(res,'<http://xmlns.com/foaf/0.1/firstName>', val)

def lastName(res=None, val=None):
	return Datum(res,'<http://xmlns.com/foaf/0.1/lastName>', val)