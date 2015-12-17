from utils import get_triple_objects, search

def rdf_type(sbj=None, obj=None):
	return (sbj, 'rdf:type', obj)

def rdfs_label(sbj=None, obj=None):
	return (sbj, 'rdfs:label', obj)

def bprofile_credentialFor(sbj=None, obj=None):
	pred = 'http://vivo.brown.edu/ontology/profile#credentialFor'
	return (sbj, pred, obj)

def bprofile_credentialGrantedBy(sbj=None, obj=None):
	pred = 'http://vivo.brown.edu/ontology/profile#credentialGrantedBy'
	return (sbj, pred, obj)

def bprofile_startDate(sbj=None, obj=None):
	return (sbj, 'bprofile:startDate', obj)

def bprofile_endDate(sbj=None, obj=None):
	return (sbj, 'bprofile:endDate', obj)

def fake_intValid(sbj=None, obj=None):
	if isinstance(obj, int):
		return (sbj, 'fake:intValid', obj)
	else:
		raise Exception("invalid input!")