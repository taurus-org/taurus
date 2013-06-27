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

"""
  The TaurusFactory model containning the abstract base class that any valid
  Factory in Taurus must inherit.
  
  Taurus object naming is URI based:

  foo://username:password@example.com:8042/over/there/index.dtb;type=animal?name=ferret#nose
  \ /   \________________/\_________/ \__/\_________/ \___/ \_/ \_________/ \_________/ \__/
   |           |               |        |     |         |     |       |            |     |
scheme     userinfo         hostname  port  path  filename extension parameter(s) query fragment
        \________________________________/
                    authority
"""

__all__ = ["TaurusFactory"]

__docformat__ = "restructuredtext"

from .taurusbasetypes import OperationMode
from .taurusdatabase import TaurusDatabase
from .taurusdevice import TaurusDevice
from .taurusattribute import TaurusAttribute
from .taurusconfiguration import TaurusConfiguration, TaurusConfigurationProxy

class TaurusFactory(object):
    """The base class for valid Factories in Taurus."""
    
    schemes = ()

    DefaultPollingPeriod = 3000
    
    def __init__(self):
        self._polling_period = self.DefaultPollingPeriod
        self.operation_mode = OperationMode.ONLINE
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

    def findObjectClass(self, absolute_name):
        """findObjectClass(string absolute_name) -> taurus.core.taurusmodel.TaurusModel subclass
           
        Obtain the class object corresponding to the given name.
           
        @param[in] absolute_name the object absolute name string

        @return a class object that should be a subclass of a taurus.core.taurusmodel.TaurusModel
        @throws TaurusException if the given name is invalid.
        """
        raise RuntimeError("findObjectClass cannot be called for abstract" \
                           " TaurusFactory")

    def getDatabase(self, db_name=None):
        """getDatabase(string db_name) -> taurus.core.taurusdatabase.TaurusDatabase
           
        Obtain the object corresponding to the given database name or the 
        default database if db_name is None.
        If the corresponding database object already exists, the existing 
        instance is returned. Otherwise a new instance is stored and returned.
           
        @param[in] db_name database name string. It should be formed like: 
                           <scheme>://<authority>. If <scheme> is ommited then 
                           it will use the default scheme. if db_name is None, 
                           the default database is used
                           
        @return a taurus.core.taurusdatabase.TaurusDatabase object 
        @throws TaurusException if the given name is invalid.
        """
        raise RuntimeError("getDatabase cannot be called for abstract" \
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
        raise RuntimeError("getDevice cannot be called for abstract" \
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
        raise RuntimeError("getAttribute cannot be called for abstract" \
                           " TaurusFactory")

    def getConfiguration(self, param):
        """getConfiguration(param) -> taurus.core.taurusconfiguration.TaurusConfiguration

        Obtain the object corresponding to the given attribute or full name.
        If the corresponding configuration already exists, the existing instance
        is returned. Otherwise a new instance is stored and returned.

        @param[in] param taurus.core.taurusattribute.TaurusAttribute object or full configuration name
           
        @return a taurus.core.taurusattribute.TaurusAttribute object
        @throws TaurusException if the given name is invalid.
        """
        raise RuntimeError("getConfiguration cannot be called for abstract" \
                           " TaurusFactory")

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
        return scheme in self.shemes

    def setOperationMode(self, mode):
        """ setOperationMode(OperationMode mode) -> None
            Sets the operation mode for the Tango system."""
        self.operation_mode = mode
        
    def getOperationMode(self):
        return self.operation_mode

    def findObject(self, absolute_name):
        """ Must give an absolute name"""
        if self.operation_mode == OperationMode.OFFLINE or not absolute_name:
            return None
        obj = None
        cls = self.findObjectClass(absolute_name)
        if cls:
            obj = self.getObject(cls, absolute_name)
        return obj

    def getObject(self, cls, name):
        if issubclass(cls, TaurusDatabase):
            return self.getDatabase(name)
        elif issubclass(cls, TaurusDevice):
            return self.getDevice(name)
        elif issubclass(cls, TaurusAttribute):
            return self.getAttribute(name)
        elif issubclass(cls, TaurusConfiguration):
            return self.getConfiguration(name)
        elif issubclass(cls, TaurusConfigurationProxy):
            return self.getConfiguration(name)
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
        raise RuntimeError("addAttributeToPolling cannot be called for abstract" \
                           " TaurusFactory")
        
    def removeAttributeFromPolling(self, attribute):
        """Deactivate the polling (client side) for the given attribute. If the
           polling of the attribute was not previously enabled, nothing happens.

           :param attribute: (str) attribute name.
        """
        raise RuntimeError("removeAttributeFromPolling cannot be called for abstract" \
                           " TaurusFactory")

    def __str__(self):
        return '{0}()'.format(self.__class__.__name__)

    def __repr__(self):
        return '{0}(schemes={1})'.format(self.__class__.__name__, ", ".join(self.schemes))
