import sys, os, imp

from taurus.core import ManagerState
import taurus.core.util

class ModuleManager(taurus.core.util.Singleton, taurus.core.util.Logger):
    
    def __init__(self):
        """ Initialization. Nothing to be done here for now."""
        pass

    def init(self, *args, **kwargs):
        """Singleton instance initialization."""
        name = self.__class__.__name__
        self._state = ManagerState.UNINITIALIZED
        self.call__init__(taurus.core.util.Logger, name)
        self._module_list_obj = taurus.core.util.ListEventGenerator('ModuleList')
        self.reInit()
    
    def reInit(self):
        if self._state == ManagerState.INITED:
            return
        
        # dict<str, module>
        # key   - module name (without path and without extension)
        # value - python module object reference
        self._modules = {}
        
        self._state = ManagerState.INITED
    
    def cleanUp(self):
        if self._state == ManagerState.CLEANED:
            return

        self.unloadModules()

        self._modules = None

        self._state = ManagerState.CLEANED
    
    def reloadModule(self, module_name, path=None):
        """Loads/reloads the given module name"""

        # Store how was the old list of modules to see if an event needs to be
        # fired
        old_modules = self.getModuleListStr()

        self.unloadModule(module_name)
        
        m, trace, file = None, None, None
        try:
            file, pathname, desc = imp.find_module(module_name, path)
            self.info("(re)loading module %s...", module_name)
            m = imp.load_module(module_name, file, pathname, desc)
        except Exception, e:
            self.info("failed to (re)load module %s", module_name)
            self.debug("Error detail:", exc_info=1)
            raise e
        finally:
            if file:
                file.close()
        
        
        self._modules[module_name] = m
        
        new_modules = self.getModuleListStr()
        
        if old_modules != new_modules:
            self._fireModuleEvent(new_modules)
        
        return m
    
    def unloadModule(self, module_name, fire_event=True):
        """Unloads the given module name"""
        if self._modules.has_key(module_name):
            self.debug("unloading module %s" % module_name)
            assert(sys.modules.has_key(module_name))
            self._modules.pop(module_name)
            del sys.modules[module_name]
            if fire_event:
                self._fireModuleEvent()
            
    def unloadModules(self, module_list = None, fire_event=True):
        """Unloads the given module name"""
        modules = module_list or self._modules.keys()
        for module in modules:
            self.unloadModule(module, False)
        if fire_event:
            self._fireModuleEvent()
    
    def getModule(self, module_name):
        """Returns the module object for the given module name"""
        m = self._modules.get(module_name)
        if m is None:
            m = self.reloadModule(module_name)
        return m

    def getModuleListStr(self):
        l = self._modules.keys().sort()
        return l
    
    def _fireModuleEvent(self, data=None):
        """Helper method that fires event for the current existing macros"""
        module_list = data or self.getModuleListStr()
        self._module_list_obj.fireEvent(module_list)
        return module_list
    