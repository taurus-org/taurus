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

"""This module provides widgets that display the database in a table format"""

__all__ = ["TaurusBaseTableWidget"]

__docformat__ = 'restructuredtext'

import PyQt4.Qt as Qt

import taurus
from taurus.core import TaurusElementType
from taurus.qt.qtcore.model import *
from taurus.qt.qtgui.base import TaurusBaseWidget, QBaseModelWidget
from taurus.qt.qtgui.resource import getIcon, getThemeIcon, \
    getElementTypeIcon, getElementTypeIconName
from taurus.qt.qtgui.util import ActionFactory


class QBaseTableWidget(QBaseModelWidget):

    def createViewWidget(self):
        table = Qt.QTableView(self)
        return table


class TaurusBaseTableWidget(QBaseTableWidget, TaurusBaseWidget):
    """A class:`taurus.qt.qtgui.tree.QBaseTableWidget` that connects to a
    taurus model.
    
    Filters can be inserted into this widget to restrict the tree nodes that are
    seen."""
    
    KnownPerspectives = { }
    DftPerspective = None
    
    def __init__(self, parent=None, designMode=False, with_filter_widget=True,
                 perspective=None, proxy=None):
        name = self.__class__.__name__
        self._perspective = None
        self._proxyModel = proxy
        self.call__init__(QBaseTableWidget, parent, designMode=designMode,
                          with_filter_widget=with_filter_widget)
        self.call__init__(TaurusBaseWidget, name, designMode=designMode)
        if perspective is None: 
            perspective = self.DftPerspective
        self.__init(perspective)

    def __init(self, perspective):
        toolBar = self.toolBar()
        
        b = self._perspective_button = Qt.QToolButton(toolBar)
        b.setToolTip("Perspective selection")
        b.setPopupMode(Qt.QToolButton.InstantPopup)
        b.setToolButtonStyle(Qt.Qt.ToolButtonTextBesideIcon)
        
        menu = Qt.QMenu("Perspective", b)
        b.setMenu(menu)
        af = ActionFactory()
        for persp, persp_data in self.KnownPerspectives.items():
            label = persp_data["label"]
            icon = getIcon(persp_data["icon"])
            tip = persp_data["tooltip"]
            action = af.createAction(self, label, icon=icon, tip=tip,
                                     triggered=self._onSwitchPerspective)
            action.perspective = persp
            menu.addAction(action)
            if persp == perspective:
                b.setDefaultAction(action)
        
        toolBar.insertWidget(self._toolbar_actions[0][0], b)
        self.setPerspective(perspective)
    
    def switchPerspectiveButton(self):
        """Returns the QToolButton that handles the switch perspective.
        
        :return: (PyQt4.QtGui.QToolButton) the switch perspective tool button
        """
        return self._perspective_button
    
    def _onSwitchPerspective(self):
        action = self.sender()
        self.switchPerspectiveButton().setDefaultAction(action)
        self.setPerspective(action.perspective)

    def perspective(self):
        return self._perspective
    
    def setPerspective(self, perspective):
        if self._perspective == perspective:
            return
        
        qmodel_classes = self.KnownPerspectives[perspective]["model"]
        qmodel_class, qmodel_proxy_classes = qmodel_classes[-1], qmodel_classes[:-1]
        qmodel_proxy_classes.reverse()
        qmodel = qmodel_class(self, self.getModelObj())
        qmodel_source = qmodel
        if self._proxyModel is None:
            for qmodel_proxy_class in qmodel_proxy_classes:
                qproxy = qmodel_proxy_class(self)
                qproxy.setSourceModel(qmodel_source)
                qmodel_source = qproxy
        else:
            self._proxyModel.setSourceModel(qmodel_source)
            qmodel_source = self._proxyModel
        self.setQModel(qmodel_source)
        self._perspective = perspective
    
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # TaurusBaseWidget overwriting
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    def updateStyle(self):
        """overwritten from class:`taurus.qt.qtgui.base.TaurusBaseWidget`.
        It is called when the taurus model changes."""
        TaurusBaseWidget.updateStyle(self)
    
    def setModel(self, m):
        TaurusBaseWidget.setModel(self, m)

        table, modelObj = self.viewWidget(), self.getModelObj()
        model = table.model()
        if model is None: return
        model.setDataSource(modelObj)
    
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # QT property definition
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    
    #: This property holds the unique URI string representing the model name 
    #: with which this widget will get its data from. The convention used for 
    #: the string can be found :ref:`here <model-concept>`.
    #: 
    #: In case the property :attr:`useParentModel` is set to True, the model 
    #: text must start with a '/' followed by the attribute name.
    #:
    #: **Access functions:**
    #:
    #:     * :meth:`TaurusBaseWidget.getModel`
    #:     * :meth:`TaurusBaseWidget.setModel`
    #:     * :meth:`TaurusBaseWidget.resetModel`
    #:
    #: .. seealso:: :ref:`model-concept`
    model = Qt.pyqtProperty("QString", TaurusBaseWidget.getModel, setModel,
                            TaurusBaseWidget.resetModel)
    

