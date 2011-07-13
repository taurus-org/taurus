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

__all__ = [ "PoolAcquisition" ]

__docformat__ = 'restructuredtext'

import time
import weakref

import taurus.core.util

from sardana import State
from pooldefs import AcqTriggerMode
from poolaction import *

class PoolAcquirableItem(PoolActionItem):
    
    def __init__(self, acquirable):
        PoolActionItem.__init__(self, acquirable)
        
class PoolAcquisition(PoolAction):
    
    def __init__(self, name="GlobalAcquisition"):
        PoolAction.__init__(self, name)
    
    def load(self, master, integ_time):
        master_axis = master.axis
        master_ctrl = master.controller.ctrl
        master_ctrl.PreLoadAll()
        res = master_ctrl.PreLoadOne(master_axis, integ_time)
        if not res:
            raise Exception("PreLoadOne(%d) returns False" % (master_axis,))
        master_ctrl.LoadOne(master_axis, integ_time)
        master_ctrl.LoadAll()
    
    def start_action(self, *args, **kwargs):
        """items -> countables; integration_time; master"""
        
        items = kwargs["items"]
        integ_time = kwargs["integration_time"]
        master = kwargs["master"]
        master_axis = master.axis
        master_controller = master.controller
        
        # prepare data structures
        self._aborted = False
        self._master = master
        self._terminate_on = kwargs["termination_mode"]
        acquisition_info = {}
        for item in items:
            acquisition_info[item] = PoolAcquirableItem(item)
        self._acquisition_info = acquisition_info
        
        pool_ctrls = self._pool_ctrls.keys()
        acquirables = [ acquirable() for acquirable in self._elements ]
        
        # make sure the controller which has the master channel is the last to
        # be called
        pool_ctrls.remove(master_controller)
        pool_ctrls.append(master_controller)
        
        # Load the master timer/monitor with the proper value
        self.load(master, integ_time)
        
        # PreStartAll on all controllers
        for pool_ctrl in pool_ctrls:
            pool_ctrl.ctrl.PreStartAllCT()
        
        # PreStartOne on all elements
        for acq in acquirables:
            ctrl, axis = acq.controller.ctrl, acq.axis
            ret = ctrl.PreStartOneCT(axis)
            if not ret:
                raise Exception("PreStartOneCT(%d) returns False" % (axis,))
            ctrl.StartOneCT(axis)
        
        # set the state of all elements to  and inform their listeners
        for acq in acquirables:
            acq.set_state(State.Moving)
        
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

