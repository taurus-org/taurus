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
__all__ = ["YYYAttribute"]

"""
For create your basic scheme attribute.
Remplace XXX for the name of your scheme. i.e. tango
Remplace YYY for the name of your Scheme. i.e. Tango
"""

import taurus.core
from taurus.core import SubscriptionState, TaurusEventType
from .XXXvalidator import YYYAttributeNameValidator
from .XXXconfiguration import YYYConfiguration

from taurus.core.taurusattribute import TaurusAttribute
from taurus.core.taurusbasetypes import TaurusAttrValue, TaurusEventType,\
         AttrQuality, TaurusTimeVal
from taurus import Factory
import numpy, time, numbers


class YYYAttribute(TaurusAttribute):
    '''
    A :class:`TaurusAttribute` that gives access to an YYY Process Variable.
    
    .. seealso:: :mod:`taurus.core.XXX` 
    
    .. warning:: In most cases this class should not be instantiated directly.
                 Instead it should be done via the :meth:`YYYFactory.getAttribute`
    '''

    # helper class property that stores a reference to the corresponding factory
    _factory = None
    _scheme = 'XXX'

    def __init__(self, name, parent, storeCallback = None):
        self.call__init__(TaurusAttribute, name, parent, storeCallback=storeCallback)
        self.deviceName = self.getNormalName().split('/')[1]
        self.attrName = self.getSimpleName() 
        try:
            #YYY Obj
            self.obj = parent.getHWObj()
            self.valueCache = None
        except:
            self.warning('Error, Try to create attribute without parent (=None)')
            raise

        self._value = TaurusAttrValue()
        self._value.value = None
        self._value.w_value = None
        # reference to the configuration object
        self.__attr_config = None                                               
        self.__attr_timestamp = 0

      
    def onYYYEvent(self, name, value):
        self.valueCache = value

        self._value = self.decode_XXX(value)
        self.fireEvent(TaurusEventType.Change, self._value)

    def __getattr__(self,name):
        return getattr(self._getRealConfig(), name)
    
    def _getRealConfig(self):
        """ Returns the current configuration of the attribute."""
        if self.__attr_config is None:
            cfg_name = "%s?configuration" % self.getFullName()
            self.__attr_config = YYYConfiguration(cfg_name, self)
        return self.__attr_config 
        
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # Necessary to overwrite from TaurusAttribute
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    def isNumeric(self):
        return True
        #or
        #return isinstance(self._value.value , numbers.Number)
        
    def isBoolean(self):
        return isinstance(self._value.value, bool)
    
    def isState(self):
        return False

    def getDisplayValue(self,cache=True):
        return str(self.read(cache=cache).value)

    def encode(self, attr):
        """
            Encode the given attr, it could be TaurusAttrValue or a simple numeric value  
        """
        if isinstance(attr, TaurusAttrValue):
            attr =  attr.value
        attr = str(attr)
        return attr 

    def decode(self, attr):
        #if isinstance(obj, TaurusAttrValue):
        return self.decode_XXX(attr)

    def decode_XXX(self, attr):
        """
            adapt it according your necessities
        """
        if isinstance(attr, TaurusAttrValue):
            attr = attr.value
        attr = str(attr) 
        self._value.value = attr
        #cp name
        self._value.name = self.attrName
        self._value.w_value = attr
        self._value.time = TaurusTimeVal.now()
        self._value.quality = AttrQuality.ATTR_VALID
        self._value.config.data_format = len(numpy.shape(self._value.value))
        return self._value

    def write(self, value, with_read=True): 
        value = self.encode(value)
        self.valueCache = value                                              
        f =  self.factory()
        #TODO Call your write obj function i.e.
#        if with_read:
#            value = self.obj.write_read_attribute(name, value)
#            self._value = self.decode(value)
#            self.poll()
#            return self._value
#        else:
#            #self.obj.write_attribute(name, value)
#            value = self.obj.setValue(value)


    def read(self, cache=True):
        '''returns the value of the attribute.
        
        :param cache: (bool) If True (default), the last calculated value will
                      be returned. If False, the referenced values will be re-
                      read and the transformation string will be re-evaluated (Not used)
                      
        :return: attribute value
        '''  
        
#        if cache:
#            #TODO check refresh and add timer (depend of your polity)
#            dt = (time.time() - self.__attr_timestamp)*1000
#            #if dt < self.getPollingPeriod():
#            if not self.valueCache is None: # and dt < self.getPollingPeriod():
#                return self.decode(self.valueCache)
#            else:
#                return self.read(cache=False)  
        self.__attr_timestamp = time.time()
        f =  self.factory()
        #TODO Call your read obj function
        #i..e. value = self.obj.read_attribute(name)
        self.valueCache = value
        #Decode as TaurusAttribute
        self._value = self.decode(value)
        return self._value
 
    def poll(self):
        v = self.read(cache=False)  
        f = self.factory()
        f.__subscription_event.set()
        self.fireEvent(TaurusEventType.Periodic, v)

    def _subscribeEvents(self): 
        pass
        
    def _unsubscribeEvents(self):
        pass

    def isUsingEvents(self):
        return True #TODO
        #return bool(len(self._references)) #if this attributes depends from others, then we consider it uses events

