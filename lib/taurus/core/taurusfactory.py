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

"""
  This module provides the :class:`TaurusFactory` base class that any valid
  Factory in Taurus must inherit.

  The Factory objects are the basic block for building and interacting with a
  given scheme in Taurus. They provide Taurus model objects (TaurusAuthority,
  TaurusDevice or TaurusAttribute) for a given taurus model name.

  Taurus model naming is URI based (see <https://tools.ietf.org/html/rfc3986>)

  All the standard components of an URI (scheme, authority, path, query and
  fragment) may be part of a model name, and they are separated as follows:

  <scheme>:<authority><path>?<query>#<fragment>


  The following are some points to consider when using and/or implementing
  schemes based on this Abstract class:

  - It is strongly recommended that the scheme component is always present
  explicitly in the model name, although a default scheme can be defined in
  :mod:`taurus.tauruscustomsettings` so that model names which do not explicit
  the scheme can be auto-completed.

  - The authority component (if present on a given name) must always begin by
  a double slash ('//'). (see
  <https://tools.ietf.org/html/rfc3986#section-3.2>)

  - The path component, if present, must start by a single slash ('/') (see
  <https://tools.ietf.org/html/rfc3986#section-3.3>)

"""
from __future__ import absolute_import
from builtins import object

import atexit
from weakref import WeakValueDictionary
from .taurusbasetypes import TaurusElementType
from .taurusauthority import TaurusAuthority
from .taurusdevice import TaurusDevice
from .taurusattribute import TaurusAttribute
from .taurusconfiguration import TaurusConfiguration, TaurusConfigurationProxy
from .taurusexception import TaurusException
from taurus.core.tauruspollingtimer import TaurusPollingTimer

__all__ = ["TaurusFactory"]

__docformat__ = "restructuredtext"


