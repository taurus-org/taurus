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

"""
itemsmodel Model and view for new CurveItem configuration 
"""
__all__=['TaurusModelModel','TaurusModelItem', 'TaurusModelList']
#raise UnimplementedError('Under Construction!')

import copy

from taurus.qt import Qt
from PyQt4 import Qwt5
import taurus
from taurus.core import TaurusException, TaurusElementType
from taurus.qt.qtcore.mimetypes import TAURUS_MODEL_LIST_MIME_TYPE, TAURUS_ATTR_MIME_TYPE
from taurus.qt.qtgui.resource import getThemeIcon, getElementTypeIcon


#set some named constants
SRC_ROLE =  Qt.Qt.UserRole + 1

class TaurusModelItem(object):
    '''An item object for :class:`TaurusModelModel`. Exposes `display` `icon` and `ok` 
    attributes which are calculated and kept in synch with the property `src`'''
    def __init__(self, src=None):
        self.display = ''
        self.icon = Qt.QIcon()
        self.ok = True
        self._src = None
        self.setSrc(self.src)
        
    def __repr__(self):
        ret = "TaurusModelItem('%s')"%(self.display)
        return ret
    
    def getSrc(self):
        '''getter for src.'''
        return self._src
    
    def setSrc(self, src):
        '''processes the src and sets the values of _src, display, icon and ok attributes'''
        if src is None:
            self._src, self.display, self.icon, self.ok = '', '(Empty)', Qt.QIcon(),True
            return
        src = str(src).strip()
        self._src = src
        #empty
        if src == '':
            self.display, self.icon, self.ok = '(Empty)', Qt.QIcon(),True
            return
        #for tango devices
        try:
            dev = taurus.Device(src)
            if dev.isValidDev():
                self.display, self.icon, self.ok = dev.getSimpleName(), getElementTypeIcon(TaurusElementType.Device), True
                return
            else:
                self.display, self.icon, self.ok = src, getThemeIcon('network-error'),False
                return
        except:               
            #for tango attributes
            try:
                attr = taurus.Attribute(src) 
                dev = attr.getParentObj()
            except TaurusException:
                self.display, self.icon, self.ok = src, getThemeIcon('dialog-warning'), False
                return
            if not dev.isValidDev():
                self.display, self.icon, self.ok = src, getThemeIcon('network-error'),False
                return
            self.display, self.icon, self.ok = attr.getSimpleName(), getElementTypeIcon(TaurusElementType.Attribute),True
        
    #properties
    src = property(getSrc, setSrc)

