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

"""This module contains the base class for a taurus database"""

__all__ = ["TaurusInfo", "TaurusDevInfo", "TaurusServInfo", "TaurusDevClassInfo",
           "TaurusAttrInfo", "TaurusDevTree", "TaurusServerTree",
           "TaurusDatabaseCache", "TaurusDatabase"]

__docformat__ = "restructuredtext"

import weakref
import operator

from .taurusbasetypes import TaurusEventType, TaurusSWDevHealth, TaurusElementType
from .taurusmodel import TaurusModel
from .util.containers import CaselessDict

DFT_DATABASE_DESCRIPTION = "A database"


class TaurusInfo(object):
    def __init__(self, container, name=None, full_name=None):
        self._container = weakref.ref(container)
        self._name = name
        self._full_name = full_name
    
    def container(self):
        return self._container()
    
    def name(self):
        return self._name

    def fullName(self):
        return self._full_name
    
    def __str__(self): return "%s(%s)" % (self.__class__.__name__, self.name())
    __repr__ = __str__


class TaurusDevInfo(TaurusInfo):
    def __init__(self, container, name=None, full_name=None, alias=None, server=None, klass=None, exported=False, host=None):
        super(TaurusDevInfo, self).__init__(container, name=name, full_name=full_name)
        self._alias = alias
        self._server = weakref.ref(server)
        self._klass = weakref.ref(klass)
        self._exported = bool(int(exported))
        self._alive = None
        self._health = None
        self._host = host
        self._domain, self._family, self._member = map(str.upper, name.split("/", 2))
        self._attributes = None

    def domain(self):
        return self._domain

    def family(self):
        return self._family

    def member(self):
        return self._member
    
    def alias(self):
        return self._alias
    
    def server(self):
        return self._server()
    
    def klass(self):
        return self._klass()
    
    def exported(self):
        return self._exported
    
    def alive(self):
        return self._alive
    
    def health(self):
        if self._health is None:
            if self.exported():
                alive = self.alive()
                if alive == True:
                    self._health = TaurusSWDevHealth.ExportedAlive
                elif alive == False:
                    self._health = TaurusSWDevHealth.ExportedNotAlive
                else:
                    self._health = TaurusSWDevHealth.Exported
            else:
                self._health = TaurusSWDevHealth.NotExported
        return self._health
        
    def host(self):
        return self._host
    
    def attributes(self):
        return self._attributes
    
    def getAttribute(self, attrname):
        attrname= attrname.lower()
        for a in self.attributes():
            if a.name() == attrname:
                return a
        return None
    
    def setAttributes(self, attributes):
        self._attributes = attributes
    

class TaurusServInfo(TaurusInfo):
    def __init__(self, container, name=None, full_name=None):
        super(TaurusServInfo, self).__init__(container, name=name, full_name=full_name)
        self._devices = CaselessDict()
        self._exported = False
        self._alive = None
        self._host = ""
        self._server_name, self._server_instance = name.split("/", 1)
    
    def devices(self):
        return self._devices

    def getDeviceNames(self):
        if not hasattr(self, "_device_name_list"):
            self._device_name_list = sorted(map(TaurusDevInfo.name, self._devices.values()))
        return self._device_name_list

    def getClassNames(self):
        if not hasattr(self, "_klass_name_list"):
            klasses = set(map(TaurusDevInfo.klass, self._devices.values()))
            self._klass_name_list = sorted(map(TaurusDevClassInfo.name, klasses))
        return self._klass_name_list

    def exported(self):
        return self._exported

    def alive(self):
        return self._alive

    def health(self):
        exported = self.exported()
        if exported:
            alive = self.alive()
            if alive == True:
                return TaurusSWDevHealth.ExportedAlive
            elif alive == False:
                return TaurusSWDevHealth.ExportedNotAlive
            else:
                return TaurusSWDevHealth.Exported
        return TaurusSWDevHealth.NotExported
    
    def host(self):
        return self._host
    
    def serverName(self):
        return self._server_name

    def serverInstance(self):
        return self._server_instance
    
    def addDevice(self, dev):
        self._exported |= dev.exported()
        self._host = dev.host()
        self._devices[dev.name()] = dev


class TaurusDevClassInfo(TaurusInfo):
    def __init__(self, container, name=None, full_name=None):
        super(TaurusDevClassInfo, self).__init__(container, name=name, full_name=full_name)
        self._devices = CaselessDict()
    
    def devices(self):
        return self._devices
    
    def getDeviceNames(self):
        if not hasattr(self, "_device_name_list"):
            self._device_name_list = sorted(map(TaurusDevInfo.name, self._devices.values()))
        return self._device_name_list
    
    def addDevice(self, dev):
        self._devices[dev.name()] = dev


class TaurusAttrInfo(TaurusInfo):
    def __init__(self, container, name=None, full_name=None, device=None, info=None):
        super(TaurusAttrInfo, self).__init__(container, name=name, full_name=full_name)
        self._info = info
        self._device = weakref.ref(device)

    def device(self):
        return self._device()
    
    def info(self):
        return self._info
    
    def __getattr__(self, name):
        return getattr(self._info, name)


