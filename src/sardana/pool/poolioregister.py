#!/usr/bin/env python

##############################################################################
##
## This file is part of Sardana
##
## http://www.sardana-controls.org/
##
## Copyright 2011 CELLS / ALBA Synchrotron, Bellaterra, Spain
##
## Sardana is free software: you can redistribute it and/or modify
## it under the terms of the GNU Lesser General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## Sardana is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU Lesser General Public License for more details.
##
## You should have received a copy of the GNU Lesser General Public License
## along with Sardana.  If not, see <http://www.gnu.org/licenses/>.
##
##############################################################################

"""This module is part of the Python Pool libray. It defines the base classes
for """

__all__ = ["PoolIORegister"]

__docformat__ = 'restructuredtext'

import time

from sardana import ElementType
from sardana.sardanaattribute import SardanaAttribute
from sardana.pool.poolelement import PoolElement
from sardana.pool.poolacquisition import PoolIORAcquisition


class Value(SardanaAttribute):

    def __init__(self, *args, **kwargs):
        super(Value, self).__init__(*args, **kwargs)

    def update(self, cache=True, propagate=1):
        if not cache or not self.has_value():
            value = self.obj.read_value()
            self.set_value(value, propagate=propagate)


class PoolIORegister(PoolElement):

    def __init__(self, **kwargs):
        kwargs['elem_type'] = ElementType.IORegister
        PoolElement.__init__(self, **kwargs)
        self._value = Value(self, listeners=self.on_change)
        self._config = None
        acq_name = "%s.Acquisition" % self._name
        self.set_action_cache(PoolIORAcquisition(self.pool, name=acq_name))

    def get_value_attribute(self):
        """Returns the value attribute object for this IO register

        :return: the value attribute
        :rtype: :class:`~sardana.sardanaattribute.SardanaAttribute`"""
        return self._value

    # -------------------------------------------------------------------------
    # Event forwarding
    # -------------------------------------------------------------------------

    def on_change(self, evt_src, evt_type, evt_value):
        # forward all events coming from attributes to the listeners
        self.fire_event(evt_type, evt_value)

    # -------------------------------------------------------------------------
    # default acquisition channel
    # -------------------------------------------------------------------------

    def get_default_attribute(self):
        return self.get_value_attribute()

    # -------------------------------------------------------------------------
    # value
    # -------------------------------------------------------------------------
    def read_value(self):
        """Reads the IO register value from hardware.

        :return:
            a :class:`~sardana.sardanavalue.SardanaValue` containing the IO
            register value
        :rtype:
            :class:`~sardana.sardanavalue.SardanaValue`"""
        return self.get_action_cache().read_value()[self]

    def put_value(self, value, propagate=1):
        """Sets a value.

        :param value:
            the new value
        :type value:
            :class:`~sardana.sardanavalue.SardanaValue`
        :param propagate:
            0 for not propagating, 1 to propagate, 2 propagate with priority
        :type propagate:
            int"""
        val_attr = self._value
        val_attr.set_value(value, propagate=propagate)
        return val_attr

    def get_value(self, cache=True, propagate=1):
        value = self.get_value_attribute()
        value.update(cache=cache, propagate=propagate)
        return value

    def set_value(self, value, timestamp=None):
        self.write_register(value, timestamp=timestamp)

    def set_write_value(self, w_value, timestamp=None, propagate=1):
        """Sets a new write value for the IO registere

        :param w_value:
            the new write value for IO register
        :type w_value:
            :class:`~numbers.Number`
        :param propagate:
            0 for not propagating, 1 to propagate, 2 propagate with priority
        :type propagate:
            int"""
        self._value.set_write_value(w_value, timestamp=timestamp,
                                    propagate=propagate)

    value = property(get_value, set_value, doc="ioregister value")

    def write_register(self, value, timestamp=None):
        self._aborted = False
        self._stopped = False
        if not self._simulation_mode:
            if timestamp is None:
                timestamp = time.time()
            self.set_write_value(value, timestamp=timestamp, propagate=0)
            self.controller.write_one(self.axis, value)
