############################################
### BEGIN XSD Primitive datatypes ##########
### https://www.w3.org/TR/xmlschema11-2/ ###
############################################

xsdNsTemplate = "\"{literal}\"^^<http://www.w3.org/2001/XMLSchema#{dtype}>"

class XSDData(str):
	def __new__(cls, value):
		obj = str.__new__(cls, value)
		obj.rdf = cls.transform(value)
		return obj

class XSDBoolean(XSDData):
	@classmethod
	def transform(cls, value):
		return xsdNsTemplate.format(
			literal=value,dtype="boolean")

# class XSDDecimal(XSDData):

# class XSDFloat(XSDData):

# class XSDDouble(XSDData):

# class XSDDuration(XSDData):

# class XSDDateTime(XSDData):

# class XSDTime(XSDData):

# class XSDDate(XSDData):

# class XSDYearMonth(XSDData):

# class XSDYear(XSDData):

# class XSDMonthDay(XSDData):

# class XSDDay(XSDData):

# class XSDMonth(XSDData):

# class XSDHexBinary(XSDData):

# class XSDBase64Binary(XSDData):

# class XSDAnyURI(XSDData):

# class XSDQName(XSDData):

# class XSDNOTATION(XSDData):
