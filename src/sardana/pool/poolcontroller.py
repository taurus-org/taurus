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

__all__ = ["PoolController", "PoolPseudoMotorController",
           "PoolPseudoCounterController"]

__docformat__ = 'restructuredtext'

import sys
import weakref
import StringIO
import traceback
import functools
import threading
import numbers

from taurus.core.util import CaselessDict
from taurus.core.util import InfoIt

from sardana import State, ElementType, InvalidAxis, InvalidId, is_number
from sardana.sardanaevent import EventType

from poolelement import PoolBaseElement


class PoolBaseController(PoolBaseElement):
    """Base class for all controllers"""
    def __init__(self, **kwargs):
        self._ctrl = None
        self._ctrl_error = None
        self._element_ids = {}
        self._pending_element_ids = {}
        self._element_axis = {}
        self._pending_element_axis = {}
        self._element_names = CaselessDict()
        self._pending_element_names = CaselessDict()
        self._operator = None
        super(PoolBaseController, self).__init__(**kwargs)
    
    def get_ctrl_types(self):
        raise NotImplementedError
    
    def get_ctrl_type_names(self):
        return map(ElementType.whatis, self.get_ctrl_types())
        
    def get_type(self):
        return ElementType.Controller
    
    def is_online(self):
        return True
    
    def get_ctrl_error(self):
        return self._ctrl_error
    
    def get_ctrl_error_str(self):
        """"""
        err = self._ctrl_error
        if err is None:
            return ""
        sio = StringIO.StringIO()
        traceback.print_exception(err[0], err[1], err[2], None, sio)
        s = sio.getvalue()
        sio.close()
        if s[-1:] == "\n":
            s = s[:-1]
        return s
    
    def add_element(self, elem, propagate=1):
        name, axis, id = elem.get_name(), elem.get_axis(), elem.get_id()
        if self.is_online():
            try:
                self._ctrl.AddDevice(axis)
            except:
                self.error("Unable to add %s(%s)", name, axis, exc_info=1)
                self._pending_element_ids[id] = elem
                self._pending_element_axis[axis] = elem
                self._pending_element_names[name] = elem
            self._element_ids[id] = elem
            self._element_axis[axis] = elem
            self._element_names[name] = elem
        else:
            #TODO: raise exception
            self._pending_element_ids[id] = elem
            self._pending_element_axis[axis] = elem
            self._pending_element_names[name] = elem
        if propagate:
            elements = self.get_elements()
            elements = [ elements[id].name for id in sorted(elements) ]
            self.fire_event(EventType("elementlist", priority=propagate),
                            elements)
    
    def remove_element(self, elem, propagate=1):
        name, axis, id = elem.get_name(), elem.get_axis(), elem.get_id()
        f = self._element_ids.has_key(id)
        if not f:
            f = self._pending_element_ids.has_key(id)
            if not f:
                raise Exception("element '%s' is not in controller")
            del self._pending_element_ids[id]
            del self._pending_element_axis[axis]
            del self._pending_element_names[name]
        else:
            del self._element_ids[id]
            del self._element_axis[axis]
            del self._element_names[name]
            try:
                self._ctrl.DeleteDevice(axis)
            except:
                self.error("Unable to delete %s(%s)", name, axis, exc_info=1)
        if propagate:
            elements = self.get_elements()
            elements = [ elements[id].name for id in sorted(elements) ]
            self.fire_event(EventType("elementlist", priority=propagate),
                            elements)

    def remove_axis(self, axis, propagate=1):
        f = self._element_axis.has_key(axis)
        if not f:
            f = self._pending_element_axis.has_key(axis)
            if not f:
                raise Exception("element '%s' is not in controller")
            elem = self._pending_element_axis[axis]
        else:
            elem = self._element_axis[axis]
        self.remove_element(elem, propagate=propagate)
        
    def get_elements(self):
        return self._element_ids
    
    def get_element_ids(self):
        return self._element_ids
    
    def get_element_axis(self):
        return self._element_axis
    
    def get_element(self, **kwargs):
        k = kwargs.get('axis')
        if k is None:
            k = kwargs.get('name')
            if k is None:
                k = kwargs.get('id')
                if k is None:
                    raise Exception("Must give either name, id or axis")
                d, pd = self._element_ids, self._pending_element_ids
            else:
                d, pd = self._element_names, self._pending_element_names
        else:
            d, pd = self._element_axis, self._pending_element_axis
        
        elem = d.get(k)
        if elem is None:
            elem = pd.get(k)
        return elem

    def read_axis_states(self, axises=None):
        """Reads the state for the given axises. If axises is None, reads the
        state of all active axises.
        
        :param axises: the list of axis to get the state. Default is None meaning
                       all active axis in this controller
        :type axises: seq<int> or None
        :return: a map containing the controller state information for each axis
        :rtype: dict<PoolElement, state info>
        """
        raise NotImplementedError
    
    def read_axis_values(self, axises=None):
        """Reads the value for the given axises. If axises is None, reads the
        value of all active axises.
        
        :param axises: the list of axis to get the value. Default is None meaning
                       all active axis in this controller
        :type axises: seq<int> or None
        :return: a map containing the controller value information for each axis
        :rtype: dict<PoolElement, value>
        """
        raise NotImplementedError


