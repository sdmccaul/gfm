from datasets import Datum

def rdfType(res=None, val=None):
	return Datum(res,'http://www.w3.org/1999/02/22-rdf-syntax-ns#type', val)