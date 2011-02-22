import time
import sys
import numpy
import PyTango
from pool import OneDController

class Channel:
    
    def __init__(self,idx):
        self.idx = idx            # 1 based index
        self.value = 0.0
        self.active = False
        
class DummyOneDController(OneDController):
    "This class is the Tango Sardana 0D controller for tests"

    gender = "Simulation"
    model  = "Basic"
    organization = "CELLS - ALBA"
    image = "dummy_1d_ctrl.png"
    logo = "ALBA_logo.png"

    MaxDevice = 1024

    def __init__(self,inst,props):
        OneDController.__init__(self,inst, props)

        self.channels = [ Channel(i+1) for i in xrange(self.MaxDevice) ]
        self.read_channels = {}
        
    def AddDevice(self,ind):
        idx = ind - 1
        self.channels[ind].active = True
        
    def DeleteDevice(self,ind):
        self.channels[ind].active = False

    def StateOne(self,ind):
        sta, status = PyTango.DevState.ON, "OK"
        return (sta,status)
        
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
