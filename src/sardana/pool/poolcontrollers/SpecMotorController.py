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

#import time
#import threading
#import traceback
#from math import pow, sqrt

from sardana import State  #sustituye a   import PyTango
from sardana.pool.controller import MotorController

from SpecClient import SpecConnectionsManager
from SpecClient import SpecMotor
from SpecClient.Spec import Spec

class SpecMotorController(MotorController):
    """This class represents a basic, Spec motor controller."""
    gender = "Simulation"
    model  = "Basic"
    organization = "CELLS - ALBA && ESRF"
#    image = "dummy_motor_ctrl.png"
    logo = "ALBA_logo.png"


    ctrl_properties= { 'spec' : { 'Type' : 'DevString', 'Description' : 'Spec session to connect to (host:port_or_session_name string)' } }
    axis_attributes = {'specmotorname' : { 'type' : str, 'Description' : 'Spec motor name'} }
#    axis_attributes = {'specmotorname' : { 
#                               'type' : str, 'Description' : 'Spec motor name',
#                               'fget' : 'getSMN',
#                               'fset' : 'setSMN' }
#        }
    MaxDevice = 1024

# --------------------------------------------------------------------------
# Init() 
# --------------------------------------------------------------------------  
    def __init__(self, inst, props, *args, **kwargs):
        MotorController.__init__(self, inst, props, *args, **kwargs)
        self.m = self.MaxDevice*[None,]
        # connect to spec ;
        # need to use a thread to process socket events, because there is no way to
        # interface with an existing loop AFAIK
        self.specConman = SpecConnectionsManager.SpecConnectionsManager(pollingThread = True, also_dispatch_events = True)
        # establish connection with spec
        self.specCon = self.specConman.getConnection(self.spec)
        self.specM = Spec(self.spec) 

# --------------------------------------------------------------------------
# AddDevice/DelDevice() 
# --------------------------------------------------------------------------    
    def AddDevice(self,axis):
        idx = axis - 1
        if len(self.m) < axis:
            self._log.error("Invalid axis %d" % axis)
            raise Exception("Invalid axis %d" % axis)

    def DeleteDevice(self, axis):
        idx = axis - 1
        if len(self.m) < axis or not self.m[idx]:
            self._log.error("Invalid axis %d" % axis)
            raise Exception("Invalid axis %d" % axis)
        self.m[idx] = None

# --------------------------------------------------------------------------
# StateOne() ??
# --------------------------------------------------------------------------    
    def StateOne(self, axis):
        state = State.Unknown
        status = "Undefined"
        idx = axis - 1
        if len(self.m) < axis or not self.m[idx]:
            self._log.error("Invalid axis %d" % axis)
            raise Exception("Invalid axis %d" % axis)
        specMotor = self.m[idx]
        if not self.specCon.isSpecConnected():
            state = State.Disable
            status = "Disable"
        else: 
            s =  self.m[idx].getState()
            if (SpecMotor.UNUSABLE == s):
                state =  State.Fault
                status = "Motor is powered" 
            if (SpecMotor.READY == s):
                state =  State.On
                status = "Motor is on"  
            if (SpecMotor.MOVESTARTED == s):
                state =  State.Running
                status = "Motor is ready"  
            if (SpecMotor.MOVING == s):
                state =  State.Moving
                status = "Motor is moving"   
            if (SpecMotor.ONLIMIT == s):
                state =  State.Alarm
                status = "Motor HW is in alarm"                

            return state, status

# --------------------------------------------------------------------------
# ReadOne() 
# --------------------------------------------------------------------------  
    def ReadOne(self,axis):
        idx = axis - 1
        if len(self.m) < axis or not self.m[idx]:
            self._log.error("Invalid axis %d" % axis)
            raise Exception("Invalid axis %d" % axis)
        return self.m[idx].getPosition()

