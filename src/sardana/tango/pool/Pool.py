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

""" """

__all__ = ["Pool", "PoolClass"]

__docformat__ = 'restructuredtext'

import json
import operator
import os.path

import PyTango

from taurus import Factory
from taurus.core.util.containers import CaselessDict
from taurus.core.util.codecs import CodecFactory
from taurus.core.util.log import Logger, DebugIt

from sardana import State, SardanaServer, ElementType, Interface, \
    TYPE_ACQUIRABLE_ELEMENTS, TYPE_PSEUDO_ELEMENTS
from sardana.pool.pool import Pool as POOL
from sardana.pool.poolmetacontroller import TYPE_MAP_OBJ
from sardana.tango.core.util import get_tango_version_number

class Pool(PyTango.Device_4Impl, Logger):

    ElementsCache = None

    def __init__(self,cl, name):
        PyTango.Device_4Impl.__init__(self,cl,name)
        Logger.__init__(self, name)
        self.init(name)
        self.init_device()

    def init(self, full_name):
        try:
            db = Factory().getDatabase()
            alias = db.get_alias(full_name)
            if alias.lower() == 'nada':
                alias = None
        except:
            alias = None

        if alias is None:
            alias = PyTango.Util.instance().get_ds_inst_name()

        self._pool = POOL(self.get_full_name(), alias)
        self._pool.add_listener(self.on_pool_changed)

    def get_full_name(self):
        db = PyTango.Util.instance().get_database()
        db_name = db.get_db_host() + ":" + db.get_db_port()
        return db_name + "/" + self.get_name()

    @property
    def pool(self):
        return self._pool

    @DebugIt()
    def delete_device(self):
        #self.pool.monitor.pause()
        pass

    @DebugIt()
    def init_device(self):
        self.set_state(PyTango.DevState.INIT)
        self.get_device_properties(self.get_device_class())
        p = self.pool
        p.set_python_path(self.PythonPath)
        p.set_path(self.PoolPath)
        p.set_motion_loop_sleep_time(self.MotionLoop_SleepTime / 1000.0)
        p.set_motion_loop_states_per_position(self.MotionLoop_StatesPerPosition)
        p.set_acq_loop_sleep_time(self.AcqLoop_SleepTime / 1000.0)
        p.set_acq_loop_states_per_value(self.AcqLoop_StatesPerValue)
        p.set_drift_correction(self.DriftCorrection)
        if self.RemoteLog is None:
            p.clear_remote_logging()
        else:
            try:
                h_p = self.RemoteLog.split(":",1)
                if len(h_p) == 1:
                    host = h_p[0]
                    port = None
                else:
                    host, port = h_p
                    port = int(port)
                p.init_remote_logging(host=host, port=port)
            except:
                self.warning("Invalid property value for 'RemoteLog': %s",
                             self.RemoteLog)
                p.clear_remote_logging()
        self._recalculate_instruments()
        for attr in self.get_device_class().attr_list:
            if attr.lower().endswith("list"):
                self.set_change_event(attr, True, False)
        self.set_change_event("State", True, False)
        self.set_change_event("Status", True, False)
        self.set_change_event("Elements", True, False)
        #hold the monitor thread for now!
        #self.pool.monitor.resume()
        self.set_state(PyTango.DevState.ON)

    def _recalculate_instruments(self):
        il = self.InstrumentList = list(self.InstrumentList)
        p = self.pool
        instruments = p.get_element_type_map().get(ElementType.Instrument, {})
        ids = set()
        for i in range(0, len(il), 3):
            iklass, iname, iid = il[i:i+3]
            iid = int(iid)
            ids.add(iid)
            if iid in instruments:
                #TODO make sure the instrument didn't change
                pass
            else:
                p.create_instrument(iname, iklass, id=iid)

    #@DebugIt()
    def always_executed_hook(self):
        pass

    #@DebugIt()
    def read_attr_hardware(self,data):
        pass

    #@DebugIt()
    def read_ControllerLibList(self, attr):
        info = self.pool.get_elements_str_info(ElementType.ControllerLibrary)
        attr.set_value(info)

    #@DebugIt()
    def read_ControllerClassList(self, attr):
        info = self.pool.get_elements_str_info(ElementType.ControllerClass)
        attr.set_value(info)

    #@PyTango.DebugIt(show_args=True,show_ret=True)
    def read_ControllerList(self, attr):
        info = self.pool.get_elements_str_info(ElementType.Controller)
        attr.set_value(info)

    def read_InstrumentList(self, attr):
        #instruments = self._pool.get_elements_by_type(ElementType.Instrument)
        #instrument_names = map(PoolInstrument.get_full_name, instruments)
        #attr.set_value(instrument_names)
        info = self.pool.get_elements_str_info(ElementType.Instrument)
        attr.set_value(info)

    #@DebugIt()
    def read_ExpChannelList(self, attr):
        info = []
        info.extend(self.pool.get_elements_str_info(ElementType.CTExpChannel))
        info.extend(self.pool.get_elements_str_info(ElementType.ZeroDExpChannel))
        info.extend(self.pool.get_elements_str_info(ElementType.OneDExpChannel))
        info.extend(self.pool.get_elements_str_info(ElementType.TwoDExpChannel))
        info.extend(self.pool.get_elements_str_info(ElementType.PseudoCounter))
        attr.set_value(info)

    #@DebugIt()
    def read_AcqChannelList(self, attr):
        info = self.pool.get_acquisition_elements_str_info()
        attr.set_value(info)

    #@DebugIt()
    def read_MotorGroupList(self, attr):
        info = self.pool.get_elements_str_info(ElementType.MotorGroup)
        attr.set_value(info)

    #@DebugIt()
    def read_MotorList(self, attr):
        info = self.pool.get_elements_str_info(ElementType.Motor)
        info.extend(self.pool.get_elements_str_info(ElementType.PseudoMotor))
        attr.set_value(info)

    #@DebugIt()
    def read_MeasurementGroupList(self, attr):
        info = self.pool.get_elements_str_info(ElementType.MeasurementGroup)
        attr.set_value(info)

    #@DebugIt()
    def read_IORegisterList(self, attr):
        info = self.pool.get_elements_str_info(ElementType.IORegister)
        attr.set_value(info)

    #@DebugIt()
    def read_ComChannelList(self, attr):
        info = self.pool.get_elements_str_info(ElementType.Communication)
        attr.set_value(info)

    #@DebugIt()
    def getElements(self, cache=True):
        value = self.ElementsCache
        if cache and value is not None:
            return value
        value = dict(new=self.pool.get_elements_info())
        value = CodecFactory().encode('json', ('', value))
        self.ElementsCache = value
        return value

    #@DebugIt()
    def read_Elements(self, attr):
        element_list = self.getElements()
        attr.set_value(*element_list)

    def is_Elements_allowed(self, req_type):
        return True
        return SardanaServer.server_state == State.Running

    is_ControllerLibList_allowed = \
    is_ControllerClassList_allowed = \
    is_ControllerList_allowed = \
    is_InstrumentList_allowed = \
    is_ExpChannelList_allowed = \
    is_AcqChannelList_allowed = \
    is_MotorGroupList_allowed = \
    is_MotorList_allowed = \
    is_MeasurementGroupList_allowed = \
    is_IORegisterList_allowed = \
    is_ComChannelList_allowed = is_Elements_allowed

    def _get_interface_ids(self, interface, elem_names):
        _pool, motor_ids = self.pool, []
        for elem_name in elem_names:
            try:
                element = _pool.get_element_by_name(elem_name)
            except:
                element = _pool.get_element_by_full_name(elem_name)
            elem_interface = element.get_interface()
            if not Interface.Moveable & elem_interface:
                raise Exception("%s is a %s. It MUST be a moveable"
                                % (element.name, Interface[elem_interface]))
            motor_ids.append(element.id)
        return motor_ids

    def _get_moveable_ids(self, elem_names):
        return self._get_interface_ids(Interface.Moveable, elem_names)

    def _get_acquirable_ids(self, elem_names):
        return self._get_interface_ids(Interface.Acquirable, elem_names)

    #@DebugIt()
    def CreateController(self, argin):
        kwargs = self._format_CreateController_arguments(argin)
        # TODO: Support in future sequence of elements
        kwargs = kwargs[0]

        type_str = kwargs['type']
        lib = kwargs['library']
        class_name = kwargs['klass']
        name = kwargs['name']
        properties = kwargs['properties']
        elem_type = ElementType[type_str]
        mod_name, _ = os.path.splitext(lib)
        kwargs['module'] = mod_name

        td = TYPE_MAP_OBJ[ElementType.Controller]
        auto_full_name = td.auto_full_name
        ctrl_class = td.ctrl_klass

        full_name = kwargs.get("full_name", auto_full_name.format(**kwargs))
        util = PyTango.Util.instance()

        # check that element doesn't exist yet
        self._check_element(name, full_name)

        # check library exists
        ctrl_manager = self.pool.ctrl_manager
        mod_name, _ = os.path.splitext(lib)
        ctrl_lib = ctrl_manager.getControllerLib(mod_name)
        if ctrl_lib is None:
            raise Exception("Controller library '%s' not found" % lib)

        # check class exists
        ctrl_class = ctrl_lib.get_controller(class_name)
        if ctrl_class is None:
            raise Exception("Controller class '%s' not found in '%s'"
                            % (class_name, lib))

        # check that class type matches the required type
        if not elem_type in ctrl_class.types:
            raise Exception("Controller class '%s' does not implement '%s' "
                            "interface" % (class_name, type_str))

        # check that necessary property values are set
        for prop_name, prop_info in ctrl_class.ctrl_properties.items():
            prop_value = properties.get(prop_name)
            if prop_value is None:
                if prop_info.default_value is None:
                    raise Exception("Controller class '%s' needs property '%s'"
                                    % (class_name, prop_name))
                properties[prop_name] = prop_info.default_value
            else:
                properties[prop_name] = prop_value

        # for pseudo motor check that motors are given
        if elem_type == ElementType.PseudoMotor:
            klass_roles = ctrl_class.controller_class.motor_roles
            klass_pseudo_roles = ctrl_class.controller_class.pseudo_motor_roles
            if not len(klass_pseudo_roles):
                klass_pseudo_roles = class_name,
            roles = kwargs.get('roles')
            if roles is None:
                raise Exception("Pseudo motor controller class %s needs motors "
                                "for roles: %s and pseudo roles: %s"
                                % (class_name, ", ".join(klass_roles),
                                   ", ".join(klass_pseudo_roles)))
            motor_ids = []
            for klass_role in klass_roles:
                if not klass_role in roles:
                    raise Exception("Pseudo motor controller class '%s' needs "
                                    "motor(s) for role(s) %s"
                                    % (class_name, klass_role))
                motor_name = roles[klass_role]
                motor_ids.extend(self._get_moveable_ids((motor_name,)))
            properties['motor_role_ids'] = motor_ids

            pseudo_motor_infos = {}
            pseudo_motor_ids = []
            for i, klass_pseudo_role in enumerate(klass_pseudo_roles):
                if not klass_pseudo_role in roles:
                    raise Exception("Pseudo motor controller class '%s' needs "
                                    "pseudo motor name for role '%s'"
                                    % (class_name, klass_pseudo_role))
                pm_id = self.pool.get_new_id()
                pm_name = roles[klass_pseudo_role]
                info = dict(id=pm_id, name=pm_name, ctrl_name=name, axis=i+1,
                            type='PseudoMotor', elements=motor_ids)
                if pm_name.count(',') > 0:
                    n, fn = map(str.strip, pm_name.split(',', 1))
                    info['name'], info['full_name'] = n, fn
                pseudo_motor_infos[klass_pseudo_role] = info
                pseudo_motor_ids.append(pm_id)
            properties['pseudo_motor_role_ids'] = pseudo_motor_ids
        # for pseudo counter check counters are given
        elif elem_type == ElementType.PseudoCounter:
            klass_roles = ctrl_class.controller_class.counter_roles
            klass_pseudo_roles = ctrl_class.controller_class.pseudo_counter_roles
            if not len(klass_pseudo_roles):
                klass_pseudo_roles = class_name,
            roles = kwargs.get('roles')
            if roles is None:
                raise Exception("Pseudo counter controller class '%s' needs "
                                "counter(s) for role(s): %s and pseudo "
                                "role(s): %s"
                                % (class_name, ", ".join(klass_roles),
                                   ", ".join(klass_pseudo_roles)))
            counter_ids = []
            for klass_role in klass_roles:
                if not klass_role in roles:
                    raise Exception("Pseudo counter controller class '%s' "
                                    "needs counter name for role '%s'"
                                    % (class_name, klass_role))
                counter_name = roles[klass_role]
                counter_ids.extend(self._get_acquirable_ids((counter_name,)))
            properties['counter_role_ids'] = counter_ids

            pseudo_counter_infos = {}
            pseudo_counter_ids = []
            for i, klass_pseudo_role in enumerate(klass_pseudo_roles):
                if not klass_pseudo_role in roles:
                    raise Exception("Pseudo counter controller class %s needs "
                                    "pseudo motor name for role %s"
                                    % (class_name, klass_pseudo_role))
                pc_id = self.pool.get_new_id()
                pc_name = roles[klass_pseudo_role]
                info = dict(id=pc_id, name=pc_name, ctrl_name=name, axis=i+1,
                            type='PseudoCounter', elements=counter_ids)
                if pc_name.count(',') > 0:
                    n, fn = map(str.strip, pc_name.split(',', 1))
                    info['name'], info['full_name'] = n, fn
                pseudo_counter_infos[klass_pseudo_role] = info
                pseudo_counter_ids.append(pc_id)
            properties['pseudo_counter_role_ids'] = pseudo_counter_ids

        properties['type'] = type_str
        properties['library'] = lib
        properties['klass'] = class_name

        def create_controller_cb(device_name):
            try:
                db = util.get_database()
                #types = [ pool.ElementType.whatis(t) for t in ctrl.get_ctrl_types() ]
                properties['id'] = self.pool.get_new_id()
                db.put_device_property(device_name, properties)
            except:
                self.warning("Unexpected error in controller creation callback",
                             exc_info=True)
                raise

        util.create_device('Controller', full_name, name,
                           cb=create_controller_cb)

        # Determine which controller writtable attributes have default value
        # and apply them to the newly created controller
        attrs = []
        for attr_name, attr_info in ctrl_class.ctrl_attributes.items():
            default_value = attr_info.default_value
            if default_value is None:
                continue
            attrs.append((attr_name, default_value))
        if attrs:
            ctrl_proxy = PyTango.DeviceProxy(full_name)
            try:
                ctrl_proxy.write_attributes(attrs)
            except:
                self.warning("Error trying to write controller default value "
                             "for attribute(s)", exc_info=1)

        # for pseudo motor/counter controller also create pseudo
        # motor(s)/counter(s) automatically
        if elem_type == ElementType.PseudoMotor:
            for pseudo_motor_info in pseudo_motor_infos.values():
                self._create_single_element(pseudo_motor_info)
        elif elem_type == ElementType.PseudoCounter:
            for pseudo_counter_info in pseudo_counter_infos.values():
                self._create_single_element(pseudo_counter_info)

    #@DebugIt()
    def CreateInstrument(self, argin):
        instrument = self.pool.create_instrument(*argin)
        instrument_list = self.InstrumentList
        # update database property
        instrument_list.append(instrument.instrument_class)
        instrument_list.append(instrument.full_name)
        instrument_list.append(instrument.id)
        db = PyTango.Util.instance().get_database()
        props = { 'InstrumentList' : instrument_list }
        db.put_device_property(self.get_name(), props)

    #@DebugIt()
    def CreateElement(self, argin):
        kwargs_seq = self._format_CreateElement_arguments(argin)
        for kwargs in kwargs_seq:
            self._create_single_element(kwargs)

    def _create_single_element(self, kwargs):
        elem_type_str = kwargs['type']
        ctrl_name = kwargs['ctrl_name']
        axis = kwargs['axis']

        try:
            elem_type = ElementType[elem_type_str]
        except KeyError:
            raise Exception("Unknown element type '%s'" % elem_type_str)
        name = kwargs['name']

        td = TYPE_MAP_OBJ[elem_type]
        auto_full_name = td.auto_full_name

        full_name = kwargs.get("full_name", auto_full_name.format(**kwargs))

        ctrl = self.pool.get_element(name=ctrl_name)

        if ctrl.get_type() != ElementType.Controller:
            type_str = ElementType.whatis(ctrl.get_type())
            raise Exception("'%s' is not a controller (It is a %s)" %
                            (ctrl_name, type_str))

        ctrl_types = ctrl.get_ctrl_types()
        if elem_type not in ctrl_types:
            ctrl_type_str = ElementType.whatis(ctrl_types[0])
            raise Exception("Cannot create %s in %s controller" %
                            (type, ctrl_type_str))

        elem_axis = ctrl.get_element(axis=axis)
        if elem_axis is not None:
            raise Exception("Controller already contains axis %d (%s)" %
                            (axis, elem_axis.get_name()))

        self._check_element(name, full_name)

        util = PyTango.Util.instance()

        def create_element_cb(device_name):
            try:
                db = util.get_database()
                data = { "id" : self.pool.get_new_id(),
                         "ctrl_id" : ctrl.get_id(), "axis" : axis, }
                if elem_type in TYPE_PSEUDO_ELEMENTS:
                    data['elements'] = kwargs['elements']

                db.put_device_property(device_name, data)

                data = {}
                if elem_type == ElementType.Motor:
                    data["position"] = { "abs_change" : "1.0"}
                    data["dialposition"] = { "abs_change" : "5.0"}
                    if get_tango_version_number() < 80000:
                        print 20*"AH! "
                        data["limit_switches"] = { "abs_change" : "1.0"}
                elif elem_type == ElementType.CTExpChannel:
                    data["value"] = { "abs_change" : "1.0"}
                elif elem_type == ElementType.PseudoMotor:
                    data["position"] = { "abs_change" : "1.0"}
                elif elem_type == ElementType.PseudoCounter:
                    data["value"] = { "abs_change" : "1.0"}
                elif elem_type == ElementType.IORegister:
                    data["value"] = { "abs_change" : "1"}
                db.put_device_attribute_property(device_name, data)
            except:
                import traceback
                traceback.print_exc()

        util.create_device(elem_type_str, full_name, name, cb=create_element_cb)

        # Hack to register event abs change until tango bug #3151801 is solved
        elem_proxy = PyTango.DeviceProxy(full_name)
        cfg = []
        if elem_type == ElementType.Motor:
            attr = elem_proxy.get_attribute_config_ex("position")[0]
            attr.events.ch_event.abs_change = "1"
            cfg.append(attr)
            try:
                attr = elem_proxy.get_attribute_config_ex("dialposition")[0]
                attr.events.ch_event.abs_change = "5.0"
                cfg.append(attr)
            except:
                pass
            try:
                if get_tango_version_number() < 80000:
                    attr = elem_proxy.get_attribute_config_ex("limit_switches")[0]
                    attr.events.ch_event.abs_change = "1"
                    cfg.append(attr)
            except:
                pass
        elif elem_type == ElementType.CTExpChannel:
            attr = elem_proxy.get_attribute_config_ex("value")[0]
            attr.events.ch_event.abs_change = "1.0"
            cfg.append(attr)
        elif elem_type == ElementType.ZeroDExpChannel:
            attr = elem_proxy.get_attribute_config_ex("value")[0]
            attr.events.ch_event.abs_change = "1.0"
            cfg.append(attr)
        elif elem_type == ElementType.PseudoMotor:
            attr = elem_proxy.get_attribute_config_ex("position")[0]
            attr.events.ch_event.abs_change = "1"
            cfg.append(attr)
        elif elem_type == ElementType.PseudoCounter:
            attr = elem_proxy.get_attribute_config_ex("value")[0]
            attr.events.ch_event.abs_change = "1"
            cfg.append(attr)
        elif elem_type == ElementType.IORegister:
            attr = elem_proxy.get_attribute_config_ex("value")[0]
            attr.events.ch_event.abs_change = "1"
            cfg.append(attr)
        elem_proxy.set_attribute_config(cfg)

        return

        # Determine which writtable attributes have default value and apply
        # them to the newly created element
        ctrl_class_info = ctrl.get_ctrl_info()
        attrs = []
        for attr_name, attr_info in ctrl_class_info.getAxisAttributes().items():
            default_value = attr_info.default_value
            if default_value is None:
                continue
            attrs.append((attr_name, default_value))
        if attrs:
            elem_proxy = PyTango.DeviceProxy(full_name)
            try:
                elem_proxy.write_attributes(attrs)
            except:
                self.warning("Error trying to write default value for "
                             "attribute(s)", exc_info=1)

    #@DebugIt()
    def CreateMotorGroup(self, argin):
        kwargs = self._format_CreateMotorGroup_arguments(argin)
        # TODO: Support in future sequence of elements
        kwargs = kwargs[0]

        util = PyTango.Util.instance()

        name = kwargs['name']
        kwargs['pool_name'] = self.pool.name

        td = TYPE_MAP_OBJ[ElementType.MotorGroup]
        auto_full_name = td.auto_full_name

        full_name = kwargs.get("full_name", auto_full_name.format(**kwargs))

        self._check_element(name, full_name)

        elem_ids = self._get_moveable_ids(kwargs["elements"])

        def create_motgrp_cb(device_name):
            db = util.get_database()
            data = { "id" : self.pool.get_new_id(),
                     "elements" : elem_ids }
            db.put_device_property(device_name, data)

            data = {}
            data["position"] = { "abs_change" : "1.0" }

            db.put_device_attribute_property(device_name, data)

        util.create_device("MotorGroup", full_name, name, cb=create_motgrp_cb)

    #@DebugIt()
    def CreateMeasurementGroup(self, argin):
        kwargs = self._format_CreateMeasurementGroup_arguments(argin)
        # TODO: Support in future sequence of elements
        kwargs = kwargs[0]

        util = PyTango.Util.instance()

        name = kwargs['name']
        kwargs['pool_name'] = self.pool.name

        td = TYPE_MAP_OBJ[ElementType.MeasurementGroup]
        auto_full_name = td.auto_full_name

        full_name = kwargs.get("full_name", auto_full_name.format(**kwargs))

        self._check_element(name, full_name)

        elem_ids = []
        for elem_name in kwargs["elements"]:
            # if internal pool element (channel, motor, ioregister, etc) store
            # it's id
            try:
                elem = self.pool.get_element(name=elem_name)
                elem_ids.append(elem.id)
            except:
                # otherwise assume a tango attribute/command
                elem_ids.append(elem_name)

        def create_mntgrp_cb(device_name):
            db = util.get_database()
            data = { "id" : self.pool.get_new_id(),
                     "elements" : elem_ids }
            db.put_device_property(device_name, data)

            data = { }

            db.put_device_attribute_property(device_name, data)

        util.create_device("MeasurementGroup", full_name, name,
                           cb=create_mntgrp_cb)

    def _check_element(self, name, full_name):
        self.pool.check_element(name, full_name)
        db = PyTango.Util.instance().get_database()
        e = None
        try:
            db.import_device(name)
            e = Exception("The tango alias '%s' already exists" % name)
        except:
            pass
        if e: raise e

        try:
            db.import_device(full_name)
            e = Exception("The tango device '%s' already exists" % full_name)
        except:
            pass
        if e: raise e

    def on_pool_changed(self, evt_src, evt_type, evt_value):
        # during server startup and shutdown avoid processing element
        # creation events
        if SardanaServer.server_state != State.Running:
            return

        evt_name = evt_type.name.lower()

        if evt_name in ("elementcreated", "elementdeleted"):
            elem = evt_value
            elem_type = elem.get_type()
            td = TYPE_MAP_OBJ[elem_type]
            attribute_list_name = td.family + "List"
            info = self.pool.get_elements_str_info(elem_type)
            self.push_change_event(attribute_list_name, info)

            if elem_type in TYPE_ACQUIRABLE_ELEMENTS:
                info = self.pool.get_acquisition_elements_str_info()
                self.push_change_event('AcqChannelList', info)

            # force the element list cache to be rebuild next time someone reads
            # the element list
            self.ElementsCache = None

            value = { }
            if "created" in evt_name:
                key = 'new'
            else:
                key = 'del'
            json_elem = elem.serialize(pool=self.pool.full_name)
            value[key] = json_elem,
            value = CodecFactory().getCodec('json').encode(('', value))
            self.push_change_event('Elements', *value)
        elif evt_name == "elementschanged":
            # force the element list cache to be rebuild next time someone reads
            # the element list
            self.ElementsCache = None
            pool_name = self.pool.full_name
            new_values, changed_values, deleted_values = [], [], []
            for elem in evt_value['new']:
                json_elem = elem.serialize(pool=pool_name)
                new_values.append(json_elem)
            for elem in evt_value['change']:
                json_elem = elem.serialize(pool=pool_name)
                changed_values.append(json_elem)
            for elem in evt_value['del']:
                json_elem = elem.serialize(pool=pool_name)
                deleted_values.append(json_elem)
            value = { "new" : new_values, "change": changed_values,
                      "del" : deleted_values }
            value = CodecFactory().getCodec('json').encode(('', value))
            self.push_change_event('Elements', *value)

    def _format_create_json_arguments(self, argin):
        elems, ret = json.loads(argin[0]), []
        if operator.isMappingType(elems):
            elems = [elems]
        for elem in elems:
            d = {}
            for k,v in elem.items():
                d[str(k)] = str(v)
            ret.append(d)
        return ret

    def _format_CreateElement_arguments(self, argin):
        if len(argin) == 0:
            msg = PoolClass.cmd_list["CreateElement"][0][1]
            raise Exception(msg)
        if len(argin) == 1:
            return self._format_create_json_arguments(argin)

        ret = { 'type' : argin[0], 'ctrl_name' : argin[1], 'axis': int(argin[2]),
                'name' : argin[3] }
        if len(argin) > 4:
            ret['full_name'] = argin[4]
        return [ret]

    def _format_CreateController_arguments(self, argin):
        if len(argin) == 0:
            msg = PoolClass.cmd_list["CreateController"][0][1]
            raise Exception(msg)
        if len(argin) == 1:
            ret = self._format_create_json_arguments(argin)
            if not ret.has_key('type'):
                raise KeyError("Missing key 'type'")
            if not ret.has_key('library'):
                raise KeyError("Missing key 'library'")
            if not ret.has_key('klass'):
                raise KeyError("Missing key 'klass'")
            if not ret.has_key('name'):
                raise KeyError("Missing key 'name'")
            if not ret.has_key('properties'):
                ret['properties'] = CaselessDict()
            return ret

        ret = { 'type' : argin[0], 'library' : argin[1], 'klass' : argin[2],
                'name' : argin[3] }

        i = 4
        roles = {}
        for arg in argin[4:]:
            role_data = arg.split('=', 1)
            if len(role_data) < 2:
                break
            role_name, role_element = role_data
            roles[role_name] = role_element
            i += 1

        if len(roles) > 0:
            ret['roles'] = roles

        p = argin[i:]
        if len(p) % 2:
            raise Exception("must give pair of property name, property value")
        props = CaselessDict()
        for name, value in zip(p[0::2], p[1::2]):
            props[name] = value
        ret['properties'] = props
        return [ret]

    def _format_CreateMotorGroup_arguments(self, argin):
        if len(argin) == 0:
            msg = PoolClass.cmd_list["CreateMotorGroup"][0][1]
            raise Exception(msg)
        if len(argin) == 1:
            ret = []
            try:
                elems = json.loads(argin[0])
            except:
                elems = argin
            if operator.isMappingType(elems):
                elems = [elems]
            for elem in elems:
                d = {}
                for k,v in elem.items():
                    d[str(k)] = str(v)
                ret.append(d)
            return ret
        ret = { 'name' : argin[0] }
        if argin[-1].count('/') == 2:
            ret['full_name'] = argin[-1]
            del argin[-1]
        ret['elements'] = argin[1:]
        return [ret]

    def _format_CreateMeasurementGroup_arguments(self, argin):
        if len(argin) == 0:
            msg = PoolClass.cmd_list["CreateMeasurementGroup"][0][1]
            raise Exception(msg)
        if len(argin) == 1:
            ret = []
            try:
                elems = json.loads(argin[0])
            except:
                elems = argin
            if operator.isMappingType(elems):
                elems = [elems]
            for elem in elems:
                d = {}
                for k,v in elem.items():
                    d[str(k)] = str(v)
                ret.append(d)
            return ret
        ret = { 'name' : argin[0] }
        #if argin[-1].count('/') == 2:
        #    ret['full_name'] = argin[-1]
        #    del argin[-1]
        channels = []
        for arg in argin[1:]:
            try:
                channel = self.pool.get_element_by_full_name(arg)
                channels.append(channel.name)
            except:
                try:
                    channel = self.pool.get_element_by_name(arg)
                    channels.append(channel.name)
                except:
                    channels.append(arg)
        ret['elements'] = channels
        return [ret]

    #@DebugIt()
    def DeleteElement(self, name):
        try:
            elem = self.pool.get_element(full_name=name)
        except:
            elem = self.pool.get_element(name=name)

        elem_type = elem.get_type()
        if elem_type == ElementType.Controller:
            if len(elem.get_elements()) > 0:
                raise Exception("Cannot delete controller with elements. " \
                                "Delete elements first")

        td = TYPE_MAP_OBJ[elem_type]
        type_name = td.name

        full_name = elem.get_full_name()

        self.pool.delete_element(name)
        if elem_type == ElementType.Instrument:
            # update database property
            il = self.InstrumentList
            idx = il.index(full_name)
            self.InstrumentList = il[:idx-1] + il[idx+2:]
            db = PyTango.Util.instance().get_database()
            props = { 'InstrumentList' : self.InstrumentList }
            db.put_device_property(self.get_name(), props)
        else:
            util = PyTango.Util.instance()
            util.delete_device(type_name, full_name)

    #@DebugIt()
    def GetControllerClassInfo(self, names):
        if names.startswith('['):
            names = json.loads(names)
        else:
            names = (names,)
        ctrl_classes = self.pool.get_controller_classes_info(names)
        ret = []
        for name in names:
            ctrl_class = ctrl_classes[name]
            data = None
            if ctrl_class is not None:
                data = ctrl_class.toDict()
            ret.append(data)
        return json.dumps(ret)

    #@DebugIt()
    def ReloadControllerLib(self, lib_name):
        self.pool.reload_controller_lib(lib_name)

    #@DebugIt()
    def ReloadControllerClass(self, class_name):
        self.pool.reload_controller_class(class_name)

    def Stop(self):
        self.pool.stop()

    def Abort(self):
        self.pool.abort()

    def SendToController(self, stream):
        ctrl_name, stream = stream[:2]
        try:
            ctrl = self.pool.get_element_by_name(ctrl_name)
        except KeyError:
            ctrl = self.pool.get_element_by_full_name(ctrl_name)
        return ctrl.send_to_controller(stream)

    def GetFile(self, name):
        p = self.pool
        manager = p.ctrl_manager
        lib = manager.getControllerLib(name)
        if lib is None:
            raise Exception("Unknown controller file '%s'", name)
        return lib.f_path, "".join(lib.getCode())

    def PutFile(self, file_data):
        p = self.pool
        manager = p.ctrl_manager
        manager.setControllerLib(*file_data)
    
    def GetControllerCode(self, argin):
        pass

    def SetControllerCode(self, argin):
        pass
        