class TaurusDevTree(CaselessDict):

    def __init__(self, other=None):
        super(TaurusDevTree, self).__init__()
        self._devices = CaselessDict()
        if other is not None:
            self._update(other)

    def _update(self, other):
        try:
            if operator.isMappingType(other):
                other = other.values()
            for dev in other:
                try:
                    self.addDevice(dev)
                except Exception, e:
                    print e
        except Exception, e:
            raise Exception("Must give dict<obj, TaurusDevInfo> or sequence<TaurusDevInfo>")
        
    def addDevice(self, dev_info):
        domain, family, member = dev_info.domain(), dev_info.family(), dev_info.member()
        
        families = self[domain] = self.get(domain, CaselessDict())
        devs = self._devices[domain] = self._devices.get(domain, CaselessDict())
        devs[dev_info.name()] = dev_info
        
        families[family] = members = families.get(family, CaselessDict())
        
        members[member] = dev_info

    def getDomainDevices(self, domain):
        """Returns all devices under the given domain. Returns empty list if
        the domain doesn't exist or doesn't contain any devices"""
        return self._devices.get(domain, {}).values()
    
    def getFamilyDevices(self, domain, family):
        """Returns all devices under the given domain/family. Returns empty list if
        the domain/family doesn't exist or doesn't contain any devices"""
        families = self.get(domain)
        if families is None:
            return 
        return families.get(family, {}).values()


class TaurusServerTree(dict):
    
    def __init__(self, other=None):
        super(TaurusServerTree, self).__init__()
        if other is not None:
            self._update(other)

    def _update(self, other):
        try:
            if operator.isMappingType(other):
                other = other.values()
            for serv in other:
                try:
                    self.addServer(serv)
                except Exception, e:
                    print e
        except Exception, e:
            raise Exception("Must give dict<obj, TaurusServInfo> or sequence<TaurusServInfo>")
        
    def addServer(self, serv_info):
        serverName, serverInstance = serv_info.serverName(), serv_info.serverInstance()
        
        serverInstances = self[serverName] = self.get(serverName, {})
        
        serverInstances[serverInstance] = serv_info

    def getServerNameInstances(self, serverName):
        """Returns all servers under the given serverName. Returns empty list if
        the server name doesn't exist or doesn't contain any instances"""
        return self.get(serverName, {}).values()


class TaurusDatabaseCache(object):
    
    def __init__(self, db):
        self._db = weakref.ref(db)
        self._device_tree = None
        self._server_tree = None
        self._servers = None
        self._server_name_list = None
        self._devices = None
        self._device_name_list = None
        self._klasses = None
        self._klass_name_list = None
        self._aliases = None
        self._alias_name_list = None
        self.refresh()
    
    @property
    def db(self):
        return self._db()
    
    def refresh(self):
        raise RuntimeError("Must be implemented in subclass")
    
    def refreshAttributes(self, device):
        raise RuntimeError("Must be implemented in subclass")
    
    def getDevice(self, name):
        """Returns a :class:`taurus.core.taurusdatabase.TaurusDevInfo` object with information 
        about the given device name
        
        :param name: (str) the device name
        
        :return: (TaurusDevInfo) information about the device"""
        return self._devices.get(name)
    
    def getDeviceNames(self):
        """Returns a list of registered device names
        
        :return: (sequence<str>) a sequence with all registered device names"""
        if self._device_name_list is None:
            self._device_name_list = sorted(map(TaurusDevInfo.name, self.devices().values()))
        return self._device_name_list

    def getAliasNames(self):
        if self._alias_name_list is None:
            self._alias_name_list = sorted(map(TaurusDevInfo.alias, self.aliases().values()))
        return self._alias_name_list
    
    def getServerNames(self):
        """Returns a list of registered server names
        
        :return: (sequence<str>) a sequence with all registered server names"""
        if self._server_name_list is None:
            self._server_name_list = sorted(map(TaurusServInfo.name, self.servers().values()))
        return self._server_name_list

    def getClassNames(self):
        """Returns a list of registered device classes
        
        :return: (sequence<str>) a sequence with all registered device classes"""
        if self._klass_name_list is None:
            self._klass_name_list = sorted(map(TaurusDevClassInfo.name, self.klasses().values()))
        return self._klass_name_list

    def deviceTree(self):
        """Returns a tree container with all devices in three levels: domain,
           family and member
           
           :return: (TaurusDevTree) a tree containning all devices"""
        return self._device_tree
    
    def serverTree(self):
        """Returns a tree container with all servers in two levels: server name
        and server instance
           
           :return: (TaurusServerTree) a tree containning all servers"""
        return self._server_tree
    
    def servers(self):
        return self._servers
    
    def devices(self):
        return self._devices
    
    def klasses(self):
        return self._klasses
    
    def getDeviceDomainNames(self):
        return self._device_tree.keys()
    
    def getDeviceFamilyNames(self, domain):
        families = self._device_tree.get(domain)
        if families is None: return []
        return families.keys()
    
    def getDeviceMemberNames(self, domain, family):
        families = self._device_tree.get(domain)
        if families is None: return []
        members = families.get(family)
        if members is None: return []
        return members.keys()
    
    def getDomainDevices(self, domain):
        return self.deviceTree().getDomainDevices(domain)
    
    def getFamilyDevices(self, domain, family):
        return self.deviceTree().getFamilyDevices(domain, family)

    def getServerNameInstances(self, serverName):
        return self.serverTree().getServerNameInstances(serverName)


