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
acquisition"""

__all__ = [ "AcquisitionState", "AcquisitionMap", "PoolCTAcquisition",
            "Pool0DAcquisition", "Channel", "PoolIORAcquisition" ]

__docformat__ = 'restructuredtext'

import time

from taurus.core.util import Enumeration, DebugIt

from sardana import State, ElementType, TYPE_TIMERABLE_ELEMENTS
from sardana.sardanathreadpool import get_thread_pool
from poolaction import ActionContext, PoolActionItem, PoolAction

#: enumeration representing possible motion states
AcquisitionState = Enumeration("AcquisitionState", ( \
    "Stopped",
#    "StoppedOnError",
#    "StoppedOnAbort",
    "Acquiring",
    "Invalid") )

AS = AcquisitionState
AcquiringStates = AS.Acquiring,
StoppedStates = AS.Stopped, #MS.StoppedOnError, MS.StoppedOnAbort

AcquisitionMap = {
    #AS.Stopped           : State.On,
    AS.Acquiring         : State.Moving,
    AS.Invalid           : State.Invalid,
}

class PoolAcquisition(PoolAction):

    def __init__(self, main_element, name="Acquisition"):
        PoolAction.__init__(self, main_element, name)
        ctname = name + ".CTAcquisition"
        zerodname = name + ".0DAcquisition"
        self._0d_acq = zd_acq = Pool0DAcquisition(main_element, name=zerodname)
        self._ct_acq = PoolCTAcquisition(main_element, name=ctname, slaves=(zd_acq,))

    def run(self, *args, **kwargs):
        n = kwargs.get('multiple', 1)
        if n == 1:
            return self._run_single(*args, **kwargs)
        return self._run_multiple(*args, **kwargs)
    
    def _run_multiple(self, *args, **kwargs):
        n = kwargs['multiple']
        synch = kwargs.get("synch", False)
        if synch:
            for _ in range(n):
                self._run_single(self, *args, **kwargs)
        else:
            kwargs["synch"] = True
            get_thread_pool().add(self._run_multiple, None, *args, **kwargs)
    
    def _run_single(self, *args, **kwargs):
        """Runs this action"""
        synch = kwargs.get("synch", False)
        ct_acq = self._ct_acq
        zd_acq = self._0d_acq
        if synch:
            ct_acq.run(*args, **kwargs)
        else:
            ct_acq.run(*args, **kwargs)
            zd_acq.run(*args, **kwargs)

    def _get_acq_for_element(self, element):
        elem_type = element.get_type()
        if elem_type in TYPE_TIMERABLE_ELEMENTS:
            return self._ct_acq
        elif elem_type == ElementType.ZeroDExpChannel:
            return self._0d_acq

    def clear_elements(self):
        """Clears all elements from this action"""

    def add_element(self, element):
        """Adds a new element to this action.

        :param element: the new element to be added
        :type element: sardana.pool.poolelement.PoolElement"""
        return self._get_acq_for_element(element).add_element(element)

    def remove_element(self, element):
        """Removes an element from this action. If the element is not part of
        this action, a ValueError is raised.

        :param element: the new element to be removed
        :type element: sardana.pool.poolelement.PoolElement

        :raises: ValueError"""
        return self._get_acq_for_element(element).add_element(element)

    def get_elements(self, copy_of=False):
        """Returns a sequence of all elements involved in this action.

        :param copy_of: If False (default) the internal container of elements is
                        returned. If True, a copy of the internal container is
                        returned instead
        :type copy_of: bool
        :return: a sequence of all elements involved in this action.
        :rtype: seq<sardana.pool.poolelement.PoolElement>"""
        return self._ct_acq.get_elements() + self._0d_acq.get_elements()

    def get_pool_controller_list(self):
        """Returns a list of all controller elements involved in this action.

        :return: a list of all controller elements involved in this action.
        :rtype: list<sardana.pool.poolelement.PoolController>"""
        return self._pool_ctrl_list

    def get_pool_controllers(self):
        """Returns a dict of all controller elements involved in this action.

        :return: a dict of all controller elements involved in this action.
        :rtype: dict<sardana.pool.poolelement.PoolController, seq<sardana.pool.poolelement.PoolElement>>"""
        ret = {}
        ret.update(self._ct_acq.get_pool_controllers())
        ret.update(self._0d_acq.get_pool_controllers())
        return ret

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
        :rtype: dict<:class:~`sardana.pool.poolelement.PoolElement`,
                     :class:~`sardana.sardanavalue.SardanaValue`>"""
        ret = self._ct_acq.read_value(ret=ret, serial=serial)
        ret.update(self._0d_acq.read_value(ret=ret, serial=serial))
        return ret


