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

'''
Epics module. See __init__.py for more detailed documentation
'''
__all__ = ['EpicsFactory', 'EpicsDatabase', 'EpicsDevice', 
           'EpicsAttribute','EpicsConfiguration', 
           'EpicsConfigurationNameValidator', 'EpicsDeviceNameValidator', 
           'EpicsAttributeNameValidator']



import time, re, weakref
import numpy

from taurus import Factory
from taurus.core.taurusexception import TaurusException, DoubleRegistration
from taurus.core.util.singleton import Singleton
from taurus.core.util.log import Logger
from taurus.core.taurusbasetypes import MatchLevel, TaurusSWDevState, \
    SubscriptionState, TaurusEventType, TaurusAttrValue, TaurusTimeVal, \
    AttrQuality
from taurus.core.taurusfactory import TaurusFactory
from taurus.core.taurusattribute import TaurusAttribute
from taurus.core.taurusdevice import TaurusDevice
from taurus.core.taurusdatabase import TaurusDatabase
from taurus.core.taurusconfiguration import TaurusConfiguration
from taurus.core.tauruspollingtimer import TaurusPollingTimer

try:
    import epics 
except ImportError: #note that if epics is not installed the factory will not be available
    from taurus.core.util.log import debug
    debug('cannot import epics module. Taurus will not support the "epics" scheme')
    #raise

class AbstractEpicsNameValidator(Singleton):
    #@todo: provide a mechanism to make base_sep configurable at installation time. 
    base_sep = ':' #the following characters need to be escaped with "\":  ^$()<>[{\|.*+?
    name_pattern = ''
    
    def __init__(self):
        """ Initialization. Nothing to be done here for now."""
        pass
    
    def init(self, *args, **kwargs):
        """Singleton instance initialization."""
        self.name_re = re.compile(self.name_pattern)
        
    def isValid(self,s, matchLevel = MatchLevel.ANY):
        return self.name_re.match(s) is not None
        
    def getParams(self, s):
        m = self.attrname_re.match(s)
        if m is None:
            return None
        return m.groupdict()

    def getNames(self, s, factory=None):
        """Returns the full, normal and simple names for this object, or None if there is no match'''
        """
        raise RuntimeError('Not Allowed to call this method from subclasses')
    
    def getDeviceName(self, s, full=True):
        '''
        returns the device name for the given attribute name. 
        The "full" argument is ignored since the DB is never included in the epics models
        '''
        m = self.name_re.match(s)
        if m is None:
            return None
        devname = m.group('devname') or EpicsFactory.DEFAULT_DEVICE
        return 'epics://%s%s'%(devname,m.group('base_sep') or self.base_sep )
    
    def getDBName(self, s):
        '''returns the full data base name for the given attribute name.
        Note: the DB name is not a valid epics URI because the epics scheme does not implement a DB model'''
        dbname = EpicsFactory.DEFAULT_DATABASE
        return dbname
    

class EpicsAttributeNameValidator(AbstractEpicsNameValidator):
    #The groups in a match object using the regexp below are:
    #    1: scheme; named as 'scheme'
    #    2: EPICS PV name (in the case of attribute names) or same as $3 (in the case of device names) 
    #    3: device name including the trailing base_sep; optional
    #    4: device name; optional; named as 'devname'
    #    5: base separator if it appears on the URI; named as 'base_sep'
    #    6: attribute name;optional; named as 'attrname'
    #
    #    Reconstructing the names
    #    attrname= $6
    #    devname= $4 or EpicsFactory.DEFAULT_DEVICE
    #    fullname= "epics://%s"%($2)
    # 
    #                1                   2             34                  5                 6
    name_pattern = '^(?P<scheme>epics)://(?P<epicsname>((?P<devname>[^?#]*)(?P<base_sep>%s))?(?P<attrname>[^?#%s]+))$'%(AbstractEpicsNameValidator.base_sep, AbstractEpicsNameValidator.base_sep)
    
