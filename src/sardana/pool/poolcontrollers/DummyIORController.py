#############################################################################
##
## file :    DummyIORController.py
##
## description : 
##
## project :    Sardana/Pool/ctrls/OIRegister
##
## developers history: gcuni,sblanch
##
## copyleft :    Cells / Alba Synchrotron
##               Bellaterra
##               Spain
##
#############################################################################
##
## This file is part of Sardana.
##
## This is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 3 of the License, or
## (at your option) any later version.
##
## This software is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program; if not, see <http://www.gnu.org/licenses/>.
###########################################################################

from sardana import State
from sardana.pool.controller import IORegisterController


class DummyIORController(IORegisterController):
    """This controller offers as many IORegisters as the user wants.
    """

    gender = ""
    model  = ""
    organization = "CELLS - ALBA"
    image = ""
    icon = ""
    logo = "ALBA_logo.png"
    MaxDevice = 1024
    
    predefined_values = ("0", "Online", "1" , "Offline", "2", "Standby" )
    
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
