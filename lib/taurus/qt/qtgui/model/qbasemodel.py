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

"""This module provides base widget that displays a Qt view widget envolved
by a toolbar and a status bar (optional)"""

__all__ = ["QBaseModelWidget", "TaurusBaseModelWidget",
           "BaseToolBar", "FilterToolBar", "EditorToolBar", "SelectionToolBar",
           "RefreshToolBar", "PerspectiveToolBar"]

__docformat__ = 'restructuredtext'

from taurus.external.qt import Qt, compat

from taurus.qt.qtgui.util import ActionFactory
from taurus.qt.qtgui.base import TaurusBaseWidget


class BaseToolBar(Qt.QToolBar):

    def __init__(self, name=None, view=None, parent=None, designMode=False):
        if name is None:
            name = "Base toolbar"
        self._viewWidget = view or parent
        Qt.QToolBar.__init__(self, name, parent)
        self.setIconSize(Qt.QSize(16, 16))
        self.setFloatable(False)
        self.setMovable(False)

    def viewWidget(self):
        return self._viewWidget


class FilterToolBar(BaseToolBar):
    """Internal widget providing quick filter to be placed in a _QToolArea"""

    filterEdited = Qt.pyqtSignal('const QString &')
    filterChanged = Qt.pyqtSignal('const QString &')
    clearFilterTriggered = Qt.pyqtSignal()

    def __init__(self, view=None, parent=None, designMode=False):
        BaseToolBar.__init__(self, name="Taurus filter toolbar", view=view,
                             parent=parent, designMode=designMode)
        filterLineEdit = self._filterLineEdit = Qt.QLineEdit(self)
        filterLineEdit.setSizePolicy(Qt.QSizePolicy(Qt.QSizePolicy.Preferred,
                                                    Qt.QSizePolicy.Preferred))
        filterLineEdit.setToolTip("Quick filter")
        filterLineEdit.textChanged.connect(self.onFilterChanged)
        filterLineEdit.textEdited.connect(self.onFilterEdited)
        self.addWidget(filterLineEdit)

        af = ActionFactory()
        self._clearFilterAction = af.createAction(self, "Clear",
                                                  icon=Qt.QIcon.fromTheme(
                                                      "edit-clear"),
                                                  tip="Clears the filter",
                                                  triggered=self.onClearFilter)
        self.addAction(self._clearFilterAction)

    def getFilterLineEdit(self):
        return self._filterLineEdit

    def onClearFilter(self):
        self.getFilterLineEdit().setText("")
        self.clearFilterTriggered.emit()

    def onFilterChanged(self, text=None):
        text = text or self.getFilterLineEdit().text()
        self.filterChanged.emit(text)

    def onFilterEdited(self, text=None):
        text = text or self.getFilterLineEdit().text()
        self.filterEdited.emit(text)

    def setFilterText(self, text):
        self.getFilterLineEdit().setText(text)


