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

"""This module provides base widget that displays a Qt view widget envolved
by a toolbar and a status bar (optional)"""

__all__ = ["QBaseModelWidget", "TaurusBaseModelWidget"]

__docformat__ = 'restructuredtext'

from PyQt4 import Qt

from taurus.qt.qtcore.model import *
from taurus.qt.qtgui.util import ActionFactory
from taurus.qt.qtgui.resource import getIcon, getThemeIcon
from taurusbase import TaurusBaseWidget

class _FilterWidget(Qt.QWidget):
    """Internal widget providing quick filter to be placed in a toolbar"""
    
    def __init__(self, parent = None, designMode = False):
        name = self.__class__.__name__
        super(_FilterWidget, self).__init__(parent)
        self.init()
        
    def init(self):
        l = Qt.QHBoxLayout()
        l.setContentsMargins(0,0,0,0)
        self.setLayout(l)
        
        filterLineEdit = self._filterLineEdit = Qt.QLineEdit()
        filterLineEdit.setSizePolicy(Qt.QSizePolicy(Qt.QSizePolicy.Preferred, Qt.QSizePolicy.Preferred))
        filterLineEdit.setToolTip("Quick filter")
        Qt.QObject.connect(filterLineEdit, Qt.SIGNAL("textChanged(const QString &)"), self._filterChanged)
        l.addWidget(filterLineEdit)

        clearFilterButton = self._clearFilterButton = Qt.QPushButton(getThemeIcon("edit-clear"), "")
        clearFilterButton.setToolTip("Clear filter")
        Qt.QObject.connect(clearFilterButton, Qt.SIGNAL("clicked()"), self._clearFilter)
        l.addWidget(clearFilterButton)

    def filterLineEdit(self):
        return self._filterLineEdit
    
    def _clearFilter(self):
        self.filterLineEdit().setText("")

    def _filterChanged(self, text=None):
        text = text or self.filterLineEdit().text()
        self.emit(Qt.SIGNAL("filterChanged"), text)


class _QToolArea(Qt.QWidget):
    
    def __init__(self, parent=None):
        Qt.QWidget.__init__(self, parent)
        l0 = Qt.QHBoxLayout(self)
        l1 = Qt.QHBoxLayout(self)
        l0.setContentsMargins(0, 0, 0, 0)
        l1.setContentsMargins(0, 0, 0, 0)
        l0.addLayout(l1, 0)
        l0.addStretch(1)
        self.setLayout(l0)
        self._layout = l1
        self._iconSize = Qt.QSize(16,16)
    
    def addToolBar(self, toolbar):
        toolbar.setIconSize(self._iconSize)
        self._layout.addWidget(toolbar)

    def insertToolBar(self, before, toolbar):
        idx = before
        toolbar.setIconSize(self._iconSize)
        if isinstance(before, Qt.QWidget):
            idx = self._layout.indexOf(before)
        self._layout.insertWidget(idx, toolbar)
    
    def setIconSize(self, qsize):
        self._iconSize = qsize
        l = self._layout
        for i in range(l.count()):
            l.itemAt(i).widget().setIconSize(qsize)
    
    def iconSize(self):
        return self._iconSize

    def toolBar(self, index=0):
        return self._layout.itemAt(index).widget()


