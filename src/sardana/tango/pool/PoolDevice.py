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

"""Generic Tango Pool Device base classes"""

__all__ = ["PoolDevice", "PoolDeviceClass",
           "PoolElementDevice", "PoolElementDeviceClass",
           "PoolGroupDevice", "PoolGroupDeviceClass"]

__docformat__ = 'restructuredtext'

import time

from PyTango import Util, DevVoid, DevLong, DevLong64, DevBoolean, DevString, \
    DevDouble, DevVarStringArray, DispLevel, DevState, SCALAR, SPECTRUM, \
    IMAGE, READ_WRITE, READ, AttReqType, AttrData
    
from taurus.core.util import CaselessDict
#from taurus.core.util.log import DebugIt, InfoIt

from sardana import State, InvalidId, InvalidAxis, ElementType
from sardana.pool.poolmetacontroller import DataInfo
from sardana.tango.core.SardanaDevice import SardanaDevice, SardanaDeviceClass
from sardana.tango.core.util import GenericScalarAttr, GenericSpectrumAttr, \
    GenericImageAttr, to_tango_attr_info


class PoolDevice(SardanaDevice):
    """Base Tango Pool Device class"""

    ExtremeErrorStates = DevState.FAULT, DevState.UNKNOWN
    BusyStates = DevState.MOVING, DevState.RUNNING

    BusyRetries = 3    
    
    def __init__(self, dclass, name):
        SardanaDevice.__init__(self, dclass, name)
    
    def init(self, name):
        SardanaDevice.init(self, name)
        util = Util.instance()
        self._pool_device = util.get_device_list_by_class("Pool")[0]
        self._element = None
        
    @property
    def pool_device(self):
        return self._pool_device

    @property
    def pool(self):
        return self.pool_device.pool
    
    def get_element(self):
        return self._element
    
    def set_element(self, element):
        self._element = element
    
    element = property(get_element, set_element)
    
    def init_device(self):
        SardanaDevice.init_device(self)
    
    def delete_device(self):
        SardanaDevice.delete_device(self)
        #self.pool.delete_element(self.element.get_name())
        
    def Abort(self):
        self.element.abort()
        try:
            self.element.get_state(cache=False, propagate=2)
        except:
            self.info("Abort: failed to read state")
    
    def is_Abort_allowed(self):
        return self.get_state() != DevState.UNKNOWN
    
    def Stop(self):
        self.element.stop()
        try:
            self.element.get_state(cache=False, propagate=2)
        except:
            self.info("Stop: failed to read state")
    
    def is_Stop_allowed(self):
        return self.get_state() != DevState.UNKNOWN
    
    def _is_allowed(self, req_type):
