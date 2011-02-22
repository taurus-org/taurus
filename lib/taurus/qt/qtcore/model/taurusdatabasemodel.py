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

"""This module provides widgets that display the database in a tree format"""

__all__ = ["TaurusTreeItem", "TaurusTreeDevicePartItem", "TaurusTreeDeviceDomainItem",
    "TaurusTreeDeviceFamilyItem", "TaurusTreeDeviceMemberItem", "TaurusTreeSimpleDeviceItem",
    "TaurusTreeDeviceItem", "TaurusTreeAttributeItem", "TaurusTreeServerNameItem",
    "TaurusTreeServerItem", "TaurusTreeDeviceClassItem", "TaurusDbBaseModel",
    "TaurusDbSimpleDeviceModel", "TaurusDbPlainDeviceModel", "TaurusDbDeviceModel",
    "TaurusDbServerModel", "TaurusDbDeviceClassModel", "TaurusDbBaseProxyModel",
    "TaurusDbDeviceProxyModel", "TaurusDbServerProxyModel", "TaurusDbDeviceClassProxyModel"]

__docformat__ = 'restructuredtext'

from PyQt4 import Qt

import taurus.core
import taurus.qt.qtcore.mimetypes

ElemType = taurus.core.TaurusElementType
DevHealth = taurus.core.TaurusSWDevHealth

def getElementTypeIcon(*args, **kwargs):
    """Wrapper to prevent loading qtgui when this module is imported"""
    import taurus.qt.qtgui.resource
    return taurus.qt.qtgui.resource.getElementTypeIcon(*args, **kwargs)

def getElementTypeToolTip(*args, **kwargs):
    """Wrapper to prevent loading qtgui when this module is imported"""
    import taurus.qt.qtgui.resource
    return taurus.qt.qtgui.resource.getElementTypeToolTip(*args, **kwargs)

def getElementTypeSize(*args, **kwargs):
    """Wrapper to prevent loading qtgui when this module is imported"""
    import taurus.qt.qtgui.resource
    return taurus.qt.qtgui.resource.getElementTypeSize(*args, **kwargs)

def getSWDevHealthIcon(*args, **kwargs):
    """Wrapper to prevent loading qtgui when this module is imported"""
    import taurus.qt.qtgui.resource
    return taurus.qt.qtgui.resource.getSWDevHealthIcon(*args, **kwargs)

def getSWDevHealthToolTip(*args, **kwargs):
    """Wrapper to prevent loading qtgui when this module is imported"""
    import taurus.qt.qtgui.resource
    return taurus.qt.qtgui.resource.getSWDevHealthToolTip(*args, **kwargs)


class TaurusTreeItem(object):
    """A generic node"""
    
    DisplayFunc = taurus.core.TaurusInfo.name

    def __init__(self, model, data, parent = None):
        self._model = model
        self._itemData = data
        self._parentItem = parent
        self._childItems = []
        self._depth = self._calcDepth()
        
    def itemData(self):
        """The internal itemData object
        
        :return: (object) object holding the data of this item
        """
        return self._itemData
        
    def depth(self):
        """Depth of the node in the hierarchy
        
        :return: (int) the node depth
        """
        return self._depth
    
    def appendChild(self, child):
        """Adds a new child node
        
        :param child: (TaurusTreeItem) child to be added
        """
        self._childItems.append(child)
    
    def child(self, row):
        """Returns the child in the given row
        
        :return: (TaurusTreeItem) the child node for the given row"""
        return self._childItems[row]
    
    def childCount(self):
        """Returns the number of childs for this node
        
        :return: (int) number of childs for this node
        """
        return len(self._childItems)
    
    def hasChildren(self):
        return len(self._childItems) > 0
    
    def data(self, index):
        """Returns the data of this node for the given index
        
        :return: (object) the data for the given index
        """
        return self._itemData[index.column()]
    
    def setData(self, data):
        """Sets the node data
        
        :param data: (object) the data to be associated with this node
        """
        self._itemData = data
    
    def parent(self):
        """Returns the parent node or None if no parent exists
        
        :return: (TaurusTreeItem) the parent node
        """
        return self._parentItem
    
    def row(self):
        """Returns the row for this node
        
        :return: (int) row number for this node
        """
        if self._parentItem is None:
            return 0
        return self._parentItem._childItems.index(self)

    def _calcDepth(self):
        d = 0
        n = self.parent()
        while n is not None:
            n = n.parent()
            d += 1
        return d
    
    def toolTip(self):
        return

    def display(self):
        """Returns the display string for this node
        
        :return: (str) the node's display string"""
        if not hasattr(self, "_display"):
            if self._itemData is None:
                return None
            self._display = self.DisplayFunc(self._itemData)
        return self._display

    def qdisplay(self):
        """Returns the display QString for this node
        
        :return: (Qt.QString) the node's display string"""
        if not hasattr(self, "_qdisplay"):
            d = self.display()
            if d is None:
                return None
            self._qdisplay = Qt.QString(d)
        return self._qdisplay

    def mimeData(self, index):
        return self.data(index)

    def role(self):
        """Returns the prefered role for the item.
        This implementation returns taurus.core.TaurusElementType.Unknown
        
        This method should be able to return any kind of python object as long
        as the model that is used is compatible.
        
        :return: (taurus.core.TaurusElementType) the role in form of element type"""
        return ElemType.Unknown


