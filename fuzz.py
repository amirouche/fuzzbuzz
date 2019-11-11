import sys
from pathlib import Path
from string import punctuation
from collections import namedtuple

from html2text import HTML2Text
from wordfreq import top_n_list
from unidecode import unidecode
from Stemmer import Stemmer
from collections import Counter
from pyblake2 import blake2b

from lsm import LSM
from lsm import SEEK_LE, SEEK_GE
from tuple import pack, unpack, strinc


HASH_SIZE = 512


DATA = Path('./data').resolve()


GARBAGE_TO_SPACE = dict.fromkeys((ord(x) for x in punctuation), " ")
STOP_WORDS = set(top_n_list("en", 500))

WORD_MIN_LENGTH = 4
WORD_MAX_LENGTH = 64  # sha2 length


instance = HTML2Text()
instance.ignore_links = True
html2text = instance.handle

stem = Stemmer("english").stemWord


def hash(string):
    digest_size = HASH_SIZE // 8
    return int.from_bytes(blake2b(string.encode('utf-8'), digest_size).digest(), 'big')


def sane(word):
    return WORD_MIN_LENGTH <= len(word) <= WORD_MAX_LENGTH


def string2bag(string):
    """Converts a string to a list of words.

    Removes punctuation, lowercase, words strictly smaller than 2 and strictly bigger than 64
    characters

    Returns a set.
    """
    clean = string.translate(GARBAGE_TO_SPACE).lower()
    unaccented = unidecode(clean)
    bag = (stem(word) for word in unaccented.split() if (sane(word) and word not in STOP_WORDS))
    bag = Counter(bag)
    return bag


def int2bits(integer):
    return list(bin(integer)[2:].zfill(HASH_SIZE))


def simhash(features):
    intermediate = [0] * HASH_SIZE
    for feature, count in features.items():
        feature = hash(feature)
        bits = int2bits(feature)
        assert len(bits) == HASH_SIZE
        for index, bit in enumerate(bits):
            intermediate[index] += count if bit == '1' else -count
    # compute simhash
    out = ''.join(['1' if v > 0 else '0' for v in intermediate])
    assert len(out) == HASH_SIZE
    out = int(out, 2)
    return out

def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]


db = LSM('fuzzbuzz.ldb')


def merkeltree(booleans):
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


def fuzzbuzz(bitstring):
    booleans = [bit == '1' for bit in bitstring]
    tree = merkeltree(booleans)
    buzz = ''.join('1' if x else '0' for x in tree)
    out = int(buzz, 2)
    return out


def hamming2(s1, s2):
    """Calculate the Hamming distance between two bit strings"""
    s1 = int2bits(s1)
    s2 = int2bits(s2)
    # Taken from https://stackoverflow.com/a/31007358/140837
    assert len(s1) == len(s2)
    return sum(c1 != c2 for c1, c2 in zip(s1, s2))


input = list(DATA.glob('*/*/*/*'))
LIMIT = 10

if sys.argv[1] == 'index':

    for filepath in input:
        print(filepath)

        with filepath.open() as f:
            html = f.read()

        text = html2text(html)
        bag = string2bag(text)
        value = simhash(bag)
        bitstring = int2bits(value)
        value = value.to_bytes(HASH_SIZE // 8, 'big')
        assert len(bitstring) == HASH_SIZE, "bitstring is not good"
        for subspace, chunk in enumerate(chunks(bitstring, HASH_SIZE // 4)):
            out = fuzzbuzz(chunk)
            length = (HASH_SIZE * 2) // 8
            key = out.to_bytes(length, 'big')
            db[pack((subspace, key, value, str(filepath)))] = b'\x42'

elif sys.argv[1] == 'query':
    html = sys.stdin.read()
    text = html2text(html)
    bag = string2bag(text)
    integer = simhash(bag)

    # check that bbk fuzzbuzz does something similar
    distances = Counter()

    bitstring = int2bits(integer)
    for subspace, chunk in enumerate(chunks(bitstring, HASH_SIZE // 4)):
        with db.cursor() as cursor:
            out = fuzzbuzz(chunk)
            length = (HASH_SIZE * 2) // 8
            key = out.to_bytes(length, 'big')
            # strip the NULL byte suffix included in all strings by pack
            start = pack((subspace, key))
            start = start[:-1]
            cursor.seek(start, SEEK_LE)
            current = cursor.key()
            def lcp(a, b):
                """Longest Common Prefix between a and b"""
                out = []
                for x, y in zip(a, b):
                    if x == y:
                        out.append(x.to_bytes(1, 'big'))
                    else:
                        break
                return b''.join(out)



            prefix = lcp(start, current)
            end = strinc(prefix)

            cursor.seek(prefix, SEEK_GE)
            for packed, _ in cursor.fetch_until(end):
                _, _, other, filepath = unpack(packed)
                other = int.from_bytes(other, 'big')
                distances[filepath] = -hamming2(integer, other)

    print('* most similar according to bbk fuzzbuzz')
    for key, distance in distances.most_common(LIMIT):
        print('**', key, "\t", distance)
    print('* bbk fuzzbuzz computed the hamming distance against:', len(distances), "documents")

    # compute the hamming distance with all the documents

    distances = Counter()

    for filepath in input:
        with filepath.open() as f:
            html = f.read()

        text = html2text(html)
        bag = string2bag(text)
        other = simhash(bag)
        distances[str(filepath)] = -hamming2(integer, other)

    # check that hamming distance capture something
    print('* most similar according to hamming distance over the simhash')
    for key, distance in distances.most_common(LIMIT):
        print('**', key, "\t", distance)
    print('* There is grand total of:', len(distances), "documents")

else:
    raise NotImplementedError()


# at last!
db.close()
