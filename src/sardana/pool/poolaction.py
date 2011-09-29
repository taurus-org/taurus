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

"""This module is part of the Python Pool libray. It defines the class for an
abstract action over a set of pool elements"""

__all__ = [ "OperationInfo", "PoolAction", "PoolActionItem", "get_thread_pool" ]

__docformat__ = 'restructuredtext'

import sys
import weakref
import traceback
import threading
import copy

from taurus.core.util import Logger
#from taurus.core.util import DebugIt, InfoIt

from sardana import State

def get_thread_pool():
    """Returns the global pool of threads"""
    from sardana.pool.pool import get_thread_pool as gtp
    return gtp()


class PoolActionItem(object):
    """The base class for an atomic action item"""
    
    def __init__(self, element):
        self._element = weakref.ref(element)

    def get_element(self):
        """Returns the element associated with this item"""
        return self._element()
    
    def set_element(self, element):
        """Sets the element for this item"""
        self._element = weakref.ref(element)
    
    element = property(get_element)
    

class OperationInfo(object):
    """Stores synchronization data for a certain operation"""
    
    def __init__(self):
        self.state_count = 0
        self.state_lock = threading.Lock()
        self.state_event_lock = threading.Lock()
        self.state_event = threading.Event()
        
    def init(self, count):
        """Initializes this operation with a certain count"""
        self.state_count = count
        self.state_event.clear()
    
    def wait(self, timeout=None):
        """waits for the operation to finish"""
        return self.state_event.wait(timeout)
        
    def finish_one(self):
        """Notifies this operation that one step was finished"""
        with self.state_event_lock:
            self.state_count = self.state_count - 1
            if self.state_count < 1:
                self.state_count = 0
                self.state_event.set()
    
    def acquire(self):
        """Acquires this operation lock"""
        self.state_lock.acquire()
    
    def release(self):
        """Releases this operation lock"""
        self.state_lock.release()
    
    def __enter__(self):
        return self.acquire()
    
    def __exit__(self, exc_type, exc_value, exc_traceback):
        return self.release()


class OperationContext(object):
    """Stores operation context"""
    
    def __init__(self, pool_action):
        self._pool_action = pool_action
    
    def enter(self):
        """Enters operation context"""
        self._pool_action.warning("Context enter")
        pool_action = self._pool_action
        for element in pool_action.get_elements():
            element.set_operation(pool_action)
    
    def exit(self):
        """Leaves operation context"""
        self._pool_action.warning("Context exit")
        pool_action = self._pool_action
        for element in pool_action.get_elements():
            element.clear_operation()
    
    def __enter__(self):
        return self.enter()
        
    def __exit__(self, exc_type, exc_value, exc_traceback):
        return self.exit()
    

