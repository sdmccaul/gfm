# http://stackoverflow.com/questions/5029934/python-defaultdict-of-defaultdict
from collections import defaultdict
import csv

from datasets import Datum, DataSet
  
class SetManager(object):
    def __init__(self, initial_set):
      self.current = initial_set
      self.pending = initial_set.copy()
      self.sbj_index = defaultdict(set)
      self.prd_index = defaultdict(set)
      self.sbj_prd_index = defaultdict(set)
      self.prd_obj_index = defaultdict(set)
      self._update_indices()

    def _update_indices(self):
      self._index_subjects()
      self._index_predicates()
      self._index_subject_predicates()
      self._index_predicate_objects()

    def _index_subjects(self):
      for s in self.pending:
        self.sbj_index[(s[0],None,None)].add(s)

    def _index_predicates(self):
      for s in self.pending:
        self.prd_index[(None,s[1],None)].add(s)

    def _index_subject_predicates(self):
      for s in self.pending:
        self.sbj_prd_index[(s[0],s[1],None)].add(s)

    def _index_predicate_objects(self):
      for s in self.pending:
        self.prd_obj_index[(None,s[1],s[2])].add(s)

    def attach(self, resource):
      pass

    def add(self, sentence):
      pass

    def remove(self, sentence):
      pass

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


def clean_brackets(d):
  if d.startswith('<http'):
    return d[1:-1]

init = set()
with open('all_triples.csv','r') as f:
  csv_r = csv.reader(f)
  for row in csv_r:
    s,p,o = map(clean_brackets,row)
    init.add(Datum(s,p,o))

mgmt=DataSet(init)