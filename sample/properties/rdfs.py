from datasets import Datum

def label(res=None, val=None):
	return Datum(res,'<http://www.w3.org/2000/01/rdf-schema#label>', val)