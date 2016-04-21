# http://stackoverflow.com/questions/5029934/python-defaultdict-of-defaultdict
from collections import defaultdict
import csv

from graphstatements import Statement
from graphset import GraphSet

init = GraphSet()
with open('all_triples.csv','r') as f:
  csv_r = csv.reader(f)
  for row in csv_r:
    init.add(Statement(row[0],row[1],row[2]))