import datetime
import urlparse

class Predicate(object):	

	def __init__(self, uri):
		self.uri = urlparse.urlparse(uri)

	def __get__(self, instance, cls):
		

class ObjectProperty(Predicate):

	def __init__(self, uri):
		self.uri = urlparse.urlparse(uri)
		self.domain = 'anyURI'

	def __call__(self, value, xsd=True, builtin=False):
		xsd = not builtin
		if xsd:
			if isinstance(value, urlparse.ParseResult):
				return value
			else:
				try:
					return urlparse.urlparse(value)
				except:
					raise ValueError("Bad URI: ", value)
		if builtin:
			try:
				return value.geturl()
			except AttributeError:
				return value.decode("UTF-8")
			except:
				raise ValueError("Bad URI: ", value)

class DateProperty(Predicate):
	def __init__(self, uri):
		self.uri = urlparse.urlparse(uri)
		self.domain = 'date'

	def __call__(self, value, xsd=True, builtin=False):
		xsd = not builtin
		if xsd:
			
		if builtin:


class DateTimeProperty(Predicate):
	def __init__(self, uri):
		self.uri = urlparse.urlparse(uri)
		self.domain = 'dateTime'

	def __call__(self, value, xsd=True, builtin=False):
		xsd = not builtin
		if xsd:
			if isinstance(value, datetime.datetime):
				return value
			else:
				try:
					return datetime.datetime.strptime(value, '%Y-%m-%dT%H:%M:%S.%fZ')
				except:	
					raise ValueError("Bad date: ", value)
		if builtin:
			try:
				return value.isoformat()
			except AttributeError:
				return value.decode("UTF-8")
			except:
				raise ValueError

class StringProperty(Predicate):
	def __init__(self, uri):
		self.uri = urlparse.urlparse(uri)
		self.domain = 'string'

	def __call__(self, value, xsd=True, builtin=False):
		xsd = not builtin
		if xsd:
			try:
				return value.decode('UTF-8')
			except:
				raise UnicodeError("Bad unicode: ", value)
		if builtin:
			try:
				return value.decode('UTF-8')
			except:
				raise UnicodeError("Bad unicode: ", value)