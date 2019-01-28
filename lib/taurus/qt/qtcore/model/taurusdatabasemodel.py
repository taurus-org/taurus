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

"""This module provides widgets that display the database in a tree format"""
# TODO: tango-centric

from builtins import str, bytes

from taurus.external.qt import Qt
from taurus.core.taurusbasetypes import TaurusElementType, TaurusDevState
import taurus.qt.qtcore.mimetypes
from .taurusmodel import TaurusBaseTreeItem, TaurusBaseModel, TaurusBaseProxyModel


__all__ = ["TaurusTreeDevicePartItem", "TaurusTreeDeviceDomainItem",
           "TaurusTreeDeviceFamilyItem", "TaurusTreeDeviceMemberItem", "TaurusTreeSimpleDeviceItem",
           "TaurusTreeDeviceItem", "TaurusTreeAttributeItem", "TaurusTreeServerNameItem",
           "TaurusTreeServerItem", "TaurusTreeDeviceClassItem", "TaurusDbBaseModel",
           "TaurusDbSimpleDeviceModel", "TaurusDbPlainDeviceModel", "TaurusDbDeviceModel",
           "TaurusDbSimpleDeviceAliasModel",
           "TaurusDbPlainServerModel", "TaurusDbServerModel",
           "TaurusDbDeviceClassModel",
           "TaurusDbBaseProxyModel",
           "TaurusDbDeviceProxyModel", "TaurusDbServerProxyModel", "TaurusDbDeviceClassProxyModel"]

__docformat__ = 'restructuredtext'


ElemType = TaurusElementType


def getElementTypeIcon(*args, **kwargs):
    """Wrapper to prevent loading qtgui when this module is imported"""
    from taurus.qt.qtgui.icon import getElementTypeIcon
    return getElementTypeIcon(*args, **kwargs)


def getElementTypeToolTip(*args, **kwargs):
    """Wrapper to prevent loading qtgui when this module is imported"""
    from taurus.qt.qtgui.icon import getElementTypeToolTip
    return getElementTypeToolTip(*args, **kwargs)


def getElementTypeSize(*args, **kwargs):
    """Wrapper to prevent loading qtgui when this module is imported"""
    from taurus.qt.qtgui.icon import getElementTypeSize
    return getElementTypeSize(*args, **kwargs)


def getDevStateIcon(*args, **kwargs):
    """Wrapper to prevent loading qtgui when this module is imported"""
    from taurus.qt.qtgui.icon import getDevStateIcon
    return getDevStateIcon(*args, **kwargs)


def getDevStateToolTip(*args, **kwargs):
    """Wrapper to prevent loading qtgui when this module is imported"""
    from taurus.qt.qtgui.icon import getDevStateToolTip
    return getDevStateToolTip(*args, **kwargs)


class TaurusTreeDbBaseItem(TaurusBaseTreeItem):
    try:
        # TODO: tango-centric
        import taurus.core.tango

        @staticmethod
        def DisplayFunc(obj):
            from taurus.core.tango.tangodatabase import TangoInfo
            return TangoInfo.name(obj)
    except:
        pass


class TaurusTreeDevicePartItem(TaurusTreeDbBaseItem):
    """A node designed to represent a 'part' (or totality) of a device name"""

    def data(self, index):
        column = index.column()
        if column > 0:
            return

        model = index.model()
        role = model.role(column, self.depth())

        if role == self.role():
            return self._itemData

    def role(self):
        return ElemType.Device


class TaurusTreeDeviceDomainItem(TaurusTreeDevicePartItem):
    """A node designed to represent a the domain part of a device name"""

    DisplayFunc = str

    def role(self):
        return ElemType.Domain


class TaurusTreeDeviceFamilyItem(TaurusTreeDevicePartItem):
    """A node designed to represent a the family part of a device name"""

    DisplayFunc = str

    def role(self):
        return ElemType.Family


class TaurusTreeDeviceMemberItem(TaurusTreeDevicePartItem):
    """A node designed to represent a the member part of a device name"""

    DisplayFunc = str

    def role(self):
        return ElemType.Member