class Channel(PoolActionItem):

    def __init__(self, acquirable, info=None):
        PoolActionItem.__init__(self, acquirable)
        if info:
            self.__dict__.update(info)

    def __getattr__(self, name):
        return getattr(self.element, name)


class PoolCTAcquisition(PoolAction):

    def __init__(self, main_element, name="CTAcquisition", slaves=None):
        self._channels = None

        if slaves is None:
            slaves = ()
        self._slaves = slaves

        PoolAction.__init__(self, main_element, name)

    def get_read_value_loop_ctrls(self):
        return self._pool_ctrl_dict_loop
    
    def start_action(self, *args, **kwargs):
        """Prepares everything for acquisition and starts it.

           :param: config"""

        pool = self.pool

        # prepare data structures
        self._aborted = False
        self._stopped = False

        self._acq_sleep_time = kwargs.pop("acq_sleep_time",
                                             pool.acq_loop_sleep_time)
        self._nb_states_per_value = \
            kwargs.pop("nb_states_per_value",
                       pool.acq_loop_states_per_value)

        self._integ_time = integ_time = kwargs.get("integ_time")
        self._mon_count = mon_count = kwargs.get("monitor_count")
        if integ_time is None and mon_count is None:
            raise Exception("must give integration time or monitor counts")
        if integ_time is not None and mon_count is not None:
            raise Exception("must give either integration time or monitor counts (not both)")

        _ = kwargs.get("items", self.get_elements())
        cfg = kwargs['config']

        # determine which is the controller which holds the master channel
        
        if integ_time is not None:
            master_key = 'timer'
            master_value = integ_time
        if mon_count is not None:
            master_key = 'monitor'
            master_value = - mon_count

        master = cfg[master_key]
        master_ctrl = master.controller

        pool_ctrls_dict = dict(cfg['controllers'])
        pool_ctrls_dict.pop('__tango__', None)
        pool_ctrls = []
        self._pool_ctrl_dict_loop = _pool_ctrl_dict_loop = {}
        for ctrl, v in pool_ctrls_dict.items():
            if ctrl.is_timerable():
                pool_ctrls.append(ctrl)
            if ElementType.CTExpChannel in ctrl.get_ctrl_types():
                _pool_ctrl_dict_loop[ctrl] = v
            
        # make sure the controller which has the master channel is the last to
        # be called
        pool_ctrls.remove(master_ctrl)
        pool_ctrls.append(master_ctrl)

        # Determine which channels are active
        self._channels = channels = {}
        for pool_ctrl in pool_ctrls:
            ctrl = pool_ctrl.ctrl
            pool_ctrl_data = pool_ctrls_dict[pool_ctrl]
            main_unit_data = pool_ctrl_data['units']['0']
            elements = main_unit_data['channels']

            for element, element_info in elements.items():
                axis = element.axis
                channel = Channel(element, info=element_info)
                channels[element] = channel

        #for channel in channels:
        #    channel.prepare_to_acquire(self)

        with ActionContext(self):

            # PreLoadAll, PreLoadOne, LoadOne and LoadAll
            for pool_ctrl in pool_ctrls:
                ctrl = pool_ctrl.ctrl
                pool_ctrl_data = pool_ctrls_dict[pool_ctrl]
                main_unit_data = pool_ctrl_data['units']['0']
                ctrl.PreLoadAll()
                master = main_unit_data[master_key]
                axis = master.axis
                res = ctrl.PreLoadOne(axis, master_value)
                if not res:
                    raise Exception("%s.PreLoadOne(%d) returns False" % (pool_ctrl.name, axis,))
                ctrl.LoadOne(axis, master_value)
                ctrl.LoadAll()

            # PreStartAll on all controllers
            for pool_ctrl in pool_ctrls:
                pool_ctrl.ctrl.PreStartAll()

            # PreStartOne & StartOne on all elements
            for pool_ctrl in pool_ctrls:
                ctrl = pool_ctrl.ctrl
                pool_ctrl_data = pool_ctrls_dict[pool_ctrl]
                main_unit_data = pool_ctrl_data['units']['0']
                elements = main_unit_data['channels']
                for element in elements:
                    axis = element.axis
                    channel = channels[element]
                    if channel.enabled:
                        ret = ctrl.PreStartOne(axis, master_value)
                        if not ret:
                            raise Exception("%s.PreStartOne(%d) returns False" \
                                            % (pool_ctrl.name, axis))
                        ctrl.StartOne(axis, master_value)

            # set the state of all elements to  and inform their listeners
            for channel in channels:
                channel.set_state(State.Moving, propagate=2)

            # StartAll on all controllers
            for pool_ctrl in pool_ctrls:
                pool_ctrl.ctrl.StartAll()

    def in_acquisition(self, states):
        """Determines if we are in acquisition or if the acquisition has ended
        based on the current unit trigger modes and states returned by the
        controller(s)

        :param states: a map containing state information as returned by
                       read_state_info
        :type states: dict<PoolElement, State>
        :return: returns True if in acquisition or False otherwise
        :rtype: bool"""
        for elem in states:
            s = states[elem][0][0]
            if self._is_in_action(s):
                return True

    def action_loop(self):
        i = 0

        states, values = {}, {}
        for element in self._channels:
            states[element] = None
            #values[element] = None

        nap = self._acq_sleep_time
        nb_states_per_value = self._nb_states_per_value

        # read values to send a first event when starting to acquire
        with ActionContext(self):
            self.raw_read_value_loop(ret=values)
            for acquirable, value in values.items():
                acquirable.put_value(value, propagate=2)
        
        while True:
            self.read_state_info(ret=states)

            if not self.in_acquisition(states):
                break

            # read value every n times
            if not i % nb_states_per_value:
                self.read_value_loop(ret=values)
                for acquirable, value in values.items():
                    acquirable.put_value(value)
                    
            time.sleep(nap)
            i += 1

        for slave in self._slaves:
            try:
                slave.stop_action()
            except:
                self.warning("Unable to stop slave acquisition %s",
                             slave.getLogName())
                self.debug("Details", exc_info=1)

        with ActionContext(self):
            self.raw_read_state_info(ret=states)
            self.raw_read_value_loop(ret=values)

        for acquirable, state_info in states.items():
            # first update the element state so that value calculation
            # that is done after takes the updated state into account
            acquirable.set_state_info(state_info, propagate=0)
            if acquirable in values:
                value = values[acquirable]
                acquirable.put_value(value, propagate=2)
            with acquirable:
                acquirable.clear_operation()
                state_info = acquirable._from_ctrl_state_info(state_info)
                acquirable.set_state_info(state_info, propagate=2)


