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
AttributeChooser.py: widget for choosing (a list of) attributes from a tango DB
"""


import sys
from PyQt4 import Qt
import taurus.core
from taurus.qt.qtgui.container import TaurusWidget
from taurus.qt.qtgui.tree import TaurusDbTreeWidget
from taurus.core.util import CaselessList
import taurus.qt.qtgui.resource


class TaurusModelSelectorTree(TaurusWidget):
    def __init__(self, parent = None, selectables=None, buttonsPos=None, designMode = None):
        TaurusWidget.__init__(self, parent)
        if selectables is None: selectables = [taurus.core.TaurusElementType.Attribute, taurus.core.TaurusElementType.Member]
        self._selectables = selectables
        if buttonsPos is None: buttonsPos = Qt.Qt.BottomToolBarArea
                        
        #tree
        self._deviceTree = TaurusDbTreeWidget(perspective=taurus.core.TaurusElementType.Device)
        self._deviceTree.getQModel().setSelectables(self._selectables)
        self._deviceTree.setUseParentModel(True)
        
        #toolbar 
        self._toolbar = Qt.QToolBar("TangoSelector toolbar")
        self._toolbar.setIconSize(Qt.QSize(16,16))
        self._toolbar.setFloatable(False)
        self._addSelectedAction = self._toolbar.addAction(taurus.qt.qtgui.resource.getThemeIcon("list-add"), "Add selected", self.onAddSelected)
        
        #add to layout
        if buttonsPos == Qt.Qt.BottomToolBarArea:
            self.setLayout(Qt.QVBoxLayout())
            self.layout().addWidget(self._deviceTree)
            self.layout().addWidget(self._toolbar)
        elif buttonsPos == Qt.Qt.TopToolBarArea:
            self.setLayout(Qt.QVBoxLayout())
            self.layout().addWidget(self._toolbar)
            self.layout().addWidget(self._deviceTree)
        elif buttonsPos == Qt.Qt.LeftToolBarArea:
            self._toolbar.setOrientation(Qt.Qt.Vertical)
            self.setLayout(Qt.QHBoxLayout())
            self.layout().addWidget(self._toolbar)
            self.layout().addWidget(self._deviceTree)
        elif buttonsPos == Qt.Qt.RightToolBarArea:
            self._toolbar.setOrientation(Qt.Qt.Vertical)
            self.setLayout(Qt.QHBoxLayout())
            self.layout().addWidget(self._deviceTree)
            self.layout().addWidget(self._toolbar)
        else:
            raise ValueError("Invalid buttons position")
        
        self._deviceTree.recheckTaurusParent()  ##NOT WORKING????
        self.connect(self, Qt.SIGNAL(self.ModelChangedSignal), self._deviceTree.setModel)  ##@todo: This is Workaround because UseSetParentModel is giving trouble again!
    
    def getSelectedModels(self):
        selected = []
        for item in self._deviceTree.selectedItems():
            nfo = item.itemData()
            if isinstance(nfo, taurus.core.TaurusDevInfo):
                selected.append(nfo.fullName())
            elif isinstance(nfo, taurus.core.TaurusAttrInfo):
                selected.append( "%s/%s"%(nfo.device().fullName(),nfo.name()) )
            else: 
                self.info("Unknown item '%s' in selection"%repr(nfo))
        return selected
        
    def onAddSelected(self):
        self.emit(Qt.SIGNAL("addModels"), self.getSelectedModels())
    
    @classmethod
    def getQtDesignerPluginInfo(cls):
        None

class TaurusModelChooser(TaurusWidget):
    '''A widget that allows the user to select a list of models from a tree representing
    devices and attributes from a Tango server.
    
    The user selects models and adds them to a list. Then the user should click on the
    update button to notify that the selection is ready.
    
    signals::
      - "updateModels"  emitted when the user clicks on the update button. It
        passes a list<str> of models that have been selected.
    ''' 
    def __init__(self, parent = None, selectables=None, host=None, designMode = None):
        '''Creator of TaurusModelChooser
        
        :param parent: (QObject) parent for the dialog 
        :param selectables: (list<TaurusElementType>) if passed, only elements of the tree whose
                            type is in the list will be selectable. 
        :param host: (QObject) Tango host to be explored by the chooser
        '''
        TaurusWidget.__init__(self, parent)
        if host is None: host = taurus.Database().getNormalName() 
        self._listedModels = CaselessList([])
        self._singleAttrMode = False
        self._allowDuplicates = False
        
        self.setLayout(Qt.QVBoxLayout())
        
        self.tree =  TaurusModelSelectorTree(selectables = selectables)
        self.tree.setModel(host)
        self.list = Qt.QListWidget()
        self.list.setSelectionMode(Qt.QAbstractItemView.ExtendedSelection)
        applyBT = Qt.QToolButton()
        applyBT.setToolButtonStyle(Qt.Qt.ToolButtonTextBesideIcon)
        applyBT.setText('Apply')
        applyBT.setIcon(taurus.qt.qtgui.resource.getIcon(":/status/available.svg"))
        
        #toolbar 
        self._toolbar = self.tree._toolbar
        self._removeSelectedAction = self._toolbar.addAction(taurus.qt.qtgui.resource.getThemeIcon("list-remove"), "Remove selected", self.onRemoveSelected)
        self._clearSelectedAction = self._toolbar.addAction(taurus.qt.qtgui.resource.getThemeIcon("edit-clear"), "Remove all", self.resetListedModels)
        self._toolbar.addSeparator()
        self._toolbar.addWidget(applyBT)
        self.layout().addWidget(self.tree)
        self.layout().addWidget(self.list)
        
        #self.tree.setUseParentModel(True)  #It does not work!!!!
        self.connect(self, Qt.SIGNAL(self.ModelChangedSignal), self.tree.setModel) ##@todo: This is Workaround because UseSetParentModel is giving trouble again!
        
        #connections:
        self.connect(self.tree, Qt.SIGNAL("addModels"), self.addModels)
        self.connect(applyBT, Qt.SIGNAL("clicked()"), self._onUpdateModels)
#        self.connect(self.tree._deviceTree, Qt.SIGNAL("itemDoubleClicked"), self.onTreeDoubleClick)
        
#    def onTreeDoubleClick(self, item, colum): #@todo: Implement this function properly
#        if item.Role in self.tree._selectables:
#            self.addModels([str(item.text())])
    
    def getListedModels(self, asMimeData=False):
        '''returns the list of models that have been added
        
        :param asMimeData: (bool) If False (default), the return value will be a
                           list of models. If True, the return value is a 
                           `QMimeData` containing at least `TAURUS_MODEL_LIST_MIME_TYPE`
                           and `text/plain` MIME types. If only one model was selected,
                           the mime data also contains a TAURUS_MODEL_MIME_TYPE.
        
        :return: (list<str> or QMimeData) the type of return depends on the value of `asMimeData`'''
        if asMimeData:
            md =  Qt.QMimeData()
            md.setData(taurus.qt.qtcore.mimetypes.TAURUS_MODEL_LIST_MIME_TYPE, "\r\n".join(self._listedModels))
            md.setText(", ".join(self._listedModels))
            if len(self._listedModels) == 1:
                md.setData(taurus.qt.qtcore.mimetypes.TAURUS_MODEL_MIME_TYPE, str(self._listedModels[0]))
            return md
        return self._listedModels
    
    def setListedModels(self, models):
        '''adds the given list of models to the widget list
        '''
        self._listedModels = CaselessList(models)
        self.list.clear()
        self.list.addItems(models)
        
    def resetListedModels(self):
        '''equivalent to setListedModels([])'''
        self._listedModels = CaselessList([])
        self.list.clear()
        
    def updateList(self, attrList ): 
        '''for backwards compatibility with AttributeChooser only. Use :meth:`setListedModels` instead'''
        self.info('ModelChooser.updateList() is provided for backwards compatibility only. Use setListedModels() instead')
        self.setListedModels(attrList)
    
    def addModels(self, models):
        ''' Add given models to the selected models list'''
        for m in models:
            if self._allowDuplicates or m not in self._listedModels:
                self._listedModels.append(m)
                self.list.addItem(m)
    
    def onRemoveSelected(self):
        '''
        Remove the list-selected models from the list
        '''
        toremove = [str(item.text()).lower() for item in self.list.selectedItems()]
        newlist = [model for model in self._listedModels if model.lower() not in toremove]
        self.setListedModels(newlist)
        
    def _onUpdateModels(self):
        self.emit(Qt.SIGNAL("updateModels"), self._listedModels)
        if taurus.core.TaurusElementType.Attribute in self.tree._selectables:
            self.emit(Qt.SIGNAL("UpdateAttrs"), self._listedModels) #for backwards compatibility with the old AttributeChooser
    
    def setSingleAttrMode(self, single):
        '''sets whether the selection should be limited to just one model
        (single=True) or not (single=False)'''
        if single == self._singleAttrMode: return        
        if single:
            self.tree.treeView().setSelectionMode(Qt.QAbstractItemView.SingleSelection)
        else:
            self.tree.treeView().setSelectionMode(Qt.QAbstractItemView.ExtendedSelection)
        self._singleAttrMode = single
        
    def isSingleAttrMode(self):
        '''returns True if the selection is limited to just one model. Returns False otherwise.
        
        :return: (bool)'''
        return self._singleAttrMode
    
    def resetSingleAttrMode(self):
        '''equivalent to setSingleAttrMode(False)'''
        self.setSingleAttrMode(self, False)
    
    @staticmethod
    def modelChooserDlg(parent = None, selectables=None, host=None, asMimeData=False):
        '''Static method that launches a modal dialog containing a TaurusModelChooser
        
        :param parent: (QObject) parent for the dialog 
        :param selectables: (list<TaurusElementType>) if passed, only elements of the tree whose
                            type is in the list will be selectable. 
        :param host: (QObject) Tango host to be explored by the chooser
        :param asMimeData: (bool) If False (default),  a list of models will be.
                           returned. If True, a `QMimeData` object will be
                           returned instead. See :meth:`getListedModels` for a
                           detailed description of this QMimeData object.
        
        :return: (list,bool or QMimeData,bool) Returns a models,ok tuple. models can be 
                 either a list of models or a QMimeData object, depending on
                 `asMimeData`. ok is True if the dialog was accepted (by
                 clicking on the "update" button) and False otherwise
        '''
        dlg = Qt.QDialog(parent)
        layout = Qt.QVBoxLayout()
        w = TaurusModelChooser(parent = parent, selectables=selectables, host=host)
        layout.addWidget(w)
        dlg.setLayout(layout)
        dlg.connect(w,Qt.SIGNAL('updateModels'), dlg.accept)
        dlg.exec_()
        return w.getListedModels(asMimeData=asMimeData), (dlg.result() == dlg.Accepted)
    
    @classmethod
    def getQtDesignerPluginInfo(cls):
        ret = TaurusWidget.getQtDesignerPluginInfo()
        ret['module'] = 'taurus.qt.qtgui.panel'
        ret['icon'] = ":/designer/listview.png"
        ret['container'] = False
        ret['group'] = 'Taurus Composite Widgets'
        return ret
        
        
def main(args):
    if len(sys.argv)>1: 
        host=sys.argv[1]
    else: 
        host = None
    
    app = Qt.QApplication(args)
    print TaurusModelChooser.modelChooserDlg(host=host)
    sys.exit()

if __name__=="__main__":
    main(sys.argv)
