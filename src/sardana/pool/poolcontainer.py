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
for a pool container element"""

__all__ = ["PoolContainer"]

__docformat__ = 'restructuredtext'

from sardana.sardanacontainer import SardanaContainer


class PoolContainer(SardanaContainer):
    """A container class for pool elements"""
    
    def get_controller_class(self, **kwargs):
        eid = kwargs.get("id")
        if eid is not None:
            return self.get_controller_class_by_id(eid, **kwargs)
        
        name = kwargs.pop("name")
        self.get_controller_class_by_name(name, **kwargs)
    
    def get_controller_class_by_id(self, eid, **kwargs):
        raise NotImplementedError
    
    def get_controller_class_by_name(self, name, **kwargs):
        raise NotImplementedError