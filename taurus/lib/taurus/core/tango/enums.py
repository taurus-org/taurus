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

"""This module contains all basic tango enumerations"""

__all__ = ["TangoObjectType", "EVENT_TO_POLLING_EXCEPTIONS",
           "FROM_TANGO_TO_NUMPY_TYPE", "FROM_TANGO_TO_STR_TYPE"]

__docformat__ = "restructuredtext"

from taurus.core.taurusbasetypes import SubscriptionState
from taurus.core.util.enumeration import Enumeration

TangoObjectType = Enumeration("TangoObjectType", 
                              ["Database", "Server", "Class", "Device", 
                               "Attribute","Property","Configuration",
                               "Object"])

import numpy
import PyTango

# The exception reasons that will force switching from events to polling
# API_AttributePollingNotStarted - the attribute does not support events. 
#                                  Don't try to resubscribe.
# API_DSFailedRegisteringEvent - same exception then the one above but higher
#                                in the stack
# API_NotificationServiceFailed - Problems in notifd, it was not able to
#                                 register the event.
# API_EventChannelNotExported - the notifd is not running
# API_EventTimeout - after a successfull register the the device server 
#                    and/or notifd shuts down/crashes
# API_CommandNotFound - Added on request from ESRF (Matias Guijarro). They have
#                       a DS in java (doesn't have events) and the only way they
#                       found to fix the event problem was to add this exception
#                       type here. Maybe in future this will be solved in a better
#                       way
# API_BadConfigurationProperty - the device server is not running
EVENT_TO_POLLING_EXCEPTIONS = ('API_AttributePollingNotStarted',
                               'API_DSFailedRegisteringEvent',
                               'API_NotificationServiceFailed',
                               'API_EventChannelNotExported',
                               'API_EventTimeout',
                               'API_EventPropertiesNotSet',
                               'API_CommandNotFound',
)
#                                   'API_BadConfigurationProperty')    

FROM_TANGO_TO_NUMPY_TYPE = {
   PyTango.DevBoolean : numpy.bool8,
     PyTango.DevUChar : numpy.ubyte,
     PyTango.DevShort : numpy.short,
    PyTango.DevUShort : numpy.ushort,
      PyTango.DevLong : numpy.int32,
     PyTango.DevULong : numpy.uint32,
    PyTango.DevLong64 : numpy.int64,
   PyTango.DevULong64 : numpy.uint64,
    PyTango.DevString : numpy.str,
    PyTango.DevDouble : numpy.float64,
     PyTango.DevFloat : numpy.float32,
}

FROM_TANGO_TO_STR_TYPE = {
   PyTango.DevBoolean : 'bool8',
   PyTango.DevUChar : 'ubyte',
   PyTango.DevShort : 'short',
   PyTango.DevUShort : 'ushort',
   PyTango.DevLong : 'int32',
   PyTango.DevULong : 'uint32',
   PyTango.DevLong64 : 'int64',
   PyTango.DevULong64 : 'uint64',
   PyTango.DevString : 'str',
   PyTango.DevDouble : 'float64',
   PyTango.DevFloat : 'float32',
}
