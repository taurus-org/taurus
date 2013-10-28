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

"""This module contains the base class for a taurus attribute"""

__all__ = ["TaurusAttribute", "TaurusStateAttribute"]

__docformat__ = "restructuredtext"

import weakref

from taurus.core.taurusbasetypes import TaurusElementType
from .taurusmodel import TaurusModel
from .taurusconfiguration import TaurusConfigurationProxy

class TaurusAttribute(TaurusModel):
    
    def __init__(self, name, parent, **kwargs):
        self.call__init__(TaurusModel, name, parent)

        self.__parentDevice = parent # just to keep it alive
        
        # User enabled/disabled polling
        self.__enable_polling = kwargs.get('enablePolling', True) 
        
        # attribute should be polled. The attribute is in fact polled only if the polling is also enabled 
        self.__activate_polling = False
        
        # efectively tells if the attribute is being polled periodically
        # in summary: polled = enable_polling and activate_polling
        self.__polled = False
        
        # current polling period
        self.__polling_period = kwargs.get("pollingPeriod", 3000)
        
        # stores if polling has been forced by user API
        self.__forced_polling = False
        
        # Everything went ok so now we are sure we can store the object
        storeCallback = kwargs.get("storeCallback", None)
        if not storeCallback is None:
            storeCallback(self)

        self._dev_hw_obj = parent.getHWObj()
    
    def cleanUp(self):
        self.trace("[TaurusAttribute] cleanUp")
        self._unsubscribeEvents()
        self._dev_hw_obj = None
        TaurusModel.cleanUp(self)
        
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # TaurusModel implementation
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    @classmethod
    def getTaurusElementType(cls):
        return TaurusElementType.Attribute
            
    @classmethod
    def buildModelName(cls, parent_model, relative_name):
        """build an 'absolute' model name from the parent model and the 'relative'
        name. 
        - If parent_model is a TaurusDevice, the return is a composition of
        the database model name and is device name
        - If parent_model is a TaurusAttribute, the relative name is ignored and
        the parent name is returned
        """
        if parent_model is None:
            return relative_name
        parent_name = parent_model.getFullName()
        if not parent_name:
            return relative_name
        if isinstance(parent_model, cls):
            return parent_name
        return '%s%s' % (parent_name,relative_name)  
            
    @classmethod
    def getNameValidator(cls):
        import taurusvalidator
        return taurusvalidator.AttributeNameValidator()
        
    # received configuration events
    def eventReceived(self, src, src_type, evt_value):
        """Method invoked by the configuration object when a configuration event
           is received. Default implementation propagates the event to all 
           listeners."""
        #self.fireEvent(src_type, evt_value)
        pass

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # Necessary to overwrite in subclass
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    def isNumeric(self):
        raise RuntimeError("Not allowed to call AbstractClass TaurusAttribute.isNumeric")
        
    def isBoolean(self):
        raise RuntimeError("Not allowed to call AbstractClass TaurusAttribute.isBoolean")
    
    def isState(self):
        raise RuntimeError("Not allowed to call AbstractClass TaurusAttribute.isState")

    def getDisplayValue(self,cache=True):
        raise RuntimeError("Not allowed to call AbstractClass TaurusAttribute.getDisplayValue")

    def encode(self, value):
        raise RuntimeError("Not allowed to call AbstractClass TaurusAttribute.encode")

    def decode(self, attr_value):
        raise RuntimeError("Not allowed to call AbstractClass TaurusAttribute.decode")

    def write(self, value, with_read=True):
        raise RuntimeError("Not allowed to call AbstractClass TaurusAttribute.write")

    def read(self, cache=True):
        raise RuntimeError("Not allowed to call AbstractClass TaurusAttribute.read")

    def poll(self):
        raise RuntimeError("Not allowed to call AbstractClass TaurusAttribute.poll")
            
    def _subscribeEvents(self):
        raise RuntimeError("Not allowed to call AbstractClass TaurusAttribute._subscribeEvents")
        
    def _unsubscribeEvents(self):
        raise RuntimeError("Not allowed to call AbstractClass TaurusAttribute._unsubscribeEvents")

    def isUsingEvents(self):
        raise RuntimeError("Not allowed to call AbstractClass TaurusAttribute.isUsingEvents")
        
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # TaurusModel necessary overwrite
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    def getValueObj(self, cache=True):
        try:
            return self.read(cache=cache)
        except Exception:
            return None

    def getDisplayDescrObj(self,cache=True):
        name = self.getLabel(cache=cache)
        if name:
            name += " (" + self.getNormalName().upper() + ")"
        else:
            name = self.getDisplayName(cache=cache)
        obj = [('name', name)]

        descr = self.getDescription(cache=cache)
        if descr and descr != self.no_description:
            obj.append(('description',descr.replace("<","&lt;").replace(">","&gt;")))
        
        unit = self.getUnit(cache=cache)
        if unit and unit != self.no_unit:
            obj.append(('unit', unit))
            
        limits = self.getRange(cache=cache)
        if limits and (limits[0] != self.no_min_value or \
                       limits[1] != self.no_max_value):
            if limits[0] == self.no_min_value: limits[0] = self.no_cfg_value
            if limits[1] == self.no_max_value: limits[1] = self.no_cfg_value
            obj.append(('limits', "[%s, %s]" % (limits[0],limits[1])))

        alarms = self.getAlarms(cache=cache)
        if alarms and (alarms[0] != self.no_min_alarm or \
                       alarms[1] != self.no_max_alarm):
            if alarms[0] == self.no_min_alarm: alarms[0] = self.no_cfg_value
            if alarms[1] == self.no_max_alarm: alarms[1] = self.no_cfg_value
            obj.append(('alarms', "[%s, %s]" % (alarms[0],alarms[1])))

        warnings = self.getWarnings(cache=cache)
        if warnings and (warnings[0] != self.no_min_warning or \
                         warnings[1] != self.no_max_warning):
            if warnings[0] == self.no_min_warning: warnings[0] = self.no_cfg_value
            if warnings[1] == self.no_max_warning: warnings[1] = self.no_cfg_value
            obj.append(('warnings', "[%s, %s]" % (warnings[0],warnings[1])))
        
        return obj
        
    def areStrValuesEqual(self,v1,v2):
        try:
            if "nan" == str(v1).lower() == str(v2).lower(): return True
            return self.encode(v1) == self.encode(v2)
        except:
            return False

    def getDisplayWriteValue(self,cache=True):
        if not self.isWritable():
            self.warning("requesting write value of a read-only attribute")
            return None

        attrvalue = self.getValueObj(cache=cache)
        if not attrvalue:
            return None
        
        v = attrvalue.w_value
        return self.displayValue(v)
        
    def displayValue(self,value):
        if value is None:
            return None
        ret = None
        try:
            if self.isScalar():
                fmt = self.getFormat()
                if self.isNumeric() and fmt is not None:
                    ret = fmt % value
                else:
                    ret = str(value)
            elif self.isSpectrum():
                ret = str(value)
            else:
                ret = str(value)
        except:
            # if cannot calculate value based on the format just return the value
            ret = str(value)
        return ret
    
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # API for listeners
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-    
    
    def hasEvents(self):
        self.deprecated("Don't use this anymore. Use isUsingEvents instead")
        return self.isUsingEvents()

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # Polling (client side)
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    
    def enablePolling(self, force=False):
        self.__enable_polling = True
        self.__forced_polling = force
        if force:
            self.__activate_polling = True
        
        if self.__activate_polling:
            self._activatePolling()
    
    def disablePolling(self):
        self.__enable_polling = False
        self.__forced_polling = False
        if self.__activate_polling:
            self._deactivatePolling()
            
    def isPollingEnabled(self):
        return self.__enable_polling
        
    def _activatePolling(self):
        self.__activate_polling = True
        if not self.isPollingEnabled():
            return
        self.factory().addAttributeToPolling(self, self.getPollingPeriod())
        self.__polled = True
    
    def _deactivatePolling(self):
        self.__activate_polling = False
        self.factory().removeAttributeFromPolling(self)
        self.__polled = False
    
    def isPollingActive(self):
        return self.__polled
    
    def isPollingForced(self):
        return self.__forced_polling
    
    def changePollingPeriod(self, period):
        """change polling period to period miliseconds """
        if self.__polling_period == period and self.__activate_polling:
            return
            
        self.__polling_period = period
        if self.__activate_polling:
            self._deactivatePolling()
            self._activatePolling()

    def isPolled(self):
        self.deprecated("use isPollingActive()")
        return self.isPollingActive()
    
    def getPollingPeriod(self):
        """returns the polling period """
        return self.__polling_period

    # The following are deprecated and maintained only for compatibility

    def activatePolling(self, period, unsubscribe_evts=False, force=False):
        """activate polling for attribute.
        
           :param period: polling period (in miliseconds)
           :type period: int
        """
        ## REENABLED, used to solve problems with ID GUI's and other systems where event independency is needed.
        #self.deprecated("use changePollingPeriod(). Not exactly the same functionality. Only activates polling if necessary")
        self.changePollingPeriod(period)
        self.enablePolling(force=force)

    def deactivatePolling(self, maintain_enabled=False):
        """unregister attribute from polling"""
        self.deprecated("use disablePolling()")
        self.disablePolling()
            
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # API for attribute configuration
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-    

    def _getRealConfig(self):
        """ Returns the current configuration of the attribute."""
        raise RuntimeError("Not allowed to call AbstractClass TaurusAttribute::_getRealConfig")

    def getConfig(self):
        """ Returns the current configuration of the attribute."""
        try:
            ob = None
            ob = self.__weakFakeConfigObj()
        except Exception:
            pass

        if ob is not None:
            return ob

        ob = TaurusConfigurationProxy(self)
        self.__weakFakeConfigObj = weakref.ref(ob)
        return ob
    
    def isWritable(self, cache=True):
        return not self._getRealConfig().isReadOnly(cache=cache)
    
    def isWrite(self, cache=True):
        return self._getRealConfig().isWrite(cache=cache)
    
    def isReadOnly(self, cache=True):
        return self._getRealConfig().isReadOnly(cache=cache)

    def isReadWrite(self, cache=True):
        return self._getRealConfig().isReadWrite(cache=cache)

    def getWritable(self, cache=True):
        return self._getRealConfig().getWritable(cache=cache)


class TaurusStateAttribute(TaurusAttribute):
    """ """
    
    def __init__(self, name, parent, **kwargs):
        self.call__init__(TaurusAttribute, name, parent, **kwargs)
        
    def isInformDeviceOfErrors(self):
        return True

#del weakef
#del TaurusModel
#del TaurusConfigurationProxy