class Pool0DAcquisition(PoolAction):

    def __init__(self, main_element, name="0DAcquisition"):
        self._channels = None
        PoolAction.__init__(self, main_element, name)

    def start_action(self, *args, **kwargs):
        """Prepares everything for acquisition and starts it.

           :param: config"""

        pool = self.pool

        # prepare data structures
        self._aborted = False
        self._stopped = False

        self._acq_sleep_time = kwargs.pop("acq_sleep_time",
                                          pool.acq_loop_sleep_time)
        self._nb_states_per_value = \
            kwargs.pop("nb_states_per_value",
                       pool.acq_loop_states_per_value)

        integ_time = kwargs.get("integ_time")
        mon_count = kwargs.get("monitor_count")
        if integ_time is None and mon_count is None:
            raise Exception("must give integration time or monitor counts")
        if integ_time is not None and mon_count is not None:
            raise Exception("must give either integration time or monitor counts (not both)")

        items = kwargs.get("items")
        if items is None:
            items = self.get_elements()
        cfg = kwargs['config']

        pool_ctrls_dict = dict(cfg['controllers'])
        pool_ctrls_dict.pop('__tango__', None)
        pool_ctrls = []
        for ctrl in pool_ctrls_dict:
            if ElementType.ZeroDExpChannel in ctrl.get_ctrl_types():
                pool_ctrls.append(ctrl)

        # Determine which channels are active
        self._channels = channels = {}
        for pool_ctrl in pool_ctrls:
            ctrl = pool_ctrl.ctrl
            pool_ctrl_data = pool_ctrls_dict[pool_ctrl]
            main_unit_data = pool_ctrl_data['units']['0']
            elements = main_unit_data['channels']

            for element, element_info in elements.items():
                channel = Channel(element, info=element_info)
                channels[element] = channel

        with ActionContext(self):
            # set the state of all elements to  and inform their listeners
            for channel in channels:
                channel.clear_buffer()
                channel.set_state(State.Moving, propagate=2)

    def in_acquisition(self, states):
        """Determines if we are in acquisition or if the acquisition has ended
        based on the current unit trigger modes and states returned by the
        controller(s)

        :param states: a map containing state information as returned by
                       read_state_info
        :type states: dict<PoolElement, State>
        :return: returns True if in acquisition or False otherwise
        :rtype: bool"""
        for state in states:
            s = states[state][0]
            if self._is_in_action(s):
                return True

    def action_loop(self):
        i = 0

        states, values = {}, {}
        for element in self._channels:
            states[element] = None
            values[element] = None

        nap = self._acq_sleep_time
        while not (self._stopped or self._aborted):
            self.read_value(ret=values)
            for acquirable, value in values.items():
                acquirable.put_value(value)

            i += 1
            time.sleep(nap)

        with ActionContext(self):
            self.raw_read_state_info(ret=states)

        for acquirable, state_info in states.items():
            # first update the element state so that value calculation
            # that is done after takes the updated state into account
            state_info = acquirable._from_ctrl_state_info(state_info)
            acquirable.set_state_info(state_info, propagate=0)
            with acquirable:
                acquirable.clear_operation()
                acquirable.set_state_info(state_info, propagate=2)

    def stop_action(self, *args, **kwargs):
        """Stop procedure for this action."""
        self._stopped = True

    def abort_action(self, *args, **kwargs):
        """Aborts procedure for this action"""
        self._aborted = True


