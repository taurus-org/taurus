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

"""This module provides base tree widget"""

__all__ = ["QBaseTreeWidget"]

__docformat__ = 'restructuredtext'

from taurus.external.qt import Qt
from taurus.qt.qtgui.model import QBaseModelWidget, BaseToolBar
from taurus.qt.qtgui.util import ActionFactory


class _NavigationWidget(Qt.QFrame):
    """Internal widget that provides a navigation path to be placed in a toolbar"""

    def __init__(self, treeWidget, toolBarWidget, parent=None):
        super(_NavigationWidget, self).__init__(parent)
        self._tree = treeWidget
        self._toolbar = toolBarWidget
        self._label = Qt.QLabel()
        l = Qt.QHBoxLayout()
        l.setContentsMargins(4, 0, 4, 0)
        self.setLayout(l)
        l.addWidget(self._label)

    def treeWidget(self):
        return self._tree

    def viewWidget(self):
        return self.treeWidget().viewWidget()

    def toolBarWidget(self):
        return self._toolbar

    def updateSelection(self, index):
        treeWidget = self.treeWidget()
        src_model = treeWidget.getBaseQModel()
        toolbar = self.toolBarWidget()
        txt = u""

        while index.isValid():
            src_index = treeWidget._mapToSource(index)
            name = src_model.pyData(src_index, Qt.Qt.DisplayRole)
            txt = u" \u00bb " + name + txt
            index = index.parent()
        txt = u"Root" + txt
        self._label.setText(txt)

    def onGotoNode(self, *args):
        label = self.sender()
        persistent_index = label.parent().index()
        index = Qt.QModelIndex(persistent_index)
        tree = self.viewWidget()
        tree.setRootIndex(index)
        tree.setCurrentIndex(index.child(0, 0))


class NavigationToolBar(BaseToolBar):

    goIntoTriggered = Qt.pyqtSignal()
    goUpTriggered = Qt.pyqtSignal()
    goTopTriggered = Qt.pyqtSignal()

    def __init__(self, view=None, parent=None, designMode=False):
        BaseToolBar.__init__(self, name="Taurus selection toolbar", view=view,
                             parent=parent, designMode=designMode)

        af = ActionFactory()
        self._goIntoAction = af.createAction(self, "Go Into",
                                             icon=Qt.QIcon.fromTheme("go-down"),
                                             tip="Go into the selected item",
                                             triggered=self.goInto)
        self._goUpAction = af.createAction(self, "Go Up",
                                           icon=Qt.QIcon.fromTheme("go-up"),
                                           tip="Go up one level",
                                           triggered=self.goUp)
        self._goTopAction = af.createAction(self, "Go Top",
                                            icon=Qt.QIcon.fromTheme("go-top"),
                                            tip="Go to top level",
                                            triggered=self.goTop)
        self.addAction(self._goIntoAction)
        self.addAction(self._goUpAction)
        self.addAction(self._goTopAction)
        self._navigationWidget = _NavigationWidget(view, self, parent=self)
        self._navigationAction = self.addWidget(self._navigationWidget)

    def goIntoAction(self):
        return self._goIntoAction

    def goTopAction(self):
        return self._goTopAction

    def goUpAction(self):
        return self._goUpAction

    def goInto(self):
        self.goIntoTriggered.emit()

    def goUp(self):
        self.goUpTriggered.emit()

    def goTop(self):
        self.goTopTriggered.emit()


class ExpansionBar(BaseToolBar):

    expandTriggered = Qt.pyqtSignal()
    collapseTriggered = Qt.pyqtSignal()
    expandSelectionTriggered = Qt.pyqtSignal()
    collapseSelectionTriggered = Qt.pyqtSignal()

    def __init__(self, view=None, parent=None, designMode=False):
        BaseToolBar.__init__(self, name="Taurus selection toolbar", view=view,
                             parent=parent, designMode=designMode)

        af = ActionFactory()
        self._expandAllAction = af.createAction(self, "Expand All",
                                                icon=Qt.QIcon(
                                                    "actions:expand.png"),
                                                tip="Expand all items",
                                                triggered=self.onExpandAll)
        self._collapseAllAction = af.createAction(self, "Collapse All",
                                                  icon=Qt.QIcon(
                                                      "actions:collapse.png"),
                                                  tip="Collapse all items",
                                                  triggered=self.onCollapseAll)
        self._expandSelectionAction = af.createAction(self, "Expand selection",
                                                      icon=Qt.QIcon(
                                                          "actions:expand-selection.png"),
                                                      tip="Expand selection",
                                                      triggered=self.onExpandSelection)
        self._collapseSelectionAction = af.createAction(self, "Collapse All",
                                                        icon=Qt.QIcon(
                                                            "actions:collapse-selection.png"),
                                                        tip="Collapse selection",
                                                        triggered=self.onCollapseSelection)
        self.addAction(self._expandAllAction)
        self.addAction(self._collapseAllAction)
        self.addAction(self._expandSelectionAction)
        self.addAction(self._collapseSelectionAction)

    def onExpandAll(self):
        self.expandTriggered.emit()

    def onCollapseAll(self):
        self.collapseTriggered.emit()

    def onExpandSelection(self):
        self.expandSelectionTriggered.emit()

    def onCollapseSelection(self):
        self.collapseSelectionTriggered.emit()


