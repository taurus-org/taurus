#!/usr/bin/env python

##############################################################################
##
## This file is part of Sardana
##
## http://www.tango-controls.org/static/sardana/latest/doc/html/index.html
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

__all__ = ["SardanaBaseManager"]

__docformat__ = 'restructuredtext'


from taurus.core.util import CodecFactory


class SardanaBaseManager(object):
    
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

