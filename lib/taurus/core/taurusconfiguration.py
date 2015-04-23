#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

"""This module contains the base class for a taurus attribute configuration"""

__all__ = ["TaurusConfigurationProxy", "TaurusConfiguration"]

__docformat__ = "restructuredtext"

from .taurusbasetypes import AttrAccess, TaurusElementType
from .taurusmodel import TaurusModel
from .taurushelper import Factory

from taurus import tauruscustomsettings


class TaurusConfigurationProxy(object):
    """
    TaurusAttribute has a reference to TaurusConfiguration and it should also have
    a reference to TaurusAttribute. To solve this cyclic dependency,
    TaurusConfiguration has a weak reference to TaurusAttribute. But then we must
    be sure that no other references to TaurusConfiguration exist so that
    no one tries to use it after its TaurusAttribute has disappeared.
    That's why to the outside world we don't give access to it directly
    but to objects of this new TaurusConfigurationProxy class.
    """
    def __init__(self, parent):
        self.__parent = parent

    def __getattr__(self, name):
        return getattr(self.__parent._getRealConfig(), name)
    
    def getRealConfigClass(self):
        return self.__parent._getRealConfig().__class__


class TaurusConfiguration(TaurusModel):
    
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

        self.call__init__(TaurusModel, name, parent)
        
        # Everything went ok so now we are sure we can store the object
        if not storeCallback is None:
            storeCallback(self.getFullName(),self)
        
        self._dev_hw_obj = self._getDev().getHWObj()
            
        self._subscribeEvents()

    def __str__(self):
        return self.getFullName()
        
    def _subscribeEvents(self):
        pass
    
    def cleanUp(self):
        self.trace("[TaurusConfiguration] cleanUp")
        self._unsubscribeEvents()
        self._attr_info = None
        self._dev_hw_obj = None
        TaurusModel.cleanUp(self)        

    @classmethod
    def factory(cls):
        if cls._factory is None:
            cls._factory = Factory(scheme=cls._scheme)
        return cls._factory
        
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # TaurusModel implementation
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-    

    @classmethod
    def getTaurusElementType(cls):
        return TaurusElementType.Configuration

    @classmethod
    def buildModelName(cls, parent_model, relative_name):
        """build an 'absolute' model name from the parent model and the 'relative'
        name. 
        - If parent_model is a TaurusAttribute, the return is a composition of
        the database model name and is device name
        - If parent_model is a TaurusConfiguration, the relative name is ignored and
        the parent name is returned
        
        Note: This is a basic implementation. You may need to reimplement this 
              for a specific scheme if it supports "useParentModel". 
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
        return cls.factory().getConfigurationNameValidator()
    
    def _getDevName(self):
        params = self.getNameValidator().getUriGroups(self.getFullName())
        return params.get('devname')
    
    def _getFullAttrName(self):
        params = self.getNameValidator().getUriGroups(self.getFullName())
        return '%s/%s' % (params.get('devname'), params.get('_shortattrname'))

    def _getAttrName(self):
        return self.getNameValidator().getUriGroups(self.getFullName()).get('_shortattrname')
         
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
            attrObj = self.factory().getAttribute(attrname,
                                                  create_if_needed=createAttr)
        return attrObj
    
    def getValueObj(self, cache=True):
        """ Returns the current configuration for the attribute."""
        raise RuntimeError("May not be called in abstract TaurusConfiguration")
    
    def getDisplayValue(self,cache=True):
        confvalue = self.getValueObj(cache=cache)
        if not confvalue:
            return None
        return confvalue.label

    def getDisplayDescription(self,cache=True):
        return self.getDescription(cache)
    
    def getDisplayDescrObj(self,cache=True):
        name = self.getLabel(cache=cache)
        attrObj = self.getParentObj()
        if attrObj is not None:
            if name:
                name += " (" + attrObj.getNormalName() + ")"
            else:
                name = attrObj.getDisplayName(cache=cache)
        obj = [('name', name)]

        descr = self.getDescription(cache=cache)
        if descr and descr != self.no_description:
            obj.append(('description',descr.replace("<","&lt;").replace(">","&gt;")))
            
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
    
#    def isWritable(self):
#        return True
    
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # API for listeners
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-    s

#    def addListener(self, listener):
#        """ Add a TaurusListener object in the listeners list.
#            If the listener is already registered nothing happens."""
#        ret = TaurusModel.addListener(self, listener)
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
        c = self.getValueObj(cache=cache)
        if c is None:
            raise RuntimeError('Cannot access the config Value')
        return c.writable
        
    def getWritable(self, cache=True):
        '''deprecated'''
        self.deprecated(dep='getWritable', alt='isWritable', rel='taurus 4')
        return self.isWritable(cache)
    
    def getType(self, cache=True):
        c = self.getValueObj(cache=cache)
        if c:
            return c.type
        return None

    def getDataFormat(self, cache=True):
        c = self.getValueObj(cache=cache)
        if c:
            return c.data_format
        return None

    def getMaxDim(self, cache=True):
        c = self.getValueObj(cache=cache)
        if c:
            return c.max_dim
        return None

    def getMaxDimX(self, cache=True):
        '''.. warning: Deprecated. Use :meth:`getMaxDim`
        '''
        self.deprecated(dep='getMaxDimX', alt='getMaxDim')
        c = self.getValueObj(cache=cache)
        if c:
            return c.max_dim[0]
        return None

    def getMaxDimY(self, cache=True):
        '''.. warning: Deprecated. Use :meth:`getMaxDim`
        '''
        self.deprecated(dep='getMaxDimY', alt='getMaxDim')
        c = self.getValueObj(cache=cache)
        if c:
            return c.max_dim[1]
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
        self.deprecated(dep='getUnit', alt='TaurusAttrValue.rvalue.units',
                        rel='taurus 4')
        try:
            return str(self._getAttr().read().rvalue.units)
        except:
            return None
    
    def getStandardUnit(self, cache=True):
        self.deprecated(dep='getStandardUnit', 
                        alt='TaurusAttrValue.rvalue.units',
                        rel='taurus 4')
        try:
            return str(self._getAttr().read().rvalue.units)
        except:
            return None
        
    def getDisplayUnit(self, cache=True):
        self.deprecated(dep='getDisplayUnit', 
                        alt='TaurusAttrValue.rvalue.units',
                        rel='taurus 4')
        try:
            return str(self._getAttr().read().rvalue.units)
        except:
            return None

    def getFormat(self, cache=True):
        c = self.getValueObj(cache=cache)
        if c:
            return c.format
        return None
        
    def getMinValue(self, cache=True):
        c = self.getValueObj(cache=cache)
        if c:
            return c.range[0]
        return None

    def getMaxValue(self, cache=True):
        c = self.getValueObj(cache=cache)
        if c:
            return c.range[1]
        return None
        
    def getLimits(self, cache=True):
        '''.. warning: Deprecated. Use :meth:`getRange`
        '''
        self.info('Deprecation warning: TaurusConfiguration.getLimits is deprecated. Use getRange')
        self.getRange(cache=cache)
    
    def getRange(self, cache=True):
        c = self.getValueObj(cache=cache)
        if c:
            return c.range
        return None
    
    def getRanges(self, cache=True):
        '''.. warning: Deprecated. Use :meth:`getRange`
        '''
        self.info('Deprecation warning: TaurusConfiguration.getRanges is deprecated. Use getRange')
        c = self.getValueObj(cache=cache)
        if c:
            return [c.range[0], c.alarm[0], c.warning[0], c.warning[1], c.alarm[1], c.range[1]]
        return None
    
    def getMinAlarm(self, cache=True):
        c = self.getValueObj(cache=cache)
        if c:
            return c.alarm[0]
        return None

    def getMaxAlarm(self, cache=True):
        c = self.getValueObj(cache=cache)
        if c:
            return c.alarm[1]
        return None
    
    def getAlarms(self, cache=True):
        c = self.getValueObj(cache=cache)
        if c:
            return list(c.alarm)
        return None
    
    def getMinWarning(self, cache=True):
        c = self.getValueObj(cache=cache)
        if c:
            return c.warning[0]
        return None

    def getMaxWarning(self, cache=True):
        c = self.getValueObj(cache=cache)
        if c:
            return c.warning[1]
        return None
        
    def getWarnings(self, cache=True):
        c = self.getValueObj(cache=cache)
        if c:
            return list(c.warning)
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
            config.description = descr
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
        
    def setLimits(self, low, high):
        '''.. warning: Deprecated. Use :meth:`setRange`
        '''
        self.info('Deprecation warning: TaurusConfiguration.setLimits is deprecated. Use setRange')
        self.setRange(low, high)
            
    def setRange(self,low, high):
        config = self.getValueObj()
        if config:
            config.range = [low, high]
            self._applyConfig()

    def setWarnings(self,low, high):
        config = self.getValueObj()
        if config:
            config.warning = [low, high]
            self._applyConfig()

    def setAlarms(self,low, high):
        config = self.getValueObj()
        if config:
            config.alarm = [low, high]
            self._applyConfig()

    def _applyConfig(self):
        pass

    def isBoolean(self, cache=True):
        attr = self.getParentObj()
        if attr is None: return False
        v = attr.read(cache=cache)
        return isinstance(v.rvalue, bool)

    def isScalar(self, cache=True):
        attr = self.getParentObj()
        if attr is None: return False
        v = attr.read(cache=cache).rvalue
        m = getattr(v, 'magnitude', v) 
        import numpy
        return numpy.isscalar(m)
    
    def isSpectrum(self, cache=True):
        attr = self.getParentObj()
        if attr is None: return False
        v = attr.read(cache=cache).rvalue
        m = getattr(v, 'magnitude', v)
        import numpy
        return not numpy.isscalar(m) and numpy.array(m).ndim == 1
    
    def isImage(self, cache=True):
        attr = self.getParentObj()
        if attr is None: return False
        v = attr.read(cache=cache).rvalue
        m = getattr(v, 'magnitude', v)
        import numpy
        return not numpy.isscalar(m) and numpy.array(m).ndim == 2
    
    def isWrite(self, cache=True):
        '''deprecated'''
        self.deprecated(dep='isWrite', alt='isWritable', rel='taurus 4')
        return self.isWritable(cache)
    
    def isReadOnly(self, cache=True):
        '''deprecated'''
        self.deprecated(dep='isReadOnly', alt='isWritable', rel='taurus 4')
        return not self.isWritable(cache)

    def isReadWrite(self, cache=True):
        '''deprecated'''
        self.deprecated(dep='isReadWrite', alt='isWritable', rel='taurus 4')
        return self.isWritable(cache)
    
    
    
    
    
    

#del AttrAccess
#del TaurusModel