#    def isValid(self,s, matchLevel = MatchLevel.ANY):
#        m = self.name_re.match(s)
#        return m is not None and m.group('attrname') #the model contains an attrname 
    
    def getNames(self, s, factory=None):
        """Returns the complete, normal and short names.
        
        For example::
        
            >>> EpicsDeviceNameValidator.getNames("epics://foo:bar:baz")
            >>> ("epics://foo:bar:baz", "foo:bar:baz", "baz")
        
        """
        m = self.name_re.match(s)
        if m is None:
            return None
        #The following comments are for an example name like: "epics://foo:bar:baz"
        attr_name = m.group('attrname') # attr_name = "baz"
        normal_name = m.group('epicsname')  #normal_name = "foo:bar:baz"
        fullname = "%s://%s"%(m.group('scheme'),normal_name) #fullname = "epics://foo:bar:baz"
        return fullname, normal_name, attr_name
        

class EpicsDeviceNameValidator(AbstractEpicsNameValidator):
    '''A validator of names for :class:`EpicsDevice`. By taurusconvention, 
    the model name for an epics device name *must* end with the base separator
    (in order to distinguish device names from attribute names)'''
    
    name_pattern = '^(?P<scheme>epics)://(?P<epicsname>((?P<devname>[^?#]*)(?P<base_sep>%s)))$'%(AbstractEpicsNameValidator.base_sep)
    
#    def isValid(self,s, matchLevel = MatchLevel.ANY):
#        m = self.name_re.match(s)
#        return m is not None and not m.group('attrname') #to be a device it must not contain an attribute
    
    def getNames(self, s, factory=None):
        """Returns the complete, normal and short names. (note: complete=normal)
        
        :param s: (str) input string describing the device
        :param factory: (TaurusFactory) [Unused]
        
        :return: (tuple<str,str,str> or None) A tuple of complete, normal and
                 short names, or None if s is an invalid device name
        """
        m = self.name_re.match(s)
        if m is None:
            return None
        #The following comments are for a name of the type: "epics://foo:bar:" 
        devname = m.group('devname')  # foo:bar
        normal_name = m.group('epicsname') #foo:bar:
        full_name = self.getDeviceName(s, full=True) #epics://foo:bar:
        return full_name, normal_name, devname


class EpicsConfigurationNameValidator(AbstractEpicsNameValidator):
    '''A validator of names for :class:`EpicsConfiguration`'''
    # The groups in a match object using the regexp below are the 
    # same as for the AbstractEpicsNameValidator plus:
    #   +1: configuration extension
    #   +2: configuration key;optional; named as 'cfgkey'
    
    name_pattern = '^(?P<scheme>epics)://(?P<epicsname>((?P<devname>[^?#]*)(?P<base_sep>%s))?(?P<attrname>[^?#%s]+)\?configuration=?(?P<cfgkey>[^#?]*))$'%(AbstractEpicsNameValidator.base_sep, AbstractEpicsNameValidator.base_sep)
        
    def getNames(self, s, factory=None):
        """Returns the complete, normal and short names"""
        m = self.name_re.match(s)
        if m is None:
            return None
        #The following comments are for an example name like: "epics://foo:bar:baz?configuration=label"
        cfg_key = m.group('cfgkey') # cfg_key = "label"
        full_name = s               # "epics://foo:bar:baz?configuration=label"
        normal_name = full_name     # "epics://foo:bar:baz?configuration=label"
        return full_name, normal_name, cfg_key
    
    def getAttrName(self, s):
        names = self.getNames(s)
        if names is None: return None
        return names[0].rsplit('?configuration')[0]#remove the "?configuration..." substring from the fullname 
        

class EpicsDatabase(TaurusDatabase):
    '''
    Dummy database class for Epics (the Database concept is not used in the Epics scheme)
    
    .. warning:: In most cases this class should not be instantiated directly.
                 Instead it should be done via the :meth:`EpicsFactory.getDataBase`
    '''
    def factory(self):
        return EpicsFactory()
        
    def __getattr__(self, name):
        return "EpicsDatabase object calling %s" % name