# --------------------------------------------------------------------------
# StartOne/StopOne() 
# --------------------------------------------------------------------------     
    def StartOne(self, axis, pos):
        idx = axis - 1
        if len(self.m) < axis or not self.m[idx]:
            self._log.error("Invalid axis %d" % axis)
            raise Exception("Invalid axis %d" % axis)
        self.m[idx].move(pos)     
       
    def AbortOne(self, axis):
        idx = axis - 1
        if len(self.m) < axis or not self.m[idx]:
            self._log.error("Invalid axis %d" % axis)
            raise Exception("Invalid axis %d" % axis)
        self.m[idx].stop(pos)   

    def StopOne(self, axis):
        self.AbortOne(axis)

    def StartAll(self): 
        pass

    def AbortAll(self):
        pass

# --------------------------------------------------------------------------
# SetAxisPar/GetAxisPar() 
# --------------------------------------------------------------------------    
    def SetAxisPar(self,axis,par_name,*args):
        idx = axis - 1
        par_name = par_name.lower()
        if len(self.m) < axis or not self.m[idx]:
            self._log.error("Invalid axis %d" % axis)
            return
        if par_name == "velocity" and len(args)>0:
            self.spec_motor.setParameter("slew_rate", args[0])
        elif par_name in ("acceleration")  and len(args)>0:
            return self.spec_motor.setParameter("acceleration", args[0]) 
        elif par_name == "base_rate" and len(args)>0:
            return self.spec_motor.setParameter("base_rate", args[0])   
        elif par_name == "backlash":
            return self.spec_motor.setParameter("backlash", args[0])
        elif par_name == "offset" and len(args)>0:
            self.spec_motor.setParameter("offset",args[0])
        elif par_name == "limits" and len(args)>1:
            self.spec.chg_offset(self.spec_motor, args[0], args[1])
        else:
            self._log.error("Invalid parameter")     

    def GetAxisPar(self,axis,par_name):
        idx = axis - 1
        par_name = par_name.lower()
        if len(self.m) < axis or not self.m[idx]:
            self._log.error("Invalid axis %d" % axis)
            return
        if par_name == "velocity":
            return self.m[idx].getParameter("slew_rate")
        elif par_name in ("acceleration"):
            return self.m[idx].getParameter("acceleration") 
        elif par_name == "base_rate":
            return self.m[idx].getParameter("base_rate")   
        elif par_name == "backlash":
            return self.m[idx].getParameter("backlash")
        elif par_name == "dial_position":
            return self.m[idx].getDialPosition()
        elif par_name == "offset":
            return self.m[idx].getOffset()
        elif par_name == "step_per_unit":
            return self.m[idx].getParameter("step_size")
        elif par_name == "limits":
            return self.m[idx].getLimits()
        elif par_name == "sign":
            return self.m[idx].getSign()
        elif par_name == "position":
            return self.m[idx].getPosition()
        elif par_name == "state":
            return self.m[idx].getState()
        elif par_name == "name":
            return self.m[idx].specName
        else:
            self._log.error("Invalid parameter")     

# --------------------------------------------------------------------------
# SetAxisExtraPar/GetAxisExtraPar() 
# --------------------------------------------------------------------------    
    def SetAxisExtraPar(self,axis,name,value):
        idx = axis - 1
        if name == "specmotorname":
#            self.m[idx] = SpecMotor.SpecMotorA(value, self.spec)
            exists = 0
            nm = self.specCon.getChannel('var/MOTORS').read()
            #check motor name
            for i in range(nm):
                if self.specM.motor_mne(i)==value:
                    self.m[idx] = SpecMotor.SpecMotorA(value, self.spec)
                    exists = 1
                    break
            if not exists:
                self.m[idx] = None
        else:
            self.m[idx] = None
                    

    def GetAxisExtraPar(self,axis):
        idx = axis - 1
        if len(self.m) < axis or not self.m[idx]:
            self._log.error("Invalid axis %d" % axis)
            raise Exception("Invalid axis %d" % axis)
        return self.m[idx].specName

#    def getSpecMotorName(self):
#        return self.SpecMotorName
    
#    def setSpecMotorName(self, value):
#        self.SpecMotorName = value
        
#    def getSMN(self, axis):
#        return self.m[axis - 1].getSpecMotorName()

#    def setSMN(self, axis, name):
##        axis_attributes['SpecMotorName'] = attr_name
#        self.m[axis - 1].setSpecMotorName(name)