class TaurusFactory(object):
    """The base class for valid Factories in Taurus."""

    schemes = ()  # reimplement in derived classes to declare supported schemes
    caseSensitive = True  # reimplement if your scheme is case insensitive

    elementTypesMap = None  # reimplement in derived classes to profit from
                            # generic implementations of getAuthority,
                            # getDevice, getAttribute, findObjectClass, etc.
                            # see findObjectClass for more details

    DefaultPollingPeriod = 3000

    def __init__(self):
        atexit.register(self.cleanUp)
        self._polling_period = self.DefaultPollingPeriod
        self.polling_timers = {}
        self._polling_enabled = True
        self._attrs = WeakValueDictionary()
        self._devs = WeakValueDictionary()
        self._auths = WeakValueDictionary()

        from . import taurusmanager
        manager = taurusmanager.TaurusManager()
        self._serialization_mode = manager.getSerializationMode()

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # API for cleanUp at exit
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    def cleanUp(self):
        """Reimplement if you need to execute code on program execution exit.
        Default implementation does nothing.
        """
        pass

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # API for serialization
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    def setSerializationMode(self, mode):
        """Sets the serialization mode for the system.

        :param mode: (TaurusSerializationMode) the new serialization mode
        """
        self._serialization_mode = mode

    def getSerializationMode(self):
        """Gives the serialization operation mode.

        :return: (TaurusSerializationMode) the current serialization mode
        """
        return self._serialization_mode

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # API to get objects. Generic implementation. You may want to reimplement
    # it in your scheme factory
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    def getAuthority(self, name=None):
        """Obtain the model object corresponding to the given authority name.
        If the corresponding authority already exists, the existing instance
        is returned. Otherwise a new instance is stored and returned.

        :param name: (str) authority name

        :return: a taurus.core.taurusauthority.TaurusAuthority object
        :raises: :TaurusException: if the given name is invalid.
        """
        v = self.getAuthorityNameValidator()
        if not v.isValid(name):
            msg = "Invalid {scheme} authority name '{name}'".format(
                    scheme=self.schemes[0], name=name)
            raise TaurusException(msg)

        fullname, _, _ = v.getNames(name)
        auth = self._auths.get(fullname)
        if auth is not None:
            return auth

        cls = self.elementTypesMap[TaurusElementType.Authority]
        auth = cls(name=fullname)
        self._auths[fullname] = auth
        return auth

    def getDevice(self, name, **kw):
        """Obtain the model object corresponding to the given device name.
        If the corresponding device already exists, the existing instance
        is returned. Otherwise a new instance is stored and returned.

        :param name: (str) device name

        :return: a taurus.core.taurusdevice.TaurusDevice object
        :raises: :TaurusException: if the given name is invalid.
        """
        v = self.getDeviceNameValidator()
        if not v.isValid(name):
            msg = "Invalid {scheme} device name '{name}'".format(
                    scheme=self.schemes[0], name=name)
            raise TaurusException(msg)

        fullname, _, _ = v.getNames(name)
        dev = self._devs.get(fullname)
        if dev is not None:
            return dev

        try:
            # this works if the authority name is present in the dev full name
            # (which in principle should always be the case)
            authname = v.getUriGroups(fullname)['authority']
            auth = self.getAuthority(authname)
        except:
            self.debug('Cannot get device parent from name "%s"', fullname)
            auth = None

        cls = self.elementTypesMap[TaurusElementType.Device]
        dev = cls(name=fullname, parent=auth)
        self._devs[fullname] = dev
        return dev

    def getAttribute(self, name):
        """ Obtain the model object corresponding to the given attribute name.
        If the corresponding attribute already exists, the existing instance
        is returned. Otherwise a new instance is stored and returned.

        :param name: (str) attribute name

        :return: a taurus.core.taurusattribute.TaurusAttribute object
        :raises: :TaurusException: if the given name is invalid.
        """
        v = self.getAttributeNameValidator()
        if not v.isValid(name):
            msg = "Invalid {scheme} attribute name '{name}'".format(
                    scheme=self.schemes[0], name=name)
            raise TaurusException(msg)

        fullname, _, _ = v.getNames(name)
        attr = self._attrs.get(fullname)
        if attr is not None:
            return attr

        try:
            # this works only if the devname is present in the attr full name
            # (not all schemes are constructed in this way)
            devname = v.getUriGroups(fullname)['devname']
            dev = self.getDevice(devname)
        except:
            self.debug('Cannot get attribute parent from name "%s"', fullname)
            dev = None

        cls = self.elementTypesMap[TaurusElementType.Attribute]
        attr = cls(name=fullname, parent=dev)
        self._attrs[fullname] = attr
        return attr

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # Methods that must be implemented by the specific Factory
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    def getAuthorityNameValidator(self):
        raise NotImplementedError("getAuthorityNameValidator cannot be called"
                                  " for abstract TaurusFactory")

    def getDeviceNameValidator(self):
        raise NotImplementedError("getDeviceNameValidator cannot be called"
                                  " for abstract TaurusFactory")

    def getAttributeNameValidator(self):
        raise NotImplementedError("getAttributeNameValidator cannot be called"
                                  " for abstract TaurusFactory")

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # Factory extension API
    # Override the following methods if you need to provide special classes for
    # special object types
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    def registerAttributeClass(self, attr_name, attr_klass):
        pass

    def unregisterAttributeClass(self, attr_name):
        pass

    def registerDeviceClass(self, dev_klass_name, dev_klass):
        pass

    def unregisterDeviceClass(self, dev_klass_name):
        pass

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # Generic methods
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    def supportsScheme(self, scheme):
        """Returns whether the given scheme is supported by this factory

        :param scheme: (str) the name of the schem to be checked

        :return: (bool) True if the scheme is supported (False otherwise)
        """
        return scheme in self.schemes

    def findObject(self, absolute_name):
        """ Must give an absolute name"""
        if not absolute_name:
            return None
        obj = None
        cls = self.findObjectClass(absolute_name)
        if cls:
            obj = self.getObject(cls, absolute_name)
        return obj

    def getObject(self, cls, name):
        t4_msg = 'The TaurusConfiguration classes are deprecated in tep14'
        if issubclass(cls, TaurusAuthority):
            return self.getAuthority(name)
        elif issubclass(cls, TaurusDevice):
            return self.getDevice(name)
        elif issubclass(cls, TaurusAttribute):
            return self.getAttribute(name)
        # For backward compatibility
        elif issubclass(cls, TaurusConfiguration):
            self.deprecated(dep='TaurusConfiguration', alt='TaurusAttribute',
                            rel='4.0', dbg_msg=t4_msg)
            return self.getAttribute(name)
        elif issubclass(cls, TaurusConfigurationProxy):
            self.deprecated(dep='TaurusConfigurationProxy',
                            alt='TaurusAttribute',
                            rel='4.0', dbg_msg=t4_msg)
            return self.getAttribute(name)
        else:
            return None

    def changeDefaultPollingPeriod(self, period):
        if period > 0:
            self._polling_period = period

    def getDefaultPollingPeriod(self):
        return self._polling_period

    def isPollingEnabled(self):
        """Tells if the Taurus polling is enabled

           :return: (bool) whether or not the polling is enabled
        """
        return self._polling_enabled

    def disablePolling(self):
        """Disable the application tango polling"""
        if not self.isPollingEnabled():
            return
        self._polling_enabled = False
        for period, timer in self.polling_timers.items():
            timer.stop()

    def enablePolling(self):
        """Enable the application tango polling"""
        if self.isPollingEnabled():
            return
        for period, timer in self.polling_timers.items():
            timer.start()
        self._polling_enabled = True

    def addAttributeToPolling(self, attribute, period, unsubscribe_evts=False):
        """Activates the polling (client side) for the given attribute with the
           given period (seconds).

           :param attribute: (taurus.core.taurusattribute.TaurusAttribute)
                             the attribute to be added
           :param period: (float) polling period (in seconds)
           :param unsubscribe_evts: (bool) whether or not to unsubscribe from events
        """
        tmr = self.polling_timers.get(period, TaurusPollingTimer(period))
        self.polling_timers[period] = tmr
        tmr.addAttribute(attribute, self.isPollingEnabled())

    def removeAttributeFromPolling(self, attribute):
        """Deactivate the polling (client side) for the given attribute. If the
           polling of the attribute was not previously enabled, nothing happens.

           :param attribute: (taurus.core.taurusattribute.TaurusAttribute)
                             the attribute to be removed
        """
        timers = dict(self.polling_timers)
        for period, timer in timers.items():
            timer.removeAttribute(attribute)
            if not timer.dev_dict and period in self.polling_timers:
                del self.polling_timers[period]

    def __str__(self):
        return '{0}()'.format(self.__class__.__name__)

    def __repr__(self):
        return '{0}(schemes={1})'.format(self.__class__.__name__, ", ".join(self.schemes))

    def getValidTypesForName(self, name, strict=None):
        '''
        Returns a list of all Taurus element types for which `name` is a valid
        model name (while in many cases a name may only be valid for one
        element type, this is not necessarily true in general)

        In this base implementation, name is checked first for Attribute, then
        for Device and finally for Authority, and the return value is sorted in
        that same order.

        If a given schema requires a different ordering, reimplement this method

        :param name: (str) taurus model name

        :return: (list<TaurusElementType.element>) where element can be one of:
                 `Attribute`, `Device` or `Authority`
        '''
        ret = []
        if self.getAttributeNameValidator().isValid(name, strict=strict):
            ret.append(TaurusElementType.Attribute)
        if self.getDeviceNameValidator().isValid(name, strict=strict):
            ret.append(TaurusElementType.Device)
        if self.getAuthorityNameValidator().isValid(name, strict=strict):
            ret.append(TaurusElementType.Authority)
        return ret

    def getValidatorFromName(self, name):
        """
        Obtain the validator object corresponding to the given model
        name. If the model name is not valid for any TaurusModel class,
        it returns None
        """
        modeltypes = self.getValidTypesForName(name)
        if not modeltypes:
            return None
        return self.elementTypesMap[modeltypes[0]].getNameValidator()

    def findObjectClass(self, absolute_name):
        """
        Obtain the class object corresponding to the given name.

        Note, this generic implementation expects that derived classes provide a
        an attribute called elementTypesMap consisting in a dictionary whose
        keys are TaurusElementTypes and whose values are the corresponding
        specific object classes. e.g., the FooFactory should provide::

          class FooFactory(TaurusFactory):
              elementTypesMap = {TaurusElementType.Authority: FooAuthority,
                                 TaurusElementType.Device: FooDevice,
                                 TaurusElementType.Attribute: FooAttribute,
                                 }
              (...)


        :param absolute_name: (str) the object absolute name string

        :return: (taurus.core.taurusmodel.TaurusModel or None) a TaurusModel
                 class derived type or None if the name is not valid

        """
        try:
            elementTypesMap = self.elementTypesMap
        except AttributeError:
            msg = ('generic findObjectClass called but %s does ' +
                   'not define elementTypesMap.') % self.__class__.__name__
            raise RuntimeError(msg)
        for t in self.getValidTypesForName(absolute_name):
            ret = elementTypesMap.get(t, None)
            if ret is not None:
                return ret
        return None
