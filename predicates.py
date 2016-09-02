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

def _XSD_encode_uri(value):
	try:
		return "<"+ value +">"
	except:
		raise ValueError("XSD encoding of URI failed")

def _XSD_encode_string(value):
	try:
		# escaped_quotes = value.replace('"', '\"')
		return '"'+ value +'"'
	except:
		raise ValueError("XSD encoding of string failed")

def _XSD_encode_dateTime(value):
	try:
		return '"'+ value +'"^^<http://www.w3.org/2001/XMLSchema#dateTime>'
	except:
		raise ValueError("XSD encoding of dateTime failed")

class Predicate(object):

	def __init__(self, uri, datatype):
		self.uri = uri
		self.datatype = datatype
		if datatype == 'uri':
			self.validator = _validate_uri
			self.XSD_encoding = _XSD_encode_uri
		elif datatype == 'dateTime' or datatype == 'datetime':
			self.validator = _validate_datetime
			self.XSD_encoding = _XSD_encode_dateTime
		elif datatype == 'string':
			self.validator = _validate_string
			self.XSD_encoding = _XSD_encode_string

	def validate(self, value):
		return self.validator(value)