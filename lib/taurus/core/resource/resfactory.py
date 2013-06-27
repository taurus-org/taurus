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

"""
simfactory.py: 
"""

import os, imp, operator, types

from taurus import Factory, Database, Manager
from taurus.core.taurusexception import TaurusException
from taurus.core.taurusbasetypes import OperationMode, MatchLevel, \
    TaurusAttrValue, TaurusEventType
from taurus.core.util.singleton import Singleton
from taurus.core.util.log import Logger
from taurus.core.taurusfactory import TaurusFactory
from taurus.core.taurusattribute import TaurusAttribute
from taurus.core.taurusdevice import TaurusDevice
from taurus.core.taurusdatabase import TaurusDatabase
from taurus.core.taurusconfiguration import TaurusConfiguration

class ModuleDict(dict):
    def __init__(self, mod):
        self.__mod = mod

    def __getitem__(self, name):
        return self.__mod.__getattribute__(name)

class ResourcesFactory(Singleton, TaurusFactory, Logger):
    """A Singleton class designed to provide Simulation related objects."""

    #: the list of schemes that this factory supports. For this factory: 'res' 
    #: and 'resources' are the supported schemes
    schemes = ("res", "resource",)
    
    #: the default resource file name
    DftResourceName = 'taurus_resources.py'
    
    #: priority for the default resource
    DftResourcePriority = 10
    
    def __init__(self):
        """ Initialization. Nothing to be done here for now."""
        pass

    def init(self, *args, **kwargs):
        """Singleton instance initialization.
           **For internal usage only**"""
        name = self.__class__.__name__
        self.call__init__(Logger, name)
        self.call__init__(TaurusFactory)
        
        self._resource_map = {}
        self._resource_priority = {}
        self._resource_priority_keys = []
        self._resource_count = 0
        
    def reloadResource(self, obj=None, priority=1, name=None):
        """(Re)Loads the given resource.
           
           :param obj: (dict or file or None) the resource object. Default is 
                       None meaning in will (re)load the default resource: 
                       taurus_resources.py from the application directory
           :param priority: (int) the resource priority. Default is 1 meaning 
                            maximum priority
           :param name: (str) an optional name to give to the resource
           
           :return: (dict) a dictionary version of the given resource object
        """
        if operator.isMappingType(obj):
            name = name or 'DICT%02d' % priority
        elif type(obj) in types.StringTypes or obj is None:
            name, obj = self.__reloadResource(obj)
            obj = ModuleDict(obj)
        else:
            raise TypeError
        
        if self._resource_map.get(name) is None:
            self._resource_count += 1
        self._resource_map[name] = obj
        if self._resource_count == 1:
            self._first_resource = obj
    
        pl = self._resource_priority.get(priority)
        if pl is None:
            self._resource_priority[priority] = pl = []
        pl.append(name)
        self._resource_priority_keys = self._resource_priority.keys()
        self._resource_priority_keys.sort()
        return obj
        
    loadResource = reloadResource
    loadResource.__doc__ = reloadResource.__doc__
    
    def __reloadResource(self, name=None):
        path = os.path.curdir
        if name is None:
            file_name = ResourcesFactory.DftResourceName
        else:
            path, file_name = os.path.split(name)
            if not path: path = os.path.curdir
        path = os.path.abspath(path)

        full_name = os.path.join(path, file_name)

        if not os.path.isfile(full_name):
            raise ImportError

        module_name, ext = os.path.splitext(file_name)
        
        m, file = None, None
        try:
            file, pathname, desc = imp.find_module(module_name, [path])
            self.info("(re)loading resource %s", pathname)
            m = imp.load_module(module_name, file, pathname, desc)
            if file: file.close()
        except Exception, e:
            if file: file.close()
            raise e
        
        if m is None:
            self.warning("failed to (re)load resource %s" % module_name)
            raise ImportError
        
        return full_name, m
    
    def __get(self, alias):
        if self._resource_count == 0:
            self.reloadResource(priority = ResourcesFactory.DftResourcePriority)
        
        # optimization: many applications contain only one resource: in that
        # case avoid the loop
        if self._resource_count == 1:
            return self._first_resource[alias]
            
        for p in self._resource_priority_keys:
            for resource_name in self._resource_priority[p]:
                resource = self._resource_map[resource_name]
                try: return resource[alias]
                except: pass
    
    def __splitResourceName(self, alias):
        for i, c in enumerate(alias):
            if not c.isalnum():
                return i, c, alias.split(c, 1)
        return None, '', [alias]
    
    def __splitScheme(self, alias):
        try:
            i = alias.index('://')
            return alias[:i], alias[i+3:]
        except:
            return '', alias
    
    def getValue(self, key):
        """Returns the value for a given key
           
           :param key: (str) a key
           
           :return: (str) the value for the given key
        """
        alias = self.__splitScheme(key)
        if alias[0] and not alias[0] in ResourcesFactory.schemes:
            return None
        i, c, alias = self.__splitResourceName(alias[1])
        alias[0] = self.__get(alias[0]) or ''
        return c.join(alias)
    
    def findObjectClass(self, absolute_name):
        """
        Obtain the class object corresponding to the given name.
           
        :param absolute_name: (str) the object absolute name string

        :return: (taurus.core.taurusmodel.TaurusModel) a class object that should be a subclass of a taurus.core.taurusmodel.TaurusModel
        :raise: (taurus.core.taurusexception.TaurusException) if the given name is invalid.
        """
        objType = None

        return objType

    def getDatabase(self, alias=None):
        """
        Obtain the object corresponding to the given database name or the 
        default database if db_name is None.
        If the corresponding database object already exists, the existing 
        instance is returned. Otherwise a new instance is stored and returned.
           
        :param alias: (str) database name string alias. If None, the 
                     default database is used
                           
        :return: (taurus.core.taurusdatabase.TaurusDatabase) database object
        :raise: (NameError) if the alias does not exist
        :raise: (taurus.core.taurusexception.TaurusException) if the given alias is invalid.
        """
        if alias is None:
            return Database()
        
        alias = self.getValue(alias)
        if not alias:
            raise NameError(alias)
        
        return Manager().getDatabase(alias)

    def getDevice(self, alias):
        """
        Obtain the object corresponding to the given device name. If the 
        corresponding device already exists, the existing instance is returned. 
        Otherwise a new instance is stored and returned.
           
        :param alias: device name string alias.
        
        :return: (taurus.core.taurusdevice.TaurusDevice) device object
        :raise: (NameError) if the alias does not exist
        :raise: (taurus.core.taurusexception.TaurusException) if the given alias is invalid.
        """
        alias = self.getValue(alias)
        if not alias:
            raise NameError(alias)
        return Manager().getDevice(alias)
        
    def getAttribute(self, alias):
        """
        Obtain the object corresponding to the given attribute name.
        If the corresponding attribute already exists, the existing instance
        is returned. Otherwise a new instance is stored and returned.

        :param alias: (str) attribute name string alias
             
        :return: (taurus.core.taurusattribute.TaurusAttribute) attribute object
        :raise: (NameError) if the alias does not exist
        :raise: (taurus.core.taurusexception.TaurusException) if the given alias is invalid.
        """
        alias = self.getValue(alias)
        if not alias:
            raise NameError(alias)
        return Manager().getAttribute(alias)

    def getConfiguration(self, alias):
        """
        Obtain the object corresponding to the given attribute or full name.
        If the corresponding configuration already exists, the existing instance
        is returned. Otherwise a new instance is stored and returned.

        :param alias: (str) configuration name string alias
             
        :return: (taurus.core.taurusconfiguration.TaurusConfiguration) configuration object
        :raise: (NameError) if the alias does not exist
        :raise: (taurus.core.taurusexception.TaurusException) if the given alias is invalid.
        """
        alias = self.getValue(alias)
        if not alias:
            raise NameError(alias)
        return Manager().getConfiguration(alias)

