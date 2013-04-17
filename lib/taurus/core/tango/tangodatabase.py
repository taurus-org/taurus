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

"""This module contains all taurus tango database"""

__all__ = ["TangoDevInfo", "TangoServInfo", "TangoDatabaseCache",
           "TangoDatabase" ]

__docformat__ = "restructuredtext"

import os

import PyTango
import PyTango.utils

from taurus import Factory
from taurus.core.taurusbasetypes import TaurusSWDevHealth
from taurus.core.taurusdatabase import TaurusDatabaseCache, TaurusDevInfo, \
    TaurusAttrInfo, TaurusServInfo, TaurusDevClassInfo, TaurusDevTree, \
    TaurusServerTree
from taurus.core.util.containers import CaselessDict
from taurus.core.taurusdatabase import TaurusDatabase

InvalidAlias = "nada"


class TangoDevInfo(TaurusDevInfo):
    
    def __init__(self, container, name=None, full_name=None, alias=None, server=None, klass=None, exported=False, host=None):
        super(TangoDevInfo, self).__init__(container, name=name, full_name=full_name, alias=alias, server=server, klass=klass, exported=exported, host=host)
        self._alivePending = False
    
    def attributes(self):
        if self._attributes is None or len(self._attributes) == 0:
            self.refreshAttributes()
        return self._attributes

    def getHWObj(self):
        db = self.container().db
        name = self.name()
        full_name = db.getFullName() + "/" + name
        dev = None
        try:
            dev = db.factory().getDevice(full_name).getHWObj()
        except:
            pass
        return dev
    
    def alive(self):
        if self._alive is None:
            if self._alivePending:
                return False
            self._alivePending = True
            try:
                dev = self.getHWObj()
                state = dev.state()
                self._alive = True
            except:
                self._alive = False
            self._alivePending = False
        return self._alive
    
    def health(self):
        """Overwrite health so it doesn't call 'alive()' since it can take
        a long time for devices that are declared as exported but are in fact
        not running (crached, network error, power cut, etc)"""
        if not self._health is None:
            return self._health
        exported = self.exported()
        if exported:
            self._health = TaurusSWDevHealth.Exported
        else:
            self._health = TaurusSWDevHealth.NotExported
        return self._health
    
    def refreshAttributes(self):
        attrs = []
        try:
            dev = self.getHWObj()
            if dev is None:
                raise PyTango.DevFailed() # @todo: check if this is the right exception to throw
            attr_info_list = dev.attribute_list_query_ex()
            for attr_info in attr_info_list:
                full_name = "%s/%s" % (self.fullName(), attr_info.name)
                attr_obj = TaurusAttrInfo(self.container(), 
                    name=attr_info.name.lower(), full_name=full_name.lower(),
                    device=self, info=attr_info)
                attrs.append(attr_obj)
            attrs = sorted(attrs, key=lambda attr : attr.name())
        except PyTango.DevFailed as df:
            if self.health() == TaurusSWDevHealth.Exported:
                self._health = TaurusSWDevHealth.ExportedNotAlive
        self.setAttributes(attrs)


class TangoServInfo(TaurusServInfo):
    
    def __init__(self, container, name=None, full_name=None):
        super(TangoServInfo, self).__init__(container, name=name, full_name=full_name)
        self._alivePending = False
        
    def alive(self):
        if self._alive is None:
            if self._alivePending:
                return False
            try:
                self._alivePending = True
                alive = True
                for d in self.devices().values():
                    alive = d.alive()
                    if not alive:
                        break
                self._alive = alive
            except Exception,e:
                print "except",e
                self._alive = False
            self._alivePending = False
        return self._alive


class TangoDatabaseCache(TaurusDatabaseCache):

    def refresh(self):
        db = self.db
        
        query = "SELECT name, alias, exported, host, server, class FROM device"
        
        r = db.command_inout("DbMySqlSelect", query)
        row_nb, column_nb = r[0][-2], r[0][-1]
        results, data = r[0][:-2], r[1]
        assert row_nb == len(data) / column_nb
        
        CD = CaselessDict
        #CD = dict
        dev_dict, serv_dict, klass_dict, alias_dict = CD(), {}, {}, CD()

        for i in xrange(0, len(data), column_nb):
            name, alias, exported, host, server, klass = data[i:i+column_nb]
            if name.count("/") != 2: continue # invalid/corrupted entry: just ignore it
            if server.count("/") != 1: continue # invalid/corrupted entry: just ignore it
            if not len(alias): alias = None

            serv_dict[server] = si = serv_dict.get(server, 
                                                   TangoServInfo(self, name=server,
                                                                 full_name=server))
            
            klass_dict[klass] = dc = klass_dict.get(klass,
                                                    TaurusDevClassInfo(self,
                                                                       name=klass,
                                                                       full_name=klass))
            
            full_name = "tango://%s/%s" % (db.getFullName(), name) 
            dev_dict[name] = di = TangoDevInfo(self, name=name, full_name=full_name, 
                                               alias=alias, server=si, klass=dc,
                                               exported=exported, host=host)
            
            si.addDevice(di)
            dc.addDevice(di)
            if alias is not None:
                alias_dict[alias] = di
        
        self._devices = dev_dict
        self._device_tree = TaurusDevTree(dev_dict)
        self._server_tree = TaurusServerTree(serv_dict)
        self._servers = serv_dict
        self._klasses = klass_dict
        self._aliases = alias_dict
        
    def refreshAttributes(self, device):
        attrs = []
        try:
            db = self.db
            name = device.name()
            full_name = db.getFullName() + "/" + name
            taurus_dev = db.factory().getExistingDevice(full_name)
            if taurus_dev is None:
                dev = PyTango.DeviceProxy(full_name)
            else:
                dev = taurus_dev.getHWObj()
            attr_info_list = dev.attribute_list_query_ex()
            for attr_info in attr_info_list:
                full_attr_name = "%s/%s" % (full_name, attr_info.name)
                attr_obj = TaurusAttrInfo(self, name=attr_info.name,
                                          full_name=full_attr_name,
                                          device=device, info=attr_info) 
                attrs.append(attr_obj)
            attrs = sorted(attrs, key=lambda attr : attr.name().lower())
        except PyTango.DevFailed as df:
            pass
        device.setAttributes(attrs)


