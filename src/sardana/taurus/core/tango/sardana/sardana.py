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

"""The sardana submodule. It contains specific part of sardana"""

__all__ = ["BaseSardanaElement", "BaseSardanaElementContainer",
           "Pool", "MacroServer", "Door", "Sardana", "SardanaManager",
           "PoolElementType", "ControllerClassInfo", "ControllerInfo",
           "ChannelView", "PlotType", "Normalization", "AcqTriggerType",
           "AcqMode"]

#-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
# T E M P O R A R Y   I M P L E M E N T A T I O N
#
# THIS IS USED FOR TEST PURPOSES ONLY. DO NOT USE IT OUTSIDE SARDANA TESTS
#-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

__docformat__ = 'restructuredtext'

import PyTango

from taurus.core.util.enumeration import Enumeration
from taurus.core.util.log import Logger
from taurus.core.util.singleton import Singleton
from taurus.core.util.containers import CaselessDict
from taurus.core.util.codecs import CodecFactory

PoolElementType = Enumeration("PoolElementType",
    ("0D", "1D", "2D", "Communication", "CounterTimer", "IORegister",
      "Motor", "PseudoCounter", "PseudoMotor"))

ChannelView = Enumeration("ChannelView",
    ("Channel", "Enabled", "Output", "PlotType", "PlotAxes", "Timer",
     "Monitor", "Trigger", "Conditioning", "Normalization", "NXPath",
     "Shape", "DataType",
     "Unknown"))

PlotType = Enumeration("PlotType", ("No", "Spectrum", "Image"))

Normalization = Enumeration("Normalization", ("No", "Avg", "Integ"))

#: an enumeration describing all possible acquisition trigger types
AcqTriggerType = Enumeration("AcqTriggerType", (\
    "Software",  # channel triggered by software - start and stop by software
    "Gate",  # channel triggered by HW - start and stop by external
    "Unknown"))

#: an enumeration describing all possible acquisition mode types
AcqMode = Enumeration("AcqMode", (\
    "Timer",
    "Monitor",
    "Unknown"))


class BaseSardanaElement(object):
    """Generic sardana element"""

    def __init__(self, *args, **kwargs):
        self._manager = kwargs.pop('manager')
        self.__dict__.update(kwargs)
        self._data = kwargs
        self._object = None

    def __repr__(self):
        return "{0}({1})".format(self.type, self.full_name)

    def __str__(self):
        return self.name

    def __getattr__(self, name):
        return getattr(self.getObj(), name)

    def __cmp__(self, elem):
        return cmp(self.name, elem.name)

    def getData(self):
        return self._data

    def getName(self):
        return self.name

    def getId(self):
        return self.full_name

    def getType(self):
        return self.getTypes()[0]

    def getTypes(self):
        elem_types = self.type
        if isinstance(elem_types, (str, unicode)):
            return [elem_types]
        return elem_types

    def serialize(self, *args, **kwargs):
        kwargs.update(self._data)
        return kwargs

    def str(self, *args, **kwargs):
        #TODO change and check which is the active protocol to serialize
        #acordingly
        return CodecFactory().encode(('json', self.serialize(*args, **kwargs)))

    def getObj(self):
        obj = self._object
        if obj is None:
            self._object = obj = self._manager.getObject(self)
        return obj



