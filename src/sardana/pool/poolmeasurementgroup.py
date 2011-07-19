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

"""This module is part of the Python Pool libray. It defines the base classes
for"""

__all__ = [ "PoolMeasurementGroup" ]

__docformat__ = 'restructuredtext'

import math

from poolbase import *
from pooldefs import *
from poolgroupelement import *
from poolacquisition import *
from sardana import State

# dict <str, obj> with (at least) keys:
#    - 'timer' : the timer channel name / timer channel id
#    - 'monitor' : the monitor channel name / monitor channel id
#    - 'units' : dict<str/int, dict> where:
#        - key: the unit name / ctrl name / ctrl id
#        - value: dict<str, dict> with (at least) keys:
#            - 'master' : the master channel name / master channel id
#            - 'trigger_type' : 'Gate'/'Software'
#            - 'channels' where value is a dict<str, obj> with (at least) keys:
#                - 'id' : the channel name ( channel id )
#                optional keys:
#                - 'enabled' : True/False (default is True)
#                any hints:
#                - 'output' : True/False (default is True)
#                - 'plottable' : 'False'/'x'/'y1'/'y2' (default is 'y1')
#                - 'label' : prefered label (default is channel name)
#                - 'scale' : <float, float> with min/max (defaults to channel
#                            range if it is defined
#                - 'color' : int representing RGB
#    optional keys:
#    - 'label' : measurement group label (defaults to measurement group name)
#    - 'description' : measurement group description

# <MeasurementGroupConfiguration>
#  <timer>UxTimer</timer>
#  <monitor>CT1</monitor>
# </MeasurementGroupConfiguration>

# Example: 2 NI cards, where channel 1 of card 1 is wired to channel 1 of card 2
# at configuration time we should set:
# ctrl.setPar( <unit>, <parameter name>, <parameter value> )
# ni0ctrl.setCtrlPar(0, 'trigger_type', AcqTriggerMode.Software)
# ni0ctrl.setCtrlPar(0, 'timer', 1) # channel 1 is the timer
# ni0ctrl.setCtrlPar(0, 'monitor', 4) # channel 4 is the monitor
# ni1ctrl.setCtrlPar(0, 'trigger_type', AcqTriggerMode.ExternalTrigger)
# ni1ctrl.setCtrlPar(0, 'master', 0)

# when we count for 1.5 seconds:
# ni1ctrl.Load(1.5)
# ni0ctrl.Load(1.5)
# ni1ctrl.Start()
# ni0ctrl.Start()

"""

"""

_S_DICT = { State.Fault: 0, State.Alarm : 0, State.On : 0, State.Moving : 0, State.Running : 0 }

