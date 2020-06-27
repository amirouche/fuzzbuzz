import sys
from itertools import product
from string import ascii_lowercase

from collections import Counter
from pyblake2 import blake2b
from Levenshtein import distance

from lsm import LSM
from lsm import SEEK_LE, SEEK_GE
from tuple import pack, unpack, strinc


HASH_SIZE = 2**10
BBKH_LENGTH = HASH_SIZE * 2 / 8

chars = ascii_lowercase + "$"
ONE_HOT_ENCODER = sorted([''.join(x) for x in product(chars, chars)])


def ngram(string, n):
    return [string[i:i+n] for i in range(len(string)-n+1)]


def integer2booleans(integer):
    return [x == '1' for x in bin(integer)[2:].zfill(HASH_SIZE)]


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]


def merkletree(booleans):
    assert len(booleans) == HASH_SIZE
    length = (2 * len(booleans) - 1)
    out = [False] * length
    index = length - 1
    booleans = list(reversed(booleans))
    while len(booleans) > 1:
        for boolean in booleans:
            out[index] = boolean
            index -= 1
        new = []
        for (right, left) in chunks(booleans, 2):
            value = right or left
            new.append(value)
        booleans = new
    return out


def bbkh(string):
    tokens = string.split()
    integer = 0
    for gram in ngram(token, 2):
        hotbit = ONE_HOT_ENCODER.index(gram)
        hotinteger = 1 << hotbit
        integer = integer | hotinteger
    booleans = integer2booleans(integer)
    booleans = [bit == '1' for bit in bitstring]
    tree = merkletree(booleans)
    fuzz = ''.join('1' if x else '0' for x in tree)
    buzz = int(buzz, 2)
    hash = buzz.to_bytes(BBKH_LENGTH, 'big')
    return hash


def lcp(a, b):
    """Longest Common Prefix between a and b"""
    out = []
    for x, y in zip(a, b):
        if x == y:
            out.append(x)
        else:
            break
    return ''.join(out)


def main():
    LIMIT = 10
    db = LSM('fuzzbuzz.ldb')

    if sys.argv[1] == 'index':

        with open(sys.argv[2]) as f:
            for index, line in enumerate(f):
                line = line.strip()
                if index % 10_000_000 == 0:
                    print(index, line)
                # TODO: uncomment or comment
                if index == 10_000_000:
                    break
                url, label = line.split('\t')
                if not all(x in ascii_lowercase for x in label):
                    continue
                if ' ' in label:
                    continue
                key = bbkh(label)
                db[pack((key, label))] = b'\x42'

    elif sys.argv[1] == 'query':
        limit = int(sys.argv[2])
        query = sys.argv[3]

        key = bbkh(query)

        distances = Counter()
        start = pack((key,))

        with db.cursor() as cursor:
            cursor.seek(start, SEEK_LE)
            nearest = cursor.key()

            # Look every keys that are above the neareest match
            for _ in range(limit * 10):
                packed = cursor.key()
                key, label = unpack(packed)
                d = -distance(label, query)
                # Replace with a levenshtein distance, that returns
                # None in the case the maximum threshold is reached,
                # to speed up the algorithm.
                if d >= -2:
                    distances[label] = d
                if not cursor.previous():
                    break

            cursor.seek(nearest, SEEK_GE)

            for _ in range(limit * 10):
                packed = cursor.key()
                key, label = unpack(packed)
                d = -distance(label, query)
                # Replace with a levenshtein distance, that returns
                # None in the case the maximum threshold is reached.
                # to speed up the algorithm.
                if d >= -2:
                    distances[label] = d
                cursor.next()

        print('* most similar according to bbk fuzzbuzz')
        print(distances)
        for key, d in distances.most_common(limit):
            print('**', key, "\t", d)


    else:
        raise NotImplementedError()


    # at last!
    db.close()


if __name__ == "__main__":
    main()
