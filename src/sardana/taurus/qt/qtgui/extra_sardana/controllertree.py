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

__all__ = ["ControllerClassTreeWidget", "ControllerClassSelectionDialog"]

__docformat__ = 'restructuredtext'

import sys
import os

import taurus.core
from taurus.core.util.enumeration import Enumeration
from taurus.external.qt import Qt
from taurus.qt.qtcore.mimetypes import TAURUS_MODEL_MIME_TYPE, TAURUS_MODEL_LIST_MIME_TYPE
from taurus.qt.qtcore.model import TaurusBaseTreeItem, TaurusBaseModel, TaurusBaseProxyModel
from taurus.qt.qtgui.tree import TaurusBaseTreeWidget
from taurus.qt.qtgui.resource import getThemeIcon, getIcon

PoolControllerView = Enumeration("PoolControllerView", ("ControllerModule", "ControllerClass", "Unknown"))

def getElementTypeIcon(t):
    if t == PoolControllerView.ControllerModule:
        return getIcon(":/python-file.png")
    elif t == PoolControllerView.ControllerClass:
        return getIcon(":/python.png")
    return getIcon(":/tango.png")

def getElementTypeSize(t):
    return Qt.QSize(200, 24)

def getElementTypeToolTip(t):
    """Wrapper to prevent loading qtgui when this module is imported"""
    if t == PoolControllerView.ControllerModule:
        return "Controller module"
    elif t == PoolControllerView.ControllerClass:
        return "Controller class"


class ControllerBaseTreeItem(TaurusBaseTreeItem):
    """A generic node"""

    def data(self, index):
        """Returns the data of this node for the given index
        
        :return: (object) the data for the given index
        """
        return self._itemData

    def role(self):
        """Returns the prefered role for the item.
        This implementation returns taurus.core.taurusbasetypes.TaurusElementType.Unknown
        
        This method should be able to return any kind of python object as long
        as the model that is used is compatible.
        
        :return: (PoolControllerView) the role in form of element type"""
        return PoolControllerView.Unknown


class ControllerModuleTreeItem(ControllerBaseTreeItem):

    def role(self):
        return PoolControllerView.ControllerModule

    def toolTip(self):
        return "The controller module '%s'" % self.display()

    def icon(self):
        return getIcon(":/python-file.png")


class ControllerTreeItem(ControllerBaseTreeItem):

    def data(self, index):
        """Returns the data of this node for the given index
        
        :return: (object) the data for the given index
        """
        return self._itemData.name

    def role(self):
        return PoolControllerView.ControllerClass

    def toolTip(self):
        return self._itemData.doc

    def icon(self):
        return getIcon(":/python.png")


class ControllerBaseModel(TaurusBaseModel):

    ColumnNames = "Controllers",
    ColumnRoles = (PoolControllerView.ControllerModule, PoolControllerView.ControllerModule, PoolControllerView.ControllerClass),

    def setDataSource(self, pool):
        if self._data_src is not None:
            Qt.QObject.disconnect(self._data_src, Qt.SIGNAL('controllerClassesUpdated'), self.controllerClassesUpdated)
        if pool is not None:
            Qt.QObject.connect(pool, Qt.SIGNAL('controllerClassesUpdated'), self.controllerClassesUpdated)
        TaurusBaseModel.setDataSource(self, pool)

    def controllerClassesUpdated(self):
        self.refresh()

    def createNewRootItem(self):
        return ControllerBaseTreeItem(self, self.ColumnNames)

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
        return ["text/plain", TAURUS_MODEL_LIST_MIME_TYPE, TAURUS_MODEL_MIME_TYPE]

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

    def pyData(self, index, role):
        if not index.isValid():
            return None

        item = index.internalPointer()
        row, column, depth = index.row(), index.column(), item.depth()
        item_role = self.role(column, depth)

        ret = None
        if role == Qt.Qt.DisplayRole:
            ret = Qt.QString(item.data(index))
        elif role == Qt.Qt.DecorationRole:
            ret = item.icon()
        elif role == Qt.Qt.ToolTipRole:
            ret = item.toolTip()
        #elif role == Qt.Qt.SizeHintRole:
        #    ret = self.columnSize(column)
        elif role == Qt.Qt.FontRole:
            ret = self.DftFont
        return ret

    def setupModelData(self, data):
        pool = self.dataSource()
        if pool is None:
            return
        root = self._rootItem
        ctrl_modules = {}
        # TODO
        #ctrl_class_dict = pool.getControllerClasses()
        #for ctrl_class_name, ctrl_class in ctrl_class_dict.items():
        #    module_name = ctrl_class.module_name
        #    moduleNode = ctrl_modules.get(module_name)
        #    if moduleNode is None:
        #        moduleNode = ControllerModuleTreeItem(self, module_name, root)
        #        root.appendChild(moduleNode)
        #        ctrl_modules[module_name] = moduleNode
        #    ctrlNode = ControllerTreeItem(self, ctrl_class, moduleNode)
        #    moduleNode.appendChild(ctrlNode)