class TaurusModelModel(Qt.QAbstractListModel):
    ''' A Qt data model for describing taurus models
    '''

    def __init__(self,items=None):
        if items is None: items=[]
        super(TaurusModelModel,self).__init__()
        self.items = items
    
    def addItem(self, item):
        '''appends an item to the internal list
        
        :param item: (TaurusModelItem) '''
        self.items.append(item)
        
    def dumpData(self):
        '''returns a deep copy of the internal item list representation'''
        return copy.deepcopy(self.items)
    
    def rowCount(self,index=Qt.QModelIndex()):
        '''reimplemented from :class:`Qt.QAbstractListModel`'''
        return len(self.items)
        
    def data(self, index, role=Qt.Qt.DisplayRole):
        '''reimplemented from :class:`Qt.QAbstractListModel`'''
        if not index.isValid() or not (0 <= index.row() < self.rowCount()):
            return Qt.QVariant()
        row = index.row()
        #Display Role
        if role == Qt.Qt.DisplayRole:
            return Qt.QVariant(Qt.QString(self.items[row].display))
        elif role == Qt.Qt.DecorationRole:
            return Qt.QVariant(self.items[row].icon)
        elif role == Qt.Qt.TextColorRole:
            if not self.items[row].src:
                return Qt.QVariant(Qt.QColor('gray'))
            return Qt.QVariant(Qt.QColor(self.items[row].ok and 'green' or 'red'))
        elif role == SRC_ROLE:
            return Qt.QVariant(Qt.QString(self.items[row].src))
        elif role == Qt.Qt.ToolTipRole:
            return Qt.QVariant(Qt.QString(self.items[row].src))
        if role == Qt.Qt.EditRole:
            return Qt.QVariant(Qt.QString(self.items[row].src))
        return Qt.QVariant()
        
    def flags(self, index):
        '''reimplemented from :class:`Qt.QAbstractListModel`'''
        if not index.isValid():
            return Qt.Qt.ItemIsEnabled
        return Qt.Qt.ItemFlags(Qt.Qt.ItemIsEnabled |Qt.Qt.ItemIsEditable | Qt.Qt.ItemIsDragEnabled | Qt.Qt.ItemIsDropEnabled | Qt.Qt.ItemIsSelectable)
                     
    def setData(self, index, value=None, role=Qt.Qt.EditRole):
        '''reimplemented from :class:`Qt.QAbstractListModel`'''
        if index.isValid() and (0 <= index.row() < self.rowCount()):
            row = index.row()
            item = self.items[row]
            value = unicode(value.toString())
            item.src = value
            self.emit(Qt.SIGNAL("dataChanged(QModelIndex,QModelIndex)"),index, index)
            return True
        return False
    
    def insertRows(self, position=None,rows=1, parentindex=None):
        '''reimplemented from :class:`Qt.QAbstractListModel`'''
        if position is None: position = self.rowCount()
        if parentindex is None: parentindex = Qt.QModelIndex()
        self.beginInsertRows(parentindex, position, position + rows -1)
        slice = [TaurusModelItem() for i in range(rows)]
        self.items = self.items[:position]+slice+self.items[position:]
        self.endInsertRows()
        return True
        
    def removeRows(self, position,rows=1,parentindex=None):
        '''reimplemented from :class:`Qt.QAbstractListModel`'''
        if parentindex is None: parentindex = Qt.QModelIndex()
        self.beginRemoveRows(parentindex, position, position + rows - 1)
        self.items = self.items[:position]+self.items[position+rows:]
        self.endRemoveRows()
        self.reset()
        return True
    
    def clearAll(self):
        '''clears all rows'''
        self.removeRows(0, self.rowCount())
        
    def swapItems(self, index1, index2):
        '''swap the items described by index1 and index2 in the list'''
        r1, r2 = index1.row(), index2.row()
        self.items[r1], self.items[r2] = self.items[r2], self.items[r1]
        self.emit(Qt.SIGNAL("dataChanged(QModelIndex,QModelIndex)"),index1, index2)
    
    def mimeTypes(self):
        '''reimplemented from :class:`Qt.QAbstractListModel`'''
        result = list(Qt.QAbstractItemModel.mimeTypes(self))
        result += [TAURUS_ATTR_MIME_TYPE, 'text/plain']
        return result
    
    def dropMimeData(self, data, action, row, column, parent):
        '''reimplemented from :class:`Qt.QAbstractListModel`'''
        if row == -1:
            if parent.isValid(): row = parent.row()
            else: row = parent.rowCount()
        if data.hasFormat(TAURUS_ATTR_MIME_TYPE):
            self.setData(self.index(row), 
                         value=Qt.QVariant(str(data.data(TAURUS_ATTR_MIME_TYPE))))
            return True
        elif data.hasFormat(TAURUS_MODEL_LIST_MIME_TYPE):
            models = str(data.data(TAURUS_MODEL_LIST_MIME_TYPE)).split()
            self.insertRows(row,len(models))
            for i,m in enumerate(models):
                self.setData(self.index(row+i), value=Qt.QVariant(m))
            return True
        elif data.hasText():
            self.setData(self.index(row), Qt.QVariant(data.text()))
            return True
        return False
    
    def mimeData(self, indexes):
        '''reimplemented from :class:`Qt.QAbstractListModel`'''
        mimedata = Qt.QAbstractListModel.mimeData(self, indexes)
        if len(indexes)==1:
#            mimedata.setData(TAURUS_ATTR_MIME_TYPE, str(self.data(indexes[0]).toString()))
            mimedata.setText(self.data(indexes[0],role=SRC_ROLE).toString())
        return mimedata
        #mimedata.setData()
    

