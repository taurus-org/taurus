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

__all__ = ["Controller", "ControllerClass"]

__docformat__ = 'restructuredtext'

import sys
import PyTango

from taurus.core.util.log import InfoIt, DebugIt

from sardana import DataType, DataFormat
from PoolDevice import PoolDevice, PoolDeviceClass
from sardana.tango.core import to_tango_type_format, to_tango_access

def to_bool(s):
    return s.lower() == "true"

class Controller(PoolDevice):

    def __init__(self, dclass, name):
        PoolDevice.__init__(self, dclass, name)
        self.init_device()

    def init(self, name):
        PoolDevice.init(self, name)

    def get_ctrl(self):
        return self.element

    def set_ctrl(self, ctrl):
        self.element = ctrl
    
    ctrl = property(get_ctrl, set_ctrl)
    
    @DebugIt()
    def delete_device(self):
        self.pool.delete_element(self.ctrl.get_name())
    
    #@DebugIt()
    def init_device(self):
        self.set_state(PyTango.DevState.ON)
        self.get_device_properties(self.get_device_class())
        self.set_change_event("ElementList", True, False)
        
        if self.ctrl is None:
            props = self._get_ctrl_properties()
            ctrl = self.pool.create_controller(type=self.Type,
                name=self.alias, full_name=self.get_name(),
                library=self.Library, klass=self.Klass, id=self.Id, properties=props)
            ctrl.add_listener(self.elements_changed)
            self.ctrl = ctrl
    
    def _get_ctrl_properties(self):
        try:
            ctrl_info = self.pool.get_controller_class_info(self.Klass)
            prop_infos = ctrl_info.getControllerProperties()
        except:
            return {}
        db = PyTango.Util.instance().get_database()
        
        props = {}
        if prop_infos:
            props.update(db.get_device_property(self.get_name(), prop_infos.keys()))
        for p in props.keys():
            if len(props[p]) == 0: props[p] = None

        ret = {}
        missing_props = []
        for prop_name, prop_value in props.items():
            if prop_value is None:
                dv = prop_infos[prop_name].default_value
                if dv is None:
                    missing_props.append(prop_name)
                ret[prop_name] = dv
                continue
            prop_info = prop_infos[prop_name]
            dtype, dformat = prop_info.dtype, prop_info.dformat
            
            op = str
            if dtype == DataType.Integer:
                op = int
            elif dtype == DataType.Double:
                op = float
            elif dtype == DataType.Boolean:
                op = to_bool
            prop_value = map(op, prop_value)
            if dformat == DataFormat.Scalar:
                prop_value = prop_value[0]
            ret[prop_name] = prop_value
        
        if missing_props:
            self.set_state(PyTango.DevState.ALARM)
            missing_props = ", ".join(missing_props)
            self.set_status("Controller has missing properties: %s" % missing_props)
        
        return ret
    
    def always_executed_hook(self):
        pass
    
    def read_attr_hardware(self,data):
        pass
    
    def dev_state(self):
        if self.ctrl is None or not self.ctrl.is_online():
            return PyTango.DevState.FAULT
        return PyTango.DevState.ON
    
    def dev_status(self):
        if self.ctrl is None or not self.ctrl.is_online():
            self._status = self.ctrl.get_ctrl_error_str()
        else:
            self._status = PoolDevice.dev_status(self)
        return self._status
    
    def read_ElementList(self, attr):
        attr.set_value(self.get_element_names())

    def CreateElement(self, argin):
        pass
    
    def DeleteElement(self, argin):
        pass
    
    def get_element_names(self):
        elements = self.ctrl.get_elements()
        return [ elements[id].get_name() for id in sorted(elements) ]
    
    def elements_changed(self, evt_src, evt_type, evt_value):
        self.push_change_event("ElementList", self.get_element_names())

    def initialize_dynamic_attributes(self):
        info = self.ctrl.ctrl_info
        if info is None:
            self.warning("Controller %s doesn't have any information", self.ctrl)
            return
        for name, attr_info in info.getControllerAttributes().items():
            tg_type, tg_format = to_tango_type_format(attr_info.dtype, attr_info.dformat)
            tg_access = to_tango_access(attr_info.access)
            read, write = Controller.read_DynammicAttribute, None
            if tg_access == PyTango.READ_WRITE:
                write = Controller.write_DynammicAttribute
            klass = GenericScalarAttr
            if tg_format == PyTango.SPECTRUM:
                klass = GenericSpectrumAttr
            elif tg_format == PyTango.IMAGE:
                klass = GenericImageAttr
                
            attr = klass(name, tg_type, tg_access)
            if tg_access == PyTango.READ_WRITE:
                attr.set_memorized()
                attr.set_memorized_init(True)
            self.add_attribute(attr, read, write)

    def read_DynammicAttribute(self, attr):
        attr_name = attr.get_name()
        attr.set_value(self.ctrl.get_ctrl_attr(attr_name))

    def write_DynammicAttribute(self, attr):
        v = attr.get_write_value()
        attr_name = attr.get_name()
        self.ctrl.set_ctrl_attr(attr_name, v)

    def read_LogLevel(self, attr):
        l = self.ctrl.get_log_level()
        self.debug(l)
        attr.set_value(l)
    
    def write_LogLevel(self, attr):
        self.ctrl.set_log_level(attr.get_write_value())
    

class GenericScalarAttr(PyTango.Attr):
    pass


class GenericSpectrumAttr(PyTango.SpectrumAttr):
    
    def __init__(self, name, tg_type, tg_access):
        PyTango.SpectrumAttr.__init__(self, name, tg_type, tg_access, 2048)


class GenericImageAttr(PyTango.ImageAttr):

    def __init__(self, name, tg_type, tg_access):
        PyTango.ImageAttr.__init__(self, name, tg_type, tg_access, 2048, 2048)


class ControllerClass(PoolDeviceClass):

    #    Class Properties
    class_property_list = {
        }
    class_property_list.update(PoolDeviceClass.class_property_list)

    #    Device Properties
    device_property_list = {
        'Type':
            [PyTango.DevString,
            "",
            [] ],
        'Library':
            [PyTango.DevString,
            "",
            [] ],
        'Klass':
            [PyTango.DevString,
            "",
            [] ],
        }
    device_property_list.update(PoolDeviceClass.device_property_list)

    #    Command definitions
    cmd_list = {
        'CreateElement':
            [[PyTango.DevVarStringArray, ""],
            [PyTango.DevVoid, ""]],
        'DeleteElement':
            [[PyTango.DevString, ""],
            [PyTango.DevVoid, ""]],
        }
    cmd_list.update(PoolDeviceClass.cmd_list)

    #    Attribute definitions
    attr_list = {
        'ElementList':
            [[PyTango.DevString,
            PyTango.SPECTRUM,
            PyTango.READ, 4096]],
        'LogLevel':
            [[PyTango.DevLong,
            PyTango.SCALAR,
            PyTango.READ_WRITE]],
        }
    attr_list.update(PoolDeviceClass.attr_list)

    def __init__(self, name):
        PoolDeviceClass.__init__(self, name)
        self.set_type(name)
    

if __name__ == '__main__':
    try:
        py = PyTango.Util(sys.argv)
        py.add_class(ControllerClass,Controller,'Controller')

        U = PyTango.Util.instance()
        U.server_init()
        U.server_run()

    except PyTango.DevFailed,e:
        print '-------> Received a DevFailed exception:',e
    except Exception,e:
        print '-------> An unforeseen exception occured....',e
