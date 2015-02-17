#!/usr/bin/env python

##############################################################################
##
## This file is part of Sardana
##
## http://www.sardana-controls.org/
##
## Copyright 2011 CELLS / ALBA Synchrotron, Bellaterra, Spain
##
## Sardana is free software: you can redistribute it and/or modify
## it under the terms of the GNU Lesser General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## Sardana is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU Lesser General Public License for more details.
##
## You should have received a copy of the GNU Lesser General Public License
## along with Sardana.  If not, see <http://www.gnu.org/licenses/>.
##
##############################################################################

"""This module contains a taurus text editor widget."""

__all__ = ["SardanaBaseElementModel", "SardanaElementTypeModel",
           "SardanaElementPlainModel", "SardanaBaseProxyModel",
           "SardanaTypeProxyModel",
           "SardanaBaseTreeItem", "SardanaRootTreeItem",
           "SardanaElementTreeItem", "SardanaTypeTreeItem",
           "SardanaEnvironmentModel"]

__docformat__ = 'restructuredtext'

try:
    import pygments
    from pygments import highlight
    from pygments.formatters import HtmlFormatter
    from pygments.lexers import PythonLexer, PythonTracebackLexer
except:
    pygments = None

from taurus.core.taurusdevice import TaurusDevice
from taurus.external.qt import Qt
from taurus.core.util.enumeration import Enumeration
from taurus.qt.qtcore.model import TaurusBaseTreeItem, TaurusBaseModel, \
    TaurusBaseProxyModel
from taurus.qt.qtcore.mimetypes import TAURUS_MODEL_LIST_MIME_TYPE, \
    TAURUS_MODEL_MIME_TYPE

_MOD, _CLS, _FNC, _TNG = ":/python-module.png", ":/class.png", ":/function.png", ":/tango.png"

TYPE_MAP = {
    "ControllerLibrary"    : ("Controller libraries", _MOD, "Controller library",),
    "ControllerClass"      : ("Controller classes", _CLS, "Controller class",),
    "Controller"           : ("Controllers", _TNG, "Controller",),
    "Motor"                : ("Motors", _TNG, "Motor",),
    "PseudoMotor"          : ("Pseudo motors", _TNG, "Pseudo Motor",),
    "CTExpChannel"         : ("Counter/Timers", _TNG, "Counter/Timer experiment channel",),
    "CounterTimer"         : ("Counter/Timers", _TNG, "Counter/Timer experiment channel",),
    "ZeroDExpChannel"      : ("0D channels", _TNG, "0D experiment channel",),
    "OneDExpChannel"       : ("1D channels", _TNG, "1D experiment channel",),
    "TwoDExpChannel"       : ("2D channels", _TNG, "2D experiment channel",),
    "MotorGroup"           : ("Motor groups", _TNG, "Motor group",),
    "MeasurementGroup"     : ("Measurement groups", _TNG, "Measurement group",),
    "CommunicationChannel" : ("Communication channels", _TNG, "Communication channel",),
    "MacroLibrary"         : ("Macro libraries", _MOD, "Macro library",),
    "MacroClass"           : ("Macro classes", _CLS, "Macro class",),
    "Instrument"           : ("Instruments", _TNG, "Instrument",),
    "MacroFunction"        : ("Macro functions", _FNC, "Macro function",),
}

def getElementTypeLabel(t):
    return TYPE_MAP.get(t, (t,))[0]

def getElementTypeIcon(t):
    import taurus.qt.qtgui.resource
    try:
        return taurus.qt.qtgui.resource.getIcon(TYPE_MAP.get(t, (None, _TNG))[1])
    except:
        return None

def getElementTypeSize(t):
    return Qt.QSize(200, 24)

def getElementTypeToolTip(t):
    return TYPE_MAP.get(t, (None, None, 'no information'))[2]


class SardanaBaseTreeItem(TaurusBaseTreeItem):
    """A generic node"""

    def data(self, index):
        """Returns the data of this node for the given index
        
        :return: (object) the data for the given index
        """
        if index.column() > 0:
            return None
        return getElementTypeLabel(self._itemData)

    def role(self):
        """Returns the prefered role for the item.
        This implementation returns taurus.core.taurusbasetypes.TaurusElementType.Unknown
        
        This method should be able to return any kind of python object as long
        as the model that is used is compatible.
        
        :return: the role in form of element type"""
        return 'type'


class SardanaRootTreeItem(SardanaBaseTreeItem):
    pass


class SardanaTypeTreeItem(SardanaBaseTreeItem):
    pass


