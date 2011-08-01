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

""" """

__all__ = ["SardanaDevice", "SardanaDeviceClass",
           "to_tango_state", "to_tango_type_format", "to_tango_type",
           "to_tango_access", 
           "GenericScalarAttr", "GenericSpectrumAttr", "GenericImageAttr"]

__docformat__ = 'restructuredtext'

from PyTango import Device_4Impl, DeviceClass, Util, DevFailed, \
    DevVoid, DevLong, DevLong64, DevBoolean, DevString, DevDouble, \
    DevVarLong64Array, DispLevel, DevState, SCALAR, SPECTRUM, IMAGE, \
    READ_WRITE, READ, Attr, SpectrumAttr, ImageAttr
from taurus.core.util.log import Logger, InfoIt

from sardana import DataType, DataFormat, DataAccess

def to_tango_state(state):
    return DevState(state)

def to_tango_type_format(dtype, dformat):
    t = DevLong
    f = SCALAR
    if dtype == DataType.Double:
        t = DevDouble
    elif dtype == DataType.String:
        t = DevString
    elif dtype == DataType.Boolean:
        t = DevBoolean
    if dformat == DataFormat.OneD:
        f = SPECTRUM
    elif dformat == DataFormat.TwoD:
        f = IMAGE
    return t, f

def to_tango_type(dtype):
    t = DevLong
    if dtype == DataType.Double:
        t = DevDouble
    elif dtype == DataType.String:
        t = DevString
    elif dtype == DataType.Boolean:
        t = DevBoolean
    return t

def to_tango_access(access):
    a = READ_WRITE
    if access == DataAccess.ReadOnly:
        a = READ
    return a


class GenericScalarAttr(Attr):
    pass


class GenericSpectrumAttr(SpectrumAttr):
    
    def __init__(self, name, tg_type, tg_access, dim_x=2048):
        SpectrumAttr.__init__(self, name, tg_type, tg_access, dim_x)


class GenericImageAttr(ImageAttr):

    def __init__(self, name, tg_type, tg_access, dim_x=2048, dim_y=2048):
        ImageAttr.__init__(self, name, tg_type, tg_access, dim_x, dim_y)


class SardanaDevice(Device_4Impl, Logger):
    
    def __init__(self, dclass, name):
        Device_4Impl.__init__(self, dclass, name)
        self.init(name)
        if self._alias:
            name = "Tango_%s" % self.alias
        Logger.__init__(self, name)
        
    def init(self, name):
        util = Util.instance()
        db = util.get_database()
        try:
            
            self._alias = db.get_alias(name)
            if self._alias.lower() == 'nada':
                self._alias = None
        except:
            self._alias = None
    
    @property
    def alias(self):
        return self._alias

    def init_device(self):
        self.get_device_properties(self.get_device_class())
    
    def initialize_dynamic_attributes(self):
        pass
    

class SardanaDeviceClass(DeviceClass):

    #    Class Properties
    class_property_list = {}

    #    Device Properties
    device_property_list = {
    }

    #    Command definitions
    cmd_list = {
    }

    #    Attribute definitions
    attr_list = {
    }

    def dyn_attr(self, dev_list):
        for dev in dev_list:
            dev.initialize_dynamic_attributes()

