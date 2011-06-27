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

__all__ = [ "PoolAction", "PoolActionItem" ]

__docformat__ = 'restructuredtext'

import weakref

import taurus.core.util

from pooldefs import State

def ThreadPool():
    import pool
    return pool.ThreadPool()

class PoolActionItem(object):
    
    def __init__(self, element):
        pass

class PoolAction(taurus.core.util.Logger):
    
    def __init__(self, name="GlobalAction"):
        taurus.core.util.Logger.__init__(self, name)
        self._elements = []
        self._pool_ctrls = {}

    def add_element(self, element):
        ctrl_items = self._pool_ctrls.get(element.controller)
        if ctrl_items is None:
            ctrl_items = []
            self._pool_ctrls[element.controller] = ctrl_items
        
        element = weakref.ref(element)
        self._elements.append(element)
        ctrl_items.append(element)
    
    def remove_element(self, element):
        ctrl = element.controller
        element = weakref.ref(element)
        try:
            idx = self._elements.index(element)
        except ValueError:
            raise Exception("action doesn't contain %s" % element.name)
        del self._elements[idx]
        ctrl_items = self._pool_ctrls[ctrl]
        del ctrl_items[ctrl_items.index(element)]
        if not len(ctrl_items):
            del self._pool_ctrls[ctrl]
    
    def _is_in_action(self, state):
        return state == State.Moving or state == State.Running
    
    def run(self, *args, **kwargs):
        synch = kwargs.pop("synch", False)
        self.start_action(*args, **kwargs)
        if synch:
            self.action_loop()
        else:
            ThreadPool().add(self.action_loop)

    def start_action(self, *args, **kwargs):
        raise RuntimeError("start_action must be implemented in subclass")
    
    def action_loop(self):
        raise RuntimeError("action_loop must be implemented in subclass")
    
    def read_state_info(self, ret=None):
        """"""
        pool_ctrls = self._pool_ctrls.keys()
        elements = ret or [ element() for element in self._elements ]
        
        # PreReadAll on all controllers
        for pool_ctrl in pool_ctrls: pool_ctrl.ctrl.PreStateAll()
        
        # PreReadOne on all elements
        for element in elements:
            element.controller.ctrl.PreStateOne(element.axis)
        
        # ReadAll on all controllers
        for pool_ctrl in pool_ctrls: pool_ctrl.ctrl.StateAll()
        
        ret = ret or {}
        
        # PreReadOne on all elements
        for element in elements:
            info = element.controller.ctrl.StateOne(element.axis)
            ret[element] = info
        
        return ret
    
    def read_value(self, ret=None):
        """"""
        pool_ctrls = self._pool_ctrls.keys()
        elements = [ element() for element in self._elements ]
        
        # PreReadAll on all controllers
        for pool_ctrl in pool_ctrls: pool_ctrl.ctrl.PreReadAll()
        
        # PreReadOne on all elements
        for element in elements:
            element.controller.ctrl.PreReadOne(element.axis)

        # ReadAll on all controllers
        for pool_ctrl in pool_ctrls: pool_ctrl.ctrl.ReadAll()

        ret = ret or {}
        
        # PreReadOne on all elements
        for element in elements:
            ret[element] = element.controller.ctrl.ReadOne(element.axis)
        
        return ret
    
    def abort(self, element=None):
        self._aborted = True
        if element is None:
            pass # TODO
        else:
            element.controller.ctrl.AbortOne(element.axis)