#        state = self.get_state()
#        if state in self.ExtremeErrorStates:
#            return False
#        if req_type == AttReqType.WRITE_REQ:
#            if state in self.BusyStates:
#                return False
        return True

    def get_dynamic_attributes(self):
        return CaselessDict(), CaselessDict()

    def initialize_dynamic_attributes(self):
        self._attributes = attrs = CaselessDict()
        
        attr_data = self.get_dynamic_attributes()
        
        std_attrs, dyn_attrs = attr_data
        self.remove_unwanted_dynamic_attributes()

        #self.info("init dynamic attributes %s %s", std_attrs.keys(), dyn_attrs.keys())

        if std_attrs is not None:
            read = self.__class__._read_DynamicAttribute
            write = self.__class__._write_DynamicAttribute
            is_allowed = self.__class__._is_DynamicAttribute_allowed
            for attr_name, data_info in std_attrs.items():
                attr_name, data_info, attr_info = data_info
                attr = self.add_standard_attribute(attr_name, data_info,
                                                   attr_info, read,
                                                   write, is_allowed)
                attrs[attr.get_name()] = None
        
        if dyn_attrs is not None:
            read = self.__class__._read_DynamicAttribute
            write = self.__class__._write_DynamicAttribute
            is_allowed = self.__class__._is_DynamicAttribute_allowed
            for attr_name, data_info in dyn_attrs.items():
                attr_name, data_info, attr_info = data_info
                attr = self.add_dynamic_attribute(attr_name, data_info,
                                                  attr_info, read,
                                                  write, is_allowed)
                attrs[attr.get_name()] = None
        return attrs
    
    def remove_unwanted_dynamic_attributes(self):
        """Removes unwanted dynamic attributes from previous device creation"""
        
        dev_class = self.get_device_class()
        multi_attr = self.get_device_attr()
        multi_class_attr = dev_class.get_class_attr()
        static_attr_names = map(str.lower, dev_class.attr_list.keys())
        static_attr_names.extend(('state', 'status'))
        standard_attr_names = map(str.lower, dev_class.standard_attr_list.keys())
        
        device_attr_names = []
        for i in range(multi_attr.get_attr_nb()):
            device_attr_names.append(multi_attr.get_attr_by_ind(i).get_name())
        
        for attr_name in device_attr_names:
            attr_name_lower = attr_name.lower()
            if attr_name_lower in static_attr_names:
                continue
            try:
                self.remove_attribute(attr_name)
            except Exception, e:
                self.warning("Error removing dynamic attribute %s (%s)",
                             attr_name_lower, e)
        
        klass_attr_names = []
        klass_attrs = multi_class_attr.get_attr_list()
        for ind in range(len(klass_attrs)):
            klass_attr_names.append(klass_attrs[ind].get_name())
        
        klass_name = dev_class.get_name()
        for attr_name in klass_attr_names:
            attr_name_lower = attr_name.lower()
            if attr_name_lower in static_attr_names:
                continue
            try:
                attr = multi_class_attr.get_attr(attr_name)
                multi_class_attr.remove_attr(attr.get_name(), attr.get_cl_name())
            except Exception, e:
                self.warning("Error removing dynamic attribute %s from device "
                             "class (%s)",
                             attr_name, e)
    
    def add_dynamic_attribute(self, attr_name, data_info, attr_info, read,
                              write, is_allowed):
        tg_type, tg_format, tg_access = data_info[0]

        if tg_access == READ:
            write = None
        klass = GenericScalarAttr
        if tg_format == SPECTRUM:
            klass = GenericSpectrumAttr
        elif tg_format == IMAGE:
            klass = GenericImageAttr
            
        attr = klass(attr_name, tg_type, tg_access)
        if tg_access == READ_WRITE and tg_format == SCALAR:
            attr.set_memorized()
            attr.set_memorized_init(True)
        attr.set_disp_level(DispLevel.EXPERT)
        return self.add_attribute(attr, read, write, is_allowed)
    
    def add_standard_attribute(self, attr_name, data_info, attr_info, read,
                               write, is_allowed):
        dev_class = self.get_device_class()
        attr_data = AttrData(attr_name, dev_class.get_name(), data_info)
        attr = self.add_attribute(attr_data, read, write, is_allowed)
        return attr
    
    def read_DynamicAttribute(self, attr):
        raise NotImplementedError

    def write_DynamicAttribute(self, attr):
        raise NotImplementedError

    def is_DynamicAttribute_allowed(self, req_type):
        return self._is_allowed(req_type)
    
    def _read_DynamicAttribute(self, attr):
        name = attr.get_name()
        
        read_name = "read_" + name
        if hasattr(self, read_name):
            read = getattr(self, read_name)
            return read(attr)
        
        return self.read_DynamicAttribute(attr)
    
    def _write_DynamicAttribute(self, attr):
        name = attr.get_name()
        write_name = "write_" + name
        if hasattr(self, write_name):
            write = getattr(self, write_name)
            return write(attr)
        return self.write_DynamicAttribute(attr)

    def _is_DynamicAttribute_allowed(self, req_type):
        return self.is_DynamicAttribute_allowed(req_type)

    def dev_state(self):
        element = self.element
        try:
            moving = self.get_state() == DevState.MOVING and element.is_in_operation()
            ctrl_state = element.get_state(cache=moving, propagate=0)
            state = self.calculate_tango_state(ctrl_state)
            return state
        except:
            self.error("Exception trying to return state")
            self.debug("Details:", exc_info=1)
            return DevState.FAULT
            
    def dev_status(self):
        element = self.element
        try:
            moving = self.get_state() == DevState.MOVING and element.is_in_operation()
            ctrl_status = self.element.get_status(cache=moving, propagate=0)
            status = self.calculate_tango_status(ctrl_status)
            return status
        except Exception, e:
            msg = "Exception trying to return status: %s" % str(e)
            self.error(msg)
            self.debug("Details:", exc_info=1)
            return msg
    
    def wait_for_operation(self):
        element, n = self.element, self.BusyRetries
        while element.is_in_operation():
            if n == 0:
                raise Exception("Wait for operation timedout")
            time.sleep(0.01)
            n = n - 1

