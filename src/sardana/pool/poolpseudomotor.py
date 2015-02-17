#!/usr/bin/env python
from sardana.sardanavalue import SardanaValue

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

"""This module is part of the Python Pool library. It defines the
PoolPseudoMotor class"""

__all__ = ["PoolPseudoMotor", "PoolPseudoMotorFrontend"]

__docformat__ = 'restructuredtext'

import sys
import time
import collections

from sardana import State, ElementType, TYPE_PHYSICAL_ELEMENTS
from sardana.sardanaattribute import SardanaAttribute
from sardana.sardanaexception import SardanaException

from sardana.pool.poolbaseelement import PoolBaseElement
from sardana.pool.poolelement import PoolElement
from sardana.pool.poolbasegroup import PoolBaseGroup
from sardana.pool.poolmotion import PoolMotion
from sardana.pool.poolexception import PoolException


class Position(SardanaAttribute):

    def __init__(self, *args, **kwargs):
        self._exc_info = None
        super(Position, self).__init__(*args, **kwargs)

        # 130226: We found a bug https://sourceforge.net/p/sardana/tickets/2/ that makes the Pool segfault with some pseudomotor configuration:
        # It can be reproduced by:
        # 4 physical motors: m1 m2 m3 m4
        # 2 slits: s1g,s1o = f(m1,m2) and s2g,s2o = f(m3,m4)
        # The pool will not be able to start if we create a third slit with s3g,s3o = f(s1g, s2g)
        # self.obj.get_physical_position_attribute_iterator() raises a KeyError exception
        # so we will flag the Position object as no_listeners for later configuration
        # We should still investigate the root of the problem when ordering the creation of elements
        self._listeners_configured = False
        try:
            for position_attr in self.obj.get_physical_position_attribute_iterator():
                position_attr.add_listener(self.on_change)
            self._listeners_configured = True
        except KeyError:
            pass

    def _in_error(self):
        for position_attr in self.obj.get_physical_position_attribute_iterator():
            if position_attr.error:
                return True
        return self._exc_info != None

    def _has_value(self):
        for position_attr in self.obj.get_physical_position_attribute_iterator():
            if not position_attr.has_value():
                return False
        return True

    def _has_write_value(self):
        for position_attr in self.obj.get_physical_position_attribute_iterator():
            if not position_attr.has_write_value():
                return False
        return True

    def _get_value(self):
        return self.calc_pseudo().value

    def _set_value(self, value, exc_info=None, timestamp=None, propagate=1):
        raise Exception("Cannot set position value for %s" % self.obj.name)

    def _get_write_value(self):
        w_positions = self.get_physical_write_positions()
        return self.calc_pseudo(physical_positions=w_positions).value

    def _set_write_value(self, w_value, timestamp=None, propagate=1):
        raise Exception("Cannot set position write value for %s" % self.obj.name)

    def _get_exc_info(self):
        exc_info = self._exc_info
        if exc_info is None:
            for position_attr in self.obj.get_physical_position_attribute_iterator():
                if position_attr.error:
                    return position_attr.get_exc_info()
        return exc_info

    def _get_timestamp(self):
        timestamps = [ pos_attr.timestamp for pos_attr in self.obj.get_physical_position_attribute_iterator() ]
        if not len(timestamps):
            timestamps = self._local_timestamp,
        return max(timestamps)

    def get_physical_write_positions(self):
        ret = []
        for pos_attr in self.obj.get_physical_position_attribute_iterator():
            if pos_attr.has_write_value():
                value = pos_attr.w_value
            else:
                if not pos_attr.has_value():
                    # if underlying moveable doesn't have position yet, it is
                    # because of a cold start
                    pos_attr.update(propagate=0)
                if pos_attr.in_error():
                    raise PoolException("Cannot get '%' position" % pos_attr.obj.name,
                                        exc_info=pos_attr.exc_info)
                value = pos_attr.value
            ret.append(value)
        return ret

    def get_physical_positions(self):
        ret = []
        for pos_attr in self.obj.get_physical_position_attribute_iterator():
            # if underlying moveable doesn't have position yet, it is because
            # of a cold start
            if not pos_attr.has_value():
                pos_attr.update(propagate=0)
            if pos_attr.in_error():
                raise PoolException("Cannot get '%' position" % pos_attr.obj.name,
                                    exc_info=pos_attr.exc_info)
            ret.append(pos_attr.value)
        return ret

    def calc_pseudo(self, physical_positions=None):
        try:
            obj = self.obj
            if physical_positions is None:
                physical_positions = self.get_physical_positions()
            else:
                l_p, l_u = len(physical_positions), len(obj.get_user_elements())
                if l_p != l_u:
                    raise IndexError("CalcPseudo(%s): must give %d physical " \
                                     "positions (you gave %d)" % (obj.name, l_u, l_p))
            result = obj.controller.calc_pseudo(obj.axis, physical_positions, None)
        except SardanaException as se:
            result = SardanaValue(exc_info=se.exc_info)
        except:
            result = SardanaValue(exc_info=sys.exc_info())
        return result

    def calc_all_pseudo(self, physical_positions=None):
        try:
            obj = self.obj
            if physical_positions is None:
                physical_positions = self.get_physical_positions()
            else:
                l_p, l_u = len(physical_positions), len(obj.get_user_elements())
                if l_p != l_u:
                    raise IndexError("CalcAllPseudo():: must give %d physical " \
                                     "positions (you gave %d)" % (l_u, l_p))
            result = obj.controller.calc_all_pseudo(physical_positions, None)
        except SardanaException as se:
            result = SardanaValue(exc_info=se.exc_info)
        except:
            result = SardanaValue(exc_info=sys.exc_info())
        return result

    def calc_physical(self, new_position):
        try:
            obj = self.obj
            curr_physical_positions = self.get_physical_positions()
            if isinstance(new_position, collections.Sequence):
                new_positions = new_position
            else:
                positions = obj.get_siblings_positions()
                positions[obj] = new_position
                new_positions = len(positions) * [None]
                for pseudo, position in positions.items():
                    new_positions[pseudo.axis - 1] = position

            result = obj.controller.calc_all_physical(new_positions,
                                                      curr_physical_positions)
        except SardanaException as se:
            result = SardanaValue(exc_info=se.exc_info)
        except:
            result = SardanaValue(exc_info=sys.exc_info())
        return result

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
            if not len(dial_position_values):
                self._local_timestamp = time.time()
            for motion_obj, position_value in dial_position_values.items():
                motion_obj.put_dial_position(position_value, propagate=propagate)