class PoolIORAcquisition(PoolAction):

    def __init__(self, pool, name="IORAcquisition"):
        self._channels = None
        PoolAction.__init__(self, pool, name)

    def start_action(self, *args, **kwargs):
        pass

    def in_acquisition(self, states):
        return True
        pass

    @DebugIt()
    def action_loop(self):
        i = 0

        states, values = {}, {}
        for element in self._channels:
            states[element] = None
            values[element] = None

        # read values to send a first event when starting to acquire
        self.read_value(ret=values)
        for acquirable, value in values.items():
            acquirable.put_value(value, propagate=2)

        while True:
            self.read_state_info(ret=states)

            if not self.in_acquisition(states):
                break

            # read value every n times
            if not i % 5:
                self.read_value(ret=values)
                for acquirable, value in values.items():
                    acquirable.put_value(value)

            i += 1
            time.sleep(0.01)

        self.read_state_info(ret=states)

        # first update the element state so that value calculation
        # that is done after takes the updated state into account
        for acquirable, state_info in states.items():
            acquirable.set_state_info(state_info, propagate=0)

        # Do NOT send events before we exit the OperationContext, otherwise
        # we may be asked to start another action before we leave the context
        # of the current action. Instead, send the events in the finish hook
        # which is executed outside the OperationContext

        def finish_hook(*args, **kwargs):
            # read values and propagate the change to all listeners
            self.read_value(ret=values)
            for acquirable, value in values.items():
                acquirable.put_value(value, propagate=2)

            # finally set the state and propagate to all listeners
            for acquirable, state_info in states.items():
                acquirable.set_state_info(state_info, propagate=2)

        self.set_finish_hook(finish_hook)