class TaurusDbTableWidget(TaurusBaseTableWidget):
    """A class:`taurus.qt.qtgui.tree.TaurusBaseTableWidget` that connects to a
    :class:`taurus.core.TaurusDatabase` model. It can show the list of database
    elements in four different perspectives:
    
    - device : a three level hierarchy of devices (domain/family/name)
    - server : a server based perspective
    - class : a class based perspective
    
    Filters can be inserted into this widget to restrict the tree nodes that are
    seen.
    """
    
    KnownPerspectives = {
        TaurusElementType.Device : {
            "label"   : "By device",
            "icon"    : getElementTypeIconName(TaurusElementType.Device),
            "tooltip" : "View by device",
            "model"   : [TaurusDbDeviceProxyModel, TaurusDbBaseModel,],
        },
        TaurusElementType.Server : {
            "label" : "By server",
            "icon" : getElementTypeIconName(TaurusElementType.Server),
            "tooltip" : "View by server",
            "model" : [TaurusDbServerProxyModel, TaurusDbServerModel,],
        },
        TaurusElementType.DeviceClass : {
            "label" : "By class",
            "icon" : getElementTypeIconName(TaurusElementType.DeviceClass),
            "tooltip" : "View by class",
            "model" : [TaurusDbDeviceClassProxyModel, TaurusDbDeviceClassModel,], 
        },
    }

    DftPerspective = TaurusElementType.Device

    def getModelClass(self):
        return taurus.core.TaurusDatabase
    
    def sizeHint(self):
        return Qt.QSize(1024, 512)

    @classmethod
    def getQtDesignerPluginInfo(cls):
        ret = TaurusBaseWidget.getQtDesignerPluginInfo()
        ret['module'] = 'taurus.qt.qtgui.table'
        ret['group'] = 'Taurus Item Widgets'
        ret['icon'] = ":/designer/table.png"
        return ret


def main_TaurusDbTableWidget(host, perspective=TaurusElementType.Device):
    w = TaurusDbTableWidget(perspective=perspective)
    w.setWindowIcon(getElementTypeIcon(perspective))
    w.setWindowTitle("A Taurus Table Example")
    w.setModel(host)
    w.show()
    return w

def demo():
    """DB panels"""

    db = taurus.Database()
    host = db.getNormalName()
    w = main_TaurusDbTableWidget(host, TaurusElementType.Device)
    
    return w

def main():
    import sys
    import taurus.qt.qtgui.application
    Application = taurus.qt.qtgui.application.TaurusApplication
    
    app = Application.instance()
    owns_app = app is None
    
    if owns_app:
        app = Application(app_name="DB model demo", app_version="1.0",
                          org_domain="Taurus", org_name="Tango community")
    w = demo()
    w.show()
    
    if owns_app:
        sys.exit(app.exec_())
    else:
        return w
    
if __name__ == "__main__":
    main()

