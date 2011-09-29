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

"""This module is part of the Python Pool libray. It defines the class for an
acquisition"""

__all__ = [ "PoolCTAcquisition" ]

__docformat__ = 'restructuredtext'

import time
import weakref

import taurus.core.util

from sardana import State
from poolaction import *

class PoolAcquisition(PoolAction):
    
    def __init__(self, name="Acquisition"):
        PoolAction.__init__(self, name)
        ctname = name + ".CTAcquisition"
        zerodname = name + ".0DAcquisition"
        self._ct_acq = PoolCTAcquisition(name=ctname)
        self._0d_acq = Pool0DAcquisition(name=zerodname)
    
    def start_action(self, *args, **kwargs):
        pass
    
class Channel(PoolActionItem):
    
    def __init__(self, acquirable, info=None):
        PoolActionItem.__init__(self, acquirable)
        if info:
            self.__dict__.update(info)
    
    def __getattr__(self, name):
        return getattr(self.element, name)
        

class PoolCTAcquisition(PoolAction):
    
    def __init__(self, pool, name="CTAcquisition"):
        self._channels = None
        PoolAction.__init__(self, pool, name)
    
    def start_action(self, *args, **kwargs):
        """Prepares everything for acquisition and starts it.
        
           :param: config"""
        integ_time = kwargs.get("integ_time")
        mon_count = kwargs.get("monitor_count")
        if integ_time is None and mon_count is None:
            raise Exception("must give integration time or monitor counts")
        if integ_time is not None and mon_count is not None:
            raise Exception("must give either integration time or monitor counts (not both)")
        
        items = kwargs.get("items")
        if items is None:
            items = self.get_elements()
        cfg = kwargs['config']
        
        # determine which is the controller which olds the master channel
        master_key, master_value = 'timer', integ_time

        if mon_count is not None:
            master_key = 'monitor'
            master_value = - mon_count
        
        master = cfg[master_key]
        master_ctrl = master.controller

        pool_ctrls_dict = cfg['controllers']
        pool_ctrls = pool_ctrls_dict.keys()
        
        # make sure the controller which has the master channel is the last to
        # be called
        pool_ctrls.remove(master_ctrl)
        pool_ctrls.append(master_ctrl)
        
        # Determine which channels are active
        self._channels = channels = {}
        for pool_ctrl in pool_ctrls:
            ctrl = pool_ctrl.ctrl
            pool_ctrl_data = pool_ctrls_dict[pool_ctrl]
            main_unit_data = pool_ctrl_data['units']['0']
            elements = main_unit_data['channels']
            
            for element, element_info in elements.items():
                axis = element.axis
                channel = Channel(element, info=element_info)
                channels[element] = channel

        for channel in channels:
            channel.prepare_to_acquire(self)

        # PreLoadAll, PreLoadOne, LoadOne and LoadAll
        for pool_ctrl in pool_ctrls:
            ctrl = pool_ctrl.ctrl
            pool_ctrl_data = pool_ctrls_dict[pool_ctrl]
            main_unit_data = pool_ctrl_data['units']['0']
            ctrl.PreLoadAll()
            master = main_unit_data[master_key]
            axis = master.axis
            res = ctrl.PreLoadOne(axis, master_value)
            if not res:
                raise Exception("%s.PreLoadOne(%d) returns False" % (pool_ctrl.name, axis,))
            ctrl.LoadOne(axis, master_value)
            ctrl.LoadAll()

        # PreStartAll on all controllers
        for pool_ctrl in pool_ctrls:
            pool_ctrl.ctrl.PreStartAll()
        
        # PreStartOne & StartOne on all elements
        for pool_ctrl in pool_ctrls:
            ctrl = pool_ctrl.ctrl
            pool_ctrl_data = pool_ctrls_dict[pool_ctrl]
            main_unit_data = pool_ctrl_data['units']['0']
            elements = main_unit_data['channels']
            for element in elements:
                axis = element.axis
                channel = channels[element]
                if channel.enabled:
                    ret = ctrl.PreStartOne(axis, master_value)
                    if not ret:
                        raise Exception("%s.PreStartOne(%d) returns False" \
                                        % (ctrl.name, axis))
                    ctrl.StartOne(axis)
        
        # set the state of all elements to  and inform their listeners
        for channel in channels:
            channel.set_state(State.Moving, propagate=2)
        
        # StartAll on all controllers
        for pool_ctrl in pool_ctrls:
            pool_ctrl.ctrl.StartAll()
        
    def in_acquisition(self, states):
        """Determines if we are in acquisition or if the acquisition has ended
        based on the current unit trigger modes and states returned by the
        controller(s)
        
        :param states: a map containning state information as returned by
                       read_state_info
        :type states: dict<PoolElement, State>
        :return: returns True if in acquisition or False otherwise
        :rtype: bool"""
        for state in states:
            s = states[state][0]
            if self._is_in_action(s):
                return True
    
    @taurus.core.util.DebugIt()
    def action_loop(self):
        i = 0
        
        states, values = {}, {}
        for element in self._channels:
            states[element] = None
            values[element] = None

        # read values to send a first event when starting to acquire
        self.read_value(ret=values)
        for acquirable, value in values.items():
            acquirable.put_value(value, propagate=2)
            
        while True:
            self.read_state_info(ret=states)
            
            if not self.in_acquisition(states):
                break
            
            # read value every n times
            if not i % 5:
                self.read_value(ret=values)
                for acquirable, value in values.items():
                    acquirable.put_value(value)
                
            i += 1
            time.sleep(0.01)
        
        self.read_state_info(ret=states)
        
        # first update the element state so that value calculation
        # that is done after takes the updated state into account
        for acquirable, state_info in states.items():
            acquirable.set_state_info(state_info, propagate=0)
        
        # Do NOT send events before we exit the OperationContext, otherwise
        # we may be asked to start another action before we leave the context
        # of the current action. Instead, send the events in the finish hook
        # which is executed outside the OperationContext

        def finish_hook(*args, **kwargs):
            # read values and propagate the change to all listeners
            self.read_value(ret=values)
            for acquirable, value in values.items():
                acquirable.put_value(value, propagate=2)
            
            # finally set the state and propagate to all listeners
            for acquirable, state_info in states.items():
                acquirable.set_state_info(state_info, propagate=2)
        
        self.set_finish_hook(finish_hook)