CREATE_CONTROLLER_PAR_IN_DOC = """\
Must give either:

        * A JSON encoded dict as first string with:
            * mandatory keys: 'type', 'library', 'klass' and 'name' (values are
              strings).
            * optional keys:
                * 'properties': a dict with keys being property names and values
                  the property values
                * 'roles': a dict with keys being controller roles and values being
                  element names. (example: { 'gap' : 'motor21', 'offset' : 'motor55' }).
                  Only applicable of pseudo controllers
        * a sequence of strings: <type>, <library>, <class>, <name>
          [, <role_name>'='<element name>] [, <property name>, <property value>]

    Examples::
              
        data = dict(type='Motor', library='DummyMotorController',
                    klass='DummyMotorController',
                    name='my_motor_ctrl_1')
        pool.CreateController([json.dumps(data)])
              
        pool.CreateController(['Motor', 'DummyMotorController', 'DummyMotorController',
                               'my_motor_ctrl_2'])
"""

CREATE_CONTROLLER_PAR_OUT_DOC = "None"

CREATE_CONTROLLER_DOC = """\
Tango command to create controller.

:param argin:
    {0}
:type argin: list<str>
:return:
    {1}
""".format(CREATE_CONTROLLER_PAR_IN_DOC, CREATE_CONTROLLER_PAR_OUT_DOC)

