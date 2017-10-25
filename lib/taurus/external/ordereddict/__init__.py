from __future__ import absolute_import

try:
    # ordereddict from python 2.7 or from ordereddict installed package?
    from collections import OrderedDict
except ImportError:
    # ordereddict from local import
    import os
