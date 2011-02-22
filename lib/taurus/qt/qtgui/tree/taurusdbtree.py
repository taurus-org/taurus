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

__all__ = ["QDbTreeWidget", "TaurusDbTreeWidget"]

__docformat__ = 'restructuredtext'

import PyQt4.Qt as Qt

import taurus.core

from taurus.qt.qtcore.model import *
import taurus.qt.qtgui.base
import taurus.qt.qtgui.resource

ElemType = taurus.core.TaurusElementType
TaurusBaseWidget = taurus.qt.qtgui.base.TaurusBaseWidget
getThemeIcon = taurus.qt.qtgui.resource.getThemeIcon
getIcon = taurus.qt.qtgui.resource.getIcon
getElementTypeIcon = taurus.qt.qtgui.resource.getElementTypeIcon


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
        return self.treeWidget().treeView()    

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
        viewWidget = treeWidget.treeView()
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


class QDbTreeWidget(Qt.QWidget):
    """A pure Qt widget implementing a tree with a navigation toolbar"""
    
    def __init__(self, parent = None):
        super(QDbTreeWidget, self).__init__(parent)
        self._baseQModel = None
        self.__init()
        
    def __init(self):
        l = Qt.QGridLayout()
        l.setContentsMargins(0,0,0,0)
        self.setLayout(l)

        tb = self._toolbar = Qt.QToolBar("Taurus tree toolbar")
        tb.setIconSize(Qt.QSize(16,16))
        tb.setFloatable(False)

        tree = self._tree = Qt.QTreeView()

        sb = self._statusbar = Qt.QStatusBar()
        sb.setSizeGripEnabled(False)
        
        filterWidget = self._filterWidget = _FilterWidget()
        Qt.QObject.connect(filterWidget, Qt.SIGNAL("filterChanged"), self.setFilter)
        tb.addWidget(filterWidget)
        
        tb.addSeparator()
        self._selectAllAction = tb.addAction(getThemeIcon("edit-select-all"), "Select All", self.selectAllTree)
        tb.addSeparator()
        self._expandAllAction = tb.addAction(getIcon(":/actions/expand-all.svg"), "Expand All", self.expandAllTree)
        self._collapseAllAction = tb.addAction(getIcon(":/actions/collapse-all.svg"), "Collapse All", tree.collapseAll)
        tb.addSeparator()
        self._refreshAction = tb.addAction(getThemeIcon("view-refresh"), "Refresh", self.refreshTree)
        tb.addSeparator()
        self._goIntoAction = tb.addAction(getThemeIcon("go-down"), "Go Into", self.goIntoTree)
        self._goUpAction = tb.addAction(getThemeIcon("go-up"), "Go Up", self.goUpTree)
        self._goTopAction = tb.addAction(getThemeIcon("go-top"), "Go Top", self.goTopTree)
        
        self._goIntoAction.setToolTip("Go into the selected item")
        self._goUpAction.setToolTip("Go up one level")
        self._goTopAction.setToolTip("Go to top level")

        tb.addSeparator()
        self._navigationBar = _NavigationWidget(self, tb)
        tb.addWidget(self._navigationBar )
        l.setMenuBar(tb)

        tree.setSortingEnabled(True)
        tree.setUniformRowHeights(True)
        tree.setAlternatingRowColors(True)
        tree.setSelectionBehavior(Qt.QTreeView.SelectRows)
        tree.setSelectionMode(Qt.QTreeView.ExtendedSelection)
        tree.setDragEnabled(True)
        tree.setDropIndicatorShown(True)
        
        Qt.QObject.connect(tree, Qt.SIGNAL("expanded(QModelIndex)"), self.onExpanded)
        Qt.QObject.connect(tree, Qt.SIGNAL("clicked(QModelIndex)"), self._onClicked)
        Qt.QObject.connect(tree, Qt.SIGNAL("doubleClicked(QModelIndex)"), self._onDoubleClicked)
        h = tree.header()
        h.setResizeMode(0, Qt.QHeaderView.Stretch)
        l.addWidget(tree, 0, 0)
        l.addWidget(sb, 1 ,0)

    def resizeColumns(self):
        tree = self.treeView()
        model = tree.model()
        if model is None:
            return
        for c in range(model.columnCount()):
            tree.resizeColumnToContents(c)

    def refreshTree(self):
        self.getQModel().refresh(True)

    def selectAllTree(self):
        tree = self.treeView()
        tree.selectAll()

    def expandAllTree(self):
        self._statusbar.showMessage("Expanding all nodes... (it may take a few seconds)")
        tree = self.treeView()
        Qt.QTimer.singleShot(0, self._expandTree)

    def _expandTree(self):
        tree = self.treeView()
        tree.expandAll()
        self._statusbar.showMessage("All nodes expanded!", 3000)

    def onExpanded(self):
        self.resizeColumns()
        
    def _onClicked (self, index):
        '''Emits an "itemClicked" signal with with the clicked item and column as arguments'''
        item = self._mapToSource(index).internalPointer()
        self.emit(Qt.SIGNAL('itemClicked'),item, index.column())
        
    def _onDoubleClicked (self, index):
        '''Emits an "itemDoubleClicked" signal with the clicked item and column as arguments'''
        item = self._mapToSource(index).internalPointer()
        self.emit(Qt.SIGNAL('itemDoubleClicked'),item, index.column())

    def treeView(self):
        return self._tree
    
    def toolBar(self):
        return self._toolbar

    def goIntoAction(self):
        return self._goIntoAction
    
    def goTopAction(self):
        return self._goTopAction
    
    def goUpAction(self):
        return self._goUpAction

    def getQModel(self):
        return self.treeView().model()

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
        
        tree = self.treeView()
        old_selection_model = tree.selectionModel()
        CC = 'currentChanged(const QModelIndex &,const QModelIndex &)'
        SC = 'selectionChanged(QItemSelection &, QItemSelection &)'
        if old_selection_model is not None:
            Qt.QObject.disconnect(old_selection_model, Qt.SIGNAL(CC),
                                  self.treeCurrentIndexChanged)
            Qt.QObject.disconnect(old_selection_model, Qt.SIGNAL(SC),
                                  self.treeSelectionChanged)
        tree.setModel(qmodel)
        new_selection_model = tree.selectionModel()
        if new_selection_model is not None:
            Qt.QObject.connect(new_selection_model, Qt.SIGNAL(CC),
                               self.treeCurrentIndexChanged)
            Qt.QObject.connect(new_selection_model, Qt.SIGNAL(SC),
                               self.treeSelectionChanged)
        tree.setCurrentIndex(tree.rootIndex())
        self._updateToolBar()
    
    def treeSelectionChanged(self, selected, deselected):
        self.emit(Qt.SIGNAL("itemSelectionChanged"))
    
    def treeCurrentIndexChanged(self, current, previous):
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
        self.emit(Qt.SIGNAL("currentItemChanged"), currentTaurusTreeItem, previousTaurusTreeItem)

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
        tree = self.treeView()
        index = tree.rootIndex()
        if not index.isValid():
            return
        index_parent = index.parent()
        
        tree.setRootIndex(index_parent)
        tree.setCurrentIndex(index)
        self._updateToolBar()

    def goTopTree(self):
        tree = self.treeView()
        current_root = tree.rootIndex()
        p = current_root.parent()
        while p.isValid():
            p = p.parent()
        tree.setRootIndex(p)
        tree.setCurrentIndex(p)
        self._updateToolBar()
            
    def _updateToolBar(self, current=None, previous=None):
        tree = self.treeView()
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
    
    def selectedItems(self):
        """Returns a list of all selected non-hidden items
        
        :return: (list<TaurusTreeItem>)
        """
        return [self._mapToSource(index).internalPointer() for index in self._tree.selectedIndexes()]
    
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


