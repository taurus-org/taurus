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

"""
  This module provides the :class:`TaurusFactory` base class that any valid
  Factory in Taurus must inherit.
  
  The Factory objects are the basic block for building and interacting with a 
  given scheme in Taurus. They provide Taurus Element objects (TaurusAuthority, 
  TaurusDevice, TaurusAttribute or TaurusConfiguration) for a given taurus model
  name.
  
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

__all__ = ["TaurusFactory"]

__docformat__ = "restructuredtext"

from taurusbasetypes import TaurusElementType
from taurusauthority import TaurusAuthority
from taurusdevice import TaurusDevice
from taurusattribute import TaurusAttribute
from taurusconfiguration import TaurusConfiguration, TaurusConfigurationProxy

class TaurusFactory(object):
    """The base class for valid Factories in Taurus."""
    
    schemes = () # reimplement in derived classes to provide the supported sche
    caseSensitive = True # reimplement if your scheme is case insensitive 

    DefaultPollingPeriod = 3000
    
    def __init__(self):
        self._polling_period = self.DefaultPollingPeriod
        self.polling_timers = {}
        self._polling_enabled = True    
        
        import taurusmanager
        manager = taurusmanager.TaurusManager()
        self._serialization_mode = manager.getSerializationMode()

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
    # Methods that must be implemented by the specific Factory
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-  

    def getAuthority(self, name=None):
        """getAuthority(string db_name) -> taurus.core.taurusauthority.TaurusAuthority
           
        Obtain the object corresponding to the given authority name or the 
        default authority if db_name is None.
        If the corresponding authority object already exists, the existing 
        instance is returned. Otherwise a new instance is stored and returned.
           
        @param[in] db_name authority name string. It should be formed like: 
                           <scheme>://<authority>. If <scheme> is ommited then 
                           it will use the default scheme. if db_name is None, 
                           the default authority is used
                           
        @return a taurus.core.taurusauthority.TaurusAuthority object 
        @throws TaurusException if the given name is invalid.
        """
        raise NotImplementedError("getAuthority cannot be called for abstract" \
                           " TaurusFactory")

    def getDevice(self, dev_name, **kw):
        """getDevice(string dev_name) -> taurus.core.taurusdevice.TaurusDevice
           
        Obtain the object corresponding to the given device name. If the 
        corresponding device already exists, the existing instance is returned. 
        Otherwise a new instance is stored and returned.
           
        @param[in] dev_name the device name string. It should be formed like:
                            <scheme>://<authority>/<device name>. If <scheme> 
                            is ommited then it will use the default scheme. 
                            If authority is ommited then it will use the 
                            default authority for the scheme.
        
        @return a taurus.core.taurusdevice.TaurusDevice object 
        @throws TaurusException if the given name is invalid.
        """
        raise NotImplementedError("getDevice cannot be called for abstract" \
                           " TaurusFactory")

    def getAttribute(self, attr_name):
        """getAttribute(string attr_name) -> taurus.core.taurusattribute.TaurusAttribute

        Obtain the object corresponding to the given attribute name.
        If the corresponding attribute already exists, the existing instance
        is returned. Otherwise a new instance is stored and returned.

        @param[in] attr_name string attribute name
             
        @return a taurus.core.taurusattribute.TaurusAttribute object 
        @throws TaurusException if the given name is invalid.
        """
        raise NotImplementedError("getAttribute cannot be called for abstract" \
                           " TaurusFactory")

    def getAuthorityNameValidator(self):
        raise NotImplementedError("getAuthorityNameValidator cannot be called" \
                                  " for abstract TaurusFactory")

    def getDeviceNameValidator(self):
        raise NotImplementedError("getDeviceNameValidator cannot be called" \
                                  " for abstract TaurusFactory")

    def getAttributeNameValidator(self):
        raise NotImplementedError("getAttributeNameValidator cannot be called" \
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
        return scheme in self.shemes

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
                            rel='taurus 4', dbg_msg=t4_msg)
            return self.getAttribute(name)
        elif issubclass(cls, TaurusConfigurationProxy):
            self.deprecated(dep='TaurusConfigurationProxy',
                            alt='TaurusAttribute',
                            rel='taurus 4', dbg_msg=t4_msg)
            return self.getAttribute(name)
        else:
            return None

    def changeDefaultPollingPeriod(self, period):
        if period > 0:
            self._polling_period = period

    def getDefaultPollingPeriod(self):
        return self._polling_period
    
    def isPollingEnabled(self):
        """Tells if the local tango polling is enabled
        
           :return: (bool) wheter or not the polling is enabled
        """
        return self._polling_enabled
        
    def disablePolling(self):
        """Disable the application tango polling"""
        if not self.isPollingEnabled():
            return
        self._polling_enabled = False
        for period,timer in self.polling_timers.iteritems():
            timer.stop()
            
    def enablePolling(self):
        """Enable the application tango polling"""
        if self.isPollingEnabled():
            return
        for period,timer in self.polling_timers.iteritems():
            timer.start()
        self._polling_enabled = True
        
    def addAttributeToPolling(self, attribute, period, unsubscribe_evts = False):
        """Activates the polling (client side) for the given attribute with the
           given period (seconds).

           :param attribute: (taurus.core.tango.TangoAttribute) attribute name.
           :param period: (float) polling period (in seconds)
           :param unsubscribe_evts: (bool) whether or not to unsubscribe from events
        """
        raise NotImplementedError("addAttributeToPolling cannot be called" \
                                  " for abstract TaurusFactory")
        
    def removeAttributeFromPolling(self, attribute):
        """Deactivate the polling (client side) for the given attribute. If the
           polling of the attribute was not previously enabled, nothing happens.

           :param attribute: (str) attribute name.
        """
        raise NotImplementedError("removeAttributeFromPolling cannot be" \
                                  " called for abstract TaurusFactory")

    def __str__(self):
        return '{0}()'.format(self.__class__.__name__)

    def __repr__(self):
        return '{0}(schemes={1})'.format(self.__class__.__name__, ", ".join(self.schemes))
    
    def getValidTypesForName(self, name, strict=None):
        '''
        Returns a list of all Taurus element types for which `name` is a valid 
        model name (while in many cases a name may only be valid for one 
        element type, this is not necessarily true in general)
        
        In this base implementation, name is checked first for Configuration, 
        then for Attribute, then for Device and finally for Authority, and the 
        return value is sorted in that same order.
        
        If a given schema requires a different ordering, reimplement this method
        
        :param name: (str) taurus model name
        
        :return: (list<TaurusElementType.element>) where element can be one of:
                 `Configuration`, `Attribute`, `Device` or `Authority` 
        '''
        ret = []
        if self.getAttributeNameValidator().isValid(name, strict=strict):
            ret.append(TaurusElementType.Attribute)
        if self.getDeviceNameValidator().isValid(name, strict=strict):
            ret.append(TaurusElementType.Device)
        if self.getAuthorityNameValidator().isValid(name, strict=strict):
            ret.append(TaurusElementType.Authority)
        return ret
    
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
                                 TaurusElementType.Configuration: FooConfiguration
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