class TaurusTreeDevicePartItem(TaurusTreeItem):
    """A node designed to represent a 'part' (or totality) of a device name"""

    def data(self, index):
        column = index.column()
        if column > 0: return
        
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


class TaurusTreeSimpleDeviceItem(TaurusTreeItem):
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
            return obj.health()
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


class TaurusTreeDeviceItem(TaurusTreeItem):
    """A node designed to represent a device"""
    
    SearchForAttributeHealth = DevHealth.Exported, DevHealth.ExportedAlive, \
                               DevHealth.NotExportedAlive

    def child(self, row):
        self.updateChilds()
        return super(TaurusTreeDeviceItem, self).child(row)

    def hasChildren(self):
        return True
        nb = super(TaurusTreeDeviceItem, self).childCount()
        if nb > 0:
            return True
        data = self.itemData()
        if not data.health() in self.SearchForAttributeHealth:
            return False
        return True
    
    def childCount(self):
        nb = super(TaurusTreeDeviceItem, self).childCount()
        if nb > 0:
            return nb
        data = self.itemData()
        if not data.health() in self.SearchForAttributeHealth:
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
            return obj.health()
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


class TaurusTreeAttributeItem(TaurusTreeItem):
    """A node designed to represent an attribute"""
    
    def data(self, index):
        column, model = index.column(), index.model()
        role = model.role(column, self.depth())
        if role == ElemType.Attribute or role == ElemType.Name:
            return self._itemData.name()

    def mimeData(self, index):
        return self.itemData().fullName()

    def role(self):
        return ElemType.Attribute

        
class TaurusTreeServerNameItem(TaurusTreeItem):
    """A node designed to represent the server name part of a server"""
    
    DisplayFunc = str
    
    def data(self, index):
        column, model = index.column(), index.model()
        role = model.role(column, self.depth())
        
        if role == ElemType.ServerName or role == ElemType.Name:
            return self._itemData

    def role(self):
        return ElemType.ServerName


class TaurusTreeServerItem(TaurusTreeItem):
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
            return self._itemData.health()
        elif role == ElemType.Host:
            return self._itemData.host()

    def mimeData(self, index):
        return self.itemData().fullName()

    def role(self):
        return ElemType.Server


class TaurusTreeDeviceClassItem(TaurusTreeItem):
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