class TaurusTreeSimpleDeviceItem(TaurusTreeDbBaseItem):
    """A node designed to represent a device (without any child nodes)"""

    def hasChildren(self):
        return False

    def childCount(self):
        return 0

    def data(self, index):
        column, model = index.column(), index.model()
        role = model.role(column, self.depth())
        obj = self.itemData()
        if role == ElemType.Device or role == ElemType.Name:
            return obj.name()
        elif role == ElemType.DeviceAlias:
            return obj.alias()
        elif role == ElemType.Server:
            return obj.server().name()
        elif role == ElemType.DeviceClass:
            return obj.klass().name()
        elif role == ElemType.Exported:
            return obj.state()
        elif role == ElemType.Host:
            return obj.host()
        elif role == ElemType.Domain:
            return obj.domain()
        elif role == ElemType.Family:
            return obj.family()
        elif role == ElemType.Member:
            return obj.member()

    def mimeData(self, index):
        return self.itemData().name()

    def role(self):
        return ElemType.Device


class TaurusTreeDeviceItem(TaurusTreeDbBaseItem):
    """A node designed to represent a device"""

    def child(self, row):
        self.updateChilds()
        return super(TaurusTreeDeviceItem, self).child(row)

    def hasChildren(self):
        return True
        nb = super(TaurusTreeDeviceItem, self).childCount()
        if nb > 0:
            return True
        data = self.itemData()
        if data.state() != TaurusDevState.Ready:
            return False
        return True

    def childCount(self):
        nb = super(TaurusTreeDeviceItem, self).childCount()
        if nb > 0:
            return nb
        data = self.itemData()
        if data.state() != TaurusDevState.Ready:
            return 0
        self.updateChilds()
        return super(TaurusTreeDeviceItem, self).childCount()

    def updateChilds(self):
        if len(self._childItems) > 0:
            return
        for attr in self._itemData.attributes():
            c = TaurusTreeAttributeItem(self._model, attr, self)
            self.appendChild(c)
        return

    def data(self, index):
        column, model = index.column(), index.model()
        role = model.role(column, self.depth())
        obj = self.itemData()
        if role == ElemType.Device or role == ElemType.Name:
            return obj.name()
        elif role == ElemType.DeviceAlias:
            return obj.alias()
        elif role == ElemType.Server:
            return obj.server().name()
        elif role == ElemType.DeviceClass:
            return obj.klass().name()
        elif role == ElemType.Exported:
            return obj.state()
        elif role == ElemType.Host:
            return obj.host()
        elif role == ElemType.Domain:
            return obj.domain()
        elif role == ElemType.Family:
            return obj.family()
        elif role == ElemType.Member:
            return obj.member()

    def mimeData(self, index):
        return self.itemData().fullName()

    def role(self):
        return ElemType.Device


class TaurusTreeAttributeItem(TaurusTreeDbBaseItem):
    """A node designed to represent an attribute"""

    def data(self, index):
        column, model = index.column(), index.model()
        role = model.role(column, self.depth())
        if role == ElemType.Attribute or role == ElemType.Name:
            data = self.itemData()
            data_info = data.info()
            ret = data.name()
            if data_info and hasattr(data_info, 'label'):
                ret = "'" + data_info.label + "' (" + ret + ")"
            return ret

    def toolTip(self, index):
        if index.column() > 0:
            return TaurusTreeDbBaseItem.toolTip(self, index)
        data = self.itemData()
        di = data.info()
        if di is None:
            return data.name()
        ret = '<TABLE border="0" cellpadding="1" cellspacing="0">'
        items = dict(
            name="'" + di.label + "' (" + data.name() + ")",
            description=di.description.replace(
                "<", "&lt;").replace(">", "&gt;"),
            unit=di.unit,
            limits="[%s, %s]" % (di.min_value, di.max_value),
            alarms="[%s, %s]" % (di.alarms.min_alarm, di.alarms.max_alarm),
            warnings="[%s, %s]" % (di.alarms.min_warning, di.alarms.max_warning),)

        for id, value in items.items():
            ret += '<TR><TD WIDTH="80" ALIGN="RIGHT" VALIGN="MIDDLE"><B>%s:</B></TD><TD>%s</TD></TR>' % (
                id.capitalize(), value)
        ret += '</TABLE>'
        return ret

    def mimeData(self, index):
        return self.itemData().fullName()

    def role(self):
        return ElemType.Attribute


