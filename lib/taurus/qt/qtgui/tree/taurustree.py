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

__all__ = ["QBaseTreeWidget", "TaurusBaseTreeWidget"]

__docformat__ = 'restructuredtext'

import PyQt4.Qt as Qt

from taurus.qt.qtcore.model import *
from taurus.qt.qtgui.base import TaurusBaseWidget, QBaseModelWidget, TaurusBaseModelWidget
from taurus.qt.qtgui.util import ActionFactory
import taurus.qt.qtgui.resource

getThemeIcon = taurus.qt.qtgui.resource.getThemeIcon
getIcon = taurus.qt.qtgui.resource.getIcon


class _NavigationLabel(Qt.QWidget):
    """Internal widget providing a navigation label & icon"""
    
    def __init__(self, pixmap, text, cont, index, parent=None):
        super(_NavigationLabel, self).__init__(parent)
        self._index = index
        
        l = Qt.QHBoxLayout()
        l.setContentsMargins(0,0,0,0)
        self.setLayout(l)
        if pixmap is not None:
            p = Qt.QLabel()
            p.setPixmap(pixmap)
            l.addWidget(p)
        self._label = Qt.QLabel(text)
        l.addWidget(self._label)
        if cont:
            l.addWidget(Qt.QLabel(u" \u00bb "))
    
    def label(self):
        return self._label
    
    def index(self):
        return self._index


class _NavigationWidget(Qt.QFrame):
    """Internal widget that provides a navigation path to be placed in a toolbar"""
     
    def __init__(self, treeWidget, toolBarWidget, parent=None):
        super(_NavigationWidget, self).__init__(parent)
        self._tree = treeWidget
        self._toolbar = toolBarWidget
        l = Qt.QHBoxLayout()
        l.setContentsMargins(4, 0, 4, 0)
        self.setLayout(l)
   
    def treeWidget(self):
        return self._tree

    def viewWidget(self):
        return self.treeWidget().viewWidget()

    def toolBarWidget(self):
        return self._toolbar
    
    def clean(self):
        l = self.layout()
        w = l.takeAt(0)
        while w is not None:
            w = w.widget()
            Qt.QObject.disconnect(w, Qt.SIGNAL("clicked()"), self.onGotoNode)
            w.setParent(None)
            w = l.takeAt(0)

    def updateSelection(self, index):
        self.clean()
        treeWidget = self.treeWidget()
        viewWidget = treeWidget.viewWidget()
        model = viewWidget.model()
        src_model = treeWidget.getBaseQModel()
        toolbar = self.toolBarWidget()
        size = None
        rootPixmap = getThemeIcon("go-home").pixmap(toolbar.iconSize())
        rootText = u"Top"
        
        l = self.layout()
        n = 0
        while index.isValid():
            src_index = treeWidget._mapToSource(index)
            name = src_model.pyData(src_index, Qt.Qt.DisplayRole)
            font = src_model.pyData(src_index, Qt.Qt.FontRole)
            tooltip = src_model.pyData(src_index, Qt.Qt.ToolTipRole)
            decoration = src_model.pyData(src_index, Qt.Qt.DecorationRole) 
            pixmap = None
            if isinstance(decoration, Qt.QIcon):
                pixmap = decoration.pixmap(toolbar.iconSize())
            elif isinstance(decoration, Qt.QPixmap):
                pixmap = decoration
            button = _NavigationLabel(pixmap, name, n>0, Qt.QPersistentModelIndex(index))
            font = font or model.DftFont
            button.setFont(font)
            button.setToolTip(tooltip)
            Qt.QObject.connect(button.label(), Qt.SIGNAL("linkActivated(const QString &)"), self.onGotoNode)
            l.insertWidget(0, button)
            index = index.parent()
            n += 1
        rootButton = _NavigationLabel(rootPixmap, rootText, n>0, Qt.QPersistentModelIndex(index))
        rootButton.setFont(model.DftFont)
        #Qt.QObject.connect(rootButton.label(), Qt.SIGNAL("linkActivated(const QString &)"), self.onGotoNode)
        l.insertWidget(0, rootButton)
        
        lastLabel = l.itemAt(l.count()-1).widget()
        
    def onGotoNode(self, *args):
        label = self.sender()
        persistent_index = label.parent().index()
        index = Qt.QModelIndex(persistent_index)
        tree = self.viewWidget()
        tree.setRootIndex(index)
        tree.setCurrentIndex(index.child(0, 0))


