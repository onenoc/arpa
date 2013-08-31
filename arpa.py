#!/usr/bin/env python
# Copyright 2013 Tetsuo Kiso. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

import optparse
import cPickle
import mmap
import sys
from collections import defaultdict

def read_header(mm):
    # Move to the header
    ptr = mm.find('\\data\\')
    if ptr == -1:
        print 'ARPA file format is broken'
        sys.exit()
    mm.seek(ptr)
    mm.readline()

    # Detect N-gram order
    while True:
        line = mm.readline()
        if line == '\n':
            break
        ngram_order = int(line[6:7])
    return ngram_order

def move_start_ngram(mm, n):
    ptr = mm.find('\\%d-grams' % n)
    if ptr == -1:
        print 'ARPA file format is broken at reading %d-grams' % n
        sys.exit()
    mm.seek(ptr)
    mm.readline()

def read_unigram(mm, vocab, vocab_array):
    # giant unigram array
    unigram = []

    entry = []
    while True:
        line = mm.readline().rstrip()
        if line == '':
            break
        entry = line.split('\t')

        # print entry
        vocab_array.append(entry[1])
        vocab[entry[1]] = len(vocab_array)
        if len(entry) == 3:
            unigram.append((float(entry[0]), len(vocab), float(entry[2])))
        elif len(entry) == 2: # there is no backoff
            unigram.append((float(entry[0]), len(vocab), None))
    return unigram

# This is the most time-consuming part.
def read_higher_order_ngram(mm, n, ngram_order, vocab):
    ngram = []
    piece = []
    entry = []
    while True:
        line = mm.readline().rstrip()
        if line == '':
            break
        buf = line.split('\t')
        piece = buf[1].split(' ')

        entry.append(float(buf[0]))

        for s in piece:
            entry.append(vocab[s])

        # # Set back-off weights. This is needed for (N-1)-grams.
        if n < ngram_order:
            if len(buf) == n + 2:
                entry.append(float(buf[-1]))
            elif len(buf) == n + 1: # there is no backoff
                entry.append(None)

        ngram.append(tuple(entry))
        entry = []
    return ngram

# too long...
def read_arpa(filename, length=0):
    """Read text ARPA format using the mmap module."""

    # giant unigram array
    ptr = 0
    vocab_array = []
    vocab = defaultdict(int)

    # The N-gram order we're reading.
    ngram_order = 1

    # array of unigram, bigram, trigram, ... entries
    ngram_arrays = []

    with open(filename, 'r+b') as f:
        mm = mmap.mmap(f.fileno(), length, mmap.MAP_SHARED)

        ngram_order = read_header(mm)

        # Unigram
        move_start_ngram(mm, 1)
        ngram_arrays.append(read_unigram(mm, vocab, vocab_array))

        # Read higher order N-gram
        order = None
        if ngram_order > 1:
            order = 2

        for n in range(order, ngram_order + 1):
            move_start_ngram(mm, n)
            ngram_arrays.append(read_higher_order_ngram(mm, n, ngram_order, vocab))

        mm.close()
    return vocab, vocab_array, ngram_arrays

def serialize_and_write(filename, vocab, vocab_array, ngram_arrays):
    """Serialize and write ARPA to a file."""
    with open(filename, 'wb') as fout:
        cPickle.dump(vocab, fout)
        cPickle.dump(vocab_array, fout)
        cPickle.dump(ngram_arrays, fout)

def read_serialized(filename):
    with open(filename, 'rb') as f:
        vocab = cPickle.load(f)
        vocab_array = cPickle.load(f)
        ngram_arrays = cPickle.load(f)
    return vocab, vocab_array, ngram_arrays

def main():
    from optparse import OptionParser
    parser = OptionParser(usage="usage: %prog [--text] FILE")
    parser.add_option("--text", action="store_true",
                      dest="text", default=False,
                      help="read text file")
    (opts, args) = parser.parse_args()

    if opts.text:
        vocab, vocab_array, ngram_arrays = read_arpa(args[0])
    else:
        vocab, vocab_array, ngram_arrays = read_serialized(args[0])

if __name__ == '__main__':
    main()
