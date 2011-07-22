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

__all__ = [ "PoolAction", "PoolActionItem", "get_thread_pool" ]

__docformat__ = 'restructuredtext'

import sys
import time
import weakref
import traceback

from taurus.core.util import Logger, DebugIt, InfoIt

from sardana import State
from pooldefs import ControllerOfflineException

def get_thread_pool():
    import pool
    return pool.get_thread_pool()


class PoolActionItem(object):
    
    def __init__(self, element):
        self._element = weakref.ref(element)

    def get_element(self):
        return self._element()
    
    element = property(get_element)
    

class PoolAction(Logger):
    
    def __init__(self, name="GlobalAction"):
        Logger.__init__(self, name)
        self._elements = []
        self._pool_ctrls = {}

    def add_element(self, element):
        ctrl_items = self._pool_ctrls.get(element.controller)
        if ctrl_items is None:
            ctrl_items = []
            self._pool_ctrls[element.controller] = ctrl_items
        
        #element = weakref.ref(element)
        self._elements.append(element)
        ctrl_items.append(element)
    
    def remove_element(self, element):
        ctrl = element.controller
        #element = weakref.ref(element)
        try:
            idx = self._elements.index(element)
        except ValueError:
            raise Exception("action doesn't contain %s" % element.name)
        del self._elements[idx]
        ctrl_items = self._pool_ctrls[ctrl]
        del ctrl_items[ctrl_items.index(element)]
        if not len(ctrl_items):
            del self._pool_ctrls[ctrl]
    
    def get_elements(self):
        return self._elements
    
    def get_pool_controllers(self):
        return self._pool_ctrls
    
    def _is_in_action(self, state):
        return state == State.Moving or state == State.Running
    
    def run(self, *args, **kwargs):
        synch = kwargs.pop("synch", False)
        self.start_action(*args, **kwargs)
        if synch:
            self.action_loop()
        else:
            get_thread_pool().add(self.action_loop)
    
    def start_action(self, *args, **kwargs):
        raise NotImplementedError("start_action must be implemented in subclass")
    
    def action_loop(self):
        raise NotImplementedError("action_loop must be implemented in subclass")
    
    def read_state_info(self, ret=None, serial=False):
        if ret is None: ret = {}
        self._state_count = len(self._pool_ctrls)
        read = self._read_state_info_concurrent
        if serial:
            read = self._read_state_info_serial

        return read(ret)

    def _read_state_info_serial(self, ret):
        for pool_ctrl in self._pool_ctrls:
            self._read_ctrl_state_info(ret, pool_ctrl)
        return ret

    def _read_state_info_concurrent(self, ret):
        tp = get_thread_pool()
        for pool_ctrl in self._pool_ctrls:
            tp.add(self._read_ctrl_state_info, None, ret, pool_ctrl)
        
        while self._state_count > 0:
            self.debug("waiting for all controllers to finish")
            time.sleep(0.01)
        return ret
    
    def _get_ctrl_error_state_info(self, pool_ctrl):
        exc_type, exc_value, tb = sys.exc_info()
        if exc_type is None:
            if pool_ctrl.is_online():
                return State.Fault, "Unknown controller error"
        else:
            if pool_ctrl.is_online():
                s = "".join(traceback.format_exception(exc_type, exc_value, tb))
                return State.Fault, "Unexpected controller error:\n" + s
        return State.Fault, pool_ctrl.get_ctrl_error_str()
    
    def _read_ctrl_state_info(self, ret, pool_ctrl):
        try:
            axises = [ elem.axis for elem in self._pool_ctrls[pool_ctrl] ]
            state_infos = pool_ctrl.read_axis_states(axises)
            ret.update( state_infos )
        except:
            state_info = self._get_ctrl_error_state_info(pool_ctrl)
            for elem in self._pool_ctrls[pool_ctrl]:
                ret[elem] = state_info
        finally:
            self._state_count = max(0, self._state_count-1)

    def read_value(self, ret=None, serial=False):
        if ret is None: ret = {}
        self._value_count = len(self._pool_ctrls)
        read = self._read_value_concurrent
        if serial:
            read = self._read_value_serial

        return read(ret)

    def _read_value_serial(self, ret):
        for pool_ctrl in self._pool_ctrls:
            self._read_ctrl_value(ret, pool_ctrl)
        return ret

    def _read_value_concurrent(self, ret):
        tp = get_thread_pool()
        for pool_ctrl in self._pool_ctrls:
            tp.add(self._read_ctrl_value, None, ret, pool_ctrl)
        
        while self._value_count > 0:
            self.debug("waiting for all controllers to finish")
            time.sleep(0.01)
        return ret
    
    def _read_ctrl_value(self, ret, pool_ctrl):
        try:
            axises = [ elem.axis for elem in self._pool_ctrls[pool_ctrl] ]
            value_infos = pool_ctrl.read_axis_values(axises)
            ret.update( value_infos )
        finally:
            self._value_count = max(0, self._value_count-1)
    
    
    def abort(self, element=None):
        self._aborted = True
        if element is None:
            pass # TODO
        else:
            element.controller.ctrl.AbortOne(element.axis)
