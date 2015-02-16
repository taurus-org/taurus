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

__all__ = ["PoolMotorGroup"]

__docformat__ = 'restructuredtext'

import time
import collections

from sardana import ElementType
from sardana.sardanaattribute import SardanaAttribute
from sardana.pool.poolgroupelement import PoolGroupElement
from sardana.pool.poolmotion import PoolMotion


class Position(SardanaAttribute):

    def __init__(self, *args, **kwargs):
        self._w_value_map = None
        super(Position, self).__init__(*args, **kwargs)
        for pos_attr in self.obj.get_physical_position_attribute_iterator():
            pos_attr.add_listener(self.on_change)

    def _has_value(self):
        for pos_attr in self.obj.get_physical_position_attribute_iterator():
            if not pos_attr.has_value():
                return False
        return True

    def _in_error(self):
        for pos_attr in self.obj.get_physical_position_attribute_iterator():
            if pos_attr.in_error():
                return True
        return False

    def get_elements(self):
        return self.obj.get_user_elements()

    def get_element_nb(self):
        return len(self.get_user_elements())

    def _get_exc_info(self):
        for position_attr in self.obj.get_physical_position_attribute_iterator():
            if position_attr.error:
                return position_attr.get_exc_info()

    def _get_timestamp(self):
        return max([ pos_attr.timestamp for pos_attr in self.obj.get_physical_position_attribute_iterator() ])

    def _set_value(self, value, exc_info=None, timestamp=None, propagate=1):
        raise Exception("Cannot set position value for motor group %s" % self.obj.name)

    def _get_value(self):
        return [ position.value for position in self.obj.get_physical_position_attribute_iterator() ]

    def _get_write_value(self):
        return [ position.w_value for position in self.obj.get_physical_position_attribute_iterator() ]

    def _set_write_value(self, w_value, timestamp=None, propagate=1):
        assert len(w_value) == self.get_element_nb()
        if isinstance(w_value, collections.Sequence):
            w_value_map = {}
            for v, elem in zip(w_value, self.get_elements()):
                w_value_map[elem] = v
        else:
            w_value_map = w_value
            w_value = []
            for elem in self.get_elements():
                w_value.append(w_value_map[elem])
        self._w_value_map = w_value
        super(Position, self).set_write_value(w_value, timestamp=timestamp,
                                              propagate=propagate)

    def on_change(self, evt_src, evt_type, evt_value):
        self.fire_read_event(propagate=evt_type.priority)

    def update(self, cache=True, propagate=1):
        if cache:
            for phy_elem_pos in self.obj.get_low_level_physical_position_attribute_iterator():
                if not phy_elem_pos.has_value():
                    cache = False
                    break
        if not cache:
            dial_position_values = self.obj.motion.read_dial_position(serial=True)
            for motion_obj, position_value in dial_position_values.items():
                motion_obj.put_dial_position(position_value, propagate=propagate)


class PoolMotorGroup(PoolGroupElement):

    def __init__(self, **kwargs):
        self._physical_elements = []
        self._in_start_move = False
        kwargs['elem_type'] = ElementType.MotorGroup
        PoolGroupElement.__init__(self, **kwargs)
        on_change = self.on_change
        self._position = Position(self, listeners=on_change)

    def _create_action_cache(self):
        motion_name = "%s.Motion" % self._name
        return PoolMotion(self, motion_name)

    # --------------------------------------------------------------------------
    # Event forwarding
    # --------------------------------------------------------------------------

    def on_change(self, evt_src, evt_type, evt_value):
        # forward all events coming from attributes to the listeners
        self.fire_event(evt_type, evt_value)

    def on_element_changed(self, evt_src, evt_type, evt_value):
        name = evt_type.name.lower()
        if name in ('state', 'position'):
            state, status = self._calculate_states()
            if name == 'state':
                propagate_state = evt_type.priority
            else:
                propagate_state = 0
            self.set_state(state, propagate=propagate_state)
            self.set_status(status, propagate=propagate_state)

    def add_user_element(self, element, index=None):
        elem_type = element.get_type()
        if elem_type == ElementType.Motor:
            pass
        elif elem_type == ElementType.PseudoMotor:
            #TODO: make this happen
            pass
        else:
            raise Exception("element %s is not a motor" % element.name)

        PoolGroupElement.add_user_element(self, element, index=index)

    # --------------------------------------------------------------------------
    # position
    # --------------------------------------------------------------------------

    def get_position_attribute(self):
        return self._position

    def get_low_level_physical_position_attribute_iterator(self):
        return self.get_physical_elements_attribute_iterator()

    def get_physical_position_attribute_iterator(self):
        return self.get_user_elements_attribute_iterator()

    def get_physical_positions_attribute_sequence(self):
        return self.get_user_elements_attribute_sequence()

    def get_physical_positions_attribute_map(self):
        return self.get_user_elements_attribute_map()

    def get_position(self, cache=True, propagate=1):
        """Returns the user position.

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
            the user position
        :rtype:
            :class:`~sardana.sardanaattribute.SardanaAttribute`"""
        position = self._position
        position.update(cache=cache, propagate=propagate)
        return position

    def set_position(self, positions):
        """Moves the motor group to the specified user positions

        :param positions:
            the user positions to move to
        :type positions:
            sequence< :class:`~numbers.Number` >"""
        self.start_move(positions)

    def set_write_position(self, w_position, timestamp=None, propagate=1):
        """Sets a new write value for the user position.

        :param w_position:
            the new write value for user position
        :type w_position:
            sequence< :class:`~numbers.Number` >
        :param propagate:
            0 for not propagating, 1 to propagate, 2 propagate with priority
        :type propagate: int"""
        self._position.set_write_value(w_position, timestamp=timestamp,
                                       propagate=propagate)

    position = property(get_position, set_position, doc="motor group positions")

    # --------------------------------------------------------------------------
    # default acquisition channel
    # --------------------------------------------------------------------------

    def get_default_attribute(self):
        return self.get_position_attribute()

    # --------------------------------------------------------------------------
    # motion
    # --------------------------------------------------------------------------

    def get_motion(self):
        return self.get_action_cache()

    motion = property(get_motion, doc="motion object")

    # --------------------------------------------------------------------------
    # motion calculation
    # --------------------------------------------------------------------------

    def calculate_motion(self, new_positions, items=None):
        user_elements = self.get_user_elements()
        if items is None:
            items = {}
        calculated = {}
        for new_position, element in zip(new_positions, user_elements):
            calculated[element] = new_position

        for new_position, element in zip(new_positions, user_elements):
            element.calculate_motion(new_position, items=items,
                                     calculated=calculated)
        return items

    def start_move(self, new_position):
        self._in_start_move = True
        try:
            return self._start_move(new_position)
        finally:
            self._in_start_move = False

    def _start_move(self, new_positions):
        self._aborted = False
        items = self.calculate_motion(new_positions)
        timestamp = time.time()
        for item, position_info in items.items():
            item.set_write_position(position_info[0], timestamp=timestamp,
                                    propagate=0)
        if not self._simulation_mode:
            self.motion.run(items=items)
