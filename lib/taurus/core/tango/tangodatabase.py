#!/usr/bin/env python

#############################################################################
##
# This file is part of Taurus
##
# http://taurus-scada.org
##
# Copyright 2011 CELLS / ALBA Synchrotron, Bellaterra, Spain
##
# Taurus is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
##
# Taurus is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
##
# You should have received a copy of the GNU Lesser General Public License
# along with Taurus.  If not, see <http://www.gnu.org/licenses/>.
##
#############################################################################

"""This module contains all taurus tango authority"""

from __future__ import print_function

from builtins import str
from builtins import map
from builtins import range
from builtins import object
try:
    from collections.abc import Mapping
except ImportError:  # bck-compat py 2.7
    from collections import Mapping

import os
import weakref

from PyTango import (Database, DeviceProxy, DevFailed, ApiUtil)
from taurus import Device
from taurus.core.taurusbasetypes import TaurusDevState, TaurusEventType
from taurus.core.taurusauthority import TaurusAuthority
from taurus.core.util.containers import CaselessDict
from taurus.core.util.log import taurus4_deprecation
from taurus.core.util.fqdn import fqdn_no_alias


__all__ = ["TangoInfo", "TangoAttrInfo", "TangoDevInfo", "TangoServInfo",
           "TangoDevClassInfo", "TangoDatabaseCache", "TangoDatabase",
           "TangoAuthority"]

__docformat__ = "restructuredtext"

InvalidAlias = "nada"


class TangoInfo(object):

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

    def __str__(self):
        return "%s(%s)" % (self.__class__.__name__, self.name())
    __repr__ = __str__


class TangoAttrInfo(TangoInfo):

    def __init__(self, container, name=None, full_name=None, device=None,
                 info=None):
        super(TangoAttrInfo, self).__init__(container, name=name,
                                            full_name=full_name)
        self._info = info
        self._device = weakref.ref(device)

    def device(self):
        return self._device()

    def info(self):
        return self._info

    def __getattr__(self, name):
        return getattr(self._info, name)


class TangoDevClassInfo(TangoInfo):

    def __init__(self, container, name=None, full_name=None):
        super(TangoDevClassInfo, self).__init__(container, name=name,
                                                full_name=full_name)

        self._devices = CaselessDict()

    def devices(self):
        return self._devices

    def addDevice(self, dev):
        self._devices[dev.name()] = dev

    def getDeviceNames(self):
        if not hasattr(self, "_device_name_list"):
            self._device_name_list = sorted(map(TangoDevInfo.name,
                                                self._devices.values()))
        return self._device_name_list