class PoolPseudoMotor(PoolBaseGroup, PoolElement):
    """A class representing a Pseudo Motor in the Sardana Device Pool"""

    def __init__(self, **kwargs):
        self._siblings = None
        self._in_start_move = False
        self._drift_correction = kwargs.pop('drift_correction', None)
        user_elements = kwargs.pop('user_elements')
        kwargs['elem_type'] = ElementType.PseudoMotor
        PoolElement.__init__(self, **kwargs)
        PoolBaseGroup.__init__(self, user_elements=user_elements,
                               pool=kwargs['pool'])
        self._position = Position(self, listeners=self.on_change)

    # --------------------------------------------------------------------------
    # Event forwarding
    # --------------------------------------------------------------------------

    def on_change(self, evt_src, evt_type, evt_value):
        # forward all events coming from attributes to the listeners
        self.fire_event(evt_type, evt_value)

    def serialize(self, *args, **kwargs):
        kwargs = PoolElement.serialize(self, *args, **kwargs)
        elements = [ elem.name for elem in self.get_user_elements() ]
        physical_elements = []
        for elem_list in self.get_physical_elements().values():
            for elem in elem_list:
                physical_elements.append(elem.name)
        cl_name = self.__class__.__name__
        cl_name = cl_name[4:]
        kwargs['elements'] = elements
        kwargs['physical_elements'] = physical_elements
        return kwargs

    def _create_action_cache(self):
        motion_name = "%s.Motion" % self._name
        return PoolMotion(self, motion_name)

    def set_drift_correction(self, drift_correction):
        self._drift_correction = drift_correction

    def get_drift_correction(self):
        dc = self._drift_correction
        if dc is None:
            dc = self.manager.drift_correction
        return dc

    drift_correction = property(get_drift_correction,
                                set_drift_correction,
                                doc="drift correction")

    def get_action_cache(self):
        return self._get_action_cache()

    def set_action_cache(self, action_cache):
        self._set_action_cache(action_cache)

    def get_siblings(self):
        if self._siblings is None:
            self._siblings = siblings = set()
            for axis, sibling in self.controller.get_element_axis().items():
                if axis == self.axis:
                    continue
                siblings.add(sibling)
        return self._siblings

    siblings = property(fget=get_siblings,
                        doc="the siblings for this pseudo motor")

    def on_element_changed(self, evt_src, evt_type, evt_value):
        name = evt_type.name.lower()
        # always calculate state.
        status_info = self._calculate_states()
        state, status = self.calculate_state_info(status_info=status_info)
        state_propagate = 0
        status_propagate = 0
        if name == 'state':
            state_propagate = evt_type.priority
        elif name == 'status':
            status_propagate = evt_type.priority
        self.set_state(state, propagate=state_propagate)
        self.set_status(status, propagate=status_propagate)

    def add_user_element(self, element, index=None):
        elem_type = element.get_type()
        if elem_type == ElementType.Motor:
            pass
        elif elem_type == ElementType.PseudoMotor:
            #TODO: make this happen
            pass
        else:
            raise Exception("element %s is not a motor" % element.name)

        PoolBaseGroup.add_user_element(self, element, index=index)

    # ------------------------------------------------------------------------
    # position
    # ------------------------------------------------------------------------

    def calc_pseudo(self, physical_positions=None):
        return self.get_position_attribute().calc_pseudo(physical_positions=physical_positions)

    def calc_physical(self, new_position):
        return self.get_position_attribute().calc_physical(new_position)

    def calc_all_pseudo(self, physical_positions=None):
        return self.get_position_attribute().calc_all_pseudo(physical_positions=physical_positions)

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

    def get_physical_positions(self, cache=True, propagate=1):
        """Get positions for underlying elements.

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
            the physical positions
        :rtype:
            dict <PoolElement, :class:`~sardana.sardanaattribute.SardanaAttribute` >"""
        self._position.update(cache=cache, propagate=propagate)
        return self.get_physical_positions_attribute_map()

    def get_siblings_positions(self, use=None, write_pos=True):
        """Get the last positions for all siblings.
        If write_pos is True and a sibling has already been moved before,
        it's last write position is used. Otherwise its read position is used
        instead.
        
        :param use: the already calculated positions. If a sibling is in this
                    dictionary, the position stored here is used instead
        :type use: dict <PoolElement, :class:`~sardana.sardanavalue.SardanaValue` >
        :param write_pos: determines if should try to use the last set point
                          [default: True]
        :type write_pos: bool
        :return: a dictionary with siblings write positions
        :rtype:
            dict <PoolElement, position(float?) >"""
        positions = {}
        for sibling in self.siblings:
            pos_attr = sibling.get_position(propagate=0)
            if use and sibling in use:
                pos = use[sibling]
            elif pos_attr.has_write_value() and write_pos:
                pos = pos_attr.w_value
            else:
                if pos_attr.in_error():
                    raise PoolException("Cannot get '%s' position" % sibling.name,
                                        exc_info=pos_attr.exc_info)
                pos_value = pos_attr.calc_pseudo()
                if pos_value.error:
                    raise PoolException("Cannot get '%s' position" % sibling.name,
                                        exc_info=pos_value.exc_info)
                pos = pos_value.value
            positions[sibling] = pos
        return positions

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
        position_attr = self._position
        position_attr.update(cache=cache, propagate=propagate)
        return position_attr

    def set_position(self, position):
        """Moves the motor to the specified user position

        :param position:
            the user position to move to
        :type position:
            :class:`~numbers.Number`"""
        self.start_move(position)

    def set_write_position(self, w_position, timestamp=None, propagate=1):
        """Sets a new write value for the user position.

        :param w_position:
            the new write value for user position
        :type w_position:
            :class:`~numbers.Number`
        :param propagate:
            0 for not propagating, 1 to propagate, 2 propagate with priority
        :type propagate:
            int"""
        # SardanaAttribute position will raise an exception so we let it do it
        self._position.set_write_value(w_position, timestamp=timestamp,
                                       propagate=propagate)

    position = property(get_position, set_position, doc="pseudo motor position")

    # ------------------------------------------------------------------------
    # state information
    # ------------------------------------------------------------------------

    _STD_STATUS = "{name} is {state}\n{ctrl_status}"
    def calculate_state_info(self, status_info=None):

        # Refer to Position.__init__ method for an explanation on this 'hack'
        if not self._position._listeners_configured:
            for position_attr in self.get_physical_position_attribute_iterator():
                position_attr.add_listener(self._position.on_change)
            self._position._listeners_configured = True

        if status_info is None:
            status_info = self._state, self._status
        state, status = status_info
        if state == State.On:
            state_str = "Stopped"
        else:
            state_str = "in " + State[state]
        new_status = self._STD_STATUS.format(name=self.name, state=state_str,
                                             ctrl_status=status)
        return status_info[0], new_status

    def read_state_info(self, state_info=None):
        if state_info is None:
            state_info = {}
            action_cache = self.get_action_cache()
            ctrl_state_infos = action_cache.read_state_info(serial=True)
            for motion_obj, ctrl_state_info in ctrl_state_infos.items():
                state_info[motion_obj] = motion_state_info = \
                    motion_obj._from_ctrl_state_info(ctrl_state_info)
                motion_obj.put_state_info(motion_state_info)
        for user_element in self.get_user_elements():
            if user_element.get_type() not in TYPE_PHYSICAL_ELEMENTS:
                motion_state_info = user_element._calculate_states()
                user_element.put_state_info(motion_state_info)

        ret = self._calculate_states()
        return ret

    # --------------------------------------------------------------------------
    # default acquisition channel
    # --------------------------------------------------------------------------

    def get_default_attribute(self):
        return self.get_position_attribute()

    # ------------------------------------------------------------------------
    # motion
    # ------------------------------------------------------------------------

    def get_motion(self):
        return self.get_action_cache()

    motion = property(get_motion, doc="motion object")

    # ------------------------------------------------------------------------
    # motion calculation
    # ------------------------------------------------------------------------

    def calculate_motion(self, new_position, items=None, calculated=None):
        # if items already contains the positions for this pseudo motor
        # underlying motors it means the motion has already been calculated
        # by a sibling
        if items is not None and len(items):
            physical_elements = self.get_physical_elements_set()
            s_items = set(items)
            if s_items == physical_elements:
                if calculated is not None and self in calculated:
                    return

        user_elements = self.get_user_elements()
        positions = self.get_siblings_positions(use=calculated,
                                                write_pos=self.drift_correction)
        positions[self] = new_position
        pseudo_positions = len(positions) * [None]
        for pseudo, position in positions.items():
            pseudo_positions[pseudo.axis - 1] = position
        curr_physical_positions = self._position.get_physical_positions()
        physical_positions = self.controller.calc_all_physical(pseudo_positions,
                                                               curr_physical_positions)
        if physical_positions.error:
            raise PoolException("Cannot calculate motion: "
                                "calc_all_physical raises exception",
                                exc_info=physical_positions.exc_info)
        else:
            if physical_positions.value is None:
                raise PoolException("Cannot calculate motion: "
                                    "calc_all_physical returns None")

        if items is None:
            items = {}
        for new_position, element in zip(physical_positions.value, user_elements):
            if new_position is None:
                raise PoolException("Cannot calculate motion: %s reports "
                                     "position to be None" % element.name)
            element.calculate_motion(new_position, items=items,
                                     calculated=calculated)
        return items

    def start_move(self, new_position):
        self._in_start_move = True
        try:
            return self._start_move(new_position)
        finally:
            self._in_start_move = False

    def _start_move(self, new_position):
        self._aborted = False
        self._stopped = False
        items = self.calculate_motion(new_position)
        timestamp = time.time()
        for item, position_info in items.items():
            item.set_write_position(position_info[0], timestamp=timestamp,
                                    propagate=1)
        if not self._simulation_mode:
            self.motion.run(items=items)

    # ------------------------------------------------------------------------
    # stop
    # ------------------------------------------------------------------------

    def stop(self):
        #surpass the PoolElement.stop because it doesn't do what we want
        PoolBaseElement.stop(self)
        PoolBaseGroup.stop(self)

    # ------------------------------------------------------------------------
    # abort
    # ------------------------------------------------------------------------

    def abort(self):
        #surpass the PoolElement.abort because it doesn't do what we want
        PoolBaseElement.abort(self)
        PoolBaseGroup.abort(self)

    # ------------------------------------------------------------------------
    # involved in an operation
    # ------------------------------------------------------------------------

    def get_operation(self):
        return PoolBaseGroup.get_operation(self)
