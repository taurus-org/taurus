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

"""This module is part of the Python Sardana libray. It defines the base class
for Sardana manager"""

from __future__ import absolute_import

__all__ = ["SardanaElementManager", "SardanaIDManager"]

__docformat__ = 'restructuredtext'

from taurus.core.util.codecs import CodecFactory

from sardana import InvalidId


class SardanaElementManager(object):
    """A class capable of manage elements"""
    
    SerializationProtocol = 'json'
    
    def get_serialization_protocol(self):
        return self.SerializationProtocol
    
    def set_serialization_protocol(self, protocol):
        self.SerializationProtocol = protocol
    
    serialization_protocol = property(get_serialization_protocol,
                                      set_serialization_protocol,
                                      doc="the serialization protocol")
    
    def serialize_element(self, element, *args, **kwargs):
        obj = element.serialize(*args, **kwargs)
        return self.serialize_object(obj)
    
    def serialize_object(self, obj, *args, **kwargs):
        return CodecFactory().encode(self.serialization_protocol, ('', obj),
                                     *args, **kwargs)[1]
    
    def str_element(self, element, *args, **kwargs):
        obj = element.serialize(*args, **kwargs)
        return self.str_object(obj)
    
    def str_object(self, obj, *args, **kwargs):
        # TODO: use the active codec instead of hardcoded json
        return  CodecFactory().encode('json', ('', obj), *args, **kwargs)[1]


class SardanaIDManager(object):
    """A class capable of manage ids"""
    
    _last_id = InvalidId
    
    def get_new_id(self):
        """Returns a new ID. The ID becomes reserved at this moment.
        
        :return: a new ID
        :rtype: int"""
        self._last_id += 1
        return self._last_id
    
    def rollback_id(self):
        """Free previously reserved ID"""
        self._last_id -= 1
    
    def reserve_id(self, nid):
        """Marks the given ID as reserved
        
        :param id: the ID to be reserved
        :type id: int"""
        assert type(nid) == int
        if nid > self._last_id:
            self._last_id = nid
    