class TangoDevInfo(TangoInfo):

    def __init__(self, container, name=None, full_name=None, alias=None,
                 server=None, klass=None, exported=False, host=None):
        super(TangoDevInfo, self).__init__(container, name=name,
                                           full_name=full_name)
        self._alias = alias
        self._server = weakref.ref(server)
        self._klass = weakref.ref(klass)
        self._exported = bool(int(exported))
        self._alive = None
        self._state = None
        self._host = host
        name = str(name) # python2 compatibility
        self._domain, self._family, self._member = list(map(str.upper,
                                                       name.split("/", 2)))
        self._attributes = None
        self._alivePending = False

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
        if self._alive is None:
            if self._alivePending:
                return False
            self._alivePending = True
            try:
                dev = self.getDeviceProxy()
                _ = dev.state()
                self._alive = True
            except:
                self._alive = False
            self._alivePending = False
        return self._alive

    def state(self):
        """Overwrite state so it doesn't call 'alive()' since it can take
        a long time for devices that are declared as exported but are in fact
        not running (crashed, network error, power cut, etc)"""
        if not self._state is None:
            return self._state
        exported = self.exported()
        if exported:
            self._state = TaurusDevState.Ready
        else:
            self._state = TaurusDevState.NotReady
        return self._state

    def host(self):
        return self._host

    def attributes(self):
        if self._attributes is None or len(self._attributes) == 0:
            self.refreshAttributes()
        return self._attributes

    def getAttribute(self, attrname):
        attrname = attrname.lower()
        for a in self.attributes():
            if a.name() == attrname:
                return a
        return None

    def setAttributes(self, attributes):
        self._attributes = attributes

    @taurus4_deprecation(alt="getDeviceProxy()")
    def getHWObj(self):
        return self.getDeviceProxy()

    def getDeviceProxy(self):
        db = self.container().db
        name = self.name()
        full_name = db.getFullName() + "/" + name
        dev = None
        try:
            dev = db.factory().getDevice(full_name).getDeviceProxy()
        except:
            pass
        return dev

    def refreshAttributes(self):
        attrs = []
        try:
            dev = self.getDeviceProxy()
            if dev is None:
                raise DevFailed()  # @todo: check if this is the right exception to throw
            attr_info_list = dev.attribute_list_query_ex()
            for attr_info in attr_info_list:
                full_name = "%s/%s" % (self.fullName(), attr_info.name)
                attr_obj = TangoAttrInfo(self.container(),
                                         name=attr_info.name.lower(), full_name=full_name.lower(),
                                         device=self, info=attr_info)
                attrs.append(attr_obj)
            attrs = sorted(attrs, key=lambda attr: attr.name())
        except DevFailed as df:
            self._state = TaurusDevState.NotReady
        self.setAttributes(attrs)


class TangoServInfo(TangoInfo):

    def __init__(self, container, name=None, full_name=None):
        super(TangoServInfo, self).__init__(container, name=name,
                                            full_name=full_name)
        self._devices = {}
        self._exported = False
        self._alive = None
        self._host = ""
        self._server_name, self._server_instance = name.split("/", 1)
        self._alivePending = False

    def devices(self):
        return self._devices

    def getDeviceNames(self):
        if not hasattr(self, "_device_name_list"):
            self._device_name_list = sorted(map(TangoDevInfo.name, self._devices.values()))
        return self._device_name_list

    def getClassNames(self):
        if not hasattr(self, "_klass_name_list"):
            klasses = set(map(TangoDevInfo.klass, self._devices.values()))
            self._klass_name_list = sorted(map(TangoDevClassInfo.name,
                                               klasses))
        return self._klass_name_list

    def exported(self):
        return self._exported

    def state(self):
        exported = self.exported()
        if exported:
            return TaurusDevState.Ready
        return TaurusDevState.NotReady

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
            except Exception as e:
                print("except", e)
                self._alive = False
            self._alivePending = False
        return self._alive