class TaurusTreeServerNameItem(TaurusTreeDbBaseItem):
    """A node designed to represent the server name part of a server"""

    DisplayFunc = str

    def data(self, index):
        column, model = index.column(), index.model()
        role = model.role(column, self.depth())

        if role == ElemType.ServerName or role == ElemType.Name:
            return self._itemData

    def role(self):
        return ElemType.ServerName


class TaurusTreeServerItem(TaurusTreeDbBaseItem):
    """A node designed to represent a server"""

    def data(self, index):
        column, model = index.column(), index.model()
        role = model.role(column, self.depth())

        if role == ElemType.Server or role == ElemType.Name:
            return self._itemData.name()
        elif role == ElemType.ServerName:
            return self._itemData.serverName()
        elif role == ElemType.ServerInstance:
            return self._itemData.serverInstance()
        elif role == ElemType.Exported:
            return self._itemData.state()
        elif role == ElemType.Host:
            return self._itemData.host()

    def mimeData(self, index):
        return self.itemData().fullName()

    def role(self):
        return ElemType.Server


class TaurusTreeFullServerItem(TaurusTreeDbBaseItem):
    """A node designed to represent a server"""

    def data(self, index):
        column, model = index.column(), index.model()
        role = model.role(column, self.depth())

        if role == ElemType.Server or role == ElemType.Name:
            return self._itemData.fullName()
        elif role == ElemType.ServerName:
            return self._itemData.serverName()
        elif role == ElemType.ServerInstance:
            return self._itemData.fullName()
        elif role == ElemType.Exported:
            return self._itemData.state()
        elif role == ElemType.Host:
            return self._itemData.host()

    def mimeData(self, index):
        return self.itemData().fullName()

    def role(self):
        return ElemType.Server


class TaurusTreeDeviceClassItem(TaurusTreeDbBaseItem):
    """A node designed to represent a device class"""

    def data(self, index):
        column, model = index.column(), index.model()
        role = model.role(column, self.depth())

        if role == ElemType.Name or role == ElemType.DeviceClass:
            return self._itemData.name()

    def mimeData(self, index):
        return self.itemData().fullName()

    def role(self):
        return ElemType.DeviceClass