class EditorToolBar(BaseToolBar):
    """Internal widget to be placed in a _QToolArea providing buttons for
    moving, adding and removing items from a view based widget"""

    addTriggered = Qt.pyqtSignal()
    removeTriggered  = Qt.pyqtSignal()
    moveTopTriggered = Qt.pyqtSignal()
    moveDownTriggered = Qt.pyqtSignal()
    moveUpTriggered = Qt.pyqtSignal()
    moveBottomTriggered = Qt.pyqtSignal()

    def __init__(self, view=None, parent=None, designMode=False):
        BaseToolBar.__init__(self, name="Taurus editor toolbar", view=view,
                             parent=parent, designMode=designMode)

        af = ActionFactory()
        self._addAction = af.createAction(self, "New item",
                                          icon=Qt.QIcon.fromTheme("list-add"),
                                          tip="Add new item",
                                          triggered=self.onAdd)
        self._removeAction = af.createAction(self, "Remove item",
                                             icon=Qt.QIcon.fromTheme(
                                                 "list-remove"),
                                             tip="Remove item",
                                             triggered=self.onRemove)
        self._moveTopAction = af.createAction(self, "To top",
                                              icon=Qt.QIcon.fromTheme("go-top"),
                                              tip="Move selected item to top",
                                              triggered=self.onMoveTop)
        self._moveUpAction = af.createAction(self, "Move up",
                                             icon=Qt.QIcon.fromTheme("go-up"),
                                             tip="Move selected item up one level",
                                             triggered=self.onMoveUp)
        self._moveDownAction = af.createAction(self, "Move down",
                                               icon=Qt.QIcon.fromTheme(
                                                   "go-down"),
                                               tip="Move selected item down one level",
                                               triggered=self.onMoveDown)
        self._moveBottomAction = af.createAction(self, "To bottom",
                                                 icon=Qt.QIcon.fromTheme(
                                                     "go-bottom"),
                                                 tip="Move selected item to bottom",
                                                 triggered=self.onMoveBottom)
        self.addAction(self._addAction)
        self.addAction(self._removeAction)
        self.addAction(self._moveTopAction)
        self.addAction(self._moveUpAction)
        self.addAction(self._moveDownAction)
        self.addAction(self._moveBottomAction)
        #self.setStyleSheet("QWidget {background : red; }")

    def onAdd(self):
        self.addTriggered.emit()

    def onRemove(self):
        self.removeTriggered.emit()

    def onMoveTop(self):
        self.moveTopTriggered.emit()

    def onMoveUp(self):
        self.moveUpTriggered.emit()

    def onMoveDown(self):
        self.moveDownTriggered.emit()

    def onMoveBottom(self):
        self.moveBottomTriggered.emit()


class SelectionToolBar(BaseToolBar):

    selectAllTriggered = Qt.pyqtSignal()
    clearSelectionTriggered = Qt.pyqtSignal()

    def __init__(self, view=None, parent=None, designMode=False):
        BaseToolBar.__init__(self, name="Taurus selection toolbar", view=view,
                             parent=parent, designMode=designMode)

        af = ActionFactory()
        self._selectAllAction = af.createAction(self, "Select All",
                                                icon=Qt.QIcon.fromTheme(
                                                    "edit-select-all"),
                                                tip="Select all items",
                                                triggered=self.onSelectAll)
        self._clearSelectionAction = af.createAction(self, "Clear selection",
                                                     icon=Qt.QIcon.fromTheme(
                                                         "edit-clear"),
                                                     tip="Clears current selection",
                                                     triggered=self.onclearSelection)

        self.addAction(self._selectAllAction)
        self.addAction(self._clearSelectionAction)

    def onSelectAll(self):
        self.selectAllTriggered.emit()

    def onclearSelection(self):
        self.clearSelectionTriggered.emit()


class RefreshToolBar(BaseToolBar):

    refreshTriggered = Qt.pyqtSignal()

    def __init__(self, view=None, parent=None, designMode=False):
        BaseToolBar.__init__(self, name="Taurus refresh toolbar", view=view,
                             parent=parent, designMode=designMode)

        af = ActionFactory()
        self._refreshAction = af.createAction(self, "Refresh",
                                              icon=Qt.QIcon.fromTheme(
                                                  "view-refresh"),
                                              tip="Refresh view",
                                              triggered=self.onRefresh)
        self.addAction(self._refreshAction)

    def onRefresh(self):
        self.refreshTriggered.emit()


