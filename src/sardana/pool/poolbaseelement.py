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

__all__ = ["PoolBaseElement"]

__docformat__ = 'restructuredtext'

import weakref
import threading

from taurus.core.util.lock import TaurusLock

from sardana import State
from sardana.sardanaevent import EventType
from sardana.pool.poolobject import PoolObject


class PoolBaseElement(PoolObject):
    """A Pool object that besides the name, reference to the pool, ID, full_name
    and user_full_name has:
       
       - _simulation_mode : boolean telling if in simulation mode
       - _state : element state
       - _status : element status"""

    def __init__(self, **kwargs):
        self._simulation_mode = False
        self._state = None
        self._state_event = None
        self._status = None
        self._status_event = None
        self._action_cache = None
        self._aborted = False
        self._stopped = False

        lock_name = kwargs['name'] + "Lock"

        # A lock for high level operations: monitoring, motion or acquisition
        self._lock = TaurusLock(name=lock_name, lock=threading.RLock())

        # The operation context in which the element is involved
        self._operation = None

        # The :class:`PoolAction` in which element is involved
        self._pool_action = None

        super(PoolBaseElement, self).__init__(**kwargs)

    def __enter__(self):
        self.lock()

    def __exit__(self, exc_type, exc_value, traceback):
        self.unlock()
        return False

    def lock(self, blocking=True):
        """Acquires the this element lock
        
        :param blocking:
            whether or not to block if lock is already acquired [default: True]
        :type blocking: bool"""
        ret = self._lock.acquire(blocking)
        return ret

    def unlock(self):
        ret = self._lock.release()
        return ret

    def get_action_cache(self):
        """Returns the internal action cache object"""
        return self._action_cache

    def serialize(self, *args, **kwargs):
        ret = PoolObject.serialize(self, *args, **kwargs)
        return ret

    # --------------------------------------------------------------------------
    # simulation mode
    # --------------------------------------------------------------------------

    def get_simulation_mode(self, cache=True, propagate=1):
        """Returns the simulation mode for this object.
        
        :param cache: not used [default: True]
        :type cache: bool
        :param propagate: [default: 1]
        :type propagate: int
        :return: the current simulation mode
        :rtype: bool"""
        return self._simulation_mode

    def set_simulation_mode(self, simulation_mode, propagate=1):
        self._simulation_mode = simulation_mode
        if not propagate:
            return
        if simulation_mode == self._simulation_mode:
            # current state is equal to last state_event. Skip event
            return
        self.fire_event(EventType("simulation_mode", priority=propagate),
                        simulation_mode)

    def put_simulation_mode(self, simulation_mode):
        self._simulation_mode = simulation_mode

    simulation_mode = property(get_simulation_mode, set_simulation_mode,
                               doc="element simulation mode")

    # --------------------------------------------------------------------------
    # state
    # --------------------------------------------------------------------------

    def get_state(self, cache=True, propagate=1):
        """Returns the state for this object. If cache is True (default) it
        returns the current state stored in cache (it will force an update if
        cache is empty). If propagate > 0 and if the state changed since last
        read, it will propagate the state event to all listeners.
        
        :param cache:
            tells if return value from local cache or update from HW read
            [default: True]
        :type cache: bool
        :param propagate:
            if > 0 propagates the event in case it changed since last HW read.
            Values bigger that mean the event if sent should be a priority event
            [default: 1]
        :type propagate: int
        :return: the current object state
        :rtype: :obj:`sardana.State`"""
        if not cache or self._state is None:
            state_info = self.read_state_info()
            self._set_state_info(state_info, propagate=propagate)
        return self._state

    def inspect_state(self):
        """Looks at the current cached value of state

        :return: the current object state
        :rtype: :obj:`sardana.State`"""
        return self._state

    def set_state(self, state, propagate=1):
        self._set_state(state, propagate=propagate)

    def _set_state(self, state, propagate=1):
        self._state = state
        if not propagate:
            return
        if state == self._state_event:
            # current state is equal to last state_event. Skip event
            return
        self._state_event = state
        self.fire_event(EventType("state", priority=propagate), state)

    def put_state(self, state):
        self._state = state

    state = property(get_state, set_state, doc="element state")

    # --------------------------------------------------------------------------
    # status
    # --------------------------------------------------------------------------

    def inspect_status(self):
        """Looks at the current cached value of status

        :return: the current object status
        :rtype: str"""
        return self._status

    def get_status(self, cache=True, propagate=1):
        """Returns the status for this object. If cache is True (default) it
        returns the current status stored in cache (it will force an update if
        cache is empty). If propagate > 0 and if the status changed since last
        read, it will propagate the status event to all listeners.
        
        :param cache:
            tells if return value from local cache or update from HW read
            [default: True]
        :type cache: bool
        :param propagate:
            if > 0 propagates the event in case it changed since last HW read.
            Values bigger that mean the event if sent should be a priority event
            [default: 1]
        :type propagate: int
        :return: the current object status
        :rtype: str"""
        if not cache or self._status is None:
            state_info = self.read_state_info()
            self._set_state_info(state_info, propagate=propagate)
        return self._status

    def set_status(self, status, propagate=1):
        self._set_status(status, propagate=propagate)

    def _set_status(self, status, propagate=1):
        self._status = status
        if not propagate:
            return
        s_evt = self._status_event
        if s_evt is not None and len(status) == len(s_evt) and status == s_evt:
            # current status is equal to last status_event. Skip event
            return
        self._status_event = status
        self.fire_event(EventType("status", priority=propagate), status)

    def put_status(self, status):
        self._status = status

    status = property(get_status, set_status, doc="element status")

    # --------------------------------------------------------------------------
    # state information
    # --------------------------------------------------------------------------

    _STD_STATUS = "{name} is {state}\n{ctrl_status}"
    def calculate_state_info(self, status_info=None):
        """Transforms the given state information. This specific base
        implementation transforms the given state,status tuple into a
        state, new_status tuple where new_status is "*self.name* is *state*
        plus the given status.
        It is assumed that the given status comes directly from the controller
        status information.
        
        :param status_info:
            given status information [default: None, meaning use current state status.
        :type status_info: tuple<State, str>
        :return: a transformed state information
        :rtype: tuple<State, str>"""
        if status_info is None:
            status_info = self._state, self._status
        state, status = status_info
        state_str = State[state]
        new_status = self._STD_STATUS.format(name=self.name, state=state_str,
                                             ctrl_status=status)
        return status_info[0], new_status

    def set_state_info(self, state_info, propagate=1):
        self._set_state_info(state_info, propagate=propagate)

    def _set_state_info(self, state_info, propagate=1):
        state_info = self.calculate_state_info(state_info)
        state, status = state_info[:2]
        self._set_status(status, propagate=propagate)
        self._set_state(state, propagate=propagate)

    def read_state_info(self):
        action_cache = self.get_action_cache()
        ctrl_state_info = action_cache.read_state_info(serial=True)[self]
        return self._from_ctrl_state_info(ctrl_state_info)

    def put_state_info(self, state_info):
        self.set_state_info(state_info, propagate=0)

    def _from_ctrl_state_info(self, state_info):
        try:
            state_str = State.whatis(state_info)
            return int(state_info), "{0} is in {1}".format(self.name, state_str)
        except KeyError:
            pass
        state_info, _ = state_info
        state, status = state_info[:2]
        state = int(state)
        return state, status

    # --------------------------------------------------------------------------
    # default attribute
    # --------------------------------------------------------------------------

    def get_default_attribute(self):
        return NotImplementedError("%s doesn't have default attribute" % self.__class__.__name__)

    # --------------------------------------------------------------------------
    # default acquisition channel name
    # --------------------------------------------------------------------------

    def get_default_acquisition_channel(self):
        return self.get_default_attribute().name

    # --------------------------------------------------------------------------
    # stop
    # --------------------------------------------------------------------------

    def stop(self):
        self._stopped = True

    def was_stopped(self):
        return self._stopped

    # --------------------------------------------------------------------------
    # abort
    # --------------------------------------------------------------------------

    def abort(self):
        self._aborted = True

    def was_aborted(self):
        return self._aborted

    # --------------------------------------------------------------------------
    # interrupted
    # --------------------------------------------------------------------------

    def was_interrupted(self):
        """Tells if action ended by an abort or stop"""
        return self.was_aborted() or self.was_stopped()

    # --------------------------------------------------------------------------
    # involved in an operation
    # --------------------------------------------------------------------------

    def is_action_running(self):
        """Determines if the element action is running or not."""
        return self.get_action_cache().is_running()

    def is_in_operation(self):
        """Returns True if this element is involved in any operation"""
        return self.get_operation() is not None

    def is_in_local_operation(self):
        return self.get_operation() == self.get_action_cache()

    def get_operation(self):
        return self._operation

    def set_operation(self, operation):
        if self.is_in_operation() and operation is not None:
            raise Exception("%s is already involved in an operation"
                            % self.name)
        if operation is not None:
            self._aborted = False
            self._stopped = False
        self._operation = operation

    def clear_operation(self):
        return self.set_operation(None)