##############################################################################
##
## This file is part of Sardana
##
## http://www.tango-controls.org/static/sardana/latest/doc/html/axisex.html
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
import numpy

from sardana import State
from sardana.pool.controller import OneDController, MaxDimSize
from sardana.pool.controller import DefaultValue, Description, FGet, FSet, Type

def gauss(x, mean, ymax, fwhm, yoffset=0):
    return yoffset + ymax*numpy.power(2,-4*((x-mean)/fwhm)**2)

class Channel:
    
    def __init__(self,idx):
        self.idx = idx            # 1 based axisex
        self.value = []
        self.is_counting = False
        self.active = True
        self.amplitude = BaseValue('1.0')


class BaseValue(object):
    
    def __init__(self, value):
        self.raw_value = value
        self.init()
    
    def init(self):
        self.value = float(self.raw_value)
    
    def get(self):
        return self.value

    def get_value_name(self):
        return self.raw_value


class TangoValue(BaseValue):
    
    def init(self):
        import PyTango
        self.attr_proxy = PyTango.AttributeProxy(self.raw_value)

    def get(self):
        return self.attr_proxy.read().value


class DummyOneDController(OneDController):
    "This class is the Tango Sardana OneDController controller for tests"

    gender = "Simulation"
    model  = "Basic"
    organization = "Sardana team"

    MaxDevice = 1024
    
    BufferSize = 1024,

    axis_attributes = {
        'Amplitude' : { 
            Type : str,
            FGet : 'getAmplitude', 
            FSet : 'setAmplitude',        
            Description : 'Amplitude. Maybe a number or a tango attribute(must start with tango://)',
            DefaultValue : '1.0' },
    }
    
    def __init__(self, inst, props, *args, **kwargs):
        OneDController.__init__(self, inst, props, *args, **kwargs)
        self.channels = self.MaxDevice*[None,]
        self.reset()

    def GetAxisAttributes(self, axis):
        # the default max shape for 'value' is (16*1024,). We don't need so much
        # so we set it to BufferSize
        attrs = super(DummyOneDController, self).GetAxisAttributes(axis)
        attrs['Value'][MaxDimSize] = self.BufferSize
        return attrs
        
    def reset(self):
        self.start_time = None
        self.integ_time = None
        self.monitor_count = None
        self.read_channels = {}
        self.counting_channels = {}
        
    def AddDevice(self,axis):
        idx = axis - 1
        self.channels[idx] = channel = Channel(axis)
        channel.value = numpy.zeros(self.BufferSize, dtype=numpy.float64)
        
    def DeleteDevice(self,axis):
        idx = axis - 1
        self.channels[idx] = None

    def PreStateAll(self):
        pass
    
    def PreStateOne(self, axis):
        pass
    
    def StateAll(self):
        pass
    
    def StateOne(self, axis):
        idx = axis - 1
        sta = State.On
        status = "Stopped"
        if axis in self.counting_channels:
            channel = self.channels[idx]
            now = time.time()
            elapsed_time = now - self.start_time
            self._updateChannelState(axis, elapsed_time)
            if channel.is_counting:
                sta = State.Moving
                status = "Acquiring"
        return sta, status
        
    def _updateChannelState(self, axis, elapsed_time):
        channel = self.channels[axis-1]
        if self.integ_time is not None:
            # counting in time
            if elapsed_time >= self.integ_time:
                self._finish(elapsed_time)
        elif self.monitor_count is not None:
            # monitor counts
            v = int(elapsed_time*100*axis)
            if v >= self.monitor_count:
                self._finish(elapsed_time)
    
    def _updateChannelValue(self, axis, elapsed_time):
        channel = self.channels[axis-1]
        t = elapsed_time
        if self.integ_time is not None and not channel.is_counting:
            t = self.integ_time
        x = numpy.linspace(-10, 10, self.BufferSize[0])
        amplitude = axis * t * channel.amplitude.get()
        channel.value = gauss(x, 0, amplitude, 4)
    
    def _finish(self, elapsed_time, axis=None):
        if axis is None:
            for axis, channel in self.counting_channels.items():
                channel.is_counting = False
                self._updateChannelValue(axis, elapsed_time)
        else:
            if axis in self.counting_channels:
                channel = self.counting_channels[axis]
                channel.is_counting = False
                self._updateChannelValue(axis, elapsed_time)
            else:
                channel = self.channels[axis-1]
                channel.is_counting = False
        self.counting_channels = {}
                
    def PreReadAll(self):
        self.read_channels = {}
    
    def PreReadOne(self,axis):
        channel = self.channels[axis-1]
        self.read_channels[axis] = channel

    def ReadAll(self):
        # if in acquisition then calculate the values to return
        if self.counting_channels:
            now = time.time()
            elapsed_time = now - self.start_time
            for axis, channel in self.read_channels.items():
                self._updateChannelState(axis, elapsed_time)
                if channel.is_counting:
                    self._updateChannelValue(axis, elapsed_time)
    
    def ReadOne(self, axis):
        self._log.debug("ReadOne(%s)", axis)
        v = self.read_channels[axis].value
        return v
    
    def PreStartAll(self):
        self.counting_channels = {}
    
    def PreStartOne(self, axis, value):
        idx = axis - 1
        channel = self.channels[idx]
        channel.value = 0.0
        self.counting_channels[axis] = channel
        return True
    
    def StartOne(self, axis, value):
        self.counting_channels[axis].is_counting = True
    
    def StartAll(self):
        self.start_time = time.time()
    
    def LoadOne(self, axis, value):
        idx = axis - 1
        if value > 0:
            self.integ_time = value
            self.monitor_count = None
        else:
            self.integ_time = None
            self.monitor_count = -value
    
    def AbortOne(self, axis):
        now = time.time()
        if axis in self.counting_channels:
            elapsed_time = now - self.start_time
            self._finish(elapsed_time, axis=axis)
    
    def getAmplitude(self, axis):
        idx = axis - 1
        channel = self.channels[idx]
        return channel.amplitude.get_value_name()
    
    def setAmplitude(self, axis, value):
        idx = axis - 1
        channel = self.channels[idx]
        
        klass = BaseValue
        if value.startswith("tango://"):
            klass = TangoValue
        channel.amplitude = klass(value) 
        