class PoolMeasurementGroup(PoolGroupElement):

    def __init__(self, **kwargs):
        self._integration_time = None
        self._monitor_count = None
        PoolGroupElement.__init__(self, **kwargs)
        self.set_acquisition(PoolCTAcquisition("%s.CTAcquisition" % kwargs.get('name')))
        self.set_configuration(kwargs.get('config'))
    
    def get_type(self):
        return ElementType.MeasurementGroup
    
    def on_element_changed(self, evt_src, evt_type, evt_value):
        name = evt_type.name
        if name == 'state':
            fault, alarm, on, moving = 0, 0, 0, 0
            status = []
            for e in self.get_user_elements():
                s = e.get_state()
                if s == State.Moving: moving += 1
                elif s == State.On: on += 1
                elif s == State.Fault:
                    status.append(e.name + " is in FAULT")
                    fault += 1
                elif s == State.Alarm:
                    status.append(e.name + " is in ALARM")
                    alarm += 1
            state = State.On
            if fault:
                state = State.Fault
            elif alarm:
                state = State.Alarm
            elif moving:
                state = State.Moving
            self.set_state(state, propagate=2)
            if status:
                self.set_status("\n".join(status))
    
    # --------------------------------------------------------------------------
    # configuration
    # --------------------------------------------------------------------------
    
    def set_configuration(self, config=None, propagate=1):
        if config is None:
            config = {}
            config['timer'] = self.get_user_elements()[0]
            config['monitor'] = self.get_user_elements()[0]
            config['units'] = units = {}
            ctrls = self.get_acquisition().get_pool_controllers()
            for ctrl, elements in ctrls.items():
                units[ctrl] = unit_data = {}
                unit_data['master'] = elements[0]
                unit_data['trigger_type'] = AcqTriggerType.Software
                unit_data['channels'] = channels = {}
                for element in elements:
                    channels[element] = channel_data = {}
                    channel_data['enabled'] = True
                    channel_data['label'] = element.name
                    channel_data['output'] = True
                    channel_data['plottable'] = 'y1'
            config['label'] = self.name
            config['description'] = 'General purpose measurement group'
        self._config = config
        if not propagate:
            return
        self.fire_event(EventType("configuration", priority=propagate), config)
        
    def get_configuration(self):
        return self._config
    
    def get_user_configuration(self):
        c = self.get_configuration()
        config = {}
        config['timer'] = c['timer'].name
        config['monitor'] = c['monitor'].name
        config['units'] = units = {}
        
        for u, ud in c['units'].items():
            units[u.name] = unit_data = {}
            unit_data['master'] = ud['master']
            unit_data['trigger_type'] = ud['trigger_type']
            unit_data['channels'] = channels = {}
            for c, cd in ud['channels'].items():
                channels[c.name] = channel_data = dict(cd)
        
        config['label'] = c['label']
        config['description'] = c['description']
        return config
    
    def load_configuration(self, force=False):
        """Loads the current configuration to all involved controllers"""
        cfg = self.get_configuration()
        timer, monitor = cfg['timer'], cfg['monitor']
        for unit, unit_data in cfg['units'].items():
            ctrl = unit
            if ctrl.operator == self and not force:
                continue
            ctrl.operator = self
            if ctrl == timer.controller:
                ctrl.set_ctrl_par('timer', timer.axis)
            if ctrl == monitor.controller:
                ctrl.set_ctrl_par('monitor', monitor.axis)
            ctrl.set_ctrl_par('master', unit_data['master'].axis)
            ctrl.set_ctrl_par('trigger_type', unit_data['trigger_type'])
    
    def get_timer(self):
        return self.get_configuration()['timer']
    
    timer = property(get_timer)

    # --------------------------------------------------------------------------
    # integration time
    # --------------------------------------------------------------------------
    
    def get_integration_time(self):
        return self._integration_time
    
    def set_integration_time(self, integration_time, propagate=1):
        self._integration_time = integration_time
        if not propagate:
            return
        self.fire_event(EventType("integration_time", priority=propagate), integration_time)
    
    integration_time = property(get_integration_time, set_integration_time,
                                doc="the current integration time")
    
#    # --------------------------------------------------------------------------
#    # master
#    # --------------------------------------------------------------------------
    
#    def get_master(self):
#        return self._master
    
#    def set_master(self, master, propagate=1):
#        self._master = self.get_element_by_id(master.id)
#        if not propagate:
#            return
#        self.fire_event(EventType("master", priority=propagate), master)
    
#    def set_master_name(self, name, propagate=1):
#        self.set_master( self.get_element_by_name(name), propagate=propagate )
    
#    master = property(get_master, set_master, doc="master channel")

#    # --------------------------------------------------------------------------
#    # trigger mode
#    # --------------------------------------------------------------------------
    
#    def get_trigger_mode(self):
#        return self._trigger_mode
    
#    def set_trigger_mode(self, trigger_mode, propagate=1):
#        self._trigger_mode = trigger_mode
#        if not propagate:
#            return
#        self.fire_event(EventType("trigger_mode", priority=propagate), trigger_mode)
    
#    trigger_mode = property(get_trigger_mode, set_trigger_mode,
#                            doc="active trigger mode")
    
    # --------------------------------------------------------------------------
    # acquisition
    # --------------------------------------------------------------------------
    def start_acquisition(self, value=None):
        self._aborted = False
        if not self._simulation_mode:
            # load configuration into controller(s) if necessary
            self.load_configuration()
            # start acquisition
            self.acquisition.run(head=self, integ_time=self._integration_time,
                                 config=self._config)
    
    def set_acquisition(self, acq_cache):
        self.set_action_cache(acq_cache)
    
    def get_acquisition(self):
        return self.get_action_cache()
    
    acquisition = property(get_acquisition, doc="acquisition object")