class EpicsDevice(TaurusDevice):
    '''
    An Epics device object. 
    @todo: For the moment is a dummy object. Eventually we may map it to an epics record.
    
    .. seealso:: :mod:`taurus.core.epics`
    
    .. warning:: In most cases this class should not be instantiated directly.
                 Instead it should be done via the :meth:`EpicsFactory.getDevice`
    '''
    
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # TaurusModel necessary overwrite
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # helper class property that stores a reference to the corresponding factory
    _factory = None
    
    @classmethod
    def factory(cls):
        if cls._factory is None:
            cls._factory = Factory(scheme='epics')
        return cls._factory
    
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # TaurusDevice necessary overwrite
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    def _createHWObject(self):
        return 'Epics'
    
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    def getAttribute(self, attrname):
        """Returns the attribute object given its name"""
        full_attrname = "%s%s"%(self.getFullName(), attrname)
        return self.factory().getAttribute(full_attrname)
    
    @classmethod
    def getNameValidator(cls):
        return EpicsDeviceNameValidator()
    
    def decode(self, event_value):
        if isinstance(event_value, int): # TaurusSWDevState
            new_sw_state = event_value
        else:
            self.info("Unexpected value to decode: %s" % str(event_value))
            new_sw_state = TaurusSWDevState.Crash
        value = TaurusAttrValue() 
        value.value = new_sw_state
        return value
    

class EpicsAttribute(TaurusAttribute):
    '''
    A :class:`TaurusAttribute` that gives access to an Epics Process Variable.
    
    .. seealso:: :mod:`taurus.core.epics` 
    
    .. warning:: In most cases this class should not be instantiated directly.
                 Instead it should be done via the :meth:`EpicsFactory.getAttribute`
    '''
    
    def __init__(self, name, parent, storeCallback = None):
        self.call__init__(TaurusAttribute, name, parent, storeCallback=storeCallback)
               
        self.__attr_config = None
        self.__pv = epics.PV(self.getNormalName(), callback=self.onEpicsEvent)
        connected = self.__pv.wait_for_connection()
        if connected:
            self.info('successfully connected to epics PV')
            self._value = self.decode_pv(self.__pv)
        else:
            self.info('connection to epics PV failed')
            self._value = TaurusAttrValue()
        
        #print "INIT",self.__pv, connected
        
    def onEpicsEvent(self, **kw):
        '''callback for PV changes'''
        self._value = self.decode_epics_evt(kw)
        self.fireEvent(TaurusEventType.Change, self._value)
    
    def __getattr__(self,name):
        return getattr(self._getRealConfig(), name)
    
    def _getRealConfig(self):
        """ Returns the current configuration of the attribute."""
        if self.__attr_config is None:
            cfg_name = "%s?configuration" % self.getFullName()
            self.__attr_config = EpicsConfiguration(cfg_name, self)
        return self.__attr_config
            
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # Necessary to overwrite from TaurusAttribute
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    def isNumeric(self):
        return True
        
    def isBoolean(self):
        return isinstance(self._value.value, bool)
    
    def isState(self):
        return False

    def getDisplayValue(self,cache=True):
        return self.__pv.get(as_string=True, use_monitor=cache)

    def encode(self, value):
        '''encodes the value passed to the write method into 
        a representation that can be written in epics'''
        try:
            typeclass = numpy.dtype(self.__pv.type).type
            return typeclass(value) #cast the value with the python type for this PV
        except:
            return value

    def decode (self, obj):
        if isinstance(obj, epics.PV):
            return self.decode_pv(obj)
        else:
            return self.decode_epics_evt(obj)

    def decode_pv(self, pv):
        """Decodes an epics pv into the expected taurus representation"""
        #@todo: This is a very basic implementation, and things like quality may not be correct
        attr_value = TaurusAttrValue()
        attr_value.value = pv.value
        if pv.write_access:
            attr_value.w_value = pv.value
        if pv.timestamp is None: 
            attr_value.time = TaurusTimeVal.now()
        else:
            attr_value.time = TaurusTimeVal.fromtimestamp(pv.timestamp)
        if pv.severity > 0:
            attr_value.quality = AttrQuality.ATTR_ALARM
        else:
            attr_value.quality = AttrQuality.ATTR_VALID
        attr_value.config.data_format = len(numpy.shape(attr_value.value))
        return attr_value
    
    def decode_epics_evt(self, evt):
        """Decodes an epics event (a callback keywords dict) into the expected taurus representation"""
        #@todo: This is a very basic implementation, and things like quality may not be correct
        attr_value = TaurusAttrValue()
        attr_value.value = evt.get('value')
        if evt.get('write_access', False):
            attr_value.w_value = attr_value.value
        timestamp =  evt.get('timestamp', None)
        if timestamp is None: 
            attr_value.time = TaurusTimeVal.now()
        else:
            attr_value.time = TaurusTimeVal.fromtimestamp(timestamp)
        if evt.get('severity', 1) > 0:
            attr_value.quality = AttrQuality.ATTR_ALARM
        else:
            attr_value.quality = AttrQuality.ATTR_VALID
        attr_value.config.data_format = len(numpy.shape(attr_value.value))
        return attr_value

    def write(self, value, with_read=True):
        value = self.encode(value)
        self.__pv.put(value)
        if with_read:
            return self.decode_pv(self.__pv)

    def read(self, cache=True):
        '''returns the value of the attribute.
        
        :param cache: (bool) If True (default), the last calculated value will
                      be returned. If False, the referenced values will be re-
                      read and the transformation string will be re-evaluated
                      
        :return: attribute value
        '''
        if not cache:
            self.__pv.get(use_monitor=False)
            self._value = self.decode_pv(self.__pv)
        return self._value    

    def poll(self):
        v = self.read(cache=False)
        self.fireEvent(TaurusEventType.Periodic, v)

    def isUsingEvents(self):
        return True #@todo
        