def check_ctrl(fn):
    @functools.wraps(fn)
    def wrapper(pool_ctrl, *args, **kwargs):
        if not pool_ctrl.is_online():
            raise Exception("Cannot execute '%s' because '%s' is offline" % \
                            (fn.__name__, pool_ctrl.name))
        return fn(pool_ctrl, *args, **kwargs)
    return wrapper

def ctrl_access(fn):
    @functools.wraps(fn)
    def wrapper(pool_ctrl, *args, **kwargs):
        with pool_ctrl:
            return fn(pool_ctrl, *args, **kwargs)
    return wrapper


class PoolController(PoolBaseController):
    """Controller class mediator for sardana controller plugins"""
    
    def __init__(self, **kwargs):
        self._lib_info = kwargs.pop('lib_info')
        self._ctrl_info = kwargs.pop('class_info')
        self._lib_name = kwargs.pop('library')
        self._class_name = kwargs.pop('klass')
        self._properties = kwargs.pop('properties')
        super(PoolController, self).__init__(**kwargs)
        self.re_init()

    def serialize(self, *args, **kwargs):
        kwargs = PoolBaseController.serialize(self, *args, **kwargs)
        ctrl_info = self._ctrl_info
        if ctrl_info is None:
            kwargs['module'] = self._lib_name
            kwargs['klass'] = self._class_name
            kwargs['language'] = 'Python'
            kwargs['file_name'] = None
            kwargs['types'] = None
            kwargs['main_type'] = None
            kwargs['parent'] = self._class_name
        else:
            types = self.get_ctrl_type_names()
            kwargs['module'] = ctrl_info.module_name
            kwargs['klass'] = ctrl_info.name
            kwargs['language'] = 'Python'
            kwargs['file_name'] = ctrl_info.file_name
            kwargs['types'] = types
            kwargs['parent'] = ctrl_info.name
            if len(types):
                kwargs['main_type'] = types[0]
            else:
                kwargs['main_type'] = None
        return kwargs
    
    def _create_ctrl_args(self):
        name = self.name
        klass = self._ctrl_info.klass
        props = dict(self._properties)
        args, kwargs = [], dict(pool_controller=weakref.ref(self))
        return name, klass, props, args, kwargs
    
    def _create_controller(self):
        name, klass, props, args, kwargs = self._create_ctrl_args()
        api = self._ctrl_info.api_version
        if api == 0:
            ctrl = klass(name, props)
            ctrl._args = args
            ctrl._kwargs = kwargs
        elif api == 1:
            ctrl = klass(name, props, *args, **kwargs)
        return ctrl

    def _init(self):
        if self._ctrl_info is None:
            if self._lib_info is not None:
                self._ctrl_error = self._lib_info.get_error()
            return
        try:
            self._ctrl = self._create_controller()
        except:
            self._ctrl = None
            self._ctrl_error = sys.exc_info()
    
    def re_init(self):
        self.set_state(State.Init, propagate=2)
        status = "{0} is Initializing (temporarly unavailable)".format(self.name)
        self.set_status(status, propagate=2)
        manager = self.pool.ctrl_manager
        old_e_ids = self._element_ids
        old_p_e_ids = self._pending_element_ids
        
        elem_axis = dict(self._element_axis)
        for axis in elem_axis:
            self.remove_axis(axis, propagate=0)
        
        if self._lib_info is None:
            mod_name = self.get_library_name()
        else:
            mod_name = self._lib_info.name

        if self._ctrl_info is None:
            class_name = self.get_class_name()
        else:
            class_name = self._ctrl_info.name
        
        self._ctrl_error = None
        self._ctrl_info = None
        self._lib_info = manager.getControllerLib(mod_name)
        if self._lib_info is not None:
            self._ctrl_info = self._lib_info.get_controller(class_name)
        self._init()
        
        for elem in elem_axis.values():
            self.add_element(elem, propagate=0)
    
        state, status = State.Fault, ""
        if self.is_online():
            state = State.On
        else:
            status = "\n" + self.get_ctrl_error_str()
        
        status = "{0} is {1}".format(self.name, State[state]) + status
        self.set_status(status, propagate=2)
        self.set_state(state, propagate=2)

    def get_ctrl_types(self):
        return self._ctrl_info.types

    def is_online(self):
        return self._ctrl_error is None and self._ctrl is not None
    
    def get_ctrl(self):
        return self._ctrl
    
    ctrl = property(fget=get_ctrl, doc="actual controller object")
    
    def get_ctrl_info(self):
        return self._ctrl_info
    
    ctrl_info = property(fget=get_ctrl_info, doc="controller information object")
    
    def set_operator(self, operator):
        """Defines the current operator object for this controller.
           For example, in acquisition, it should be a :class:`PoolMeasurementGroup`
           object.
           
           :param operator: the new operator object
           :type operator: object"""
        self._operator = operator
    
    def get_operator(self):
        return self._operator
    
    operator = property(fget=get_operator, fset=set_operator, doc="current controller operator")
    
    # START API WHICH ACCESSES CONTROLLER API ----------------------------------
    
    @check_ctrl
    def set_log_level(self, level):
        self.ctrl._log.log_obj.setLevel(level)
    
    @check_ctrl
    def get_log_level(self):
        return self.ctrl._log.log_obj.level
    
    def get_library_name(self):
        return self._lib_name
    
    def get_class_name(self):
        return self._class_name
    
    @check_ctrl
    def get_axis_attributes(self, axis):
        return self.ctrl.GetAxisAttributes(axis)
    
    @check_ctrl
    def get_ctrl_attr(self, name):
        ctrl_info = self.ctrl_info
        attr_info = ctrl_info.ctrl_attributes[name]
        fget = getattr(self.ctrl, attr_info.fget)
        return fget()
    
    @check_ctrl
    def set_ctrl_attr(self, name, value):
        ctrl_info = self.ctrl_info
        attr_info = ctrl_info.ctrl_attributes[name]
        fset = getattr(self.ctrl, attr_info.fset)
        fset(value)
    
    @check_ctrl
    def get_axis_attr(self, axis, name):
        ctrl_info = self.ctrl_info
        axis_attr_info = ctrl_info.axis_attributes[name]
        if hasattr(self.ctrl, axis_attr_info.fget):
            ret = getattr(self.ctrl, axis_attr_info.fget)(axis)
        else:
            ret = self.ctrl.GetAxisExtraPar(axis, name)
        return ret
    
    @check_ctrl
    def set_axis_attr(self, axis, name, value):
        ctrl_info = self.ctrl_info
        axis_attr_info = ctrl_info.axis_attributes[name]
        try:
            return getattr(self.ctrl, axis_attr_info.fset)(axis, value)
        except AttributeError:
            return self.ctrl.SetAxisExtraPar(axis, name, value)
    
    @check_ctrl
    def set_ctrl_par(self, name, value):
        #return self.ctrl.setCtrlPar(unit, name, value)
        return self.ctrl.SetCtrlPar(name, value)
    
    @check_ctrl
    def get_ctrl_par(self, name):
        #return self.ctrl.getCtrlPar(unit, name, value)
        return self.ctrl.GetCtrlPar(name)
    
    @check_ctrl
    def set_axis_par(self, axis, name, value):
        #return self.ctrl.SetAxisPar(unit, axis, name, value)
        return self.ctrl.SetAxisPar(axis, name, value)
    
    @check_ctrl
    def get_axis_par(self, axis, name):
        #return self.ctrl.GetAxisPar(unit, axis, name, value)
        return self.ctrl.GetAxisPar(axis, name)

    # END API WHICH ACCESSES CONTROLLER API ------------------------------------
    
    # START API WHICH ACCESSES CRITICAL CONTROLLER API (like StateOne) ---------

    def __build_exc_info(self, ctrl_states, axises, exc_info):
        status = s = "".join(traceback.format_exception(*exc_info))
        state_info = State.Fault, status
        for axis in axises:
            element = self.get_element(axis=axis)
            ctrl_states[element] = state_info
    
    @staticmethod
    def _format_exception(exc_info):
        fmt_exc = traceback.format_exception_only(*exc_info[:2])
        fmt_exc = "".join(fmt_exc)
        if fmt_exc.endswith("\n"):
            fmt_exc = fmt_exc[:-1]
        return fmt_exc
    
    def raw_read_axis_states(self, axises=None, ctrl_states=None):
        """**Unsafe method**. Reads the state for the given axises. If axises
        is None, reads the state of all active axises.
        
        :param axises: the list of axis to get the state. Default is None meaning
                       all active axis in this controller
        :type axises: seq<int> or None
        :return:
            a tuple of two elements: a map containing the controller state
            information for each axis and a boolean telling if an error occured
        :rtype: dict<PoolElement, state info>, bool"""
        if axises is None:
            axises = self._element_axis.keys()
        if ctrl_states is None:
            ctrl_states = {}
        
        ctrl = self.ctrl
        
        try:
            ctrl.PreStateAll()
            for axis in axises:
                ctrl.PreStateOne(axis)
            ctrl.StateAll()
        except:
            exc_info = sys.exc_info()
            status = self._format_exception(exc_info)
            state_info = (State.Fault, status), exc_info
            for axis in axises:
                element = self.get_element(axis=axis)
                ctrl_states[element] = state_info
            return ctrl_states, True
        
        error = False
        for axis in axises:
            element = self.get_element(axis=axis)
            try:
                state_info = ctrl.StateOne(axis)
                if state_info is None:
                    raise Exception("%s.StateOne(%s(%d)) returns 'None'"
                                    % (self.name, element.name, axis))
                state_info = state_info, None
            except:
                exc_info = sys.exc_info()
                status = self._format_exception(exc_info)
                state_info = (State.Fault, status), exc_info
                error = True
            ctrl_states[element] = state_info
        return ctrl_states, error
    
    @check_ctrl
    def read_axis_states(self, axises=None):
        """Reads the state for the given axises. If axises is None, reads the
        state of all active axises.
        
        :param axises: the list of axis to get the state. Default is None
                       meaning all active axis in this controller
        :type axises: seq<int> or None
        :return: a map containing the controller state information for each axis
        :rtype: dict<PoolElement, state info>"""
        return self.raw_read_axis_states(axises=axises)
    
    def raw_read_axis_values(self, axises=None, ctrl_values=None):
        """**Unsafe method**. Reads the value for the given axises. If axises
        is None, reads the value of all active axises.
        
        :param axises: the list of axis to get the value. Default is None
                       meaning all active axis in this controller
        :type axises: seq<int> or None
        :return: a map containing the controller value information for each axis
        :rtype: dict<PoolElement, value>"""
        if axises is None:
            axises = self._element_axis.keys()
        if ctrl_values is None:
            ctrl_values = {}
        
        ctrl = self.ctrl
        
        try:
            ctrl.PreReadAll()
            for axis in axises:
                ctrl.PreReadOne(axis)
            ctrl.ReadAll()
        except:
            exc_info = sys.exc_info()
            for axis in axises:
                element = self.get_element(axis=axis)
                ctrl_values[element] = None, exc_info
            return ctrl_values
            
        for axis in axises:
            element = self.get_element(axis=axis)
            try:
                value = ctrl.ReadOne(axis)
                if not is_number(value):
                    t = type(value)
                    if value is None:
                        t = 'None'
                    msg = '%s.ReadOne(%s[%d]) return error: Expected number, ' \
                          'got %s instead' % (self.name, element.name, axis,
                                              str(t))
                    raise ValueError(msg)
                ctrl_values[element] = value, None
            except:
                ctrl_values[element] = None, sys.exc_info()
        
        return ctrl_values

    @check_ctrl
    def read_axis_values(self, axises=None):
        """Reads the value for the given axises. If axises is None, reads the
        value of all active axises.
        
        :param axises: the list of axis to get the value. Default is None meaning
                       all active axis in this controller
        :type axises: seq<int> or None
        :return: a map containing the controller value information for each axis
        :rtype: dict<PoolElement, value>"""
        return self.raw_read_axis_values(axises=axises)
    
    def raw_stop_all(self):
        try:
            return self._raw_stop_all()
        except:
            pass
    
    def raw_stop_one(self, axis):
        try:
            self._raw_stop_one(axis)
        except:
            pass
    
    def _raw_stop_all(self):
        try:
            return self.ctrl.StopAll()
        except:
            self.warning("StopAll() raises exception")
            self.debug("Details:", exc_info=1)
            raise
    
    def _raw_stop_one(self, axis):
        try:
            self.ctrl.StopOne(axis)
        except:
            self.warning("StopOne(%d) raises exception", axis)
            self.debug("Details:", exc_info=1)
            raise
    
    @check_ctrl
    def stop_all(self):
        self.raw_stop_all()
    
    stop = stop_all
    
    @check_ctrl
    def stop_one(self, axis):
        return self.raw_stop_one(axis)
    
    @check_ctrl
    def stop_axises(self, axises=None):
        """Stops the given axises. If axises is None, stops all active axises.
        
        :param axises: the list of axis to stop. Default is None
                       meaning all active axis in this controller
        :type axises: seq<int> or None
        """
        if axises is None:
            return self.raw_stop_all()
        
        for axis in axises:
            self.raw_stop_one(axis)
    
    @check_ctrl
    def stop_elements(self, elements=None):
        """Stops the given elements. If axises is None, stops all active axises.
        
        :param elements: the list of elements to stop. Default is None
                         meaning all active axis in this controller
        :type axises: seq<PoolElement> or None
        """
        if elements is None:
            return self.raw_stop_all()
        
        for element in elements:
            self.raw_stop_one(element.axis)
    
    def raw_abort_all(self):
        try:
            return self._raw_abort_all()
        except:
            pass
    
    def raw_abort_one(self, axis):
        try:
            self._raw_abort_one(axis)
        except:
            pass
    
    def _raw_abort_all(self):
        try:
            return self.ctrl.AbortAll()
        except:
            self.warning("AbortAll() raises exception")
            self.debug("Details:", exc_info=1)
            raise
    
    def _raw_abort_one(self, axis):
        try:
            self.ctrl.AbortOne(axis)
        except:
            self.warning("AbortOne(%d) raises exception", axis)
            self.debug("Details:", exc_info=1)
            raise

    @check_ctrl
    def abort_all(self):
        self.raw_abort_all()

    @check_ctrl
    def abort_one(self, axis):
        return self.raw_abort_one(axis)
    
    @check_ctrl
    def abort_axises(self, axises=None):
        """Aborts the given axises. If axises is None, aborts all active axises.
        
        :param axises: the list of axis to abort. Default is None
                       meaning all active axis in this controller
        :type axises: seq<int> or None
        """
        if axises is None:
            return self.raw_abort_all()
        
        for axis in axises:
            self.raw_abort_one(axis)
    
    @check_ctrl
    def abort_elements(self, elements=None):
        """Aborts the given elements. If axises is None, aborts all active axises.
        
        :param elements: the list of elements to abort. Default is None
                         meaning all active axis in this controller
        :type axises: seq<PoolElement> or None
        """
        if elements is None:
            return self.raw_abort_all()
        
        for element in elements:
            self.raw_abort_one(element.axis)
    
    abort = abort_all
    
    @check_ctrl
    def emergency_break(self, elements=None):
        """Stops the given elements. If axises is None, stops all active axises.
        If stop raises exception, an abort is attempted.
        
        :param elements: the list of elements to stop. Default is None
                         meaning all active axis in this controller
        :type axises: seq<PoolElement> or None
        """
        if elements is None:
            try:
                return self._raw_stop_all()
            except:
                return self.raw_abort_all()
        
        for element in elements:
            try:
                self._raw_stop_one(element.axis)
            except:
                self.raw_abort_one(element.axis)
    
    @check_ctrl
    def send_to_controller(self, stream):
        return self.ctrl.SendToCtrl(stream)
    
    # END API WHICH ACCESSES CRITICAL CONTROLLER API (like StateOne) -----------
    
    # START SPECIFIC TO MOTOR CONTROLLER ---------------------------------------
    
    def raw_move(self, axis_pos):
        ctrl = self.ctrl
        ctrl.PreStartAll()
        for axis, dial_position in axis_pos.items():
            ret = ctrl.PreStartOne(axis, dial_position)
            if not ret:
                raise Exception("%s.PreStartOne(%d, %f) returns False" \
                                % (self.name, axis, dial_position))
        
        for axis, dial_position in axis_pos.items():
            ctrl.StartOne(axis, dial_position)
        
        ctrl.StartAll()

    @check_ctrl
    def move(self, axis_pos):
        return self.raw_move(axis_pos)
    
    def has_backlash(self):
        return "Backlash" in self._ctrl.ctrl_features
    
    def wants_rounding(self):
        return "Rounding" in self._ctrl.ctrl_features

    @check_ctrl
    def define_position(self, axis, position):
        return self.ctrl.DefinePosition(axis, position)
        
    # END SPECIFIC TO MOTOR CONTROLLER -----------------------------------------
    # START SPECIFIC TO IOR CONTROLLER -------------

    def write_one(self, axis, value):
        self.ctrl.WriteOne(axis, value)

    # END SPECIFIC TO IOR CONTROLLER ----------