class TangoDatabaseCache(object):

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
        db = self.db
        db_dev_name = '/'.join((db.getFullName(), db.dev_name()))
        if hasattr(Device(db_dev_name), 'DbMySqlSelect'):
            # optimization in case the db exposes a MySQL select API
            query = ("SELECT name, alias, exported, host, server, class " +
                     "FROM device")
            r = db.command_inout("DbMySqlSelect", query)
            row_nb, column_nb = r[0][-2:]
            data = r[1]
            assert row_nb == len(data) // column_nb
        else:
            # fallback using tango commands (slow but works with sqlite DB)
            # see http://sf.net/p/tauruslib/tickets/148/
            data = []
            all_alias = {}
            all_devs = db.get_device_name('*', '*')
            all_exported = db.get_device_exported('*')
            for k in db.get_device_alias_list('*'):  # Time intensive!!
                all_alias[db.get_device_alias(k)] = k
            for d in all_devs:  # Very time intensive!!
                _info = db.command_inout("DbGetDeviceInfo", d)[1]
                name, ior, level, server, host, started, stopped = _info[:7]
                klass = db.get_class_for_device(d)
                alias = all_alias.get(d, '')
                exported = str(int(d in all_exported))
                data.extend((name, alias, exported, host, server, klass))
            column_nb = 6  # len ((name, alias, exported, host, server, klass))

        CD = CaselessDict
        dev_dict, serv_dict, klass_dict, alias_dict = CD(), {}, {}, CD()

        for i in range(0, len(data), column_nb):
            name, alias, exported, host, server, klass = data[i:i + column_nb]
            if name.count("/") != 2:
                continue  # invalid/corrupted entry: just ignore it
            if server.count("/") != 1:
                continue  # invalid/corrupted entry: just ignore it
            if not len(alias):
                alias = None

            serv_dict[server] = si = serv_dict.get(server,
                                                   TangoServInfo(self, name=server,
                                                                 full_name=server))

            klass_dict[klass] = dc = klass_dict.get(klass,
                                                    TangoDevClassInfo(self,
                                                                      name=klass,
                                                                      full_name=klass))

            full_name = "%s/%s" % (db.getFullName(), name)
            dev_dict[name] = di = TangoDevInfo(self, name=name, full_name=full_name,
                                               alias=alias, server=si, klass=dc,
                                               exported=exported, host=host)

            si.addDevice(di)
            dc.addDevice(di)
            if alias is not None:
                alias_dict[alias] = di

        self._devices = dev_dict
        self._device_tree = TangoDevTree(dev_dict)
        self._server_tree = TangoServerTree(serv_dict)
        self._servers = serv_dict
        self._klasses = klass_dict
        self._aliases = alias_dict

    def refreshAttributes(self, device):
        attrs = []
        try:
            db = self.db
            name = device.name()
            full_name = db.getFullName() + "/" + name
            taurus_dev = db.factory().getDevice(full_name,
                                                create_if_needed=False)
            if taurus_dev is None:
                dev = DeviceProxy(full_name)
            else:
                dev = taurus_dev.getDeviceProxy()
            attr_info_list = dev.attribute_list_query_ex()
            for attr_info in attr_info_list:
                full_attr_name = "%s/%s" % (full_name, attr_info.name)
                attr_obj = TangoAttrInfo(self, name=attr_info.name,
                                         full_name=full_attr_name,
                                         device=device, info=attr_info)
                attrs.append(attr_obj)
            attrs = sorted(attrs, key=lambda attr: attr.name().lower())
        except DevFailed as df:
            pass
        device.setAttributes(attrs)

    def getDevice(self, name):
        """Returns a :class:`TangoDevInfo` object with information
        about the given device name

        :param name: (str) the device name

        :return: (TangoDevInfo) information about the device"""
        return self._devices.get(name)

    def getDeviceNames(self):
        """Returns a list of registered device names

        :return: (sequence<str>) a sequence with all registered device names"""
        if self._device_name_list is None:
            self._device_name_list = sorted(
                map(TangoDevInfo.name, self.devices().values()))
        return self._device_name_list

    def getAliasNames(self):
        if self._alias_name_list is None:
            self._alias_name_list = sorted(
                map(TangoDevInfo.alias, self.aliases().values()))
        return self._alias_name_list

    def getServerNames(self):
        """Returns a list of registered server names

        :return: (sequence<str>) a sequence with all registered server names"""
        if self._server_name_list is None:
            self._server_name_list = sorted(
                map(TangoServInfo.name, self.servers().values()))
        return self._server_name_list

    def getClassNames(self):
        """Returns a list of registered device classes

        :return: (sequence<str>) a sequence with all registered device classes"""
        if self._klass_name_list is None:
            self._klass_name_list = sorted(
                map(TangoDevClassInfo.name, self.klasses().values()))
        return self._klass_name_list

    def deviceTree(self):
        """Returns a tree container with all devices in three levels: domain,
           family and member

           :return: (TangoDevTree) a tree containning all devices"""
        return self._device_tree

    def serverTree(self):
        """Returns a tree container with all servers in two levels: server name
        and server instance

           :return: (TangoServerTree) a tree containning all servers"""
        return self._server_tree

    def servers(self):
        return self._servers

    def devices(self):
        return self._devices

    def klasses(self):
        return self._klasses

    def getDeviceDomainNames(self):
        return list(self._device_tree.keys())

    def getDeviceFamilyNames(self, domain):
        families = self._device_tree.get(domain)
        if families is None:
            return []
        return list(families.keys())

    def getDeviceMemberNames(self, domain, family):
        families = self._device_tree.get(domain)
        if families is None:
            return []
        members = families.get(family)
        if members is None:
            return []
        return list(members.keys())

    def getDomainDevices(self, domain):
        return self.deviceTree().getDomainDevices(domain)

    def getFamilyDevices(self, domain, family):
        return self.deviceTree().getFamilyDevices(domain, family)

    def getServerNameInstances(self, serverName):
        return self.serverTree().getServerNameInstances(serverName)