class BaseSardanaElementContainer:

    def __init__(self):
        # dict<str, dict> where key is the type and value is:
        #     dict<str, MacroServerElement> where key is the element full name
        #                                   and value is the Element object
        self._type_elems_dict = CaselessDict()

        # dict<str, container> where key is the interface and value is the set
        # of elements which implement that interface
        self._interfaces_dict = {}

    def addElement(self, elem):
        elem_type = elem.getType()
        elem_full_name = elem.full_name

        #update type_elems
        type_elems = self._type_elems_dict.get(elem_type)
        if type_elems is None:
            self._type_elems_dict[elem_type] = type_elems = CaselessDict()
        type_elems[elem_full_name] = elem

        # update interfaces
        for interface in elem.interfaces:
            interface_elems = self._interfaces_dict.get(interface)
            if interface_elems is None:
                self._interfaces_dict[interface] = interface_elems = CaselessDict()
            interface_elems[elem_full_name] = elem

    def removeElement(self, e):
        elem_type = e.getType()

        # update type_elems
        type_elems = self._type_elems_dict.get(elem_type)
        if type_elems:
            del type_elems[e.full_name]

        # update interfaces
        for interface in e.interfaces:
            interface_elems = self._interfaces_dict.get(interface)
            del interface_elems[e.full_name]

    def removeElementsOfType(self, t):
        for elem in self.getElementsOfType(t):
            self.removeElement(elem)

    def getElementsOfType(self, t):
        elems = self._type_elems_dict.get(t, {})
        return elems

    def getElementNamesOfType(self, t):
        return [e.name for e in self.getElementsOfType(t).values()]

    def getElementsWithInterface(self, interface):
        elems = self._interfaces_dict.get(interface, {})
        return elems

    def getElementsWithInterfaces(self, interfaces):
        ret = CaselessDict()
        for interface in interfaces:
            ret.update(self.getElementsWithInterface(interface))
        return ret

    def getElementNamesWithInterface(self, interface):
        return [e.name for e in self.getElementsWithInterface(interface).values()]

    def hasElementName(self, elem_name):
        return self.getElement(elem_name) != None

    def getElement(self, elem_name):
        elem_name = elem_name.lower()
        for elems in self._type_elems_dict.values():
            elem = elems.get(elem_name)  # full_name?
            if elem is not None:
                return elem
            for elem in elems.values():
                if elem.name.lower() == elem_name:
                    return elem

    def getElementWithInterface(self, elem_name, interface):
        elem_name = elem_name.lower()
        elems = self._interfaces_dict.get(interface, {})
        if elem_name in elems:
            return elems[elem_name]
        for elem in elems.values():
            if elem.name.lower() == elem_name:
                return elem

    def getElements(self):
        ret = set()
        for elems in self._type_elems_dict.values():
            ret.update(elems.values())
        return ret

    def getInterfaces(self):
        return self._interfaces_dict

    def getTypes(self):
        return self._type_elems_dict

#-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
# T E M P O R A R Y   I M P L E M E N T A T I O N
#
# THIS IS USED FOR TEST PURPOSES ONLY. DO NOT USE IT OUTSIDE SARDANA TESTS
#-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
class PropertyInfo():
    def __init__(self, name, type, format, default_value=None):
        self._name = name
        self._type = type
        self._format = format
        self._default_value = default_value

    def get_name(self):
        return self._name

    def get_type(self):
        return self._type

    def get_format(self):
        return self._format

    def get_default_value(self):
        return self._default_value


#-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
# T E M P O R A R Y   I M P L E M E N T A T I O N
#
# THIS IS USED FOR TEST PURPOSES ONLY. DO NOT USE IT OUTSIDE SARDANA TESTS
#-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
class ControllerClassInfo(object):

    def __init__(self, name, type, library):
        self._name = name
        self._type = type
        self._library = library

    def get_max_elements(self):
        return 20

    def get_name(self):
        return self._name

    def get_model(self):
        # fake data ###############
        return "Model of " + self._name

    def get_icon(self):
        # fake data ###############
        import taurus.qt.qtgui.resource

        return taurus.qt.qtgui.resource.getIcon(":/designer/extra_motor.png")

    def get_organization(self):
        # fake data ###############
        return "Organization of " + self._name

    def get_description(self):
        #fake data############
        descr = "This is description of "
        for i in range(20):
            descr = descr + " and " + self._name
        ####################
        return descr

    def get_family(self):
        # fake data ###############
        return "Family of " + self._name

    def get_properties(self):
        properties = []
        # fake data ######################
        properties.append(PropertyInfo("my parameter", "string", "0D", "deviceName"))
        properties.append(PropertyInfo("asdsadasd", "integer", "0D", 5))
        properties.append(PropertyInfo("boollll0", "boolean", "0D", False))
        properties.append(PropertyInfo("boollll0", "boolean", "0D", True))
        properties.append(PropertyInfo("boollll0", "boolean", "0D", False))
        properties.append(PropertyInfo("number1", "float", "0D", 3.5))
        properties.append(PropertyInfo("string2", "string", "0D", "hehe"))
        properties.append(PropertyInfo("tableIntegerD1", "integer", "1D", [1, 2, 3]))
        properties.append(PropertyInfo("tablestringD1", "string", "1D", ["aaaa", "bbb", "ccc"]))
        properties.append(PropertyInfo("tablefloatD1", "float", "1D", [1.0, 2.5, 3.6]))
        properties.append(PropertyInfo("tablebooleanD1", "boolean", "1D", [True, False, True, False]))
        properties.append(PropertyInfo("tablebleintegerD1", "integer", "1D", [1, 2, 3]))
        properties.append(PropertyInfo("tablebooleanD2", "boolean", "2D", [ [True, False, True], [True, True, True], [False, False, False] ]))
        properties.append(PropertyInfo("tableinteger2", "integer", "2D", [ [1, 2, 3], [11, 22, 33], [-10, -20, -30] ]))
        properties.append(PropertyInfo("tablefloatD2", "float", "2D", [ [0.5, 0.6, 0.8], [0.4, 0.0, 0.333333], [-0.1111, 1, 123123.6] ]))
        properties.append(PropertyInfo("tablestringD2", "string", "2D", [ ["aaaa", "bbb", "ccc"], ["aaaa2", "bbb2", "ccc2"], ["aaaa3", "bbb3", "ccc3"] ]))

        return properties

    def get_controller_type(self):
        return self._type


