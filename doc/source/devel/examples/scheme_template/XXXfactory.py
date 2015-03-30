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

'''
YYY module. See __init__.py for more detailed documentation
'''

#Todo: this is very outdated *and* tango-centric. Needs complete rewriting.

__all__ = ['YYYFactory']

"""
For create your basic scheme factory.
Replace XXX for the name of your scheme. i.e. tango
Replace YYY for the name of your Scheme. i.e. Tango
"""



from taurus.core.util.enumeration import Enumeration
from taurus.core.util.log import Logger
from taurus.core.util.singleton import Singleton
from taurus.core.tauruspollingtimer import TaurusPollingTimer
from taurus.core.taurusfactory import TaurusFactory

from .XXXattribute import YYYAttribute
from .XXXauthority import YYYAuthority
from .XXXdevice import YYYDevice  
from .XXXconfiguration import YYYConfiguration

from taurus import Factory


class YYYFactory(Singleton, TaurusFactory, Logger):
    """
    A Singleton class that provides YYY related objects.
    """

    schemes = ("XXX",)

    def __init__(self):
        """ Initialization. Nothing to be done here for now."""
        pass

    def init(self, *args, **kwargs):
        """Singleton instance initialization."""
        name = self.__class__.__name__
        self.call__init__(Logger, name)
        self.call__init__(TaurusFactory)
        self.dbs = weakref.WeakValueDictionary()  
        self.devs = weakref.WeakValueDictionary()
        self.attrs = weakref.WeakValueDictionary() 
        self.configs = weakref.WeakValueDictionary()
        #TODO Add your variables 


    def findObjectClass(self, absolute_name):
        """
        Obtain the class object corresponding to the given name.
        """
        if YYYConfiguration.isValid(absolute_name):
            return YYYConfiguration
        elif YYYAuthority.isValid(absolute_name):
            return YYYAuthority
        elif YYYDevice.isValid(absolute_name):
            return YYYDevice
        elif YYYAttribute.isValid(absolute_name):
            return YYYAttribute
        else:
            self.debug("Not able to find Object class for %s" % absolute_name)
            self.traceback()
            return None

    def getAuthority(self, db_name):
        """Obtain the YYYAuthority object.
        
        :param db_name: (str) this is ignored because only one dummy authority is supported
                           
        :return: (YYYAuthority)
        """
        validator = YYYAuthority.getNameValidator()
        params = validator.getParams(db_name)
        if params is None:
            raise TaurusException("Invalid YYY Authority name %s" % db_name)
        #TODO It is just an example
        fullname = params.get('session')
        db = self.dbs.get(fullname, None)
        if db is None: 
            db = YYYAuthority(fullname)
            self.dbs[fullname] = db
        return db
    
    def getDevice(self, dev_name):
        """Obtain the YYYDevice object.
        
        :param dev_name: (str) this is ignored because only one dummy device is supported
                           
        :return: (YYYDevice)
        
        .. todo:: YYY records may be implemented as taurus devices...
        """
        validator = YYYDevice.getNameValidator()
        params = validator.getParams(dev_name)
        if params is None:
            raise TaurusException("Invalid YYY device name %s" % dev_name)
        #TODO It is just an example
        session = params.get('session')
        fullname = session + '/' + params.get('devicename') 

        d = self.devs.get(fullname, None) 
        if d is None: 
            db = self.getAuthority(session)
            d = YYYDevice(fullname, parent=db)
            self.devs[fullname] = d
        return d
    
    def getAttribute(self, attr_name):
        """Obtain the object corresponding to the given attribute name. If the 
        corresponding attribute already exists, the existing instance is
        returned. Otherwise a new instance is stored and returned. The 
        device associated to this attribute will also be created if necessary.
           
        :param attr_name: (str) the attribute name string. See
                          :mod:`taurus.core.XXX` for valid attribute names
        
        :return: (YYYAttribute)
         
        @throws TaurusException if the given name is invalid.
        """
        validator = YYYAttribute.getNameValidator()
        params = validator.getParams(attr_name)
        if params is None:
            raise TaurusException("Invalid YYY device name %s" % attr_name)
        #TODO It is just an example
        session = params.get('session')
        devicename = params.get('devicename')
        attributename = params.get('attributename')
        fullname = session+'/'+devicename+'/'+attributename
        a = self.attrs.get(fullname, None)
        if a is None: 
            dev = self.getDevice(session+'/'+devicename)
            a = YYYAttribute(fullname, parent=dev)
            self.attrs[fullname] = a
        return a

    def getConfiguration(self, param):
        """getConfiguration(param) -> taurus.core.TaurusConfiguration

        Obtain the object corresponding to the given attribute or full name.
        If the corresponding configuration already exists, the existing instance
        is returned. Otherwise a new instance is stored and returned.

        @param[in] param taurus.core.TaurusAttribute object or full configuration name
           
        @return a taurus.core.TaurusAttribute object
        @throws TaurusException if the given name is invalid.
        """
        if isinstance(param, str):
            return self._getConfigurationFromName(param)
        return self._getConfigurationFromAttribute(param)

    def _getConfigurationFromName(self, cfg_name):
        cfg = self.configs.get(cfg_name, None) #first try with the given name
        if cfg is None: #if not, try with the full name
            validator = YYYConfiguration.getNameValidator()
            names = validator.getNames(cfg_name)
            if names is None:
                raise TaurusException("Invalid evaluation configuration name %s" % cfg_name)
            fullname = names[0]
            attr = self.getAttribute(fullname.split('?')[0])
            cfg = YYYConfiguration(fullname, parent=attr)
            self.configs[cfg_name] = cfg
        return cfg
        
    def _getConfigurationFromAttribute(self, attr):
        cfg = attr.getConfig()
        cfg_name = attr.getFullName() + "?configuration"
        self.configs[cfg_name] = cfg
        return cfg
        
    def addAttributeToPolling(self, attribute, period, unsubscribe_evts = False):
        """Activates the polling (client side) for the given attribute with the
           given period (seconds).

           :param attribute: (taurus.core.XXX.XXXAttribute) attribute name.
           :param period: (float) polling period (in seconds)
           :param unsubscribe_evts: (bool) whether or not to unsubscribe from events
        """
        tmr = self.polling_timers.get(period,TaurusPollingTimer(period))
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
            
