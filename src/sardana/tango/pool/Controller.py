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

from PyTango import Util, DevFailed
from PyTango import DevVoid, DevLong, DevLong64, DevBoolean, DevString, DevDouble
from PyTango import DevVarStringArray, DevVarLongArray
from PyTango import DispLevel, DevState
from PyTango import SCALAR, SPECTRUM, IMAGE
from PyTango import READ_WRITE, READ
from PyTango import Attr, SpectrumAttr, ImageAttr

from taurus.core.util.log import InfoIt, DebugIt

from sardana import DataType, DataFormat
from sardana.tango.core import GenericScalarAttr, GenericSpectrumAttr, \
    GenericImageAttr, to_tango_type_format, to_tango_access

from PoolDevice import PoolDevice, PoolDeviceClass

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
    
    @InfoIt()
    def init_device(self):
        PoolDevice.init_device(self)

        detect_evts = "state", "status"
        non_detect_evts = "elementlist",
        self.set_change_events(detect_evts, non_detect_evts)

        if self.ctrl is None:
            args = dict(type=self.Type, name=self.alias,
                        full_name=self.get_name(),
                        library=self.Library, klass=self.Klass,
                        id=self.Id, role_ids=self.Role_ids,
                        properties=self._get_ctrl_properties())
            ctrl = self.pool.create_controller(**args)
            ctrl.add_listener(self.elements_changed)
            self.ctrl = ctrl
        
    def _get_ctrl_properties(self):
        try:
            ctrl_info = self.pool.get_controller_class_info(self.Klass)
            prop_infos = ctrl_info.getControllerProperties()
        except:
            return {}
        db = Util.instance().get_database()
        
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
            self.set_state(DevState.ALARM)
            missing_props = ", ".join(missing_props)
            self.set_status("Controller has missing properties: %s" % missing_props)
        
        return ret
    
    def always_executed_hook(self):
        pass
    
    def read_attr_hardware(self,data):
        pass
    
    def dev_state(self):
        if self.ctrl is None or not self.ctrl.is_online():
            return DevState.FAULT
        return DevState.ON
    
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
            if tg_access == READ_WRITE:
                write = Controller.write_DynammicAttribute
            klass = GenericScalarAttr
            if tg_format == SPECTRUM:
                klass = GenericSpectrumAttr
            elif tg_format == IMAGE:
                klass = GenericImageAttr
                
            attr = klass(name, tg_type, tg_access)
            if tg_access == READ_WRITE:
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


class ControllerClass(PoolDeviceClass):

    #    Class Properties
    class_property_list = {
    }
    class_property_list.update(PoolDeviceClass.class_property_list)

    #    Device Properties
    device_property_list = {
        'Type':           [DevString, "", [] ],
        'Library':        [DevString, "", [] ],
        'Klass':          [DevString, "", [] ],
        'Role_ids':       [DevVarLongArray, "", [] ],
    }
    device_property_list.update(PoolDeviceClass.device_property_list)

    #    Command definitions
    cmd_list = {
        'CreateElement': [ [DevVarStringArray, ""], [DevVoid, ""] ],
        'DeleteElement': [ [DevString, ""], [DevVoid, ""] ],
    }
    cmd_list.update(PoolDeviceClass.cmd_list)

    #    Attribute definitions
    attr_list = {
        'ElementList':   [ [DevString, SPECTRUM, READ, 4096] ],
        'LogLevel':      [ [DevLong, SCALAR, READ_WRITE],
                           { 'Memorized'     : "true",
                             'label'         : "Log level",
                             'Display level' : DispLevel.EXPERT } ],
        }
    attr_list.update(PoolDeviceClass.attr_list)

    def __init__(self, name):
        PoolDeviceClass.__init__(self, name)
        self.set_type(name)
