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

""" """

__all__ = ["OneDExpChannel", "OneDExpChannelClass"]

__docformat__ = 'restructuredtext'

import sys
import time

from PyTango import DevFailed, DevVoid, DevString, DevState, AttrQuality, \
    Except, READ, SCALAR

from taurus.core.util.log import DebugIt

from sardana import State, DataFormat, SardanaServer
from sardana.sardanaattribute import SardanaAttribute
from sardana.pool.controller import OneDController, MaxDimSize, Type
from sardana.tango.core.util import to_tango_type_format, exception_str

from sardana.tango.pool.PoolDevice import PoolElementDevice, \
    PoolElementDeviceClass


class OneDExpChannel(PoolElementDevice):

    def __init__(self, dclass, name):
        PoolElementDevice.__init__(self, dclass, name)

    def init(self, name):
        PoolElementDevice.init(self, name)

    def get_oned(self):
        return self.element

    def set_oned(self, oned):
        self.element = oned

    oned = property(get_oned, set_oned)

    @DebugIt()
    def delete_device(self):
        PoolElementDevice.delete_device(self)
        oned = self.oned
        if oned is not None:
            oned.remove_listener(self.on_oned_changed)

    @DebugIt()
    def init_device(self):
        PoolElementDevice.init_device(self)
        oned = self.oned
        if oned is None:
            full_name = self.get_full_name()
            name = self.alias or full_name
            self.oned = oned = \
                self.pool.create_element(type="OneDExpChannel",
                    name=name, full_name=full_name, id=self.Id, axis=self.Axis,
                    ctrl_id=self.Ctrl_id)
            if self.instrument is not None:
                oned.set_instrument(self.instrument)
        oned.add_listener(self.on_oned_changed)

        ## force a state read to initialize the state attribute
        #state = ct.state
        self.set_state(DevState.ON)

    def on_oned_changed(self, event_source, event_type, event_value):
        try:
            self._on_oned_changed(event_source, event_type, event_value)
        except not DevFailed:
            msg = 'Error occurred "on_oned_changed(%s.%s): %s"'
            exc_info = sys.exc_info()
            self.error(msg, self.motor.name, event_type.name,
                       exception_str(*exc_info[:2]))
            self.debug("Details", exc_info=exc_info)

    def _on_oned_changed(self, event_source, event_type, event_value):
        # during server startup and shutdown avoid processing element
        # creation events
        if SardanaServer.server_state != State.Running:
            return

        timestamp = time.time()
        name = event_type.name.lower()

        try:
            attr = self.get_attribute_by_name(name)
        except DevFailed:
            return

        quality = AttrQuality.ATTR_VALID
        priority = event_type.priority
        value, w_value, error = None, None, None

        if name == "state":
            value = self.calculate_tango_state(event_value)
        elif name == "status":
            value = self.calculate_tango_status(event_value)
        else:
            if isinstance(event_value, SardanaAttribute):
                if event_value.error:
                    error = Except.to_dev_failed(*event_value.exc_info)
                else:
                    value = event_value.value
                timestamp = event_value.timestamp

            if name == "value":
                state = self.oned.get_state()
                if state == State.Moving:
                    quality = AttrQuality.ATTR_CHANGING
        self.set_attribute(attr, value=value, w_value=w_value,
                           timestamp=timestamp, quality=quality,
                           priority=priority, error=error, synch=False)

    def always_executed_hook(self):
        #state = to_tango_state(self.oned.get_state(cache=False))
        pass

    def read_attr_hardware(self, data):
        pass

    def get_dynamic_attributes(self):
        cache_built = hasattr(self, "_dynamic_attributes_cache")

        std_attrs, dyn_attrs = \
            PoolElementDevice.get_dynamic_attributes(self)

        if not cache_built:
            # For value attribute, listen to what the controller says for data
            # type (between long and float) and length
            value = std_attrs.get('value')
            if value is not None:
                _, data_info, attr_info = value
                ttype, _ = to_tango_type_format(attr_info.dtype)
                data_info[0][0] = ttype
                shape = attr_info.maxdimsize
                data_info[0][3] = shape[0]
        return std_attrs, dyn_attrs

    def read_Value(self, attr):
        oned = self.oned
        use_cache = oned.is_in_operation() and not self.Force_HW_Read
        value = oned.get_value(cache=use_cache, propagate=0)
        if value.error:
            Except.throw_python_exception(*value.exc_info)
        state = oned.get_state(cache=use_cache, propagate=0)
        quality = None
        if state == State.Moving:
            quality = AttrQuality.ATTR_CHANGING
        self.set_attribute(attr, value=value.value, quality=quality,
                           timestamp=value.timestamp, priority=0)

    def is_Value_allowed(self, req_type):
        if self.get_state() in [DevState.FAULT, DevState.UNKNOWN]:
            return False
        return True

    def read_DataSource(self, attr):
        data_source = self.oned.get_data_source()
        if data_source is None:
            data_source = "tango://{0}/value".format(self.get_full_name())
        attr.set_value(data_source)

    def Start(self):
        self.oned.start_acquisition()


_DFT_VALUE_INFO = OneDController.standard_axis_attributes['Value']
_DFT_VALUE_MAX_SHAPE = _DFT_VALUE_INFO[MaxDimSize]
_DFT_VALUE_TYPE, _DFT_VALUE_FORMAT = to_tango_type_format(_DFT_VALUE_INFO[Type], DataFormat.OneD)


class OneDExpChannelClass(PoolElementDeviceClass):

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
                          _DFT_VALUE_MAX_SHAPE[0] ],
                        { 'abs_change' : '1.0', } ],
    }
    standard_attr_list.update(PoolElementDeviceClass.standard_attr_list)

    def _get_class_properties(self):
        ret = PoolElementDeviceClass._get_class_properties(self)
        ret['Description'] = "1D device class"
        ret['InheritedFrom'].insert(0, 'PoolElementDevice')
        return ret