class TangoDevTree(CaselessDict):

    def __init__(self, other=None):
        super(TangoDevTree, self).__init__()
        self._devices = CaselessDict()
        if other is not None:
            self._update(other)

    def _update(self, other):
        try:
            if isinstance(other, Mapping):
                other = list(other.values())
            for dev in other:
                try:
                    self.addDevice(dev)
                except Exception as e:
                    print(e)
        except Exception as e:
            raise Exception(
                "Must give dict<obj, TangoDevInfo> or sequence<TangoDevInfo>")

    def addDevice(self, dev_info):
        domain, family, member = dev_info.domain(), dev_info.family(), dev_info.member()

        families = self[domain] = self.get(domain, CaselessDict())
        devs = self._devices[domain] = self._devices.get(
            domain, CaselessDict())
        devs[dev_info.name()] = dev_info

        families[family] = members = families.get(family, CaselessDict())

        members[member] = dev_info

    def getDomainDevices(self, domain):
        """Returns all devices under the given domain. Returns empty list if
        the domain doesn't exist or doesn't contain any devices"""
        return list(self._devices.get(domain, {}).values())

    def getFamilyDevices(self, domain, family):
        """Returns all devices under the given domain/family. Returns empty list if
        the domain/family doesn't exist or doesn't contain any devices"""
        families = self.get(domain)
        if families is None:
            return
        return list(families.get(family, {}).values())


class TangoServerTree(dict):

    def __init__(self, other=None):
        super(TangoServerTree, self).__init__()
        if other is not None:
            self._update(other)

    def _update(self, other):
        try:
            if isinstance(other, Mapping):
                other = list(other.values())
            for serv in other:
                try:
                    self.addServer(serv)
                except Exception as e:
                    print(e)
        except Exception as e:
            raise Exception(
                "Must give dict<obj, TangoServInfo> or sequence<TangoServInfo>")

    def addServer(self, serv_info):
        serverName, serverInstance = serv_info.serverName(), serv_info.serverInstance()

        serverInstances = self[serverName] = self.get(serverName, {})

        serverInstances[serverInstance] = serv_info

    def getServerNameInstances(self, serverName):
        """Returns all servers under the given serverName. Returns empty list if
        the server name doesn't exist or doesn't contain any instances"""
        return list(self.get(serverName, {}).values())


def get_home():
    """
    Find user's home directory if possible. Otherwise raise error.

    :return: user's home directory
    :rtype: str

    New in PyTango 7.2.0
    """
    path = ''
    try:
        path = os.path.expanduser("~")
    except:
        pass
    if not os.path.isdir(path):
        for evar in ('HOME', 'USERPROFILE', 'TMP'):
            try:
                path = os.environ[evar]
                if os.path.isdir(path):
                    break
            except:
                pass
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

    with open(fname) as f:
        for line in f:
            strippedline = line.split('#', 1)[0].strip()

            if not strippedline:
                # empty line
                continue

            tup = strippedline.split('=', 1)
            if len(tup) != 2:
                # illegal line!
                continue

            key, val = list(map(str.strip, tup))
            if key == env_var_name:
                return val