#------------------------------------------------------------------------------ 

    def isWritable(self, cache=True):
        return self.__pv.write_access
    
    def isWrite(self, cache=True):
        return self.__pv.write_access
    
    def isReadOnly(self, cache=True):
        return self.__pv.read_access and not self.__pv.write_access

    def isReadWrite(self, cache=True):
        return self.__pv.read_access and self.__pv.write_access

    def getWritable(self, cache=True):
        return self.__pv.write_access


    def factory(self):
        return EpicsFactory()
    
    @classmethod
    def getNameValidator(cls):
        return EpicsAttributeNameValidator()

    

class EpicsConfiguration(TaurusConfiguration):
    '''
    A :class:`TaurusConfiguration` 
    
    .. seealso:: :mod:`taurus.core.epics` 
    
    .. warning:: In most cases this class should not be instantiated directly.
                 Instead it should be done via the :meth:`EpicsFactory.getConfig`
    '''
    def __init__(self, name, parent, storeCallback = None):
        self.call__init__(TaurusConfiguration, name, parent, storeCallback=storeCallback)
        
        #fill the attr info
        i = parent.read().config
        a=parent
        d=self._getDev()
        # add dev_name, dev_alias, attr_name, attr_full_name
        i.dev_name = d.getNormalName()
        i.dev_alias = d.getSimpleName()
        i.attr_name = a.getSimpleName()
        i.attr_fullname = a.getNormalName()
        i.label = a.getSimpleName()
        self._attr_info = i
        
    def __getattr__(self, name): 
        try:
            return getattr(self._attr_info,name)
        except:
            raise AttributeError("'%s'object has no attribute '%s'"%(self.__class__.__name__, name))
    @classmethod
    def getNameValidator(cls):
        return EpicsConfigurationNameValidator()
        
    def _subscribeEvents(self): 
        pass
    
    def _unSubscribeEvents(self):
        pass   
    
    def factory(self):
        EpicsFactory()
    
    def getValueObj(self, cache=True):
        """ Returns the current configuration for the attribute."""
        return self._attr_info   
    
    
class EpicsFactory(Singleton, TaurusFactory, Logger):
    """
    A Singleton class that provides Epics related objects.
    """

    schemes = ("epics",)
    DEFAULT_DEVICE = '_DefaultEpicsDevice'
    DEFAULT_DATABASE = '_DefaultEpicslDB'
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
        if EpicsConfiguration.isValid(absolute_name):
            return EpicsConfiguration
        elif EpicsDevice.isValid(absolute_name):
            return EpicsDevice
        elif EpicsAttribute.isValid(absolute_name):
            return EpicsAttribute
        else:
            self.debug("Not able to find Object class for %s" % absolute_name)
            self.traceback()
            return None

    def getDatabase(self, db_name=None):
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
                db = self.getDatabase()
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
def test1():
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
    

def test2():
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
    
def test3():
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
    test3()
    
        
