#!/usr/bin/env python
#############################################################################
##
# This file is part of Taurus
##
# http://taurus-scada.org
##
# Copyright 2011 CELLS / ALBA Synchrotron, Bellaterra, Spain
##
# Taurus is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
##
# Taurus is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
##
# You should have received a copy of the GNU Lesser General Public License
# along with Taurus.  If not, see <http://www.gnu.org/licenses/>.
##
#############################################################################

"""
a misc collection of basic types
"""

import datetime

from .util.enumeration import Enumeration
from .util.log import taurus4_deprecation
from enum import IntEnum
from future.utils import PY2
from builtins import object


__all__ = ["TaurusSWDevState", "TaurusSWDevHealth", "OperationMode",
           "TaurusSerializationMode", "SubscriptionState", "TaurusEventType",
           "MatchLevel", "TaurusElementType", "LockStatus", "DataFormat",
           "AttrQuality", "AttrAccess", "DisplayLevel", "ManagerState",
           "TaurusTimeVal", "TaurusAttrValue", "TaurusConfigValue", "DataType",
           "TaurusLockInfo", "TaurusDevState", "TaurusModelValue"]

__docformat__ = "restructuredtext"


class TaurusDevState(IntEnum):
    """Enumeration of possible states of :class:`taurus.core.TaurusDevice`
    objects. This is returned, e.g. by :meth:`TaurusDevice.state`.

    The description of the values of this enumeration is:

    - Ready: the device can be operated by the user and could even be
      involved in some operation.
    - NotReady: the device can not be operated by the user (e.g. due to
      still being initialized, or due to a device failure,...)
    - Undefined: it is not possible to retrieve a coherent state from the
      device (e.g. due to communication, or to contradictory internal
      states, ...)
    """
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
        'Concurrent',
        'TangoSerial',
    ))

TaurusEventType = Enumeration(
    'TaurusEventType', (
        'Change',
        'Config',  # Deprecated in Taurus >=4
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
        'Integer',  # Can be used in scheme-agnostic code
        'Float',  # Can be used in scheme-agnostic code
        'String',  # Can be used in scheme-agnostic code
        'Boolean',  # Can be used in scheme-agnostic code
        'Bytes',
        'DevState',  # This type is for Tango backwards-compat. Avoid using it
        'DevEncoded',  # This type is for Tango backwards-compat. Avoid using it
        'Object'  # use this for opaque py objects not described by any of the above
    ))
# monkey-patch DataType to provide from_python_type()
__PYTHON_TYPE_TO_TAURUS_DATATYPE = {
    str: DataType.String,
    int: DataType.Integer,
    # long : DataType.Integer,  # (only in py2) see below...
    float: DataType.Float,
    bool: DataType.Boolean,
    # bytes : DataType.Bytes,  # (only in py>=3) see below...
}
if PY2:  # Python 2
    __PYTHON_TYPE_TO_TAURUS_DATATYPE[long] = DataType.Integer
else:  # Python >=3
    __PYTHON_TYPE_TO_TAURUS_DATATYPE[bytes] = DataType.Bytes
DataType.from_python_type = __PYTHON_TYPE_TO_TAURUS_DATATYPE.get

SubscriptionState = Enumeration(
    "SubscriptionState", (
        "Unsubscribed",
        "Subscribing",
        "Subscribed",
        "PendingSubscribe"
    ))


class AttrQuality(IntEnum):
    """Enumeration of quality states for Taurus attributes. based on
    This is the Taurus equivalent to PyTango.AttrQuality.
    The members present in PyTango are also defined here with the same values,
    allowing equality comparisons with :class:`PyTango.AttrQuality` (but not
    identity checks!)::

        from taurus.core import AttrQuality as Q1
        from PyTango import AttrQuality as Q2

        Q1.ATTR_ALARM == Q2.ATTR_ALARM                  # --> True
        Q1.ATTR_ALARM in (Q2.ATTR_ALARM, Q2.ATTR_ALARM) # --> True
        Q1.ATTR_ALARM == 2                              # --> True
        Q1.ATTR_ALARM is 2                              # --> False
        Q1.ATTR_ALARM is Q2.ATTR_ALARM                  # --> False
    """
    ATTR_VALID = 0
    ATTR_INVALID = 1
    ATTR_ALARM = 2
    ATTR_CHANGING = 3
    ATTR_WARNING = 4

    def __str__(self):
        # Todo: BEWARE!! This alters the usual behaviour of IntEnum!
        return self.name

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

ManagerState = Enumeration(
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


TaurusSWDevState = DeprecatedEnum('TaurusSWDevState', 'TaurusDevState')
TaurusSWDevHealth = DeprecatedEnum('TaurusSWDevHealth', 'TaurusDevState')


class TaurusTimeVal(object):

    def __init__(self):
        self.tv_sec = 0
        self.tv_usec = 0
        self.tv_nsec = 0

    def __repr__(self):
        return "%s(tv_sec=%i, tv_usec=%i, tv_nsec=%i)" % (self.__class__.__name__, self.tv_sec, self.tv_usec, self.tv_nsec)

    def __float__(self):
        return self.totime()

    def totime(self):
        return self.tv_nsec * 1e-9 + self.tv_usec * 1e-6 + self.tv_sec

    def todatetime(self):
        return datetime.datetime.fromtimestamp(self.totime())

    def isoformat(self):
        return self.todatetime().isoformat()

    @staticmethod
    def fromtimestamp(v):
        tv = TaurusTimeVal()
        tv.tv_sec = int(v)
        usec = (v - tv.tv_sec) * 1000000
        tv.tv_usec = int(usec)
        tv.tv_nsec = int((usec - tv.tv_usec) * 1000)
        return tv

    @staticmethod
    def fromdatetime(v):
        import time
        tv = TaurusTimeVal()
        tv.tv_sec = int(time.mktime(v.timetuple()))
        tv.tv_usec = v.microsecond
        tv.tv_nsec = 0  # datetime does not provide ns info
        return tv

    @staticmethod
    def now():
        return TaurusTimeVal.fromdatetime(datetime.datetime.now())


class TaurusModelValue(object):

    def __init__(self):
        self.rvalue = None

    def __repr__(self):
        return "%s%s" % (self.__class__.__name__, repr(self.__dict__))


class TaurusAttrValue(TaurusModelValue):

    def __init__(self):
        TaurusModelValue.__init__(self)
        self.wvalue = None
        self.time = None
        self.quality = AttrQuality.ATTR_VALID
        self.error = None


class TaurusConfigValue(object):

    @taurus4_deprecation(alt='TaurusAttrValue')
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
