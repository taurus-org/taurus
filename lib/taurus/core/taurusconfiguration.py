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

"""This module contains the base class for a taurus attribute configuration"""

__all__ = ["TaurusConfigurationProxy", "TaurusConfiguration"]

__docformat__ = "restructuredtext"

# -*- coding: utf-8 -*-
import time
import weakref

from enums import TaurusEventType
import taurusmodel

class TaurusConfigurationProxy(object):
    """
    TaurusAttribute has a reference to TaurusConfiguration and it should also have
    a reference to TaurusAttribute. To solve this cyclic dependency,
    TaurusConfiguration has a weak reference to TaurusAttribute. But then we must
    be sure that no other references to TaurusConfiguration exist so that
    no one tries to use it after its TaurusAttribute has disappeared.
    That's why to the outside world we don't give acces to it directly
    but to objects of this new TaurusConfigurationProxy class.
    """
    def __init__(self, parent):
        self.__parent = parent

    def __getattr__(self, name):
        return getattr(self.__parent._getRealConfig(), name)


class TaurusConfiguration(taurusmodel.TaurusModel):
    
    no_cfg_value = '-----'
    no_unit = 'No unit'
    no_standard_unit = 'No standard unit'
    no_display_unit = 'No display unit'
    no_description = 'No description'
    not_specified = 'Not specified'
    no_min_value = no_max_value = not_specified
    no_min_alarm = no_max_alarm = not_specified
    no_min_warning = no_max_warning = not_specified
    no_delta_t = no_delta_val = not_specified
    no_rel_change = no_abs_change = not_specified
    no_archive_rel_change = no_archive_abs_change = not_specified
    no_archive_period = not_specified
    
    DftTimeToLive = 10000 # 10s
    
    def __init__(self, name, parent, storeCallback = None):
    
        # the last configuration value
        self._attr_info  = None
        
        # the last time the configuration was read
        self._attr_timestamp = 0
        
        # the configuration event identifier
        self._cfg_evt_id = None

        self.call__init__(taurusmodel.TaurusModel, name, parent)
        
        # Everything went ok so now we are sure we can store the object
        if not storeCallback is None:
            storeCallback(self.getFullName(),self)
        
        self._dev_hw_obj = self._getDev().getHWObj()
            
        self._subscribeEvents()
    
    def cleanUp(self):
        self.trace("[TaurusConfiguration] cleanUp")
        self._unsubscribeEvents()
        self._attr_info = None
        self._dev_hw_obj = None
        taurusmodel.TaurusModel.cleanUp(self)        
        
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # TaurusModel implementation
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-    

    def getTaurusElementType(self):
        import taurus.core
        return taurus.core.TaurusElementType.Configuration

    @classmethod
    def buildModelName(cls, parent_model, relative_name):
        """build an 'absolute' model name from the parent model and the 'relative'
        name. 
        - If parent_model is a TaurusAttribute, the return is a composition of
        the database model name and is device name
        - If parent_model is a TaurusConfiguration, the relative name is ignored and
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
        return taurusvalidator.ConfigurationNameValidator()
    
    def _getDevName(self):
        params = self.getNameValidator().getParams(self.getFullName())
        return params.get('devicename') or params.get('devalias')
    
    def _getFullAttrName(self):
        params = self.getNameValidator().getParams(self.getFullName())
        ret = params.get('devicename') or params.get('devalias')
        ret += '/' + params.get('attributename')
        return ret

    def _getAttrName(self):
        return self.getNameValidator().getParams(self.getFullName()).get('attributename')
         
    def _getDev(self):
        dev = None
        attrObj = self.getParentObj()
        if attrObj is None or attrObj.getParent() is None:
            devname = self._getDevName()
            dev = self.factory().getDevice(devname)
        else:
            dev = attrObj.getParent()
        return dev
    
    def _getAttr(self, createAttr=False):
        attrObj = self.getParentObj()
        if attrObj is None:
            attrname = self._getFullAttrName()
            if createAttr:
                attrObj = self.factory().getAttribute(attrname)
            else:
                attrObj = self.factory().getExistingAttribute(attrname)
        return attrObj
    
    def getValueObj(self, cache=True):
        """ Returns the current configuration for the attribute.
            if cache is set to True (default) and the the configuration has 
            events active then it will return the local cached value. Otherwise
            it will read from the tango layer."""
        raise RuntimeException("May not be called in abstract TaurusConfiguration")
    
    def getDisplayValue(self,cache=True):
        confvalue = self.getValueObj(cache=cache)
        if not confvalue:
            return None
        return confvalue.label

    def getDisplayDescription(self,cache=True):
        return self.getDescription(cache)

    def getDisplayDescrObj(self,cache=True):
        attrObj = self.getParentObj()
        if attrObj is None:
            return [('name', self.getLabel(cache=cache))]
        return attrObj.getDisplayDescrObj(cache=cache)
    
    def isWritable(self):
        return True
    
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # API for listeners
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-    s

#    def addListener(self, listener):
#        """ Add a TaurusListener object in the listeners list.
#            If the listener is already registered nothing happens."""
#        ret = taurusmodel.TaurusModel.addListener(self, listener)
#        if not ret:
#            return ret
        
