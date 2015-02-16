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
for TwoDExpChannel"""

__all__ = ["Pool2DExpChannel"]

__docformat__ = 'restructuredtext'

from sardana import ElementType
from sardana.sardanaevent import EventType

from sardana.pool.poolbasechannel import PoolBaseChannel


class Pool2DExpChannel(PoolBaseChannel):

    def __init__(self, **kwargs):
        self._data_source = None
        kwargs['elem_type'] = ElementType.TwoDExpChannel
        PoolBaseChannel.__init__(self, **kwargs)

    # --------------------------------------------------------------------------
    # data source
    # --------------------------------------------------------------------------

    def get_data_source(self, cache=True, propagate=1):
        if not cache or self._data_source is None:
            data_source = self.read_data_source()
            self._set_data_source(data_source, propagate=propagate)
        return self._data_source

    def _set_data_source(self, data_source, propagate=1):
        self._data_source = data_source
        if not propagate:
            return
        self.fire_event(EventType("data_source", priority=propagate), data_source)

    def read_data_source(self):
        data_source = self.controller.get_axis_par(self.axis, "data_source")
        return data_source

    data_source = property(get_data_source, doc="source identifier for the 2D data")
