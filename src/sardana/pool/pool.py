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

"""This module contains the main pool class"""

from __future__ import print_function
from __future__ import with_statement

__all__ = ["Pool"]

__docformat__ = 'restructuredtext'

import os.path
import logging.handlers

from taurus.core.taurusvalidator import AttributeNameValidator
from taurus.core.util.containers import CaselessDict

from sardana import InvalidId, ElementType, TYPE_ACQUIRABLE_ELEMENTS, \
    TYPE_PSEUDO_ELEMENTS, TYPE_PHYSICAL_ELEMENTS, TYPE_MOVEABLE_ELEMENTS
from sardana.sardanamanager import SardanaElementManager, SardanaIDManager
from sardana.sardanamodulemanager import ModuleManager
from sardana.sardanaevent import EventType

from .poolobject import PoolObject
from .poolcontainer import PoolContainer
from .poolcontroller import PoolController
from .poolmonitor import PoolMonitor
from .poolmetacontroller import TYPE_MAP_OBJ
from .poolcontrollermanager import ControllerManager


class Graph(dict):

    def find_path(self, start, end, path=[]):
        path = path + [start]
        if start == end:
            return path
        if start not in self:
            return None
        for node in self[start]:
            if node not in path:
                newpath = self.find_path(node, end, path)
                if newpath: return newpath
        return None

    def find_all_paths(self, start, end, path=[]):
        path = path + [start]
        if start == end:
            return [path]
        if start not in self:
            return []
        paths = []
        for node in self[start]:
            if node not in path:
                newpaths = self.find_all_paths(node, end, path)
                for newpath in newpaths:
                    paths.append(newpath)
        return paths

    def find_shortest_path(self, start, end, path=[]):
        path = path + [start]
        if start == end:
            return path
        if start not in self:
            return None
        shortest = None
        for node in self[start]:
            if node not in path:
                newpath = self.find_shortest_path(node, end, path)
                if newpath:
                    if not shortest or len(newpath) < len(shortest):
                        shortest = newpath
        return shortest

        