CREATE_ELEMENT_PAR_IN_DOC = """\
Must give either:

        * A JSON encoded dict as first string with:
            * mandatory keys: 'type', 'ctrl_name', 'axis', 'name' (values are
              strings).
            * optional keys:
                * 'full_name' : a string representing the full tango device name
                
        * a sequence of strings: <type>, <ctrl_name>, <axis>, <name> [, <full_name>]

    Examples::

        data = dict(type='Motor', ctrl_name='my_motor_ctrl_1', axis='4', name='theta',
                    full_name='BL99/EH/THETA')
        pool.CreateElement([json.dumps(data)])
        
        pool.CreateElement(['Motor', 'my_motor_ctrl_1', '1', 'phi', 'BL99/EH/PHI'])
"""

CREATE_ELEMENT_PAR_OUT_DOC = "None"

CREATE_ELEMENT_DOC = """\
Tango command to create element (motor, counter/timer, 0D, 1D, 2D, IORegister).

:param argin:
    {0}
:type argin: list<str>
:return:
    {1}
""".format(CREATE_ELEMENT_PAR_IN_DOC, CREATE_ELEMENT_PAR_OUT_DOC)

CREATE_INSTRUMENT_PAR_IN_DOC = """\
Must give either:

        * A JSON encoded dict as first string with:
            * mandatory keys: 'full_name', 'klass' (values are strings).
        * a sequence of strings: <full_name>, <class>
        
    Examples::
        
        pool.CreateInstrument(['/OH', 'NXhutch'])
        pool.CreateInstrument(['/OH/Mono', 'NXmonochromator'])
        pool.CreateInstrument(['/EH', 'NXhutch'])
        pool.CreateInstrument(['/EH/Pilatus', 'NXdetector'])
"""