class TaurusDbBaseModel(TaurusBaseModel):
    """The base class for all Taurus database Qt models.
    By default, this model represents a plain device perspective of the underlying
    database."""

    ColumnNames = "Device", "Alias", "Server", "Class", "Alive", "Host"
    ColumnRoles = (
        ElemType.Device, ElemType.Device), ElemType.DeviceAlias, ElemType.Server, ElemType.DeviceClass, ElemType.Exported, ElemType.Host

    def createNewRootItem(self):
        return TaurusTreeDbBaseItem(self, self.ColumnNames)

    def refresh(self, refresh_source=False):
        data = self.dataSource()
        if refresh_source and data is not None:
            data.refreshCache()
        TaurusBaseModel.refresh(self, refresh_source=refresh_source)

    def roleIcon(self, taurus_role):
        return getElementTypeIcon(taurus_role)

    def columnIcon(self, column):
        return self.roleIcon(self.role(column))

    def roleToolTip(self, taurus_role):
        return getElementTypeToolTip(taurus_role)

    def columnToolTip(self, column):
        return self.roleToolTip(self.role(column))

    def roleSize(self, taurus_role):
        return getElementTypeSize(taurus_role)

    def columnSize(self, column):
        taurus_role = self.role(column)
        s = self.roleSize(taurus_role)
        return s

    def mimeTypes(self):
        return ["text/plain", taurus.qt.qtcore.mimetypes.TAURUS_MODEL_LIST_MIME_TYPE, taurus.qt.qtcore.mimetypes.TAURUS_MODEL_MIME_TYPE]

    def mimeData(self, indexes):
        ret = Qt.QMimeData()
        data = []
        for index in indexes:
            if not index.isValid():
                continue
            #item = index.internalPointer()
            #data = item.mimeData(index)
            #stream << item.mimeData(index)
            tree_item = index.internalPointer()
            mime_data_item = tree_item.mimeData(index)
            if mime_data_item is None:
                continue
            data.append(bytes(mime_data_item, encoding='utf8'))
        ret.setData(
            taurus.qt.qtcore.mimetypes.TAURUS_MODEL_LIST_MIME_TYPE,
            b"\r\n".join(data)
        )
        ret.setText(", ".join(map(str, data)))
        if len(data) == 1:
            ret.setData(
                taurus.qt.qtcore.mimetypes.TAURUS_MODEL_MIME_TYPE, data[0])
        return ret

    def pyData(self, index, role):
        if not index.isValid():
            return None

        item = index.internalPointer()
        row, column, depth = index.row(), index.column(), item.depth()
        taurus_role = self.role(column, depth)

        ret = None
        if role == Qt.Qt.DisplayRole:
            if taurus_role != ElemType.Exported:
                ret = item.data(index)
        elif role == Qt.Qt.DecorationRole:
            if column == 0:
                ret = self.roleIcon(taurus_role)
            if taurus_role == ElemType.Exported:
                state = item.data(index)
                ret = getDevStateIcon(state)
        elif role == Qt.Qt.ToolTipRole:
            ret = item.toolTip(index)
            if ret is None:
                data = item.data(index)
                if data is not None:
                    if taurus_role == ElemType.Exported:
                        ret = getDevStateToolTip(data)
                    else:
                        ret = self.roleToolTip(taurus_role)
        # elif role == Qt.Qt.SizeHintRole:
        #    ret = self.columnSize(column)
        elif role == Qt.Qt.FontRole:
            ret = self.DftFont
        return ret

    def setupModelData(self, data):
        if data is None:
            return

        from taurus.core.tango.tangodatabase import TangoDatabase
        if isinstance(data, TangoDatabase):
            data = data.cache()
        devices = data.devices()

        rootItem = self._rootItem
        for dev_name in data.getDeviceNames():
            dev = devices[dev_name]
            devItem = TaurusTreeSimpleDeviceItem(self, dev, rootItem)
            rootItem.appendChild(devItem)


class TaurusDbSimpleDeviceModel(TaurusDbBaseModel):
    """A Qt model that structures device elements in 1 level tree with
    device name as node leafs. This model contains only 1 column."""

    ColumnNames = "Device",
    ColumnRoles = (ElemType.Device, ElemType.Device),


class TaurusDbSimpleDeviceAliasModel(TaurusDbBaseModel):
    """A Qt model that structures device elements in 1 level tree with
    device alias as node leafs. This model contains only 1 column."""

    ColumnNames = "Alias",
    ColumnRoles = (ElemType.DeviceAlias, ElemType.DeviceAlias),

    def setupModelData(self, data):
        if data is None:
            return

        from taurus.core.tango.tangodatabase import TangoDatabase
        if isinstance(data, TangoDatabase):
            data = data.cache()
        devices = data.devices()

        rootItem = self._rootItem
        for dev_name in data.getDeviceNames():
            dev = devices[dev_name]
            if dev.alias() is not None:
                devItem = TaurusTreeSimpleDeviceItem(self, dev, rootItem)
                rootItem.appendChild(devItem)


class TaurusDbPlainDeviceModel(TaurusDbBaseModel):
    """A Qt model that structures device elements in 1 level tree. Device
    nodes will have attribute child nodes if the device is running."""

    ColumnNames = "Device", "Alias", "Server", "Class", "Alive", "Host"
    ColumnRoles = (ElemType.Device, ElemType.Device,
                   ElemType.Attribute), ElemType.DeviceAlias, ElemType.Server, ElemType.DeviceClass, ElemType.Exported, ElemType.Host

    def setupModelData(self, data):
        if data is None:
            return

        from taurus.core.tango.tangodatabase import TangoDatabase
        if isinstance(data, TangoDatabase):
            data = data.cache()
        devices = data.devices()

        rootItem = self._rootItem
        for dev_name in data.getDeviceNames():
            dev = devices[dev_name]
            devItem = TaurusTreeDeviceItem(self, dev, rootItem)
            rootItem.appendChild(devItem)