class PerspectiveToolBar(BaseToolBar):

    perspectiveChanged = Qt.pyqtSignal(compat.PY_OBJECT)

    def __init__(self, perspective, view=None, parent=None, designMode=False):
        BaseToolBar.__init__(self, name="Taurus refresh toolbar", view=view,
                             parent=parent, designMode=designMode)
        self._perspective = perspective
        view = self.viewWidget()
        b = self._perspective_button = Qt.QToolButton(self)
        b.setToolTip("Perspective selection")
        b.setPopupMode(Qt.QToolButton.InstantPopup)
        b.setToolButtonStyle(Qt.Qt.ToolButtonTextBesideIcon)

        menu = Qt.QMenu("Perspective", b)
        b.setMenu(menu)
        af = ActionFactory()
        for persp, persp_data in view.KnownPerspectives.items():
            label = persp_data["label"]
            icon = Qt.QIcon.fromTheme(persp_data["icon"])
            tip = persp_data["tooltip"]
            action = af.createAction(self, label, icon=icon, tip=tip,
                                     triggered=self.onSwitchPerspective)
            action.perspective = persp
            menu.addAction(action)
            if persp == perspective:
                b.setDefaultAction(action)

        self._perspectiveAction = self.addWidget(b)

    def switchPerspectiveButton(self):
        """Returns the QToolButton that handles the switch perspective.

        :return: (PyQt4.QtGui.QToolButton) the switch perspective tool button
        """
        return self._perspective_button

    def onSwitchPerspective(self):
        action = self.sender()
        self._perspective = action.perspective
        self._perspective_button.setDefaultAction(action)
        self.perspectiveChanged.emit(action.perspective)

    def perspective(self):
        return self._perspective


