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
           "TaurusLockInfo", "DevState"]

__docformat__ = "restructuredtext"

import datetime

from .util.enumeration import Enumeration

TaurusSWDevState = Enumeration(
'TaurusSWDevState', (
    'Uninitialized',
    'Running', 
    'Shutdown', 
    'Crash', 
    'EventSystemShutdown'
))

TaurusSWDevHealth = Enumeration(
'TaurusSWDevHealth', (
    'Exported',           # device reported exported
    'ExportedAlive',      # device reported exported and confirmed connection
    'ExportedNotAlive',   # device reported exported but connection failed!!
    'NotExported',        # device didn't report exported
    'NotExportedAlive',   # device didn't report exported but connection confirmed!
    'NotExportedNotAlive' # device didn't report exported and connection failed
))

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

DevState =  Enumeration(
'DevState', (
    'ON',
    'OFF',
    'CLOSE',
    'OPEN',
    'INSERT',
    'EXTRACT',
    'MOVING',
    'STANDBY',
    'FAULT',
    'INIT',
    'RUNNING',
    'ALARM',
    'DISABLE',
    'UNKNOWN'
))

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
    def __init__(self, config=None):
        # TODO: config parameter is maintained for backwards compatibility
        self.rvalue = None
        self.wvalue = None
        self.time = None
        self.quality = AttrQuality.ATTR_VALID
        #self.format = 0
        self.error = None
        ########################################################################
        # From TaurusConfigValue attributes
        self.name = None
        self.writable = None
        self.data_format = None
        self.label = None
        self.type = None
        self.description = None
        self.range = float('-inf'), float('inf')
        self.alarm = float('-inf'), float('inf')
        self.warning = float('-inf'), float('inf')
        ########################################################################
        # TODO remove this ref
        self.config = self

    # --------------------------------------------------------
    # This is for backwards compat with the API of taurus < 4 
    #
    def _get_value(self):
        '''for backwards compat with taurus < 4'''
        from taurus.core.util.log import deprecated 
        deprecated(dep='value', alt='.rvalue', rel='taurus 4',
                   dbg_msg=repr(self))
        try:
            return self.__fix_int(self.rvalue.magnitude)
        except AttributeError: 
            return self.rvalue
        
    def _set_value(self, value):
        '''for backwards compat with taurus < 4'''
        from taurus.core.util.log import deprecated 
        deprecated(dep='value',  alt='.rvalue', rel='taurus 4',
                   dbg_msg='Setting %r to %s'%(value, self.name))
        
        if self.rvalue is None: #we do not have a previous rvalue
            import numpy
            dtype = numpy.array(value).dtype
            if numpy.issubdtype(dtype, int) or numpy.issubdtype(dtype, float):
                msg = 'Refusing to set ambiguous value (deprecated .value API)'
                raise ValueError(msg)
            else:
                self.rvalue = value                
        elif hasattr(self.rvalue, 'units'): # we do have it and is a Quantity
            from taurus.external.pint import Quantity
            self.rvalue = Quantity(value, units = self.rvalue.units)
        else: # we do have a previous value and is not a quantity
            self.rvalue = value

    value = property(_get_value, _set_value)
        
    def _get_w_value(self):
        '''for backwards compat with taurus < 4'''
        from taurus.core.util.log import deprecated 
        deprecated(dep='w_value', alt='.wvalue', rel='taurus 4',
                        dbg_msg=repr(self))
        try:
            return self.__fix_int(self.wvalue.magnitude)
        except AttributeError: 
            return self.wvalue
         
    def _set_w_value(self, value):
        '''for backwards compat with taurus < 4'''
        from taurus.core.util.log import deprecated
        deprecated(dep='w_value', alt='.wvalue', rel='taurus 4',
                        dbg_msg='Setting %r to %s'%(value, self.name))
        
        if self.wvalue is None: #we do not have a previous wvalue
            import numpy
            dtype = numpy.array(value).dtype
            if numpy.issubdtype(dtype, int) or numpy.issubdtype(dtype, float):
                msg = 'Refusing to set ambiguous value (deprecated .value API)'
                raise ValueError(msg)
            else:
                self.wvalue=value                
        elif hasattr(self.wvalue, 'units'): # we do have it and is a Quantity
            from taurus.external.pint import Quantity
            self.wvalue = Quantity(value, units = self.wvalue.units)
        else: # we do have a previous value and is not a quantity
            self.wvalue=value

    w_value = property(_get_w_value, _set_w_value)
            
    @property
    def has_failed(self):
        '''for backwards compat with taurus < 4'''
        from taurus.core.util.log import deprecated 
        deprecated(dep='has_failed', alt='.error', rel='taurus 4')
        return self.error
        
    def __fix_int(self, value):
        '''cast value to int if  it is an integer.
        Works on scalar and non-scalar values'''
        if self.type != DataType.Integer:
            return value
        try:
            return int(value)
        except TypeError:
            import numpy
            return numpy.array(value, dtype='int')
    
    def __repr__(self):
        return "%s%s"%(self.__class__.__name__, repr(self.__dict__))

    ############################################################################
    # Form TaurusConfigValue methods

    #===========================================================================
    # The following methods are here for taurus<4 bck-compat
    #
    
    def _get_unit(self):
        '''for backwards compat with taurus < 4'''
        from taurus.core.util.log import deprecated 
        deprecated(dep='unit', alt='TaurusAttrValue.rvalue.units', 
                        rel='taurus 4', dbg_msg='Cannot return unit')
        return ''
        
    def _set_unit(self, value):
        '''for backwards compat with taurus < 4'''
        extra_msg = 'ignoring setting of units of %s to %r' % (self.name,
                                                               value )
        from taurus.core.util.log import deprecated
        deprecated(dep='unit', alt='.rvalue.units', rel='taurus 4',
                   dbg_msg=extra_msg)

    unit = property(_get_unit, _set_unit)
    
    def isWrite(self, cache=True):
        from taurus.core.util.log import deprecated 
        deprecated(dep='isWrite', alt='self.writable', rel='taurus 4')
        return self.writable
     
    def isReadOnly(self, cache=True):
        from taurus.core.util.log import deprecated 
        deprecated(dep='isReadOnly', alt='self.writable', rel='taurus 4')
        return not self.writable
 
    def isReadWrite(self, cache=True):
        from taurus.core.util.log import deprecated 
        deprecated(dep='isReadWrite', alt='self.writable', rel='taurus 4')
        return self.writable

    def isScalar(self):
        from taurus.core.util.log import deprecated 
        deprecated(dep='isScalar', alt='self.format', rel='taurus 4')
        return self.format == DataFormat._0D
    
    def isSpectrum(self):
        from taurus.core.util.log import deprecated 
        deprecated(dep='isSpectrum', alt='self.format', rel='taurus 4')
        return self.format == DataFormat._1D
    
    def isImage(self):
        from taurus.core.util.log import deprecated 
        deprecated(dep='isImage', alt='self.format', rel='taurus 4')
        return self.format == DataFormat._2D
    #
    #===========================================================================

class TaurusConfigValue(object):
    def __init__(self):
        from taurus.core.util.log import deprecated
        deprecated(dep='TaurusConfigValue',  alt='TaurusAttrValue',
                   rel='taurus 4', dbg_msg='Do not use this class')

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
