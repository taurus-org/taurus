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

"""This module is part of the Python Pool libray. It defines the base classes
for moveable elements"""

__all__ = ["PoolMoveable"]

__docformat__ = 'restructuredtext'


class PoolMoveable(object):

    def get_size(self):
        raise RuntimeError("Must be implemented in subclass")

    def calc_move(self, positions, ctrl_map, trust=False):
        raise RuntimeError("Must be implemented in subclass")

    def set_value(self, v, propagate=True):
        raise RuntimeError("Must be implemented in subclass")

    def get_value(self, cache=True):
        raise RuntimeError("Must be implemented in subclass")