class QBaseModelWidget(Qt.QMainWindow):
    """A pure Qt widget designed to display a Qt view widget (QTreeView for
    example), envolved by optional toolbar and statusbar.
    The Qt model associated with the internal Qt view widget should be a
    :class:`taurus.qt.qtcore.model.TaurusBaseModel`"""

    KnownPerspectives = {}
    DftPerspective = None

    itemClicked = Qt.pyqtSignal(compat.PY_OBJECT, int)
    itemDoubleClicked = Qt.pyqtSignal(compat.PY_OBJECT, int)
    itemSelectionChanged = Qt.pyqtSignal()
    currentItemChanged = Qt.pyqtSignal(compat.PY_OBJECT, compat.PY_OBJECT)

    def __init__(self, parent=None, designMode=False, with_filter_widget=True,
                 with_selection_widget=True, with_refresh_widget=True,
                 perspective=None, proxy=None):
        Qt.QMainWindow.__init__(self, parent)
        self.setWindowFlags(Qt.Qt.Widget)
        self._baseQModel = None
        self._toolBars = []

        if with_filter_widget:
            if isinstance(with_filter_widget, (bool, int)):
                self._with_filter_widget = FilterToolBar
            else:
                self._with_filter_widget = with_filter_widget
        else:
            self._with_filter_widget = None

        if with_selection_widget:
            if isinstance(with_selection_widget, (bool, int)):
                self._with_selection_widget = SelectionToolBar
            else:
                self._with_selection_widget = with_selection_widget
        else:
            self._with_selection_widget = None

        if with_refresh_widget:
            if isinstance(with_refresh_widget, (bool, int)):
                self._with_refresh_widget = RefreshToolBar
            else:
                self._with_refresh_widget = with_refresh_widget
        else:
            self._with_refresh_widget = None

        self._proxyModel = proxy

        toolBars = self.createToolArea()
        self._viewWidget = self.createViewWidget()
        statusbar = self.createStatusBar()

        for toolBar in toolBars:
            # toolBar.addSeparator()
            self.addToolBar(toolBar)
        self.setContentsMargins(0, 0, 0, 0)
        self.setCentralWidget(self._viewWidget)
        self.setStatusBar(statusbar)

        if perspective is None:
            perspective = self.DftPerspective

        if len(self.KnownPerspectives) > 1:
            p_bar = self._perspectiveBar = PerspectiveToolBar(
                perspective, view=self, parent=self)
            p_bar.perspectiveChanged.connect(self.onSwitchPerspective)
            self.addToolBar(p_bar)
        else:
            self._perspectiveBar = None
        self._setPerspective(perspective)

    def createViewWidget(self, klass=None):
        raise NotImplementedError

    def createStatusBar(self):
        sb = Qt.QStatusBar()
        sb.setSizeGripEnabled(False)
        return sb

    def createToolArea(self):
        tb = []  # tb = self._toolArea = QToolArea(self)
        if self._with_filter_widget:
            f_bar = self._filterBar = self._with_filter_widget(
                view=self, parent=self)
            f_bar.filterChanged.connect(self.onFilterChanged)
            tb.append(f_bar)
        else:
            self._filterBar = None

        if self._with_selection_widget:
            s_bar = self._selectionBar = self._with_selection_widget(
                view=self, parent=self)
            s_bar.selectAllTriggered.connect(self.onSelectAll)
            s_bar.clearSelectionTriggered.connect(self.onClearSelection)
            tb.append(s_bar)
        else:
            self._selectionBar = None

        if self._with_refresh_widget:
            r_bar = self._refreshBar = self._with_refresh_widget(
                view=self, parent=self)
            r_bar.refreshTriggered.connect(self.onRefreshModel)
            tb.append(r_bar)
        else:
            self._refreshBar = None

        return tb

    def getPerspectiveBar(self):
        return self._perspectiveBar

    def getFilterBar(self):
        return self._filterBar

    def getSelectionBar(self):
        return self._selectionBar

    def getRefreshBar(self):
        return self._refreshBar

    def onRefreshModel(self):
        self.getQModel().refresh(True)

    def onSelectAll(self):
        view = self.viewWidget()
        view.selectAll()

    def onClearSelection(self):
        view = self.viewWidget()
        view.clearSelection()

    def _onClicked(self, index):
        '''Emits an "itemClicked" signal with with the clicked item and column
        as arguments'''
        item = self._mapToSource(index).internalPointer()
        self.itemClicked.emit(item, index.column())

    def _onDoubleClicked(self, index):
        '''Emits an "itemDoubleClicked" signal with the clicked item and column
        as arguments'''
        item = self._mapToSource(index).internalPointer()
        self.itemDoubleClicked.emit(item, index.column())

    def viewWidget(self):
        return self._viewWidget

    def getQModel(self):
        return self.viewWidget().model()

    def getBaseQModel(self):
        return self._baseQModel

    def usesProxyQModel(self):
        return isinstance(self.getQModel(), Qt.QAbstractProxyModel)

    def _mapToSource(self, index):
        if not self.usesProxyQModel():
            return index
        model = self.getQModel()
        while isinstance(model, Qt.QAbstractProxyModel):
            index = model.mapToSource(index)
            model = model.sourceModel()
        return index

    def setQModel(self, qmodel):

        self._baseQModel = qmodel
        while isinstance(self._baseQModel, Qt.QAbstractProxyModel):
            self._baseQModel = self._baseQModel.sourceModel()

        view = self.viewWidget()
        old_selection_model = view.selectionModel()
        CC = 'currentChanged(const QModelIndex &,const QModelIndex &)'
        SC = 'selectionChanged(QItemSelection &, QItemSelection &)'
        if old_selection_model is not None:
            old_selection_model.currentChanged.disconnect(
                                  self.viewCurrentIndexChanged)
            old_selection_model.selectionChanged.disconnect(
                                  self.viewSelectionChanged)
        view.setModel(qmodel)
        new_selection_model = view.selectionModel()
        if new_selection_model is not None:
            new_selection_model.currentChanged.connect(
                               self.viewCurrentIndexChanged)
            new_selection_model.selectionChanged.connect(
                               self.viewSelectionChanged)
        view.setCurrentIndex(view.rootIndex())
        self._updateToolBar()

    def viewSelectionChanged(self, selected, deselected):
        self.itemSelectionChanged.emit()

    def viewCurrentIndexChanged(self, current, previous):
        # if there is a proxy model we have to translate the selection
        base_current = self._mapToSource(current)
        base_previous = self._mapToSource(previous)

        self._updateToolBar(current)

        if base_current.isValid():
            currentTaurusTreeItem = base_current.internalPointer()
        else:
            currentTaurusTreeItem = None

        if base_previous.isValid():
            previousTaurusTreeItem = base_previous.internalPointer()
        else:
            previousTaurusTreeItem = None
        self.currentItemChanged.emit(currentTaurusTreeItem,
                  previousTaurusTreeItem)

    def _updateToolBar(self, current=None, previous=None):
        pass

    def selectedItems(self):
        """Returns a list of all selected non-hidden items

        :return: (list<TaurusTreeItem>)
        """
        view = self.viewWidget()
        return [self._mapToSource(index).internalPointer() for index in view.selectedIndexes()]

    def onFilterChanged(self, filter):
        if not self.usesProxyQModel():
            return
        proxy_model = self.getQModel()
        if len(filter) > 0 and filter[0] != '^':
            filter = '^' + filter
        proxy_model.setFilterRegExp(filter)
        # proxy_model.setFilterFixedString(filter)
        # proxy_model.setFilterWildcard(filter)
        # self.update()

    def refresh(self):
        self.getQModel().refresh()

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # Perspective handling
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    def perspective(self):
        return self._perspectiveBar.perspective()

    def onSwitchPerspective(self, perspective):
        old_qmodel = self.getQModel()
        self._setPerspective(perspective)

        # set the selectables as they where in the previous model
        if hasattr(old_qmodel, "selectables"):
            self.getQModel().setSelectables(old_qmodel.selectables())

        # set the taurus model (if any) to the qmodel
        if hasattr(self, 'getModelObj'):
            taurusModel = self.getModelObj()
            if taurusModel is not None:
                self.getQModel().setDataSource(taurusModel)

    def _setPerspective(self, perspective):
        qmodel_classes = self.KnownPerspectives[perspective]["model"]
        # reversed
        qmodel_class, qmodel_proxy_classes = qmodel_classes[
            -1], qmodel_classes[-2::-1]
        qmodel = qmodel_class(parent=self)
        qmodel_source = qmodel
        if self._proxyModel is None:  # applies the chain of proxies
            for qmodel_proxy_class in qmodel_proxy_classes:
                qproxy = qmodel_proxy_class(self)
                qproxy.setSourceModel(qmodel_source)
                qmodel_source = qproxy
        else:
            self._proxyModel.setSourceModel(qmodel_source)
            qmodel_source = self._proxyModel
        self.setQModel(qmodel_source)

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # QMainWindow overwriting
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    def addToolBar(self, toolbar):
        Qt.QMainWindow.addToolBar(self, toolbar)
        self._toolBars.append(toolbar)

    def insertToolBar(self, before, toolbar):
        if isinstance(before, Qt.QToolBar):
            index = self._toolBars.index(before)
        else:
            index = before
            before = self._toolBars[before]
        Qt.QMainWindow.insertToolBar(self, before, toolbar)
        self._toolBars.insert(index, toolbar)


class TaurusBaseModelWidget(TaurusBaseWidget):
    """A class:`taurus.qt.qtgui.base.TaurusBaseWidget` that connects to a
    taurus model. It must be used together with
    class:`~taurus.qt.qtgui.base.QBaseModelWidget`"""

    def __init__(self, designMode=False):  # , perspective=None, proxy=None):
        name = self.__class__.__name__
        self.call__init__(TaurusBaseWidget, name, designMode=designMode)

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # TaurusBaseWidget overwriting
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    def setModel(self, m):
        TaurusBaseWidget.setModel(self, m)

        view, modelObj = self.viewWidget(), self.getModelObj()
        model = view.model()
        if model is None:
            return
        model.setDataSource(modelObj)

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # QT property definition
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    #: This property holds the unique URI string representing the model name
    #: with which this widget will get its data from. The convention used for
    #: the string can be found :ref:`here <model-concept>`.
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
