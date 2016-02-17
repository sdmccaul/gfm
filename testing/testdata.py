# http://stackoverflow.com/questions/5029934/python-defaultdict-of-defaultdict
from collections import defaultdict
import csv

from datasets import Datum, DataSet

init = set()
with open('all_triples.csv','r') as f:
  csv_r = csv.reader(f)
  for row in csv_r:
    s,p,o = map(clean_brackets,row)
    init.add(Datum(s,p,o))

tset=DataSet(init)