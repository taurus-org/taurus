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
simfactory.py: 

Simulation Factory uses the Taurus object naming (URI based):

  foo://username:password@example.com:8042/over/there/index.dtb;type=animal?name=ferret#nose
  \ /   \________________/\_________/ \__/\_________/ \___/ \_/ \_________/ \_________/ \__/
   |           |               |        |     |         |     |       |            |     |
scheme     userinfo         hostname  port  path  filename extension parameter(s) query fragment
        \________________________________/
                    authority
"""

from taurus import Factory
from taurus.core.taurusexception import TaurusException
from taurus.core.taurusbasetypes import OperationMode, MatchLevel, \
    TaurusAttrValue, TaurusEventType
from taurus.core.util.log import Logger
from taurus.core.util.singleton import Singleton
from taurus.core.taurusfactory import TaurusFactory
from taurus.core.taurusattribute import TaurusAttribute
from taurus.core.taurusdevice import TaurusDevice
from taurus.core.taurusdatabase import TaurusDatabase
from taurus.core.taurusconfiguration import TaurusConfiguration


class SimulationDatabase(TaurusDatabase):
    def factory(self):
        return SimulationFactory()
        
    def getElementAlias(self, full_name):
        return "abc"
        
    def getElementFullName(self, alias):
        return "a/b/c"
    
    def cache(self):
        return Factory('tango').getDatabase().cache()
        
    def __getattr__(self, name):
        return "SimulationDatabase object calling %s" % name
    
   
class SimulationDevice(TaurusDevice):
    def _createHWObject(self):
        return "Simulation"

    def getAttribute(self, attrname):
        return self._attr
    
    def factory(self):
        return SimulationFactory()

class D:
    pass
    
class SimulationConfiguration(TaurusConfiguration):
    
    def __init__(self, name, parent, storeCallback = None):
        i = D()
        i.name = "d"
        i.writable = 3
        i.data_format = 0
        i.data_type = 5
        i.max_dim_x = 1
        i.max_dim_y = 0
        i.description = "a bloody attribute, what else?"
        i.label = "Voltage"
        i.unit = "mV"
        i.standard_unit = "No standard unit"
        i.display_unit = "No display unit"
        i.format = "%6.2f"
        i.min_value = -2000
        i.max_value = 2000
        i.min_alarm = -1800
        i.max_alarm = 1800
        i.writable_attr_name = i.name
        i.extensions = []
        i.disp_level = 0
        i.alarms = D()
        i.alarms.min_alarm = -1800
        i.alarms.max_alarm = 1800
        i.alarms.min_warning = -1500
        i.alarms.max_warning = 1500
        i.alarms.delta_t = SimulationConfiguration.not_specified
        i.alarms.delta_val = SimulationConfiguration.not_specified
        i.climits = [i.min_value, i.max_value]
        i.calarms = [i.min_alarm, i.max_alarm]
        i.cwarnings = [i.alarms.min_warning, i.alarms.max_warning]
        i.cranges = [i.min_value, i.min_alarm, i.alarms.min_warning,
                    i.alarms.max_warning, i.max_alarm, i.max_value]
        # add dev_name, dev_alias, attr_name, attr_full_name
        attr = parent
        dev = attr.getParentObj()
        i.dev_name = dev.getNormalName()
        i.dev_alias = dev.getSimpleName()
        i.attr_name = attr.getSimpleName()
        i.attr_fullname = attr.getNormalName()
        self.attr_info = i
        self.call__init__(TaurusConfiguration, name, parent, storeCallback=storeCallback)

    def factory(self):
        return SimulationFactory()

    def getValueObj(self, cache=True):
        """ Returns the current configuration for the attribute.
            if cache is set to True (default) and the the configuration has 
            events active then it will return the local cached value. Otherwise
            it will read from the tango layer."""
        return self.attr_info
            
    def _subscribeEvents(self):
        pass
        
    def _unSubscribeEvents(self):
        pass
        
    def isWrite(self, cache=True):
        return False
    
    def isReadOnly(self, cache=True):
        return False

    def isReadWrite(self, cache=True):
        return True
    
    def isScalar(self, cache=True):
        return True
    
    def isSpectrum(self, cache=True):
        return False
    
    def isImage(self, cache=True):
        return False
    
    def encode(self, value):
        return value
    
    def decode(self, value):
        return value

    
class SimulationAttribute(TaurusAttribute):

    def __init__(self, name, parent, storeCallback = None):
        self._value = TaurusAttrValue()
        self._config = None
        self._value.value = 123.45
        self._value.w_value = 123.45
        self._value.quality = "ATTR_VALID"
        self._value.time_stamp = 1
        self.call__init__(TaurusAttribute, name, parent, storeCallback=storeCallback)
        
    def __getattr__(self,name):
        return getattr(self.getConfig(), name)

    def factory(self):
        return SimulationFactory()

    def isNumeric(self):
        return True
        
    def isBoolean(self):
        return False

    def getDisplayValue(self,cache=True):
        return str(self._value.value)

    def encode(self, value):
        return value

    def decode(self, attr_value):
        return attr_value

    def write(self, value, with_read=True):
        self._value = value
        if with_read: return self._value

    def read(self, cache=True):
        return self._value
        
    def _subscribeEvents(self):
        pass
        
    def _unSubscribeEvents(self):
        pass

    def _getRealConfig(self):
        if self._config is None:
            cfg_name = "%s?configuration" % self.getFullName()
            self._config = SimulationConfiguration(cfg_name, self)
        return self._config

    def getConfig(self):
        return self._getRealConfig()

    def addListener(self, listener):
        """ Add a TaurusListener object in the listeners list.
            If it is the first element and Polling is enabled starts the 
            polling mechanism.
            If the listener is already registered nothing happens."""
        ret = TaurusAttribute.addListener(self, listener)
        if not ret:
            return ret

        #fire a first configuration event
        cfg_val, val = self.getConfig().getValueObj(), self.read()
        self.fireEvent(TaurusEventType.Config, cfg_val, listener)
        #fire a first change event
        self.fireEvent(TaurusEventType.Change, val, listener)
        return ret

class SimulationFactory(Singleton, TaurusFactory, Logger):
    """A Singleton class designed to provide Simulation related objects."""

    schemes = ("simulation",)
    
    def __init__(self):
        """ Initialization. Nothing to be done here for now."""
        pass

    def init(self, *args, **kwargs):
        """Singleton instance initialization."""
        name = self.__class__.__name__
        self.call__init__(Logger, name)
        self.call__init__(TaurusFactory)
        
    def findObjectClass(self, absolute_name):
        """findObjectClass(string absolute_name) -> taurus.core.taurusmodel.TaurusModel subclass
           
        Obtain the class object corresponding to the given name.
           
        @param[in] absolute_name the object absolute name string

        @return a class object that should be a subclass of a taurus.core.taurusmodel.TaurusModel
        @throws TaurusException if the given name is invalid.
        """
        objType = None
        try:
            if SimulationDatabase.isValid(absolute_name, MatchLevel.NORMAL_COMPLETE):
                objType = SimulationDatabase 
            elif SimulationDevice.isValid(absolute_name, MatchLevel.NORMAL_COMPLETE):
                objType = SimulationDevice
            elif SimulationAttribute.isValid(absolute_name, MatchLevel.NORMAL_COMPLETE):
                objType = SimulationAttribute
            elif SimulationConfiguration.isValid(absolute_name, MatchLevel.NORMAL_COMPLETE):
                objType = SimulationConfiguration
        except Exception, e:
            self.debug("Not able to find Object class for %s" % absolute_name)
            self.traceback()
        return objType

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
        if not db_name is None:
            validator = SimulationDatabase.getNameValidator()
            params = validator.getParams(db_name)
            if params is None:
                raise TaurusException("Invalid database name %s." % db_name)
        
        if not hasattr(self, "_db"):
            self._db = SimulationDatabase("sim:01")
        return self._db

    def getDevice(self, dev_name):
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
        validator = SimulationDevice.getNameValidator()
        params = validator.getParams(dev_name)
        if params is None:
            raise TaurusException("Invalid device name %s." % dev_name)

        if not hasattr(self, "_dev"):
            db = self.getDatabase("sim:01")
            self._dev = SimulationDevice("sim:01/a/b/c", parent=db, storeCallback=self._storeDev)
        return self._dev
        
    def getAttribute(self, attr_name):
        """getAttribute(string attr_name) -> taurus.core.taurusattribute.TaurusAttribute

        Obtain the object corresponding to the given attribute name.
        If the corresponding attribute already exists, the existing instance
        is returned. Otherwise a new instance is stored and returned.

        @param[in] attr_name string attribute name
             
        @return a taurus.core.taurusattribute.TaurusAttribute object 
        @throws TaurusException if the given name is invalid.
        """
        validator = SimulationAttribute.getNameValidator()
        params = validator.getParams(attr_name)
        
        if params is None:
            raise TaurusException("Invalid attribute name %s." % attr_name)
        
        if not hasattr(self, "_attr"):
            dev = self.getDevice("sim:01/a/b/c")
            SimulationAttribute("sim:01/a/b/c/d", parent=dev, storeCallback=self._storeAttr)
        return self._attr

    def getConfiguration(self, param):
        """getConfiguration(param) -> taurus.core.taurusconfiguration.TaurusConfiguration

        Obtain the object corresponding to the given attribute or full name.
        If the corresponding configuration already exists, the existing instance
        is returned. Otherwise a new instance is stored and returned.

        @param[in] param taurus.core.taurusattribute.TaurusAttribute object or full configuration name
           
        @return a taurus.core.taurusattribute.TaurusAttribute object
        @throws TaurusException if the given name is invalid.
        """
        if isinstance(param, str):
            return self._getConfigurationFromName(param)
        return self._getConfigurationFromAttribute(param)

    def _getConfigurationFromName(self, name):
        validator = SimulationConfiguration.getNameValidator()
        params = validator.getParams(name)
                
        if params is None:
            raise taurus.core.taurusexception.TaurusException("Invalid configuration name %s." % name)

        if not hasattr(self, "_conf"):
            name = "sim:01/a/b/c/d?configuration"
            attr = self.getAttribute("sim:01/a/b/c/d")
            SimulationConfiguration(name, attr, storeCallback=self._storeConfig)
        return self._config
    
    def _getConfigurationFromAttribute(self, attr):
        if not hasattr(self, "_conf"):
            name = "sim:01/a/b/c/d?configuration"
            SimulationConfiguration(name, attr, storeCallback=self._storeConfig)
        return self._config
    
    def _storeDev(self, dev):
        self._dev = dev
    
    def _storeAttr(self, attr):
        self._attr = attr
        
    def _storeConfig(self, name, config):
        self._config = config