CREATE_INSTRUMENT_PAR_OUT_DOC = "None"

CREATE_INSTRUMENT_DOC = """\
Tango command to create instrument.

:param argin:
    {0}
:type argin: list<str>
:return:
    {1}
""".format(CREATE_INSTRUMENT_PAR_IN_DOC, CREATE_INSTRUMENT_PAR_OUT_DOC)

CREATE_MOTOR_GROUP_PAR_IN_DOC = """\
Must give either:

        * A JSON encoded dict as first string with:
            * mandatory keys: 'name', 'elements' (with value being a list of moveables)
            * optional keys:
                * 'full_name': with value being a full tango device name
        
        * a sequence of strings: <motor group name> [, <element> ]"

    Examples::

        data = dict(name='diffrac_motor_group', elements=['theta', 'theta2', 'phi'])
        pool.CreateMotorGroup([json.dumps(data)])
        
        pool.CreateMotorGroup(['diffrac_mg', 'theta', 'theta2' ])
"""

CREATE_MOTOR_GROUP_PAR_OUT_DOC = "None"

CREATE_MOTOR_GROUP_DOC = """\
Tango command to create motor group.

:param argin:
    {0}
:type argin: list<str>
:return:
    {1}
""".format(CREATE_MOTOR_GROUP_PAR_IN_DOC, CREATE_MOTOR_GROUP_PAR_OUT_DOC)

