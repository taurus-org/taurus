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
#    - 'controllers' : dict<str/int, dict> where:
#        - key: ctrl name / ctrl id
#        - value: dict<str, dict> with (at least) keys:
#            - 'units': dict<str, dict> with (at least) keys:
#                - 'id' : the unit ID inside the controller
#                - 'master' : the master channel name / master channel id
#                - 'trigger_type' : 'Gate'/'Software'
#                - 'channels' where value is a dict<str, obj> with (at least) keys:
#                    - 'id' : the channel name ( channel id )
#                    optional keys:
#                    - 'enabled' : True/False (default is True)
#                    any hints:
#                    - 'output' : True/False (default is True)
#                    - 'plottable' : True/False (default is True)
#                    - 'plot_axis' : 'x'/'y1'/'y2' (default is 'y1')
#                    - 'label' : prefered label (default is channel name)
#                    - 'scale' : <float, float> with min/max (defaults to channel
#                                range if it is defined
#                    - 'plot_color' : int representing RGB
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
# ni0ctrl.setCtrlPar(0, 'trigger_type', AcqTriggerType.Software)
# ni0ctrl.setCtrlPar(0, 'timer', 1) # channel 1 is the timer
# ni0ctrl.setCtrlPar(0, 'monitor', 4) # channel 4 is the monitor
# ni1ctrl.setCtrlPar(0, 'trigger_type', AcqTriggerType.ExternalTrigger)
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

    DFT_DESC = 'General purpose measurement group'

    def __init__(self, **kwargs):
        self._integration_time = None
        self._monitor_count = None
        self._acquisition_mode = AcqMode.Timer
        self._config = None
        self._config_dirty = True
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
    
    def get_pool_controllers(self):
        return self.get_acquisition().get_pool_controllers()
    
    def get_pool_controller_by_name(self, name):
        name = name.lower()
        for ctrl in self.get_pool_controllers():
            if ctrl.name.lower() == name:
                return ctrl
            
    # --------------------------------------------------------------------------
    # configuration
    # --------------------------------------------------------------------------
    
    def set_configuration(self, config=None, propagate=1):
        if config is None:
            config = {}
            user_elements = self.get_user_elements()
            ctrls = self.get_pool_controllers()
            
            config['timer'] = g_timer = user_elements[0]
            config['monitor'] = g_monitor = user_elements[0]
            config['controllers'] = controllers = {}
            
            # by default set 1 unit per controller
            for ctrl, elements in ctrls.items():
                controllers[ctrl] = ctrl_data = {}
                ctrl_data['units'] = units = {}
                units['0'] = unit_data = {}
                unit_data['id'] = 0
                if g_timer in elements:
                    unit_data['timer'] = g_timer
                else:
                    unit_data['timer'] = elements[0]
                if g_monitor in elements:
                    unit_data['monitor'] = g_monitor
                else:
                    unit_data['monitor'] = elements[0]
                unit_data['trigger_type'] = AcqTriggerType.Software
                unit_data['channels'] = channels = {}
                for element in elements:
                    channels[element] = channel_data = {}
                    channel_data['index'] = user_elements.index(element)
                    channel_data['enabled'] = True
                    channel_data['label'] = element.name
                    channel_data['output'] = True
                    channel_data['plottable'] = True
                    channel_data['plot_axis'] = 'y1'
            config['label'] = self.name
            config['description'] = self.DFT_DESC
        # checks
        g_timer, g_monitor = config['timer'], config['monitor']
        
        # attention: following line only prepared for 1 unit per controller
        timer_ctrl_data = config['controllers'][g_timer.controller]['units']['0']
        if timer_ctrl_data['timer'] != g_timer:
            self.warning('unit timer and global timer mismatch. Using global timer')
            timer_ctrl_data['timer'] = g_timer
        
        # attention: following line only prepared for 1 unit per controller
        monitor_ctrl_data = config['controllers'][g_monitor.controller]['units']['0']
        if monitor_ctrl_data['monitor'] != g_monitor:
            self.warning('unit monitor and global monitor mismatch. Using global monitor')
            monitor_ctrl_data['monitor'] != g_monitor
        
        self._config = config
        self._config_dirty = True
        if not propagate:
            return
        self.fire_event(EventType("configuration", priority=propagate), config)
        
    def get_configuration(self):
        return self._config
    
    def get_user_configuration(self):
        cfg = self.get_configuration()
        config = {}
        
        config['timer'] = cfg['timer'].name
        config['monitor'] = cfg['monitor'].name
        config['controllers'] = controllers = {}
        
        for c, c_data in cfg['controllers'].items():
            controllers[c.name] = ctrl_data = {}
            ctrl_data['units'] = units = {}
            for u_id, u_data in c_data['units'].items():
                units[u_id] = unit_data = {}
                unit_data['id'] = u_data['id']
                unit_data['timer'] = u_data['timer'].name
                unit_data['monitor'] = u_data['monitor'].name
                unit_data['trigger_type'] = u_data['trigger_type']
                unit_data['channels'] = channels = {}
                for ch, ch_data in u_data['channels'].items():
                    channels[ch.name] = channel_data = dict(ch_data)

        config['label'] = cfg['label']
        config['description'] = cfg['description']
        return config
    
    def set_configuration_from_user(self, cfg, propagate=1):
        config = {}
        user_elements = self.get_user_elements()
        ctrls = self.get_pool_controllers()
        
        timer_name = cfg.get('timer', user_elements[0].name)
        monitor_name = cfg.get('monitor', user_elements[0].name)
        config['timer'] = self.get_element_by_name(timer_name)
        config['monitor'] = self.get_element_by_name(monitor_name)
        config['controllers'] = controllers = {}
        
        for c_name, c_data in cfg['controllers'].items():
            ctrl = self.get_pool_controller_by_name(c_name)
            controllers[ctrl] = ctrl_data = {}
            ctrl_data['units'] = units = {}
            for u_id, u_data in c_data['units'].items():
                units[u_id] = unit_data = dict(u_data)
                unit_data['id'] = u_data.get('id', u_id)
                unit_data['timer'] = self.get_element_by_name(u_data['timer'])
                unit_data['monitor'] = self.get_element_by_name(u_data['monitor'])
                unit_data['trigger_type'] = u_data['trigger_type']
                unit_data['channels'] = channels = {}
                for ch_name, ch_data in u_data['channels'].items():
                    channel = self.get_element_by_name(ch_name)
                    channels[channel] = channel_data = dict(ch_data)
        
        config['label'] = cfg.get('label', self.name)
        config['description'] = cfg.get('description', self.DFT_DESC)
        self.set_configuration(config, propagate=propagate)
    
    def load_configuration(self, force=False):
        """Loads the current configuration to all involved controllers"""
        cfg = self.get_configuration()
        g_timer, g_monitor = cfg['timer'], cfg['monitor']
        for unit, unit_data in cfg['units'].items():
            ctrl = unit
            if ctrl.operator == self and not force and not self._config_dirty:
                continue
            ctrl.operator = self
            
            #if ctrl == g_timer.controller:
            #    ctrl.set_ctrl_par('timer', g_timer.axis)
            #if ctrl == g_monitor.controller:
            #    ctrl.set_ctrl_par('monitor', g_monitor.axis)
            ctrl.set_ctrl_par('timer', unit_data['timer'].axis)
            ctrl.set_ctrl_par('monitor', unit_data['monitor'].axis)
            ctrl.set_ctrl_par('trigger_type', unit_data['trigger_type'])

            self._config_dirty = False
            
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

    # --------------------------------------------------------------------------
    # integration time
    # --------------------------------------------------------------------------
    
    def get_monitor_count(self):
        return self._monitor_count
    
    def set_monitor_count(self, monitor_count, propagate=1):
        self._monitor_count = monitor_count
        if not propagate:
            return
        self.fire_event(EventType("monitor_count", priority=propagate), monitor_count)
        
    
    monitor_count = property(get_monitor_count, set_monitor_count,
                             doc="the current monitor count")
    
    # --------------------------------------------------------------------------
    # acquisition mode
    # --------------------------------------------------------------------------
    
    def get_acquisition_mode(self):
        return self._acquisition_mode
    
    def set_acquisition_mode(self, acquisition_mode, propagate=1):
        self._acquisition_mode = acquisition_mode
        if not propagate:
            return
        self.fire_event(EventType("acquisition_mode", priority=propagate), acquisition_mode)
    
    acquisition_mode = property(get_acquisition_mode, set_acquisition_mode,
                                doc="the current acquisition mode")
    
    # --------------------------------------------------------------------------
    # acquisition
    # --------------------------------------------------------------------------
    
    def start_acquisition(self, value=None):
        self._aborted = False
        if not self._simulation_mode:
            # load configuration into controller(s) if necessary
            self.load_configuration()
            # start acquisition
            kwargs = dict(head=self, config=self._config)
            if self.acquisition_mode == AcqMode.Timer:
                kwargs["integ_time"] = self._integration_time
            elif self.acquisition_mode == AcqMode.Monitor:
                kwargs["monitor_count"] = self._monitor_count
            self.acquisition.run(**kwargs)
    
    def set_acquisition(self, acq_cache):
        self.set_action_cache(acq_cache)
    
    def get_acquisition(self):
        return self.get_action_cache()
    
    acquisition = property(get_acquisition, doc="acquisition object")