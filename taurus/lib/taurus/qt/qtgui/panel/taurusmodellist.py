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
import taurus
from taurus.core.taurusbasetypes import TaurusElementType
from taurus.core.taurusexception import TaurusException
from taurus.qt.qtcore.mimetypes import TAURUS_MODEL_LIST_MIME_TYPE, TAURUS_ATTR_MIME_TYPE, TAURUS_MODEL_MIME_TYPE
from taurus.qt.qtgui.resource import getThemeIcon, getElementTypeIcon, getIcon


#set some named constants
SRC_ROLE =  Qt.Qt.UserRole + 1

class TaurusModelItem(object):
    '''An item object for :class:`TaurusModelModel`. Exposes `display` `icon` and `ok` 
    attributes which are calculated and kept in synch with the property `src`'''
    def __init__(self, src=None, display=None):
        self.icon = Qt.QIcon()
        self.ok = True
        self._src = None
        self.setSrc(src)
        if display is not None:
            self.display = display
        
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
        if src == self._src:
            return
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
            except Exception: #@todo: this catchall except is here as an emergency bugfix, but should probably be narrowed to PyTango DevFailed. 
                self.display, self.icon, self.ok = src, getThemeIcon('network-error'),False
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
            return Qt.Qt.ItemIsEnabled|Qt.Qt.ItemIsDropEnabled
        return Qt.Qt.ItemFlags(Qt.Qt.ItemIsEnabled |Qt.Qt.ItemIsEditable | Qt.Qt.ItemIsDragEnabled | Qt.Qt.ItemIsSelectable)
                     
    def setData(self, index, value=None, role=Qt.Qt.EditRole):
        '''reimplemented from :class:`Qt.QAbstractListModel`'''
        if index.isValid() and (0 <= index.row() < self.rowCount()):
            row = index.row()
            item = self.items[row]
            value = Qt.from_qvariant(value, unicode)
            if role == Qt.Qt.EditRole:
                item.src = value
            elif role == Qt.Qt.DisplayRole:
                item.display = value
            self.emit(Qt.SIGNAL("dataChanged(QModelIndex,QModelIndex)"),index, index)
            return True 
        return False
    
    def insertRows(self, position=None,rows=1, parentindex=None, items=None):
        '''reimplemented from :class:`Qt.QAbstractListModel`'''
        if position is None or position==-1: position = self.rowCount()
        if parentindex is None: parentindex = Qt.QModelIndex()
        if items is None:
            slice = [TaurusModelItem() for i in xrange(rows)]
        else:
            slice=list(items)
            rows = len(slice) #note that the rows parameter is ignored if items is passed
        self.beginInsertRows(parentindex, position, position + rows -1)
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
        result += [TAURUS_ATTR_MIME_TYPE, TAURUS_MODEL_MIME_TYPE, 
                   TAURUS_MODEL_LIST_MIME_TYPE, 'text/plain']
        return result
    
    def dropMimeData(self, data, action, row, column, parent):
        '''reimplemented from :class:`Qt.QAbstractListModel`'''
        if row == -1 and parent.isValid(): 
            row = parent.row()
        if data.hasFormat(TAURUS_ATTR_MIME_TYPE):
            items = [str(data.data(TAURUS_ATTR_MIME_TYPE))]
        elif data.hasFormat(TAURUS_MODEL_MIME_TYPE):
            items = [str(data.data(TAURUS_MODEL_MIME_TYPE))]
        elif data.hasFormat(TAURUS_MODEL_LIST_MIME_TYPE):
            items = str(data.data(TAURUS_MODEL_LIST_MIME_TYPE)).split()
        elif data.hasText():
            items = [str(data.text())]
        else:
            return False
        self.insertItems(row, items)
        return True
    
    def insertItems(self, row, items):
        '''convenience method to add new rows by passing a list of strings ()
        
        :param row: (int) the row of the list at which the item insertion 
                         starts, if row==-1, items will be appended to the list
        :param items: (seq) a sequence items to add to the list. The objects 
                      in the sequence can be either strings, :class:`TaurusModelItem` objects
                      or tuples of valid arguments for initializing :class:`TaurusModelItem` objects
        '''
        itemobjs = []
        for e in items:
            if isinstance(e,TaurusModelItem): 
                itemobjs.append(e)
            elif isinstance(e,basestring):
                itemobjs.append(TaurusModelItem(src=e))
            else: #assuming it is a sequence of arguments that can be passed to the constructor of TaurusModelItem
                itemobjs.append(TaurusModelItem(*e))
        self.insertRows(position=row,items=itemobjs)
    
    def mimeData(self, indexes):
        '''reimplemented from :class:`Qt.QAbstractListModel`'''
        mimedata = Qt.QAbstractListModel.mimeData(self, indexes)
        if len(indexes)==1:
#            mimedata.setData(TAURUS_ATTR_MIME_TYPE, Qt.from_qvariant(self.data(indexes[0]), str)))
            txt = Qt.from_qvariant(self.data(indexes[0],role=SRC_ROLE), str)
            mimedata.setText(txt)
        return mimedata
        #mimedata.setData()
    