class TaurusDbBaseModel(Qt.QAbstractItemModel):
    """The base class for all Taurus database Qt models.
    By default, this model represents a plain device perspective of the underlying
    database."""
    
    ColumnNames = "Device", "Alias", "Server", "Class", "Alive", "Host"
    ColumnRoles = (ElemType.Device, ElemType.Device), ElemType.DeviceAlias, ElemType.Server, ElemType.DeviceClass, ElemType.Exported, ElemType.Host
    
    DftFont = Qt.QFont("Mono", 8)
    
    def __init__(self, parent=None, data=None):
        super(TaurusDbBaseModel, self).__init__(parent)
        # if qt < 4.6, beginResetModel and endResetModel don't exist. In this
        # case we set beginResetModel to be an empty function and endResetModel
        # to be reset.
        if not hasattr(Qt.QAbstractItemModel, "beginResetModel"):
            self.beginResetModel = lambda : None
            self.endResetModel = self.reset
        self._filters = []
        self._selectables = [ self.ColumnRoles[0][-1] ]
        self.setDataSource(data)

    def __getattr__(self, name):
        return getattr(self.dataSource(), name)

    def dataSource(self):
        return self._data_src

    def setDataSource(self, data):
        self.beginResetModel()
        self._data_src = data
        self._rootItem = TaurusTreeItem(self, self.ColumnNames)
        self.setupModelData(data)
        self.endResetModel()
        
    def refresh(self, refresh_source=False):
        self.beginResetModel()
        self._rootItem = TaurusTreeItem(self, self.ColumnNames)
        data = self._data_src
        if refresh_source and data is not None:
            data.refreshCache()
        self.setupModelData(data)
        self.endResetModel()

    def setSelectables(self, seq_elem_types):
        self._selectables = seq_elem_types
    
    def selectables(self):
        return self._selectables

    def role(self, column, depth=0):
        cr = self.ColumnRoles
        if column == 0:
            return cr[0][depth]
        return self.ColumnRoles[column]

    def columnCount(self, parent = Qt.QModelIndex()):
        return len(self.ColumnRoles)
    
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
            if not index.isValid(): continue
            #item = index.internalPointer()
            #data = item.mimeData(index)
            #stream << item.mimeData(index)
            tree_item = index.internalPointer()
            mime_data_item = tree_item.mimeData(index)
            if mime_data_item is None:
                continue
            data.append(mime_data_item)
        ret.setData(taurus.qt.qtcore.mimetypes.TAURUS_MODEL_LIST_MIME_TYPE, "\r\n".join(data))
        ret.setText(", ".join(data))
        if len(data)==1:
            ret.setData(taurus.qt.qtcore.mimetypes.TAURUS_MODEL_MIME_TYPE, str(data[0]))
        return ret

    def data(self, index, role):
        ret = self.pyData(index, role)
        if ret is None:
            ret = Qt.QVariant()
        else:
            ret = Qt.QVariant(ret)
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
                health = item.data(index)
                ret = getSWDevHealthIcon(health)
        elif role == Qt.Qt.ToolTipRole:
            data = item.data(index)
            if data is not None:
                if taurus_role == ElemType.Exported:
                    ret = getSWDevHealthToolTip(data)
                else:
                    ret = self.roleToolTip(taurus_role)
        #elif role == Qt.Qt.SizeHintRole:
        #    ret = self.columnSize(column)
        elif role == Qt.Qt.FontRole:
            ret = self.DftFont
        return ret
        
    def flags(self, index):
        if not index.isValid():
            return 0
        
        ret = Qt.Qt.ItemIsEnabled | Qt.Qt.ItemIsDragEnabled
        
        item = index.internalPointer()
        column, depth = index.column(), item.depth()
        taurus_role = self.role(column, depth)
        
        if taurus_role in self.selectables():
            ret |= Qt.Qt.ItemIsSelectable	
        return ret

    def headerData(self, section, orientation, role=Qt.Qt.DisplayRole):
        ret = None
        if orientation == Qt.Qt.Horizontal:
            if role == Qt.Qt.TextAlignmentRole:
                ret = int(Qt.Qt.AlignLeft | Qt.Qt.AlignVCenter)
            elif role == Qt.Qt.DisplayRole:
                ret = self.ColumnNames[section]
            elif role == Qt.Qt.SizeHintRole:
                ret = Qt.QSize(self.columnSize(section))
                ret.setHeight(24)
            elif role == Qt.Qt.ToolTipRole:
                ret = self.columnToolTip(section)
            elif role == Qt.Qt.DecorationRole:
                ret = self.columnIcon(section)
                
        return Qt.QVariant(ret)
    
    def index(self, row, column, parent = Qt.QModelIndex()):
        if not self.hasIndex(row, column, parent):
            return Qt.QModelIndex()
        if not parent.isValid():
            parentItem = self._rootItem
        else:
            parentItem = parent.internalPointer()
        childItem = parentItem.child(row)
        if childItem:
            return self.createIndex(row, column, childItem)
        
        return Qt.QModelIndex()
    
    def parent(self, index):
        if not index.isValid():
            return Qt.QModelIndex()
        
        childItem = index.internalPointer()
        parentItem = childItem.parent()
        
        if parentItem == self._rootItem:
            return Qt.QModelIndex()
        
        return self.createIndex(parentItem.row(), 0, parentItem)
        
    def rowCount(self, parent = Qt.QModelIndex()):
        if parent.column() > 0:
            return 0
        
        if not parent.isValid():
            parentItem = self._rootItem
        else:
            parentItem = parent.internalPointer()
        return parentItem.childCount()

    def hasChildren(self, parent = Qt.QModelIndex()):
        if parent.column() > 0:
            return 0
        if not parent.isValid():
            parentItem = self._rootItem
        else:
            parentItem = parent.internalPointer()
        return parentItem.hasChildren()

    def setupModelData(self, data):
        if data is None:
            return
        if isinstance(data, taurus.core.TaurusDatabase):
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
    
    
class TaurusDbPlainDeviceModel(TaurusDbBaseModel):
    """A Qt model that structures device elements in 1 level tree. Device
    nodes will have attribute child nodes if the device is running."""
    
    ColumnNames = "Device", "Alias", "Server", "Class", "Alive", "Host"
    ColumnRoles = (ElemType.Device, ElemType.Device, ElemType.Attribute), ElemType.DeviceAlias, ElemType.Server, ElemType.DeviceClass, ElemType.Exported, ElemType.Host

    def setupModelData(self, data):
        if data is None:
            return
        if isinstance(data, taurus.core.TaurusDatabase):
            data = data.cache()
        devices = data.devices()
        
        rootItem = self._rootItem
        for dev_name in data.getDeviceNames():
            dev = devices[dev_name]
            devItem = TaurusTreeDeviceItem(self, dev, rootItem)
            rootItem.appendChild(devItem)
            

