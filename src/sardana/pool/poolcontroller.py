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

__all__ = [ "PoolController", "PoolPseudoMotorController" ]

__docformat__ = 'restructuredtext'

import sys
import weakref
import StringIO
import traceback
from taurus.core.util import CaselessDict

from poolbase import *
from pooldefs import *

class PoolController(PoolObject):
    
    def __init__(self, **kwargs):
        self._lib_info = kwargs.pop('lib_info')
        self._ctrl_info = kwargs.pop('class_info')
        self._lib_name = kwargs.pop('library')
        self._class_name = kwargs.pop('klass')
        self._properties = kwargs.pop('properties')
        self._ctrl = None
        self._ctrl_error = None
        self._element_ids = {}
        self._pending_element_ids = {}
        self._element_axis = {}
        self._pending_element_axis = {}
        self._element_names = CaselessDict()
        self._pending_element_names = CaselessDict()
        super(PoolController, self).__init__(**kwargs)
        
        self.init()
    
    def init(self):
        if self._ctrl_info is None:
            if self._lib_info is not None:
                self._ctrl_error = self._lib_info.getError()
            return
        try:
            klass = self._ctrl_info.getControllerClass()
            props = dict(self._properties)
            props["__pool_controller"] = self
            self._ctrl = klass(self.get_name(), self._properties)
        except:
            self._ctrl_error = sys.exc_info()
    
    def reInit(self):
        self.info("reInit")
        manager = self.pool.ctrl_manager
        old_e_ids = self._element_ids
        old_p_e_ids = self._pending_element_ids
        
        elem_axis = dict(self._element_axis)
        for axis in elem_axis.keys():
            self.remove_axis(axis)
        
        mod_name = self._lib_info.name
        class_name = self._ctrl_info.name
        
        self._ctrl_info = None
        self._lib_info = manager.getControllerLib(mod_name)
        if self._lib_info is not None:
            self._ctrl_info = self._lib_info.getController(class_name)
        
        self.init()
        
        for elem in elem_axis.values():
            self.add_element(elem)
    
    def get_type(self):
        return ElementType.Ctrl

    def get_ctrl_types(self):
        return self._ctrl_info.getTypes()

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
    
    def is_online(self):
        return self._ctrl_error is None and self._ctrl is not None
    
    def get_ctrl(self):
        return self._ctrl
    
    ctrl = property(fget=get_ctrl, doc="actual controller object")
    
    def get_ctrl_info(self):
        return self._ctrl_info
    
    ctrl_info = property(fget=get_ctrl_info, doc="controller information object")
    
    def set_log_level(self, level):
        self.ctrl._log.log_obj.setLevel(level)
    
    def get_log_level(self):
        return self.ctrl._log.log_obj.level
    
    def add_element(self, elem):
        name, axis, id = elem.get_name(), elem.get_axis(), elem.get_id()
        if not self.is_online():
            #TODO: raise exception
            self._pending_element_ids[id] = elem
            self._pending_element_axis[axis] = elem
            self._pending_element_names[name] = elem
        else:
            self._ctrl.AddDevice(axis)
            self._element_ids[id] = elem
            self._element_axis[axis] = elem
            self._element_names[name] = elem
        self.fire_event("ElementCreated", elem)
        
    def remove_element(self, elem):
        id = elem.id
        f = self._element_ids.has_key(id)
        if not f:
            f = self._pending_element_ids.has_key(id)
            if not f:
                raise Exception("element '%s' is not in controller")
            del self._pending_element_ids[id]
            del self._pending_element_axis[elem.get_axis()]
            del self._pending_element_names[elem.get_name()]
        else:
            del self._element_ids[id]
            del self._element_axis[elem.get_axis()]
            del self._element_names[elem.get_name()]
            self._ctrl.DeleteDevice(elem.get_axis())
        self.fire_event("ElementDeleted", elem)
    
    def remove_axis(self, axis):
        f = self._element_axis.has_key(axis)
        if not f:
            f = self._pending_element_axis.has_key(axis)
            if not f:
                raise Exception("element '%s' is not in controller")
            elem = self._pending_element_axis[axis]
        else:
            elem = self._element_axis[axis]
        self.remove_element(elem)
    
    def get_library_name(self):
        return self._lib_name
    
    def get_class_name(self):
        return self._class_name

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

    def get_standard_axis_attributes(self, axis):
        return self.ctrl.getStandardAxisAttributes(axis)

    def get_ctrl_attr(self, name):
        ctrl_info = self.ctrl_info
        attr_info = ctrl_info.getControllerAttributes()[name]
        fget = getattr(self.ctrl, attr_info.fget)
        return fget()

    def set_ctrl_attr(self, name, value):
        ctrl_info = self.ctrl_info
        attr_info = ctrl_info.getControllerAttributes()[name]
        fset = getattr(self.ctrl, attr_info.fset)
        fset(value)

    def get_axis_attr(self, axis, name):
        ctrl_info = self.ctrl_info
        axis_attr_info = ctrl_info.getAxisAttributes()[name]
        if hasattr(self.ctrl, axis_attr_info.fget):
            ret = getattr(self.ctrl, axis_attr_info.fget)(axis)
        else:
            ret = self.ctrl.GetExtraPar(axis, name)
        return ret
    
    def set_axis_attr(self, axis, name, value):
        ctrl_info = self.ctrl_info
        axis_attr_info = ctrl_info.getAxisAttributes()[name]
        try:
            return getattr(self.ctrl, axis_attr_info.fset)(axis, value)
        except AttributeError:
            return self.ctrl.SetExtraPar(axis, name, value)

    
    # START SPECIFIC TO MOTOR CONTROLLER ---------------------------------------
    
    def has_backlash(self):
        return "Backlash" in self._ctrl.ctrl_features
    
    def wants_rounding(self):
        return "Rounding" in self._ctrl.ctrl_features
        
    # END SPECIFIC TO MOTOR CONTROLLER -----------------------------------------


class PoolPseudoMotorController(PoolController):
    
    def __init__(self, **kwargs):
        motor_ids = kwargs.pop('motor_ids')
        pseudo_motor_ids = kwargs.pop('pseudo_motor_ids')
        super(PoolPseudoMotorController, self).__init__(**kwargs)
        
    
    