class QBaseModelWidget(Qt.QWidget):
    """A pure Qt widget designed to display a Qt view widget (QTreeView for example),
    envolved by optional toolbar and statusbar.
    The Qt model associated with the internal Qt view widget should be a
    :class:`taurus.qt.qtcore.model.TaurusBaseModel`"""
    
    def __init__(self, parent=None, designMode=False, with_filter_widget=True):
        Qt.QWidget.__init__(self, parent)
        self._baseQModel = None
        self._with_filter_widget = with_filter_widget
        self.__init()
    
    def createViewWidget(self):
        raise NotImplementedError
    
    def createStatusBar(self):
        sb = self._statusbar = Qt.QStatusBar()
        sb.setSizeGripEnabled(False)
        return sb
    
    def createToolArea(self):
        tb = self._toolArea = _QToolArea(self)
        v_bar = self._viewBar = Qt.QToolBar("Taurus view toolbar")
        v_bar.setFloatable(True)
        tb.addToolBar(v_bar)
        filter_action = None
        if self._with_filter_widget:
            f_bar = self._filterBar = Qt.QToolBar("Taurus filter toolbar")
            filterWidget = self._filterWidget = _FilterWidget()
            Qt.QObject.connect(filterWidget, Qt.SIGNAL("filterChanged"), self.setFilter)
            filter_action = self._filterAction = f_bar.addWidget(filterWidget)
            tb.addToolBar(f_bar)
        else:
            self._filterBar = None
            self._filterWidget = None
            self._filterAction = None

        s_bar = self._selectionBar = Qt.QToolBar("Taurus selection toolbar")
        r_bar = self._refreshBar = Qt.QToolBar("Taurus refresh toolbar")
        
        af = ActionFactory()
        self._selectAllAction = af.createAction(self, "Select All",
                                                icon=getThemeIcon("edit-select-all"),
                                                tip="Select all items",
                                                triggered=self.selectAllTree)
        s_bar.addAction(self._selectAllAction)
        tb.addToolBar(s_bar)
        self._refreshAction = af.createAction(self, "Refresh",
                                              icon=getThemeIcon("view-refresh"),
                                              tip="Refresh",
                                              triggered=self.refreshModel)
        r_bar.addAction(self._refreshAction)
        tb.addToolBar(r_bar)

        return tb
    
    def __init(self):
        l = Qt.QGridLayout()
        l.setContentsMargins(0,0,0,0)
        self.setLayout(l)
        
        toolarea = self.createToolArea()
        self._viewWidget = self.createViewWidget()
        statusbar = self.createStatusBar()
        l.setMenuBar(toolarea)
        l.addWidget(self._viewWidget, 0, 0)
        l.addWidget(statusbar, 1 ,0)

    def refreshModel(self):
        self.getQModel().refresh(True)

    def selectAllTree(self):
        view = self.viewWidget()
        view.selectAll()

    def _onClicked (self, index):
        '''Emits an "itemClicked" signal with with the clicked item and column as arguments'''
        item = self._mapToSource(index).internalPointer()
        self.emit(Qt.SIGNAL('itemClicked'),item, index.column())
        
    def _onDoubleClicked (self, index):
        '''Emits an "itemDoubleClicked" signal with the clicked item and column as arguments'''
        item = self._mapToSource(index).internalPointer()
        self.emit(Qt.SIGNAL('itemDoubleClicked'),item, index.column())

    def viewWidget(self):
        return self._viewWidget
    
    def toolArea(self):
        return self._toolArea

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
            Qt.QObject.disconnect(old_selection_model, Qt.SIGNAL(CC),
                                  self.viewCurrentIndexChanged)
            Qt.QObject.disconnect(old_selection_model, Qt.SIGNAL(SC),
                                  self.viewSelectionChanged)
        view.setModel(qmodel)
        new_selection_model = view.selectionModel()
        if new_selection_model is not None:
            Qt.QObject.connect(new_selection_model, Qt.SIGNAL(CC),
                               self.viewCurrentIndexChanged)
            Qt.QObject.connect(new_selection_model, Qt.SIGNAL(SC),
                               self.viewSelectionChanged)
        view.setCurrentIndex(view.rootIndex())
        self._updateToolBar()
    
    def viewSelectionChanged(self, selected, deselected):
        self.emit(Qt.SIGNAL("itemSelectionChanged"))
    
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
        self.emit(Qt.SIGNAL("currentItemChanged"), currentTaurusTreeItem,
                  previousTaurusTreeItem)
    
    def _updateToolBar(self, current=None, previous=None):
        pass
    
    def selectedItems(self):
        """Returns a list of all selected non-hidden items
        
        :return: (list<TaurusTreeItem>)
        """
        view = self.viewWidget()
        return [self._mapToSource(index).internalPointer() for index in view.selectedIndexes()]
    
    def setFilter(self, filter):
        if not self.usesProxyQModel():
            return
        proxy_model = self.getQModel()
        if len(filter) > 0 and filter[0] != '^':
            filter = '^' + filter
        proxy_model.setFilterRegExp(filter)
        #proxy_model.setFilterFixedString(filter)
        #proxy_model.setFilterWildcard(filter)
        #self.update()
    
    def refresh(self):
        self.getQModel().refresh()


class TaurusBaseModelWidget(TaurusBaseWidget):
    """A class:`taurus.qt.qtgui.base.TaurusBaseWidget` that connects to a
    taurus model. It must be used together with class:`taurus.qt.qtgui.base.QBaseModelWidget`"""
    
    KnownPerspectives = { }
    DftPerspective = None

    def __init__(self, designMode=False, perspective=None, proxy=None):
        name = self.__class__.__name__
        self._perspective = None
        self._proxyModel = proxy
        self.call__init__(TaurusBaseWidget, name, designMode=designMode)
        if perspective is None:
            perspective = self.DftPerspective
        self.__init(perspective)

    def __init(self, perspective):
        toolArea = self.toolArea()
        p_bar = self._perspectiveBar = Qt.QToolBar("Perspective toolbar")
        
        b = self._perspective_button = Qt.QToolButton(p_bar)
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
        
        self._perspectiveAction = self._perspectiveBar.addWidget(b)
        toolArea.insertToolBar(0, p_bar)
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

    def setModel(self, m):
        TaurusBaseWidget.setModel(self, m)

        view, modelObj = self.viewWidget(), self.getModelObj()
        model = view.model()
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