Pool.CreateMotorGroup.__func__.__doc__= CREATE_MOTOR_GROUP_DOC

CREATE_MEASUREMENT_GROUP_PAR_IN_DOC = """\
Must give either:

        * A JSON encoded dict as first string with:
            * mandatory keys: 'name', 'elements' (with value being a list of acquirables)"
            * optional keys:
                * 'full_name': with value being a full tango device name
        
        * a sequence of strings: <motor group name> [, <element> ]"

    An acquirable is either a sardana element (counter/timer, 0D, 1D, 2D, motor) or
    a tango attribute (ex: sys/tg_test/1/short_spectrum_ro)

    Examples::

        data = dict(name='my_exp_01', elements=['timer', 'C1', 'sys/tg_test/1/double_scalar'])
        pool.CreateMeasurementGroup([json.dumps(data)])
        
        pool.CreateMeasurementGroup(['my_exp_02', 'timer', 'CCD1', 'sys/tg_test/1/short_spectrum_ro'])
"""

CREATE_MEASUREMENT_GROUP_PAR_OUT_DOC = "None"

CREATE_MEASUREMENT_GROUP_DOC = """\
Tango command to create measurement group.

:param argin:
    {0}
:type argin: list<str>
:return:
    {1}
""".format(CREATE_MEASUREMENT_GROUP_PAR_IN_DOC, CREATE_MEASUREMENT_GROUP_PAR_OUT_DOC)

