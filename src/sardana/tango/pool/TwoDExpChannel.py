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

__all__ = ["TwoDExpChannel", "TwoDExpChannelClass"]

__docformat__ = 'restructuredtext'

import time

from PyTango import DevVoid, DevString, DevState, AttrQuality, \
    Except, READ, SCALAR, IMAGE

from taurus.core.util.log import DebugIt

from sardana import State, DataFormat, SardanaServer
from sardana.sardanaattribute import SardanaAttribute
from sardana.pool.controller import TwoDController, MaxDimSize, Type
from sardana.tango.core.util import to_tango_type_format

from PoolDevice import PoolElementDevice, PoolElementDeviceClass


class TwoDExpChannel(PoolElementDevice):

    def __init__(self, dclass, name):
        PoolElementDevice.__init__(self, dclass, name)
        TwoDExpChannel.init_device(self)

    def init(self, name):
        PoolElementDevice.init(self, name)

    def get_twod(self):
        return self.element

    def set_twod(self, twod):
        self.element = twod

    twod = property(get_twod, set_twod)

    @DebugIt()
    def delete_device(self):
        PoolElementDevice.delete_device(self)
        twod = self.twod
        if twod is not None:
            twod.remove_listener(self.on_twod_changed)
            
    @DebugIt()
    def init_device(self):
        PoolElementDevice.init_device(self)
        twod = self.twod
        if twod is None:
            full_name = self.get_full_name()
            name = self.alias or full_name
            self.twod = twod = \
                self.pool.create_element(type="TwoDExpChannel",
                    name=name, full_name=full_name, id=self.Id, axis=self.Axis,
                    ctrl_id=self.Ctrl_id)
            if self.instrument is not None:
                ct.set_instrument(self.instrument)
        twod.add_listener(self.on_twod_changed)

        ## force a state read to initialize the state attribute
        #state = ct.state
        self.set_state(DevState.ON)

    def on_twod_changed(self, event_source, event_type, event_value):
        # during server startup and shutdown avoid processing element
        # creation events
        if SardanaServer.server_state != State.Running:
            return

        timestamp = time.time()
        name = event_type.name
        quality = AttrQuality.ATTR_VALID
        priority = event_type.priority
        error = None
        attr = self.get_device_attr().get_attr_by_name(name)

        if name == "state":
            event_value = self.calculate_tango_state(event_value)
        elif name == "status":
            event_value = self.calculate_tango_status(event_value)
        else:
            if isinstance(event_value, SardanaAttribute):
                if event_value.error:
                    error = Except.to_dev_failed(*event_value.exc_info)
                timestamp = event_value.timestamp
                event_value = event_value.value

            if name == "value":
                state = self.twod.get_state()
                if state == State.Moving:
                    quality = AttrQuality.ATTR_CHANGING
        self.set_attribute(attr, value=event_value, timestamp=timestamp,
                           quality=quality, priority=priority, error=error,
                           synch=False)

    def always_executed_hook(self):
        #state = to_tango_state(self.twod.get_state(cache=False))
        pass

    def read_attr_hardware(self,data):
        pass

    def get_dynamic_attributes(self):
        std_attrs, dyn_attrs = \
            PoolElementDevice.get_dynamic_attributes(self)

        # For value attribute, listen to what the controller says for data
        # type (between long and float) and length
        value = std_attrs.get('value')
        if value is not None:
            attr_name, data_info, attr_info = value
            ttype, tformat = to_tango_type_format(attr_info.get(Type))
            data_info[0][0] = ttype
            shape = attr_info.get(MaxDimSize)
            data_info[0][3] = shape[0]
            data_info[0][4] = shape[1]
        return std_attrs, dyn_attrs
        
    def read_Value(self, attr):
        twod = self.twod
        #use_cache = twod.is_action_running() and not self.Force_HW_Read
        use_cache = self.get_state() == DevState.MOVING and not self.Force_HW_Read
        value = twod.get_value(cache=use_cache)
        quality = None
        if self.get_state() == DevState.MOVING:
            quality = AttrQuality.ATTR_CHANGING
        self.set_attribute(attr, value=value, quality=quality, priority=0)

    def is_Value_allowed(self, req_type):
        if self.get_state() in [DevState.FAULT, DevState.UNKNOWN]:
            return False
        return True

    def read_DataSource(self, attr):
        data_source = self.oned.get_data_source()
        attr.set_value(data_source)
        
    def Start(self):
        self.twod.start_acquisition()


_DFT_VALUE_INFO = TwoDController.standard_axis_attributes['Value']
_DFT_VALUE_MAX_SHAPE = _DFT_VALUE_INFO[MaxDimSize]
_DFT_VALUE_TYPE, _DFT_VALUE_FORMAT = to_tango_type_format(_DFT_VALUE_INFO[Type], DataFormat.TwoD)

class TwoDExpChannelClass(PoolElementDeviceClass):

    #    Class Properties
    class_property_list = {
    }

    #    Device Properties
    device_property_list = {
    }
    device_property_list.update(PoolElementDeviceClass.device_property_list)

    #    Command definitions
    cmd_list = {
        'Start' :   [ [DevVoid, ""], [DevVoid, ""] ],
    }
    cmd_list.update(PoolElementDeviceClass.cmd_list)

    #    Attribute definitions
    attr_list = {
        'DataSource' : [ [ DevString, SCALAR, READ ] ],
    }
    attr_list.update(PoolElementDeviceClass.attr_list)

    standard_attr_list = {
        'Value'     : [ [ _DFT_VALUE_TYPE, _DFT_VALUE_FORMAT, READ, 
                          _DFT_VALUE_MAX_SHAPE[0], _DFT_VALUE_MAX_SHAPE[1] ],
                        { 'abs_change' : '1.0', } ],
    }
    standard_attr_list.update(PoolElementDeviceClass.standard_attr_list)
    
    def _get_class_properties(self):
        ret = PoolElementDeviceClass._get_class_properties(self)
        ret['Description'] = "2D device class"
        ret['InheritedFrom'].insert(0, 'PoolElementDevice')
        return ret
