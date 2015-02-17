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

"""This module is part of the Python Pool library. It defines the base classes
for experiment channels"""

__all__ = ["Value", "PoolBaseChannel"]

__docformat__ = 'restructuredtext'

from sardana.sardanaattribute import SardanaAttribute

from sardana.pool.poolelement import PoolElement
from sardana.pool.poolacquisition import PoolCTAcquisition


class Value(SardanaAttribute):

    def __init__(self, *args, **kwargs):
        super(Value, self).__init__(*args, **kwargs)

    def update(self, cache=True, propagate=1):
        if not cache or not self.has_value():
            value = self.obj.read_value()
            self.set_value(value, propagate=propagate)


class PoolBaseChannel(PoolElement):

    ValueAttributeClass = Value
    AcquisitionClass = PoolCTAcquisition

    def __init__(self, **kwargs):
        PoolElement.__init__(self, **kwargs)
        self._value = self.ValueAttributeClass(self, listeners=self.on_change)
        if not self.AcquisitionClass is None:
            acq_name = "%s.Acquisition" % self._name
            self.set_action_cache(self.AcquisitionClass(self, name=acq_name))

    def get_value_attribute(self):
        """Returns the value attribute object for this experiment channel
        
        :return: the value attribute
        :rtype: :class:`~sardana.sardanaattribute.SardanaAttribute`"""
        return self._value

    # --------------------------------------------------------------------------
    # Event forwarding
    # --------------------------------------------------------------------------

    def on_change(self, evt_src, evt_type, evt_value):
        # forward all events coming from attributes to the listeners
        self.fire_event(evt_type, evt_value)

    # --------------------------------------------------------------------------
    # default acquisition channel
    # --------------------------------------------------------------------------

    def get_default_attribute(self):
        return self.get_value_attribute()

    # --------------------------------------------------------------------------
    # acquisition
    # --------------------------------------------------------------------------

    def get_acquisition(self):
        return self.get_action_cache()

    acquisition = property(get_acquisition, doc="acquisition object")

    # --------------------------------------------------------------------------
    # value
    # --------------------------------------------------------------------------

    def read_value(self):
        """Reads the channel value from hardware.

        :return:
            a :class:`~sardana.sardanavalue.SardanaValue` containing the channel
            value
        :rtype:
            :class:`~sardana.sardanavalue.SardanaValue`"""
        return self.acquisition.read_value()[self]

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
        """Returns the channel value.

        :param cache:
            if ``True`` (default) return value in cache, otherwise read value
            from hardware
        :type cache:
            bool
        :param propagate:
            0 for not propagating, 1 to propagate, 2 propagate with priority
        :type propagate:
            int
        :return:
            the channel value
        :rtype:
            :class:`~sardana.sardanaattribute.SardanaAttribute`"""
        return self._get_value(cache=cache, propagate=propagate)

    def _get_value(self, cache=True, propagate=1):
        value = self.get_value_attribute()
        value.update(cache=cache, propagate=propagate)
        return value

    def set_value(self, value):
        """Starts an acquisition on this channel

        :param value:
            the value to count
        :type value:
            :class:`~numbers.Number`"""
        return self._set_value(value)

    def _set_value(self, value):
        self.start_acquisition(value)

    value = property(get_value, set_value, doc="channel value")

    def start_acquisition(self, value=None):
        self._aborted = False
        self._stopped = False
        if value is None:
            value = self.get_write_value()
        if value is None:
            raise Exception("Invalid integration_time '%s'. Hint set a new value for 'value' first" % value)
        if not self._simulation_mode:
            acq = self.acquisition.run(integ_time=value)