class QBaseTreeWidget(QBaseModelWidget):
    """A pure Qt tree widget implementing a tree with a navigation toolbar"""
    
    def __init__(self, parent=None, designMode=False, with_navigation_bar=True,
                 with_filter_widget=True):
        self._with_navigation_bar = with_navigation_bar
        QBaseModelWidget.__init__(self, parent, with_filter_widget=with_filter_widget)
    
    def createToolBar(self):
        tb = QBaseModelWidget.createToolBar(self)
        if self._with_navigation_bar:
            self._navigationBar = _NavigationWidget(self, tb)
            action = tb.addWidget(self._navigationBar )
        return tb
    
    def createViewWidget(self):
        tree = Qt.QTreeView()
        tree.setSortingEnabled(True)
        tree.setUniformRowHeights(True)
        tree.setAlternatingRowColors(True)
        tree.setSelectionBehavior(Qt.QTreeView.SelectRows)
        tree.setSelectionMode(Qt.QTreeView.ExtendedSelection)
        tree.setDragEnabled(True)
        tree.setDropIndicatorShown(True)

        self.connect(tree, Qt.SIGNAL("expanded(QModelIndex)"), self.onExpanded)
        self.connect(tree, Qt.SIGNAL("clicked(QModelIndex)"), self._onClicked)
        self.connect(tree, Qt.SIGNAL("doubleClicked(QModelIndex)"), self._onDoubleClicked)
        h = tree.header()
        h.setResizeMode(0, Qt.QHeaderView.Stretch)
        return tree
    
    def createToolBarActions(self):
        tb_actions = QBaseModelWidget.createToolBarActions(self)
        af = ActionFactory()
        self._expandAllAction = af.createAction(self, "Expand All",
                                                icon=getIcon(":/actions/expand-all.svg"),
                                                tip="Expand all items",
                                                triggered=self.expandAllTree)
        self._collapseAllAction = af.createAction(self, "Collapse All",
                                                  icon=getIcon(":/actions/collapse-all.svg"),
                                                  tip="Collapse all items",
                                                  triggered=self.collapseAllTree)
        tb_actions.append([ self._expandAllAction, self._collapseAllAction ])
    
        if self._with_navigation_bar:
            self._goIntoAction = af.createAction(self, "Go Into",
                                                icon=getThemeIcon("go-down"),
                                                tip="Go into the selected item",
                                                triggered=self.goIntoTree)
            self._goUpAction = af.createAction(self, "Go Up",
                                                icon=getThemeIcon("go-up"),
                                                tip="Go up one level",
                                                triggered=self.goUpTree)
            self._goTopAction = af.createAction(self, "Go Top",
                                                icon=getThemeIcon("go-top"),
                                                tip="Go to top level",
                                                triggered=self.goTopTree)
            tb_actions.append([self._goIntoAction, self._goUpAction, self._goTopAction])
            
            tb = self.toolBar()
            self._navigationBar = _NavigationWidget(self, tb)
            action = tb.addWidget(self._navigationBar )
            #tb_actions.append([action])
        else:
            self._goIntoAction = None
            self._goUpAction = None
            self._goTopAction = None
            self._navigationBar = None
            
        return tb_actions

    def treeView(self):
        return self.viewWidget()

    def goIntoAction(self):
        return self._goIntoAction
    
    def goTopAction(self):
        return self._goTopAction
    
    def goUpAction(self):
        return self._goUpAction
    
    def expandAllTree(self):
        self._statusbar.showMessage("Expanding all items... (it may take a few seconds)")
        tree = self.viewWidget()
        Qt.QTimer.singleShot(0, self._expandTree)
    
    def _expandTree(self):
        tree = self.viewWidget()
        tree.expandAll()
        self._statusbar.showMessage("All nodes expanded!", 3000)
    
    def onExpanded(self):
        self.resizeColumns()
    
    def collapseAllTree(self):
        self.viewWidget().collapseAll()
    
    def resizeColumns(self):
        tree = self.viewWidget()
        model = tree.model()
        if model is None:
            return
        for c in range(model.columnCount()):
            tree.resizeColumnToContents(c)
    
    def goIntoTree(self):
        index = self._tree.currentIndex()
        base_index = self._mapToSource(index)
        
        if not index.isValid():
            return
        
        # do not enter if the item doesn't have any children
        if base_index.internalPointer().childCount() == 0:
            return
    
        self._tree.setRootIndex(index)
        self._tree.setCurrentIndex(index.child(0, 0))
        self._updateToolBar()
    
    def goUpTree(self):
        tree = self.viewWidget()
        index = tree.rootIndex()
        if not index.isValid():
            return
        index_parent = index.parent()
        
        tree.setRootIndex(index_parent)
        tree.setCurrentIndex(index)
        self._updateToolBar()
    
    def goTopTree(self):
        tree = self.viewWidget()
        current_root = tree.rootIndex()
        p = current_root.parent()
        while p.isValid():
            p = p.parent()
        tree.setRootIndex(p)
        tree.setCurrentIndex(p)
        self._updateToolBar()
    
    def _updateToolBar(self, current=None, previous=None):
        if not self._with_navigation_bar:
            return
        tree = self.viewWidget()
        if current is None:
            current = tree.currentIndex()
        goInto = False
        
        base_current = self._mapToSource(current)
        if current.isValid():
            ip = base_current.internalPointer()
            if ip is not None:
                goInto = ip.childCount() > 0
        self._goIntoAction.setEnabled(goInto)
        
        goUp = tree.rootIndex().isValid()
        self._goUpAction.setEnabled(goUp)
        self._goTopAction.setEnabled(goUp)
        
        index = tree.rootIndex()
        self._navigationBar.updateSelection(index)
        

