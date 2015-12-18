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
Epics module. See __init__.py for more detailed documentation
'''
__all__ = ['EpicsFactory']



import time, weakref

from taurus.core.taurusexception import TaurusException, DoubleRegistration
from taurus.core.util.singleton import Singleton
from taurus.core.util.log import Logger
from taurus.core.taurusbasetypes import MatchLevel, TaurusDevState, \
    SubscriptionState, TaurusEventType, TaurusAttrValue, TaurusTimeVal, \
    AttrQuality
from taurus.core.taurusfactory import TaurusFactory
from taurus.core.tauruspollingtimer import TaurusPollingTimer

try:
    import epics 
except ImportError: #note that if epics is not installed the factory will not be available
    from taurus.core.util.log import debug
    debug('cannot import epics module. Taurus will not support the "epics" scheme')
    #raise


class EpicsFactory(Singleton, TaurusFactory, Logger):
    """
    A Singleton class that provides Epics related objects.
    """

    schemes = ("epics",)
    DEFAULT_DEVICE = ''
    DEFAULT_AUTHORITY = '//'
    def __init__(self):
        """ Initialization. Nothing to be done here for now."""
        pass

    def init(self, *args, **kwargs):
        """Singleton instance initialization."""
        name = self.__class__.__name__
        self.call__init__(Logger, name)
        self.call__init__(TaurusFactory)
        self.epics_attrs = weakref.WeakValueDictionary()
        self.epics_devs = weakref.WeakValueDictionary()
        self.epics_configs = weakref.WeakValueDictionary()
        
    def findObjectClass(self, absolute_name):
        """
        Obtain the class object corresponding to the given name.
        """
        if EpicsDevice.isValid(absolute_name):
            return EpicsDevice
        elif EpicsAttribute.isValid(absolute_name):
            return EpicsAttribute
        else:
            self.debug("Not able to find Object class for %s" % absolute_name)
            self.traceback()
            return None

    def getAuthority(self, db_name=None):
        """Obtain the EpicsDatabase object.
        
        :param db_name: (str) this is ignored because only one dummy database is supported
                           
        :return: (EpicsDatabase)
        """
        if not hasattr(self, "_db"):
            self._db = EpicsDatabase(self.DEFAULT_DATABASE)
        return self._db

    def getDevice(self, dev_name):
        """Obtain the EpicsDevice object.
        
        :param dev_name: (str) this is ignored because only one dummy device is supported
                           
        :return: (EpicsDevice)
        
        .. todo:: Epics records may be implemented as taurus devices...
        """
        d = self.epics_devs.get(dev_name, None) #first try with the given name
        if d is None: #if not, try with the full name
            validator = EpicsDevice.getNameValidator()
            names = validator.getNames(dev_name)
            if names is None:
                raise TaurusException("Invalid epics device name %s" % dev_name)
            fullname = names[0]
            d = self.epics_devs.get(fullname, None)
            if d is None: #if the full name is not there, create one
                db = self.getAuthority()
                d = EpicsDevice(fullname, parent=db, storeCallback=self._storeDev) #use full name
        return d
    
    def getAttribute(self, attr_name):
        """Obtain the object corresponding to the given attribute name. If the 
        corresponding attribute already exists, the existing instance is
        returned. Otherwise a new instance is stored and returned. The 
        device associated to this attribute will also be created if necessary.
           
        :param attr_name: (str) the attribute name string. See
                          :mod:`taurus.core.epics` for valid attribute names
        
        :return: (EpicsAttribute)
         
        @throws TaurusException if the given name is invalid.
        """
        a = self.epics_attrs.get(attr_name, None) #first try with the given name
        if a is None: #if not, try with the full name
            validator = EpicsAttribute.getNameValidator()
            names = validator.getNames(attr_name)
            if names is None:
                raise TaurusException("Invalid epics attribute name %s" % attr_name)
            fullname = names[0]
            a = self.epics_attrs.get(fullname, None)
            if a is None: #if the full name is not there, create one
                dev = self.getDevice(validator.getDeviceName(attr_name))
                a = EpicsAttribute(fullname, parent=dev, storeCallback=self._storeAttr) #use full name
        return a

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

    def _getConfigurationFromName(self, cfg_name):
        cfg = self.epics_configs.get(cfg_name, None) #first try with the given name
        if cfg is None: #if not, try with the full name
            validator = EpicsConfiguration.getNameValidator()
            names = validator.getNames(cfg_name)
            if names is None:
                raise TaurusException("Invalid evaluation configuration name %s" % cfg_name)
            fullname = names[0]
            cfg = self.epics_configs.get(fullname, None)
            if cfg is None: #if the full name is not there, create one
                attr = self.getAttribute(validator.getAttrName(cfg_name))
                cfg = EpicsConfiguration(fullname, parent=attr, storeCallback=self._storeConfig) 
        return cfg
        
    def _getConfigurationFromAttribute(self, attr):
        cfg = attr.getConfig()
        cfg_name = attr.getFullName() + "?configuration"
        self.epics_configs[cfg_name] = cfg
        return cfg
    
    def _storeDev(self, dev):
        name = dev.getFullName()
        exists = self.epics_devs.get(name)
        if exists is not None:
            if exists == dev: 
                self.debug("%s has already been registered before" % name)
                raise DoubleRegistration
            else:
                self.debug("%s has already been registered before with a different object!" % name)
                raise DoubleRegistration
        self.epics_devs[name] = dev
    
    def _storeAttr(self, attr):
        name = attr.getFullName()
        exists = self.epics_attrs.get(name)
        if exists is not None:
            if exists == attr: 
                self.debug("%s has already been registered before" % name)
                raise DoubleRegistration
            else:
                self.debug("%s has already been registered before with a different object!" % name)
                raise DoubleRegistration
        self.epics_attrs[name] = attr
        
    def _storeConfig(self, fullname, config):
        #name = config.getFullName()
        name = fullname
        exists = self.epics_configs.get(name)
        if exists is not None:
            if exists == config: 
                self.debug("%s has already been registered before" % name)
                raise DoubleRegistration
            else:
                self.debug("%s has already been registered before with a different object!" % name)
                raise DoubleRegistration
        self.epics_configs[name] = config
        
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
            

#===============================================================================
# Just for testing
#===============================================================================
def _test1():
    f = EpicsFactory()
    d = f.getDevice('epics://foo:bar:')
    a = f.getAttribute('epics://foo:bar:baz')
    p = a.getParentObj()
    c = f.getConfiguration('epics://foo:bar:baz?configuration=label')
#    cp = a.getConfig()
    print "FACTORY:", f
    print "DEVICE:", d, d.getSimpleName(), d.getNormalName(), d.getFullName()
    print "ATTRIBUTE", a, a.getSimpleName(), a.getNormalName(), a.getFullName()
    print "ATTRIBUTE PARENT", p, p.getSimpleName(), p.getNormalName(), p.getFullName(), p is d
    print "CONFIGURATION", c, c.getSimpleName(), c.getNormalName(), c.getFullName()
#    print "CONFIGPROXY", cp, cp.getSimpleName()
#    print
#    print c.getValueObj()
#    print c.getUnit()
    

def _test2():
    from taurus import Attribute
    a = Attribute('epics://mp49t:sim1.RBV')
    class Dummy:
        n=0
        def eventReceived(self, s,t,v):
            print "DUMMY:",self.n, v.value
            self.n += 1
    kk = Dummy()
    a.addListener(kk)
    while kk.n <= 2:
        time.sleep(1)
    a.removeListener(kk)
    while kk.n <= 20:
        time.sleep(1)        
    
def _test3():
    import sys
    from taurus.qt.qtgui.application import TaurusApplication
    from taurus.qt.qtgui.panel import TaurusForm
    from taurus.qt.qtgui.plot import TaurusTrend
#    from taurus.qt.qtgui.display import TaurusLabel
    app = TaurusApplication()
    
    w = TaurusForm()
    w.modifiableByUser=True
    w2=TaurusTrend()
#    w=TaurusLabel()

    w.setModel(['epics://mp49t:sim1.RBV', 'epics://mp49t:sim1.VAL', 'epics://mp49t:sim1.HIGH'])
    w2.setModel(['epics://mp49t:sim1.RBV', 'epics://mp49t:sim1.VAL'])

#    a=w.getModelObj()
#    print a, a.read().value
    
#    a=w.getModelObj()
#    a.setUnit('asd')
#    c=a.getConfig()

    w.show()
    w2.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    _test3()
    
        