#-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
# T E M P O R A R Y   I M P L E M E N T A T I O N
#
# THIS IS USED FOR TEST PURPOSES ONLY. DO NOT USE IT OUTSIDE SARDANA TESTS
#-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
class ControllerInfo(object):

    def __init__(self, name, ctrl_class_info):
        self._name = name
        self._ctrl_class_info = ctrl_class_info

    def get_controller_class_info(self):
        return self._ctrl_class_info

    def get_controller_type(self):
        return self._ctrl_class_info.get_controller_type()

    def get_name(self):
        return self._name

    def get_max_elements(self):
        return self._ctrl_class_info.get_max_elements()

    def is_axis_free(self, axis):
        #fake data
        if axis == 3:
            return False
        else:
            return True

    def is_name_free(self, name):
        #fake data
        if name == "asd":
            return False
        else:
            return True

    def get_icon(self):
        return self._ctrl_class_info.get_icon()

#-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
# T E M P O R A R Y   I M P L E M E N T A T I O N
#
# THIS IS USED FOR TEST PURPOSES ONLY. DO NOT USE IT OUTSIDE SARDANA TESTS
#-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
class Pool(object):

    def __init__(self, sardana, name, poolpath, version, alias=None, device_name=None):
        self._sardana = sardana
        self._name = name
        self._poolpath = poolpath
        self._version = version
        self._alias = alias
        self._device_name = device_name

    def starter_run(self, host, level=1):
        return True

    def get_name(self):
        return self._name

    def local_run(self):
        return True

    def get_element_types(self):
        return sorted(PoolElementType.keys())

    def get_controller_class_infos(self):
        #fake data ########################
        data = []
        for i in range(5):
            data.append(ControllerClassInfo("motorController" + str(i), PoolElementType.Motor, None))
        for i in range(5):
            data.append(ControllerClassInfo("counterTimerController" + str(i), PoolElementType.CounterTimer, None))

        return data

    def get_controller_infos(self):
        ctrl_classes = self.get_controller_class_infos()
        data = []
        for i in range(2):
            data.append(ControllerInfo("My_motor_ctrl_" + str(i), ctrl_classes[i]))
        for i in range(2):
            data.append(ControllerInfo("My_ct_ctrl_" + str(i), ctrl_classes[i + 5]))
        return data

    def create_controller(self, controller_class_info, name, properties):
        pass

    def create_element(self, controller_name, name, axis):
        pass


