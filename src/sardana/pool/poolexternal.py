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

"""This module is part of the Python Pool libray. It defines the base classes
for external objects to the pool (like tango objects)"""

__all__ = ["PoolBaseExternalObject", "PoolTangoObject"]

__docformat__ = 'restructuredtext'

import PyTango

from sardana import ElementType
from poolbase import PoolBaseObject


class PoolBaseExternalObject(PoolBaseObject):
    """TODO"""
    
    def __init__(self, **kwargs):
        PoolBaseObject.__init__(self, **kwargs)
    
    def get_type(self):
        """Returns this pool object type
        
        :return: this pool object type
        :rtype: :obj:'"""
        return ElementType.External
    
    def get_source(self):
        return self.full_name

class PoolTangoObject(PoolBaseExternalObject):
    """TODO"""
    
    def __init__(self, **kwargs):
        scheme = kwargs.pop('scheme', 'tango')
        attributename = kwargs.pop('attributename')
        host, port = kwargs.pop('host', None), kwargs.pop('port', None)
        devalias = kwargs.pop('devalias', None)
        devicename = kwargs.pop('devicename', None)
        if host is None:
            db = PyTango.Database()
            host, port = db.get_db_host(), db.get_db_port()
        else:
            db = PyTango.Database(host, port)
        full_name = "<unknown>"
        if devicename is None:
            if devalias is not None:
                try:
                    devicename = db.get_device_alias(devalias)
                    full_name = "{0}:{1}/{2}/{3}".format(host, port, devicename,
                                                         attributename)
                except:
                    full_name = "{0}/{1}".format(devalias, attributename)
        else:
            full_name = "{0}:{1}/{2}/{3}".format(host, port, devicename,
                                                 attributename)
        kwargs['name'] = attributename
        kwargs['full_name'] = full_name
        PoolBaseExternalObject.__init__(self, **kwargs)

