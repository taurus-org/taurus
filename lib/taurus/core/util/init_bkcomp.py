#!/usr/bin/env python

#############################################################################
##
# This file is part of Taurus
##
# http://taurus-scada.org
##
# Copyright 2011 CELLS / ALBA Synchrotron, Bellaterra, Spain
##
# Taurus is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
##
# Taurus is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
##
# You should have received a copy of the GNU Lesser General Public License
# along with Taurus.  If not, see <http://www.gnu.org/licenses/>.
##
#############################################################################

"""This package consists of a collection of useful classes and functions. Most of
the elements are taurus independent and can be used generically.

This module contains a python implementation of :mod:`json`. This was done because
json only became part of python since version 2.6.
The json implementation follows the rule:

    #. if python >= 2.6 use standard json from python distribution
    #. otherwise use private implementation distributed with taurus
"""
from __future__ import absolute_import


# taurus cannot work properly without the following modules so
# they are promptly imported here has a facility (also for backward
# compatibility)
# However, new applications should in their code use the full import.
# Example, use:
#     from taurus.core.util.log import Logger
# instead of:
#     from taurus.core.util import Logger

from .containers import *
from .enumeration import *
from .event import *
from .log import *
from .object import *
from .singleton import *

from .codecs import *
from .colors import *
from .constant import *
from .timer import *
from .safeeval import *
from .prop import *
from .threadpool import *
from .user import *

from . import eventfilters

try:
    from lxml import etree
except:
    etree = None

__docformat__ = "restructuredtext"

def dictFromSequence(seq):
    """Translates a sequence into a dictionary by converting each to elements of
    the sequence (k,v) into a k:v pair in the dictionary

    :param seq: (sequence) any sequence object
    :return: (dict) dictionary built from the given sequence"""
    def _pairwise(iterable):
        """Utility method used by dictFromSequence"""
        itnext = iter(iterable).__next__
        while True:
            yield itnext(), itnext()
    return dict(_pairwise(seq))










