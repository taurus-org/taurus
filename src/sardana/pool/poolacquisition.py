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
    
    def __init__(self, name="CTAcquisition"):
        PoolAction.__init__(self, name)
    
    def start_action(self, *args, **kwargs):
        """Prepares everything for acquisition and starts it.
        
           :param config"""
        integ_time = kwargs.get("integ_time")
        mon_count = kwargs.get("monitor_count")
        if integ_time is None and mon_count is None:
            raise Exception("must give integration time or monitor counts")
        if integ_time is not None and mon_count is not None:
            raise Exception("must give either integration time or monitor counts (not both)")
        
        self._head = head = kwargs.get("head")
        items = kwargs.get("items")
        if items is None:
            items = self.get_elements()
        cfg = kwargs['config']
        
        # determine which is the controller which olds the timer
        if integ_time is not None:
            timer = cfg['timer']
            timer_ctrl = timer.controller

        pool_ctrls = self._pool_ctrls.keys()
        
        # make sure the controller which has the master channel is the last to
        # be called
        pool_ctrls.remove(timer_ctrl)
        pool_ctrls.append(timer_ctrl)
        
        units = cfg['units']
        for pool_ctrl in pool_ctrls:
            ctrl = pool_ctrl.ctrl
            timer = units[pool_ctrl]['timer']
            axis = timer.axis
            ctrl.PreLoadAll()
            res = ctrl.PreLoadOne(axis, integ_time)
            if not res:
                raise Exception("%s.PreLoadOne(%d) returns False" % (pool_ctrl.name, axis,))
            ctrl.LoadOne(axis, integ_time)
            ctrl.LoadAll()

        # PreStartAllCT on all controllers
        for pool_ctrl in pool_ctrls:
            pool_ctrl.ctrl.PreStartAllCT()
        
        # PreStartOneCT & StartOneCT on all elements
        enabled_channels = []
        for pool_ctrl in pool_ctrls:
            elements = self._pool_ctrls[pool_ctrl]
            unit = units[pool_ctrl]
            channels = unit['channels']
            ctrl = pool_ctrl.ctrl
            for element in elements:
                axis = element.axis
                info = channels[element]
                channel = Channel(element, info=info)
                if channel.enabled:
                    ret = ctrl.PreStartOneCT(axis)
                    if not ret:
                        raise Exception("%s.PreStartOneCT(%d) returns False" \
                                        % (ctrl.name, axis))
                    ctrl.StartOneCT(axis)
                    enabled_channels.append(channel)
        
        #if head is not None:
        #    head.set_state(State.Moving, propagate=2)
        
        # set the state of all elements to  and inform their listeners
        for channel in enabled_channels:
            channel.set_state(State.Moving, propagate=2)
        
        # StartAllCT on all controllers
        for pool_ctrl in pool_ctrls:
            pool_ctrl.ctrl.StartAllCT()
        
        self._channels = enabled_channels
    
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
        for channel in self._channels:
            element = channel.element
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
        
        # read values and propagate the change to all listeners
        self.read_value(ret=values)
        for acquirable, value in values.items():
            acquirable.put_value(value, propagate=2)
        
        # finally set the state and propagate to all listeners
        for acquirable, state_info in states.items():
            acquirable.set_state_info(state_info, propagate=2)
        
        #if self._head is not None:
        #    self._head.set_state(State.On, propagate=2)

