arpa
====

Python modules that reads a ARPA file in both text and serialized
format by cPickle module.

The module for serialization is also avaiable.

### Usage ###

Read serialized files

    $ ./arpa.py arpa.pickle

Read text ARPA files:

    $ ./arpa.py --text arpa.txt

Serialize ARPA files

    $ ./arpa_serializer.py arpa.txt arpa.pickle

## License ##

This code is distributed under the New BSD License. See the file LICENSE.