class TaurusDbDeviceModel(TaurusDbBaseModel):
    """A Qt model that structures device elements in a 3 level tree organized
       as:

           - <domain>
           - <family>
           - <member>"""
    ColumnRoles = (ElemType.Device, ElemType.Domain, ElemType.Family, ElemType.Member,
                   ElemType.Attribute), ElemType.DeviceAlias, ElemType.Server, ElemType.DeviceClass, ElemType.Exported, ElemType.Host

    def setupModelData(self, data):
        if data is None:
            return
        try:
            # TODO: Tango-centric
            # TODO: is this try needed? (not done in, e.g. TaurusDbPlainDeviceModel)
            from taurus.core.tango.tangodatabase import TangoDatabase
        except ImportError:
            return
        if isinstance(data, TangoDatabase):
            data = data.deviceTree()

        rootItem = self._rootItem
        for domain in data:
            families = data[domain]
            domainItem = TaurusTreeDeviceDomainItem(
                self, domain.upper(), rootItem)
            for family in families:
                members = families[family]
                familyItem = TaurusTreeDeviceFamilyItem(
                    self, family.upper(), domainItem)
                for member in members:
                    dev = members[member]
                    memberItem = TaurusTreeDeviceItem(
                        self, dev, parent=familyItem)
                    familyItem.appendChild(memberItem)
                domainItem.appendChild(familyItem)
            rootItem.appendChild(domainItem)


class TaurusDbPlainServerModel(TaurusDbBaseModel):
    ColumnNames = "Server", "Alive", "Host"
    ColumnRoles = (ElemType.Server,
                   ElemType.ServerInstance), ElemType.Exported, ElemType.Host

    def setupModelData(self, data):
        if data is None:
            return

        from taurus.core.tango.tangodatabase import TangoDatabase
        if isinstance(data, TangoDatabase):
            data = data.cache()

        servers = data.servers()
        rootItem = self._rootItem

        for server_name, server in servers.items():
            serverInstanceItem = TaurusTreeFullServerItem(
                self, server, rootItem)
            rootItem.appendChild(serverInstanceItem)


class TaurusDbServerModel(TaurusDbBaseModel):
    """A Qt model that structures server elements in a tree organized
    as:

        - <Server name>
        - <Server instance>
        - <Class>
        - <Device>
        - <Attribute>"""

    ColumnNames = "Server", "Alive", "Host"
    ColumnRoles = (ElemType.Server, ElemType.ServerName, ElemType.ServerInstance,
                   ElemType.DeviceClass, ElemType.Device, ElemType.Attribute), ElemType.Exported, ElemType.Host

    def setupModelData(self, data):
        if data is None:
            return

        from taurus.core.tango.tangodatabase import TangoDatabase
        if isinstance(data, TangoDatabase):
            data = data.cache()

        servers, klasses, devices = data.servers(), data.klasses(), data.devices()
        rootItem = self._rootItem
        server_dict = {}

        server_names = data.getServerNames()
        for server_name in server_names:
            server = servers[server_name]
            name, instance = server.serverName(), server.serverInstance()

            serverNameItem = server_dict.get(name)
            if serverNameItem is None:
                serverNameItem = TaurusTreeServerNameItem(self, name, rootItem)
                rootItem.appendChild(serverNameItem)
                server_dict[name] = serverNameItem
                # rootItem.appendChild(serverNameItem)

            serverInstanceItem = TaurusTreeServerItem(
                self, server, serverNameItem)
            serverNameItem.appendChild(serverInstanceItem)

            klass_names = server.getClassNames()
            device_names = server.getDeviceNames()
            for klass_name in klass_names:
                klass = klasses[klass_name]
                klassItem = TaurusTreeDeviceClassItem(
                    self, klass, serverInstanceItem)
                serverInstanceItem.appendChild(klassItem)
                for dev_name in device_names:
                    dev = devices[dev_name]
                    if dev.klass() == klass:
                        devItem = TaurusTreeDeviceItem(self, dev, klassItem)
                        klassItem.appendChild(devItem)


