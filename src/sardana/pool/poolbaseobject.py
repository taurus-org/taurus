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

__all__ = ["PoolBaseObject"]

__docformat__ = 'restructuredtext'

from sardana.sardanabase import SardanaBaseObject


class PoolBaseObject(SardanaBaseObject):
    """The Pool most abstract object."""
    
    def __init__(self, **kwargs):
        kwargs['manager'] = kwargs.pop('pool')
        SardanaBaseObject.__init__(self, **kwargs)
    
    def get_pool(self):
        """Return the :class:`sardana.pool.pool.Pool` which *owns* this pool
        object.
        
        :return: the pool which *owns* this pool object.
        :rtype: :class:`sardana.pool.pool.Pool`"""
        return self.get_manager()
    
    def serialize(self, *args, **kwargs):
        kwargs = SardanaBaseObject.serialize(self, *args, **kwargs)
        kwargs['pool'] = self.pool.name
        return kwargs
    
    pool = property(get_pool,
                    doc="reference to the :class:`sardana.pool.pool.Pool`")
    
