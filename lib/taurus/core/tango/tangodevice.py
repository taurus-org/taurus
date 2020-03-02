#!/usr/bin/env python

#############################################################################
##
# This file is part of Taurus
##
# http://taurus-scada.org
##
# Copyright 2011 CELLS / ALBA Synchrotron, Bellaterra, Spain
##
# Taurus is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
##
# Taurus is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
##
# You should have received a copy of the GNU Lesser General Public License
# along with Taurus.  If not, see <http://www.gnu.org/licenses/>.
##
#############################################################################

"""This module defines the TangoDevice object"""

from builtins import object

import time
from PyTango import (DeviceProxy, DevFailed, LockerInfo, DevState)

from taurus.core.taurusdevice import TaurusDevice
from taurus.core.taurusbasetypes import (TaurusDevState, TaurusLockInfo,
                                         LockStatus, TaurusEventType)
from taurus.core.util.log import taurus4_deprecation


__all__ = ["TangoDevice"]

__docformat__ = "restructuredtext"


class _TangoInfo(object):
    pass

def __init__(self):
    self.dev_class = self.dev_type = 'TangoDevice'
    self.doc_url = 'http://www.esrf.fr/computing/cs/tango/tango_doc/ds_doc/'
    self.server_host = 'Unknown'
    self.server_id = 'Unknown'
    self.server_version = 1


