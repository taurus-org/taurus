#!/usr/bin/env python

##############################################################################
##
## This file is part of Sardana
##
## http://www.sardana-controls.org/
##
## Copyright 2011 CELLS / ALBA Synchrotron, Bellaterra, Spain
##
## Sardana is free software: you can redistribute it and/or modify
## it under the terms of the GNU Lesser General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## Sardana is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU Lesser General Public License for more details.
##
## You should have received a copy of the GNU Lesser General Public License
## along with Sardana.  If not, see <http://www.gnu.org/licenses/>.
##
##############################################################################

"""This module is part of the Python Sardana libray. It defines the base
classes for Sardana values"""

from __future__ import absolute_import

__all__ = ["SardanaValue"]

__docformat__ = 'restructuredtext'

import time


class SardanaValue(object):

    def __init__(self, value=None, exc_info=None, timestamp=None,
                 dtype=None, dformat=None):
        self.value = value
        self.error = exc_info is not None
        self.exc_info = exc_info
        if timestamp is None:
            timestamp = time.time()
        self.timestamp = timestamp
        self.dtype = dtype
        self.dformat = dformat

    def __repr__(self):
        v = None
        if self.error:
            v = "<Error>"
        else:
            v = self.value
        return "{0.__class__.__name__}(value={1}, timestamp={0.timestamp})".format(self, v)

    def __str__(self):
        return repr(self)