class QBaseTreeWidget(QBaseModelWidget):
    """A pure Qt tree widget implementing a tree with a navigation toolbar"""

    def __init__(self, parent=None, designMode=False, with_navigation_bar=True,
                 with_filter_widget=True, with_selection_widget=True,
                 with_refresh_widget=True, perspective=None, proxy=None):

        if with_navigation_bar:
            if isinstance(with_navigation_bar, (bool, int)):
                self._with_navigation_bar = NavigationToolBar
            else:
                self._with_navigation_bar = with_navigation_bar
        else:
            self._with_navigation_bar = None

        QBaseModelWidget.__init__(self, parent,
                                  with_filter_widget=with_filter_widget,
                                  with_selection_widget=with_selection_widget,
                                  with_refresh_widget=with_refresh_widget,
                                  perspective=perspective, proxy=proxy)

    def createToolArea(self):
        ta = QBaseModelWidget.createToolArea(self)

        e_bar = self._expandBar = ExpansionBar(view=self, parent=self)
        e_bar.expandTriggered.connect(self.expandAllTree)
        e_bar.collapseTriggered.connect(self.collapseAllTree)
        e_bar.expandSelectionTriggered.connect(self.expandSelectionTree)
        e_bar.collapseSelectionTriggered.connect(self.collapseSelectionTree)
        ta.append(e_bar)

        if self._with_navigation_bar:
            n_bar = self._navigationToolBar = self._with_navigation_bar(
                view=self, parent=self)
            n_bar.goIntoTriggered.connect(self.goIntoTree)
            n_bar.goTopTriggered.connect(self.goTopTree)
            n_bar.goUpTriggered.connect(self.goUpTree)
            ta.append(n_bar)
        else:
            self._navigationToolBar = None
        return ta

    def createViewWidget(self, klass=None):
        if klass is None:
            klass = Qt.QTreeView
        tree = klass()
        tree.setSortingEnabled(True)
        tree.sortByColumn(0, Qt.Qt.AscendingOrder)
        tree.setUniformRowHeights(True)
        tree.setAlternatingRowColors(True)
        tree.setSelectionBehavior(Qt.QAbstractItemView.SelectRows)
        tree.setSelectionMode(Qt.QAbstractItemView.ExtendedSelection)
        tree.setDragEnabled(True)
        tree.setDropIndicatorShown(True)

        tree.expanded.connect(self.onExpanded)
        tree.clicked.connect(self._onClicked)
        tree.doubleClicked.connect(self._onDoubleClicked)
        h = tree.header()
        if h.length() > 0:
            try:
                h.setSectionResizeMode(0, h.Stretch)
            except AttributeError:
                h.setResizeMode(0, h.Stretch)
        return tree

    def treeView(self):
        return self.viewWidget()

    def goIntoAction(self):
        return self._navigationToolBar.goIntoAction()

    def goTopAction(self):
        return self._navigationToolBar.goTopAction()

    def goUpAction(self):
        return self._navigationToolBar.goUpAction()

    def expandAllTree(self):
        self.statusBar().showMessage("Expanding all items... (it may take a few seconds)")
        Qt.QTimer.singleShot(0, self._expandTree)

    def _expandTree(self):
        tree = self.viewWidget()
        tree.expandAll()
        self.statusBar().showMessage("All items expanded!", 3000)

    def onExpanded(self):
        self.resizeColumns()

    def collapseAllTree(self):
        self.viewWidget().collapseAll()

    def expandSelectionTree(self):
        tree = self.viewWidget()
        index = tree.currentIndex()
        if index.isValid():
            tree.expand(index)

    def collapseSelectionTree(self):
        tree = self.viewWidget()
        index = tree.currentIndex()
        if index.isValid():
            tree.collapse(index)

    def resizeColumns(self):
        tree = self.viewWidget()
        model = tree.model()
        if model is None:
            return
        for c in range(model.columnCount()):
            tree.resizeColumnToContents(c)

    def goIntoTree(self):
        tree = self.viewWidget()
        index = tree.currentIndex()
        base_index = self._mapToSource(index)

        if not index.isValid():
            return

        # do not enter if the item doesn't have any children
        if base_index.internalPointer().childCount() == 0:
            return

        tree.setRootIndex(index)
        tree.setCurrentIndex(index.child(0, 0))
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
        self._navigationToolBar._goIntoAction.setEnabled(goInto)
        self._expandBar._expandSelectionAction.setEnabled(goInto)
        self._expandBar._collapseSelectionAction.setEnabled(goInto)

        goUp = tree.rootIndex().isValid()
        self._navigationToolBar._goUpAction.setEnabled(goUp)
        self._navigationToolBar._goTopAction.setEnabled(goUp)

        index = tree.rootIndex()
        self._navigationToolBar._navigationWidget.updateSelection(index)
