#!/usr/bin/env python

#############################################################################
##
## This file is part of Taurus, a Tango User Interface Library
## 
## http://www.tango-controls.org/static/taurus/latest/doc/html/index.html
##
## Copyright 2011 CELLS / ALBA Synchrotron, Bellaterra, Spain
## 
## Taurus is free software: you can redistribute it and/or modify
## it under the terms of the GNU Lesser General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
## 
## Taurus is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU Lesser General Public License for more details.
## 
## You should have received a copy of the GNU Lesser General Public License
## along with Taurus.  If not, see <http://www.gnu.org/licenses/>.
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

__docformat__ = "restructuredtext"

import sys
import os.path

try:
    import json
except:
    json = None

from .codecs import *
from .colors import *
from .constant import *
from .containers import *
from .enumeration import *
from .event import *
from .log import *
from .object import *
from .timer import *
from .singleton import *
from .safeeval import *
from .prop import *
from .threadpool import *
from .user import *

import eventfilters

from lxml import etree

def str_DevFailed(df):
    """Returns a string representation of a :class:`PyTango.DevFailed`.
    
    :param df: (PyTango.DevFailed) the PyTango exception object
    :return: (str) a string representation of the given exception"""
    
    ret = ""
    try:
        desc = df.message.desc.rstrip('\n').replace('\n',"              \n")
    
        ret += "   Severity = %s\n" % df.message.severity
        ret += "     Reason = %s\n" % df.message.reason
        ret += "Description = %s\n" % desc
        ret += "     Origin = %s\n" % df.message.origin
    except:
        ret = "Exception = %s" % str(df)
    return ret

def print_DevFailed(df):
    """Prints the contents of the given :class:`PyTango.DevFailed`.
    
    :param df: (PyTango.DevFailed) the PyTango exception object"""
    import PyTango
    PyTango.Except.print_exception(df)

def dictFromSequence(seq):
    """Translates a sequence into a dictionary by converting each to elements of
    the sequence (k,v) into a k:v pair in the dictionary
    
    :param seq: (sequence) any sequence object
    :return: (dict) dictionary built from the given sequence"""
    def _pairwise(iterable):
        """Utility method used by dictFromSequence"""
        itnext = iter(iterable).next
        while True:
            yield itnext(), itnext()
    return dict(_pairwise(seq))

if sys.version_info < (2,6):
    def relpath(path, start=os.path.curdir):
        """Return a relative version of a path"""

        if not path:
            raise ValueError("no path specified")

        start_list = os.path.abspath(start).split(os.path.sep)
        path_list = os.path.abspath(path).split(os.path.sep)

        # Work out how much of the filepath is shared by start and path.
        i = len(os.path.commonprefix([start_list, path_list]))

        rel_list = [os.path.pardir] * (len(start_list)-i) + path_list[i:]
        if not rel_list:
            return os.path.curdir
        return os.path.join(*rel_list)
    
    os.path.relpath = relpath