class TaurusDbDeviceClassModel(TaurusDbBaseModel):
    """A Qt model that structures class elements in a tree organized as:

       * <Class>
           * <Device>
               * <Attribute>"""
    ColumnNames = "Class", "Alive", "Host"
    ColumnRoles = (ElemType.DeviceClass, ElemType.DeviceClass,
                   ElemType.Device, ElemType.Attribute), ElemType.Exported, ElemType.Host

    def setupModelData(self, data):
        if data is None:
            return

        from taurus.core.tango.tangodatabase import TangoDatabase
        if isinstance(data, TangoDatabase):
            data = data.cache()

        rootItem = self._rootItem
        klasses, devices = data.klasses(), data.devices()
        dev_nb = 0
        for klass_name in data.getClassNames():
            klass = klasses[klass_name]
            klassItem = TaurusTreeDeviceClassItem(self, klass, rootItem)
            for dev_name in klass.getDeviceNames():
                dev_nb += 1
                dev = devices[dev_name]
                devItem = TaurusTreeDeviceItem(self, dev, klassItem)
                klassItem.appendChild(devItem)
            rootItem.appendChild(klassItem)


class TaurusDbBaseProxyModel(TaurusBaseProxyModel):
    pass


class TaurusDbDeviceProxyModel(TaurusDbBaseProxyModel):
    """A Qt filter & sort model for model for the taurus models:
           - TaurusDbBaseModel
           - TaurusDbDeviceModel
           - TaurusDbSimpleDeviceModel
           - TaurusDbPlainDeviceModel"""

    def filterAcceptsRow(self, sourceRow, sourceParent):
        sourceModel = self.sourceModel()
        idx = sourceModel.index(sourceRow, 0, sourceParent)
        treeItem = idx.internalPointer()
        regexp = self.filterRegExp()

        # if domain node, check if it will potentially have any children
        if isinstance(treeItem, TaurusTreeDeviceDomainItem):
            domain = treeItem.display()
            devices = sourceModel.getDomainDevices(domain)
            for device in devices:
                if self.deviceMatches(device, regexp):
                    return True
            return False

        # if family node, check if it will potentially have any children
        if isinstance(treeItem, TaurusTreeDeviceFamilyItem):
            domain = treeItem.parent().display()
            family = treeItem.display()
            devices = sourceModel.getFamilyDevices(domain, family)
            for device in devices:
                if self.deviceMatches(device, regexp):
                    return True
            return False

        if isinstance(treeItem, TaurusTreeDeviceItem) or \
           isinstance(treeItem, TaurusTreeSimpleDeviceItem) or \
           isinstance(treeItem, TaurusTreeDeviceMemberItem):
            device = treeItem.itemData()
            return self.deviceMatches(device, regexp)
        return True

    def deviceMatches(self, device, regexp):
        name = device.name()

        if regexp.indexIn(name) != -1:
            return True
        name = device.alias()
        if name is None:
            return False
        return regexp.indexIn(name) != -1


class TaurusDbServerProxyModel(TaurusDbBaseProxyModel):
    """A Qt filter & sort model for the TaurusDbServerModel"""

    def filterAcceptsRow(self, sourceRow, sourceParent):
        sourceModel = self.sourceModel()
        idx = sourceModel.index(sourceRow, 0, sourceParent)
        treeItem = idx.internalPointer()
        regexp = self.filterRegExp()

        # if server name node, check if it will potentially have any children
        if isinstance(treeItem, TaurusTreeServerNameItem):
            serverName = treeItem.display()
            serverInstances = sourceModel.getServerNameInstances(serverName)
            for serverInstance in serverInstances:
                if regexp.indexIn(serverInstance.name()) != -1:
                    return True
            return False

        if isinstance(treeItem, TaurusTreeServerItem):
            # return treeItem.qdisplay().contains(regexp)
            return regexp.indexIn(treeItem.display()) != -1

        return True


class TaurusDbDeviceClassProxyModel(TaurusDbBaseProxyModel):
    """A Qt filter & sort model for the TaurusDbDeviceClassModel"""

    def filterAcceptsRow(self, sourceRow, sourceParent):
        sourceModel = self.sourceModel()
        idx = sourceModel.index(sourceRow, 0, sourceParent)
        treeItem = idx.internalPointer()

        if not isinstance(treeItem, TaurusTreeDeviceClassItem):
            return True

        regexp = self.filterRegExp()

        # return treeItem.qdisplay().contains(regexp)
        return regexp.indexIn(treeItem.display()) != -1
