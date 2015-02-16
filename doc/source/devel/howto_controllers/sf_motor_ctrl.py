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

"""This file contains the code for an hypothetical Springfield motor controller
used in documentation"""

import springfieldlib

from sardana import State
from sardana.pool.controller import MotorController

class SpringfieldBaseMotorController(MotorController):
    """The most basic controller intended from demonstration purposes only.
    This is the absolute minimum you have to implement to set a proper motor
    controller able to get a motor position, get a motor state and move a
    motor.
    
    This example is so basic that it is not even directly described in the
    documentation"""

    MaxDevice = 128
    
    def __init__(self, inst, props, *args, **kwargs):
        """Constructor"""
        super(SpringfieldBaseMotorController, self).__init__(inst, props, *args, **kwargs)
        self.springfield = springfieldlib.SpringfieldMotorHW()
        
    def ReadOne(self, axis):
        """Get the specified motor position"""
        return self.springfield.getPosition(axis)
        
    def StateOne(self, axis):
        """Get the specified motor state"""
        springfield = self.springfield
        state = springfield.getState(axis)
        if state == 1:
            return State.On, "Motor is stopped"
        elif state == 2:
            return State.Moving, "Motor is moving"
        elif state == 3:
            return State.Fault, "Motor has an error"
    
    def StartOne(self, axis, position):
        """Move the specified motor to the specified position"""
        self.springfield.move(axis, position)              

    def StopOne(self, axis):
        """Stop the specified motor"""
        self.springfield.stop(axis)        


from sardana import DataAccess
from sardana.pool.controller import Type, Description, DefaultValue, Access, FGet, FSet
    
class SpringfieldMotorController(MotorController):

    axis_attributes = { 
        "CloseLoop" : {
                Type         : bool,
                Description  : "(de)activates the motor close loop algorithm",
                DefaultValue : False,
            },
    }
    
    def getCloseLoop(self, axis):
        return self.springfield.isCloseLoopActive(axis)
    
    def setCloseLoop(self, axis, value):
        self.springfield.setCloseLoop(axis, value)
            
    def __init__(self, inst, props, *args, **kwargs):
        super(SpringfieldMotorController, self).__init__(inst, props, *args, **kwargs)
        
        # initialize hardware communication
        self.springfield = springfieldlib.SpringfieldMotorHW()
        
        # do some initialization
        self._motors = {}

    def AddDevice(self, axis):
        self._motors[axis] = True 

    def DeleteDevice(self, axis):
        del self._motors[axis]        
        
    StateMap = {
        1 : State.On,
        2 : State.Moving,
        3 : State.Fault,
    }
    
    def StateOne(self, axis):
        springfield = self.springfield
        state = self.StateMap[ springfield.getState(axis) ]
        status = springfield.getStatus(axis)
        
        limit_switches = MotorController.NoLimitSwitch
        hw_limit_switches = springfield.getLimits(axis)
        if hw_limit_switches[0]:
            limit_switches |= MotorController.HomeLimitSwitch
        if hw_limit_switches[1]:
            limit_switches |= MotorController.UpperLimitSwitch
        if hw_limit_switches[2]:
            limit_switches |= MotorController.LowerLimitSwitch
        return state, status, limit_switches

    def ReadOne(self, axis):
        position = self.springfield.getPosition(axis)
        return position
        
    def StartOne(self, axis, position):
        self.springfield.move(axis, position)        

    def StopOne(self, axis):
        self.springfield.stop(axis)  

    def AbortOne(self, axis):
        self.springfield.abort(axis)
        
    def DefinePosition(self, axis, position):
        self.springfield.setCurrentPosition(axis, position)
