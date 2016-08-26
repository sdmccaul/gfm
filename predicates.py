import datetime
import urlparse

class Predicate(object):

	def __init__(self, uri, datatype):
		self.uri = uri
		self.datatype = datatype
		if datatype == 'anyURI' or datatype == 'uri':
			self.validator = self._validate_uri
		elif datatype == 'dateTime' or datatype == 'datetime':
			self.validator = self._validate_datetime
		elif datatype == 'string':
			self.validator = self._validate_string

	def _validate_uri(self, value):
		try:
			urlparse.urlparse(value)
		except:
			raise ValueError("Bad URI: ", value)
		return value

	def _validate_datetime(self, value):
		try:
			datetime.datetime.strptime(value, '%Y-%m-%dT%H:%M:%S.%fZ')
		except:	
			raise ValueError("Bad date: ", value)
		return value

	def _validate_string(self, value):
		try:
			value.decode('UTF-8')
		except:
			raise UnicodeError("Bad unicode: ", value)
		return value

	def validate(self, value):
		return self.validator(value)