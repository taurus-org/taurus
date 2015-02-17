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

import random

from sardana import State
from sardana.pool.controller import ZeroDController

class Channel:
    
    def __init__(self,idx):
        self.idx = idx            # 1 based index
        self.value = 0.0
        self.active = False


class DummyZeroDController(ZeroDController):
    """This class represents a dummy Sardana 0D controller."""

    gender = "Simulation"
    model  = "Basic"
    organization = "Sardana team"

    MaxDevice = 1024

    def __init__(self, inst, props, *args, **kwargs):
        ZeroDController.__init__(self, inst, props, *args, **kwargs)

        self.channels = [ Channel(i+1) for i in xrange(self.MaxDevice) ]
        self.read_channels = {}
        
    def AddDevice(self,ind):
        self.channels[ind].active = True
        
    def DeleteDevice(self,ind):
        self.channels[ind].active = False

    def StateOne(self,ind):
        return State.On, "OK"
        
    def _setChannelValue(self, channel):
        channel.value = 100 * channel.idx + 10*(random.random()-0.5)

    def PreReadAll(self):
        self.read_channels = {}

    def PreReadOne(self,ind):
        channel = self.channels[ind-1]
        self.read_channels[ind] = channel

    def ReadAll(self):
        for channel in self.read_channels.values():
            self._setChannelValue(channel)

    def ReadOne(self,ind):
        v = self.read_channels[ind].value
        return v