class PoolPseudoMotorController(PoolController):
    
    def __init__(self, **kwargs):
        self._motor_ids = kwargs.pop('role_ids')
        super(PoolPseudoMotorController, self).__init__(**kwargs)
    
    def serialize(self, *args, **kwargs):
        kwargs = PoolController.serialize(self, *args, **kwargs)
        kwargs['type'] = 'Controller'
        return kwargs
        
    def _create_ctrl_args(self):
        pars = PoolController._create_ctrl_args(self)
        name, klass, props, args, kwargs = pars
        kwargs['motor_ids'] = tuple(self._motor_ids)
        return pars
    
    @check_ctrl
    def calc_all_pseudo(self, physical_pos, curr_pseudo_pos):
        ctrl = self.ctrl
        try:
            return ctrl.CalcAllPseudo(physical_pos, curr_pseudo_pos), None
        except:
            return None, sys.exc_info()

    @check_ctrl
    def calc_all_physical(self, pseudo_pos, curr_physical_pos):
        ctrl = self.ctrl
        try:
            return ctrl.CalcAllPhysical(pseudo_pos, curr_physical_pos), None
        except:
            return None, sys.exc_info()

    @check_ctrl
    def calc_pseudo(self, axis, physical_pos, curr_pseudo_pos):
        ctrl = self.ctrl
        try:
            return ctrl.CalcPseudo(axis, physical_pos, curr_pseudo_pos), None
        except:
            return None, sys.exc_info()

    @check_ctrl
    def calc_physical(self, axis, pseudo_pos, curr_physical_pos):
        ctrl = self.ctrl
        try:
            return ctrl.CalcPhysical(axis, pseudo_pos, curr_physical_pos), None
        except:
            return None, sys.exc_info()


class PoolPseudoCounterController(PoolController):
    
    def __init__(self, **kwargs):
        self._motor_ids = kwargs.pop('role_ids')
        super(PoolPseudoCounterController, self).__init__(**kwargs)
    
    def serialize(self, *args, **kwargs):
        kwargs = PoolController.serialize(self, *args, **kwargs)
        kwargs['type'] = 'Controller'
        return kwargs
        
    def _create_ctrl_args(self):
        pars = PoolController._create_ctrl_args(self)
        name, klass, props, args, kwargs = pars
        kwargs['motor_ids'] = tuple(self._motor_ids)
        return pars
    
    @check_ctrl
    def calc(self, axis, values):
        ctrl = self.ctrl
        try:
            return ctrl.Calc(axis, values), None
        except:
            return None, sys.exc_info()

