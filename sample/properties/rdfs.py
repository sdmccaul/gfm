from datasets import Datum
from graphdatatypes import URI, objectProperty, dataProperty

@dataProperty
def label(res=None, val=None):
	return Datum(res,URI('http://www.w3.org/2000/01/rdf-schema#label'), val)