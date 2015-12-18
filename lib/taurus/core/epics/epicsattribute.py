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
__all__ = ['EpicsFactory', 'EpicsDatabase', 'EpicsDevice', 
           'EpicsAttribute','EpicsConfiguration', 
           'EpicsConfigurationNameValidator', 'EpicsDeviceNameValidator', 
           'EpicsAttributeNameValidator']



import time, re, weakref
import numpy

from taurus.core.taurusbasetypes import MatchLevel, TaurusDevState, \
    SubscriptionState, TaurusEventType, TaurusAttrValue, TaurusTimeVal, \
    AttrQuality
from taurus.core.taurusfactory import TaurusFactory
from taurus.core.taurusattribute import TaurusAttribute
from taurus.core.taurusdevice import TaurusDevice
from taurus.core.taurusauthority import TaurusAuthority
from taurus.core.taurusconfiguration import TaurusConfiguration
from taurus.core.tauruspollingtimer import TaurusPollingTimer

try:
    import epics 
except ImportError: #note that if epics is not installed the factory will not be available
    from taurus.core.util.log import debug
    debug('cannot import epics module. Taurus will not support the "epics" scheme')
    #raise



class EpicsAttribute(TaurusAttribute):
    """
    A :class:`TaurusAttribute` that gives access to an Epics Process Variable.

    .. seealso:: :mod:`taurus.core.epics`

    .. warning:: In most cases this class should not be instantiated directly.
                 Instead it should be done via the
                 :meth:`EpicsFactory.getAttribute`
    """
    # TODO: support non-numerical PVs

    def __init__(self, name, parent, storeCallback = None):
        self.call__init__(TaurusAttribute, name, parent,
                          storeCallback=storeCallback)
               
        self.__attr_config = None
        self.__pv = epics.PV(self.getNormalName(), callback=self.onEpicsEvent)
        connected = self.__pv.wait_for_connection()
        if connected:
            self.info('successfully connected to epics PV')
            self._value = self.decode_pv(self.__pv)
        else:
            self.info('connection to epics PV failed')
            self._value = TaurusAttrValue()
        self.scheme = 'epics'
        
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


    def write(self, value, with_read=True):
        raise NotImplementedError("Not allowed to call AbstractClass" +
                                  " TaurusAttribute.write")

    def read(self, cache=True):
        raise NotImplementedError("Not allowed to call AbstractClass" +
                                  " TaurusAttribute.read")

    def poll(self):
        raise NotImplementedError("Not allowed to call AbstractClass" +
                                  " TaurusAttribute.poll")

    def _subscribeEvents(self):
        raise NotImplementedError("Not allowed to call AbstractClass" +
                                  " TaurusAttribute._subscribeEvents")

    def _unsubscribeEvents(self):
        raise NotImplementedError("Not allowed to call AbstractClass" +
                                  " TaurusAttribute._unsubscribeEvents")

    def isUsingEvents(self):
        raise NotImplementedError("Not allowed to call AbstractClass" +
                                  " TaurusAttribute.isUsingEvents")






    def isNumeric(self):
        return True  # TODO implement generic
        
    def isBoolean(self):
        return isinstance(self._value.value, bool)
    
    def isState(self):
        return False  # TODO implement generic

    def getDisplayValue(self, cache=True):
        return self.__pv.get(as_string=True, use_monitor=cache) # TODO: merge with TaurusModel Impl

    def encode(self, value):
        '''encodes the value passed to the write method into 
        a representation that can be written in epics'''
        # TODO: support Quantities and other types
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

