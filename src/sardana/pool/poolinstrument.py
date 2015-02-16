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
for instrument"""

__all__ = ["PoolInstrument"]

__docformat__ = 'restructuredtext'

import weakref

from sardana import ElementType

from sardana.pool.poolobject import PoolObject


class PoolInstrument(PoolObject):

    def __init__(self, **kwargs):
        self._parent_instrument = kwargs.pop("parent")
        self._instrument_class = kwargs.pop("klass")
        if self._parent_instrument:
            self._parent_instrument = weakref.ref(self._parent_instrument)
        self._child_instruments = {}
        self._elements = {}
        kwargs['elem_type'] = ElementType.Instrument
        super(PoolInstrument, self).__init__(**kwargs)

    def get_parent(self):
        return self.get_parent_instrument()

    def serialize(self, *args, **kwargs):
        kwargs = PoolObject.serialize(self, *args, **kwargs)
        kwargs['klass'] = self.instrument_class
        if self.parent_instrument is not None:
            kwargs['parent_instrument'] = self.parent_instrument.full_name
        else:
            kwargs['parent_instrument'] = None
        return kwargs

    def get_instrument_class(self):
        return self._instrument_class

    def add_instrument(self, instrument):
        self._child_instruments[instrument.id] = instrument

    def remove_instrument(self, instrument):
        del self._child_instruments[instrument.id]

    def get_instruments(self):
        return self._child_instruments.values()

    def set_parent_instrument(self, instrument):
        if instrument:
            self._parent_instrument = weakref.ref(instrument)
        else:
            self._parent_instrument = None

    def get_parent_instrument(self):
        if self.has_parent_instrument():
            return self._parent_instrument()

    def has_parent_instrument(self):
        return self._parent_instrument is not None

    def add_element(self, element):
        self._elements[element.id] = weakref.ref(element)

    def remove_element(self, element):
        del self._elements[element.id]

    def get_elements(self):
        return [ e() for e in self._elements.values() ]

    def has_instruments(self):
        return len(self._child_instruments) > 0

    def has_elements(self):
        return len(self._elements) > 0

    instruments = property(get_instruments)
    elements = property(get_elements)
    instrument_class = property(get_instrument_class)
    parent_instrument = property(get_parent_instrument)