class SardanaElementTreeItem(SardanaBaseTreeItem):

    def role(self):
        return self.itemData().type

    def data(self, index):
        column, model = index.column(), index.model()
        role = model.role(column, self.depth())
        obj = self.itemData()
        if role == "parent":
            if hasattr(obj, "klass"):
                return obj.klass
            if hasattr(obj, "module"):
                return obj.module
            if hasattr(obj, "controller"):
                return obj.controller
            if hasattr(obj, "parent"):
                return obj.parent
            return None
        return getattr(obj, role)

    def toolTip(self, index):
        if index.column() > 0:
            return self.data(index)
        obj = self.itemData()
        if hasattr(obj, "exc_info") and obj.exc_info is not None:
            html_orig = '<html><head><style type="text/css">{style}' \
                        '</style></head><body>'
            formatter, style = None, ""
            if pygments is not None:
                formatter = HtmlFormatter()
                style = formatter.get_style_defs()
            txt = html_orig.format(style=style)
            if formatter is None:
                txt += "<pre>%s</pre>" % obj.exc_info
            else:
                txt += highlight(obj.exc_info, PythonTracebackLexer(),
                                 formatter)
            txt += "</body></html>"
        else:
            txt = "{0} {1}".format(getElementTypeToolTip(obj.type), obj.name)
        return txt

    def icon(self, index):
        if index.column() > 0:
            return None
        return getElementTypeIcon(self.itemData().type)


class SardanaBaseElementModel(TaurusBaseModel):

    ColumnNames = ["Elements", "Controller/Module/Parent"]
    ColumnRoles = ('Root', 'type', 'name', 'name'), "parent"

    def __init__(self, parent=None, data=None):
        TaurusBaseModel.__init__(self, parent=parent, data=data)
        self.setSelectables(self.ColumnRoles[0])

    def setDataSource(self, data_source):
        old_ds = self.dataSource()
        if old_ds is not None:
            Qt.QObject.disconnect(old_ds, Qt.SIGNAL('elementsChanged'),
                                  self.on_elements_changed)
        if data_source is not None:
            Qt.QObject.connect(data_source, Qt.SIGNAL('elementsChanged'),
                               self.on_elements_changed)
        TaurusBaseModel.setDataSource(self, data_source)

    def on_elements_changed(self):
        self.refresh()

    def createNewRootItem(self):
        return SardanaRootTreeItem(self, self.ColumnNames)

    def roleIcon(self, role):
        return getElementTypeIcon(role)

    def columnIcon(self, column):
        return self.roleIcon(self.role(column))

    def roleToolTip(self, role):
        return getElementTypeToolTip(role)

    def columnToolTip(self, column):
        return self.roleToolTip(self.role(column))

    def roleSize(self, role):
        return getElementTypeSize(role)

    def columnSize(self, column):
        role = self.role(column)
        s = self.roleSize(role)
        return s

    def mimeTypes(self):
        return "text/plain", TAURUS_MODEL_LIST_MIME_TYPE, TAURUS_MODEL_MIME_TYPE

    def mimeData(self, indexes):
        ret = Qt.QMimeData()
        data = []
        for index in indexes:
            if not index.isValid(): continue
            tree_item = index.internalPointer()
            mime_data_item = tree_item.mimeData(index)
            if mime_data_item is None:
                continue
            data.append(mime_data_item)
        ret.setData(TAURUS_MODEL_LIST_MIME_TYPE, "\r\n".join(data))
        ret.setText(", ".join(data))
        if len(data) == 1:
            ret.setData(TAURUS_MODEL_MIME_TYPE, str(data[0]))
        return ret

    def accept(self, element):
        return True

    def setupModelData(self, data):
        dev = self.dataSource()
        if dev is None:
            return
        self.ColumnNames[0] = dev.getSimpleName()
        info = dev.getElementsInfo()
        elements = info.getElements()
        root = self._rootItem
        type_nodes = {}
        parent_elements = {}
        child_elements = set()
        parent_types = "ControllerLibrary", "MacroLibrary", "Controller"
        child_types = "ControllerClass", "MacroClass", "MacroFunction", \
            "Motor", "CounterTimer", "PseudoMotor", "PseudoCounter", \
            "ZeroDExpChannel", "OneDExpChannel", "TwoDExpChannel"

        for element in elements:
            if not self.accept(element):
                continue
            element_type = element.type
            type_item = type_nodes.get(element_type)
            if type_item is None:
                type_item = SardanaTypeTreeItem(self, element_type, root)
                type_nodes[element_type] = type_item
                root.appendChild(type_item)
            element_item = SardanaElementTreeItem(self, element, type_item)
            type_item.appendChild(element_item)
            if element_type in parent_types:
                parent_elements[element.name] = element_item
            elif element_type in child_types:
                child_elements.add(element)

        for element in child_elements:
            try:
                parent_item = parent_elements[element.parent]
            except KeyError:
                self.warning("Error adding %s to parent %s (parent unknown)",
                             element.name, element.parent)
            element_item = SardanaElementTreeItem(self, element, parent_item)
            parent_item.appendChild(element_item)


class SardanaElementTypeModel(SardanaBaseElementModel):
    pass