class PoolDeviceClass(SardanaDeviceClass):
    """Base Tango Pool Device Class class"""
    
    #    Class Properties
    class_property_list = SardanaDeviceClass.class_property_list

    #    Device Properties
    device_property_list = {
        'Id'            : [DevLong64, "Internal ID", InvalidId ],
        'Force_HW_Read' : [DevBoolean, "Force a hardware read of value even "
                                       "when in operation (motion/acquisition",
                           False],
    }
    device_property_list.update(SardanaDeviceClass.device_property_list)
    
    #    Command definitions
    cmd_list = {
        'Stop' : [ [DevVoid, ""], [DevVoid, ""] ],
        'Abort': [ [DevVoid, ""], [DevVoid, ""] ]
    }
    cmd_list.update(SardanaDeviceClass.cmd_list)

    #    Attribute definitions
    attr_list = {
    }
    attr_list.update(SardanaDeviceClass.attr_list)
    
    standard_attr_list = {}


class PoolElementDevice(PoolDevice):
    """Base Tango Pool Element Device class"""
    
    def init_device(self):
        PoolDevice.init_device(self)
        
        self.instrument = None
        self.ctrl = None
        try:
            instrument_id = int(self.Instrument_id)
            if instrument_id != InvalidId:
                instrument = self.pool.get_element_by_id(instrument_id)
                self.instrument = instrument
        except ValueError:
            pass
        try:
            ctrl_id = int(self.Ctrl_id)
            if ctrl_id != InvalidId:
                ctrl = self.pool.get_element_by_id(ctrl_id)
                self.ctrl = ctrl
        except ValueError:
            pass
            
    def read_Instrument(self, attr):
        instrument = self.element.instrument
        if instrument is None:
            attr.set_value('')
        else:
            attr.set_value(instrument.full_name)
    
    def write_Instrument(self, attr):
        name = attr.get_write_value()
        instrument = None
        if name:
            instrument = self.pool.get_element(full_name=name)
            if instrument.get_type() != ElementType.Instrument:
                raise Exception("%s is not an instrument" % name)
        self.element.instrument = instrument
        db = Util.instance().get_database()
        db.put_device_property(self.get_name(), { "Instrument_id" : instrument.id })
    
    def get_dynamic_attributes(self):
        if hasattr(self, "_dynamic_attributes_cache"):
            return self._standard_attributes_cache, self._dynamic_attributes_cache
        ctrl = self.ctrl
        if ctrl is None:
            self.warning("no controller: dynamic attributes NOT created")
            return PoolDevice.get_dynamic_attributes(self)
        if not ctrl.is_online():
            self.warning("controller offline: dynamic attributes NOT created")
            return PoolDevice.get_dynamic_attributes(self)
        
        self._dynamic_attributes_cache = dyn_attrs = CaselessDict()
        self._standard_attributes_cache = std_attrs = CaselessDict()
        dev_class = self.get_device_class()
        axis_attrs = ctrl.get_axis_attributes(self.element.axis)
        
        std_attrs_lower = [ attr.lower() for attr in dev_class.standard_attr_list ]
        for attr_name, attr_info in axis_attrs.items():
            attr_name_lower = attr_name.lower()
            if attr_name_lower in std_attrs_lower:
                tg_info = dev_class.standard_attr_list[attr_name]
                std_attrs[attr_name] = attr_name, tg_info, attr_info
            else:
                data_info = DataInfo.toDataInfo(attr_name, attr_info)
                name, tg_info = to_tango_attr_info(attr_name, data_info)
                dyn_attrs[attr_name] = name, tg_info, data_info
        return std_attrs, dyn_attrs
    
    def read_DynamicAttribute(self, attr):
        name = attr.get_name()
        ctrl = self.ctrl
        if ctrl is None:
            raise Exception("Cannot read %s. Controller not build!" % name)
        v = ctrl.get_axis_attr(self.element.axis, name)
        if v is None:
            raise Exception("Cannot read %s. Controller returns %s" % (name, v))
        attr.set_value(v)
    
    def write_DynamicAttribute(self, attr):
        name = attr.get_name()
        value = attr.get_write_value()
        self.debug("writting dynamic attribute %s with value %s", name, value)
        ctrl = self.ctrl
        if ctrl is None:
            raise Exception("Cannot write %s. Controller not build!" % name)
        ctrl.set_axis_attr(self.element.axis, name, value)
    
    def read_SimulationMode(self, attr):
        attr.set_value(self.element.simulation_mode)
    
    def write_SimulationMode(self, attr):
        self.element.simulation_mode = attr.get_write_value()
    

