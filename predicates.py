import datetime
import urlparse

def _validate_uri(value):
	try:
		urlparse.urlparse(value)
	except:
		raise ValueError("Bad URI: ", value)
	return value

def _validate_datetime(value):
	try:
		datetime.datetime.strptime(value, '%Y-%m-%dT%H:%M:%S.%fZ')
	except:	
		raise ValueError("Bad date: ", value)
	return value

def _validate_string(value):
	try:
		value.decode('UTF-8')
	except:
		raise UnicodeError("Bad unicode: ", value)
	return value

class Predicate(object):

	def __init__(self, uri, datatype):
		self.uri = uri
		self.datatype = datatype
		if datatype == 'anyURI' or datatype == 'uri':
			self.validator = _validate_uri
		elif datatype == 'dateTime' or datatype == 'datetime':
			self.validator = _validate_datetime
		elif datatype == 'string':
			self.validator = _validate_string

	def validate(self, value):
		return self.validator(value)