class TaurusDbDeviceModel(TaurusDbBaseModel):
    """A Qt model that structures device elements is a 3 level tree organized
       as:
       - <domain>
           - <family>
               - <member>
    """
    ColumnRoles = (ElemType.Device, ElemType.Domain, ElemType.Family, ElemType.Member, ElemType.Attribute), ElemType.DeviceAlias, ElemType.Server, ElemType.DeviceClass, ElemType.Exported, ElemType.Host

    def setupModelData(self, data):
        if data is None:
            return
        if isinstance(data, taurus.core.TaurusDatabase):
            data = data.deviceTree()
            
        rootItem = self._rootItem
        for domain in sorted(data.keys()):
            families = data[domain]
            domainItem = TaurusTreeDeviceDomainItem(self, domain.upper(), rootItem)
            for family in sorted(families.keys()):
                members = families[family]
                familyItem = TaurusTreeDeviceFamilyItem(self, family.upper(), domainItem)
                for member in sorted(members.keys()):
                    dev = members[member]
                    memberItem = TaurusTreeDeviceItem(self, dev, parent=familyItem)
                    familyItem.appendChild(memberItem)
                domainItem.appendChild(familyItem)
            rootItem.appendChild(domainItem)


class TaurusDbServerModel(TaurusDbBaseModel):
    """A Qt model that structures server elements in a tree organized as:
       - <Server name>
           - <Server instance>
               - <Class>
                   - <Device>
                       - <Attribute>
    """

    ColumnNames = "Server", "Alive", "Host"
    ColumnRoles = (ElemType.Server, ElemType.ServerName, ElemType.ServerInstance, ElemType.DeviceClass, ElemType.Device, ElemType.Attribute), ElemType.Exported, ElemType.Host
    
    def setupModelData(self, data):
        if data is None:
            return

        if isinstance(data, taurus.core.TaurusDatabase):
            data = data.cache()
        
        servers, klasses, devices = data.servers(), data.klasses(), data.devices()
        rootItem = self._rootItem
        server_dict = {}
        
        server_names = data.getServerNames()
        for server_name in data.getServerNames():
            server = servers[server_name]
            name, instance = server.serverName(), server.serverInstance()
            
            serverNameItem = server_dict.get(name)
            if serverNameItem is None:
                serverNameItem = TaurusTreeServerNameItem(self, name, rootItem)
                rootItem.appendChild(serverNameItem)
                server_dict[name] = serverNameItem
                #rootItem.appendChild(serverNameItem)
            
            serverInstanceItem = TaurusTreeServerItem(self, server, serverNameItem)
            serverNameItem.appendChild(serverInstanceItem)
            
            klass_names = server.getClassNames()
            device_names = server.getDeviceNames()
            for klass_name in klass_names:
                klass = klasses[klass_name]
                klassItem = TaurusTreeDeviceClassItem(self, klass, serverInstanceItem)
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
    ColumnRoles = (ElemType.DeviceClass, ElemType.DeviceClass, ElemType.Device, ElemType.Attribute), ElemType.Exported, ElemType.Host
    
    def setupModelData(self, data):
        if data is None:
            return
        
        if isinstance(data, taurus.core.TaurusDatabase):
            data = data.cache()
        
        rootItem = self._rootItem
        klasses, devices = data.klasses(), data.devices()
        dev_nb = 0
        for klass_name in data.getClassNames():
            klass = klasses[klass_name]
            klassItem = TaurusTreeDeviceClassItem(self, klass, rootItem)
            for dev_name in klass.getDeviceNames():
                dev_nb+=1
                dev = devices[dev_name]
                devItem = TaurusTreeDeviceItem(self, dev, klassItem)
                klassItem.appendChild(devItem)
            rootItem.appendChild(klassItem)


