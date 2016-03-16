import imp
import importlib
from sys import modules
from taurus.core.util.singleton import Singleton


class ModuleManager(Singleton):
    '''ModuleManager class is an helper to manager the python modules.
       This class has methods to import, reload, and block python modules.
    '''

    def __init__(self):
        self._modules = {}

    def _deleteModule(self, modname):
        ''' Remove the given module name from the exported python modules

        :param modname: Module name
        :type modname: str
        '''
        try:
            thismod = modules[modname]
        except KeyError:
            # This module is not imported
            raise ValueError(modname)
        these_symbols = dir(thismod)

        del modules[modname]
        for mod in modules.values():
            try:
                delattr(mod, modname)
            except AttributeError:
                pass

    def blockModule(self, modname):
        ''' Remplace the given module name by None. inhibits the module.

        :param modname: Module name
        :type modname: str
        '''
        if self._modules.get(modname) is None:
            self.importModule(modname)

        if modules[modname] is not None:
            _mod = {}
            _mod['mod'] = modules[modname]
            _mod['submod'] = []
            # Delete and block submodules
            for mod in modules.keys():
                if mod.find(modname) != -1:
                    _mod['submod'].append((mod, modules[mod]))
                    self._deleteModule(mod)
                    modules[mod] = None
            # Delete and block the module
            self._deleteModule(modname)
            modules[modname] = None
            self._modules[modname] = _mod

    def reloadModule(self, modname):
        '''Reload the given module name.

        :param modname: Module name
        :type modname: str
        '''
        if self._modules.get(modname) is None:
            msg = 'ModuleManager: Trying to reload a not imported module, %s'\
                  % (modname)
            print msg
            return
        # Reload the submodules
        for subname, submod in self._modules[modname]['submod']:
            modules[subname] = submod
        # Reload the module
        modules[modname] = self._modules[modname]['mod']
        imp.reload(self._modules[modname]['mod'])

    def importModule(self, modname):
        ''' Import the given module name.

        :param modname: Module name
        :type modname: str
        '''
        try:
            mod = __import__(modname)
            modules[modname] = mod
            _mod = {}
            _mod['mod'] = mod
            _mod['submod'] = []
            self._modules[modname] = _mod
        except ImportError:
            print 'Imposible to import the module %s' % (modname)

    def _getModuleDict(self, modname):
        ''' Return a dictionary with the given module name and its submodels
            if exists or None.

        :param modname: Module name
        :type modname: str

        :return dictionary
        '''
        return self._modules.get(modname)

    def getModule(self, modname):
        ''' Return a module of the given module name if exists or None.

        :param modname: Module name
        :type modname: str

        :return python module
        '''
        d = self._getModuleDict(modname)
        if d is None:
            return None
        return d['mod']

#---------------------Just 4 Test-----------------------------------------


def blockPyTango(modmanager):
    import taurus
    from taurus.core.taurusmanager import TaurusManager
    tm = TaurusManager()
    print '\n-*-*-*-*-*- Block PyTango'
    modmanager.blockModule('PyTango')
    taurus.check_dependencies()
    print '\n -- Taurus plugins'
    print tm.buildPlugins()


def reloadPyTango(modmanager):
    import taurus
    from taurus.core.taurusmanager import TaurusManager
    tm = TaurusManager()
    print '\n-*-*-*-*-*- Reload PyTango'
    modmanager.reloadModule('PyTango')
    taurus.check_dependencies()
    print '\n -- Taurus plugins'
    print tm.buildPlugins()


def test():
    modmanager = ModuleManager()
    blockPyTango(modmanager)
    reloadPyTango(modmanager)
    blockPyTango(modmanager)


if __name__ == '__main__':
    test()
