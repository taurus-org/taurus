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

from PyTango import Util, DevFailed, \
    DevVoid, DevLong, DevLong64, DevDouble, DevBoolean, \
    DevString, DevEncoded, \
    DispLevel, DevState, AttrQuality, \
    READ, READ_WRITE, SCALAR, SPECTRUM
from PyTango.constants import DescNotSet

from taurus.core.util import CodecFactory
from taurus.core.util.log import InfoIt, DebugIt

from sardana import State, SardanaServer
from sardana.pool import AcqMode
from sardana.tango.core.util import to_tango_state
from PoolDevice import PoolGroupDevice, PoolGroupDeviceClass


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
        PoolGroupDevice.delete_device(self)
    
    @DebugIt()
    def init_device(self):
        PoolGroupDevice.init_device(self)

        detect_evts = () # state and status are already set by the super class
        non_detect_evts = "configuration", "integrationtime", "monitorcount", \
                          "acquisitionmode", "elementlist"
        self.set_change_events(detect_evts, non_detect_evts)
        
        self.Elements = list(self.Elements)
        for i in range(len(self.Elements)):
            try:
                self.Elements[i] = int(self.Elements[i])
            except:
                pass
        if self.measurement_group is None:
            full_name = self.get_full_name()
            name = self.alias or full_name
            mg = self.pool.create_measurement_group(name=name,
                full_name=full_name, id=self.Id, user_elements=self.Elements)
            mg.add_listener(self.on_measurement_group_changed)
            self.measurement_group = mg
        # force a state read to initialize the state attribute
        self.set_state(DevState.ON)
        #state = self.measurement_group.state
        
    def on_measurement_group_changed(self, event_source, event_type, event_value):
        
        # during server startup and shutdown avoid processing element
        # creation events
        if SardanaServer.server_state != State.Running:
            return

        t = time.time()
        name = event_type.name
        name = name.replace('_','')
        multi_attr = self.get_device_attr()
        attr = multi_attr.get_attr_by_name(name)
        quality = AttrQuality.ATTR_VALID
        
        recover = False
        if event_type.priority > 1 and attr.is_check_change_criteria():
            attr.set_change_event(True, False)
            recover = True
        
        my_name = self.alias.lower()
        try:
            if name == "state":
                state = self.calculate_tango_state(event_value)
                attr.set_value(state)
                attr.fire_change_event()
                #self.push_change_event(name, state)
            elif name == "status":
                status = self.calculate_tango_status(event_value)
                attr.set_value(status)
                attr.fire_change_event()
                #self.push_change_event(name, status)
            elif name == "acquisitionmode":
                event_value = AcqMode.whatis(event_value)
                attr.set_value_date_quality(event_value, t, quality)
                attr.fire_change_event()
                #self.push_change_event(name, event_value, t, quality)
            elif name == "configuration":
                cfg = self.measurement_group.get_user_configuration()
                codec = CodecFactory().getCodec('json')
                _, event_value = codec.encode(('', cfg))
                attr.set_value(event_value)
                attr.fire_change_event()
                #self.push_change_event(name, event_value)
            else:
                attr.set_value(event_value)
                attr.fire_change_event()
                #self.push_change_event(name, event_value, t, quality)
        finally:
            if recover:
                attr.set_change_event(True, True)
                
    def always_executed_hook(self):
        pass 
        #state = to_tango_state(self.motor_group.get_state(cache=False))
    
    def read_attr_hardware(self,data):
        pass

    def read_IntegrationTime(self, attr):
        it = self.measurement_group.integration_time
        if it is None:
            it = float('nan')
        attr.set_value(it)
    
    def write_IntegrationTime(self, attr):
        self.measurement_group.integration_time = attr.get_write_value()

    def read_MonitorCount(self, attr):
        it = self.measurement_group.monitor_count
        if it is None:
            it = 0
        attr.set_value(it)
    
    def write_MonitorCount(self, attr):
        self.measurement_group.monitor_count = attr.get_write_value()
        
    def read_AcquisitionMode(self, attr):
        acq_mode = self.measurement_group.acquisition_mode
        acq_mode_str = AcqMode.whatis(acq_mode)
        attr.set_value(acq_mode_str)
    
    def write_AcquisitionMode(self, attr):
        acq_mode_str = attr.get_write_value()
        try:
            acq_mode = AcqMode.lookup[acq_mode_str]
        except KeyError:
            raise Exception("Invalid acquisition mode. Must be one of " + \
                            ", ".join(AcqMode.keys()))
        self.measurement_group.acquisition_mode = acq_mode
        
    def read_Configuration(self, attr):
        cfg = self.measurement_group.get_user_configuration()
        codec = CodecFactory().getCodec('json')
        data = codec.encode(('', cfg))
        attr.set_value(data[1])
    
    def write_Configuration(self, attr):
        data = attr.get_write_value()
        cfg = CodecFactory().decode(('json', data), ensure_ascii=True)
        self.measurement_group.set_configuration_from_user(cfg)

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
        'IntegrationTime': [ [DevDouble, SCALAR, READ_WRITE],
                              { 'Memorized'     : "true",
                                'Display level' : DispLevel.OPERATOR } ],
        'MonitorCount': [ [DevLong, SCALAR, READ_WRITE],
                              { 'Memorized'     : "true",
                                'Display level' : DispLevel.OPERATOR } ],
        'AcquisitionMode': [ [DevString, SCALAR, READ_WRITE],
                              { 'Memorized'     : "true",
                                'Display level' : DispLevel.OPERATOR } ],
        'Configuration': [ [DevString, SCALAR, READ_WRITE],
                              { 'Memorized'     : "true",
                                'Display level' : DispLevel.EXPERT } ],
    }
    attr_list.update(PoolGroupDeviceClass.attr_list)

