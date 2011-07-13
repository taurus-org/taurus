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

"""This file contains the pool monitor class"""

__all__ = ["PoolMonitor"]

__docformat__ = 'restructuredtext'

import os.path
import threading
import time

import taurus.core.util

from poolcontrollermanager import ControllerManager

from poolbase import *
from pooldefs import *
from poolelement import *
from poolcontroller import *
from poolmotor import *


class PoolMonitor(taurus.core.util.Logger, threading.Thread):
    
    def __init__(self, pool, name='PoolMonitor', period=5.0, min_sleep=1.0, auto_start=True):
        taurus.core.util.Logger.__init__(self, name)
        threading.Thread.__init__(self, name=name)
        self.daemon = True
        self._period = period
        self._min_sleep = min_sleep
        self._pool = pool
        self._stop = False
        if auto_start:
            self.start()
    
    def on_pool_changed(self, evt_src, evt_type, evt_value):
        evt_name = evt_type.name
        
        if evt_name == 'ElementCreated':
            pass
        elif evt_name == 'ElementDeleted':
            pass
    
    def update_state_info(self):
        """"""
        pool = self._pool
        pool_ctrls = pool.get_element_type_map().get(ElementType.Ctrl, {}).values()
        pool_ctrls = [ ctrl for ctrl in pool_ctrls if ctrl.is_online() ]

        for pool_ctrl in pool_ctrls:
            state_infos = pool_ctrl.read_axis_states()
            for elem, state_info in state_infos.items():
                state_info = elem._from_ctrl_state_info(state_info)
                elem.set_state_info(state_info)
        
    
    # old read_state_info 
    def read_state_info_old(self, pool_ctrls):
        pool = self._pool
        pool_ctrls = pool.get_element_type_map().get(ElementType.Ctrl, {}).values()
        pool_ctrls = [ ctrl for ctrl in pool_ctrls if ctrl.is_online() ]

        # PreStateAll on all controllers
        for pool_ctrl in pool_ctrls: pool_ctrl.ctrl.PreStateAll()
        
        # PreReadOne on all elements
        for pool_ctrl in pool_ctrls:
            elems_axis = pool_ctrl.get_element_axis()
            for axis in elems_axis:
                pool_ctrl.ctrl.PreStateOne(axis)

        # StateAll on all controllers
        for pool_ctrl in pool_ctrls: pool_ctrl.ctrl.StateAll()
        
        # for StateOne on all elements
        for pool_ctrl in pool_ctrls:
            elems_axis = pool_ctrl.get_element_axis()
            for axis, elem in elems_axis.items():
                state_info = pool_ctrl.ctrl.StateOne(axis)
                state_info = elem._from_ctrl_state_info(state_info)
                elem.set_state_info(state_info)
        
    def stop(self):
        self._stop = True

    def monitor(self):
        start = time.time()
        
        ret = self.update_state_info()
        
        finish = time.time()
        sleep_time = self._period
        # sleep_time = max(self._period - (finish-start), self._min_sleep)
        time.sleep(sleep_time)

    def run(self):
        while not self._stop:
            self.monitor()
    
