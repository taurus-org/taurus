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

"""This module is part of the Python Pool library. It defines the base classes
for Pool object"""

__all__ = ["PoolObject"]

__docformat__ = 'restructuredtext'

from sardana.sardanabase import SardanaObjectID
from sardana.pool.poolbaseobject import PoolBaseObject


class PoolObject(SardanaObjectID, PoolBaseObject):
    """A Pool object that besides the name and reference to the pool has:

       - _id : the internal identifier"""

    def __init__(self, **kwargs):
        SardanaObjectID.__init__(self, id=kwargs.pop('id'))
        PoolBaseObject.__init__(self, **kwargs)

    def serialize(self, *args, **kwargs):
        kwargs = PoolBaseObject.serialize(self, *args, **kwargs)
        kwargs = SardanaObjectID.serialize(self, *args, **kwargs)
        return kwargs
