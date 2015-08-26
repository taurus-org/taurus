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

"""This module contains the base class for a taurus device"""

__all__ = ["TaurusDevice"]

__docformat__ = "restructuredtext"

from .taurusbasetypes import TaurusSWDevState, TaurusEventType, \
    TaurusLockInfo, TaurusElementType
from .taurusmodel import TaurusModel
from .taurushelper import Factory
from taurus.core.util.log import tep14_deprecation

DFT_DEVICE_DESCRIPTION = "A device"


class TaurusDevice(TaurusModel):

    SHUTDOWNS = (TaurusSWDevState.Shutdown, TaurusSWDevState.Crash,
                 TaurusSWDevState.EventSystemShutdown)

    """A Device object representing an abstraction of the PyTango.DeviceProxy
       object in the taurus.core layer"""

    def __init__(self, name, **kw):
        """Object initialization."""
        parent = kw.pop('parent', None)
        storeCallback = kw.pop('storeCallback', None)
        self.__dict__.update(kw)
        self.call__init__(TaurusModel, name, parent)

        self._deviceStateObj = None
        self._lock_info = TaurusLockInfo()
        self._descr = None
        self._deviceSwState = self.decode(TaurusSWDevState.Uninitialized)

        if storeCallback:
            storeCallback(self)

    def cleanUp(self):
        self.trace("[TaurusDevice] cleanUp")
        self._descr = None
        #self._deviceSwObj
        if not self._deviceStateObj is None:
            self._deviceStateObj.removeListener(self)
        self._deviceStateObj = None
        TaurusModel.cleanUp(self)

    @classmethod
    def factory(cls):
        if cls._factory is None:
            cls._factory = Factory(scheme=cls._scheme)
        return cls._factory

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

    def __contains__(self, key):
        """Reimplement in schemes if you want to support membership testing for
        attributes of the device
        """
        raise TypeError("'%s' does not support membership testing" %
                        self.__class__.__name__)

    def getStateObj(self):
        if self._deviceStateObj is None:
            self._deviceStateObj = self.factory().getAttribute("%s/state" % self.getFullName()) # tango-centric!
        return self._deviceStateObj

    def getState(self, cache=True):
        stateAttrValue = self.getStateObj().getValueObj(cache=cache)
        if not stateAttrValue is None:
            return stateAttrValue.rvalue
        return None

    def getSWState(self, cache=True):
        return self.getValueObj(cache=cache).rvalue

    def getAttribute(self, attrname):
        """Returns the attribute object given its name"""

        slashnb = attrname.count('/')
        if slashnb == 0:
            attrname = "%s/%s" % (self.getFullName(), attrname)
        elif attrname[0] == '/':
            attrname = "%s%s" % (self.getFullName(), attrname)
        import taurusattribute
        return self.factory().getObject(taurusattribute.TaurusAttribute,attrname)

    def getLockInfo(self, cache=False):
        return self._lock_info

    def lock(self, force=False):
        pass

    def unlock(self, force=False):
        pass

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # TaurusModel implementation
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    @classmethod
    def getTaurusElementType(cls):
        return TaurusElementType.Device

    @classmethod
    def buildModelName(cls, parent_model, relative_name):
        """build an 'absolute' model name from the parent model and the 'relative'
        name.
        - If parent_model is a TaurusAuthority, the return is a composition of
        the authority model name and the device name
        - If parent_model is a TaurusDevice, the relative name is ignored and
        the parent name is returned
        
        Note: This is a basic implementation. You may need to reimplement this 
              for a specific scheme if it supports "useParentModel". 
        """
        if parent_model is None:
            return relative_name
        parent_name = parent_model.getFullName()
        if not parent_name:
            return relative_name
        if isinstance(parent_model, cls):
            return parent_name
        return '%s/%s' % (parent_name,relative_name)

    @classmethod
    def getNameValidator(cls):
        return cls.factory().getDeviceNameValidator()

    def getValueObj(self, cache=True):
        if not self.hasListeners() or not cache:
            try:
                v = self.getStateObj().read(cache=cache)
            except Exception as e:
                v = e
            self._deviceSwState = self.decode(v)
        return self._deviceSwState

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

    def getDescription(self,cache=True):
        if self._descr is None or not cache:
            try:
                self._descr = self.description()
            except:
                self._descr = self._getDefaultDescription()
        return self._descr

    def removeListener(self, listener):
        ret = TaurusModel.removeListener(self, listener)
        if not ret or self.hasListeners():
            return ret # False, None or True
        return self.getStateObj().removeListener(self)

    def addListener(self, listener):
        weWereListening = self.hasListeners()
        ret = TaurusModel.addListener(self, listener)
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

    def getChildObj(self, child_name):
        if child_name is None or len(child_name) == 0:
            return None
        obj_name = "%s%s" % (self.getFullName(), child_name)
        return self.factory().findObject(obj_name)

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
        return DFT_DEVICE_DESCRIPTION

    def poll(self, attrs, asynch=False, req_id=None):
        '''Polling certain attributes of the device. This default
        implementation simply polls each attribute one by one'''

        # asynchronous requests are not supported. If asked to do it,
        # just return an ID of 1 and in the reply (req_id != None) we do a
        # synchronous polling.
        if asynch is True:
            return 1
        for attr in attrs.values():
            attr.poll()
