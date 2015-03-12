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

"""This file contains the code for an hypothetical Springfield counter/timer
controller used in documentation"""

import time

import springfieldlib

from sardana import State
from sardana.pool.controller import CounterTimerController

class SpringfieldBaseCounterTimerController(CounterTimerController):
    """The most basic controller intended from demonstration purposes only.
    This is the absolute minimum you have to implement to set a proper counter
    controller able to get a counter value, get a counter state and do an
    acquisition.
    
    This example is so basic that it is not even directly described in the
    documentation"""
    
    def __init__(self, inst, props, *args, **kwargs):
        """Constructor"""
        super(SpringfieldBaseCounterTimerController, self).__init__(inst, props, *args, **kwargs)
        self.springfield = springfieldlib.SpringfieldCounterHW()
        
    def ReadOne(self, axis):
        """Get the specified counter value"""
        return self.springfield.getValue(axis)
        
    def StateOne(self, axis):
        """Get the specified counter state"""
        springfield = self.springfield
        state = springfield.getState(axis)
        if state == 1:
            return State.On, "Counter is stopped"
        elif state == 2:
            return State.Moving, "Counter is acquiring"
        elif state == 3:
            return State.Fault, "Counter has an error"

    def StartAll(self):
        self.springfield.start_count()
            
    def StartOne(self, axis, value=None):
        """acquire the specified counter"""
        self.springfield.activate_channel(axis)              

    def LoadOne(self, axis, value):
        self.springfield.set_master(axis, value)
        
    def StopOne(self, axis):
        """Stop the specified counter"""
        self.springfield.stop(axis)        


from sardana import DataAccess
from sardana.pool.controller import Type, Description, DefaultValue, Access, FGet, FSet
    
class SpringfieldCounterTimerController(CounterTimerController):

    def __init__(self, inst, props, *args, **kwargs):
        super(SpringfieldCounterTimerController, self).__init__(inst, props, *args, **kwargs)
        
        # initialize hardware communication
        self.springfield = springfieldlib.SpringfieldCounterHW()
        
        # do some initialization
        self._counters = {}

    def AddDevice(self, axis):
        self._counters[axis] = True 

    def DeleteDevice(self, axis):
        del self._counters[axis]        
        
    StateMap = {
        1 : State.On,
        2 : State.Moving,
        3 : State.Fault,
    }
    
    def StateOne(self, axis):
        springfield = self.springfield
        state = self.StateMap[ springfield.getState(axis) ]
        status = springfield.getStatus(axis)
        return state, status

    def ReadOne(self, axis):
        value = self.springfield.getValue(axis)
        return value
        
    def StartOne(self, axis, position):
        self.springfield.move(axis, position)        

    def StopOne(self, axis):
        self.springfield.stop(axis)  

    def AbortOne(self, axis):
        self.springfield.abort(axis)
        