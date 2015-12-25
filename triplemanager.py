import sparqldb

import rdflib

def pythonize(s,p,o):
  return (s.toPython(),p.toPython(),o.toPython())

def store_query_results(rdflib_results, local_set):
  for s,p,o in rdflib_results:
    local_set.add(pythonize(s,p,o))

class SessionGraph(object):
    def __init__(self, graphstore):
      self.gs = graphstore
      self.current = set()
      self.pending_adds = set()
      self.pending_removes = set()

    def attach(self, resource):
      self.resources.append(resource)

    def add(self, sentence):
      self.keep.add(sentence)
      self._update_resources()

    def remove(self, sentence):
      self.strike.add(sentence)

    def search(self, sentence=None):
      pass

    def commit(self):
      pass

    def select(self):
      pass

    def construct(self):
      pass

    def delete(self):
      pass

    def insert(self):
      pass

    def describe(self):
      pass

    # needs to initizlize individual objects
    def all(self, model, required=None, optional=None):
      pattern = [
            (None,
            'http://www.w3.org/1999/02/22-rdf-syntax-ns#type',
            model.rdfClass)
            ]
      if required:
        for r in required:
          pattern.append((None, r, None))
      results = self.gs.construct(pattern,pattern)
      for r in results:
        self.current.add(r)
      return [ model(r[0]) for r in results
                if r[1] == pattern[1] and r[2] == pattern[2]]

    def _update_resources(self):
      for r in self.resources:
        r._notify()

def flatten(subj, stmts, result=None):
    if result is None:
        result = list()
    for pred, obj in stmts.items():
        if isinstance(obj, dict):
            flatten(subj, obj, result)
        elif isinstance(obj,list):
            for o in obj:
                flatten(subj, o, result)
        else:
            result.append((subj, pred, obj))
    return result

def nest(stmts):
    result = dict()
    for s in stmts:
        if s[1] in result:
            if isinstance(result[s[1]], list):
                result[s[1]].append(s[2])
            else:
                old = result[s[1]]
                new = s[2]
                result[s[1]] = list()
                result[s[1]].append(old)
                result[s[1]].append(new)
        else:
            result[s[1]] = s[2]
    return result

def unique(object):
  def __init__(self, statements):
    self._stmts = statements

  def unique_statement(*args):
    stmt = statement(*args)
    return stmt
  return unique_statement