class TaurusDbTreeWidget(QDbTreeWidget, TaurusBaseWidget):
    """A class:`taurus.qt.qtgui.tree.QTrauTree` that connects to a
    :class:`taurus.core.TaurusDatabase` model. It can show the list of database elements
    in four different perspectives:
    
    - device : a three level hierarchy of devices (domain/family/name)
    - server : a server based perspective
    - class : a class based perspective
    
    Filters can be inserted into this widget to restrict the tree nodes that are
    seen.
    """
    
    KnownPerspectives = { ElemType.Device : [TaurusDbDeviceProxyModel, TaurusDbDeviceModel,],
                          ElemType.Server : [TaurusDbServerProxyModel, TaurusDbServerModel,],
                     ElemType.DeviceClass : [TaurusDbDeviceClassProxyModel, TaurusDbDeviceClassModel,], }

    DftPerspective = ElemType.Device

    def __init__(self, parent=None, designMode=False, perspective=None, proxy=None):
        name = self.__class__.__name__
        if perspective is None: 
            perspective = self.DftPerspective
        self._perspective = perspective
        self._proxyModel = proxy
        self.call__init__wo_kw(QDbTreeWidget, parent)
        self.call__init__(TaurusBaseWidget, name, designMode=designMode)
        self.__init()
    
    def __init(self):
        qmodel_classes = self.KnownPerspectives[self._perspective]
        qmodel_class, qmodel_proxy_classes = qmodel_classes[-1], qmodel_classes[:-1]
        qmodel_proxy_classes.reverse()
        qmodel = qmodel_class(self)
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
    
    def sizeHint(self):
        return Qt.QSize(1024, 512)

    def perspective(self):
        return self._perspective
        
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # TaurusBaseWidget overwriting
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    def updateStyle(self):
        """overwritten from class:`taurus.qt.qtgui.base.TaurusBaseWidget`. It is called when
        the taurus model changes."""
        self.resizeColumns()
    
    def setModel(self, m):
        TaurusBaseWidget.setModel(self, m)

        tree, db = self.treeView(), self.getModelObj()
        model = tree.model()
        if model is None: return
        model.setDataSource(db)
    
    def getModelClass(self):
        return taurus.core.TaurusDatabase

    @classmethod
    def getQtDesignerPluginInfo(cls):
        ret = TaurusBaseWidget.getQtDesignerPluginInfo()
        ret['module'] = 'taurus.qt.qtgui.tree'
        ret['group'] = 'Taurus Item Widgets'
        ret['icon'] = ":/designer/listview.png"
        return ret
    
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


