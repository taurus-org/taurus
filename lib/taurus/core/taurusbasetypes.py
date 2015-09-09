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
a misc collection of basic types
'''

__all__ = ["TaurusSWDevState", "TaurusSWDevHealth", "OperationMode",
           "TaurusSerializationMode", "SubscriptionState", "TaurusEventType",
           "MatchLevel", "TaurusElementType", "LockStatus", "DataFormat",
           "AttrQuality", "AttrAccess", "DisplayLevel", "ManagerState",
           "TaurusTimeVal", "TaurusAttrValue", "TaurusConfigValue", "DataType",
           "TaurusLockInfo", "DevState", "TaurusDevState"]

__docformat__ = "restructuredtext"

import datetime

from .util.enumeration import Enumeration
from .util.log import tep14_deprecation
from taurus.external.enum import IntEnum

class TaurusDevState(IntEnum):
    """Enumeration of possible states of :class:`taurus.core.TaurusDevice`
    objects, as returned by :meth:`TaurusDevice.getDevState`."""
    # TODO: it could be extended for more detailed description using bit masks
    Ready = 1
    NotReady = 2
    Undefined = 4

# Deprecated enumeration. 
# According with TEP3, the logic of the OperationMode should be in the widgets
OperationMode = Enumeration(
'OperationMode', (
    'OFFLINE',
    'ONLINE'
))

TaurusSerializationMode = Enumeration(
'TaurusSerializationMode', (
    'Serial',
    'Concurrent'
))

TaurusEventType = Enumeration(
'TaurusEventType', (
    'Change',
    'Config',
    'Periodic',
    'Error'
))

MatchLevel = Enumeration(
'MatchLevel', (
    'ANY', 
    'SHORT', 
    'NORMAL', 
    'COMPLETE', 
    'SHORT_NORMAL', 
    'NORMAL_COMPLETE'
))

TaurusElementType = Enumeration(
'TaurusElementType', (
    'Unknown',
    'Name',
    'DeviceClass',
    'Device',
    'DeviceAlias',
    'Domain',
    'Family',
    'Member',
    'Server',
    'ServerName',
    'ServerInstance',
    'Exported',
    'Host',
    'Attribute',
    'AttributeAlias',
    'Command',
    'Property',
    'Configuration',
    'Authority'
))

LockStatus = Enumeration(
'LockStatus', (
    'Unlocked',
    'Locked',
    'LockedMaster',
    'Unknown'
))

DataFormat = Enumeration(
'DataFormat', (
    '_0D',
    '_1D',
    '_2D'
))

# TODO: Consider adding  Enum and Quantity to DataType enumeration ...
# TODO: ... and also to __PYTHON_TYPE_TO_TAURUS_DATATYPE

DataType = Enumeration(
'DataType', (
    'Integer', # Can be used in scheme-agnostic code
    'Float', # Can be used in scheme-agnostic code
    'String', # Can be used in scheme-agnostic code 
    'Boolean', # Can be used in scheme-agnostic code
    'Bytes', 
    'DevState', # This type is for Tango backwards-compat. Avoid using it
    'DevEncoded', # This type is for Tango backwards-compat. Avoid using it
    'Object' # use this for opaque py objects not described by any of the above
))
# monkey-patch DataType to provide from_python_type()
__PYTHON_TYPE_TO_TAURUS_DATATYPE = {
        str : DataType.String,
        int : DataType.Integer,
        long : DataType.Integer,
        float : DataType.Float,
        bool : DataType.Boolean,
        #bytes : DataType.Bytes, # see below... 
    }
if str is not bytes: # Python >=3
    __PYTHON_TYPE_TO_TAURUS_DATATYPE[bytes] = DataType.Bytes
# Note: in Python2, DataType.from_python_type(bytes) --> DataType.String
DataType.from_python_type = __PYTHON_TYPE_TO_TAURUS_DATATYPE.get

SubscriptionState = Enumeration(
"SubscriptionState", (
    "Unsubscribed",
    "Subscribing",
    "Subscribed", 
    "PendingSubscribe"
))


AttrQuality = Enumeration(
'AttrQuality', (
    'ATTR_VALID', 
    'ATTR_INVALID', 
    'ATTR_ALARM',
    'ATTR_CHANGING',
    'ATTR_WARNING'
))

AttrAccess = Enumeration(
'AttrAccess', (
    'READ', 
    'READ_WITH_WRITE', 
    'WRITE', 
    'READ_WRITE' 
))

DisplayLevel = Enumeration(
'DisplayLevel', (
    'OPERATOR', 
    'EXPERT', 
    'DEVELOPER'
))

ManagerState =  Enumeration(
'ManagerState', (
    'UNINITIALIZED', 
    'INITED', 
    'CLEANED'
))

class DeprecatedEnum(object):
    def __init__(self, name, alt):
        self.__name = name
        self.__alt = alt

    def __getattr__(self, name):
        raise RuntimeError('%s enumeration was removed. Use %s instead' %
                           (self.__name, self.__alt))


DevState = DeprecatedEnum('taurus.core.DevState',
                          'taurus.core.tango.util.DevState')
TaurusSWDevState = DeprecatedEnum('TaurusSWDevState', 'TaurusDevState')
TaurusSWDevHealth = DeprecatedEnum('TaurusSWDevHealth', 'TaurusDevState')

class TaurusTimeVal(object):
    def __init__(self):
        self.tv_sec = 0
        self.tv_usec = 0
        self.tv_nsec = 0
    
    def __repr__(self):
        return "%s(tv_sec=%i, tv_usec=%i, tv_nsec=%i)"%(self.__class__.__name__, self.tv_sec, self.tv_usec, self.tv_nsec)
    
    def __float__(self):
        return self.totime()
    
    def totime(self):
        return self.tv_usec*1e-9 + self.tv_usec*1e-6 + self.tv_sec
    
    def todatetime(self):
        return datetime.datetime.fromtimestamp(self.totime())
    
    def isoformat(self):
        return self.todatetime().isoformat()
    
    @staticmethod
    def fromtimestamp(v):
        tv = TaurusTimeVal()
        tv.tv_sec = int(v)
        usec = (v - tv.tv_sec)*1000000
        tv.tv_usec = int(usec)
        tv.tv_nsec = int((usec - tv.tv_usec)*1000)
        return tv
    
    @staticmethod
    def fromdatetime(v):
        import time
        tv = TaurusTimeVal()
        tv.tv_sec = int(time.mktime(v.timetuple()))
        tv.tv_usec = v.microsecond
        tv.tv_nsec = 0 #datetime does not provide ns info
        return tv
    
    @staticmethod
    def now():
        return TaurusTimeVal.fromdatetime(datetime.datetime.now())    
         

class TaurusAttrValue(object):
    def __init__(self):
        self.rvalue = None
        self.wvalue = None
        self.time = None
        self.quality = AttrQuality.ATTR_VALID
        self.error = None
    
    def __repr__(self):
        return "%s%s"%(self.__class__.__name__, repr(self.__dict__))


class TaurusConfigValue(object):
    @tep14_deprecation(alt='TaurusAttrValue')
    def __init__(self):
        pass

class TaurusLockInfo(object):
    
    LOCK_STATUS_UNKNOWN = 'Lock status unknown'
    
    def __init__(self):
        self.status = LockStatus.Unknown
        self.status_msg = self.LOCK_STATUS_UNKNOWN
        self.id = None
        self.host = None
        self.klass = None

    def __repr__(self):
        return self.status_msg

    
#del time
#del datetime
#del Enumeration
#del AttrQuality, AttrAccess, DataFormat, LockStatus