class SardanaElementPlainModel(SardanaBaseElementModel):

    ColumnNames = "Elements",
    ColumnRoles = ('Root', 'name',),

    def setupModelData(self, data):
        dev = self.dataSource()
        if dev is None:
            return
        info = dev.getElementsInfo()
        elements = info.getElements()
        root = self._rootItem
        skip_types = "ControllerLibrary", "MacroLibrary"

        for element in elements:
            element_type = element.type
            if element_type in skip_types:
                continue
            element_item = SardanaElementTreeItem(self, element, root)
            root.appendChild(element_item)


class SardanaBaseProxyModel(TaurusBaseProxyModel):

    def filterAcceptsRow(self, sourceRow, sourceParent):
        sourceModel = self.sourceModel()
        idx = sourceModel.index(sourceRow, 0, sourceParent)
        treeItem = idx.internalPointer()

        if isinstance(treeItem, SardanaElementTreeItem):
            expr = self.filterRegExp()
            element = treeItem.itemData()
            return self.elementMatches(element, expr)
        return True

    def elementMatches(self, element, expr):
        name = element.name
        if Qt.QString(name).contains(expr):
            return True
        name = element.full_name
        if name is None:
            return False
        return Qt.QString(name).contains(expr)


class SardanaTypeProxyModel(TaurusBaseProxyModel):
    """Sardana filter by element type"""

    def __init__(self, types=None, parent=None):
        TaurusBaseProxyModel.__init__(self, parent=parent)
        if types is None:
            types = ()
        self._types = types

    def filterAcceptsRow(self, sourceRow, sourceParent):
        sourceModel = self.sourceModel()
        idx = sourceModel.index(sourceRow, 0, sourceParent)
        treeItem = idx.internalPointer()

        if isinstance(treeItem, SardanaElementTreeItem):
            return treeItem.itemData().type in self._types
        return False


class EnvironmentTreeItem(TaurusBaseTreeItem):
    """An environment node"""

    def role(self):
        return self.itemData().type

    def data(self, index):
        column, model = index.column(), index.model()
        role = model.role(column, self.depth())
        obj = self.itemData()
        if role == "key":
            return obj[0]
        elif role == "value":
            return obj[1]
        elif role == "datatype":
            return type(obj[1]).__name__

    def toolTip(self, index):
        return "environment '%s'" % self.itemData()[0]

    def icon(self, index):
        if index.column() > 0:
            return None
        return ":/class.png"


class SardanaEnvironmentModel(TaurusBaseModel):

    ColumnNames = ["Environment", "Value", "Data Type"]
    ColumnRoles = ('Root', 'key'), 'value', 'datatype'

    def __init__(self, parent=None, data=None):
        TaurusBaseModel.__init__(self, parent=parent, data=data)
        self.setSelectables(self.ColumnRoles[0])

    def setDataSource(self, data_source):
        old_ds = self.dataSource()
        if old_ds is not None:
            Qt.QObject.disconnect(old_ds, Qt.SIGNAL('environmentChanged'),
                                  self.on_environment_changed)
        if data_source is not None:
            Qt.QObject.connect(data_source, Qt.SIGNAL('environmentChanged'),
                               self.on_environment_changed)
        TaurusBaseModel.setDataSource(self, data_source)

    def on_environment_changed(self):
        self.refresh()

    def createNewRootItem(self):
        return SardanaRootTreeItem(self, self.ColumnNames)

    def roleIcon(self, role):
        return ":/tango.png"
    #    return getElementTypeIcon(role)

    #def columnIcon(self, column):
    #    return self.roleIcon(self.role(column))

    def roleToolTip(self, role):
        cr = self.ColumnRoles
        if role == cr[0][1]:
            return "Environment name"
        elif role == cr[1]:
            return "Environment value"
        elif role == cr[2]:
            return "Environment value data type"

    #def columnToolTip(self, column):
    #    return self.roleToolTip(self.role(column))

    def roleSize(self, role):
        return Qt.QSize(200, 24)

    def columnSize(self, column):
        role = self.role(column)
        s = self.roleSize(role)
        return s

    def mimeTypes(self):
        return "text/plain", TAURUS_MODEL_LIST_MIME_TYPE, TAURUS_MODEL_MIME_TYPE

    def mimeData(self, indexes):
        ret = Qt.QMimeData()
        data = []
        for index in indexes:
            if not index.isValid(): continue
            tree_item = index.internalPointer()
            mime_data_item = tree_item.mimeData(index)
            if mime_data_item is None:
                continue
            data.append(mime_data_item)
        ret.setData(TAURUS_MODEL_LIST_MIME_TYPE, "\r\n".join(data))
        ret.setText(", ".join(data))
        if len(data) == 1:
            ret.setData(TAURUS_MODEL_MIME_TYPE, str(data[0]))
        return ret

    def accept(self, environment):
        return True

    def setupModelData(self, data):
        dev = self.dataSource()
        if dev is None:
            return

        env = dev.getEnvironment()
        root = self._rootItem

        for key, value in env.items():
            if not self.accept(key):
                continue
            env_item = EnvironmentTreeItem(self, (key, value), root)
            root.appendChild(env_item)