class TaurusBaseTreeWidget(QBaseTreeWidget, TaurusBaseWidget):
    """A class:`taurus.qt.qtgui.tree.QBaseTreeWidget` that connects to a
    taurus model.
    
    Filters can be inserted into this widget to restrict the tree nodes that are
    seen."""
    
    KnownPerspectives = { }
    DftPerspective = None

    def __init__(self, parent=None, designMode=False, with_navigation_bar=True,
                 with_filter_widget=True, perspective=None, proxy=None):
        name = self.__class__.__name__
        self._perspective = perspective
        self._proxyModel = proxy
        self.call__init__(QBaseTreeWidget, parent, designMode=designMode,
                          with_navigation_bar=with_navigation_bar,
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
        """overwritten from class:`taurus.qt.qtgui.base.TaurusBaseWidget`. It is called when
        the taurus model changes."""
        self.resizeColumns()
    
    def setModel(self, m):
        TaurusBaseWidget.setModel(self, m)

        tree, modelObj = self.viewWidget(), self.getModelObj()
        model = tree.model()
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
    
class TaurusBaseTreeWidget(QBaseTreeWidget, TaurusBaseModelWidget):
    
    def __init__(self, parent=None, designMode=False, with_navigation_bar=True,
                 with_filter_widget=True, perspective=None, proxy=None):
        self.call__init__(QBaseTreeWidget, parent, designMode=designMode,
                          with_navigation_bar=with_navigation_bar,
                          with_filter_widget=with_filter_widget)
        self.call__init__(TaurusBaseModelWidget, designMode=designMode,
                          perspective=perspective, proxy=proxy)
