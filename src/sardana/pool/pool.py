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

"""This file contains the main pool class"""

__all__ = ["PoolContainer", "Pool", "ThreadPool"]

__docformat__ = 'restructuredtext'

import os.path
import logging.handlers

import taurus.core.util

from poolcontrollermanager import ControllerManager, TYPE_MAP_OBJ

from poolbase import *
from pooldefs import *
from poolelement import *
from poolcontroller import *
from poolmotor import *
from poolmonitor import *

__thread_pool = None

def ThreadPool():
    global __thread_pool
    if __thread_pool is None:
        __thread_pool = taurus.core.util.ThreadPool()
    return __thread_pool

class PoolContainer(object):
    
    def __init__(self):
        
        # map of all elements
        # key - element ID
        # value - pointer to the element object
        self._element_ids = {}

        # map of all elements by name
        # key - element name
        # value - pointer to the element object
        self._element_names = taurus.core.util.CaselessDict()

        # map of all elements by name
        # key - element full name
        # value - pointer to the element object
        self._element_full_names = taurus.core.util.CaselessDict()
    
        # map of all elements by type
        # key - element type
        # value - map where:
        #    key - element ID
        #    value - pointer to the element object
        self._element_types = {}
        
        ControllerManager().reInit()

    def add_element(self, e):
        """Adds a new :class:`pool.PoolObject` to this container
           
           :param e: the pool element to be added
           :type e: :class:`pool.PoolObject`
        """
        name, full_name, id = e.get_name(), e.get_full_name(), e.get_id()
        elem_type = e.get_type()
        self._element_ids[id] = e
        self._element_names[name] = e
        self._element_full_names[full_name] = e
        type_elems = self._element_types.get(elem_type)
        if type_elems is None:
            self._element_types[elem_type] = type_elems = {}
        type_elems[id] = e
        return e
    
    def remove_element(self, e):
        """Removes the :class:`pool.PoolObject` from this container
           
           :param e: the pool object to be removed
           :type e: :class:`pool.PoolObject`
           
           :throw: KeyError
        """
        name, full_name, id = e.get_name(), e.get_full_name(), e.get_id()
        elem_type = e.get_type()
        del self._element_ids[id]
        del self._element_names[name]
        del self._element_full_names[full_name]
        type_elems = self._element_types.get(elem_type)
        del type_elems[id]
        
    def get_element_id_map(self):
        """Returns a reference to the internal pool object ID map
           
           :return: the internal pool object ID map
           :rtype: dict<id, pool.PoolObject>
        """
        return self._element_ids
    
    def get_element_name_map(self):
        """Returns a reference to the internal pool object name map
           
           :return: the internal pool object name map
           :rtype: dict<str, pool.PoolObject>
        """
        return self._element_names
    
    def get_element_type_map(self):
        """Returns a reference to the internal pool object type map
           
           :return: the internal pool object type map
           :rtype: dict<pool.ElementType, dict<id, pool.PoolObject>>
        """
        return self._element_types
    
    def get_element(self, **kwargs):
        """Returns a reference to the requested pool object
           
           :param kwargs: if key 'id' given: search by ID
                          else if key 'full_name' given: search by full name
                          else if key 'name' given: search by name
           
           :return: the pool object 
           :rtype: pool.PoolObject
           
           :throw: KeyError
        """
        if kwargs.has_key("id"):
            id = kwargs.pop("id")
            return self.get_element_by_id(id, **kwargs)
        
        if kwargs.has_key("full_name"):
            full_name = kwargs.pop("full_name")
            return self.get_element_by_full_name(full_name, **kwargs)
        
        name = kwargs.pop("name")
        return self.get_element_by_name(name, **kwargs)
    
    def get_element_by_name(self, name, **kwargs):
        """Returns a reference to the requested pool object
           
           :param name: pool object name
           :type name: str
           
           :return: the pool object 
           :rtype: pool.PoolObject
           
           :throw: KeyError
        """
        ret = self._element_names.get(name)
        if ret is None:
            raise Exception("There is no element with name '%s'" % name)
        return ret
    
    def get_element_by_full_name(self, full_name, **kwargs):
        """Returns a reference to the requested pool object
           
           :param name: pool object full name
           :type name: str
           
           :return: the pool object 
           :rtype: pool.PoolObject
           
           :throw: KeyError
        """
        ret = self._element_full_names[full_name]
        if ret is None: 
            raise Exception("There is no element with full name '%s'" % full_name)
        return ret
        
    def get_element_by_id(self, id, **kwargs):
        """Returns a reference to the requested pool object
           
           :param id: pool object ID
           :type id: int
           
           :return: the pool object 
           :rtype: pool.PoolObject
           
           :throw: KeyError
        """
        return self._element_ids[id]
    
    def get_elements_by_type(self, t):
        """Returns a list of all pool objects of the given type
           
           :param t: element type
           :type t: pool.ElementType
           
           :return: list of pool objects
           :rtype: seq<pool.PoolObject>
        """
        elem_types_dict = self._element_types.get(t)
        if elem_types_dict is None:
            return  []
        return elem_types_dict.values()

    def get_element_names_by_type(self, t):
        """Returns a list of all pool object names of the given type
           
           :param t: element type
           :type t: pool.ElementType
           
           :return: list of pool object names
           :rtype: seq<str>
        """
        return [ elem.get_name() for elem in self.get_elements_by_type(t) ]
        
    def rename_element(self, old_name, new_name):
        """Rename a pool object
           
           :param old_name: old pool object name
           :type old_name: str
           :param new_name: new pool object name
           :type new_name: str
        """
        raise RuntimeError("not implemented")
    
    def get_controller_class(self, **kwargs):
        id = kwargs.get("id")
        if id is not None:
            return self.get_controller_class_by_id(id, **kwargs)
        
        name = kwargs.pop("name")
        self.get_controller_class_by_name(name, **kwargs)
    
    def get_controller_class_by_id(self, id, **kwargs):
        raise RuntimeError("not implemented")
    
    def get_controller_class_by_name(self, name, **kwargs):
        raise RuntimeError("not implemented")
    