class _TaurusTreePanel(Qt.QWidget, TaurusBaseWidget):
    """A demonstration panel to show how :class:`taurus.qt.qtcore.TaurusDbBaseModel`
    models can interact with several model view widgets like QTreeView,
    QTableView, QListView and QComboBox"""
    
    def __init__(self, parent = None, designMode = False):
        """doc please!"""
        name = self.__class__.__name__
        self.call__init__wo_kw(Qt.QWidget, parent)
        self.call__init__(TaurusBaseWidget, name, designMode=designMode)
        self.init(designMode)
    
    def init(self, designMode):
        l = Qt.QGridLayout()
        l.setContentsMargins(0,0,0,0)
        self.setLayout(l)
        
#        tb = self._toolbar = Qt.QToolBar("Taurus tree panel toolbar")
#        tb.setFloatable(False)
#        refreshAction = self._refreshAction = tb.addAction(getThemeIcon("view-refresh"),"Refresh", self.refresh)

#        l.addWidget(tb, 0, 0)
        
        main_panel = Qt.QTabWidget()
        self._device_tree_view = TaurusDbTreeWidget(perspective=ElemType.Device)
        self._device_table_view = Qt.QTableView()
        self._device_table_view.setModel(TaurusDbBaseModel())
        self._device_list_view = Qt.QListView()
        self._device_list_view.setModel(TaurusDbSimpleDeviceModel())
        self._server_tree_view = TaurusDbTreeWidget(perspective=ElemType.Server)
        self._class_tree_view = TaurusDbTreeWidget(perspective=ElemType.DeviceClass)
        
        self._device_combo_view = Qt.QWidget()
        combo_form = Qt.QFormLayout()
        self._device_combo_view.setLayout(combo_form)
        
        self._combo_dev_tree_widget = TaurusDbTreeWidget(perspective=ElemType.Device)
        qmodel = self._combo_dev_tree_widget.getQModel()
        qmodel.setSelectables([ElemType.Member])
        device_combo = Qt.QComboBox()
        device_combo.setModel(qmodel)
        device_combo.setMaxVisibleItems(20)
        device_combo.setView(self._combo_dev_tree_widget.treeView())
        combo_form.addRow("Device selector (by device hierarchy):", device_combo)
        
        self._combo_attr_tree_widget = TaurusDbTreeWidget(perspective=ElemType.Device)
        qmodel = self._combo_attr_tree_widget.getQModel()
        device_combo = Qt.QComboBox()
        device_combo.setModel(qmodel)
        device_combo.setMaxVisibleItems(20)
        device_combo.setView(self._combo_attr_tree_widget.treeView())
        combo_form.addRow("Attribute selector (by device hierarchy):", device_combo)

        self._combo_dev_table_view = Qt.QTableView()
        self._combo_dev_table_view.setModel(TaurusDbBaseModel())
        qmodel = self._combo_dev_table_view.model()
        qmodel.setSelectables([ElemType.Device])
        device_combo = Qt.QComboBox()
        device_combo.setModel(qmodel)
        device_combo.setMaxVisibleItems(20)
        device_combo.setView(self._combo_dev_table_view)
        combo_form.addRow("Device selector (by plain device):", device_combo)
        
        main_panel.addTab(self._device_tree_view, "Device (Tree View)")
        main_panel.addTab(self._device_table_view, "Device (Table View)")
        main_panel.addTab(self._device_list_view, "Device (List View)")
        main_panel.addTab(self._server_tree_view, "Server (Tree View)")
        main_panel.addTab(self._class_tree_view, "Class (Tree View)")
        main_panel.addTab(self._device_combo_view, "ComboBox Views")
        
        l.addWidget(main_panel, 1, 0)
        
        self._main_panel = main_panel
    
    def deviceTreeWidget(self):
        return self._device_tree_view

    def deviceTableWidget(self):
        return self._device_table_view

    def deviceListWidget(self):
        return self._device_list_view
    
    def serverTreeWidget(self):
        return self._server_tree_view

    def classTreeWidget(self):
        return self._class_tree_view
    
    def sizeHint(self):
        return Qt.QSize(1024, 512)

    def _updateTreeModels(self):
        db_name, db = self.getModel(), self.getModelObj()
        
        self._device_tree_view.setModel(db_name)
        
        model = self._device_table_view.model()
        if model is not None:
            model.setDataSource(db)
        
        model = self._device_list_view.model()
        if model is not None:
            model.setDataSource(db)
        
        self._server_tree_view.setModel(db_name)
        self._class_tree_view.setModel(db_name)
        self._combo_dev_tree_widget.setModel(db_name)
        self._combo_attr_tree_widget.setModel(db_name)
        
        model = self._combo_dev_table_view.model()
        if model is not None:
            model.setDataSource(db)
        
    def refresh(self):
        db = self.getModelObj()
        if db is None:
            return
        db.refreshCache()
        self._device_tree_view.refresh()
        self._device_table_view.model().refresh()
        self._device_list_view.model().refresh()
        self._server_tree_view.refresh()
        self._class_tree_view.refresh()
    
    def goIntoTree(self):
        index = self._device_tree_view.currentIndex()
        if index is None:
            return
        #index_parent = index.parent()
        #if index_parent is None:
        #    return
        self._device_tree_view.setRootIndex(index)
    
    def goUpTree(self):
        index = self._device_tree_view.rootIndex()
        if index is None:
            return
        index_parent = index.parent()
        if index_parent is None:
            return
        self._device_tree_view.setRootIndex(index_parent)
    
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # TaurusBaseWidget overwriting
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    
    def getModelClass(self):
        return taurus.core.TaurusDatabase
    
    @Qt.pyqtSignature("setModel(QString)")
    def setModel(self, model):
        """Sets/unsets the model name for this component
        
        :param model: (str) the new model name"""
        super(_TaurusTreePanel, self).setModel(model)
        self._updateTreeModels()
            
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
    model = Qt.pyqtProperty("QString", TaurusBaseWidget.getModel,
                            TaurusBaseWidget.setModel, TaurusBaseWidget.resetModel)


def main_TaurusTreePanel(host):
    w = _TaurusTreePanel()
    w.setWindowIcon(getElementTypeIcon(ElemType.Device))
    w.setWindowTitle("A Taurus Tree Example")
    w.setModel(host)
    w.show()

def main_TaurusDbTreeWidget(host, perspective=ElemType.Device):
    w = TaurusDbTreeWidget(perspective=perspective)
    w.setWindowIcon(getElementTypeIcon(perspective))
    w.setWindowTitle("A Taurus Tree Example")
    w.setModel(host)
    w.show()

if __name__ == "__main__":
    import sys
    app = Qt.QApplication(sys.argv)
    
    host = "controls02:10000"
    if len(sys.argv) > 1:
        host = sys.argv[1]

    #main_TaurusTreePanel(host)
    main_TaurusDbTreeWidget(host, ElemType.Device)
    
    sys.exit(app.exec_())
