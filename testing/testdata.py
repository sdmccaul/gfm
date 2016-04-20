# http://stackoverflow.com/questions/5029934/python-defaultdict-of-defaultdict
from collections import defaultdict
import csv

from graphfunction import GraphData

init = set()
with open('all_triples.csv','r') as f:
  csv_r = csv.reader(f)
  for row in csv_r:
    init.add(GraphData(row[0],row[1],row[2]))