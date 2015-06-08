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

"""This module contains the base class for a taurus attribute"""

__all__ = ["TaurusAttribute", "TaurusStateAttribute"]

__docformat__ = "restructuredtext"

import weakref

from .taurushelper import Factory
from .taurusmodel import TaurusModel
from taurus.core.taurusbasetypes import TaurusElementType

class TaurusAttribute(TaurusModel):

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

        #######################################################################
        # TaurusConfiguration Attributes

        # the last configuration value
        self._attr_info  = None
        # the last time the configuration was read
        self._attr_timestamp = 0
        # the configuration event identifier
        self._cfg_evt_id = None
        # Everything went ok so now we are sure we can store the object
#        if not storeCallback is None:
#            storeCallback(self.getFullName(),self)

        self._subscribeEvents()

    def cleanUp(self):
        self.trace("[TaurusAttribute] cleanUp")
        self._unsubscribeEvents()
        self._dev_hw_obj = None
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
        return TaurusElementType.Attribute
            
    @classmethod
    def buildModelName(cls, parent_model, relative_name):
        """build an 'absolute' model name from the parent model and the 'relative'
        name. 
        - If parent_model is a TaurusDevice, the return is a composition of
        the database model name and its device name
        - If parent_model is a TaurusAttribute, the relative name is ignored and
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
        return cls.factory().getAttributeNameValidator()
        
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
        
#    def isBoolean(self):
#        raise RuntimeError("Not allowed to call AbstractClass TaurusAttribute.isBoolean")
    
    def isState(self):
        raise RuntimeError("Not allowed to call AbstractClass TaurusAttribute.isState")

#    def getDisplayValue(self,cache=True):
#        raise RuntimeError("Not allowed to call AbstractClass TaurusAttribute.getDisplayValue")

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

#    def isUsingEvents(self):
#        raise RuntimeError("Not allowed to call AbstractClass TaurusAttribute.isUsingEvents")
        
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # TaurusModel necessary overwrite
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    def getValueObj(self, cache=True):
        try:
            return self.read(cache=cache)
        except Exception:
            return None
        
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
        
        v = attrvalue.wvalue
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
        
    def getConfig(self):
        """ Returns the current configuration of the attribute."""
        self.deprecated(dep='getConfig', alt='getValueObj', rel='taurus 4')
        return self.getValueObj(cache=True)

    ##########################################################################
    # TaurusConfiguration Methods
    
    def __str__(self):
        return self.getFullName()

    ##########################################################################
    # TODO: should be deleted in a second iteration
    def _getDevName(self):
        params = self.getNameValidator().getUriGroups(self.getFullName())
        return params.get('devname')

    def _getDev(self):
        dev = None
        attrObj = self.getParentObj()
        if attrObj is None or attrObj.getParent() is None:
            devname = self._getDevName()
            dev = self.factory().getDevice(devname)
        else:
            dev = attrObj.getParent()
        return dev

    def _getFullAttrName(self):
        # TODO the method has a wrong name
        return self.getNormalName()

    def _getAttrName(self):
        return self.getSimpleName()

    def _getAttr(self, createAttr=False):
        return self
    ##########################################################################
    
    def getDisplayValue(self,cache=True):
        return self.getLabel(cache)

    def getDisplayDescription(self,cache=True):
        return self.getDescription(cache)

    def getDisplayDescrObj(self,cache=True):
        name = self.getLabel(cache=cache)
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

    def isUsingEvents(self):
        return self._cfg_evt_id

    def isWritable(self, cache=True):
        v = self.getValueObj(cache)
        if v is None:
            raise RuntimeError('Cannot access the config Value')
        return v.isWritable()

    def getWritable(self, cache=True):
        '''deprecated'''
        self.deprecated(dep='getWritable', alt='isWritable', rel='taurus 4')
        return self.isWritable(cache)

    def getType(self, cache=True):
        v = self.getValueObj(cache)
        if v:
            return v.type
        return None

    def getDataFormat(self, cache=True):
        v = self.getValueObj(cache)
        if v:
            return v.data_format
        return None

    def getMaxDim(self, cache=True):
        v = self.getValueObj(cache)
        if v:
            return v.max_dim
        return None

    def getMaxDimX(self, cache=True):
        '''.. warning: Deprecated. Use :meth:`getMaxDim`
        '''
        self.deprecated(dep='getMaxDimX', alt='getMaxDim')
        dim = self.getMaxDim(cache)
        if dim:
            return dim[0]
        else:
            return None

    def getMaxDimY(self, cache=True):
        '''.. warning: Deprecated. Use :meth:`getMaxDim`
        '''
        self.deprecated(dep='getMaxDimY', alt='getMaxDim')
        dim = self.getMaxDim(cache)
        if dim:
            return dim[1]
        else:
            return None

    def getShape(self, cache=True):
        if self.isScalar(cache):
            return ()
        elif self.isSpectrum():
            return (self.getMaxDimX(),)
        else:
            return self.getMaxDim()

    def getDescription(self, cache=True):
        v = self.getValueObj(cache)
        if v:
            return v.description
        return None

    def getLabel(self, cache=True):
        v = self.getValueObj(cache)
        if v:
            return v.label
        return None

    def getUnit(self, cache=True):
        self.deprecated(dep='getUnit', alt='TaurusAttrValue.rvalue.units',
                        rel='taurus 4')
        try:
            return str(self.getValueObj(cache).rvalue.units)
        except:
            return None

    def getStandardUnit(self, cache=True):
        self.deprecated(dep='getStandardUnit',
                        alt='TaurusAttrValue.rvalue.units',
                        rel='taurus 4')
        try:
            return str(self.getValueObj(cache).rvalue.units)
        except:
            return None

    def getDisplayUnit(self, cache=True):
        self.deprecated(dep='getDisplayUnit',
                        alt='TaurusAttrValue.rvalue.units',
                        rel='taurus 4')
        try:
            return str(self.getValueObj(cache).rvalue.units)
        except:
            return None

    def getFormat(self, cache=True):
        v = self.getValueObj(cache)
        if v:
            return v.format
        return None

    def getMinValue(self, cache=True):
        v = self.getValueObj(cache)
        if v:
            return v.range[0]
        return None

    def getMaxValue(self, cache=True):
        v = self.getValueObj(cache)
        if v:
            return v.range[1]
        return None

    def getLimits(self, cache=True):
        '''.. warning: Deprecated. Use :meth:`getRange`
        '''
        self.info('Deprecation warning: TaurusConfiguration.getLimits is deprecated. Use getRange')
        self.getRange(cache=cache)

    def getRange(self, cache=True):
        v = self.getValueObj(cache)
        if v:
            return v.range
        return None

    def getRanges(self, cache=True):
        '''.. warning: Deprecated. Use :meth:`getRange`
        '''
        self.info('Deprecation warning: TaurusConfiguration.getRanges is deprecated. Use getRange')
        v = self.getValueObj(cache)
        if v:
            return [v.range[0], v.alarm[0], v.warning[0], v.warning[1],
                    v.alarm[1], v.range[1]]
        return None

    def getMinAlarm(self, cache=True):
        v = self.getValueObj(cache)
        if v:
            return v.alarm[0]
        return None

    def getMaxAlarm(self, cache=True):
        v = self.getValueObj(cache)
        if v:
            return v.alarm[1]
        return None

    def getAlarms(self, cache=True):
        v = self.getValueObj(cache)
        if v:
            return list(v.alarm)
        return None

    def getMinWarning(self, cache=True):
        v = self.getValueObj(cache)
        if v:
            return v.warning[0]
        return None

    def getMaxWarning(self, cache=True):
        v = self.getValueObj(cache)
        if v:
            return v.warning[1]
        return None

    def getWarnings(self, cache=True):
        v = self.getValueObj(cache)
        if v:
            return v.warning
        return None

    def getParam(self, param_name):
        v = self.getValueObj(True)
        try:
            return getattr(v, param_name)
        except:
            return None

    def setParam(self, param_name, value):
        v = self.getValueObj()
        if v and self.getParam(param_name):
            setattr(v, param_name, value)
            self._applyConfig()

    def setDescription(self, descr):
        v = self.getValueObj()
        if v:
            v.description = descr
            self._applyConfig()

    def setLabel(self, lbl):
        v = self.getValueObj()
        if v:
            v.label = lbl
            self._applyConfig()

    def setUnit(self, unit):
        v = self.getValueObj()
        if v:
            v.unit = unit
            self._applyConfig()

    def setStandardUnit(self, standard_unit):
        v = self.getValueObj()
        if v:
            v.standard_unit = standard_unit
            self._applyConfig()

    def setDisplayUnit(self, display_unit):
        v = self.getValueObj()
        if v:
            v.display_unit = display_unit
            self._applyConfig()

    def setFormat(self, fmt):
        v = self.getValueObj()
        if v:
            v.format = fmt
            self._applyConfig()

    def setLimits(self, low, high):
        '''.. warning: Deprecated. Use :meth:`setRange`
        '''
        self.info('Deprecation warning: TaurusConfiguration.setLimits is deprecated. Use setRange')
        self.setRange(low, high)

    def setRange(self, low, high):
        v = self.getValueObj()
        if v:
            v.range = [low, high]
            self._applyConfig()

    def setWarnings(self, low, high):
        v = self.getValueObj()
        if v:
            v.warning = [low, high]
            self._applyConfig()

    def setAlarms(self, low, high):
        v = self.getValueObj()
        if v:
            v.alarm = [low, high]
            self._applyConfig()

    def _applyConfig(self):
        pass

    def isBoolean(self, cache=True):
        # TODO it should be implemented in TaurusAttrValue
        v = self.read(cache)
        return isinstance(v.rvalue, bool)

    def isScalar(self, cache=True):
        return self.read(cache).isScalar()

    def isSpectrum(self, cache=True):
        return self.read(cache).isSpectrum()

    def isImage(self, cache=True):
        return self.read(cache).isImage()

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

class TaurusStateAttribute(TaurusAttribute):
    """ """
    
    def __init__(self, name, parent, **kwargs):
        self.call__init__(TaurusAttribute, name, parent, **kwargs)
        
    def isInformDeviceOfErrors(self):
        return True

#del weakef
#del TaurusModel
#del TaurusConfigurationProxy