def get_home():
    """
    Find user's home directory if possible. Otherwise raise error.
    
    :return: user's home directory
    :rtype: str
    
    New in PyTango 7.2.0
    """
    path=''
    try:
        path=os.path.expanduser("~")
    except:
        pass
    if not os.path.isdir(path):
        for evar in ('HOME', 'USERPROFILE', 'TMP'):
            try:
                path = os.environ[evar]
                if os.path.isdir(path):
                    break
            except: pass
    if path:
        return path
    else:
        raise RuntimeError('please define environment variable $HOME')

def get_env_var(env_var_name):
    """
    Returns the value for the given environment name
    A backup method for old Tango/PyTango versions which don't implement
    :meth:`PyTango.ApiUtil.get_env_var`
    
    Search order:

        * a real environ var
        * HOME/.tangorc
        * /etc/tangorc
        
    :param env_var_name: the environment variable name
    :type env_var_name: str
    :return: the value for the given environment name
    :rtype: str
    """
    
    if env_var_name in os.environ:
        return os.environ[env_var_name]
    
    fname = os.path.join(get_home(), '.tangorc')
    if not os.path.exists(fname):
        if os.name == 'posix':
            fname = "/etc/tangorc"
    if not os.path.exists(fname):
        return None

    for line in file(fname):
        strippedline = line.split('#',1)[0].strip()
        
        if not strippedline:
            #empty line
            continue
        
        tup = strippedline.split('=',1)
        if len(tup) !=2:
            # illegal line!
            continue
        
        key, val = map(str.strip, tup)
        if key == env_var_name:
            return val


class TangoDatabase(TaurusDatabase):

    def __init__(self,host=None,port=None,parent=None):
        pars = ()
        if host is None or port is None:
            try:
                host, port = TangoDatabase.get_default_tango_host().rsplit(':', 1)
                pars = host, port
            except Exception, e:
                print "Error getting env TANGO_HOST:", str(e)
        else:
            pars = host, port
        self.dbObj = PyTango.Database(*pars)
        self._dbProxy = None
        self._dbCache = None
        
        complete_name = "%s:%s" % (host, port)
        self.call__init__(TaurusDatabase, complete_name, parent)

        try:
            self.get_class_for_device(self.dev_name())
        except:
            # Ok, old tango database.
            self.get_class_for_device = self.__get_class_for_device

    @staticmethod
    def get_default_tango_host():
        if hasattr(PyTango.ApiUtil, "get_env_var"):
            f = PyTango.ApiUtil.get_env_var
        else:
            f = get_env_var
        return f("TANGO_HOST")

    def __get_class_for_device(self, dev_name):
        """Backup method when connecting to tango 5 database device server"""
        # Ok, old tango database.
        serv_name = self.command_inout("DbGetDeviceInfo",dev_name)[1][3]
        devs = self.get_device_class_list(serv_name)
        dev_name_lower = dev_name.lower()
        for i in xrange(len(devs)/2):
            idx = i*2
            if devs[idx].lower() == dev_name_lower:
                return devs[idx+1]
        return None

    def get_device_attribute_list(self, dev_name, wildcard):
        return self.command_inout("DbGetDeviceAttributeList", (dev_name, wildcard))
        
    # Export the PyTango.Database interface into this object.
    # This way we can call for example get_attribute_property on an object of this class
    def __getattr__(self, name):
        if not self.dbObj is None: 
            return getattr(self.dbObj,name)
        return None
    
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # TaurusModel implementation
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-    

    # helper class property that stores a reference to the corresponding factory
    _factory = None
    
    @classmethod
    def factory(cls):
        if cls._factory is None:
            cls._factory = Factory(scheme='tango')
        return cls._factory
        
    def getValueObj(self,cache=True):
        return self.dbObj
    
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # Mandatory methods to overwrite from TaurusDatabase
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    def cache(self):
        if self._dbCache is None:
            self._dbCache = TangoDatabaseCache(self)
        return self._dbCache

    def getElementAlias(self, full_name):
        try:
            alias = self.getValueObj().get_alias(full_name)
            if alias and alias.lower() == InvalidAlias:
                alias = None 
        except:
            alias = None
        return alias
        
    def getElementFullName(self, alias):
        try:
            return self.getValueObj().get_device_alias(alias)
        except:
            pass
        return None