class TaurusDatabase(TaurusModel):
    
    def __init__(self, complete_name, parent=None):
        self._descr = None
        self.call__init__(TaurusModel, complete_name, parent)
    
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # TaurusModel implementation
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-    
    def cleanUp(self):
        self.trace("[TaurusDatabase] cleanUp")
        TaurusModel.cleanUp(self)

    @classmethod
    def getTaurusElementType(cls):
        return TaurusElementType.Database
    
    @classmethod
    def buildModelName(cls, parent_model, relative_name):
        """build an 'absolute' model name from the parent name and the 'relative'
        name. parent_model is ignored since there is nothing above the Database
        object"""
        return relative_name
    
    @classmethod
    def getNameValidator(cls):
        from .taurusvalidator import DatabaseNameValidator
        return DatabaseNameValidator()
    
    def getDescription(self,cache=True):
        if self._descr is None or not cache:
            try:
                self._descr = self.info()
            except:
                self._descr = self._getDefaultDescription()
        return self._descr

    def getDisplayValue(self,cache=True):
        return self.getDisplayDescription(cache)

    def getDisplayDescription(self,cache=True):
        return self.getFullName()
    
    def getDisplayDescrObj(self,cache=True):
        obj = []
        obj.append(('name', self.getDisplayName(cache=cache)))
        descr = self.getDescription(cache=cache)
        obj.append(('description', descr))
        return obj
    
    def addListener(self, listener):
        ret = TaurusModel.addListener(self, listener)
        if not ret:
            return ret
        self.fireEvent(TaurusEventType.Change, self.getDisplayValue(), listener)
        return ret

    def getChildObj(self,child_name):
        if not child_name:
            return None
        return self.getDevice(child_name)
        
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # Device access methods
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-    
    
    def getDevice(self, devname):
        """Returns the device object given its name"""
        import taurusdevice
        return self.factory().getObject(taurusdevice.TaurusDevice, devname)

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # Query capabilities built on top of a cache
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    
    def refreshCache(self):
        self.cache().refresh()
    
    def getDevice(self, name):
        """Returns a :class:`taurus.core.tango.TangoDevInfo` object with information 
        about the given device name
        
        :param name: (str) the device name
        
        :return: (TangoDevInfo) information about the tango device"""
        return self.cache().getDevice(name)
    
    def getDeviceNames(self):
        """Returns a list of registered tango device names
        
        :return: (sequence<str>) a sequence with all registered tango device names"""
        return self.cache().getDeviceNames()

    def getAliasNames(self):
        """Returns a list of registered tango device alias
        
        :return: (sequence<str>) a sequence with all registered tango device alias"""
        return self.cache().getAliasNames()
    
    def getServerNames(self):
        """Returns a list of registered tango device servers in format<name>/<instance>
        
        :return: (sequence<str>) a sequence with all registered tango device servers"""
        return self.cache().getServerNames()

    def getClassNames(self):
        """Returns a list of registered tango device classes
        
        :return: (sequence<str>) a sequence with all registered tango device classes"""
        return self.cache().getClassNames()

    def getDeviceDomainNames(self):
        return self.cache().getDeviceDomainNames()
    
    def getDeviceFamilyNames(self, domain):
        return self.cache().getDeviceFamilyNames(domain)
    
    def getDeviceMemberNames(self, domain, family):
        return self.cache().getDeviceMemberNames(domain, family)
    
    def getDomainDevices(self, domain):
        return self.cache().getDomainDevices(domain)
    
    def getFamilyDevices(self, domain, family):
        return self.cache().getFamilyDevices(domain, family)
    
    def getServerNameInstances(self, serverName):
        return self.cache().getServerNameInstances(serverName)
    
    def deviceTree(self):
        """Returns a tree container with all devices in three levels : domain,
           family and member
           
           :return: (TangoDevTree) a tree containning all devices"""
        return self.cache().deviceTree()
    
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # Mandatory methods to overwrite
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-    
    def cache(self):
        raise RuntimeError("TaurusDatabase.cache cannot be called")

    def getElementAlias(self, full_name):
        raise RuntimeError("TaurusDatabase.getElementAlias cannot be called")
        
    def getElementFullName(self, alias):
        raise RuntimeError("TaurusDatabase.getElementFullName cannot be called")
    
    def _getDefaultDescription(self):
        return DFT_DATABASE_DESCRIPTION