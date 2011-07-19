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

__all__ = ["MeasurementGroup", "MeasurementGroupClass"]

__docformat__ = 'restructuredtext'

import time

from PyTango import Util, DevFailed
from PyTango import DevVoid, DevLong, DevLong64, DevDouble, DevBoolean, DevString
from PyTango import DispLevel, DevState, AttrQuality
from PyTango import READ, READ_WRITE, SCALAR, SPECTRUM
from PyTango.constants import DescNotSet

from taurus.core.util.log import InfoIt, DebugIt

from PoolDevice import PoolGroupDevice, PoolGroupDeviceClass
from PoolDevice import to_tango_state

from sardana.pool import AcqTriggerMode

class MeasurementGroup(PoolGroupDevice):
    
    def __init__(self, dclass, name):
        PoolGroupDevice.__init__(self, dclass, name)
        MeasurementGroup.init_device(self)

    def init(self, name):
        PoolGroupDevice.init(self, name)
    
    def get_measurement_group(self):
        return self.element
    
    def set_measurement_group(self, measurement_group):
        self.element = measurement_group
    
    measurement_group = property(get_measurement_group, set_measurement_group)
    
    @DebugIt()
    def delete_device(self):
        self.pool.delete_element(self.measurement_group.get_name())
        self.measurement_group = None
    
    @DebugIt()
    def init_device(self):
        PoolGroupDevice.init_device(self)

        detect_evts = "state", "status"
        #non_detect_evts = "master", "triggermode", "elementlist"
        non_detect_evts = "integration_time", "elementlist"
        self.set_change_events(detect_evts, non_detect_evts)
        
        self.Elements = list(self.Elements)
        for i in range(len(self.Elements)):
            try:
                self.Elements[i] = int(self.Elements[i])
            except:
                pass
        if self.measurement_group is None:
            try:
                mg = self.pool.create_measurement_group(name=self.alias,
                    full_name=self.get_name(), id=self.Id,
                    user_elements=self.Elements)
                mg.add_listener(self.on_measurement_group_changed)
                self.measurement_group = mg
            except Exception,e:
                import traceback
                traceback.print_exc()
        # force a state read to initialize the state attribute
        self.set_state(DevState.ON)
        #state = self.measurement_group.state
        
    def on_measurement_group_changed(self, event_source, event_type, event_value):
        t = time.time()
        name = event_type.name
        multi_attr = self.get_device_attr()
        attr = multi_attr.get_attr_by_name(name)
        quality = AttrQuality.ATTR_VALID
        
        recover = False
        if event_type.priority > 1:
            self.debug("priority event %s",name)
            attr.set_change_event(True, False)
            recover = True
        
        try:
            if name == "state":
                event_value = to_tango_state(event_value)
                self.set_state(event_value)
                self.push_change_event(name, event_value)
            elif name == "status":
                self.set_status(event_value)
                self.push_change_event(name, event_value)
            else:
                self.push_change_event(name, event_value, t, quality)
        finally:
            if recover:
                attr.set_change_event(True, True)
                
    def always_executed_hook(self):
        pass 
        #state = to_tango_state(self.motor_group.get_state(cache=False))
    
    def read_attr_hardware(self,data):
        pass
    
#    def read_Master(self, attr):
#        master = self.measurement_group.master
#        v = DescNotSet
#        if master is not None:
#            v = master.name
#        attr.set_value(v)
    
#    def write_Master(self, attr):
#        self.measurement_group.set_master_name(attr.get_write_value())
    
#    def read_TriggerMode(self, attr):
#        tm = self.measurement_group.trigger_mode
#        attr.set_value(AcqTriggerMode.whatis(tm))
    
#    def write_TriggerMode(self, attr):
#        v = attr.get_write_value()
#        if not AcqTriggerMode.has_key(v):
#            raise Exception("Invalid trigger mode '%s'. Possible modes are %s" % \
#                            (v, ", ".join(AcqTriggerMode.keys())))
#        self.measurement_group.trigger_mode = AcqTriggerMode.lookup[v]

    def read_Integration_Time(self, attr):
        it = self.measurement_group.integration_time
        if it is None:
            it = float('nan')
        attr.set_value(it)
    
    def write_Integration_Time(self, attr):
        self.measurement_group.set_integration_time(attr.get_write_value())

    def read_Configuration(self, attr):
        raise NotImplementedError
    
    def write_Configuration(self, attr):
        raise NotImplementedError

    def Start(self):
        self.measurement_group.start_acquisition()
    
    
class MeasurementGroupClass(PoolGroupDeviceClass):

    #    Class Properties
    class_property_list = {
    }

    #    Device Properties
    device_property_list = {
    }
    device_property_list.update(PoolGroupDeviceClass.device_property_list)

    #    Command definitions
    cmd_list = {
        'Start': [ [DevVoid, ""], [DevVoid, ""] ]
    }
    cmd_list.update(PoolGroupDeviceClass.cmd_list)

    #    Attribute definitions
    attr_list = {
#        'Master'     : [ [DevString, SCALAR, READ_WRITE],
#                         { 'Memorized'     : "true",
#                           'Display level' : DispLevel.EXPERT } ],
#        'TriggerMode': [ [DevString, SCALAR, READ_WRITE],
#                         { 'Memorized'     : "true",
#                           'Display level' : DispLevel.EXPERT } ],
        'Integration_Time': [ [DevDouble, SCALAR, READ_WRITE],
                              { 'Memorized'     : "true",
                                'Display level' : DispLevel.OPERATOR } ],
    }
    attr_list.update(PoolGroupDeviceClass.attr_list)

    def __init__(self, name):
        PoolGroupDeviceClass.__init__(self, name)
        self.set_type(name)