class TangoDevice(TaurusDevice):
    """A Device object representing an abstraction of the PyTango.DeviceProxy
       object in the taurus.core.tango scheme"""

    # helper class property that stores a reference to the corresponding
    # factory
    _factory = None
    _scheme = 'tango'
    _description = "A Tango Device"

    def __init__(self, name='', **kw):
        """Object initialization."""
        self.call__init__(TaurusDevice, name, **kw)
        self._deviceObj = self._createHWObject()
        self._lock_info = TaurusLockInfo()
        self._deviceStateObj = None
        # TODO reimplement using the new codification
        self._deviceState = TaurusDevState.Undefined

    # Export the DeviceProxy interface into this object.
    # This way we can call for example read_attribute on an object of this
    # class
    def __getattr__(self, name):
        if name != "_deviceObj" and self._deviceObj is not None:
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

    @taurus4_deprecation(alt='.stateObj.read().rvalue [Tango] or ' +
                           '.state [agnostic]')
    def getState(self, cache=True):
        stateAttrValue = self.stateObj.read(cache=cache)
        if not stateAttrValue is None:
            state_rvalue = stateAttrValue.rvalue
            return DevState.values[state_rvalue.value]
        return None

    @taurus4_deprecation(alt='.stateObj [Tango] or ' +
                           '.factory.getAttribute(state_full_name) [agnostic]')
    def getStateObj(self):
        return self.stateObj

    @taurus4_deprecation(alt="state")
    def getSWState(self, cache=True):
        raise Exception('getSWState has been removed. Use state instead')
        # return self.getValueObj().rvalue

    @property
    def state(self, cache=True):
        """Reimplemented from :class:`TaurusDevice` to use Tango's state
        attribute for diagnosis of the current state. It supports a "cache"
        kwarg

        :param cache: (bool) If True (default), cache will be used when reading
                      the state attribute of this device

        :return: (TaurusDevState)
        """
        self._deviceState = TaurusDevState.NotReady
        try:
            taurus_tango_state = self.stateObj.read(cache).rvalue
        except:
            try:
                if self.getDeviceProxy().import_info().exported:
                    self._deviceState = TaurusDevState.Undefined
                    return self._deviceState  # Undefined
                else:
                    return self._deviceState  # NotReady
            except:
                return self._deviceState  # NotReady
        from taurus.core.tango.enums import DevState as TaurusTangoDevState
        if taurus_tango_state == TaurusTangoDevState.UNKNOWN:
            self._deviceState = TaurusDevState.Undefined
        elif taurus_tango_state not in (TaurusTangoDevState.FAULT,
                                      TaurusTangoDevState.DISABLE,
                                      TaurusTangoDevState.INIT):
            self._deviceState = TaurusDevState.Ready
        return self._deviceState

    @taurus4_deprecation(alt="state [agnostic] or stateObj.read [Tango]")
    def getValueObj(self, cache=True):
        """ Deprecated by TEP14.
        ..warning::
            this bck-compat implementation is not perfect because the
            rvalue of the returned TangoAttributeValue is now a member of
            TaurusDevState instead of TaurusSWDevState
        """
        if not cache:
            self.warning('Ignoring argument `cache=False`to getValueObj()')
        from taurus.core.tango.tangoattribute import TangoAttrValue
        ret = TangoAttrValue()
        ret.rvalue = self.state
        return ret

    def getDisplayDescrObj(self, cache=True):
        desc_obj = super(TangoDevice, self).getDisplayDescrObj(cache)
        # extend the info on dev state
        ret = []
        for name, value in desc_obj:
            if name.lower() == u'device state' and self.stateObj is not None:
                try:
                    tg_state = self.stateObj.read(cache).rvalue.name
                    value = u"%s (%s)" % (value, tg_state)
                except Exception as e:
                    value = u"cannot read state"
            ret.append((name, value))
        return ret

    def cleanUp(self):
        self.trace("[TangoDevice] cleanUp")
        self._descr = None

        if not self._deviceStateObj is None:
            self._deviceStateObj.removeListener(self)
        self._deviceStateObj = None
        self._deviceObj = None
        TaurusDevice.cleanUp(self)

    @taurus4_deprecation(alt='.state.name')
    def getDisplayValue(self, cache=True):
        return self.stateObj.read(cache=cache).rvalue.name

    def _createHWObject(self):
        try:
            return DeviceProxy(self.getFullName())
        except DevFailed as e:
            self.warning('Could not create HW object: %s' % (e.args[0].desc))
            self.traceback()

    @taurus4_deprecation(alt="getDeviceProxy()")
    def getHWObj(self):
        return self.getDeviceProxy()

    def getDeviceProxy(self):
        if self._deviceObj is None:
            self._deviceObj = self._createHWObject()
        return self._deviceObj

    @taurus4_deprecation(alt='getDeviceProxy() is not None')
    def isValidDev(self):
        """see: :meth:`TaurusDevice.isValid`"""
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

    def removeListener(self, listener):
        ret = TaurusDevice.removeListener(self, listener)
        if not ret or self.hasListeners():
            return ret  # False, None or True
        return self.stateObj.removeListener(self)

    def addListener(self, listener):
        weWereListening = self.hasListeners()
        ret = TaurusDevice.addListener(self, listener)
        if not ret:
            return ret
        # We are only listening to State if someone is listening to us
        if weWereListening:
            # We were listening already, so we must fake an event to the new
            # subscribed listener with the current value
            try:
                evt_value = self.__decode(self.stateObj.read())
            except:
                # the value may not be available (e.g. if device is not ready)
                self.debug('Cannot read state')
                return ret
            listeners = hasattr(listener, '__iter__') and listener or [
                listener]
            self.fireEvent(TaurusEventType.Change, evt_value, listeners)
        else:
            # We were not listening to events, but now we have to
            self.stateObj.addListener(self)
        return ret

    def eventReceived(self, event_src, event_type, event_value):
        if event_type == TaurusEventType.Config:
            return
        value = self.__decode(event_value)
        new_state = value.rvalue
        if new_state != self._deviceState:
            msg = "Device State changed %s -> %s" % (self._deviceState.name,
                                                     new_state.name)
            self.debug(msg)
            self._deviceState = new_state
            self.fireEvent(TaurusEventType.Change, value)

    def __decode(self, event_value):
        """Decode events from the state attribute into TangoAttrValues whose
        rvalue is the Device state"""
        from taurus.core.tango.tangoattribute import TangoAttrValue
        if isinstance(event_value, TangoAttrValue):  # for change events (&co)
            new_state = TaurusDevState.Ready
        elif isinstance(event_value, DevFailed):  # for error events
            new_state = TaurusDevState.NotReady
        else:
            self.info("Unexpected event value: %r", event_value)
            new_state = TaurusDevState.Undefined
        from taurus.core.taurusbasetypes import TaurusModelValue
        value = TaurusModelValue()
        value.rvalue = new_state
        return value

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
            req_id = self.read_attributes_asynch(list(attrs.keys()))
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
        timeout = int(timeout * 1000)
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
            result = self.read_attributes(list(attrs.keys()))
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

    @taurus4_deprecation(alt=".description")
    def getDescription(self, cache=True):
        return self.description

    @property
    def description(self):
        try:
            self._description = self.getDeviceProxy().description()
        except:
            pass
        return self._description

    @property
    def stateObj(self):
        if self._deviceStateObj is None:
            self._deviceStateObj = self.getAttribute("state")
        return self._deviceStateObj
