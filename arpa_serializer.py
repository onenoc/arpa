#!/usr/bin/env python
# Copyright 2013 Tetsuo Kiso. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

import sys
import arpa

"""
Usage: arpa_serializer.py IN OUT
"""

def main():
    if len(sys.argv) <= 2:
        print 'Usage: %s IN OUT' % sys.argv[0]
        sys.exit()
    vocab, vocab_array, ngram_arrays = arpa.read_arpa(sys.argv[1])
    arpa.serialize_and_write(sys.argv[2], vocab, vocab_array, ngram_arrays)

if __name__ == '__main__':
    main()
