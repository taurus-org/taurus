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

__all__ = ["PoolGroupElement"]

__docformat__ = 'restructuredtext'

from sardana.pool.poolbaseelement import PoolBaseElement
from sardana.pool.poolbasegroup import PoolBaseGroup


class PoolGroupElement(PoolBaseElement, PoolBaseGroup):

    def __init__(self, **kwargs):
        user_elements = kwargs.pop('user_elements')
        PoolBaseElement.__init__(self, **kwargs)
        PoolBaseGroup.__init__(self, user_elements=user_elements,
                               pool=kwargs['pool'])

    def serialize(self, *args, **kwargs):
        kwargs = PoolBaseElement.serialize(self, *args, **kwargs)
        elements = [elem.name for elem in self.get_user_elements()]
        physical_elements = []
        for elem_list in self.get_physical_elements().values():
            for elem in elem_list:
                physical_elements.append(elem.name)
        kwargs['elements'] = elements
        kwargs['physical_elements'] = physical_elements
        return kwargs

    def get_action_cache(self):
        return self._get_action_cache()

    def set_action_cache(self, action_cache):
        self._set_action_cache(action_cache)

    # -------------------------------------------------------------------------
    # state information
    # -------------------------------------------------------------------------

    def read_state_info(self):
        state_info = {}
        ctrl_state_info = self.get_action_cache().read_state_info(serial=True)
        for elem, ctrl_elem_state_info in ctrl_state_info.items():
            elem_state_info = elem._from_ctrl_state_info(ctrl_elem_state_info)
            elem.put_state_info(elem_state_info)
            state = elem.get_state(cache=True, propagate=0)
            status = elem.get_status(cache=True, propagate=0)
            state_info[elem] = state, status
        return state_info

    def _set_state_info(self, state_info, propagate=1):
        state_info = self._calculate_states(state_info)
        state, status = state_info
        self._set_status(status, propagate=propagate)
        self._set_state(state, propagate=propagate)

    # -------------------------------------------------------------------------
    # stop
    # -------------------------------------------------------------------------

    def stop(self):
        PoolBaseElement.stop(self)
        PoolBaseGroup.stop(self)

    # -------------------------------------------------------------------------
    # abort
    # -------------------------------------------------------------------------

    def abort(self):
        PoolBaseElement.abort(self)
        PoolBaseGroup.abort(self)

    # -------------------------------------------------------------------------
    # involved in an operation
    # -------------------------------------------------------------------------

    def get_operation(self):
        return PoolBaseGroup.get_operation(self)