class PoolAction(Logger):
    """A generic class to handle any type of operation (like motion or
    acquisition)"""
    
    def __init__(self, pool, name="GlobalAction"):
        Logger.__init__(self, name)
        self._pool = pool
        self._aborted = False
        self._stopped = False
        self._elements = []
        self._pool_ctrls = {}
        self._state_info = OperationInfo()
        self._value_info = OperationInfo()

    def add_element(self, element):
        """Adds a new element to this action.
        
        :param element: the new element to be added
        :type element: sardana.pool.poolelement.PoolElement"""
        ctrl_items = self._pool_ctrls.get(element.controller)
        if ctrl_items is None:
            ctrl_items = []
            self._pool_ctrls[element.controller] = ctrl_items

        self._elements.append(element)
        ctrl_items.append(element)
    
    def remove_element(self, element):
        """Removes an element from this action. If the element is not part of
        this action, a ValueError is raised.
        
        :param element: the new element to be removed
        :type element: sardana.pool.poolelement.PoolElement
        
        :raises: ValueError"""
        ctrl = element.controller
        #element = weakref.ref(element)
        try:
            idx = self._elements.index(element)
        except ValueError:
            raise ValueError("action doesn't contain %s" % element.name)
        del self._elements[idx]
        ctrl_items = self._pool_ctrls[ctrl]
        del ctrl_items[ctrl_items.index(element)]
        if not len(ctrl_items):
            del self._pool_ctrls[ctrl]
    
    def get_elements(self, copy_of=False):
        """Returns a sequence of all elements involved in this action.
        
        :param copy_of: If False (default) the internal container of elements is
                        returned. If True, a copy of the internal container is
                        returned instead
        :type copy_of: bool
        :return: a sequence of all elements involved in this action.
        :rtype: seq<sardana.pool.poolelement.PoolElement>"""
        elements = self._elements
        if copy_of:
            elements = tuple(elements)
        return elements
    
    def get_pool_controllers(self, copy_of=False):
        """Returns a map of all controller elements involved in this action.
        
        :param copy_of: If False (default) the internal container of controllers
                        is returned. If True, a copy of the internal container
                        is returned instead
        :type copy_of: bool
        :return: a sequence of all controller elements involved in this action.
        :rtype: seq<sardana.pool.poolelement.PoolController>"""
        pool_ctrls = self._pool_ctrls
        if copy_of:
            pool_ctrls = copy.deepcopy(pool_ctrls)
        return pool_ctrls
    
    def _is_in_action(self, state):
        """Determines if the given state is a busy state (Moving or Running) or
        not.
        
        :return: True if state is a busy state or False otherwise
        :rtype: bool"""
        return state == State.Moving or state == State.Running
    
    def run(self, *args, **kwargs):
        """Runs this action"""
        synch = kwargs.pop("synch", False)
        
        if synch:
            with OperationContext(self):
                try:
                    self.start_action(*args, **kwargs)
                    self.action_loop()
                finally:
                    try:
                        self.finish_action()
                    except:
                        self.warning("Unable to finish action", exc_info=1)
        else:
            context = OperationContext(self)
            context.enter()
            try:
                self.start_action(*args, **kwargs)
            except:
                try:
                    self.finish_action()
                except:
                    self.warning("Unable to finish action", exc_info=1)
                context.exit()
                raise
            get_thread_pool().add(self._asynch_action_loop, None, context)
        
    
    def start_action(self, *args, **kwargs):
        """Start procedure for this action. Default implementation raises
        NotImplementedError
        
        :raises: NotImplementedError"""
        raise NotImplementedError("start_action must be implemented in "
                                  "subclass")
    
    def finish_action(self, *args, **kwargs):
        pass
    
    def stop_action(self, *args, **kwargs):
        """Stop procedure for this action."""
        self._stopped = True
        for pool_ctrl, elements in self._pool_ctrls.items():
            pool_ctrl.stop_elements(elements)

    def abort_action(self, *args, **kwargs):
        """Aborts procedure for this action"""
        self._aborted = True
        for pool_ctrl, elements in self._pool_ctrls.items():
            pool_ctrl.abort_elements(elements)

    def was_stopped(self):
        return self._stopped
    
    def was_aborted(self):
        return self._aborted
    
    def was_action_interrupted(self):
        return self.was_aborted() or self.was_stopped()

    def _asynch_action_loop(self, context):
        """Internal method. Asynchronous action loop"""
        try:
            self.action_loop()
        finally:
            try:
                self.finish_action()
            except:
                self.warning("Unable to finish action", exc_info=1)
            context.exit()
    
    def action_loop(self):
        """Action loop for this action. Default implementation raises
        NotImplementedError
        
        :raises: NotImplementedError"""
        raise NotImplementedError("action_loop must be implemented in subclass")
    
    def read_state_info(self, ret=None, serial=False):
        """Reads state information of all elements involved in this action
        
        :param ret: output map parameter that should be filled with state
                    information. If None is given (default), a new map is
                    created an returned
        :type ret: dict
        :param serial: If False (default) perform controller HW state requests
                       in parallel. If True, access is serialized.
        :type serial: bool
        :return: a map containing state information per element
        :rtype: dict<sardana.pool.poolelement.PoolElement, stateinfo>"""
        if ret is None:
            ret = {}
        read = self._read_state_info_concurrent
        if serial:
            read = self._read_state_info_serial
        state_info = self._state_info
        with state_info:
            state_info.init(len(self._pool_ctrls))
            read(ret)
            state_info.wait()
        return ret

    def _read_state_info_serial(self, ret):
        """Internal method. Read state in a serial mode"""
        for pool_ctrl in self._pool_ctrls:
            self._read_ctrl_state_info(ret, pool_ctrl)
        return ret

    def _read_state_info_concurrent(self, ret):
        """Internal method. Read state in a concurrent mode"""
        th_pool = get_thread_pool()
        for pool_ctrl in self._pool_ctrls:
            th_pool.add(self._read_ctrl_state_info, None, ret, pool_ctrl)
        return ret
    
    def _get_ctrl_error_state_info(self, pool_ctrl):
        """Internal method. Returns the controller error in form of a 
        tuple<sardana.State, str>"""
        exc_t, exc_v, trb = sys.exc_info()
        if exc_t is None:
            if pool_ctrl.is_online():
                return State.Fault, "Unknown controller error"
        else:
            if pool_ctrl.is_online():
                err_msg = "".join(traceback.format_exception(exc_t, exc_v, trb))
                return State.Fault, "Unexpected controller error:\n" + err_msg
        return State.Fault, pool_ctrl.get_ctrl_error_str()
    
    def _read_ctrl_state_info(self, ret, pool_ctrl):
        """Internal method. Read controller information and store it in ret
        parameter"""
        try:
            axises = [ elem.axis for elem in self._pool_ctrls[pool_ctrl] ]
            state_infos = pool_ctrl.read_axis_states(axises)
            ret.update( state_infos )
        except:
            self.error("Something wrong happend: Error should have been caught"
                       "by ctrl.read_axis_states", exc_info=1)
            state_info = self._get_ctrl_error_state_info(pool_ctrl)
            for elem in self._pool_ctrls[pool_ctrl]:
                ret[elem] = state_info
        finally:
            self._state_info.finish_one()

    def read_value(self, ret=None, serial=False):
        """Reads value information of all elements involved in this action
        
        :param ret: output map parameter that should be filled with value
                    information. If None is given (default), a new map is
                    created an returned
        :type ret: dict
        :param serial: If False (default) perform controller HW value requests
                       in parallel. If True, access is serialized.
        :type serial: bool
        :return: a map containing value information per element
        :rtype: dict<sardana.pool.poolelement.PoolElement, object>"""
        
        if ret is None:
            ret = {}
        
        read = self._read_value_concurrent
        if serial:
            read = self._read_value_serial
        
        value_info = self._value_info
        
        with value_info:
            value_info.init(len(self._pool_ctrls))
            read(ret)
            value_info.wait()
        return ret

    def _read_value_serial(self, ret):
        """Internal method. Read value in a serial mode"""
        for pool_ctrl in self._pool_ctrls:
            self._read_ctrl_value(ret, pool_ctrl)
        return ret

    def _read_value_concurrent(self, ret):
        """Internal method. Read value in a concurrent mode"""
        th_pool = get_thread_pool()
        for pool_ctrl in self._pool_ctrls:
            th_pool.add(self._read_ctrl_value, None, ret, pool_ctrl)
        return ret
    
    def _read_ctrl_value(self, ret, pool_ctrl):
        """Internal method. Read controller value information and store it in
        ret parameter"""
        try:
            axises = [ elem.axis for elem in self._pool_ctrls[pool_ctrl] ]
            value_infos = pool_ctrl.read_axis_values(axises)
            ret.update( value_infos )
        finally:
            self._value_info.finish_one()
    