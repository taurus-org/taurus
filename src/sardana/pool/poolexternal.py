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
for external objects to the pool (like tango objects)"""

__all__ = ["PoolBaseExternalObject", "PoolTangoObject", "PoolExternalObject"]

__docformat__ = 'restructuredtext'

import PyTango

from sardana import ElementType
from sardana.pool.poolbaseobject import PoolBaseObject


class PoolBaseExternalObject(PoolBaseObject):
    """TODO"""

    def __init__(self, **kwargs):
        kwargs['elem_type'] = ElementType.External
        PoolBaseObject.__init__(self, **kwargs)

    def get_source(self):
        return self.full_name

    def get_config(self):
        raise NotImplementedError


class PoolTangoObject(PoolBaseExternalObject):
    """TODO"""

    def __init__(self, **kwargs):
        scheme = kwargs.pop('scheme', 'tango')
        attribute_name = kwargs.pop('attributename')
        host, port = kwargs.pop('host', None), kwargs.pop('port', None)
        devalias = kwargs.pop('devalias', None)
        device_name = kwargs.pop('devicename', None)
        if host is None:
            db = PyTango.Database()
            host, port = db.get_db_host(), db.get_db_port()
        else:
            db = PyTango.Database(host, port)
        full_name = "<unknown>"
        if device_name is None:
            if devalias is not None:
                try:
                    device_name = db.get_device_alias(devalias)
                    full_name = "{0}:{1}/{2}/{3}".format(host, port,
                                                         device_name,
                                                         attribute_name)
                except:
                    full_name = "{0}/{1}".format(devalias, attribute_name)
        else:
            full_name = "{0}:{1}/{2}/{3}".format(host, port, device_name,
                                                 attribute_name)
        self._device_name = device_name
        self._attribute_name = attribute_name
        self._config = None
        self._device = None
        kwargs['name'] = attribute_name
        kwargs['full_name'] = full_name
        PoolBaseExternalObject.__init__(self, **kwargs)

    def get_device_name(self):
        return self._device_name

    def get_attribute_name(self):
        return self._attribute_name

    def get_device(self):
        device = self._device
        if device is None:
            try:
                self._device = device = PyTango.DeviceProxy(self._device_name)
            except:
                pass
        return device

    def get_config(self):
        config = self._config
        if config is None:
            try:
                self._config = config = \
                    self._device.get_attribute_config(self._attribute_name)
            except:
                pass
        return config

    device_name = property(get_device_name)
    attribute_name = property(get_attribute_name)


_SCHEME_CLASS = { 'tango' : PoolTangoObject,
                  None    : PoolTangoObject}


def PoolExternalObject(**kwargs):
    scheme = kwargs.get('scheme', 'tango')
    klass = _SCHEME_CLASS[scheme]
    return klass(**kwargs)