DELETE_ELEMENT_PAR_IN_DOC ="""\
name of element to be deleted
"""

DELETE_ELEMENT_PAR_OUT_DOC = "None"

DELETE_ELEMENT_DOC = """\
Tango command to delete element.

:param argin:
    {0}
:type argin: str
:return:
    {1}
""".format(DELETE_ELEMENT_PAR_IN_DOC, DELETE_ELEMENT_PAR_OUT_DOC)

GET_CONTROLLER_CLASS_INFO_PAR_IN_DOC = """\
Must give either:

        * A JSON encoded list of controller class names
        * a controller class name
    
    Examples::
    
        data = "DummyMotorController", "DummyCounterTimerController"
        pool.GetControllerClassInfo(json.dumps(data))
        pool.GetControllerClassInfo("DummyMotorController")

"""

GET_CONTROLLER_CLASS_INFO_PAR_OUT_DOC = """
a JSON encoded string describing the controller class
"""

GET_CONTROLLER_CLASS_INFO_DOC = """\
Tango command to get detailed information about a controller class.

:param argin:
    {0}
:type argin: str
:return:
    {1}
:rtype: str
""".format(GET_CONTROLLER_CLASS_INFO_PAR_IN_DOC, GET_CONTROLLER_CLASS_INFO_PAR_OUT_DOC)

