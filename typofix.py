import sys

from time import time
from collections import Counter

from rapidfuzz import fuzz
from fuzz import bbkh
from lsm import LSM
from lsm import SEEK_LE, SEEK_GE
from tuple import pack, unpack, strinc


f = open(sys.argv[1])

db = LSM('fuzzbuzz.ldb')

for index, line in enumerate(f):
    print(index)
    line = line.lower()
    wrong, goods = line.split('->')
    goods = [x.strip() for x in goods.split(',')]

    begin = time()
    limit = 100
    query = wrong.lower()

    key = bbkh(query)

    distances = Counter()
    start = pack((key,))

    with db.cursor() as cursor:
        try:
            cursor.seek(start, SEEK_LE)
        except KeyError:
            continue
        nearest = cursor.key()

        # Look every keys that are above the neareest match
        for _ in range(limit * 10):
            packed = cursor.key()
            key, label = unpack(packed)
            d = fuzz.ratio(label, query, score_cutoff=70)
            if d:
                distances[label] = d
            try:
                cursor.previous()
            except StopIteration:
                break

        cursor.seek(nearest, SEEK_GE)

        for _ in range(limit * 10):
            packed = cursor.key()
            key, label = unpack(packed)
            d = fuzz.ratio(label, query, score_cutoff=70)
            if d:
                distances[label] = d
            try:
                cursor.next()
            except StopIteration:
                break
        print('* most similar according to bbkh for: {}'.format(query))
        for key, d in distances.most_common(limit):
            print('**', key, "\t", d)

        candidates = [x[0] for x in distances.most_common(limit)]
        if any(good in candidates for good in goods):
            print(True)
        else:
            print(False, goods)

        delta = time() - begin
        print(delta)

# at last!
db.close()
