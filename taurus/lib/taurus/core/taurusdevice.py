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

"""This module contains the base class for a taurus device"""

__all__ = ["TaurusDevice"]

__docformat__ = "restructuredtext"

from .taurusbasetypes import TaurusSWDevState, TaurusEventType, \
    TaurusLockInfo, TaurusElementType
from .taurusmodel import TaurusModel

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

        self._deviceObj = self._createHWObject()
        self._deviceStateObj = None
        self._lock_info = TaurusLockInfo()
        self._descr = None
        self._deviceSwState = self.decode(TaurusSWDevState.Uninitialized)

        if storeCallback:
            storeCallback(self)

    def cleanUp(self):
        self.trace("[TaurusDevice] cleanUp")
        self._deviceObj = None
        self._descr = None
        #self._deviceSwObj
        if not self._deviceStateObj is None:
            self._deviceStateObj.removeListener(self)
        self._deviceStateObj = None
        TaurusModel.cleanUp(self)

    # Export the DeviceProxy interface into this object.
    # This way we can call for example read_attribute on an object of this class
    def __getattr__(self, name):
        if '_deviceObj' in self.__dict__ and self._deviceObj is not None:
            return getattr(self._deviceObj, name)
        cls_name = self.__class__.__name__
        raise AttributeError("'%s' has no attribute '%s'" % (cls_name, name))

    #def __setattr__(self, name, value):
    #    if '_deviceObj' in self.__dict__ and self._deviceObj is not None:
    #        return setattr(self._deviceObj, name, value)
    #    super(TaurusDevice, self).__setattr__(name, value)

    # Export the 'act like dictionary' feature of PyTango.DeviceProxy
    def __getitem__(self, key):
        attr = self.getAttribute(key)
        return attr.read()

    def __setitem__(self, key, value):
        attr = self.getAttribute(key)
        return attr.write(value)

    def __contains__(self, key):
        hw = self.getHWObj()
        if hw is None:
            return False
        return hw.__contains__(key)

    def getHWObj(self):
        return self._deviceObj

    def getStateObj(self):
        if self._deviceStateObj is None:
            self._deviceStateObj = self.factory().getAttribute("%s/state" % self.getFullName())
        return self._deviceStateObj

    def getState(self, cache=True):
        stateAttrValue = self.getStateObj().getValueObj(cache=cache)
        if not stateAttrValue is None:
            return stateAttrValue.value
        return None

    def getSWState(self, cache=True):
        return self.getValueObj(cache=cache).value

    def getAttribute(self, attrname):
        """Returns the attribute object given its name"""

        slashnb = attrname.count('/')
        if slashnb == 0:
            attrname = "%s/%s" % (self.getFullName(), attrname)
        elif attrname[0] == '/':
            attrname = "%s%s" % (self.getFullName(), attrname)
        import taurusattribute
        return self.factory().getObject(taurusattribute.TaurusAttribute,attrname)

    def isValidDev(self):
        """returns True if the device is in "working conditions

        The default implementation always returns True. Reimplement it in
        subclasses if there are cases in which the device cannot be queried
        (e.g. in Tango, the TangoDevice object may exist even if there is not a real
        hardware device associated, in which case this method should return False)
        """
        return True

    def getLockInfo(self, cache=False):
        return self._lock_info

    def lock(self, force=False):
        pass

    def unlock(self, force=False):
        pass

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # Mandatory implementation in sub class
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    def _createHWObject(self):
        raise NotImplementedError

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
        - If parent_model is a TaurusDatabase, the return is a composition of
        the database model name and is device name
        - If parent_model is a TaurusDevice, the relative name is ignored and
        the parent name is returned
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
        import taurusvalidator
        return taurusvalidator.DeviceNameValidator()

    def getValueObj(self, cache=True):
        if not self.hasListeners() or not cache:
            try:
                v = self.getStateObj().read(cache=cache)
            except Exception as e:
                v = e
            self._deviceSwState = self.decode(v)
        return self._deviceSwState

    def getDisplayValue(self,cache=True):
        return TaurusSWDevState.whatis(self.getValueObj(cache).value)

    def getDisplayDescrObj(self,cache=True):
        obj = []
        obj.append(('name', self.getDisplayName(cache=cache)))
        descr = self.getDescription(cache=cache)
        if descr.lower() != self._getDefaultDescription().lower():
            obj.append(('description', descr))
        obj.append(('device state', self.getStateObj().getDisplayValue()) or self.getNoneValue())
        obj.append(('SW state', self.getDisplayValue()))
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
        return self.factory().findObject("%s%s" % (self.getFullName(), child_name))
        return self.getAttribute(child_name)

    def eventReceived(self, event_src, event_type, event_value):
        new_sw_state = TaurusSWDevState.Uninitialized

        if event_type == TaurusEventType.Config:
            return
        value = self.decode(event_value)

        if value.value != self._deviceSwState.value:
            self.debug("SW Device State changed %s -> %s" % (TaurusSWDevState.whatis(self._deviceSwState.value), TaurusSWDevState.whatis(new_sw_state)))
            self._deviceSwState = value
            self.fireEvent(TaurusEventType.Change, value)

    def _getDefaultDescription(self):
        return DFT_DEVICE_DESCRIPTION

    def poll(self, attrs):
        '''Polling certain attributes of the device. This default
        implementation simply polls each attribute one by one'''
        for attr in attrs.values():
            attr.poll()