class PoolElementDeviceClass(PoolDeviceClass):
    """Base Tango Pool Element Device Class class"""
    
    #    Class Properties
    class_property_list = PoolDeviceClass.class_property_list

    #    Device Properties
    device_property_list = {
        "Axis"          : [ DevLong64, "Axis in the controller", [ InvalidAxis ] ],
        "Ctrl_id"       : [ DevLong64, "Controller ID", [ InvalidId ] ],
        "Instrument_id" : [ DevLong64, "Controller ID", [ InvalidId ] ],
    }
    device_property_list.update(PoolDeviceClass.device_property_list)
    
    #    Attribute definitions
    attr_list = {
        'Instrument' :    [ [DevString, SCALAR, READ_WRITE],
                          { 'label'         : "Instrument",
                            'Display level' : DispLevel.EXPERT } ],
        'SimulationMode': [ [DevBoolean, SCALAR, READ_WRITE],
                          { 'label'         : "Simulation mode" } ],
    }
    attr_list.update(PoolDeviceClass.attr_list)

    def get_standard_attr_info(self, attr):
        return self.standard_attr_list[attr]
    

class PoolGroupDevice(PoolDevice):
    """Base Tango Pool Group Device class"""
    
    def read_ElementList(self, attr):
        attr.set_value(self.get_element_names())

    def get_element_names(self):
        elements = self.element.get_user_elements()
        return [ element.name for element in elements ]
    
    def elements_changed(self, evt_src, evt_type, evt_value):
        self.push_change_event("ElementList", self.get_element_names())


class PoolGroupDeviceClass(PoolDeviceClass):
    """Base Tango Pool Group Device Class class"""
    
    #    Class Properties
    class_property_list = {
    }
    
    #    Device Properties
    device_property_list = {
        "Elements" :    [ DevVarStringArray, "elements in the group", [ ] ],
    }
    device_property_list.update(PoolDeviceClass.device_property_list)
    
    #    Command definitions
    cmd_list = {
    }
    cmd_list.update(PoolDeviceClass.cmd_list)
    
    #    Attribute definitions
    attr_list = {
        'ElementList'  : [ [ DevString, SPECTRUM, READ, 4096] ],
    }
    attr_list.update(PoolDeviceClass.attr_list)
    
    def init_device(self):
        PoolDevice.init_device(self)