#        #fire a first configuration event
#        self.fireEvent(TaurusEventType.Config, self._attr_info, listener) 
#        return ret
    
    def hasEvents(self):
        self.deprecated("Don't use this anymore. Use isUsingEvents instead")
        return self.isUsingEvents()

    def isUsingEvents(self):
        return self._cfg_evt_id

    def isWritable(self, cache=True):
        return not self.isReadOnly(cache)
    
    def getWritable(self, cache=True):
        c = self.getValueObj(cache=cache)
        if c:
            return c.writable
        return None
    
    def getType(self, cache=True):
        c = self.getValueObj(cache=cache)
        if c:
            return c.data_type
        return None

    def getDataFormat(self, cache=True):
        c = self.getValueObj(cache=cache)
        if c:
            return c.data_format
        return None

    def getMaxDimX(self, cache=True):
        c = self.getValueObj(cache=cache)
        if c:
            return c.max_dim_x
        return None

    def getMaxDimY(self, cache=True):
        c = self.getValueObj(cache=cache)
        if c:
            return c.max_dim_y
        return None
        
    def getShape(self, cache=True):
        # force a read if not using cache. Then use cache until the
        # end of the method
        if not cache: self.getDataFormat(cache=cache)
        
        if self.isScalar():
            return ()
        elif self.isSpectrum():
            return (self.getMaxDimX(),)
        else:
            return (self.getMaxDimX(), self.getMaxDimY())
        
    def getDescription(self, cache=True):
        c = self.getValueObj(cache=cache)
        if c:
            return c.description
        return None
        
    def getLabel(self, cache=True):
        c = self.getValueObj(cache=cache)
        if c:
            return c.label
        return None
    
    def getUnit(self, cache=True):
        c = self.getValueObj(cache=cache)
        if c:
            return c.unit
        return None
    
    def getStandardUnit(self, cache=True):
        c = self.getValueObj(cache=cache)
        if c:
            return c.standard_unit
        return None
        
    def getDisplayUnit(self, cache=True):
        c = self.getValueObj(cache=cache)
        if c:
            return c.display_unit
        return None

    def getFormat(self, cache=True):
        c = self.getValueObj(cache=cache)
        if c:
            return c.format
        return None
        
    def getMinValue(self, cache=True):
        c = self.getValueObj(cache=cache)
        if c:
            return c.min_value
        return None

    def getMaxValue(self, cache=True):
        c = self.getValueObj(cache=cache)
        if c:
            return c.max_value
        return None
        
    def getLimits(self, cache=True):
        c = self.getValueObj(cache=cache)
        if c:
            return c.climits
        return None
    
    def getRanges(self, cache=True):
        c = self.getValueObj(cache=cache)
        if c:
            return list(c.cranges)
        return None
    
    def getMinAlarm(self, cache=True):
        c = self.getValueObj(cache=cache)
        if c:
            return c.min_alarm
        return None

    def getMaxAlarm(self, cache=True):
        c = self.getValueObj(cache=cache)
        if c:
            return c.max_alarm
        return None
        
    def getAlarms(self, cache=True):
        c = self.getValueObj(cache=cache)
        if c:
            return list(c.calarms)
        return None
    
    def getMinWarning(self, cache=True):
        c = self.getValueObj(cache=cache)
        if c:
            return c.alarms.min_warning
        return None

    def getMaxWarning(self, cache=True):
        c = self.getValueObj(cache=cache)
        if c:
            return c.alarms.max_warning
        return None
        
    def getWarnings(self, cache=True):
        c = self.getValueObj(cache=cache)
        if c:
            return list(c.cwarnings)
        return None        
    
    def getParam(self, param_name):
        config = self.getValueObj()
        if config:
            try:
                return getattr(config, param_name)
            except:
                return None
    
    def setParam(self, param_name, value):
        config = self.getValueObj()
        if config and self.getParam(param_name):
            setattr(config, param_name, value)
            self._applyConfig()
    
    def setDescription(self,descr):
        config = self.getValueObj()
        if config:
            config.description = description
            self._applyConfig()

    def setLabel(self,lbl):
        config = self.getValueObj()
        if config:
            config.label = lbl
            self._applyConfig()

    def setUnit(self,unit):
        config = self.getValueObj()
        if config:
            config.unit = unit
            self._applyConfig()

    def setStandardUnit(self,standard_unit):
        config = self.getValueObj()
        if config:
            config.standard_unit = standard_unit
            self._applyConfig()
        
    def setDisplayUnit(self,display_unit):
        config = self.getValueObj()
        if config:
            config.display_unit = display_unit
            self._applyConfig()
    
    def setFormat(self,fmt):
        config = self.getValueObj()
        if config:
            config.format = fmt
            self._applyConfig()
        
    def setLimits(self,low, high):
        config = self.getValueObj()
        if config:
            l_str, h_str = str(low), str(high)
            config.cranges[0] = config.min_value = l_str
            config.cranges[5] = config.max_value = h_str
            config.climits = [l_str, h_str]
            self._applyConfig()

    def setWarnings(self,low, high):
        config = self.getValueObj()
        if config:
            l_str, h_str = str(low), str(high)
            config.cranges[2] = config.alarms.min_warning = l_str
            config.cranges[3] = config.alarms.max_warning = h_str
            config.cwarnings = [l_str, h_str]
            self._applyConfig()

    def setAlarms(self,low, high):
        config = self.getValueObj()
        if config:
            l_str, h_str = str(low), str(high)
            config.cranges[1] = config.min_alarm = config.alarms.min_alarm = l_str
            config.cranges[4] = config.max_alarm = config.alarms.max_alarm = h_str
            config.calarms = [l_str, h_str]
            self._applyConfig()

    def _applyConfig(self):
        config = self.getValueObj()
        if config:
            self.getParentObj().setConfigEx(config)


