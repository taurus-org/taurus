#!/usr/bin/env python

#############################################################################
##
## This file is part of Taurus
## 
## http://taurus-scada.org
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

"""This module defines the TangoDevice object"""

__all__ = ["TangoDevice"]

__docformat__ = "restructuredtext"

import time
from PyTango import (DeviceProxy, DevFailed, LockerInfo)

from taurus.core.taurusdevice import TaurusDevice
from taurus.core.taurusbasetypes import (TaurusSWDevState, TaurusLockInfo,
                                         LockStatus, TaurusEventType)
from taurus.core.util.log import tep14_deprecation

DFT_TANGO_DEVICE_DESCRIPTION = "A TANGO device"

class _TangoInfo(object):

    def __init__(self):
        self.dev_class = self.dev_type = 'TangoDevice'
        self.doc_url = 'http://www.esrf.fr/computing/cs/tango/tango_doc/ds_doc/'
        self.server_host = 'Unknown'
        self.server_id = 'Unknown'
        self.server_version = 1
                
class TangoDevice(TaurusDevice):
    """A Device object representing an abstraction of the PyTango.DeviceProxy
       object in the taurus.core.tango scheme"""

    # helper class property that stores a reference to the corresponding factory
    _factory = None
    _scheme = 'tango'

    def __init__(self, name, **kw):
        """Object initialization."""
        self.call__init__(TaurusDevice, name, **kw)
        self._deviceObj = self._createHWObject()
        self._lock_info = TaurusLockInfo()

    # Export the DeviceProxy interface into this object.
    # This way we can call for example read_attribute on an object of this class
    def __getattr__(self, name):
        if self._deviceObj is not None:
            return getattr(self._deviceObj, name)
        cls_name = self.__class__.__name__
        raise AttributeError("'%s' has no attribute '%s'" % (cls_name, name))

    # def __setattr__(self, name, value):
    #     if '_deviceObj' in self.__dict__ and self._deviceObj is not None:
    #         return setattr(self._deviceObj, name, value)
    #     super(TaurusDevice, self).__setattr__(name, value)

    def __contains__(self, key):
        """delegate the contains interface to the device proxy"""
        hw = self.getDeviceProxy()
        if hw is None:
            return False
        return hw.__contains__(key)

    def __getitem__(self, key):
        """read attribute value using key-indexing syntax (e.g. as in a dict)
        on the device"""
        attr = self.getAttribute(key)
        return attr.read()

    def __setitem__(self, key, value):
        """set attribute value using key-indexing syntax (e.g. as in a dict)
        on the device"""
        attr = self.getAttribute(key)
        return attr.write(value)

    def getAttribute(self, attrname):
        """Returns the attribute object given its name"""

        slashnb = attrname.count('/')
        if slashnb == 0:
            attrname = "%s/%s" % (self.getFullName(), attrname)
        elif attrname[0] == '/':
            attrname = "%s%s" % (self.getFullName(), attrname)
        return self.factory().getAttribute(attrname)

    def getState(self, cache=True):
        stateAttrValue = self.getStateObj().getValueObj(cache=cache)
        if not stateAttrValue is None:
            return stateAttrValue.rvalue
        return None

    @tep14_deprecation(alt="getState()")
    def getSWState(self, cache=True):
        return self.getState(cache)

    def getDisplayDescrObj(self,cache=True):
        obj = []
        obj.append(('name', self.getDisplayName(cache=cache)))
        descr = self.getDescription(cache=cache)
        if descr.lower() != self._getDefaultDescription().lower():
            obj.append(('description', descr))
        obj.append(('device state', self.getStateObj().getDisplayValue()) or self.getNoneValue())
        sw_state = TaurusSWDevState.whatis(self.getValueObj(cache).rvalue)
        obj.append('SW state', sw_state)
        return obj

    def cleanUp(self):
        self._deviceObj = None
        TaurusDevice.cleanUp(self)

    @tep14_deprecation()
    def getDisplayValue(self,cache=True):
        return TaurusSWDevState.whatis(self.getValueObj(cache).rvalue)

    def _createHWObject(self):
        try:
            return DeviceProxy(self.getFullName())
        except DevFailed, e:
            self.warning('Could not create HW object: %s' % (e[0].desc))
            self.traceback()

    @tep14_deprecation(alt="getDeviceProxy()")
    def getHWObj(self):
        return self.getDeviceProxy()

    def getDeviceProxy(self):
        return self._deviceObj

    @tep14_deprecation()
    def isValidDev(self):
        '''see: :meth:`TaurusDevice.isValid`'''
        return self._deviceObj is not None

    def lock(self, force=False):
        li = self.getLockInfo()
        if force:
            if self.getLockInfo().status == TaurusLockInfo.Locked:
                self.unlock(force=True)
        return self.getDeviceProxy().lock()

    def unlock(self, force=False):
        return self.getDeviceProxy().unlock(force)
    
    def getLockInfo(self, cache=False):
        lock_info = self._lock_info
        if cache and lock_info.status != LockStatus.Unknown:
            return lock_info
        try:
            dev = self.getDeviceProxy()
            li = LockerInfo()
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
        from taurus.core.tango.tangoattribute import TangoAttrValue 
        if isinstance(event_value, TangoAttrValue):
            new_sw_state = TaurusSWDevState.Running
        elif isinstance(event_value, DevFailed):
            new_sw_state = self._handleExceptionEvent(event_value)
        elif isinstance(event_value, int): # TaurusSWDevState
            new_sw_state = event_value
        else:
            self.info("Unexpected value to decode: %s" % str(event_value))
            new_sw_state = TaurusSWDevState.Crash
            
        value = TangoAttrValue()
        value.rvalue = new_sw_state
        
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

    def removeListener(self, listener):
        ret = TaurusDevice.removeListener(self, listener)
        if not ret or self.hasListeners():
            return ret # False, None or True
        return self.getStateObj().removeListener(self)

    def addListener(self, listener):
        weWereListening = self.hasListeners()
        ret = TaurusDevice.addListener(self, listener)
        if not ret:
            return ret

        # We are only listening to State if someone is listening to us
        if weWereListening:
            # We were listening already, so we must fake an event to the new
            # subscribed listener with the current value
            self.fireEvent(TaurusEventType.Change, self.getValueObj(), hasattr(listener,'__iter__') and listener or [listener])
        else:
            # We were not listening to events, but now we have to
            self.getStateObj().addListener(self)
        return ret

    def eventReceived(self, event_src, event_type, event_value):
        if event_type == TaurusEventType.Config:
            return
        value = self.decode(event_value)

        if value.rvalue != self._deviceSwState.rvalue:
            msg = "SW Device State changed %s -> %s" %\
                  (TaurusSWDevState.whatis(self._deviceSwState.rvalue),
                   TaurusSWDevState.whatis(value.rvalue))
            self.debug(msg)
            self._deviceSwState = value
            self.fireEvent(TaurusEventType.Change, value)

    def _getDefaultDescription(self):
        return DFT_TANGO_DEVICE_DESCRIPTION

    def __pollResult(self, attrs, ts, result, error=False):
        if error:
            for attr in attrs.values():
                attr.poll(single=False, value=None, error=result, time=ts)
            return

        for da in result:
            if da.has_failed:
                v, err = None, DevFailed(*da.get_err_stack())
            else:
                v, err = da, None
            attr = attrs[da.name]
            attr.poll(single=False, value=v, error=err, time=ts)

    def __pollAsynch(self, attrs):
        ts = time.time()
        try:
            req_id = self.read_attributes_asynch(attrs.keys())
        except DevFailed as e:
            return False, e, ts
        return True, req_id, ts

    def __pollReply(self, attrs, req_id, timeout=None):
        ok, req_id, ts = req_id
        if not ok:
            self.__pollResult(attrs, ts, req_id, error=True)
            return

        if timeout is None:
            timeout = 0
        timeout = int(timeout*1000)
        result = self.read_attributes_reply(req_id, timeout)
        self.__pollResult(attrs, ts, result)

    def poll(self, attrs, asynch=False, req_id=None):
        '''optimized by reading of multiple attributes in one go'''
        if req_id is not None:
            return self.__pollReply(attrs, req_id)

        if asynch:
            return self.__pollAsynch(attrs)

        error = False
        ts = time.time()
        try:
            result = self.read_attributes(attrs.keys())
        except DevFailed as e:
            error = True
            result = e
        self.__pollResult(attrs, ts, result, error=error)
    
    def _repr_html_(self):
        try:
            info = self.getDeviceProxy().info()
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
