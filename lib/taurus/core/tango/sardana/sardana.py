#!/usr/bin/env python

#############################################################################
##
## This file is part of Taurus, a Tango User Interface Library
## 
## http://www.tango-controls.org/static/taurus/latest/doc/html/index.html
##
## Copyright 2011 CELLS / ALBA Synchrotron, Bellaterra, Spain
## 
## Taurus is free software: you can redistribute it and/or modify
## it under the terms of the GNU Lesser General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
## 
## Taurus is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU Lesser General Public License for more details.
## 
## You should have received a copy of the GNU Lesser General Public License
## along with Taurus.  If not, see <http://www.gnu.org/licenses/>.
##
#############################################################################

"""The sardana submodule. It contains specific part of sardana"""

__all__ = ["Pool", "MacroServer", "Door", "Sardana", "SardanaManager",
           "PoolElementType", "ControllerClassInfo", "ControllerInfo"]

__docformat__ = 'restructuredtext'

import socket

import time
import taurus.core.util

PoolElementType = taurus.core.util.Enumeration("PoolElementType",
    ("0D", "1D", "2D", "Communication", "CounterTimer", "IORegister", 
      "Motor","PseudoCounter", "PseudoMotor"))

class PropertyInfo():
    def __init__(self, name, type, format, default_value=None):
        self._name = name
        self._type = type
        self._format = format
        self._default_value=default_value
        
    def get_name(self):
        return self._name

    def get_type(self):
        return self._type
    
    def get_format(self):
        return self._format
    
    def get_default_value(self):
        return self._default_value
    
        
class ControllerClassInfo(object):
    
    def __init__(self, name, type, library):
        self._name = name
        self._type = type
        self._library = library
        
    def get_max_elements(self):
        return 123
    
    def get_name(self):
        return self._name
    
    def get_model(self):
        # fake data ###############
        return "Model of "+ self._name 
    
    def get_icon(self):
        # fake data ###############
        import taurus.qt.qtgui.resource
        
        return taurus.qt.qtgui.resource.getIcon(":/designer/extra_motor.png")
    
    def get_organization(self):
        # fake data ###############
        return "Organization of "+ self._name 
    
    def get_description(self):
        #fake data############
        descr="This is description of "
        for i in range(20):
            descr=descr + " and " +self._name
        ####################
        return descr
    
    def get_family(self):
        # fake data ###############
        return "Family of "+ self._name 
    
    def get_properties(self):
        properties = []
        # fake data ######################
        properties.append(PropertyInfo("name", "string", "0D", "deviceName"))
        properties.append(PropertyInfo("number0", "integer", "0D", 5))
        properties.append(PropertyInfo("boollll0", "boolean", "0D", False))
        properties.append(PropertyInfo("boollll0", "boolean", "0D", True)) 
        properties.append(PropertyInfo("boollll0", "boolean", "0D", False))     
        properties.append(PropertyInfo("number1", "float", "0D", 3.5))
        properties.append(PropertyInfo("string2", "string", "0D", "hehe"))
        properties.append(PropertyInfo("tableIntegerD1", "integer", "1D", [1,2,3]))
        properties.append(PropertyInfo("tablestringD1", "string", "1D", ["aaaa","bbb","ccc"]))
        properties.append(PropertyInfo("tablefloatD1", "float", "1D", [1.0,2.5,3.6]))
        properties.append(PropertyInfo("tablebooleanD1", "boolean", "1D", [True,False,True,False]))
        properties.append(PropertyInfo("tablebleintegerD1", "integer", "1D", [1,2,3]))
        properties.append(PropertyInfo("tablebooleanD2", "boolean", "2D",[ [True,False,True],[True,True,True],[False,False,False] ]))
        properties.append(PropertyInfo("tableinteger2", "integer", "2D",[ [1,2,3],[11,22,33],[-10,-20,-30] ]))
        properties.append(PropertyInfo("tablefloatD2", "float", "2D",[ [0.5,0.6,0.8],[0.4,0.0,0.333333],[-0.1111,1,123123.6] ]))
        properties.append(PropertyInfo("tablestringD2", "string", "2D",[ ["aaaa","bbb","ccc"],["aaaa2","bbb2","ccc2"],["aaaa3","bbb3","ccc3"] ]))
    
        return properties
    
    def get_controller_type(self):
        return self._type


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
        return False

    def get_icon(self):
        return self._ctrl_class_info.get_icon()
    
        return properties

