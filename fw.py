import sys
import time
from fuzzywuzzy import process



f = open(sys.argv[1])
limit = int(sys.argv[2])
query = sys.argv[3]

choices = set(x.split('\t')[1].strip() for x in f)
start = time.time()

for item in process.extract(query, choices, limit=limit):
    print(item)

delta = time.time() - start
print(delta)
