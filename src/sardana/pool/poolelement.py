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
for"""

__all__ = ["PoolElement", "PoolElementFrontend"]

__docformat__ = 'restructuredtext'

import weakref

from sardana.sardanaevent import EventType
from sardana.pool.poolbaseelement import PoolBaseElement


class PoolElement(PoolBaseElement):
    """A Pool element is an Pool object which is controlled by a controller.
       Therefore it contains a _ctrl_id and a _axis (the id of the element in
       the controller)."""

    def __init__(self, **kwargs):
        ctrl = kwargs.pop('ctrl')
        self._ctrl = weakref.ref(ctrl)
        self._axis = kwargs.pop('axis')
        self._ctrl_id = ctrl.get_id()
        try:
            instrument = kwargs.pop('instrument')
            self.set_instrument(instrument)
        except KeyError:
            self._instrument = None
        super(PoolElement, self).__init__(**kwargs)

    def serialize(self, *args, **kwargs):
        kwargs = PoolBaseElement.serialize(self, *args, **kwargs)
        kwargs['controller'] = self.controller.full_name
        kwargs['unit'] = '0'  #TODO: hardcoded unit to 0
        kwargs['axis'] = self.axis
        if self.instrument is not None:
            kwargs['instrument'] = self.instrument.full_name
        else:
            kwargs['instrument'] = None
        kwargs['source'] = self.get_source()
        return kwargs

    def get_parent(self):
        return self.get_controller()

    def get_controller(self):
        if self._ctrl is None:
            return None
        return self._ctrl()

    def get_controller_id(self):
        return self._ctrl_id

    def get_axis(self):
        return self._axis

    def set_action_cache(self, action_cache):
        self._action_cache = action_cache
        action_cache.add_element(self)

    def get_source(self):
        return "{0}/{1}".format(self.full_name, self.get_default_acquisition_channel())

    # --------------------------------------------------------------------------
    # instrument
    # --------------------------------------------------------------------------

    def get_instrument(self):
        if self._instrument is None:
            return None
        return self._instrument()

    def set_instrument(self, instrument, propagate=1):
        self._set_instrument(instrument, propagate=propagate)

    def _set_instrument(self, instrument, propagate=1):
        if self._instrument is not None:
            self._instrument().remove_element(self)
        new_instrument_name = ""
        if instrument is None:
            self._instrument = None
        else:
            self._instrument = weakref.ref(instrument)
            new_instrument_name = instrument.full_name
            instrument.add_element(self)
        if not propagate:
            return
        self.fire_event(EventType("instrument", priority=propagate),
                        new_instrument_name)

    # --------------------------------------------------------------------------
    # stop
    # --------------------------------------------------------------------------

    def stop(self):
        self.info("Stop!")
        PoolBaseElement.stop(self)
        self.controller.stop_one(self.axis)

    # --------------------------------------------------------------------------
    # abort
    # --------------------------------------------------------------------------

    def abort(self):
        self.info("Abort!")
        PoolBaseElement.abort(self)
        self.controller.abort_one(self.axis)

    def get_par(self, name):
        return self.controller.get_axis_par(self.axis, name)

    def set_par(self, name, value):
        return self.controller.set_axis_par(self.axis, name, value)

    def get_extra_par(self, name):
        return self.controller.get_axis_attr(self.axis, name)

    def set_extra_par(self, name, value):
        return self.controller.set_axis_attr(self.axis, name, value)

    axis = property(get_axis, doc="element axis")
    controller = property(get_controller, doc="element controller")
    controller_id = property(get_controller_id, doc="element controller id")
    instrument = property(get_instrument, set_instrument,
                          doc="element instrument")
