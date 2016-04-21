from graphstatements import Required, Optional, Linked
from graphset import GraphSet

def variableGenerator(r):
	vals = range(r)
	for v in vals:
		yield "?"+str(v)

def make_subject_variable(q,var):
	if q.res is None:
		return q._replace(res=var)
	else:
		return q

def make_object_variable(q,var):
	if q.val is None:
		return q._replace(val=var)
	else:
		return q

def variablize_values(qset):
	out = GraphSet()
	varJar = variableGenerator(100)
	for q in qset:
		var  = varJar.next()
		if (isinstance(q,Required) or isinstance(q,Optional)):
			out.add(make_object_variable(q, var))
		elif isinstance(q,Linked):
			out.add(make_subject_variable(q, var))
		else:
			continue
	return out

def variablize_resource(qset):
	out = GraphSet()
	for q in qset:
		var  = "?sbj"
		if (isinstance(q,Required) or isinstance(q,Optional)):
			out.add(make_subject_variable(q, var))
		elif isinstance(q,Linked):
			out.add(make_object_variable(q, var))
		else:
			continue
	return out

class QueryGraph(GraphSet):
	def __init__(self):
		self.resource = None
		self.filters = {}
		super(QueryGraph, self).__init__()

	def transform(self, other):
		out = GraphSet()
		for q in self:
			resp = other.query(**q._asdict())
			if resp:
				for r in resp:
					mapped = self.filters[q](r.res, r.val)
					out.add(mapped)
		return out

	def querySet(self):
		if self.resource:
			return variablize_values(self)
		else:
			return variablize_resource(variablize_values(self))