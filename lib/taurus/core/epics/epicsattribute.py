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
Epics module. See __init__.py for more detailed documentation
"""

from __future__ import print_function
from __future__ import absolute_import

import numpy
from taurus.core.units import Quantity
from taurus.core.taurusbasetypes import (TaurusEventType, TaurusAttrValue,
                                         TaurusTimeVal, AttrQuality, DataType,
                                         DataFormat)
from taurus.core.taurusattribute import TaurusAttribute
import epics
from epics.ca import ChannelAccessException
from epics import dbr


__all__ = ['EpicsAttribute']



# map for epics DBR types to Taurus Types.
Dbr2TaurusType = {dbr.STRING: DataType.String,
                  dbr.INT: DataType.Integer,
                  dbr.SHORT: DataType.Integer,
                  dbr.FLOAT: DataType.Float,
                  # dbr.ENUM: DataType.Integer,  # TODO: Support enum
                  dbr.CHAR: DataType.Bytes,
                  dbr.LONG: DataType.Integer,
                  dbr.DOUBLE: DataType.Float,
                  # TODO: if a time type is added to DataType, change the next
                  dbr.TIME_STRING: DataType.String,
                  dbr.TIME_INT: DataType.Integer,
                  dbr.TIME_SHORT: DataType.Integer,
                  dbr.TIME_FLOAT: DataType.Float,
                  # dbr.TIME_ENUM: DataType.Integer,  # TODO: Support enum
                  dbr.TIME_CHAR: DataType.Bytes,
                  dbr.TIME_LONG: DataType.Integer,
                  dbr.TIME_DOUBLE: DataType.Float,
                  dbr.CTRL_STRING: DataType.String,
                  dbr.CTRL_INT: DataType.Integer,
                  dbr.CTRL_SHORT: DataType.Integer,
                  dbr.CTRL_FLOAT: DataType.Float,
                  # dbr.CTRL_ENUM: DataType.Integer,  # TODO: Support enum
                  dbr.CTRL_CHAR: DataType.Bytes,
                  dbr.CTRL_LONG: DataType.Integer,
                  dbr.CTRL_DOUBLE: DataType.Float,
                  }


class EpicsAttribute(TaurusAttribute):
    """
    A :class:`TaurusAttribute` that gives access to an Epics Process Variable.

    .. seealso:: :mod:`taurus.core.epics`

    .. warning:: In most cases this class should not be instantiated directly.
                 Instead it should be done via the
                 :meth:`EpicsFactory.getAttribute`
    """
    # TODO: support non-numerical PVs

    def __init__(self, name='', parent=None, storeCallback=None):
        self.call__init__(TaurusAttribute, name, parent,
                          storeCallback=storeCallback)

        self._label = self.getSimpleName()
        self._value = None
        self.data_format = None
        self.type = None
        self._range = [None, None]
        self._alarm = [None, None]
        self._warning = [None, None]

        self.__pv = epics.PV(self.getNormalName(), callback=self.onEpicsEvent,
                             form='ctrl',
                             connection_callback=self.onEpicsConnectionEvent)
        self.__pv.wait_for_connection()

    def getPV(self):
        """Returns the underlying :obj:`epics.PV` object
        """
        return self.__pv

    def onEpicsEvent(self, **kwargs):
        """callback for PV changes"""
        # this is called from the ca thread.
        # TODO: Consider doing the following on a different thread
        self._value = self.decode(self.__pv)
        self.fireEvent(TaurusEventType.Change, self._value)

    def onEpicsConnectionEvent(self, **kwargs):
        """callback for PV connection changes"""
        if kwargs['conn']:
            self.debug('(re)connected to epics PV')
            if self._value is not None:
                self._value.error = None
        else:
            self.warning('Connection to epics PV lost')
            self._value.error = ChannelAccessException('PV "%s" not connected' %
                                                       kwargs['pvname'])
        self.fireEvent(TaurusEventType.Change, self._value)

    # ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # Necessary to overwrite from TaurusAttribute
    # ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    def encode(self, value):
        """encodes the value passed to the write method into
        a representation that can be written with :meth:`epics.PV.put`
        """
        if isinstance(value, Quantity):
            # convert to units of the PV
            value = value.to(self.__pv.units).magnitude
        return value

    def decode(self, pv):
        """Decodes an epics PV object into a TaurusValue, and also updates other
         properties of the Attribute object
        """
        attr_value = TaurusAttrValue()
        if not pv.connected:
            attr_value.error = ChannelAccessException('PV "%s" not connected' %
                                                      pv.pvname)
            return attr_value
        v = pv.value
        # type
        try:
            self.type = Dbr2TaurusType[pv.ftype]
        except KeyError:
            raise ValueError('Unsupported epics type "%s"' % pv.type)
        # writable
        self.writable = pv.write_access
        # data_format
        if numpy.isscalar(v):
            self.data_format = DataFormat._0D
        else:
            self.data_format = DataFormat(len(numpy.shape(v)))
        # units and limits support
        if self.type in (DataType.Integer, DataType.Float):
            v = Quantity(v, pv.units)
            self._range = self.__decode_limit(pv.lower_ctrl_limit,
                                              pv.upper_ctrl_limit)
            self._alarm = self.__decode_limit(pv.lower_alarm_limit,
                                              pv.upper_alarm_limit)
            self._warning = self.__decode_limit(pv.lower_warning_limit,
                                                pv.upper_warning_limit)

        # rvalue
        attr_value.rvalue = v
        # wvalue
        if pv.write_access:
            attr_value.wvalue = v
        # time
        if pv.timestamp is None:
            attr_value.time = TaurusTimeVal.now()
        else:
            attr_value.time = TaurusTimeVal.fromtimestamp(pv.timestamp)
        # quality
        if pv.severity > 0:
            attr_value.quality = AttrQuality.ATTR_ALARM
        else:
            attr_value.quality = AttrQuality.ATTR_VALID
        return attr_value

    def __decode_limit(self, l, h):
        units = self.__pv.units
        if l is None or numpy.isnan(l):
            l = None
        else:
            l = Quantity(l, units)
        if l is None or numpy.isnan(h):
            h = None
        else:
            h = Quantity(h, units)
        return [l, h]

    def write(self, value, with_read=True):
        value = self.encode(value)
        self.__pv.put(value, wait=True)
        if with_read:
            return self.read(cache=False)

    def read(self, cache=True):
        """returns the value of the attribute.

        :param cache: (bool) If True (default), the last calculated value will
                      be returned. If False, the referenced values will be re-
                      read and the transformation string will be re-evaluated

        :return: attribute value
        """
        if not cache:
            self.__pv.get(use_monitor=False)
            self._value = self.decode(self.__pv)
        return self._value

    def poll(self):
        v = self.read(cache=False)
        self.fireEvent(TaurusEventType.Periodic, v)

    def isUsingEvents(self):
        return True  # TODO: implement this
# ------------------------------------------------------------------------------

    def factory(self):
        from .epicsfactory import EpicsFactory
        return EpicsFactory()

    @classmethod
    def getNameValidator(cls):
        from .epicsvalidator import EpicsAttributeNameValidator
        return EpicsAttributeNameValidator()


if __name__ == '__main__':
    a = EpicsAttribute('ca:XXX:a', None)
    b = EpicsAttribute('ca:XXX:b', None)
    s = EpicsAttribute('ca:XXX:sum', None)

    a.write(3.)
    b.write(4.)
    s.read()

    print("!$!", s.read(cache=False))
    print("a,b,s", a.read().rvalue, b.read().rvalue, s.read().rvalue)
    print("DF=", a.getDataFormat(), DataFormat.whatis(a.getDataFormat()))
