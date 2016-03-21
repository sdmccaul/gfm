############################################
### BEGIN classed datatypes ################
### Add behavior for printing to rdf #######
############################################

class DataType(str):
	def __new__(cls, value):
		## add "validate" function, particular to class
		## call on each value prior to __new__
		valid = cls.validate(value)
		if valid is False:
			raise ValueError(("{0} is not valid {1}").format(value, cls))
		obj = str.__new__(cls, valid)
		obj.rdf = cls.transform(valid)
		return obj

	@classmethod
	def transform(cls, value):
		return cls.rdfTemplate.format(literal=value)


############################################
### Generic URI datatype ###################
############################################

class URI(DataType):
	rdfTemplate = "<{literal}>"

	@classmethod
	def validate(cls, value):
		if value.startswith(("<http://","<https://")) and value.endswith(">"):
			return value[1:-1]
		elif value.startswith(("http://","https://")):
			return value
		else:
			return False

############################################
### BEGIN XSD Primitive datatypes ##########
### https://www.w3.org/TR/xmlschema11-2/ ###
############################################

def xsdDataTemplate(dtype):
	xsdNs = "<http://www.w3.org/2001/XMLSchema#{0}>".format(dtype)
	return "\"{literal}\"^^" + xsdNs

class XSDString(DataType):
	xsdType = "string"
	rdfTemplate = xsdDataTemplate(xsdType)

	@classmethod
	def validate(cls,value):
		try:
			return value.decode('utf-8')
		except:
			return False

class XSDBoolean(DataType):
	xsdType = "boolean"
	rdfTemplate = xsdDataTemplate(xsdType)

class XSDDecimal(DataType):
	xsdType = "decimal"
	rdfTemplate = xsdDataTemplate(xsdType)

class XSDFloat(DataType):
	xsdType = "float"
	rdfTemplate = xsdDataTemplate(xsdType)
	
class XSDDouble(DataType):
	xsdType = "double"
	rdfTemplate = xsdDataTemplate(xsdType)
	
class XSDDuration(DataType):
	xsdType = "duration"
	rdfTemplate = xsdDataTemplate(xsdType)
	
class XSDDateTime(DataType):
	xsdType = "dateTime"
	rdfTemplate = xsdDataTemplate(xsdType)
	
class XSDTime(DataType):
	xsdType = "time"
	rdfTemplate = xsdDataTemplate(xsdType)
	
class XSDDate(DataType):
	xsdType = "date"
	rdfTemplate = xsdDataTemplate(xsdType)
	
class XSDYearMonth(DataType):
	xsdType = "gYearMonth"
	rdfTemplate = xsdDataTemplate(xsdType)
	
class XSDYear(DataType):
	xsdType = "gYear"
	rdfTemplate = xsdDataTemplate(xsdType)
	
class XSDMonthDay(DataType):
	xsdType = "gMonthDay"
	rdfTemplate = xsdDataTemplate(xsdType)
	
class XSDDay(DataType):
	xsdType = "gDay"
	rdfTemplate = xsdDataTemplate(xsdType)
	
class XSDMonth(DataType):
	xsdType = "gMonth"
	rdfTemplate = xsdDataTemplate(xsdType)
	
class XSDHexBinary(DataType):
	xsdType = "hexBinary"
	rdfTemplate = xsdDataTemplate(xsdType)
	
class XSDBase64Binary(DataType):
	xsdType = "base64Binary"
	rdfTemplate = xsdDataTemplate(xsdType)
	
class XSDAnyURI(DataType):
	xsdType = "anyURI"
	rdfTemplate = xsdDataTemplate(xsdType)
	
class XSDQName(DataType):
	xsdType = "QName"
	rdfTemplate = xsdDataTemplate(xsdType)
	
class XSDNOTATION(DataType):
	xsdType = "NOTATION"
	rdfTemplate = xsdDataTemplate(xsdType)

############################################
### BEGIN datatype decorators ##############
### for enforcing data validation ##########
### via property functions #################
############################################

def resourceProperty(func):
	def restriction(res=None, val=None):
		if res:
			res = URI(res)
		return func(res, val)
	return restriction

def dataProperty(func):
	@resourceProperty
	def restriction(res=None, val=None):
		if val:
			val = XSDString(val)
		return func(res, val)
	return restriction

def objectProperty(func):
	@resourceProperty
	def restriction(res=None, val=None):
		if val:
			val = URI(validate_uri_string(val))
		return func(res, val)
	return restriction