class TaurusModelList(Qt.QListView):
    '''A list view widget to display and manage a list of models
    
    Tries to identify the type of model and show the state of the device/attr
    associated with it. It also allows drag and drop of models and sorting.
    '''
    
    def __init__(self, parent=None, items=None, designMode=False):
        super(TaurusModelList,self).__init__(parent)
        if items is None: items = []
        self._model = TaurusModelModel(items)
        self.setModel(self._model)
        self.setDragDropMode(self.DragDrop)
        #self.setAcceptDrops(True)
        self.setSelectionMode(self.ExtendedSelection)
        
        self._contextMenu = Qt.QMenu(self)
        self.addRowAction = self._contextMenu.addAction(getThemeIcon('list-add'), 'Add new row', self.newRow, Qt.QKeySequence.New)
        self.removeSelectedAction = self._contextMenu.addAction(getThemeIcon('list-remove'), 'Remove Selected', self.removeSelected, Qt.QKeySequence.Delete)
        self.removeAllAction = self._contextMenu.addAction(getThemeIcon('edit-clear'), 'Clear all', self.clear, Qt.QKeySequence("Ctrl+Del"))
        self.moveUpAction = self._contextMenu.addAction(getThemeIcon('go-up'), 'Move up in the list', self._onMoveUpAction, Qt.QKeySequence("Alt+Up"))
        self.moveDownAction = self._contextMenu.addAction(getThemeIcon('go-down'), 'Move down in the list', self._onMoveDownAction, Qt.QKeySequence("Alt+Down"))
        self.editDisplayAction = self._contextMenu.addAction(getIcon(':/actions/format-text-italic.svg'), 'Edit the display (leave the source)', self._onEditDisplay, Qt.QKeySequence("Alt+D"))
        
        self.addActions([self.addRowAction,self.removeSelectedAction,self.removeAllAction,self.moveUpAction,self.moveDownAction, self.editDisplayAction])
        
        #signal connections
        selectionmodel = self.selectionModel()
        self.connect(selectionmodel, Qt.SIGNAL("selectionChanged(QItemSelection, QItemSelection)"), self._onSelectionChanged)
        self.connect(self._model, Qt.SIGNAL("dataChanged (QModelIndex, QModelIndex)"), self._onDataChanged)
        self.connect(self._model, Qt.SIGNAL("rowsInserted (QModelIndex, int, int)"), self._onDataChanged)
        self.connect(self._model, Qt.SIGNAL("rowsRemoved (QModelIndex, int, int)"), self._onDataChanged)
        self._onSelectionChanged(Qt.QItemSelection(),Qt.QItemSelection())
    
    def clear(self):
        '''removes all items from the list'''
        self._model.clearAll()
        
    def _onEditDisplay(self):
        selected = self.selectionModel().selectedIndexes()
        if len(selected)==1:
            idx = selected[0]
        else:
            return
        value = Qt.from_qvariant(self._model.data(idx, role=Qt.Qt.DisplayRole), str)
        src = Qt.from_qvariant(self._model.data(idx, role=SRC_ROLE), str)
        value,ok = Qt.QInputDialog.getText(self, "Display Value", "Display value for %s?"%src, Qt.QLineEdit.Normal, value)
        if not ok:
            return
        self._model.setData(idx, Qt.QVariant(value), role=Qt.Qt.DisplayRole)
    
    def _onSelectionChanged(self, selected, deselected):
        '''updates the status of the actions that depend on the selection'''
        selectedIndexes = self.selectionModel().selectedRows()
        self.removeSelectedAction.setEnabled(len(selectedIndexes)>0)
        self.moveUpAction.setEnabled(len(selectedIndexes)==1 and selectedIndexes[0].row()>0)
        self.moveDownAction.setEnabled(len(selectedIndexes)==1 and (0 <= selectedIndexes[0].row() < self._model.rowCount()-1))
        self.editDisplayAction.setEnabled(len(selectedIndexes)>0)
    
    def _onDataChanged(self, *args):
        '''emits a signal containing the current data as a list of strings'''
        self.emit(Qt.SIGNAL("dataChanged"), self.getModelItems())
        
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
        
    def newRow(self,position=None):
        '''adds an empty row *before* the given position
        
        :param position: (int or None) position at which the new row will be added.
                         If None passed, it will be added at the end.
        '''
        if position is None:
            selected = self.selectionModel().selectedIndexes()
            if len(selected)==0:
                position = -1
            elif len(selected) == 1:
                position = selected[0].row()
            else:
                return
        self._model.insertItems(position,[''])
    
    def removeSelected(self):
        '''removes selected items from the list'''
        selected = sorted([idx.row() for idx in self.selectionModel().selectedRows()], reverse=True)
        for row in selected: #we remove rows starting from the last one
            self._model.removeRows(row)
        
    def addModels(self, models):
        '''adds models to the list
        
        :param models: (list<str>) sequence of model names to be added
        '''
        self._model.insertItems(-1, models)
            
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
            'group'     : 'Taurus Input',
            'icon'      : ':/designer/taurus.png',
            'container' : False,
            'module'    : 'taurus.qt.qtgui.panel'
             }

if __name__ == "__main__":
    from taurus.qt.qtgui.application import TaurusApplication
    import sys
    app = TaurusApplication()  
    w = TaurusModelList()
    w.addModels(["item%i"%i for i in range(3)]+[TaurusModelItem(src='src1',display='d1')]+[('src2','d2')])
    w.show()    
    sys.exit(app.exec_()) 