class TangoAuthority(TaurusAuthority):

    # helper class property that stores a reference to the corresponding
    # factory
    _factory = None
    _scheme = 'tango'
    _description = 'A Tango Authority'

    def __init__(self, host=None, port=None, parent=None):
        if host is None or port is None:
            try:
                _hp = TangoAuthority.get_default_tango_host()
                host, port = _hp.rsplit(':', 1)
            except Exception:
                from taurus import warning
                warning("Error getting default Tango host")

        # Set host to fqdn
        host = fqdn_no_alias(host)

        self.dbObj = Database(host, port)
        self._dbProxy = None
        self._dbCache = None

        complete_name = "tango://%s:%s" % (host, port)
        self.call__init__(TaurusAuthority, complete_name, parent)

        try:
            self.get_class_for_device(self.dev_name())
        except:
            # Ok, old tango database.
            self.get_class_for_device = self.__get_class_for_device

    @staticmethod
    def get_default_tango_host():
        if hasattr(ApiUtil, "get_env_var"):
            f = ApiUtil.get_env_var
        else:
            f = get_env_var
        return f("TANGO_HOST")

    def __get_class_for_device(self, dev_name):
        """Backup method when connecting to tango 5 database device server"""
        # Ok, old tango database.
        serv_name = self.command_inout("DbGetDeviceInfo", dev_name)[1][3]
        devs = self.get_device_class_list(serv_name)
        dev_name_lower = dev_name.lower()
        for i in range(len(devs) // 2):
            idx = i * 2
            if devs[idx].lower() == dev_name_lower:
                return devs[idx + 1]
        return None

    def get_device_attribute_list(self, dev_name, wildcard):
        return self.command_inout("DbGetDeviceAttributeList", (dev_name, wildcard))

    # Export the PyTango.Database interface into this object.
    # This way we can call for example get_attribute_property on an object of
    # this class
    def __getattr__(self, name):
        if not self.dbObj is None:
            return getattr(self.dbObj, name)
        return None

    @taurus4_deprecation(alt='getTangoDB')
    def getValueObj(self, cache=True):
        return self.getTangoDB()

    def getTangoDB(self):
        return self.dbObj

    @taurus4_deprecation(alt='getFullName')
    def getDisplayValue(self, cache=True):
        return self.getDisplayDescription(cache)

    def addListener(self, listener):
        ret = TaurusAuthority.addListener(self, listener)
        if not ret:
            return ret
        self.fireEvent(TaurusEventType.Change, self.getFullName(), listener)
        return ret

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # Query capabilities built on top of a cache
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    def cache(self):
        if self._dbCache is None:
            self._dbCache = TangoDatabaseCache(self)
        return self._dbCache

    def refreshCache(self):
        self.cache().refresh()

    def getDevice(self, name):
        """
        Reimplemented from :class:`TaurusDevice` to use cache and return
        :class:`taurus.core.tango.TangoDevInfo` objects with information
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

    def getElementAlias(self, full_name):
        '''return the alias of an element from its full name'''
        try:
            alias = self.getTangoDB().get_alias(full_name)
            if alias and alias.lower() == InvalidAlias:
                alias = None
        except:
            alias = None
        return alias

    def getElementFullName(self, alias):
        '''return the full name of an element from its alias'''
        try:  # PyTango v>=8.1.0
            return self.getTangoDB().get_device_from_alias(alias)
        except AttributeError:
            try:  # PyTango v<8.1.0
                return self.getTangoDB().get_device_alias(alias)
            except:
                return None
        except:
            return None

    @taurus4_deprecation(alt=".description")
    def getDescription(self, cache=True):
        return self.description


# Declare this alias for backwards compatibility
TangoDatabase = TangoAuthority