class Pool(object):
    
    def __init__(self, name, poolpath, version, alias=None, device_name=None):
        self._name = name
        self._poolpath = poolpath
        self._version = version
        self._alias = alias
        self._device_name = device_name
        
    def starter_run(self, host, level=1):
        time.sleep(3)
        return True
    
    def get_name(self):
        return self._name
    
    def local_run(self):
        time.sleep(3)
        return True
    
    def get_element_types(self):
        return sorted(PoolElementType.keys())

    def get_controller_class_infos(self):
        #fake data ########################
        data = []
        for i in range(5):
            data.append(ControllerClassInfo("motorController"+str(i), PoolElementType.Motor, None))
        for i in range(5):
            data.append(ControllerClassInfo("counterTimerController"+str(i), PoolElementType.CounterTimer, None))
            
        return data

    def get_controller_infos(self):
        ctrl_classes = self.get_controller_class_infos()
        data = []
        for i in range(2):
            data.append(ControllerInfo("My_motor_ctrl_"+str(i), ctrl_classes[i]))
        for i in range(2):
            data.append(ControllerInfo("My_ct_ctrl_"+str(i), ctrl_classes[i+5]))
        return data
 
    def create_controller(self,controller_class_info, name, properties ):
        pass
    
    def create_element(self, controller_name, name, axis):
        pass


class MacroServer(object):
    
    def __init__(self, name, macropath, version, alias=None, device_name=None):
        self._name = name
        self._macropath = macropath
        self._version = version
        self._alias = alias
        self._device_name = device_name
        
    def create_door(self, alias, device_name):
        return Door(alias=alias, device_name=device_name)

    def remove_door(self, device_name):
        pass
    
    def starter_run(self, host, level=1):
        time.sleep(3)
        return True
        
    def local_run(self):
        time.sleep(3)
        return True

class Door(object):
    
    def __init__(self, alias=None, device_name=None):
        self._name = alias
        self._device_name = device_name
    

class Sardana(object):
    
    def __init__(self, name, device_name):
        self._name = name
        self._device_namee = device_name
        
    def get_name(self):
        return self._name
        
    def get_device_name(self):
        return self._device_name
        
    def get_pools(self):
        # fake data #
        fake_pools = []
        for i in range(5):
            fake_pools.append(Pool(self.get_name()+"_pool"+str(i),[],"0."+str(i),"Pool_nr"+str(i), self.get_name()+"/Pool/"+str(i)))
        #
        return fake_pools
    
    def get_macro_servers(self):
        return [MacroServer("noname",[],"0.4","MS_noname", "none/MS/1")]
        
    def create_pool(self, name, poolpath, version, alias=None, device_name=None):
        return Pool(name, poolpath, version, alias=alias, device_name=device_name)
        
    def create_macroserver(self, name, macropath, version, alias=None, device_name=None):
        
        return MacroServer(name, macropath, version, alias=alias, device_name=device_name)
        
    def remove_pool(self):
        pass
        
    def remove_macroserver(self):
        pass


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
            sardanas[service_instance] = Sardana(service_instance, dev)
    
    def create_sardana(self, name, device_name):
        if self._sardanas.has_key(name):
            raise Exception("Sardana '%s' already exists" % name)
        self._db.register_service("Sardana", name, device_name)
        sardana = Sardana(name, device_name)
        self._sardanas[name] = sardana
        return sardana
        
    def remove_sardana(self, name):
        try:
            sardana = self._sardanas.pop(name)
        except KeyError:
            raise Exception("Sardana '%s' does NOT exist" % name)
        self._db.unregister_service("Sardana", name)

    def get_sardanas(self):
        return self._sardanas
    
    def get_sardana(self, name):
        return self._sardanas[name]



class SardanaManager(taurus.core.util.Singleton, taurus.core.util.Logger):
    
    def __init__(self):
        """ Initialization. Nothing to be done here for now."""
        pass

    def init(self, *args, **kwargs):
        """Singleton instance initialization.
           **For internal usage only**"""
        name = self.__class__.__name__
        self.call__init__(taurus.core.util.Logger, name)
        self._db_sardanas = {}
        
    def _get_db_sardana(self, db=None):
        if db is None:
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
    
    
    
        
    