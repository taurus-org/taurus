#!/usr/bin/env python

#############################################################################
##
## This file is part of Taurus, a Tango User Interface Library
## 
## http://www.tango-controls.org/static/taurus/latest/doc/html/index.html
##
## Copyright 2011 CELLS / ALBA Synchrotron, Bellaterra, Spain
## 
## Taurus is free software: you can redistribute it and/or modify
## it under the terms of the GNU Lesser General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
## 
## Taurus is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU Lesser General Public License for more details.
## 
## You should have received a copy of the GNU Lesser General Public License
## along with Taurus.  If not, see <http://www.gnu.org/licenses/>.
##
#############################################################################

"""This module contains all taurus tango database"""

__all__ = ["TangoDevice"]

__docformat__ = "restructuredtext"

import time
import PyTango

import taurus.core
from taurus.core import TaurusSWDevState

DFT_TANGO_DEVICE_DESCRIPTION = "A TANGO device"

                
class TangoDevice(taurus.core.TaurusDevice):
    def __init__(self, name, **kw):
        """Object initialization."""
        self.call__init__(taurus.core.TaurusDevice, name, **kw)

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # TaurusModel necessary overwrite
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # helper class property that stores a reference to the corresponding factory
    _factory = None
    
    @classmethod
    def factory(cls):
        if cls._factory is None:
            cls._factory = taurus.Factory(scheme='tango')
        return cls._factory

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # TaurusDevice necessary overwrite
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    def _createHWObject(self):
        try:
            return PyTango.DeviceProxy(self.getFullName())
        except PyTango.DevFailed, e:
            self.warning('Could not create HW object: %s' % (e[0].desc))
            self.traceback()

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # Protected implementation
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    def _server_state(self):
        state = None
        try:
            self.dev.ping()
            state = TaurusSWDevState.Running
        except:
            try:
                if self.dev.import_info().exported:
                    state = TaurusSWDevState.Crash
                else:
                    state = TaurusSWDevState.Shutdown
            except:
                state = TaurusSWDevState.Shutdown
        return state
        
    def decode(self, event_value):
        if isinstance(event_value, PyTango.DeviceAttribute):
            new_sw_state = TaurusSWDevState.Running
        elif isinstance(event_value, PyTango.DevFailed):
            new_sw_state = self._handleExceptionEvent(event_value)
        elif isinstance(event_value, int): # TaurusSWDevState
            new_sw_state = event_value
        else:
            self.info("Unexpected value to decode: %s" % str(event_value))
            new_sw_state = TaurusSWDevState.Crash
            
        value = PyTango.DeviceAttribute()
        value.value = new_sw_state
        
        return value
        
    def _handleExceptionEvent(self, event_value):
        """Handles the tango error event and returns the proper SW state."""
        
        new_sw_state = TaurusSWDevState.Uninitialized
        reason = event_value[0].reason
        # API_EventTimeout happens when: 
        # 1 - the server where the device is running shuts down/crashes
        # 2 - the notifd shuts down/crashes
        if reason == 'API_EventTimeout':
            if not self._deviceSwState in self.SHUTDOWNS:
                serv_state = self._server_state()
                # if the device is running it means that it must have been 
                # the event system that failed
                if serv_state == TaurusSWDevState.Running:
                    new_sw_state = TaurusSWDevState.EventSystemShutdown
                else:
                    new_sw_state = serv_state
            else:
                # Keep the old state
                new_sw_state = self._deviceSwState
                
        # API_BadConfigurationProperty happens when: 
        # 1 - at client startup the server where the device is is not 
        #     running.
        elif reason == 'API_BadConfigurationProperty':
            assert(self._deviceSwState != TaurusSWDevState.Running)
            new_sw_state = TaurusSWDevState.Shutdown
        
        # API_EventChannelNotExported happens when:
        # 1 - at client startup the server is running but the notifd
        #     is not
        elif reason == 'API_EventChannelNotExported':
            new_sw_state = TaurusSWDevState.EventSystemShutdown
        return new_sw_state
    
    def _getDefaultDescription(self):
        return DFT_TANGO_DEVICE_DESCRIPTION

    def poll(self, attrs):
        attr_names = [ a.getSimpleName() for a in attrs ]
        t = time.time()
        try:
            result = self.read_attributes(attr_names)
        except PyTango.DevFailed, e:
            for attr in attrs:
                attr.poll(single=False, value=None, error=e, time=t)
            return
        
        for i, da in enumerate(result):
            attr = attrs[i]
            if da.has_failed:
                v, err = None, PyTango.DevFailed(*da.get_err_stack())
            else:
                v, err = da, None
            attr.poll(single=False, value=v, error=err, time=t)