class TaurusDbBaseProxyModel(Qt.QSortFilterProxyModel):
    """A taurus database base Qt filter & sort model"""
     
    def __init__(self, parent=None):
        super(TaurusDbBaseProxyModel, self).__init__(parent)
        
        # filter configuration
        self.setFilterCaseSensitivity(Qt.Qt.CaseInsensitive)
        self.setFilterKeyColumn(0)
        self.setFilterRole(Qt.Qt.DisplayRole)
        
        # sort configuration
        self.setSortCaseSensitivity(Qt.Qt.CaseInsensitive)
        self.setSortRole(Qt.Qt.DisplayRole)
        
        # general configuration
        self.setDynamicSortFilter(True)
        self.sort(0, Qt.Qt.AscendingOrder)
        
    def __getattr__(self, name):
        return getattr(self.sourceModel(), name)


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
        expr = self.filterRegExp()
        
        # if domain node, check if it will potentially have any children
        if isinstance(treeItem, TaurusTreeDeviceDomainItem):
            domain = treeItem.display()
            devices = sourceModel.getDomainDevices(domain)
            for d in devices:
                #if expr.exactMatch(d.name()):
                if Qt.QString(d.name()).contains(expr):
                    return True
            return False
        
        # if family node, check if it will potentially have any children
        if isinstance(treeItem, TaurusTreeDeviceFamilyItem):
            domain = treeItem.parent().display()
            family = treeItem.display()
            devices = sourceModel.getFamilyDevices(domain, family)
            for device in devices:
                #if expr.exactMatch(d.name()):
                if Qt.QString(device.name()).contains(expr):
                    return True
            return False
        
        if isinstance(treeItem, TaurusTreeDeviceItem) or \
           isinstance(treeItem, TaurusTreeSimpleDeviceItem) or \
           isinstance(treeItem, TaurusTreeDeviceMemberItem):
            #return expr.exactMatch(treeItem.qdisplay())
            return treeItem.qdisplay().contains(expr)
        
        return True


class TaurusDbServerProxyModel(TaurusDbBaseProxyModel):
    """A Qt filter & sort model for the TaurusDbServerModel"""
    
    def filterAcceptsRow(self, sourceRow, sourceParent):
        sourceModel = self.sourceModel()
        idx = sourceModel.index(sourceRow, 0, sourceParent)
        treeItem = idx.internalPointer()
        expr = self.filterRegExp()
        
        # if server name node, check if it will potentially have any children
        if isinstance(treeItem, TaurusTreeServerNameItem):
            serverName = treeItem.display()
            serverInstances = sourceModel.getServerNameInstances(serverName)
            for serverInstance in serverInstances:
                if Qt.QString(serverInstance.name()).contains(expr):
                    return True
            return False
        
        if isinstance(treeItem, TaurusTreeServerItem):
            return treeItem.qdisplay().contains(expr)

        return True


class TaurusDbDeviceClassProxyModel(TaurusDbBaseProxyModel):
    """A Qt filter & sort model for the TaurusDbDeviceClassModel"""
    
    def filterAcceptsRow(self, sourceRow, sourceParent):
        sourceModel = self.sourceModel()
        idx = sourceModel.index(sourceRow, 0, sourceParent)
        treeItem = idx.internalPointer()

        if not isinstance(treeItem, TaurusTreeDeviceClassItem):
            return True
        
        expr = self.filterRegExp()

        return treeItem.qdisplay().contains(expr)
