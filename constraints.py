import json

class multivalued(object):
	def __init__(self, prop):
		self._property = prop
		self._objects = set()

	def __repr__(self):
		return json.dumps(list(self._objects))

	def add(self, val):
		s, p, o = self._property(obj=val)
		self._objects.add(o)

	def remove(self, val):
		self._objects.discard(val)

	def clear(self):
		self._objects.clear()

class unique(object):
	def __init__(self, statements):
		self._stmts = statements

	def __call__(self, f):
		self._sntc = f

	def add(self, val):
		s, p, o = self._property(obj=val)
		self._objects = o

	def remove(self, val):
		self._objects = None

	def clear(self):
		self._objects = None