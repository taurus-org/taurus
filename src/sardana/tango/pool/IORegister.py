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

__all__ = ["IORegister", "IORegisterClass"]

__docformat__ = 'restructuredtext'

import sys
import time

from PyTango import DevFailed, Except
from PyTango import DevVoid, DevLong
from PyTango import DevState, AttrQuality
from PyTango import READ_WRITE, SCALAR

from taurus.core.util.log import DebugIt

from sardana import State, SardanaServer
from sardana.sardanaattribute import SardanaAttribute
from sardana.pool.poolexception import PoolException
from sardana.sardanautils import str_to_value

from sardana.tango.core.util import exception_str, throw_sardana_exception
from sardana.tango.pool.PoolDevice import PoolElementDevice, \
    PoolElementDeviceClass


class IORegister(PoolElementDevice):

    def __init__(self, dclass, name):
        self.in_write_value = False
        PoolElementDevice.__init__(self, dclass, name)

    def init(self, name):
        PoolElementDevice.init(self, name)

    def get_ior(self):
        return self.element

    def set_ior(self, ior):
        self.element = ior

    ior = property(get_ior, set_ior)

    def set_write_value_to_db(self):
        value_attr = self.ior.get_value_attribute()
        if value_attr.has_write_value():
            data = dict(Value=dict(__value=value_attr.w_value, __value_ts=value_attr.w_timestamp))
            db = self.get_database()
            db.put_device_attribute_property(self.get_name(), data)

    def get_write_value_from_db(self):
        name = 'Value'
        db = self.get_database()
        val_props = db.get_device_attribute_property(self.get_name(), name)[name]
        w_val = val_props["__value"][0]

        _, _, attr_info = self.get_dynamic_attributes()[0][name]
        w_val = str_to_value(w_val, attr_info.dtype, attr_info.dformat)

        w_val, w_ts = int(val_props["__value"][0]), None
        if "__value_ts" in val_props:
            w_ts = float(val_props["__value_ts"][0])
        return w_val, w_ts

    @DebugIt()
    def delete_device(self):
        PoolElementDevice.delete_device(self)
        ior = self.ior
        if ior is not None:
            ior.remove_listener(self.on_ior_changed)

    @DebugIt()
    def init_device(self):
        PoolElementDevice.init_device(self)

        ior = self.ior
        if ior is None:
            full_name = self.get_full_name()
            name = self.alias or full_name
            self.ior = ior = \
                self.pool.create_element(type="IORegister", name=name,
                    full_name=full_name, id=self.Id, axis=self.Axis,
                    ctrl_id=self.Ctrl_id)
            if self.instrument is not None:
                ior.set_instrument(self.instrument)
        ior.add_listener(self.on_ior_changed)

        ## force a state read to initialize the state attribute
        #state = ior.get_state(cache=False)
        self.set_state(DevState.ON)

    def on_ior_changed(self, event_source, event_type, event_value):
        try:
            self._on_ior_changed(event_source, event_type, event_value)
        except not DevFailed:
            msg = 'Error occurred "on_ior_changed(%s.%s): %s"'
            exc_info = sys.exc_info()
            self.error(msg, self.ior.name, event_type.name,
                       exception_str(*exc_info[:2]))
            self.debug("Details", exc_info=exc_info)

    def _on_ior_changed(self, event_source, event_type, event_value):
        # during server startup and shutdown avoid processing element
        # creation events
        if SardanaServer.server_state != State.Running:
            return

        timestamp = time.time()
        name = event_type.name.lower()

        if name == "w_value" and not self.in_write_value:
            self.debug("Storing value set point: %s", self.ior.value.w_value)
            self.set_write_value_to_db()
            return

        multi_attr = self.get_device_attr()
        try:
            attr = multi_attr.get_attr_by_name(name)
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
            state = self.ior.get_state(propagate=0)

            if name == "value":
                w_value = event_source.get_value_attribute().w_value
                if state == State.Moving:
                    quality = AttrQuality.ATTR_CHANGING
        self.set_attribute(attr, value=value, w_value=w_value,
                           timestamp=timestamp, quality=quality,
                           priority=priority, error=error, synch=False)

    def always_executed_hook(self):
        #state = to_tango_state(self.ior.get_state(cache=False))
        pass

    def read_attr_hardware(self, data):
        pass

    def initialize_dynamic_attributes(self):
        attrs = PoolElementDevice.initialize_dynamic_attributes(self)

        detect_evts = "value",
        non_detect_evts = ()

        for attr_name in detect_evts:
            if attrs.has_key(attr_name):
                self.set_change_event(attr_name, True, True)
        for attr_name in non_detect_evts:
            if attrs.has_key(attr_name):
                self.set_change_event(attr_name, True, False)
        return

    def read_Value(self, attr):
        value = self.ior.get_value(cache=False)
        if value.error:
            Except.throw_python_exception(*value.exc_info)
        self.set_attribute(attr, value=value.value, w_value=value.w_value,
                           priority=0, timestamp=value.timestamp)

    def write_Value(self, attr):
        self.in_write_value = True
        value = attr.get_write_value()
        try:
            self.ior.set_value(value)
            # manually store write value in the database
            self.set_write_value_to_db()
        except PoolException as pe:
            throw_sardana_exception(pe)
        finally:
            self.in_write_value = False

    def is_Value_allowed(self, req_type):
        if self.get_state() in [DevState.FAULT, DevState.UNKNOWN]:
            return False
        return True

    def Start(self):
        self.ior.start_acquisition()


class IORegisterClass(PoolElementDeviceClass):

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
    attr_list = {}
    attr_list.update(PoolElementDeviceClass.attr_list)

    standard_attr_list = {
        'Value'     : [ [ DevLong, SCALAR, READ_WRITE ],
                        { 'Memorized'     : "true_without_hard_applied", }, ],
    }
    standard_attr_list.update(PoolElementDeviceClass.standard_attr_list)

    def _get_class_properties(self):
        ret = PoolElementDeviceClass._get_class_properties(self)
        ret['Description'] = "IORegister device class"
        ret['InheritedFrom'].insert(0, 'PoolElementDevice')
        return ret