class ControllerModuleModel(ControllerBaseModel):
    pass


class PlainControllerModel(ControllerBaseModel):

    ColumnNames = "Controller classes",
    ColumnRoles = (PoolControllerView.ControllerClass, PoolControllerView.ControllerClass),

    def setupModelData(self, data):
        pool = self.dataSource()
        if pool is None:
            return
        root = self._rootItem
        # TODO
        #ctrl_class_dict = pool.getControllerClasses()
        #ctrl_classes = ctrl_class_dict.keys()
        #ctrl_classes.sort()
        #self.debug("Found %d controller classes", len(ctrl_classes))
        #for ctrl_class_name in ctrl_classes:
        #    ctrl_class = ctrl_class_dict[ctrl_class_name]
        #    ctrlNode = ControllerTreeItem(self, ctrl_class, root)
        #    root.appendChild(ctrlNode)


class ControllerBaseModelProxy(TaurusBaseProxyModel):
    pass


class ControllerModuleModelProxy(ControllerBaseModelProxy):
    pass


class PlainControllerModelProxy(ControllerBaseModelProxy):
    pass


class ControllerClassTreeWidget(TaurusBaseTreeWidget):

    KnownPerspectives = { PoolControllerView.ControllerModule : {
                            "label" : "By module",
                            "icon" : ":/python-file.png",
                            "tooltip" : "View by controller module",
                            "model" : [ControllerModuleModelProxy, ControllerModuleModel],
                          },
                          PoolControllerView.ControllerClass : {
                            "label" : "By controller",
                            "icon" : ":/python.png",
                            "tooltip" : "View by controller class",
                            "model" : [PlainControllerModelProxy, PlainControllerModel],
                          }
    }
    DftPerspective = PoolControllerView.ControllerModule

    def getModelClass(self):
        return taurus.core.taurusdevice.TaurusDevice


class ControllerClassSelectionDialog(Qt.QDialog):

    def __init__(self, parent=None, designMode=False, model_name=None, perspective=None):
        Qt.QDialog.__init__(self, parent)

        self.setWindowTitle("Controller Class Selection Dialog")

        layout = Qt.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        self._panel = ControllerClassTreeWidget(parent=self,
                                                perspective=perspective,
                                                designMode=designMode,
                                                with_navigation_bar=False)
        self._panel.setModel(model_name)
        self.setWindowIcon(getElementTypeIcon(self._panel.perspective()))
        self._buttonBox = Qt.QDialogButtonBox(self)
        bts = Qt.QDialogButtonBox.Ok | Qt.QDialogButtonBox.Cancel
        self._buttonBox.setStandardButtons(bts)
        layout.addWidget(self._panel)
        layout.addWidget(self._buttonBox)
        self.connect(self._buttonBox, Qt.SIGNAL("accepted()"), self.accept)
        self.connect(self._buttonBox, Qt.SIGNAL("rejected()"), self.reject)

    def selectedItems(self):
        return self._panel.selectedItems()

    def getSelectedMacros(self):
        return [ i.itemData() for i in self.selectedItems() ]


def main_ControllerClassSelecionDialog(pool, perspective=PoolControllerView.ControllerClass):
    w = ControllerClassSelectionDialog(model_name=pool, perspective=perspective)

    if w.result() == Qt.QDialog.Accepted:
        print w.getSelectedMacros()
    return w

def main_ControllerClassTreeWidget(pool, perspective=PoolControllerView.ControllerClass):
    w = ControllerClassTreeWidget(perspective=perspective, with_navigation_bar=False)
    w.setModel(pool)
    w.show()
    return w

def demo(poolname="Pool_BL98"):
    """ControllerClassTreeWidget"""
    w = main_ControllerClassSelecionDialog(poolname, PoolControllerView.ControllerClass)
    return w

def main():
    import sys
    import taurus.qt.qtgui.application
    Application = taurus.qt.qtgui.application.TaurusApplication

    app = Application.instance()
    owns_app = app is None

    if owns_app:
        app = Application(app_name="Pool controller class tree demo", app_version="1.0",
                          org_domain="Taurus", org_name="Tango community")

    args = app.get_command_line_args()
    if len(args) == 1:
        w = demo(poolname=args[0])
    else:
        w = demo()

    w.show()
    if owns_app:
        sys.exit(app.exec_())
    else:
        return w

if __name__ == "__main__":
    main()
