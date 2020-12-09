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

"""This module contains the base TaurusModel class"""

from builtins import object

import weakref
try:
    from collections.abc import Sequence
except ImportError:  # bck-compat py 2.7
    from collections import Sequence

from .util.log import Logger
from .util.event import (CallableRef,
                         BoundMethodWeakref,
                         _BoundMethodWeakrefWithCall)
from .taurusbasetypes import TaurusEventType, MatchLevel
from .taurushelper import Factory

__all__ = ["TaurusModel"]

__docformat__ = "restructuredtext"


class TaurusModel(Logger):

    _factory = None
    RegularEvent = (TaurusEventType.Change,
                    TaurusEventType.Config, TaurusEventType.Periodic)

    def __init__(self, full_name='', parent=None, serializationMode=None):
        v = self.getNameValidator()
        self._full_name, self._norm_name, self._simp_name = v.getNames(
            full_name, self.factory())

        if self._full_name is None and self._norm_name and self._simp_name is None:
            self.trace("invalid name")

        name = self._simp_name or self._norm_name or self._full_name or 'TaurusModel'
        self.call__init__(Logger, name, parent)

        if serializationMode is None:
            s_obj = parent
            if s_obj is None:
                s_obj = self.factory()
            serializationMode = s_obj.getSerializationMode()
        self._serialization_mode = serializationMode

        self._parentObj = parent
        self._listeners = []

    def __str__name__(self, name):
        return '{0}({1})'.format(self.__class__.__name__, name)

    def __str__(self):
        return self.__str__name__(self.getNormalName())

    def __repr__(self):
        return self.__str__name__(self.getFullName())

    def cleanUp(self):
        self.trace("[TaurusModel] cleanUp")
        self._parentObj = None
        self._listeners = None
        Logger.cleanUp(self)

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # API for Factory access
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    @classmethod
    def factory(cls):
        if cls._factory is None:
            cls._factory = Factory(scheme=cls._scheme)
        return cls._factory

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # API for naming
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    @classmethod
    def getTaurusElementType(cls):
        raise NotImplementedError("TaurusModel.getTaurusElementType cannot"
                                  " be called")

    def getFullName(self):
        return self._full_name

    def getNormalName(self):
        return self._norm_name

    def getSimpleName(self):
        return self._simp_name

    @classmethod
    def isValid(cls, *args, **kwargs):
        return cls.getNameValidator().isValid(*args, **kwargs)

    @classmethod
    def buildModelName(cls, parent_model, relative_name):
        raise NotImplementedError(
            "TaurusModel.buildModelName cannot be called")

    @classmethod
    def getNameValidator(cls):
        raise NotImplementedError("TaurusModel.getNameValidator cannot be"
                                  "called")

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # API for hierarchy access
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    def getParentObj(self):
        return self._parentObj

    def getChildObj(self, child_name):
        return None  # TODO: consider raising NotImplementedError instead

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # API for serialization
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    def setSerializationMode(self, mode):
        """Sets the serialization mode for the system.

        :param mode: (TaurusSerializationMode) the new serialization mode"""
        self._serialization_mode = mode

    def getSerializationMode(self):
        """Gives the serialization operation mode.

        :return: (TaurusSerializationMode) the current serialization mode"""
        return self._serialization_mode

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # API for value access
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    def getDisplayDescrObj(self, cache=True):
        """A brief description of the model. Can be used as tooltip, for example"""
        raise NotImplementedError("TaurusModel.getDisplayDescrObj cannot be"
                                  " called")

    def getDisplayName(self, cache=True, complete=True):
        full_name = self.getFullName()
        normal_name = self.getNormalName()
        simple_name = self.getSimpleName()
        if simple_name:
            ret = simple_name
            if complete:
                ret += " (" + normal_name.upper() + ")"
        elif normal_name:
            ret = normal_name.upper()
        else:
            ret = full_name.upper()
        return ret

    def getFragmentObj(self, fragmentName=None):
        """Returns a fragment object of the model. A fragment is computed from
        a model by evaluating the expression `<model>.<fragmentName>`

        For a simple fragmentName (no dots), this is roughly equivalent to
        getattr(self, fragmentName)

        If the fragment cannot be computed, :class:`AttributeError` is raised

        :param fragmentName: (str or None) the returned value will correspond to
                         the given fragmentName. If None is passed the
                         defaultFragmentName will be used instead.

        :return: (obj) the computed fragment of the modelObj.
        """
        if fragmentName is None:
            fragmentName = self.defaultFragmentName
        try:
            return eval('obj.' + fragmentName, {}, {'obj' : self})
        except Exception as e:
            # Note: always raise AttributeError to comply with existing API
            msg = "Cannot get fragment of {!r}.{!s}: Reason: {!r}"
            raise AttributeError(msg.format(self, fragmentName, e))


    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # API for listeners
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    def _listenerDied(self, weak_listener):
        if self._listeners is None:
            return
        try:
            self._listeners.remove(weak_listener)
        except Exception as e:
            self.debug("Problem removing listener: %r", e)

    def _getCallableRef(self, listener, cb=None):
        # return weakref.ref(listener, self._listenerDied)
        meth = getattr(listener, 'eventReceived', None)
        if meth is not None and hasattr(meth, '__call__'):
            return weakref.ref(listener, cb)
        else:
            return CallableRef(listener, cb)

    def addListener(self, listener):
        if self._listeners is None or listener is None:
            return False

        # TODO: _BoundMethodWeakrefWithCall is used as workaround for
        # PyTango #185 issue
        weak_listener = self._getCallableRef(
            listener, _BoundMethodWeakrefWithCall(self._listenerDied))
            # listener, self._listenerDied)
        if weak_listener in self._listeners:
            return False
        self._listeners.append(weak_listener)
        return True

    def removeListener(self, listener):
        if self._listeners is None:
            return
        weak_listener = self._getCallableRef(listener)
        try:
            self._listeners.remove(weak_listener)
        except Exception as e:
            return False
        return True

    def forceListening(self):
        class __DummyListener(object):

            def eventReceived(self, *args):
                pass
        if not hasattr(self, '__dummyListener') or self.__dummyListener is None:
            self.__dummyListener = __DummyListener()
            self.addListener(self.__dummyListener)

    def unforceListening(self):
        if hasattr(self, '__dummyListener') and self.__dummyListener is not None:
            self.removeListener(self.__dummyListener)
            self.__dummyListener = None

    def deleteListener(self, listener):
        self.deprecated("Use removeListener(listener) instead")
        self.removeListener(listener)

    def hasListeners(self):
        """ returns True if anybody is listening to events from this attribute """
        if self._listeners is None:
            return False
        return len(self._listeners) > 0

    def fireEvent(self, event_type, event_value, listeners=None):
        """sends an event to all listeners or a specific one"""

        if listeners is None:
            listeners = self._listeners

        if listeners is None:
            return

        if not isinstance(listeners, Sequence):
            listeners = listeners,

        for listener in listeners:
            if isinstance(listener, weakref.ref) or isinstance(listener, BoundMethodWeakref):
                l = listener()
            else:
                l = listener
            if l is None:
                continue
            meth = getattr(l, 'eventReceived', None)
            if meth is not None and hasattr(meth, '__call__'):
                l.eventReceived(self, event_type, event_value)
            elif hasattr(l, '__call__'):
                l(self, event_type, event_value)

    def isWritable(self):
        return False

    @property
    def name(self):
        return self._simp_name

    @property
    def fullname(self):
        return self._full_name

    parentObj = property(fget=getParentObj)
