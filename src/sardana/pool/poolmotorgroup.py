#!/usr/bin/env python

##############################################################################
##
## This file is part of Sardana
##
## http://www.tango-controls.org/static/sardana/latest/doc/html/index.html
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
for"""

__all__ = [ "PoolMotorGroup" ]

__docformat__ = 'restructuredtext'

import time
import collections

from sardana import ElementType
from sardana.sardanaattribute import SardanaAttribute
from sardana.sardanaevent import EventType

from poolelement import PoolElement
from poolgroupelement import PoolGroupElement
from poolmotion import PoolMotion


class Position(SardanaAttribute, dict):
    
    def __init__(self, obj, name=None, initial_value=None):
        self._w_value_map = None
        SardanaAttribute.__init__(self, obj, name=name, initial_value=initial_value)
        dict.__init__(self)
    
    def has_value(self):
        """Determines if the attribute's read value has been read at least once
        in the lifetime of the attribute.
        
        :return: True if the attribute has a read value stored or False otherwise
        :rtype: bool"""        
        for i in self.values():
            if not i.has_value():
                return False
        return True
    
    def in_error(self):
        """Determines if this attribute is in error state.
        
        :return: True if the attribute is in error state or False otherwise
        :rtype: bool"""        
        for i in self.values():
            if not i.in_error():
                return True
        return False
    
    def get_elements(self):
        return self.obj.get_user_elements()
    
    def get_element_nb(self):
        return len(self.get_user_elements())
    
    def set_value(self, value, exc_info=None, timestamp=None, propagate=1):
        raise RuntimeError("Cannot set the value of a multiple %s attribute" % self.name) 
    
    def get_value(self):
        """Returns the last read value for this attribute.
        
        :return: the last read value for this attribute
        :rtype: obj
        
        :raises: :exc:`Exception` if no read value has been set yet"""        
        return [ self[elem].value for elem in self.get_elements() ]
    
    def get_exc_info(self):
        """Returns the exception information (like :func:`sys.exc_info`) about
        last attribute readout or None if last read did not generate an
        exception.
        
        :return: exception information or None
        :rtype: tuple<3> or None"""        
        ret = {}
        for elem in self.get_elements():
            if elem.in_error():
                ret[elem] = elem.get_exc_info()
        return ret

    def set_write_value(self, w_value, timestamp=None, propagate=1):
        """Sets the current write value.
        
        :param w_value: the write read value for this attribute
        :type w_value: obj
        :param timestamp: timestamp of attribute write [default: None, meaning
                          create a 'now' timestamp]
        :type timestamp: float or None
        :param propagate:
            0 for not propagating, 1 to propagate, 2 propagate with priority
        :type propagate: int"""
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
    
    def get_write_value_map(self):
        """Returns the last write value for this attribute.
        
        :return: the last write value for this attribute or None if value has
                 not been written yet
        :rtype: obj"""
        return self._w_value_map        
    
    def update_write_value(self, elem_or_index, w_value, timestamp=None, propagate=1):
        """Sets the current write value.
        
        :param elem_or_index: element or index of write value to be updated
        :type elem_or_index: PoolElement or int
        :param w_value: the write read value for this attribute
        :type w_value: obj
        :param timestamp: timestamp of attribute write [default: None, meaning
                          create a 'now' timestamp]
        :type timestamp: float or None
        :param propagate:
            0 for not propagating, 1 to propagate, 2 propagate with priority
        :type propagate: int"""
        elems = self.get_elements()  
        if timestamp is None:
            timestamp = time.time()
        if isinstance(elem_or_index, PoolElement):
            elem = elem_or_index
            index = elems.index(elem_or_index)
        else:
            index = elem_or_index
            elem = elems[index]
            
        if self._w_value is None:
            self._w_value = len(elems)*[None,]
        if self._w_value_map is None:
            self._w_value_map = {}
            for e in elems:
                self._w_value_map[e] = None
        self._w_value[index] = w_value
        self._w_value_map[elem] = w_value
        self._w_timestamp = timestamp
        self.fire_write_event(propagate=propagate)   

    
class PoolMotorGroup(PoolGroupElement):

    def __init__(self, **kwargs):
        self._position = Position(self)
        self._physical_elements = []
        self._in_start_move = False
        PoolGroupElement.__init__(self, **kwargs)

    def _create_action_cache(self):
        motion_name = "%s.Motion" % self._name
        return PoolMotion(self, motion_name)

    def get_type(self):
        return ElementType.MotorGroup

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
            if name == 'position':
                self.put_element_position(evt_src, evt_value,
                                          propagate=evt_type.priority)
        elif name == "w_position":
            # if motion originated from this motor group don't need to
            # calculate write position.
            if self._in_start_move:
                return
            self._position.update_write_value(evt_src, evt_value.w_value,
                                              evt_value.w_timestamp,
                                              propagate=evt_type.priority)
                
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

    def get_position(self, cache=True, propagate=1):
        positions = self._position
        if not cache:
            dial_position_infos = self.motion.read_dial_position(serial=True)
            for motion_obj, position_info in dial_position_infos.items():
                motion_obj.put_dial_position(position_info, propagate=propagate)
            for motion_obj in self.get_user_elements():
                positions[motion_obj] = motion_obj.get_position(propagate=0)
            self._set_position(positions, propagate=propagate)
        return positions

    def set_position(self, positions):
        self.set_write_position(positions, propagate=1)
        self.start_move(positions)

    def set_write_position(self, w_position, timestamp=None, propagate=1):
        """Sets a new write value for the user position.

        :param w_position:
            the new write value for user position
        :type w_position:
            :class:`~numbers.Number`
        :param propagate:
            0 for not propagating, 1 to propagate, 2 propagate with priority
        :type propagate: int"""
        self._position.set_write_value(w_position, timestamp=timestamp,
                                       propagate=propagate)
                                                                              
    def put_position(self, positions, propagate=1):
        self._set_position(positions, propagate=propagate)

    def _set_position(self, positions, propagate=1):
        self._position = positions
        if not propagate:
            return
        self.fire_event(EventType("position", priority=propagate), positions)

    def put_element_position(self, element, position, propagate=1):
        self._position[element] = position
        if not propagate or len(self._position) < len(self.get_user_elements()):
            return
        self.fire_event(EventType("position", priority=propagate), self._position)

    position = property(get_position, set_position, doc="motor group positions")

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
        ts = self._position.w_timestamp
        items = self.calculate_motion(new_positions)
        for item, position_info in items.items():
            item.set_write_position(position_info[0], timestamp=ts)
        self.fire_event(EventType("w_position", ),
                                  self._position)
        if not self._simulation_mode:
            self.motion.run(items=items)
