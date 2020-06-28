import sys


def process(concept):
    items = concept.split('/')
    if items[2] != "en":
        return
    word = items[3]
    if "_" in word:
        return
    print("{}\t{}".format(concept, word))


csv = open(sys.argv[1])

for line in csv:
    items = line.split("\t")
    start = items[2]
    end = items[3]

    process(start)
    process(end)
