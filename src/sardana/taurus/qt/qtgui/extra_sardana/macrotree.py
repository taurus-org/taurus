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

__all__ = ["MacroTreeWidget", "MacroSelectionDialog"]

__docformat__ = 'restructuredtext'

from taurus.core.taurusdevice import TaurusDevice
from taurus.core.util.enumeration import Enumeration
from taurus.external.qt import Qt
from taurus.qt.qtcore.mimetypes import TAURUS_MODEL_MIME_TYPE, \
    TAURUS_MODEL_LIST_MIME_TYPE
from taurus.qt.qtcore.model import TaurusBaseTreeItem, TaurusBaseModel, \
    TaurusBaseProxyModel
from taurus.qt.qtgui.tree import TaurusBaseTreeWidget
from taurus.qt.qtgui.resource import getIcon

from sardana.taurus.core.tango.sardana.macro import MacroInfo


MacroView = Enumeration("MacroView", ("MacroModule", "Macro", "Unknown"))

def getElementTypeIcon(t):
    if t == MacroView.MacroModule:
        return getIcon(":/python-file.png")
    elif t == MacroView.Macro:
        return getIcon(":/python.png")
    return getIcon(":/tango.png")

def getElementTypeSize(t):
    return Qt.QSize(200, 24)

def getElementTypeToolTip(t):
    """Wrapper to prevent loading qtgui when this module is imported"""
    if t == MacroView.MacroModule:
        return "Macro module"
    elif t == MacroView.Macro:
        return "Macro item"
    return "Unknown"


class MacroTreeBaseItem(TaurusBaseTreeItem):
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
        
        :return: (MacroView) the role in form of element type"""
        return MacroView.Unknown


class MacroModuleTreeItem(MacroTreeBaseItem):

    def role(self):
        return MacroView.MacroModule

    def toolTip(self, index):
        return "The macro module '%s'" % self.display()

    def icon(self, index):
        return getIcon(":/python-file.png")


class MacroTreeItem(MacroTreeBaseItem):

    def data(self, index):
        """Returns the data of this node for the given index
        
        :return: (object) the data for the given index
        """
        return self._itemData.name

    def role(self):
        return MacroView.Macro

    def toolTip(self, index):
        return self._itemData.doc

    def icon(self, index):
        return getIcon(":/python.png")


class MacroBaseModel(TaurusBaseModel):

    ColumnNames = "Macros",
    ColumnRoles = (MacroView.MacroModule, MacroView.MacroModule, MacroView.Macro),

    def setDataSource(self, ms):
        if self._data_src is not None:
            Qt.QObject.disconnect(self._data_src, Qt.SIGNAL('macrosUpdated'), self.macrosUpdated)
        if ms is not None:
            Qt.QObject.connect(ms, Qt.SIGNAL('macrosUpdated'), self.macrosUpdated)
        TaurusBaseModel.setDataSource(self, ms)

    def macrosUpdated(self):
        self.refresh()

    def createNewRootItem(self):
        return MacroTreeBaseItem(self, self.ColumnNames)

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



    def setupModelData(self, data):
        ms = self.dataSource()
        if ms is None:
            return
        root = self._rootItem
        macro_modules = {}
        macro_dict = ms.getMacros()
        for macro_name, macro in macro_dict.items():
            module_name = macro.module
            moduleNode = macro_modules.get(module_name)
            if moduleNode is None:
                moduleNode = MacroModuleTreeItem(self, module_name, root)
                root.appendChild(moduleNode)
                macro_modules[module_name] = moduleNode
            macroNode = MacroTreeItem(self, macro, moduleNode)
            moduleNode.appendChild(macroNode)


class MacroModuleModel(MacroBaseModel):
    pass


class MacroPlainMacroModel(MacroBaseModel):

    ColumnNames = "Macros",
    ColumnRoles = (MacroView.Macro, MacroView.Macro),

    def setupModelData(self, data):
        ms = self.dataSource()
        if ms is None:
            return
        root = self._rootItem
        macro_dict = ms.getMacros()
        macros = macro_dict.keys()
        macros.sort()
        self.debug("Found %d macros", len(macros))
        for macro_name in macros:
            macro = macro_dict[macro_name]
            macroNode = MacroTreeItem(self, macro, root)
            root.appendChild(macroNode)


class MacroBaseModelProxy(TaurusBaseProxyModel):
    pass


class MacroModuleModelProxy(MacroBaseModelProxy):
    pass


class MacroPlainMacroModelProxy(MacroBaseModelProxy):
    pass


class MacroTreeWidget(TaurusBaseTreeWidget):

    KnownPerspectives = { MacroView.MacroModule : {
                            "label" : "By module",
                            "icon" : ":/python-file.png",
                            "tooltip" : "View by macro module",
                            "model" : [MacroModuleModelProxy, MacroModuleModel],
                          },
                          MacroView.Macro : {
                            "label" : "By macro",
                            "icon" : ":/python.png",
                            "tooltip" : "View by macro",
                            "model" : [MacroPlainMacroModelProxy, MacroPlainMacroModel],
                          }
    }
    DftPerspective = MacroView.MacroModule

    def getModelClass(self):
        return TaurusDevice


class MacroSelectionDialog(Qt.QDialog):

    def __init__(self, parent=None, designMode=False, model_name=None, perspective=None):
        Qt.QDialog.__init__(self, parent)

        self.setWindowTitle("Macro Selection Dialog")

        layout = Qt.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        self._panel = MacroTreeWidget(parent=self, perspective=perspective,
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


def main_MacroSelecionDialog(ms, perspective=MacroView.MacroModule):
    w = MacroSelectionDialog(model_name=ms, perspective=perspective)

    if w.result() == Qt.QDialog.Accepted:
        print w.getSelectedMacros()
    return w

def main_MacroTreeWidget(ms, perspective=MacroView.MacroModule):
    w = MacroTreeWidget(perspective=perspective, with_navigation_bar=False)
    w.setModel(ms)
    w.show()
    return w

def demo():
    """MacroTreeWidget"""
    w = main_MacroSelecionDialog("MS_BL98", MacroView.Macro)
    return w

def main():
    import sys
    import taurus.qt.qtgui.application
    Application = taurus.qt.qtgui.application.TaurusApplication

    app = Application.instance()
    owns_app = app is None

    if owns_app:
        app = Application(app_name="MacroServer macro tree demo", app_version="1.0",
                          org_domain="Taurus", org_name="Tango community")
    w = demo()
    w.show()
    if owns_app:
        sys.exit(app.exec_())
    else:
        return w

if __name__ == "__main__":
    main()
