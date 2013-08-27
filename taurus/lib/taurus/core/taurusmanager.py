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

"""This module contains the taurus base manager class"""

__all__ = ["TaurusManager"]

__docformat__ = "restructuredtext"

import os
import imp
import atexit

from .util.singleton import Singleton
from .util.log import Logger
from .util.threadpool import ThreadPool

from .taurusbasetypes import OperationMode, ManagerState, TaurusSerializationMode
from .taurusdatabase import TaurusDatabase
from .taurusdevice import TaurusDevice
from .taurusattribute import TaurusAttribute
from .taurusconfiguration import TaurusConfiguration
from .taurusexception import TaurusException
from .taurusfactory import TaurusFactory


class TaurusManager(Singleton, Logger):
    """A :class:`taurus.core.util.singleton.Singleton` class designed to provide Taurus management.
    
       Example::
       
           >>> import taurus.core.taurusmanager
           >>> manager = taurus.core.taurusmanager.TaurusManager()
           >>> print manager == taurus.core.taurusmanager.TaurusManager()
           True
    """
    PLUGIN_KEY = "__taurus_plugin__"
    
    DefaultSerializationMode = TaurusSerializationMode.Concurrent
    default_scheme = "tango"

    def __init__(self):
        """ Initialization. Nothing to be done here for now."""
        pass

    def init(self, *args, **kwargs):
        """Singleton instance initialization. 
           For internal usage only. Do **NOT** call this method directly"""
        self._state = ManagerState.UNINITIALIZED
        self.call__init__(Logger)
        self.reInit()
        atexit.register(self.cleanUp)

    def reInit(self):
        """Reinitialization"""
        if self._state == ManagerState.INITED:
            return
        
        self.trace("reInit()")
        this_path = os.path.abspath(__file__)
        self._this_path = os.path.dirname(this_path)
        self._operation_mode = OperationMode.ONLINE
        self._serialization_mode = self.DefaultSerializationMode
        if self._serialization_mode == TaurusSerializationMode.Concurrent:
            self._thread_pool = ThreadPool(name="TaurusTP",
                                           parent=self,
                                           Psize=5,
                                           Qsize=1000)
        else:
            self._thread_pool = None
        self._plugins = None
        
        self._initial_default_scheme = self.default_scheme
        
        self._state = ManagerState.INITED

    def cleanUp(self):
        """Cleanup"""
        if self._state == ManagerState.CLEANED:
            return
        self.trace("cleanUp()")
        
        if self._plugins is None:
            return
        self.trace("[TaurusManager] cleanUp")
        for f_scheme, f in self._plugins.items():
            f().cleanUp()
        self._plugins = None
        
        self._thread_pool.join()
        self._thread_pool = None
        
        self._state = ManagerState.CLEANED

    def addJob(self, job, callback=None, *args, **kw):
        """Add a new job (callable) to the queue. The new job will be processed
        by a separate thread
        
        :param job: (callable) a callable object 
        :param callback: (callable) called after the job has been processed
        :param args: (list) list of arguments passed to the job
        :param kw: (dict) keyword arguments passed to the job
        """
        if self._serialization_mode == TaurusSerializationMode.Concurrent:
            if not hasattr(self, "_thread_pool") or self._thread_pool is None:
                self.info("Job cannot be processed.")
                self.debug("The requested job cannot be processed. Make sure this manager is initialized")
                return
            self._thread_pool.add(job, callback, *args, **kw)
        else:
            job(*args, **kw)
    
    def setSerializationMode(self, mode):
        """Sets the serialization mode for the system.
        
        :param mode: (TaurusSerializationMode) the new serialization mode"""
        self._serialization_mode = mode
    
    def getSerializationMode(self):
        """Gives the serialization operation mode.
        
        :return: (TaurusSerializationMode) the current serialization mode"""
        return self._serialization_mode
    
    def setOperationMode(self, mode):
        """Sets the operation mode for the system.
        
        :param mode: (OperationMode) the new operation mode"""
        self.debug("Setting operation mode to %s" % OperationMode.whatis(mode))
        if mode == OperationMode.OFFLINE:
            self._initial_default_scheme = self.default_scheme
            self.default_scheme = "simulation"
        else:
            self.default_scheme = self._initial_default_scheme
            
        self._operation_mode = mode
        for plugin in self.getPlugins().values():
            plugin().setOperationMode(mode)
        
    def getOperationMode(self):
        """Gives the current operation mode.
        
        :return: (OperationMode) the current operation mode"""
        return self._operation_mode
        
    def getDefaultFactory(self):
        """Gives the default factory.
        
        :return: (taurus.core.taurusfactory.TaurusFactory) the default taurus factory
        """
        return self.getPlugins().get(self.default_scheme, None)
        
    def getPlugins(self):
        """Gives the information about the existing plugins
        
        :return: (dict<str, class taurus.core.taurusfactory.TaurusFactory>)the list of plugins
        """
        if self._plugins is None:
            self._plugins = self._build_plugins()
        return self._plugins
        
    def getFactory(self, scheme=None):
        """Gives the factory class object supporting the given scheme
        
        :param scheme: (str or None) the scheme. If None the default scheme is used
        :return: (taurus.core.taurusfactory.TaurusFactory or None) the factory class object for the 
                 given scheme or None if a proper factory is not found
        """
        if scheme is None:
            return self.getDefaultFactory()
        return self.getPlugins().get(scheme)

    def getObject(self, cls, name):
        """Gives the object for the given class with the given name
        
        :param cls: (taurus.core.taurusmodel.TaurusModel) object class
        :param name: (str) the object name
        :return: (taurus.core.taurusmodel.TaurusModel or None) a taurus model object
        """
        factory = self._get_factory(name)
        if factory is None: return
        return factory.getObject(cls, name)
    
    def findObject(self, absolute_name):
        """Finds the object with the given name
        
        :param absolute_name: (str) the object name
        :return: (taurus.core.taurusmodel.TaurusModel or None) the taurus model object or None if 
                 no suitable name found
        """
        factory = self._get_factory(absolute_name)
        if factory is None: return
        return factory.findObject(absolute_name)

    def findObjectClass(self,absolute_name):
        """Finds the object class for the given object name
        
        :param absolute_name: (str) the object name
        :return: (class taurus.core.taurusmodel.TaurusModel or None) the taurus model class object or 
                 None if no suitable name found
        """
        factory = self._get_factory(absolute_name)
        if factory is None: return
        return factory.findObjectClass(absolute_name)
    
    def getDatabase(self, name):
        """Returns a database object for the given name
        
        :param name: (str) database name
        :return: (taurus.core.taurusdatabase.TaurusDatabase) the database for the given name
        """
        return self.getObject(TaurusDatabase, name)

    def getDevice(self, name):
        """Returns a device object for the given name
        
        :param name: (str) device name
        :return: (taurus.core.taurusdevice.TaurusDevice) the device for the given name
        """
        return self.getObject(TaurusDevice, name)
    
    def getAttribute(self, name):
        """Returns a attribute object for the given name
        
        :param name: (str) attribute name
        :return: (taurus.core.taurusattribute.TaurusAttribute) the attribute for the given name
        """
        return self.getObject(TaurusAttribute, name)
    
    def getConfiguration(self, name):
        """Returns a configuration object for the given name
        
        :param name: (str) configuration name
        :return: (taurus.core.taurusconfiguration.TaurusConfiguration) the configuration for the given name
        """
        return self.getObject(TaurusConfiguration, name)
        
    def _get_factory(self, name):
        scheme = self._get_scheme(name)
        if scheme is None: return
        try:
            return self.getPlugins()[scheme]()
        except:
            raise TaurusException('Invalid scheme "%s"'%scheme)

    def _get_scheme(self, name):
        try:
            return name[:name.index('://')]
        except ValueError, e:
            return self.default_scheme
        
    def _get_schema(self, name):
        raise DeprecationWarning('_get_schema is deprecated. Use _get_scheme instead')

    def _build_plugins(self):
        plugin_classes = self._get_plugin_classes()
        plugins = {}
        for plugin_class in plugin_classes:
            schemes = list(plugin_class.schemes)
            for scheme in schemes:
                if plugins.has_key(scheme):
                    k = plugins[scheme]
                    self.warning("Conflicting plugins: %s and %s both implement " \
                                 "scheme %s. Will keep using %s" % (k.__name__,
                                 plugin_class.__name__, scheme, k.__name__) )
                else:
                    plugins[scheme] = plugin_class
        return plugins
        
    def _get_plugin_classes(self):
        import taurusfactory
        upgrade_classes = []
        
        elems = os.listdir(self._this_path)
        dirs = []
        for elem in elems:
            if elem.startswith('.') or elem.startswith("_"):
                continue
            elem = os.path.join(self._this_path, elem)
            if not os.path.isdir(elem):
                continue
            plugin_file = os.path.join(elem, self.PLUGIN_KEY)
            if not os.path.exists(plugin_file):
                continue
            if not os.path.exists(os.path.join(elem, '__init__.py')):
                continue
            dirs.append(elem)
        
        plugins = []
        
        full_module_names = ['taurus.core.%s'%d.split(os.path.sep)[-1] for d in dirs]
        from taurus import tauruscustomsettings
        full_module_names.extend(getattr(tauruscustomsettings,'EXTRA_SCHEME_MODULES',[]))
        
        for full_module_name in full_module_names:
            try:
                m = __import__(full_module_name, fromlist=['*'], level=0)
            except Exception, imp1:
                # just in case we are in python 2.4
                try:
                    m = __import__(full_module_name, globals(), locals(), ['*'])
                except:
                    self.debug('Failed to inspect %s' % (full_module_name))
                    self.debug('Details:', exc_info=1)
                    continue
            for s in m.__dict__.values():
                plugin = None
                try:
                    if issubclass(s, TaurusFactory) and \
                       issubclass(s, Singleton):
                        if hasattr(s, 'schemes') :
                            schemes = getattr(s, 'schemes')
                            if len(schemes):
                                plugin = s
                            else:
                                scheme = self._find_scheme(s)
                                if not scheme is None:
                                    s.schemes = (scheme,)
                                    plugin = s
                except:
                    pass
                if not plugin is None:
                    self.debug('Found plugin %s' % plugin.__name__)
                    plugins.append(plugin)
        return plugins
        
    def _find_scheme(self, factory_class):
        class_name = factory_class.__name__
        for i in xrange(1,len(class_name)):
            if class_name[i].isupper():
                return class_name[:i].lower()

    def applyPendingOperations(self, ops):
        """Executes the given operations
        
        :param ops: the sequence of operations
        :type ops: sequence<taurus.core.taurusoperation.TaurusOperation>"""
        for o in ops:
            o.execute()
            
    def changeDefaultPollingPeriod(self, period):
        self.getFactory()().changeDefaultPollingPeriod(period)
        # todo: go through all known plugin factories and change their polling
        # period

    def __str__name__(self, name):
        return '{0}({1})'.format(self.__class__.__name__, name)
    
    def __str__(self):
        return self.__str__name__("")

    def __repr__(self):
        return self.__str__name__("")
        
if __name__ == '__main__':
    manager = TaurusManager()
    print manager.getPlugins()
