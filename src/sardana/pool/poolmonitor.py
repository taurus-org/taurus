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

from taurus.core.util import Logger, ThreadPool, DebugIt, InfoIt

from poolcontrollermanager import ControllerManager

from poolbase import *
from pooldefs import *
from poolelement import *
from poolcontroller import *
from poolmotor import *


class PoolMonitor(Logger, threading.Thread):
    
    MIN_THREADS =  1
    MAX_THREADS = 10
    
    def __init__(self, pool, name='PoolMonitor', period=5.0, min_sleep=1.0, auto_start=True):
        Logger.__init__(self, name)
        threading.Thread.__init__(self, name=name)
        self.daemon = True
        self._period = period
        self._min_sleep = min_sleep
        self._pool = pool
        self._stop = False
        self._thread_pool = None
        if auto_start:
            self.start()
    
    def on_pool_changed(self, evt_src, evt_type, evt_value):
        evt_name = evt_type.name
        
        if evt_name == 'ElementCreated':
            pass
        elif evt_name == 'ElementDeleted':
            pass
    
    def _readjust_thread_pool(self, pool_ctrls):
        nb_ctrls = len(pool_ctrls)
        tp = self._thread_pool
        if tp is None:
            nb_threads = 0
        else:
            nb_threads = tp.size
        n = min(self.MAX_THREADS, nb_ctrls)
        n = max(self.MIN_THREADS, n)
        if nb_threads == n:
            return
        else:
            if tp is None:
                self.info("Creating monitor pool of threads %d", n)
                tp = ThreadPool(name=self.name, Psize=n)
                self._thread_pool = tp
            else:
                self.info("Readjusting monitor pool of threads from %d to %d", nb_threads, n)
                self._thread_pool.size = n
    
    def update_state_info(self, serial=False, wait=True):
        """Update state information of every element.
        
        :param serial: serialize or not controller access. Default is False meaning
                       use concurrent access to all controllers
        :type serial: bool
        :param wait: wheater or not to wait for end of procedure. Ignored when
                     serial==True. Default is True.
        :type wait: bool
        """
        pool = self._pool
        pool_ctrls = pool.get_element_type_map().get(ElementType.Ctrl, {}).values()
        pool_ctrls = [ ctrl for ctrl in pool_ctrls if ctrl.is_online() ]

        update = self._update_state_info_concurrent
        if serial:
            update = self._update_state_info_serial
        
        self._state_count = len(pool_ctrls)
        update(pool_ctrls)
        while self._state_count > 0:
            self.debug("waiting for all controllers to finish")
            time.sleep(0.01)
            
    def _update_state_info_serial(self, pool_ctrls):
        for pool_ctrl in pool_ctrls:
            self._update_ctrl_state_info(pool_ctrl)

    def _update_state_info_concurrent(self, pool_ctrls):
        self._readjust_thread_pool(pool_ctrls)
        for pool_ctrl in pool_ctrls:
            self._thread_pool.add(self._update_ctrl_state_info, None, pool_ctrl)
    
    def _update_ctrl_state_info(self, pool_ctrl):
        try:
            state_infos = pool_ctrl.read_axis_states()
            for elem, state_info in state_infos.items():
                state_info = elem._from_ctrl_state_info(state_info)
                elem.set_state_info(state_info)
        finally:
            self._state_count = max(0, self._state_count-1)
            
    def stop(self):
        self._stop = True

    def monitor(self):
        ret = self.update_state_info()
    
    def run(self):
        nap_time = period = self._period
        i, startup = 0, time.time()
        while not self._stop:
            time.sleep(nap_time)
            self.monitor()
            finish = time.time()
            nap_time = -1
            while nap_time < 0:
                i += 1
                nap_time = (startup + i*period) - finish
