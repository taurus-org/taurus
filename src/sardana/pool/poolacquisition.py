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
from pooldefs import AcqTriggerMode
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
    
class PoolAcquirableItem(PoolActionItem):
    
    def __init__(self, acquirable):
        PoolActionItem.__init__(self, acquirable)
        
class PoolCTAcquisition(PoolAction):
    
    def __init__(self, name="CTAcquisition"):
        PoolAction.__init__(self, name)
    
    def load(self):
        master, integ_time = self._master, self._integ_time
        master_axis = master.axis
        master_ctrl = master.controller.ctrl
        master_ctrl.PreLoadAll()
        res = master_ctrl.PreLoadOne(master_axis, integ_time)
        if not res:
            raise Exception("PreLoadOne(%d) returns False" % (master_axis,))
        master_ctrl.LoadOne(master_axis, integ_time)
        master_ctrl.LoadAll()
    
    def start_action(self, *args, **kwargs):
        """Prepares everything for acquisition and starts it.
        
           :param head: head pool element (when used by measurement group, head
                        should be the measurement group itself). Default is None,
                        meaning no head is used.
           :type head: PoolElement
           :param items: sequence of CounterTimers. Default is None meaning use all
                         current elements
           :type items: seq<PoolCounterTimer>
           :param master: master channel. Default is None meaning:
                          if head is given, use head.master. Otherwise use the first
                          item in items or first item in current elements
           :type master: PoolCounterTimer
           :param integration_time: integration time. Default is None meaning
                                    use master write value
           :type integration_time: float
           :param trigger_mode: trigger mode. Default is AcqTriggerMode.TriggerOnMaster
           :type trigger_mode: AcqTriggerMode"""
        
        self._head = kwargs.get("head")
        items = kwargs.get("items")
        if items is None:
            items = self.get_elements()
        self._master = kwargs.get("master")
        if self._master is None:
            if self._head is None:
                self._master = items[0]
            else:
                self._master = head.master
        if self._master is None:
            raise Exception("master channel not given")
        master_axis = self._master.axis
        master_controller = self._master.controller
        self._integ_time = kwargs.get("integration_time", self._master.get_value_w())
        if self._integ_time is None:
            raise Exception("integration time not given")
        
        self._terminate_on = kwargs.get("trigger_mode")
        if self._terminate_on is None:
            if self._head is None:
                self._terminate_on = AcqTriggerMode.TriggerOnMaster
            else:
                self._terminate_on = self._head.trigger_mode
        
        if self._terminate_on is None or self._terminate_on == AcqTriggerMode.TriggerUnknown:
            raise Exception("trigger mode not defined")
        
        # prepare data structures
        self._aborted = False
        
        acquisition_info = kwargs.get('acquisition_info')
        if acquisition_info is None:
            acquisition_info = {}
            for item in items:
                acquisition_info[item] = PoolAcquirableItem(item)
        self._acquisition_info = acquisition_info
        
        pool_ctrls = self._pool_ctrls.keys()
        
        # make sure the controller which has the master channel is the last to
        # be called
        pool_ctrls.remove(master_controller)
        pool_ctrls.append(master_controller)
        
        # Load the master timer/monitor with the proper value
        self.load()
        
        # PreStartAll on all controllers
        for pool_ctrl in pool_ctrls:
            pool_ctrl.ctrl.PreStartAllCT()
        
        # PreStartOne on all elements
        for item in items:
            ctrl, axis = item.controller.ctrl, item.axis
            ret = ctrl.PreStartOneCT(axis)
            if not ret:
                raise Exception("%s.PreStartOneCT(%d) returns False" % (ctrl.name, axis,))
            ctrl.StartOneCT(axis)
        
        if self._head:
            self._head.set_state(State.Moving)
        
        # set the state of all elements to  and inform their listeners
        for item in items:
            item.set_state(State.Moving)
        
        # StartAllCT on all controllers
        for pool_ctrl in pool_ctrls:
            pool_ctrl.ctrl.StartAllCT()
    
    def in_acquisition(self, states, master):
        if self._terminate_on == AcqTriggerMode.TriggerOnMaster:
            return self._is_in_action(states[master][0])
        for state in states:
            if self._is_in_action(state[0]):
                return True
        return False
    
    @taurus.core.util.DebugIt()
    def action_loop(self):
        i = 0
        
        states, values = {}, {}
        for k in self._elements:
            k = k()
            states[k] = None
            values[k] = None

        # read values to send a first event when starting to acquire
        self.read_value(ret=values)
        for acquirable, value in values.items():
            acquirable.put_value(value, propagate=2)
            
        while True:
            self.read_state_info(ret=states)
            acquiring = self.in_acquisition(states, self._master)
            
            if not acquiring:
                if self._terminate_on == AcqTriggerMode.TriggerOnMaster:
                    self.abort()
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
        
        self.read_value(ret=values)
        for acquirable, value in values.items():
            acquirable.put_value(value, propagate=2)
        
        for acquirable, state_info in states.items():
            acquirable.set_state_info(state_info, propagate=1)

