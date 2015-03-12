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

import time
from sardana import State
from sardana.pool.controller import CounterTimerController


class Channel:
    
    def __init__(self,idx):
        self.idx = idx            # 1 based index
        self.value = 0.0
        self.is_counting = False
        self.active = True


class DummyCounterTimerController(CounterTimerController):
    "This class is the Tango Sardana CounterTimer controller for tests"

    gender = "Simulation"
    model  = "Basic"
    organization = "Sardana team"

    MaxDevice = 1024
    
    StoppedMode = 0
    TimerMode = 1
    MonitorMode = 2
    CounterMode = 3

    def __init__(self, inst, props, *args, **kwargs):
        CounterTimerController.__init__(self, inst, props, *args, **kwargs)
        self.channels = self.MaxDevice*[None,]
        self.reset()
        
    def reset(self):
        self.start_time = None
        self.integ_time = None
        self.monitor_count = None
        self.read_channels = {}
        self.counting_channels = {}
        
    def AddDevice(self,ind):
        idx = ind - 1
        self.channels[idx] = Channel(ind)
        
    def DeleteDevice(self,ind):
        idx = ind - 1
        self.channels[idx] = None

    def PreStateAll(self):
        pass
    
    def PreStateOne(self, ind):
        pass
    
    def StateAll(self):
        pass
    
    def StateOne(self, ind):
        idx = ind - 1
        sta = State.On
        status = "Stopped"
        if ind in self.counting_channels:
            channel = self.channels[idx]
            now = time.time()
            elapsed_time = now - self.start_time
            self._updateChannelState(ind, elapsed_time)
            if channel.is_counting:
                sta = State.Moving
                status = "Acquiring"
        return sta, status
        
    def _updateChannelState(self, ind, elapsed_time):
        if self.integ_time is not None:
            # counting in time
            if elapsed_time >= self.integ_time:
                self._finish(elapsed_time)
        elif self.monitor_count is not None:
            # monitor counts
            v = int(elapsed_time*100*ind)
            if v >= self.monitor_count:
                self._finish(elapsed_time)
    
    def _updateChannelValue(self, ind, elapsed_time):
        channel = self.channels[ind-1]
        if self.integ_time is not None:
            t = elapsed_time
            if not channel.is_counting:
                t = self.integ_time
            if ind == self._timer:
                channel.value = t
            else:
                channel.value = t * channel.idx
        elif self.monitor_count is not None:
            channel.value = int(elapsed_time*100*ind)
            if ind == self._monitor:
                if not channel.is_counting:
                    channel.value = self.monitor_count
    
    def _finish(self, elapsed_time, ind=None):
        if ind is None:
            for ind, channel in self.counting_channels.items():
                channel.is_counting = False
                self._updateChannelValue(ind, elapsed_time)
        else:
            if ind in self.counting_channels:
                channel = self.counting_channels[ind]
                channel.is_counting = False
                self._updateChannelValue(ind, elapsed_time)
            else:
                channel = self.channels[ind-1]
                channel.is_counting = False
        self.counting_channels = {}
                
    def PreReadAll(self):
        self.read_channels = {}
    
    def PreReadOne(self,ind):
        channel = self.channels[ind-1]
        self.read_channels[ind] = channel

    def ReadAll(self):
        # if in acquisition then calculate the values to return
        if self.counting_channels:
            now = time.time()
            elapsed_time = now - self.start_time
            for ind, channel in self.read_channels.items():
                self._updateChannelState(ind, elapsed_time)
                if channel.is_counting:
                    self._updateChannelValue(ind, elapsed_time)
    
    def ReadOne(self, ind):
        v = self.read_channels[ind].value
        return v
    
    def PreStartAll(self):
        self.counting_channels = {}
    
    def PreStartOne(self, ind, value=None):
        idx = ind - 1
        channel = self.channels[idx]
        channel.value = 0.0
        self.counting_channels[ind] = channel
        return True
    
    def StartOne(self, ind, value=None):
        self.counting_channels[ind].is_counting = True
    
    def StartAll(self):
        self.start_time = time.time()
    
    def LoadOne(self, ind, value):
        if value > 0:
            self.integ_time = value
            self.monitor_count = None
        else:
            self.integ_time = None
            self.monitor_count = -value
    
    def AbortOne(self, ind):
        now = time.time()
        if ind in self.counting_channels:
            elapsed_time = now - self.start_time
            self._finish(elapsed_time, ind=ind)
            
