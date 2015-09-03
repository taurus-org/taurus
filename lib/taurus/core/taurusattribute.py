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

__all__ = ["TaurusAttribute"]

__docformat__ = "restructuredtext"

import weakref

from .taurushelper import Factory
from .taurusmodel import TaurusModel
from taurus.core.taurusbasetypes import TaurusElementType, DataFormat


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
    _description = "A Taurus Attribute"

    def __init__(self, name, parent, **kwargs):
        self.call__init__(TaurusModel, name, parent)

        # just to keep it alive
        self.__parentDevice = parent

        # User enabled/disabled polling
        self.__enable_polling = kwargs.get('enablePolling', True)

        # attribute should be polled.
        # The attribute is polled only if the polling is also enabled
        self.__activate_polling = False

        # Indicates if the attribute is being polled periodically
        # In summary: polled = enable_polling and activate_polling
        self.__polled = False

        # current polling period
        self.__polling_period = kwargs.get("pollingPeriod", 3000)

        # stores if polling has been forced by user API
        self.__forced_polling = False

        # If everything went well, the object is stored
        storeCallback = kwargs.get("storeCallback", None)
        if not storeCallback is None:
            storeCallback(self)

        self.name = None
        self.writable = None
        self.data_format = None
        self.label = None
        self.type = None
        self.range = float('-inf'), float('inf')
        self.alarm = float('-inf'), float('inf')
        self.warning = float('-inf'), float('inf')

    def cleanUp(self):
        self.trace("[TaurusAttribute] cleanUp")
        self._unsubscribeEvents()
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
        """build an 'absolute' model name from the parent model and the
        'relative' name.
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

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # Necessary to overwrite in subclass
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    def isNumeric(self):
        raise NotImplementedError("Not allowed to call AbstractClass" +
                                  " TaurusAttribute.isNumeric")

    def isState(self):
        raise NotImplementedError("Not allowed to call AbstractClass" +
                                  " TaurusAttribute.isState")

    def encode(self, value):
        raise NotImplementedError("Not allowed to call AbstractClass" +
                                  " TaurusAttribute.encode")

    def decode(self, attr_value):
        raise NotImplementedError("Not allowed to call AbstractClass" +
                                  " TaurusAttribute.decode")

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
        '''Enable polling. See :meth:`isPollingEnabled` for clarification of
        what enabled polling means.

        :param force: (bool) True also activates polling 
                      (see: :meth:`activatePolling`)
        '''
        self.__enable_polling = True
        self.__forced_polling = force
        if force:
            self.__activate_polling = True

        if self.__activate_polling:
            self._activatePolling()

    def disablePolling(self):
        '''Disable polling and if polling is active also deactivate it.
        See :meth:`isPollingEnabled` for clarification of
        what enabled polling means.
        '''
        self.__enable_polling = False
        self.__forced_polling = False
        if self.__activate_polling:
            self._deactivatePolling()

    def isPollingEnabled(self):
        '''Indicate whether polling was activated/deactivated by user.
        Enabled polling does not mean that it is active - periodically poll
        the attribute. By default the attribute creation enables polling.

        :return: (bool) whether polling is enabled

        :see: :meth:`enablePolling`, :meth:`disablePolling`
        '''
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
        '''Indicate whether polling is active. Active polling means that
        a periodic timer poll the attribute. By default the attribute creation
        does not activate polling.

        :return: (bool) whether polling is active

        :see: :meth:`activatePolling`, :meth:`disablePolling`
        '''
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

    def activatePolling(self, period, unsubscribe_evts=False, force=False):
        """activate polling for attribute.

           :param period: polling period (in miliseconds)
           :type period: int
        """
        self.changePollingPeriod(period)
        self.enablePolling(force=force)

    def deactivatePolling(self, maintain_enabled=False):
        """unregister attribute from polling"""
        self.deprecated("use disablePolling()")
        self.disablePolling()

    def __str__(self):
        return self.getFullName()

    def getDisplayDescription(self, cache=True):
        return self.description

    def getDisplayDescrObj(self, cache=True):
        name = self.getLabel(cache=cache)
        obj = [('name', name)]
        descr = self.description
        if descr and descr != self.no_description:
            _descr = descr.replace("<", "&lt;").replace(">", "&gt;")
            obj.append(('description', _descr))

        limits = self.getRange(cache=cache)
        if limits and (limits[0] != self.no_min_value or \
                       limits[1] != self.no_max_value):
            if limits[0] == self.no_min_value:
                limits[0] = self.no_cfg_value
            if limits[1] == self.no_max_value:
                limits[1] = self.no_cfg_value
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
            if warnings[0] == self.no_min_warning:
                warnings[0] = self.no_cfg_value
            if warnings[1] == self.no_max_warning:
                warnings[1] = self.no_cfg_value
            obj.append(('warnings', "[%s, %s]" % (warnings[0],warnings[1])))

        return obj

    def isWritable(self, cache=True):
        return self.writable

    def getType(self, cache=True):
        return self.type

    def getDataFormat(self, cache=True):
        return self.data_format

    def getLabel(self, cache=True):
        return self.label

    def getMinValue(self, cache=True):
        return self.range[0]

    def getMaxValue(self, cache=True):
        return self.range[1]

    def getRange(self, cache=True):
        return self.range

    def getMinAlarm(self, cache=True):
        return self.alarm[0]

    def getMaxAlarm(self, cache=True):
        return self.alarm[1]

    def getAlarms(self, cache=True):
        return list(self.alarm)

    def getMinWarning(self, cache=True):
        return self.warning[0]

    def getMaxWarning(self, cache=True):
        return self.warning[1]

    def getWarnings(self, cache=True):
        return self.warning

    def setLabel(self, lbl):
        self.label = lbl

    def setRange(self, low, high):
        self.range = [low, high]

    def setWarnings(self, low, high):
        self.warning = [low, high]

    def setAlarms(self, low, high):
        self.alarm = [low, high]

    def isBoolean(self, cache=True):
        v = self.read(cache)
        return isinstance(v.rvalue, bool)

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, descr):
        self._description = descr
