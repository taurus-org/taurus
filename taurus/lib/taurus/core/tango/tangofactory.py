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

"""This module contains all taurus tango attribute configuration"""

__all__ = ["TangoFactory"]

__docformat__ = "restructuredtext"

import sys
import os
import threading
import PyTango

from taurus.core.taurusfactory import TaurusFactory
from taurus.core.taurusbasetypes import OperationMode, MatchLevel
from taurus.core.taurusexception import TaurusException, DoubleRegistration
from taurus.core.tauruspollingtimer import TaurusPollingTimer
from taurus.core.util.enumeration import Enumeration
from taurus.core.util.log import Logger
from taurus.core.util.singleton import Singleton
from taurus.core.util.containers import CaselessWeakValueDict, CaselessDict

from .tangodatabase import TangoDatabase, InvalidAlias
from .tangoattribute import TangoAttribute, TangoStateAttribute
from .tangodevice import TangoDevice
from .tangoconfiguration import TangoConfiguration

_Database = TangoDatabase
_Attribute = TangoAttribute
_StateAttribute = TangoStateAttribute
_Device = TangoDevice
_Configuration = TangoConfiguration


class TangoFactory(Singleton, TaurusFactory, Logger):
    """A Singleton class designed to provide Tango related objects.

      The TangoFactory model containning the Factory for the Tango scheme
      
      Tango Factory uses the Taurus object naming (URI based)::

          foo://username:password@example.com:8042/over/there/index.dtb;type=animal?name=ferret#nose
          \_/   \________________/\_________/ \__/\_________/ \___/ \_/ \_________/ \_________/ \__/
           |            |              |       |       |        |    |       |            |      |
          scheme     userinfo      hostname   port   path filename extension parameter(s) query fragment
                    \____________________________/
                                |
                             authority

    For Tango:
    
        - The 'scheme' must be the string "tango" (lowercase mandatory)
        - The 'authority' is the Tango database (<hostname> and <port> mandatory)
        - The 'path' is the Tango object, which can be a Device or Attribute.
          For device it must have the format _/_/_ or alias 
          For attribute it must have the format _/_/_/_ or devalias/_
        - The 'filename' and 'extension' are always empty
        - The 'parameter' is always empty
        - The 'the query' is valid when the 'path' corresponds to an Attribute. Valid
          queries must have the format configuration=<config param>. Valid 
          configuration parameters are: label, format, description, unit, display_unit, 
          standard_unit, max_value, min_value, max_alarm, min_alarm, 
          max_warning, min_warning. in this case the Tango object is a Configuration
    """
    
    #: the list of schemes that this factory supports. For this factory: 'tango' 
    #: is the only scheme
    schemes = ("tango",)
    
    def __init__(self):
        """ Initialization. Nothing to be done here for now."""
        pass

    def init(self, *args, **kwargs):
        """Singleton instance initialization.
           **For internal usage only**"""
        name = self.__class__.__name__
        self.call__init__(Logger, name)
        self.call__init__(TaurusFactory)
        self._polling_enabled = True
        self.reInit()

    def reInit(self):
        """Reinitialize the singleton"""
        self._default_tango_host = None
        self.operation_mode = OperationMode.ONLINE
        self.dft_db = None
        self.tango_db = CaselessWeakValueDict()
        self.tango_db_queries = CaselessWeakValueDict()
        self.tango_configs = CaselessWeakValueDict()
        self.tango_attrs = CaselessWeakValueDict()
        self.tango_devs = CaselessWeakValueDict()
        self.tango_dev_queries = CaselessWeakValueDict()
        self.tango_alias_devs = CaselessWeakValueDict()
        self.polling_timers = {}
        
        # Plugin device classes
        self.tango_dev_klasses = {}
        
        # Plugin attribute classes
        self.tango_attr_klasses = CaselessDict()
        self.tango_attr_klasses["state"] = _StateAttribute

    def cleanUp(self):
        """Cleanup the singleton instance"""
        self.trace("[TangoFactory] cleanUp")
        for k,v in self.tango_attrs.items():       v.cleanUp()
        for k,v in self.tango_configs.items():     v.cleanUp()
        for k,v in self.tango_dev_queries.items(): v.cleanUp()
        for k,v in self.tango_devs.items():        v.cleanUp()
        self.dft_db = None
        for k,v in self.tango_db_queries.items():  v.cleanUp()
        for k,v in self.tango_db.items():          v.cleanUp()
        self.reInit()

    def getExistingAttributes(self):
        """Returns a new dictionary will all registered attributes on this factory
           
           :return:  dictionary will all registered attributes on this factory
           :rtype: dict"""
        return dict(self.tango_attrs)

    def getExistingDevices(self):
        """Returns a new dictionary will all registered devices on this factory
           
           :return:  dictionary will all registered devices on this factory
           :rtype: dict"""
        return dict(self.tango_devs)

    def getExistingDatabases(self):
        """Returns a new dictionary will all registered databases on this factory
           
           :return:  dictionary will all registered databases on this factory
           :rtype: dict"""
        return dict(self.tango_db)

    def getExistingConfigurations(self):
        """Returns a new dictionary will all registered configurations on this factory
           
           :return:  dictionary will all registered configurations on this factory
           :rtype: dict"""
        return dict(self.tango_configs)

    def set_default_tango_host(self, tango_host):
        """Sets the new default tango host.
        
        :param tango_host: (str) the new tango host
        """
        self._default_tango_host = tango_host
        self.dft_db = None

    def registerAttributeClass(self, attr_name, attr_klass):
        """Registers a new attribute class for the attribute name.
           
           :param attr_name: (str) attribute name
           :param attr_klass: (taurus.core.tango.TangoAttribute) the new class that 
                              will handle the attribute
        """
        self.tango_attr_klasses[attr_name] = attr_klass
    
    def unregisterAttributeClass(self, attr_name):
        """Unregisters the attribute class for the given attribute
           If no class was registered before for the given attribute, this call
           as no effect
           
           :param attr_name: (str) attribute name
        """
        if self.tango_attr_klasses.has_key(attr_name):
            del self.tango_attr_klasses[attr_name]
            
    def registerDeviceClass(self, dev_klass_name, dev_klass):
        """Registers a new python class to handle tango devices of the given tango class name
        
           :param dev_klass_name: (str) tango device class name
           :param dev_klass: (taurus.core.tango.TangoDevice) the new class that will
                             handle devices of the given tango class name
        """
        self.tango_dev_klasses[dev_klass_name] = dev_klass
    
    def unregisterDeviceClass(self, dev_klass_name):
        """Unregisters the class for the given tango class name
           If no class was registered before for the given attribute, this call
           as no effect
           
           :param dev_klass_name: (str) tango device class name
        """
        if self.tango_dev_klasses.has_key(dev_klass_name):
            del self.tango_dev_klasses[dev_klass_name]

    def findObjectClass(self,absolute_name):
        """
        Obtain the class object corresponding to the given name.
           
        :param absolute_name: (str) the object absolute name string

        :return: (taurus.core.taurusmodel.TaurusModel) a class object that should be a subclass of a taurus.core.taurusmodel.TaurusModel
        :raise: (taurus.core.taurusexception.TaurusException) if the given name is invalid.
        """
        objType = None
        try:
            if _Database.isValid(absolute_name, MatchLevel.NORMAL_COMPLETE):
                objType = _Database 
            elif _Device.isValid(absolute_name, MatchLevel.NORMAL_COMPLETE):
                objType = _Device
            elif _Attribute.isValid(absolute_name, MatchLevel.NORMAL_COMPLETE):
                objType = _Attribute
            elif _Configuration.isValid(absolute_name, MatchLevel.NORMAL_COMPLETE):
                objType = _Configuration
            elif _Database.isValid(absolute_name, MatchLevel.SHORT):
                objType = _Database 
            elif _Device.isValid(absolute_name, MatchLevel.SHORT):
                objType = _Device
            elif _Attribute.isValid(absolute_name, MatchLevel.SHORT):
                objType = _Attribute
            elif _Configuration.isValid(absolute_name, MatchLevel.SHORT):
                objType = _Configuration
        except:
            self.debug("Not able to find Object class for %s" % absolute_name, exc_info=1)
        return objType

    def getDatabase(self, db_name = None):
        """
        Obtain the object corresponding to the given database name or the 
        default database if db_name is None.
        If the corresponding database object already exists, the existing 
        instance is returned. Otherwise a new instance is stored and returned.
           
        :param db_name: (str) database name string alias. If None, the 
                        default database is used
                           
        :return: (taurus.core.tangodatabase.TangoDatabase) database object
        :raise: (taurus.core.taurusexception.TaurusException) if the given alias is invalid.
        """
        ret = None
        if db_name is None:
            if self.dft_db is None:
                try:
                    if self._default_tango_host is None:
                        self.dft_db = _Database()
                    else:
                        db_name = self._default_tango_host
                        validator = _Database.getNameValidator()
                        params = validator.getParams(db_name)
                        if params is None:
                            raise TaurusException("Invalid default Tango database name %s" % db_name)
                        host, port = params.get('host'),params.get('port')
                        self.dft_db = _Database(host,port)
                except:
                    self.debug("Could not create Database", exc_info=1)
                    raise
                db_name = self.dft_db.getFullName()
                self.tango_db[db_name] = self.dft_db
            ret = self.dft_db
        else:
            ret = self.tango_db.get(db_name)
            if not ret is None:
                return ret
            validator = _Database.getNameValidator()
            params = validator.getParams(db_name)
            if params is None:
                raise TaurusException("Invalid Tango database name %s" % db_name)
            host, port = params.get('host'),params.get('port')
            try:
                ret = _Database(host,port)
            except:
                self.debug("Could not create Database %s:%s", host, port, exc_info=1)
            
            self.tango_db[db_name] = ret
        return ret 

    def getDevice(self,dev_name,**kw):
        """Obtain the object corresponding to the given tango device name.
           If the corresponding device already exists, the existing instance
           is returned. Otherwise a new instance is stored and returned.
           
           :param dev_name: (str) tango device name or tango alias for the device.
                            It should be formed like: <host>:<port>/<tango device name>
                            - If <host>:<port> is ommited then it will use the 
                            default database.
                            - <tango device name> can be full tango device name 
                            (_/_/_) or a device alias.
             
           :return: (taurus.core.tango.TangoDevice) a device object 
           :raise: (taurus.core.taurusexception.TaurusException) if the given dev_name is invalid.
        """
        d = self.tango_devs.get(dev_name)
        if d is None:
            d = self.tango_alias_devs.get(dev_name)
        if d is not None:
            return d
        
        # Simple approach did not work. Lets build a proper device name
        if dev_name.lower().startswith("tango://"):
            dev_name = dev_name[8:]
        
        validator = _Device.getNameValidator()
        params = validator.getParams(dev_name)
        
        if params is None:
            raise TaurusException("Invalid Tango device name '%s'" % dev_name)
        
        host,port = params.get('host'),params.get('port')
        db = None
        if host is None or port is None:
            db = self.getDatabase()
            host, port = db.get_db_host(), db.get_db_port()
        else:
            db_name = "%s:%s" % (host,port)
            db = self.getDatabase(db_name)
            
        dev_name = params.get('devicename')
        alias = params.get('devalias')
        
        if dev_name:
            try:
                alias = db.get_alias(dev_name)
                if alias and alias.lower() == InvalidAlias:
                    alias = None 
            except:
                alias = None
        else:
            try:
                dev_name = db.get_device_alias(alias)
            except:
                raise TaurusException("Device %s is not defined in %s." % (alias,db.getFullName()))

        full_dev_name = db.getFullName() + "/" + dev_name
        if not alias is None:
            alias = db.getFullName() + "/" + alias
        
        d = self.tango_devs.get(full_dev_name)
        
        if d is None:
            try:
                dev_klass = self._getDeviceClass(db=db, dev_name=dev_name)
                kw['storeCallback'] = self._storeDevice
                kw['parent'] = db
                d = dev_klass(full_dev_name, **kw)
                # device objects will register themselves in this factory
                # so there is no need to do it here
            except DoubleRegistration:
                d = self.tango_devs.get(full_dev_name)
            except:
                self.debug("Error creating device %s", dev_name, exc_info=1)
                raise
        return d

    def getAttribute(self,attr_name, **kwargs):
        """Obtain the object corresponding to the given attribute name.
           If the corresponding attribute already exists, the existing instance
           is returned. Otherwise a new instance is stored and returned.

           :param attr_name: (str) attribute name
                 
           :return: (taurus.core.tangoattribute.TangoAttribute) attribute object
           :raise: (taurus.core.taurusexception.TaurusException) if the given alias is invalid.
        """
        attr = self.tango_attrs.get(attr_name)

        if not attr is None:
            return attr
        
        # Simple approach did not work. Lets build a proper device name
        if attr_name.lower().startswith("tango://"):
            attr_name = attr_name[8:]
        validator = _Attribute.getNameValidator()
        params = validator.getParams(attr_name)
        
        if params is None:
            raise TaurusException("Invalid Tango attribute name '%s'" % attr_name)
        
        host,port = params.get('host'),params.get('port')
        
        db = None
        if host is None or port is None:
            db = self.getDatabase()
            host, port = db.get_db_host(), db.get_db_port()
        else:
            db_name = "%s:%s" % (host,port)
            db = self.getDatabase(db_name)
        
        dev_name = params.get('devicename')
        
        if dev_name is None:
            dev = self.getDevice(params.get('devalias'))
            dev_name = dev.getFullName()
        else:
            dev_name = db.getFullName() + "/" + dev_name

        attr_name = params.get('attributename')
        full_attr_name = dev_name + "/" + attr_name
         
        attr = self.tango_attrs.get(full_attr_name)
        
        if attr is None:
            try:
                dev = self.getDevice(dev_name)
                if dev is not None:
                    # Do another try in case the Device object created the attribute
                    # itself. This happens for the 'state' attribute
                    attr = self.tango_attrs.get(full_attr_name)
                    if attr is not None:
                        return attr
                    try:
                        attr_klass = self._getAttributeClass(attr_name=attr_name)
                        kwargs['storeCallback'] = self._storeAttribute
                        if not kwargs.has_key('pollingPeriod'):
                            kwargs['pollingPeriod'] = self.getDefaultPollingPeriod()
                        attr = attr_klass(full_attr_name, dev, **kwargs)
                        # attribute objects will register themselves in this factory
                        # so there is no need to do it here
                    except DoubleRegistration:
                        attr = self.tango_attrs.get(full_attr_name)
            except:
                self.debug("Error creating attribute %s", attr_name, exc_info=1)
                raise
        return attr

    def getAttributeInfo(self,full_attr_name):
        """Deprecated: Use :meth:`taurus.core.tango.TangoFactory.getConfiguration` instead.

           Obtain attribute information corresponding to the given attribute name.
           If the corresponding attribute info already exists, the existing information
           is returned. Otherwise a new information instance is stored and returned.

           :param full_attr_name: (str) attribute name in format: <tango device name>'/'<attribute name>
           
           :return: (taurus.core.tango.TangoConfiguration) configuration object
        """
        self.deprecated("Use getConfiguration(full_attr_name) instead")
        attr = self.getAttribute(full_attr_name)
        return attr.getConfig()

    def getConfiguration(self,param):
        """Obtain the object corresponding to the given attribute or full name.
           If the corresponding configuration already exists, the existing instance
           is returned. Otherwise a new instance is stored and returned.

           :param param: (taurus.core.taurusattribute.TaurusAttribute or str) attrubute object or full configuration name
           
           :return: (taurus.core.tango.TangoConfiguration) configuration object
        """
        if isinstance(param, str):
            return self._getConfigurationFromName(param)
        return self._getConfigurationFromAttribute(param)

    def _getAttributeClass(self, **params):
        attr_name = params.get("attr_name")
        attr_klass = self.tango_attr_klasses.get(attr_name, _Attribute)
        return attr_klass

    def _getDeviceClass(self, **params):
        db, dev_name = params.get("db"), params.get("dev_name")
        if db is None or dev_name is None or len(self.tango_dev_klasses) == 0:
            return _Device
        else:
            tango_dev_klass = db.get_class_for_device(dev_name)
            return self.tango_dev_klasses.get(tango_dev_klass, _Device)
        
    def _getConfigurationFromName(self,cfg_name):
        cfg = self.tango_configs.get(cfg_name)
        
        if cfg is not None:
            return cfg
        
        # Simple approach did not work. Lets build a proper configuration name
        if cfg_name.lower().startswith("tango://"):
            cfg_name = cfg_name[8:]
        
        validator = _Configuration.getNameValidator()
        params = validator.getParams(cfg_name)
                
        if params is None:
            raise TaurusException("Invalid Tango configuration name %s" % cfg_name)
        
        host,port = params.get('host'),params.get('port')
        db = None
        if host is None or port is None:
            db = self.getDatabase()
            host, port = db.get_db_host(), db.get_db_port()
        else:
            db_name = "%s:%s" % (host,port)
            db = self.getDatabase(db_name)
        
        dev_name = params.get('devicename') or db.get_device_alias(params.get('devalias'))
        dev_name = db.getFullName() + "/" + dev_name
        attr_name = params.get('attributename')
        attr_name = dev_name + "/" + attr_name
        cfg_name = attr_name + "?configuration"
        
        cfg = self.tango_configs.get(cfg_name)

        if cfg is None:
            attrObj = self.getAttribute(attr_name)
            cfg = self._getConfigurationFromAttribute(attrObj)
        return cfg
        
    def _getConfigurationFromAttribute(self,attrObj):
        cfg = attrObj.getConfig()
        cfg_name = attrObj.getFullName() + "?configuration"
        self.tango_configs[cfg_name] = cfg
        return cfg
    
    def _storeDevice(self, dev):
        name, alias = dev.getFullName(), dev.getSimpleName()
        exists = self.tango_devs.get(name)
        if not exists is None:
            if exists == dev:
                msg = "%s has already been registered before" % name
            else:
                msg = "%s has already been registered before with a different object!" % name
            self.debug(msg)
            raise DoubleRegistration(msg)
        self.tango_devs[name] = dev
        if not alias is None and len(alias): 
            self.tango_alias_devs[alias] = dev
    
    def _storeAttribute(self, attr):
        name = attr.getFullName()
        exists = self.tango_attrs.get(name)
        if not exists is None:
            if exists == attr: 
                msg = "%s has already been registered before" % name
            else:
                msg = "%s has already been registered before with a different object!" % name
            self.debug(msg)
            raise DoubleRegistration(msg)
        self.tango_attrs[name] = attr
        
    def getExistingAttribute(self, attr_name):
        """Returns a registered attribute or None if the corresponding attribute
           as not been registered. This is used mainly to avoid recursion between 
           two objects supplied by this factory which can ask for the other object 
           in the constructor.
        
           :param attr_name: (str) attribute name
           :return: (taurus.core.tango.TangoAttribute or None) attribute object or None
           """
        attr = self.tango_attrs.get(attr_name)

        if attr is not None:
            return attr
        
        # Simple approach did not work. Lets build a proper device name
        if attr_name.lower().startswith("tango://"):
            attr_name = attr_name[8:]
        validator = _Attribute.getNameValidator()
        params = validator.getParams(attr_name)
        
        if params is None:
            raise TaurusException("Invalid Tango attribute name %s" % attr_name)
        
        host,port = params.get('host'),params.get('port')
        
        db = None
        if host is None or port is None:
            db = self.getDatabase()
            host, port = db.get_db_host(), db.get_db_port()
        else:
            db_name = "%s:%s" % (host,port)
            db = self.getDatabase(db_name)
        
        dev_name = params.get('devicename')
        
        if dev_name is None:
            dev = self.getDevice(params.get('devalias'))
            dev_name = dev.getFullName()
        else:
            dev_name = db.getFullName() + "/" + dev_name

        attr_name = params.get('attributename')
        full_attr_name = dev_name + "/" + attr_name
         
        attr = self.tango_attrs.get(full_attr_name)
        return attr
    
    def getExistingDevice(self, dev_name):
        """Returns a registered device or None if the corresponding device
           as not been registered. This is used mainly to avoid recursion between 
           two objects supplied by this factory which can ask for the other object 
           in the constructor.
        
           :param dev_name: (str) tango device name or tango alias for the device.
                            It should be formed like: <host>:<port>/<tango device name>
                            - If <host>:<port> is ommited then it will use the 
                            default database.
                            - <tango device name> can be full tango device name 
                            (_/_/_) or a device alias.
           :return: (taurus.core.tango.TangoDevice or None) device object or None
        """

        d = self.tango_devs.get(dev_name)
        if d is None:
            d = self.tango_alias_devs.get(dev_name)
        if d is not None:
            return d
        
        # Simple approach did not work. Lets build a proper device name
        if dev_name.lower().startswith("tango://"):
            dev_name = dev_name[8:]
        
        validator = _Device.getNameValidator()
        params = validator.getParams(dev_name)
        
        if params is None:
            raise TaurusException("Invalid Tango device name %s" % dev_name)
        
        host,port = params.get('host'),params.get('port')
        db = None
        if host is None or port is None:
            db = self.getDatabase()
            host, port = db.get_db_host(), db.get_db_port()
        else:
            db_name = "%s:%s" % (host,port)
            db = self.getDatabase(db_name)
            
        dev_name = params.get('devicename')
        alias = params.get('devalias')
        
        if dev_name:
            try:
                alias = db.get_alias(dev_name)
                if alias and alias.lower() == InvalidAlias:
                    alias = None 
            except:
                alias = None
        else:
            try:
                dev_name = db.get_device_alias(alias)
            except:
                raise TaurusException("Device %s is not defined in %s." % (alias,db.getFullName()))

        full_dev_name = db.getFullName() + "/" + dev_name
        if not alias is None:
            alias = db.getFullName() + "/" + alias
        
        return self.tango_devs.get(full_dev_name)
        
    def removeExistingDevice(self, dev_or_dev_name):
        """Removes a previously registered device.
           
           :param dev_or_dev_name: (str or TangoDevice) device name or device object
        """
        if isinstance(dev_or_dev_name, _Device):
            dev = dev_or_dev_name
        else:
            dev = self.getExistingDevice(dev_or_dev_name)
        if dev is None:
            raise KeyError("Device %s not found" % dev_or_dev_name)
        dev.cleanUp()
        full_name = dev.getFullName()
        if self.tango_devs.has_key(full_name):
            del self.tango_devs[full_name]
        simp_name = dev.getSimpleName()
        if self.tango_alias_devs.has_key(simp_name):
            del self.tango_alias_devs[simp_name]
    
    def removeExistingAttribute(self, attr_or_attr_name):
        """Removes a previously registered attribute.
           
           :param attr_or_attr_name: (str or TangoAttribute) attribute name or attribute object
        """
        if isinstance(attr_or_attr_name, _Attribute):
            attr = attr_or_attr_name
        else:
            attr = self.getExistingAttribute(attr_or_attr_name)
        if attr is None:
            raise KeyError("Attribute %s not found" % attr_or_attr_name)
        attr.cleanUp()
        full_name = attr.getFullName()
        if self.tango_attrs.has_key(full_name):
            del self.tango_attrs[full_name]
    
    def addAttributeToPolling(self, attribute, period, unsubscribe_evts = False):
        """Activates the polling (client side) for the given attribute with the
           given period (seconds).

           :param attribute: (taurus.core.tango.TangoAttribute) attribute name.
           :param period: (float) polling period (in seconds)
           :param unsubscribe_evts: (bool) whether or not to unsubscribe from events
        """
        tmr = self.polling_timers.get(period, TaurusPollingTimer(period))
        self.polling_timers[period] = tmr
        tmr.addAttribute(attribute, self.isPollingEnabled())

    def removeAttributeFromPolling(self, attribute):
        """Deactivate the polling (client side) for the given attribute. If the
           polling of the attribute was not previously enabled, nothing happens.

           :param attribute: (str) attribute name.
        """
        p = None
        for period,timer in self.polling_timers.iteritems():
            if timer.containsAttribute(attribute):
                timer.removeAttribute(attribute)
                if timer.getAttributeCount() == 0:
                    p = period
                break
        if p:
            del self.polling_timers[period]
    
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
    
