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

from sardana import State
from sardana.pool.controller import IORegisterController


class DummyIORController(IORegisterController):
    """This controller offers as many IORegisters as the user wants (up to 
    1024)."""

    gender = "Simulation"
    model  = "Basic"
    organization = "Sardana team"

    MaxDevice = 1024
    
    predefined_values = "0", "Online", "1" , "Offline", "2", "Standby"
    
    def __init__(self, inst, props, *args, **kwargs):
        IORegisterController.__init__(self, inst, props, *args, **kwargs)
        self.myvalue = 1

    def AddDevice(self, axis):
        self._log.debug('AddDevice %d' % axis)

    def DeleteDevice(self, axis):
        pass

    def StateOne(self, axis):
        return (State.On,"Device in On state")

    def ReadOne(self, axis):
        return self.myvalue

    def WriteOne(self, axis, value):
        self.myvalue = value
        
    def SendToCtrl(self,in_data):
        return ""