#-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
# T E M P O R A R Y   I M P L E M E N T A T I O N
#
# THIS IS USED FOR TEST PURPOSES ONLY. DO NOT USE IT OUTSIDE SARDANA TESTS
#-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
class MacroServer(object):

    def __init__(self, sardana, name, macropath, pool_names, version, alias=None, device_name=None):
        self._sardana = sardana
        self._name = name
        self._macropath = macropath
        self._pool_names = pool_names
        self._version = version
        self._alias = alias
        self._device_name = device_name
        self._doors = []

    def create_door(self, alias, device_name):
        try:
            return self._create_door(alias, device_name)
        except:
            db = self.get_database()
            db.delete_device(device_name)
            raise

    def _create_door(self, alias, device_name):
        db = self.get_database()
        info = PyTango.DbDevInfo()
        info.name = device_name
        info._class = "Door"
        info.server = "MacroServer/" + self._name
        db.add_device(info)
        if alias:
            db.put_device_alias(device_name, alias)
        door = Door(alias=alias, device_name=device_name)
        self._doors.append(door)
        return door

    def remove_door(self, device_name):
        pass

    def starter_run(self, host, level=1):
        return True

    def local_run(self):
        return True

    def get_database(self):
        return self._sardana.get_database()

#-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
# T E M P O R A R Y   I M P L E M E N T A T I O N
#
# THIS IS USED FOR TEST PURPOSES ONLY. DO NOT USE IT OUTSIDE SARDANA TESTS
#-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
class Door(object):

    def __init__(self, alias=None, device_name=None):
        self._name = alias
        self._device_name = device_name


#-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
# T E M P O R A R Y   I M P L E M E N T A T I O N
#
# THIS IS USED FOR TEST PURPOSES ONLY. DO NOT USE IT OUTSIDE SARDANA TESTS
#-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
class Sardana(object):

    def __init__(self, sardana_db , name, device_name=None):
        self._sardana_db = sardana_db
        self._name = name
        self._device_name = device_name
        self._pools = []
        self._macroservers = []
        self._init()

    def _init(self):
        if not self._device_name:
            return
        self._pools = []
        self._macroservers = []
        dev_name = self._device_name
        db = self.get_database()
        cache = db.cache()
        dev_info = cache.devices()[dev_name]
        dev_class_name = dev_info.klass().name()
        if dev_class_name == "Pool":
            pass
        elif dev_class_name == "MacroServer":
            ms_dev_name = dev_name
            ms_prop_list = map(str.lower, db.get_device_property_list(ms_dev_name, "*"))
            ms_props = db.get_device_property(ms_dev_name, ms_prop_list)
            ms_name = dev_info.server().serverInstance()
            ms_alias = dev_info.alias()
            ms = MacroServer(self, ms_name, ms_props.get("macropath"), ms_props.get("poolnames"),
                             ms_props.get("version"), ms_alias, ms_dev_name)
            self._macroservers.append(ms)
            for pool_dev_name in ms_props.get("poolnames", ()):
                pool_prop_list = map(str.lower, db.get_device_property_list(pool_dev_name, "*"))
                pool_props = db.get_device_property(pool_dev_name, pool_prop_list)
                pool_dev_info = cache.devices()[pool_dev_name]
                pool_name = pool_dev_info.server().serverInstance()
                pool_alias = pool_dev_info.alias()
                pool = Pool(self, pool_name, pool_props.get("poolpath"), pool_props.get("version"), pool_alias, pool_dev_name)
                self._pools.append(pool)

    def get_name(self):
        return self._name

    def set_device_name(self, device_name):
        self._device_name = device_name
        self._init()

    def get_device_name(self):
        return self._device_name

    def get_pools(self):
        return self._pools

    def get_macro_servers(self):
        return self._macro_servers

    def create_pool(self, name, poolpath, version, alias=None, device_name=None):
        try:
            return self._create_pool(name, poolpath, version, alias=alias, device_name=device_name)
        except:
            db = self.get_database()
            db.delete_device(device_name)
            raise

    def _create_pool(self, name, poolpath, version, alias=None, device_name=None):
        db = self.get_database()
        info = PyTango.DbDevInfo()
        info.name = device_name
        info._class = "Pool"
        info.server = "Pool/" + name
        db.add_device(info)
        if alias:
            db.put_device_alias(device_name, alias)

        db.put_device_property(device_name, {"PoolPath" : poolpath, "Version": version})
        pool = Pool(self, name, poolpath, version, alias=alias, device_name=device_name)
        self._pools.append(pool)
        db.cache().refresh()
        return pool

    def create_macroserver(self, name, macropath, pool_names, version, alias=None, device_name=None):
        try:
            return self._create_macroserver(name, macropath, pool_names, version, alias=alias, device_name=device_name)
        except:
            db = self.get_database()
            db.delete_device(device_name)
            raise

    def _create_macroserver(self, name, macropath, pool_names, version, alias=None, device_name=None):
        db = self.get_database()
        info = PyTango.DbDevInfo()
        info.name = device_name
        info._class = "MacroServer"
        info.server = "MacroServer/" + name
        db.add_device(info)
        if alias:
            db.put_device_alias(device_name, alias)

        db.put_device_property(device_name, {"MacroPath" : macropath, "Version": version, "PoolNames":pool_names})
        ms = MacroServer(self, name, macropath, pool_names, version, alias=alias, device_name=device_name)
        self._macroservers.append(ms)
        db.cache().refresh()
        return ms

    def remove_pool(self):
        pass

    def remove_macroserver(self):
        pass

    def get_database(self):
        return self._sardana_db.get_database()