class Pool(PoolContainer, PoolObject):
    """ """
    
    def __init__(self, full_name, name=None):
        PoolContainer.__init__(self)
        PoolObject.__init__(self, full_name=full_name, name=name, id=InvalidId, pool=self)
        self._last_id = InvalidId
        self._monitor = PoolMonitor(self, "PoolMonitor")
    
    def init_remote_logging(self, host=None, port=None):
        log = logging.getLogger("Controller")
        
        # first check that the handler has not been initialized yet
        for handler in log.handlers:
            if isinstance(handler, logging.handlers.SocketHandler):
                return
        if host is None:
            import socket
            host = socket.getfqdn()
        if port is None:
            port = logging.handlers.DEFAULT_TCP_LOGGING_PORT
        handler = logging.handlers.SocketHandler(host, port)
        log.addHandler(handler)
    
    def get_type(self):
        return ElementType.Pool
        
    def get_new_id(self):
        self._last_id += 1
        return self._last_id
    
    def rollback_id(self):
        self._last_id -= 1
    
    def reserve_id(self, id):
        if id > self._last_id:
            self._last_id = id
            
    @property
    def ctrl_manager(self):
        return ControllerManager()
    
    def set_path(self, path):
        self.ctrl_manager.setControllerPath(path)
    
    def get_controller_libs(self):
        return self.ctrl_manager.getControllerLibs()
    
    def get_controller_lib_names(self):
        return self.ctrl_manager.getControllerLibNames()
    
    def get_controller_class_names(self):
        return self.ctrl_manager.getControllerNames()
    
    def get_controller_classes(self):
        return self.ctrl_manager.getControllers()
    
    def get_controller_class_info(self, name):
        return self.ctrl_manager.getControllerMetaClass(name)
    
    def get_controller_classes_info(self, names):
        return self.ctrl_manager.getControllerMetaClasses(names)
        
    def get_controller_libs_summary_info(self):
        libs = self.get_controller_libs()
        ret = []
        for module_name, ctrl_lib_info in libs.items():
            elem = "%s (%s)" % (ctrl_lib_info.getName(), ctrl_lib_info.getFileName())
            ret.append(elem)
        return ret

    def get_controller_classes_summary_info(self):
        ctrl_classes = self.get_controller_classes()
        ret = []
        for ctrl_class_info in ctrl_classes:
            types = ctrl_class_info.getTypes()
            types_str = [ TYPE_MAP_OBJ[t].name for t in types if t != ElementType.Ctrl ]
            types_str = ", ".join(types_str)
            elem = "%s (%s) %s" % (ctrl_class_info.getName(), ctrl_class_info.getFileName(), types_str)
            ret.append(elem)
        return ret
    
    def check_element(self, name, full_name):
        raise_element_name = True
        try:
            self.get_element(name=name)
        except:
            raise_element_name = False
        if raise_element_name:
            raise Exception("An element with name '%s' already exists" % name)
        
        raise_element_full_name = True
        try:
            self.get_element(full_name=full_name)
        except:
            raise_element_full_name = False
        if raise_element_full_name:
            raise Exception("An element with full name '%s' already exists" % full_name)
    
    def create_controller(self, **kwargs):
        ctrl_type = kwargs['type']
        lib = kwargs['library']
        class_name = kwargs['klass']
        name = kwargs['name']
        elem_type = ElementType[ctrl_type]
        mod_name, ext = os.path.splitext(lib)
        kwargs['module'] = mod_name
        
        td = TYPE_MAP_OBJ[ElementType.Ctrl]
        klass_map = td.klass
        auto_full_name = td.auto_full_name
        ctrl_class = td.ctrl_klass
        kwargs['full_name'] = full_name = kwargs.get("full_name", auto_full_name.format(**kwargs))
        self.check_element(name, full_name)
        
        ctrl_class_info = None
        ctrl_lib_info = self.ctrl_manager.getControllerLib(mod_name)
        if ctrl_lib_info is not None:
            ctrl_class_info = ctrl_lib_info.getController(class_name)
        
        kwargs['pool'] = self
        kwargs['class_info'] = ctrl_class_info
        kwargs['lib_info'] = ctrl_lib_info
        id = kwargs.get('id')
        if id is None:
            kwargs['id'] = id = self.get_new_id()
        else:
            self.reserve_id(id)
        
        klass = klass_map.get(elem_type, PoolController)
        if elem_type == ElementType.PseudoMotor:
            motor_roles = kwargs['motor_ids']
            pseudo_motor_ids = kwargs.get('pseudo_motor_ids')
            if pseudo_motor_ids is None:
                if ctrl_class_info is not None:
                    ctrl_klass = ctrl_class_info.getControllerClass()
                    pm_nb = len(ctrl_klass.pseudo_motor_roles)
                    pseudo_motor_ids = [ self.get_new_id() for i in range(pm_nb) ]
                kwargs['pseudo_motor_ids'] = pseudo_motor_ids
        
        ctrl = klass(**kwargs)
        ret = self.add_element(ctrl)
        self.fire_event(EventType("ElementCreated"),
                        { "name" : name, "type" : ElementType.Ctrl })
        return ret
    
    def create_element(self, **kwargs):
        type = kwargs['type']
        ctrl_id = kwargs['ctrl_id']
        axis = kwargs['axis']
        elem_type = ElementType[type]
        name = kwargs['name']

        try:
            ctrl = self.get_element(id=ctrl_id)
        except:
            raise Exception("No controller with id '%d' found" % ctrl_id)
        
        #if not ctrl.is_online():
        #    raise Exception("Controller is offline. It is not possible to add %s" % name)

        elem_axis = ctrl.get_element(axis=axis)
        if elem_axis is not None:
            raise Exception("Controller already contains axis %d (%s)" % (axis, elem_axis.get_name()))

        kwargs['pool'] = self
        kwargs['ctrl'] = ctrl
        kwargs['ctrl_name'] = ctrl.get_name()
        
        td = TYPE_MAP_OBJ[elem_type]
        klass = td.klass
        auto_full_name = td.auto_full_name
        ctrl_class = td.ctrl_klass
        full_name = kwargs.get("full_name", auto_full_name.format(**kwargs))

        self.check_element(name, full_name)
        
        if ctrl.is_online():
            ctrl_types, ctrl_id = ctrl.get_ctrl_types(), ctrl.get_id()
            if elem_type not in ctrl_types:
                ctrl_type_str = ElementType.whatis(ctrl_types[0])
                raise Exception("Cannot create %s in %s controller" % (type, ctrl_type_str))

        #check if controller is online
        #check if axis is allowed
        #create the element in the controller
        
        id = kwargs.get('id')
        if id is None:
            kwargs['id'] = id = self.get_new_id()
        else:
            self.reserve_id(id)
        elem = klass(**kwargs)
        ctrl.add_element(elem)
        ret = self.add_element(elem)
        self.fire_event(EventType("ElementCreated"),
                        { "name" : name, "type" : elem_type })
        return ret
    
    def create_motor_group(self, **kwargs):
        name = kwargs['name']
        elem_ids = kwargs["user_elements"]
        
        kwargs['pool'] = self
        kwargs["pool_name"] = self.name
        td = TYPE_MAP_OBJ[ElementType.MotorGroup]
        klass = td.klass
        auto_full_name = td.auto_full_name
        full_name = kwargs.get("full_name", auto_full_name.format(**kwargs))
        kwargs.pop('pool_name')
        
        self.check_element(name, full_name)
        
        for elem_id in elem_ids:
            elem = self.pool.get_element(id=elem_id)
            if elem.get_type() not in (ElementType.Motor, ElementType.PseudoMotor):
                raise Exception("%s is not a motor" % elem.name)

        elem = klass(**kwargs)

        ret = self.add_element(elem)
        self.fire_event(EventType("ElementCreated"),
                        { "name" : name, "type" : ElementType.MotorGroup })
        return ret
    
    def create_measurement_group(self, **kwargs):
        name = kwargs['name']
        elem_ids = kwargs["user_elements"]
        
        kwargs['pool'] = self
        kwargs["pool_name"] = self.name
        
        td = TYPE_MAP_OBJ[ElementType.MeasurementGroup]
        klass = td.klass
        auto_full_name = td.auto_full_name
        ctrl_class = td.ctrl_klass

        full_name = kwargs.get("full_name", auto_full_name.format(**kwargs))
        kwargs.pop('pool_name')
        
        self.check_element(name, full_name)
        
        for elem_id in elem_ids:
            elem = self.pool.get_element(id=elem_id)
            # Do any check here if necessary
            
        elem = klass(**kwargs)

        ret = self.add_element(elem)
        self.fire_event(EventType("ElementCreated"),
                        { "name" : name, "type" : ElementType.MeasurementGroup })
        return ret
    
    def delete_element(self, name):
        try:
            elem = self.get_element(name=name)
        except:
            try:
                elem = self.get_element(full_name=name)
            except:
                raise Exception("There is no element with name '%s'" % name)
        
        elem_type = elem.get_type()
        if elem_type == ElementType.Ctrl:
            if len(elem.get_elements()) > 0:
                raise Exception("Cannot delete controller with elements. Delete elements first")
        elif elem_type == ElementType.Instrument:
            if elem.has_instruments():
                raise Exception("Cannot delete instrument with instruments. Delete instruments first")
            if elem.has_elements():
                raise Exception("Cannot delete instrument with elements")
            parent_instrument = elem.parent_instrument
            if parent_instrument is not None:
                parent_instrument.remove_instrument(elem)
        elif hasattr(elem, "get_controller"):
            ctrl = elem.get_controller()
            ctrl.remove_element(elem)
            instrument = elem.instrument
            if instrument is not None:
                instrument.remove_element(elem)
        
        self.remove_element(elem)
        
        self.fire_event(EventType("ElementDeleted"),
                        { "name" : name, "type" : elem_type } )
    
    def create_instrument(self, full_name, klass_name, id=None):
        is_root = full_name.count('/') == 1
        
        if is_root:
            parent_full_name, name = '', full_name[1:]
            parent = None
        else:
            parent_full_name, name = full_name.rsplit('/', 1)
            try:
                parent = self.get_element_by_full_name(parent_full_name)
            except:
                raise Exception("No parent instrument named '%s' found" % parent_full_name)
            if parent.get_type() != ElementType.Instrument:
                raise Exception("%s is not an instrument as expected" % parent_full_name)
            
        self.check_element(name, full_name)
        
        td = TYPE_MAP_OBJ[ElementType.Instrument]
        klass = td.klass
        auto_full_name = td.auto_full_name
        ctrl_class = td.ctrl_klass

        if id is None:
            id = self.get_new_id()
        else:
            self.reserve_id(id)
        elem = klass(id=id, name=name, full_name=full_name, parent=parent,
                     klass=klass_name, pool=self)
        if parent:
            parent.add_instrument(elem)
        ret = self.add_element(elem)
        self.fire_event(EventType("ElementCreated"),
                        { "name" : full_name, "type" : ElementType.Instrument })
        return ret
    
    