RELOAD_CONTROLLER_LIB_PAR_IN_DOC = """\
the controller library name (without extension)
"""

RELOAD_CONTROLLER_LIB_PAR_OUT_DOC = "None"

RELOAD_CONTROLLER_LIB_INFO_DOC = """\
Tango command to reload the controller library code.

:param argin:
    {0}
:type argin: str
:return:
    {1}
""".format(RELOAD_CONTROLLER_LIB_PAR_IN_DOC, RELOAD_CONTROLLER_LIB_PAR_OUT_DOC)

RELOAD_CONTROLLER_CLASS_PAR_IN_DOC = """\
the controller class name
"""

RELOAD_CONTROLLER_CLASS_PAR_OUT_DOC = "None"

RELOAD_CONTROLLER_CLASS_INFO_DOC = """\
Tango command to reload the controller class code (reloads the entire library
where the class is described).

:param argin:
    {0}
:type argin: str
:return:
    {1}
""".format(RELOAD_CONTROLLER_CLASS_PAR_IN_DOC, RELOAD_CONTROLLER_CLASS_PAR_OUT_DOC)

STOP_PAR_IN_DOC = "None"
STOP_PAR_OUT_DOC = "None"

STOP_DOC = """\
Stops all elements managed by this Pool

:param argin:
    {0}
:return:
    {1}
""".format(STOP_PAR_IN_DOC, STOP_PAR_OUT_DOC)

ABORT_PAR_IN_DOC = "None"
ABORT_PAR_OUT_DOC = "None"

ABORT_DOC = """\
Aborts all elements managed by this Pool

:param argin:
    {0}
:return:
    {1}
""".format(ABORT_PAR_IN_DOC, ABORT_PAR_OUT_DOC)

SEND_TO_CONTROLLER_PAR_IN_DOC = """\
a sequence of two strings: <controller name>, <data>
"""

SEND_TO_CONTROLLER_PAR_OUT_DOC = """\
the controller response
"""

SEND_TO_CONTROLLER_DOC = """\
Sends a string to a controller.

:param argin:
    {0}
:return:
    {1}
""".format(SEND_TO_CONTROLLER_PAR_IN_DOC, SEND_TO_CONTROLLER_PAR_OUT_DOC)

Pool.CreateController.__func__.__doc__= CREATE_CONTROLLER_DOC
Pool.CreateElement.__func__.__doc__= CREATE_ELEMENT_DOC
Pool.CreateInstrument.__func__.__doc__= CREATE_INSTRUMENT_DOC
Pool.CreateMotorGroup.__func__.__doc__= CREATE_MOTOR_GROUP_DOC
Pool.CreateMeasurementGroup.__func__.__doc__= CREATE_MEASUREMENT_GROUP_DOC
Pool.DeleteElement.__func__.__doc__= DELETE_ELEMENT_DOC
Pool.GetControllerClassInfo.__func__.__doc__= GET_CONTROLLER_CLASS_INFO_DOC
Pool.ReloadControllerLib.__func__.__doc__= RELOAD_CONTROLLER_LIB_INFO_DOC
Pool.ReloadControllerClass.__func__.__doc__= RELOAD_CONTROLLER_CLASS_INFO_DOC
Pool.Stop.__func__.__doc__= STOP_DOC
Pool.Abort.__func__.__doc__= ABORT_DOC


