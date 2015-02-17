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

"""This file contains the pool monitor class"""

__all__ = ["PoolMonitor"]

__docformat__ = 'restructuredtext'

import time
import threading

from taurus.core.util.log import Logger

from sardana import ElementType, TYPE_PSEUDO_ELEMENTS

from sardana.pool.poolobject import PoolObject


class PoolMonitor(Logger, threading.Thread):

    MIN_THREADS = 1
    MAX_THREADS = 10

    def __init__(self, pool, name='PoolMonitor', period=5.0, min_sleep=1.0,
                 auto_start=True):
        Logger.__init__(self, name)
        threading.Thread.__init__(self, name=name)
        self.daemon = True
        self._period = period
        self._min_sleep = min_sleep
        self._pool = pool
        self._stop = False
        self._pause = threading.Event()
        self._thread_pool = None
        self._ctrl_ids = []
        self._elem_ids = []
        pool.add_listener(self.on_pool_changed)
        if not auto_start:
            self.pause()
        self.start()

    def on_pool_changed(self, evt_src, evt_type, evt_value):
        evt_name = evt_type.name.lower()
        if "created" in evt_name or "deleted" in evt_name:
            pool = self._pool
            pool_ctrls = pool.get_elements_by_type(ElementType.Controller)
            pool_ctrls.sort(key=PoolObject.get_id)
            ctrl_ids = []
            elem_ids = []
            for pool_ctrl in pool_ctrls:
                if not pool_ctrl.is_online():
                    continue
                types = set(pool_ctrl.get_ctrl_types())
                if types.isdisjoint(TYPE_PSEUDO_ELEMENTS):
                    ctrl_ids.append(pool_ctrl.id)
                    elem_ids.extend(pool_ctrl.get_element_ids().keys())
            elem_ids.sort()
            self._elem_ids = elem_ids
            self._ctrl_ids = ctrl_ids

    def update_state_info(self):
        """Update state information of every element."""

        pool = self._pool
        elems, ctrls, ctrl_items = [], [], {}
        try:
            blocked_ctrls = set()
            for elem_id in self._elem_ids:
                elem = pool.get_element_by_id(elem_id)
                ctrl = elem.controller
                if elem.is_in_operation():
                    blocked_ctrls.add(ctrl)
                    continue
                if ctrl in blocked_ctrls:
                    continue
                ret = elem.lock(blocking=False)
                if ret:
                    elems.append(elem)
                    ctrl_elems = ctrl_items.get(ctrl)
                    if ctrl_elems is None:
                        ctrl_items[ctrl] = ctrl_elems = []
                    ctrl_elems.append(elem)
                else:
                    blocked_ctrls.add(ctrl)

            for ctrl, ctrl_elems in ctrl_items.items():
                ret = ctrl.lock(blocking=False)
                if ret:
                    ctrls.append(ctrl)
                else:
                    for elem in reversed(ctrl_elems):
                        elem.unlock()
                        elems.remove(elem)

            self._update_state_info_serial(ctrl_items)
        finally:
            for ctrl in reversed(ctrls):
                ctrl.unlock()
            for elem in reversed(elems):
                elem.unlock()

    def _update_state_info_serial(self, pool_ctrls):
        for pool_ctrl, elems in pool_ctrls.items():
            self._update_ctrl_state_info(pool_ctrl, elems)

    def _update_ctrl_state_info(self, pool_ctrl, elems):
        axes = [elem.axis for elem in elems]
        state_infos, exc_info = pool_ctrl.raw_read_axis_states(axes)
        if len(exc_info):
            self.info("STATE ERROR %s", exc_info)
        for elem, state_info in state_infos.items():
            state_info = elem._from_ctrl_state_info(state_info)
            elem.set_state_info(state_info)

    def stop(self):
        self.resume()
        self._stop = True

    def pause(self):
        self._pause.clear()

    def resume(self):
        self._pause.set()

    def monitor(self):
        ret = self.update_state_info()

    def run(self):
        nap_time = period = self._period
        i, startup = 0, time.time()
        while True:
            if self._stop:
                break
            time.sleep(nap_time)
            self._pause.wait()
            self.monitor()
            finish = time.time()
            nap_time = -1
            while nap_time < 0:
                i += 1
                nap_time = (startup + i * self._period) - finish