class Pool(PoolContainer, PoolObject, SardanaElementManager, SardanaIDManager):
    """The central pool class."""

    #: Default value representing the number of state reads per position
    #: read during a motion loop
    Default_MotionLoop_StatesPerPosition = 10

    #: Default value representing the sleep time for each motion loop
    Default_MotionLoop_SleepTime = 0.01

    #: Default value representing the number of state reads per value
    #: read during a motion loop
    Default_AcqLoop_StatesPerValue = 10

    #: Default value representing the sleep time for each acquisition loop
    Default_AcqLoop_SleepTime = 0.01

    Default_DriftCorrection = True

    def __init__(self, full_name, name=None):
        self._path_id = None
        self._motion_loop_states_per_position = self.Default_MotionLoop_StatesPerPosition
        self._motion_loop_sleep_time = self.Default_MotionLoop_SleepTime
        self._acq_loop_states_per_value = self.Default_AcqLoop_StatesPerValue
        self._acq_loop_sleep_time = self.Default_AcqLoop_SleepTime
        self._drift_correction = self.Default_DriftCorrection
        self._remote_log_handler = None
        
        # dict<str, dict<str, str>>
        # keys are acquisition channel names and value is a dict describing the
        # channel containing:
        #  - 'name': with value being the channel name (given by user)
        #  - 'full_name': acq channel full name (ex: tango attribute)
        #  - 'origin': 'local' if local to this server or 'remote' if a remote
        #    channel
        self._extra_acquisition_element_names = CaselessDict()

        PoolContainer.__init__(self)
        PoolObject.__init__(self, full_name=full_name, name=name, id=InvalidId,
                            pool=self, elem_type=ElementType.Pool)
        self._monitor = PoolMonitor(self, "PMonitor", auto_start=False)
        #self.init_local_logging()
        ControllerManager().set_pool(self)
    
    # TODO: not ready to use. path must be the same as the one calculated in
    # sardana.tango.core.util:prepare_logging 
    def init_local_logging(self):
        log = logging.getLogger("Controller")
        log.propagate = 0
        path = os.path.join(os.sep, "tmp", "tango")
        log_file_name = os.path.join(path, 'controller.log.txt')
        try:
            if not os.path.exists(path):
                os.makedirs(path, 0777)
            f_h = logging.handlers.RotatingFileHandler(log_file_name,
                                                       maxBytes=1E7,
                                                       backupCount=5)

            f_h.setFormatter(self.getLogFormat())
            log.addHandler(f_h)
            self.info("Controller logs stored in %s", log_file_name)
        except:
            self.warning("Controller logs could not be created!")
            self.debug("Details:", exc_info=1)
        
    def clear_remote_logging(self):
        rh = self._remote_log_handler
        if rh is None:
            return
        log = logging.getLogger("Controller")
        log.removeHandler(rh)
        self._remote_log_handler = None
        
    def init_remote_logging(self, host=None, port=None):
        """Initializes remote logging.

        :param host: host name [default: None, meaning use the machine host name
                     as returned by :func:`socket.gethostname`].
        :type host: str
        :param port: port number [default: None, meaning use
                     :data:`logging.handlers.DEFAULT_TCP_LOGGING_PORT`"""
        log = logging.getLogger("Controller")

        # port 0 means no remote logging
        if port == 0:
            return

        # first check that the handler has not been initialized yet
        for handler in log.handlers:
            if isinstance(handler, logging.handlers.SocketHandler):
                return
        if host is None:
            import socket
            host = socket.gethostname()
            #host = socket.getfqdn()
        if port is None:
            port = logging.handlers.DEFAULT_TCP_LOGGING_PORT
        handler = logging.handlers.SocketHandler(host, port)
        if hasattr(handler, 'retryMax'):
            # default max retry is 30s which seems too much. Let's make it that
            # the pool tries to reconnect to a client every 10s (similar to the
            # tango event reconnection
            handler.retryMax = 10.0
        log.addHandler(handler)
        self.info("Remote logging initialized for host '%s' on port %d",
                  host, port)

    def serialize(self, *args, **kwargs):
        kwargs = PoolObject.serialize(self, *args, **kwargs)
        kwargs['type'] = self.__class__.__name__
        kwargs['id'] = InvalidId
        kwargs['parent'] = None
        return kwargs

    def set_motion_loop_sleep_time(self, motion_loop_sleep_time):
        self._motion_loop_sleep_time = motion_loop_sleep_time

    def get_motion_loop_sleep_time(self):
        return self._motion_loop_sleep_time

    motion_loop_sleep_time = property(get_motion_loop_sleep_time,
                                      set_motion_loop_sleep_time,
                                      doc="motion sleep time (s)")

    def set_motion_loop_states_per_position(self, motion_loop_states_per_position):
        self._motion_loop_states_per_position = motion_loop_states_per_position

    def get_motion_loop_states_per_position(self):
        return self._motion_loop_states_per_position

    motion_loop_states_per_position = property(get_motion_loop_states_per_position,
        set_motion_loop_states_per_position,
        doc="Number of State reads done before doing a position read in the "
            "motion loop")

    def set_acq_loop_sleep_time(self, acq_loop_sleep_time):
        self._acq_loop_sleep_time = acq_loop_sleep_time

    def get_acq_loop_sleep_time(self):
        return self._acq_loop_sleep_time

    acq_loop_sleep_time = property(get_acq_loop_sleep_time,
                                   set_acq_loop_sleep_time,
                                   doc="acquisition sleep time (s)")

    def set_acq_loop_states_per_value(self, acq_loop_states_per_value):
        self._acq_loop_states_per_value = acq_loop_states_per_value

    def get_acq_loop_states_per_value(self):
        return self._acq_loop_states_per_value

    acq_loop_states_per_value = property(get_acq_loop_states_per_value,
        set_acq_loop_states_per_value,
        doc="Number of State reads done before doing a value read in the "
            "acquisition loop")

    def set_drift_correction(self, drift_correction):
        self._drift_correction = drift_correction

    def get_drift_correction(self):
        return self._drift_correction

    drift_correction = property(get_drift_correction,
                                set_drift_correction,
                                doc="drift correction")
    @property
    def monitor(self):
        return self._monitor

    @property
    def ctrl_manager(self):
        return ControllerManager()

    def set_python_path(self, path):
        mod_man = ModuleManager()
        if self._path_id is not None:
            mod_man.remove_python_path(self._path_id)
        self._path_id = mod_man.add_python_path(path)

    def set_path(self, path):
        self.ctrl_manager.setControllerPath(path, reload=False)

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
        for ctrl_lib_info in libs:
            elem = "%s (%s)" % (ctrl_lib_info.getName(), ctrl_lib_info.getFileName())
            ret.append(elem)
        return ret

    def get_controller_classes_summary_info(self):
        ctrl_classes = self.get_controller_classes()
        ret = []
        for ctrl_class_info in ctrl_classes:
            types = ctrl_class_info.getTypes()
            types_str = [ TYPE_MAP_OBJ[t].name for t in types if t != ElementType.Controller ]
            types_str = ", ".join(types_str)
            elem = "%s (%s) %s" % (ctrl_class_info.getName(), ctrl_class_info.getFileName(), types_str)
            ret.append(elem)
        return ret

    def get_elements_str_info(self, obj_type=None):
        if obj_type is None:
            objs = self.get_element_id_map().values()
            objs.extend(self.get_controller_classes())
            objs.extend(self.get_controller_libs())
        elif obj_type == ElementType.ControllerClass:
            objs = self.get_controller_classes()
        elif obj_type == ElementType.ControllerLibrary:
            objs = self.get_controller_libs()
        else:
            objs = self.get_elements_by_type(obj_type)
        name = self.full_name
        return [ obj.str(pool=name) for obj in objs ]

    def get_elements_info(self, obj_type=None):
        if obj_type is None:
            objs = self.get_element_id_map().values()
            objs.extend(self.get_controller_classes())
            objs.extend(self.get_controller_libs())
            objs.append(self)
        elif obj_type == ElementType.ControllerClass:
            objs = self.get_controller_classes()
        elif obj_type == ElementType.ControllerLibrary:
            objs = self.get_controller_libs()
        else:
            objs = self.get_elements_by_type(obj_type)
        name = self.full_name
        return [ obj.serialize(pool=name) for obj in objs ]

    def get_acquisition_elements_info(self):
        ret = []
        for _, element in self.get_element_name_map().items():
            if element.get_type() not in TYPE_ACQUIRABLE_ELEMENTS:
                continue
            acq_channel = element.get_default_acquisition_channel()
            full_name = "{0}/{1}".format(element.full_name, acq_channel)
            info = dict(name=element.name, full_name=full_name, origin='local')
            ret.append(info)
        ret.extend(self._extra_acquisition_element_names.values())
        return ret

    def get_acquisition_elements_str_info(self):
        return map(self.str_object, self.get_acquisition_elements_info())

    def create_controller(self, **kwargs):
        ctrl_type = kwargs['type']
        lib = kwargs['library']
        class_name = kwargs['klass']
        name = kwargs['name']
        elem_type = ElementType[ctrl_type]
        mod_name, _ = os.path.splitext(lib)
        kwargs['module'] = mod_name

        td = TYPE_MAP_OBJ[ElementType.Controller]
        klass_map = td.klass
        auto_full_name = td.auto_full_name
        kwargs['full_name'] = full_name = \
            kwargs.get("full_name", auto_full_name.format(**kwargs))
        self.check_element(name, full_name)

        ctrl_class_info = None
        ctrl_lib_info = self.ctrl_manager.getControllerLib(mod_name)
        if ctrl_lib_info is not None:
            ctrl_class_info = ctrl_lib_info.get_controller(class_name)

        kwargs['pool'] = self
        kwargs['class_info'] = ctrl_class_info
        kwargs['lib_info'] = ctrl_lib_info
        eid = kwargs.get('id')
        if eid is None:
            kwargs['id'] = eid = self.get_new_id()
        else:
            self.reserve_id(eid)

        # For pseudo controllers make sure 'role_ids' is given
        klass = klass_map.get(elem_type, PoolController)
        if elem_type in TYPE_PSEUDO_ELEMENTS:
            motor_roles = kwargs['role_ids']

        # make sure the properties (that may have come from a case insensitive
        # environment like tango) are made case sensitive
        props = {}
        if ctrl_class_info is None:
            ctrl_prop_info = {}
        else:
            ctrl_prop_info = ctrl_class_info.ctrl_properties
        for k, v in kwargs['properties'].items():
            info = ctrl_prop_info.get(k)
            if info is None:
                props[k] = v
            else:
                props[info.name] = v
        kwargs['properties'] = props

        ctrl = klass(**kwargs)
        ret = self.add_element(ctrl)
        self.fire_event(EventType("ElementCreated"), ctrl)
        return ret

    def create_element(self, **kwargs):
        etype = kwargs['type']
        ctrl_id = kwargs['ctrl_id']
        axis = kwargs['axis']
        elem_type = ElementType[etype]
        name = kwargs['name']

        try:
            ctrl = self.get_element(id=ctrl_id)
        except:
            raise Exception("No controller with id '%d' found" % ctrl_id)

        elem_axis = ctrl.get_element(axis=axis)
        if elem_axis is not None:
            raise Exception("Controller already contains axis %d (%s)"
                            % (axis, elem_axis.get_name()))

        kwargs['pool'] = self
        kwargs['ctrl'] = ctrl
        kwargs['ctrl_name'] = ctrl.get_name()

        td = TYPE_MAP_OBJ[elem_type]
        klass = td.klass
        auto_full_name = td.auto_full_name
        full_name = kwargs.get("full_name", auto_full_name.format(**kwargs))

        self.check_element(name, full_name)

        if ctrl.is_online():
            ctrl_types, ctrl_id = ctrl.get_ctrl_types(), ctrl.get_id()
            if elem_type not in ctrl_types:
                ctrl_type_str = ElementType.whatis(ctrl_types[0])
                raise Exception("Cannot create %s in %s controller"
                                % (etype, ctrl_type_str))

        #check if controller is online
        #check if axis is allowed
        #create the element in the controller

        eid = kwargs.get('id')
        if eid is None:
            kwargs['id'] = eid = self.get_new_id()
        else:
            self.reserve_id(eid)
        elem = klass(**kwargs)
        ctrl.add_element(elem)
        ret = self.add_element(elem)
        self.fire_event(EventType("ElementCreated"), elem)
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

        eid = kwargs.get('id')
        if eid is None:
            kwargs['id'] = eid = self.get_new_id()
        else:
            self.reserve_id(eid)

        elem = klass(**kwargs)

        ret = self.add_element(elem)
        self.fire_event(EventType("ElementCreated"), elem)
        return ret

    def create_measurement_group(self, **kwargs):
        name = kwargs['name']
        elem_ids = kwargs["user_elements"]

        kwargs['pool'] = self
        kwargs["pool_name"] = self.name

        td = TYPE_MAP_OBJ[ElementType.MeasurementGroup]
        klass = td.klass
        auto_full_name = td.auto_full_name

        full_name = kwargs.get("full_name", auto_full_name.format(**kwargs))
        kwargs.pop('pool_name')

        self.check_element(name, full_name)

        for elem_id in elem_ids:
            if type(elem_id) is int:
                self.pool.get_element(id=elem_id)
            else:
                tg_attr_validator = AttributeNameValidator()
                params = tg_attr_validator.getParams(elem_id)
                if params is None:
                    raise Exception("Invalid channel name %s" % elem_id)

        eid = kwargs.get('id')
        if eid is None:
            kwargs['id'] = eid = self.get_new_id()
        else:
            self.reserve_id(eid)

        elem = klass(**kwargs)

        ret = self.add_element(elem)
        self.fire_event(EventType("ElementCreated"), elem)
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
        if elem_type == ElementType.Controller:
            if len(elem.get_elements()) > 0:
                raise Exception("Cannot delete controller with elements. "
                                "Delete elements first")
        elif elem_type == ElementType.Instrument:
            if elem.has_instruments():
                raise Exception("Cannot delete instrument with instruments. "
                                "Delete instruments first")
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

        self.fire_event(EventType("ElementDeleted"), elem)

    def create_instrument(self, full_name, klass_name, id=None):
        is_root = full_name.count('/') == 1

        if is_root:
            parent_full_name, _ = '', full_name[1:]
            parent = None
        else:
            parent_full_name, _ = full_name.rsplit('/', 1)
            try:
                parent = self.get_element_by_full_name(parent_full_name)
            except:
                raise Exception("No parent instrument named '%s' found"
                                % parent_full_name)
            if parent.get_type() != ElementType.Instrument:
                raise Exception("%s is not an instrument as expected"
                                % parent_full_name)

        self.check_element(full_name, full_name)

        td = TYPE_MAP_OBJ[ElementType.Instrument]
        klass = td.klass

        if id is None:
            id = self.get_new_id()
        else:
            self.reserve_id(id)
        elem = klass(id=id, name=full_name, full_name=full_name,
                     parent=parent, klass=klass_name, pool=self)
        if parent:
            parent.add_instrument(elem)
        ret = self.add_element(elem)
        self.fire_event(EventType("ElementCreated"), elem)
        return ret

    def stop(self):
        controllers = self.get_elements_by_type(ElementType.Controller)
        for controller in controllers:
            controller.stop_all()

    def abort(self):
        controllers = self.get_elements_by_type(ElementType.Controller)
        for controller in controllers:
            controller.abort_all()

    # --------------------------------------------------------------------------
    # (Re)load code
    # --------------------------------------------------------------------------

    def reload_controller_lib(self, lib_name):
        manager = self.ctrl_manager

        old_lib = manager.getControllerLib(lib_name)
        new_elements, changed_elements, deleted_elements = [], [], []
        old_ctrl_classes = ()
        if old_lib is not None:
            ctrl_infos = old_lib.get_controllers()
            pool_ctrls = self.get_elements_by_type(ElementType.Controller)
            init_pool_ctrls = []
            for pool_ctrl in pool_ctrls:
                if pool_ctrl.get_ctrl_info() in ctrl_infos:
                    init_pool_ctrls.append(pool_ctrl)
            old_ctrl_classes = ctrl_infos
            changed_elements.append(old_lib)

        new_lib = manager.reloadControllerLib(lib_name)

        if old_lib is None:
            new_elements.extend(new_lib.get_controllers())
            new_elements.append(new_lib)
        else:
            new_names = set([ ctrl.name for ctrl in new_lib.get_controllers() ])
            old_names = set([ ctrl.name for ctrl in old_lib.get_controllers() ])
            changed_names = set.intersection(new_names, old_names)
            deleted_names = old_names.difference(new_names)
            new_names = new_names.difference(old_names)

            for new_name in new_names:
                new_elements.append(new_lib.get_controller(new_name))
            for changed_name in changed_names:
                changed_elements.append(new_lib.get_controller(changed_name))
            for deleted_name in deleted_names:
                deleted_elements.append(old_lib.get_controller(deleted_name))

        evt = { "new" : new_elements, "change" : changed_elements,
                "del" : deleted_elements }

        self.fire_event(EventType("ElementsChanged"), evt)

        if old_lib is not None:
            for pool_ctrl in init_pool_ctrls:
                pool_ctrl.re_init()

    def reload_controller_class(self, class_name):
        ctrl_info = self.ctrl_manager.getControllerMetaClass(class_name)
        lib_name = ctrl_info.module_name
        self.reload_controller_lib(lib_name)

    def get_element_id_graph(self):
        physical_elems_id_map = {}
        elem_type_map = self.get_element_type_map()
        for elem_type in TYPE_PHYSICAL_ELEMENTS:
            physical_elems_id_map.update(elem_type_map[elem_type])
        #TODO
        
    def _build_element_id_dependencies(self, elem_id, graph=None):
        if graph is None:
            graph = Graph()
        elem = self.get_element_by_id(elem_id)
        if elem.get_id() in graph or elem.get_type() in TYPE_PHYSICAL_ELEMENTS:
            return graph
        graph[elem_id] = list(elem.get_user_element_ids())
        return graph
        
    def get_moveable_id_graph(self):
        moveable_elems_id_map = {}
        elem_type_map = self.get_element_type_map()
        for elem_type in TYPE_MOVEABLE_ELEMENTS:
            moveable_elems_id_map.update(elem_type_map[elem_type])
        graph = Graph()
        for moveable_id in moveable_elems_id_map:
            self._build_element_id_dependencies(moveable_id, graph)
        return graph

    def _build_element_dependencies(self, elem, graph=None):
        if graph is None:
            graph = Graph()
        if elem.get_id() in graph or elem.get_type() in TYPE_PHYSICAL_ELEMENTS:
            return graph
        graph[elem] = list(elem.get_user_elements())
        return graph
        
    def get_moveable_graph(self):
        moveable_elems_map = {}
        elem_type_map = self.get_element_type_map()
        for elem_type in TYPE_MOVEABLE_ELEMENTS:
            moveable_elems_map.update(elem_type_map[elem_type])
        graph = Graph()
        for moveable in moveable_elems_map.values():
            self._build_element_dependencies(moveable, graph)
        return graph    