class PoolClass(PyTango.DeviceClass):

    #    Class Properties
    class_property_list = {
        }

    #    Device Properties
    device_property_list = {
        'PoolPath':
            [PyTango.DevVarStringArray,
            "list of directories to search for controllers (path separators "
            "can be '\n' or ':')",
            []],
        'PythonPath':
            [PyTango.DevVarStringArray,
            "list of directories to be appended to sys.path at startup (path "
            "separators can be '\n' or ':')",
            []],
        'MotionLoop_SleepTime':
            [PyTango.DevLong,
            "Sleep time in the motion loop in mS [default: %dms]" %
            int(POOL.Default_MotionLoop_SleepTime*1000),
            int(POOL.Default_MotionLoop_SleepTime*1000)],
        'MotionLoop_StatesPerPosition':
            [PyTango.DevLong,
            "Number of State reads done before doing a position read in the "
            "motion loop [default: %d]" % POOL.Default_MotionLoop_StatesPerPosition,
            POOL.Default_MotionLoop_StatesPerPosition],
        'AcqLoop_SleepTime':
            [PyTango.DevLong,
            "Sleep time in the acquisition loop in mS [default: %dms]" %
            int(POOL.Default_AcqLoop_SleepTime*1000),
            int(POOL.Default_AcqLoop_SleepTime*1000)],
        'AcqLoop_StatesPerValue':
            [PyTango.DevLong,
            "Number of State reads done before doing a value read in the "
            "acquisition loop [default: %d]" % POOL.Default_AcqLoop_StatesPerValue,
            POOL.Default_AcqLoop_StatesPerValue],
        'RemoteLog':
            [PyTango.DevString,
            "Logging (python logging) host:port [default: None]",
            None],
        'DriftCorrection':
            [PyTango.DevBoolean,
            "Globally apply drift correction on pseudo motors (can be "
            "overwritten at PseudoMotor level [default: %d]." %
            POOL.Default_DriftCorrection,
            POOL.Default_DriftCorrection],
        'InstrumentList':
            [PyTango.DevVarStringArray,
            "List of instruments (internal property)",
            []],
    }

    #    Command definitions
    cmd_list = {
        'CreateController':
            [[PyTango.DevVarStringArray, CREATE_CONTROLLER_PAR_IN_DOC],
             [PyTango.DevVoid, CREATE_CONTROLLER_PAR_OUT_DOC]],
        'CreateElement':
            [[PyTango.DevVarStringArray, CREATE_ELEMENT_PAR_IN_DOC],
             [PyTango.DevVoid, CREATE_ELEMENT_PAR_OUT_DOC]],
        'CreateInstrument':
            [[PyTango.DevVarStringArray, CREATE_INSTRUMENT_PAR_IN_DOC],
             [PyTango.DevVoid, CREATE_INSTRUMENT_PAR_OUT_DOC]],
        'CreateMotorGroup':
            [[PyTango.DevVarStringArray, CREATE_MOTOR_GROUP_PAR_IN_DOC],
             [PyTango.DevVoid, CREATE_MOTOR_GROUP_PAR_OUT_DOC]],
        'CreateMeasurementGroup':
            [[PyTango.DevVarStringArray, CREATE_MEASUREMENT_GROUP_PAR_IN_DOC],
             [PyTango.DevVoid, CREATE_MEASUREMENT_GROUP_PAR_OUT_DOC]],
        'DeleteElement':
            [[PyTango.DevString, DELETE_ELEMENT_PAR_IN_DOC],
            [PyTango.DevVoid, DELETE_ELEMENT_PAR_OUT_DOC]],
        'GetControllerClassInfo':
            [[PyTango.DevString, GET_CONTROLLER_CLASS_INFO_PAR_IN_DOC],
             [PyTango.DevString, GET_CONTROLLER_CLASS_INFO_PAR_OUT_DOC]],
        'ReloadControllerLib':
            [[PyTango.DevString, RELOAD_CONTROLLER_LIB_PAR_IN_DOC],
             [PyTango.DevVoid, RELOAD_CONTROLLER_LIB_PAR_OUT_DOC]],
        'ReloadControllerClass':
            [[PyTango.DevString, RELOAD_CONTROLLER_CLASS_PAR_IN_DOC],
             [PyTango.DevVoid, RELOAD_CONTROLLER_CLASS_PAR_OUT_DOC]],
        'GetControllerCode':
            [[PyTango.DevVarStringArray, "<Controller library name> [, <Controller class name>]"],
            [PyTango.DevVarStringArray, "result is a sequence of 3 strings:\n"
                "<full path and file name>, <code>, <line number>" ]],
        'SetControllerCode':
            [[PyTango.DevVarStringArray, "<Controller library name>, <code> [, <Auto reload>=True]\n" \
                "- if controller library is a simple module name:\n" \
                "  - if it exists, it is overwritten, otherwise a new python " \
                "file is created in the directory of the first element in "\
                "the PoolPath property" \
                "- if controller library is the full path name:\n" \
                "  - if path is not in the PoolPath, an exception is thrown" \
                "  - if file exists it is overwritten otherwise a new file " \
                "is created"],
            [PyTango.DevVoid, "" ]],
        'Stop':
            [[PyTango.DevVoid, STOP_PAR_IN_DOC],
             [PyTango.DevVoid, STOP_PAR_OUT_DOC]],
        'Abort':
            [[PyTango.DevVoid, ABORT_PAR_IN_DOC],
             [PyTango.DevVoid, ABORT_PAR_OUT_DOC]],
        'SendToController':
            [[PyTango.DevVarStringArray, SEND_TO_CONTROLLER_PAR_IN_DOC],
             [PyTango.DevString, SEND_TO_CONTROLLER_PAR_OUT_DOC]],
        'GetFile':
            [[PyTango.DevString, "name (may be module name, file name or full (with absolute path) file name"],
             [PyTango.DevVarStringArray, "[complete(with absolute path) file name, file contents]"]],
        'PutFile':
            [[PyTango.DevVarStringArray, "[name (may be module name, file name or full (with absolute path) file name, file contents]"],
             [PyTango.DevVoid, ""]],
    }


    #    Attribute definitions
    attr_list = {
        'InstrumentList':
            [[PyTango.DevString,
            PyTango.SPECTRUM,
            PyTango.READ, 4096],
            {
                'label':"Motor list",
                'description':"the list of instruments (a JSON encoded dict)",
            } ],
        'ControllerList':
            [[PyTango.DevString,
            PyTango.SPECTRUM,
            PyTango.READ, 4096],
            {
                'label':"Controller list",
                'description':"the list of controllers (a JSON encoded dict)",
            } ],
        'ExpChannelList':
            [[PyTango.DevString,
            PyTango.SPECTRUM,
            PyTango.READ, 4096],
            {
                'label':"Experiment channel list",
                'description':"The list of experiment channels (a JSON encoded dict)",
            } ],
        'AcqChannelList':
            [[PyTango.DevString,
            PyTango.SPECTRUM,
            PyTango.READ, 4096],
            {
                'label':"Acquisition channel list",
                'description':"The list of all acquisition channels (a JSON encoded dict)",
            } ],
        'MotorGroupList':
            [[PyTango.DevString,
            PyTango.SPECTRUM,
            PyTango.READ, 4096],
            {
                'label':"Motor group list",
                'description':"the list of motor groups (a JSON encoded dict)",
            } ],
        'ControllerLibList':
            [[PyTango.DevString,
            PyTango.SPECTRUM,
            PyTango.READ, 4096],
            {
                'label':"Controller library list",
                'description':"the list of controller libraries (a JSON encoded dict)",
            } ],
        'ControllerClassList':
            [[PyTango.DevString,
            PyTango.SPECTRUM,
            PyTango.READ, 4096],
            {
                'label':"Controller class list",
                'description':"the list of controller classes (a JSON encoded dict)",
            } ],
        'MotorList':
            [[PyTango.DevString,
            PyTango.SPECTRUM,
            PyTango.READ, 4096],
            {
                'label':"Motor list",
                'description':"the list of motors (a JSON encoded dict)",
            } ],
        'MeasurementGroupList':
            [[PyTango.DevString,
            PyTango.SPECTRUM,
            PyTango.READ, 4096],
            {
                'label':"Measurement group list",
                'description':"the list of measurement groups (a JSON encoded dict)",
            } ],
        'IORegisterList':
            [[PyTango.DevString,
            PyTango.SPECTRUM,
            PyTango.READ, 4096],
            {
                'label':"IORegister list",
                'description':"the list of IORegisters (a JSON encoded dict)",
            } ],
        'ComChannelList':
            [[PyTango.DevString,
            PyTango.SPECTRUM,
            PyTango.READ, 4096],
            {
                'label':"Communication channel list",
                'description':"the list of communication channels (a JSON encoded dict)",
            } ],
        'Elements':
            [[PyTango.DevEncoded,
            PyTango.SCALAR,
            PyTango.READ],
            {
                'label':"Elements",
                'description':"the list of all elements (a JSON encoded dict)",
            } ],
        }

    def __init__(self, name):
        PyTango.DeviceClass.__init__(self, name)
        self.set_type(name)

    def _get_class_properties(self):
        return dict(ProjectTitle="Sardana", Description="Device Pool management class",
                    doc_url="http://sardana-controls.org/",
                    InheritedFrom="Device_4Impl")

    def write_class_property(self):
        util = PyTango.Util.instance()
        db = util.get_database()
        if db is None:
            return
        db.put_class_property(self.get_name(), self._get_class_properties())