class TaurusModelList(Qt.QListView):
    '''A list view widget to display and manage a list of models
    
    Tries to identify the type of model and show the state of the device/attr
    associated qith it. It also allows drag and drop of models and sorting.
    '''
    
    def __init__(self, parent=None, items=None, designMode=False):
        super(TaurusModelList,self).__init__(parent)
        if items is None: items = []
        self._model = TaurusModelModel(items)
        self.setModel(self._model)
        self.setDragDropMode(self.DragDrop)
        self.setSelectionMode(self.ExtendedSelection)
        
        self._contextMenu = Qt.QMenu()
        self.addRowAction = self._contextMenu.addAction(getThemeIcon('list-add'), 'Add new row', self._model.insertRows)
        self.removeSelectedAction = self._contextMenu.addAction(getThemeIcon('list-remove'), 'Remove Selected', self.removeSelected)
        self.removeAllAction = self._contextMenu.addAction(getThemeIcon('edit-clear'), 'Clear all', self._model.clearAll)
        self.moveUpAction = self._contextMenu.addAction(getThemeIcon('go-up'), 'Move up in the list', self._onMoveUpAction)
        self.moveDownAction = self._contextMenu.addAction(getThemeIcon('go-down'), 'Move down in the list', self._onMoveDownAction)
        
        #signal connections
        selectionmodel = self.selectionModel()
        self.connect(selectionmodel, Qt.SIGNAL("selectionChanged(QItemSelection, QItemSelection)"), self._onSelectionChanged)
        self._onSelectionChanged(Qt.QItemSelection(),Qt.QItemSelection())
        
    def _onSelectionChanged(self, selected, deselected):
        '''updates the status of the actions that depend on the selection'''
        selectedIndexes = self.selectionModel().selectedRows()
        self.removeSelectedAction.setEnabled(len(selectedIndexes)>0)
        self.moveUpAction.setEnabled(len(selectedIndexes)==1 and selectedIndexes[0].row()>0)
        self.moveDownAction.setEnabled(len(selectedIndexes)==1 and (0 <= selectedIndexes[0].row() < self._model.rowCount()-1))
        
        
    def contextMenuEvent(self, event):
        '''see :meth:`QWidget.contextMenuEvent`'''
        self._contextMenu.exec_(event.globalPos())
        event.accept()    
    
    def _onMoveUpAction(self):
        '''slot for move up action'''
        selected = self.selectionModel().selectedIndexes()
        if len(selected)!=1:
            return
        i1 =  selected[0]
        i2 = self._model.index(i1.row()-1)
        self._model.swapItems(i1, i2)
        self.selectionModel().select(i2, Qt.QItemSelectionModel.ClearAndSelect)       
    
    def _onMoveDownAction(self):        
        '''slot for move down action'''
        selected = self.selectionModel().selectedIndexes()
        if len(selected)!=1:
            return
        i1 =  selected[0]
        i2 = self._model.index(i1.row()+1)
        self._model.swapItems(i1, i2) 
        self.selectionModel().select(i2, Qt.QItemSelectionModel.ClearAndSelect) 
    
    def removeSelected(self):
        '''removes selected items from the list'''
        selected = sorted([idx.row() for idx in self.selectionModel().selectedRows()], reverse=True)
        for row in selected: #we remove rows starting from the last one
            self._model.removeRows(row)
        
    def addModels(self, models):
        '''adds models to the list
        
        :param models: (list<str>) sequence of model names to be added
        '''
        nmodels = len(models)
        rowcount = self._model.rowCount()
        self._model.insertRows(rowcount,nmodels)
        for i,m in enumerate(models):
            self._model.setData(self._model.index(rowcount+i), value=Qt.QVariant(m))
            
    def getModelItems(self):
        '''returns the model item objects
        
        :return: (list<TaurusModelItem>)
        
        .. seealso:: :meth:`getModelList`
        '''
        return self._model.dumpData()
    
    def getModelList(self):
        '''returns a the model names corresponding to the items in the list
        
        :return: (list<str>)
        
        .. seealso:: :meth:`getModelItems`
        '''
        return [unicode(s.src) for s in self.getModelItems()]
    
    @classmethod
    def getQtDesignerPluginInfo(cls):
        return { 
            'group'     : 'Taurus Input Widgets',
            'icon'      : ':/designer/taurus.png',
            'container' : False,
            'module'    : 'taurus.qt.qtgui.panel'
             }

        