#-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
# T E M P O R A R Y   I M P L E M E N T A T I O N
#
# THIS IS USED FOR TEST PURPOSES ONLY. DO NOT USE IT OUTSIDE SARDANA TESTS
#-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
class DatabaseSardana(object):
    """A class containning all sardanas for a single database"""

    def __init__(self, db):
        assert(db is not None)
        self._db = db
        self.refresh()

    def refresh(self):
        self._sardanas = sardanas = {}
        services = self._db.get_service_list("Sardana/.*")
        for service, dev in services.items():
            service_type, service_instance = service.split("/", 1)
            try:
                sardanas[service_instance] = Sardana(self, service_instance, dev)
            except:
                pass

    def create_sardana(self, name, device_name):
        if self._sardanas.has_key(name):
            raise Exception("Sardana '%s' already exists" % name)
        self._db.register_service("Sardana", name, device_name)
        sardana = Sardana(self, name)
        self._sardanas[name] = sardana
        return sardana

    def remove_sardana(self, name):
        try:
            self._sardanas.pop(name)
        except KeyError:
            raise Exception("Sardana '%s' does NOT exist" % name)
        self._db.unregister_service("Sardana", name)

    def get_sardanas(self):
        return self._sardanas

    def get_sardana(self, name):
        return self._sardanas[name]

    def get_database(self):
        return self._db

#-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
# T E M P O R A R Y   I M P L E M E N T A T I O N
#
# THIS IS USED FOR TEST PURPOSES ONLY. DO NOT USE IT OUTSIDE SARDANA TESTS
#-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
class SardanaManager(Singleton, Logger):

    def __init__(self):
        """ Initialization. Nothing to be done here for now."""
        pass

    def init(self, *args, **kwargs):
        """Singleton instance initialization.
           **For internal usage only**"""
        name = self.__class__.__name__
        self.call__init__(Logger, name)
        self._db_sardanas = {}

    def _get_db_sardana(self, db=None):
        if db is None:
            import taurus
            db = taurus.Database()
        db_sardana = self._db_sardanas.get(db)
        if db_sardana is None:
            db_sardana = DatabaseSardana(db)
        return db_sardana

    def create_sardana(self, name, device_name, db=None):
        return self._get_db_sardana(db).create_sardana(name, device_name)

    def remove_sardana(self, name, db=None):
        self._get_db_sardana(db).remove_sardana(name)

    def get_sardanas(self, db=None):
        return self._get_db_sardana(db).get_sardanas()

    def get_sardana(self, name, db=None):
        return self._get_db_sardana(db).get_sardana(name)

    def get_hosts(self):
        return ["localhost"] + ["controls%02d" % i for i in range(5)]

    def get_level_range(self):
        return 1, 200

    def has_localhost_starter(self):
        import socket
        return socket.gethostname() in self.get_hosts()

    @classmethod
    def get_default_pool_path(cls):
        pathList = []
        pathList.append("/homelocal/sicilia/lib/poolcontrollers")
        pathList.append("/homelocal/sicilia/lib/python/site-packages/poolcontrollers")
        return pathList

    @classmethod
    def get_default_ms_path(cls):
        pathList = []
        pathList.append("/homelocal/sicilia/lib/python/site-packages/macroserver/macros")
        return pathList





