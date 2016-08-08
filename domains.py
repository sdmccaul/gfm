import datetime

def xsdString(value):
	try:
		return value.decode('UTF-8')
	except:
		raise UnicodeError("Bad unicode: ", value)

def xsdDateTime(value):
	if isinstance(datetime.datetime, value):
		return value
	else:
		try:
			return datetime.datetime.strptime(value, '%Y-%m-%dT%H:%M:%S.%fZ')
		except:	
			raise ValueError("Bad datetime: ", value)

def xsdDate(value):
	if isinstance(datetime.date, value):
		return value
	else:
		try:
			return datetime.datetime.strptime(value, '%Y-%m-%dT%H:%M:%S.%fZ').date()
		except:
			raise ValueError("Bad datetime: ", value)

def uriObject(value):
	if isinstance(urlparse.ParseResult, value):
		return value
	else:
		try:
			return urlparse(value)
		except:
			raise ValueError("Bad URI: ", value)