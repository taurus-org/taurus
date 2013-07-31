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

from taurus import Factory
from taurus.core.taurusdevice import TaurusDevice
from taurus.core.taurusbasetypes import TaurusSWDevState, TaurusLockInfo, LockStatus

DFT_TANGO_DEVICE_DESCRIPTION = "A TANGO device"

class _TangoInfo(object):

    def __init__(self):
        self.dev_class = self.dev_type = 'TangoDevice'
        self.doc_url = 'http://www.esrf.fr/computing/cs/tango/tango_doc/ds_doc/'
        self.server_host = 'Unknown'
        self.server_id = 'Unknown'
        self.server_version = 1
                
class TangoDevice(TaurusDevice):
    def __init__(self, name, **kw):
        """Object initialization."""
        self.call__init__(TaurusDevice, name, **kw)

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # TaurusModel necessary overwrite
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # helper class property that stores a reference to the corresponding factory
    _factory = None
    
    @classmethod
    def factory(cls):
        if cls._factory is None:
            cls._factory = Factory(scheme='tango')
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
            
    def isValidDev(self):
        '''see: :meth:`TaurusDevice.isValid`'''
        return self._deviceObj is not None

    def lock(self, force=False):
        li = self.getLockInfo()
        if force:
            if self.getLockInfo().status == TaurusLockInfo.Locked:
                self.unlock(force=True)
        return self.getHWObj().lock()

    def unlock(self, force=False):
        return self.getHWObj().unlock(force)
    
    def getLockInfo(self, cache=False):
        lock_info = self._lock_info
        if cache and lock_info.status != LockStatus.Unknown:
            return lock_info
        try:
            dev = self.getHWObj()
            li = PyTango.LockerInfo()
            locked = dev.get_locker(li)
            msg = "%s " % self.getSimpleName()
            if locked:
                lock_info.id = pid = li.li
                lock_info.language = li.ll
                lock_info.host = host = li.locker_host
                lock_info.klass = li.locker_class
                if dev.is_locked_by_me():
                    status = LockStatus.LockedMaster
                    msg += "is locked by you!"
                else:
                    status = LockStatus.Locked
                    msg += "is locked by PID %s on %s" % (pid, host)
            else:
                lock_info.id = None
                lock_info.language = None
                lock_info.host = host = None
                lock_info.klass = None
                status = LockStatus.Unlocked
                msg += "is not locked"
            lock_info.status = status
            lock_info.status_msg = msg
        except:
            self._lock_info = lock_info = TaurusLockInfo()
        return lock_info
    
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
        '''optimized by reading of multiple attributes in one go'''
        t = time.time()
        try:
            result = self.read_attributes(attrs.keys())
        except PyTango.DevFailed, e:
            for attr in attrs.values():
                attr.poll(single=False, value=None, error=e, time=t)
            return
        
        for i, da in enumerate(result):
            if da.has_failed:
                v, err = None, PyTango.DevFailed(*da.get_err_stack())
            else:
                v, err = da, None
            attr = attrs[da.name]
            attr.poll(single=False, value=v, error=err, time=t)
    
    def _repr_html_(self):
        try:
            info = self.getHWObj().info()
        except:
            info = _TangoInfo()
        txt = """\
<table>
    <tr><td>Short name</td><td>{simple_name}</td></tr>
    <tr><td>Standard name</td><td>{normal_name}</td></tr>
    <tr><td>Full name</td><td>{full_name}</td></tr>
    <tr><td>Device class</td><td>{dev_class}</td></tr>
    <tr><td>Server</td><td>{server_id}</td></tr>
    <tr><td>Documentation</td><td><a target="_blank" href="{doc_url}">{doc_url}</a></td></tr>
</table>
""".format(simple_name=self.getSimpleName(), normal_name=self.getNormalName(),
           full_name=self.getFullName(), dev_class=info.dev_class,
           server_id=info.server_id, doc_url=info.doc_url)
        return txt
