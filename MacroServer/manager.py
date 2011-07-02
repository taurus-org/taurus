"""This module contains the class definition for the MacroServer main manager"""

import os, re, copy
import operator, types

from taurus.core import ManagerState
import taurus.core.util

import pool
import motion
from modulemanager import ModuleManager
from macromanager import MacroManager
from typemanager import TypeManager
from envmanager import EnvironmentManager
from parameter import ParamType

from exception import UnknownEnv

class MacroServerManager(taurus.core.util.Singleton, taurus.core.util.Logger):
    """The MacroServer manager class. It is designed to be a singleton for the
    entire application.
    This Manager also exports the interface of the MacroManager, TypeManager and
    ModuleManager (in that order of priority)"""
    
    All = ParamType.All
    
    def __init__(self, *args):
        """ Initialization. Nothing to be done here for now."""
        pass

    def init(self, *args, **kwargs):
        """Singleton instance initialization."""
        name = self.__class__.__name__
        self._state = ManagerState.UNINITIALIZED
        self.call__init__(taurus.core.util.Logger, name)

        # dictionary for registered doors
        # dict<string, PyTango.Device_3Impl> where:
        #  - key: door device name
        #  - value: door device object
        self._doors = taurus.core.util.CaselessDict()
        
        # maximum number of parallel macros
        self._max_parallel_macros = 5

        self._pool_list_obj = taurus.core.util.ListEventGenerator('PoolList')
        self._door_list_obj = taurus.core.util.ListEventGenerator('DoorList')
        
        self.reInit(*args)

    def reInit(self, pools=None, macro_path=None, env_db=None, max_parallel=0):
        """(Re)initializes the manager"""
        if self._state == ManagerState.INITED:
            return
        
        taurus_manager = taurus.core.TaurusManager()
        taurus_manager.reInit()
        #taurus_manager.setSerializationMode(taurus.core.TaurusSerializationMode.Serial)
        factory = taurus_manager.getFactory("tango")()
        factory.registerDeviceClass("Pool", pool.Pool)
        for klass_name, klass in zip(pool.HardwareObjTypes, pool.HardwareObjTypeClasses):
            factory.registerDeviceClass(klass_name, klass)
        
        if not pools is None:
            self.setPools(pools)

        pool_thread_size = max_parallel or self._max_parallel_macros
        self._macro_thread_pool = taurus.core.util.ThreadPool(name="MSTP",
                                                            parent=self,
                                                            Psize=pool_thread_size, 
                                                            Qsize=50)

        if max_parallel > 0:
            self.setMaxParallelMacros(max_parallel)
        
        ModuleManager().reInit()
        TypeManager().reInit()
        basetypes_dir = os.path.dirname(os.path.abspath(__file__))
        TypeManager().reloadTypeModule('basetypes', path=[basetypes_dir])
        MacroManager().reInit()
        EnvironmentManager().reInit()
        EnvironmentManager().setEnvironment(env_db)
        
        if not macro_path is None:
            MacroManager().setMacroPath(macro_path)
        
        self._state = ManagerState.INITED
    
    def cleanUp(self):
        """Cleans the manager"""
        if self._state == ManagerState.CLEANED:
            return
        
        # wait for thread pool thread to finish
        self._macro_thread_pool.join()
        self._macro_thread_pool = None
        
        MacroManager().cleanUp()
        TypeManager().cleanUp()
        ModuleManager().cleanUp()

        #taurus.core.TaurusManager().cleanUp()
        
        self._pools = None
                
        self._state = ManagerState.CLEANED

    def getMaxParallelMacros(self):
        return self._macro_thread_pool.size
    
    def setMaxParallelMacros(self, n):
        assert n>0, "max parallel macros number must be > 0"
        self._macro_thread_pool.size = n
       
    def addJob(self, job, callback=None, *args, **kw):
        self._macro_thread_pool.add(job, callback, *args, **kw)

    def setPools(self, pool_names):
        """Registers a new list of device pools in this manager"""

        # dict<str, Pool>
        # key   - device name (case insensitive)
        # value - Pool object representing the device name
        self._pools = taurus.core.util.CaselessDict()
        
        for name in pool_names:
            self.debug("Creating pool %s", name)
            p = taurus.Device(name)
            if p is None:
                self.error('Could not create Pool object for %s' % name)
                continue
            self._pools[name] = p
        
        self._firePoolEvent()

    def _firePoolEvent(self):
        """Helper method that fires event for the current existing pools"""
        pool_list = self.getPoolListStr()
        self.getPoolListObj().fireEvent(pool_list)
        return pool_list
    
    def getPoolListObj(self):
        """Returns the event generator object for the list of device pools"""
        return self._pool_list_obj
    
    def getPoolObj(self, pool_name):
        """Returns the device pool object corresponding to the given device name
        or None if no match is found."""
        return self._pools.get(pool_name)
    
    def getPoolListObjs(self):
        """Returns the list of device pool objects"""
        return self._pools.values()
    
    def getPoolListStr(self):
        """Returns the list of device pool names"""
        return self._pools.keys()

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # Door list related methods
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-    

    def _fireDoorListEvent(self):
        """Helper method that fires event for the current existing doors"""
        door_list = self.getDoorListStr()
        self.getDoorListObj().fireEvent(door_list)
        return door_list
    
    def getDoorListObj(self):
        """Returns the event generator object for the list of doors"""
        return self._door_list_obj
    
    def getDoorObj(self, door_name):
        """Returns the door object corresponding to the given device name
        or None if no match is found."""
        return self._doors.get(door_name)
    
    def getDoorListObjs(self):
        """Returns the list of door objects"""
        return self._doors.values()
    
    def getDoorListStr(self):
        """Returns the list of door names"""
        return self._doors.keys()

    def addDoor(self, door):
        door_name = door.get_name()
        self._doors[door_name] = door
        self._fireDoorListEvent()
    
    def removeDoor(self, door):
        door_name = door.get_name()
        del self._doors[door_name]
        self._fireDoorListEvent()
       
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # General object access methods
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    
    def getObj(self, name, type_class=All, subtype=All, pool=All):
        objs = self.findObjs(name, type_class, subtype, pool)
        if len(objs) == 0:
            return None
        if len(objs) > 1:
            raise AttributeError('More than one object named "%s" found' % name)
        return objs[0]

    def getObjs(self, names, type_class=All, subtype=All, pool=All):
        return self.findObjs(names, type_class, subtype, pool)

    def findObjs(self, param, type_class=All, subtype=All, pool=All):
        if isinstance(param, str):
            param = (param,)

        if type_class == MacroServerManager.All:
            type_name_list = self.getTypeListObj().read()
        else:
            if type(type_class) in types.StringTypes:
                type_name_list = (type_class,)
            else:
                type_name_list = type_class
        obj_list = []
        param = [ '^%s$' % x for x in param]
        re_objs = map(re.compile, param, len(param)*(re.IGNORECASE,))
        re_subtype = re.compile(subtype, re.IGNORECASE)
        for type_name in type_name_list:
            type_class_name = type_name
            if type_class_name.endswith('*'): 
               type_class_name = type_class_name[:-1] 
            type_inst = self.getTypeObj(type_class_name)
            if not type_inst.hasCapability(ParamType.ItemList):
                continue
            for name, obj in type_inst.getObjDict(pool=pool).items():
                for re_obj in re_objs:
                    if not re_obj.match(name) is None:
                        if subtype is MacroServerManager.All or re_subtype.match(obj.getType()):
                            obj_list.append(obj)
                            break
        return obj_list

    def getMotion(self, elems, motion_source=None, read_only=False, cache=True):
        if not motion_source:
            motion_source = self.getPoolListObjs()
        return motion.Motion(elems, motion_source)
    
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # Macro, Type and Module Manager Interfaces
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    
    def __getattr__(self, name):
        try:
            return getattr(MacroManager(), name)
        except:
            try:
                return getattr(TypeManager(), name)
            except:
                try:
                    return getattr(ModuleManager(), name)
                except:
                    try:
                        return getattr(EnvironmentManager(), name)
                    except:
                        raise AttributeError("No Manager has attribute %s" % name)
