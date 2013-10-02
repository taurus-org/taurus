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
taurusconfigeditor.py: 
"""

__all__ = ["QConfigEditor"]

__docformat__ = 'restructuredtext'

from taurus.qt import Qt
import cPickle as pickle
import os
import tempfile
from taurus.qt.qtcore.configuration import BaseConfigurableClass
from taurus.qt.qtgui.resource import getThemeIcon
from taurus.qt.qtgui.container import TaurusWidget
import shutil


class QConfigEditorModel(Qt.QStandardItemModel):
    '''A custom Model for QConfigEditor'''
    def __init__(self, parent = None, designMode = False):
        super(Qt.QStandardItemModel, self).__init__()
        self._temporaryFile = None
        self._settings = None
        self._configurationDictionaries = None
        self._modifiedPerspectives = []
        self.originalFile = None
        self.markedItems = []
        
    def setData(self,index, value, role = Qt.Qt.DisplayRole):
        '''see :meth:`Qt.QAbstractTableModel.setData`'''
        
        idx_data_str = Qt.from_qvariant(index.data(), str)
        value_str = Qt.from_qvariant(value, str)
        if idx_data_str == value_str:
            return False
        #self.itemFromIndex(index).setData(value, role)
        try:
            self.valueChanged(value_str, index)
        except:
            self.emit(Qt.SIGNAL("showError"),'Wrong value!','The value you entered is wrong. The old value will be restored.')
            return Qt.QStandardItemModel.setData(self,index,index.data(),role)
        return Qt.QStandardItemModel.setData(self,index,value,role)

    def loadFile(self,iniFileName):
        '''
        Loads file with setting, creates temporary settings file, where changes
        made to configuration are saved.
        
        :param iniFileName: (str)
        '''
        self.originalFile = unicode(iniFileName)
        self._file = tempfile.NamedTemporaryFile()
        self._temporaryFile = unicode(self._file.name)

        shutil.copyfile(self.originalFile, self._temporaryFile)
        
        self._settings = Qt.QSettings(self._temporaryFile, Qt.QSettings.IniFormat)
        self.clear()
        self.setHorizontalHeaderLabels(['Configuration key', 'type', 'value'])
        self._configurationDictionaries = self.fillTopLevel()
        self.markedItems = []
    
    def deleteBranch(self):
        '''
        Deletes selected branch from the settings tree. Also updates the
        temporary configuration file.
        '''
        tmpindex = self._toDeleteIndex
        item = self.itemFromIndex(tmpindex)
        path = Qt.from_qvariant(item.data(Qt.Qt.UserRole), str)
        self._delete = False
        self._configurationDictionaries = self.removeBranch(self._configurationDictionaries, path)
        
        try: group = eval(str(path).split(';',1)[0])
        except: group = str(path).split(';',1)[0]
        itemToMark = self.itemFromIndex(tmpindex.parent())
        while(itemToMark != None):    
            itemToMark.setData(Qt.QVariant(Qt.QFont("Arial", 10, Qt.QFont.Bold)), Qt.Qt.FontRole)
            itemToMark=self.itemFromIndex(itemToMark.index().parent())
        
        self.markedItems.append(self._toDeleteIndex.parent())
        self.removeRow(tmpindex.row(), tmpindex.parent())
        self.saveSettings(group)
  
    def removeBranch(self, dict, path):
        '''
        Method called recursively by self.deleteBranch. In each step it takes
        next key (from the path) until reaches element to be deleted. After the
        element is deleted, returns updated dictionary.
        
        :param dict: (dict) a taurus configuration dictionary. See 
                     :class:`BaseConfigurableClass`
        :param path: (str) a semicolon-separated string containing the 
                     path of the branch in the tree
        
        :returns:  (dict) the modified config dict
        '''
        val = str(path).split(';',1)
        if len(val)==2:
            path = val[1]
            try: key = eval(val[0])
            except: key = val[0] 
            dict[key] = self.removeBranch(dict[key], path)
            if self._delete == True:
                if not dict.has_key('__orderedConfigNames__'):
                    return dict
                dict['__orderedConfigNames__'] = self.removeBranch(dict['__orderedConfigNames__'], path)
                self._delete = False
            return dict
        else:
            if self._delete == True:
                if dict.count(val[0]) == 0:
                    return dict
                dict.remove(val[0])
                return dict
            if not dict.has_key('__orderedConfigNames__'):
                self._delete = True
            dict.pop(val[0])
            return dict
    
    def valueChanged(self, value, index):
        '''
        Modifies value in the temporary settings file and the model internal
        dictionary. Invoked by :meth:`Qt.QAbstractTableModel.setData`, when user
        make changes to the value in the settings tree.
        
        :param value: (str) the new value (a string that will be python-evaluated)
        :param index: (QModelIndex) index of the model
        '''
        changedItem = self.itemFromIndex(index)
        path = Qt.from_qvariant(changedItem.data(Qt.Qt.UserRole), str)
        self._configurationDictionaries = self.changeTreeValue(self._configurationDictionaries, path, value)
        try: group = eval(str(path).split(';',1)[0])
        except: group = str(path).split(';',1)[0]
        itemToMark = self.itemFromIndex(index.sibling(index.row(), 0))
        self.markedItems.append(itemToMark.index())
        
        self.itemFromIndex(index.sibling(index.row(), 1)).setText(str(type(eval(value))))
        changedItem.setData(Qt.QVariant('Value has been changed. Old value: '+ str(changedItem.text())), Qt.Qt.ToolTipRole)
        itemToMark.setData(Qt.QVariant(getThemeIcon('emblem-important')), Qt.Qt.DecorationRole)
        while(itemToMark != None):    
            itemToMark.setData(Qt.QVariant(Qt.QFont("Arial", 10, Qt.QFont.Bold)), Qt.Qt.FontRole)
            itemToMark=self.itemFromIndex(itemToMark.index().parent())
        self.saveSettings(group)

    def changeTreeValue(self, cdict, path, value):
        '''
        Method called recursively by valueChanged. In each step it takes next
        key (from the path) until reaches element to be modified. After the
        element is modified, returns updated dictionary.
        
        :param cdict: a configuration dictionary.  See :class:`BaseConfigurableClass`
        :param path: (str) a semicolon-separated string containing the 
                     path of the branch in the tree
        :param value: (str) the new value (a string that will be python-evaluated)
        
        :returns:  (dict) the modified config dict
        '''
        val = str(path).split(';',1)
        if len(val) == 2:
            path = val[1]
            try: key = eval(val[0])
            except: key = val[0] 
            cdict[key] = self.changeTreeValue(cdict[key], path, value)
            return cdict
        else:
            cdict[val[0]] = eval(value)
            return cdict
    
    def fillTopLevel(self):
        '''
        Creates a dictionary containing Main Window and Perspectives settings.
        This metod creates top nodes only (names of the perspectives, main
        window) and invokes fillTaurusConfig. Returns complete dictionary.
        
        :returns:  (dict) a configuration dictionary.  See :class:`BaseConfigurableClass`
        '''
        #self.tree.clear()
        root=self.invisibleRootItem()
        item = Qt.QStandardItem('LAST')
        item.setEditable(False)
        #item.setSelectable(False)
        root.appendRow(item)
        mainConfig = {}
        configdict = self.getTaurusConfigFromSettings()
        if configdict is not None:
            mainConfig[None] = configdict
            item.setData(Qt.QVariant('None'), Qt.Qt.UserRole)
            self.fillTaurusConfig(item, configdict)
        self._settings.beginGroup("Perspectives")
        self.perspectives = self._settings.childGroups()
        for name in self.perspectives:
            item = Qt.QStandardItem(name)
            item.setEditable(False)
            #item.setSelectable(False)
            path = Qt.QVariant("Perspectives/"+name)
            item.setData(path, Qt.Qt.UserRole)
            root.appendRow(item)
            self._settings.beginGroup(name)
            configdict = self.getTaurusConfigFromSettings()
            if configdict is not None:
                mainConfig["Perspectives/"+str(name)] = configdict
                self.fillTaurusConfig(item, configdict)
            self._settings.endGroup()
        self._settings.endGroup()

        return mainConfig
        
    def fillTaurusConfig(self, item, configdict):
        '''
        Fills the non-top nodes of the dictionary recursively.
        
        :param item: (Qt.QStandardItem) parent item
        :param configdict: (dict) a configuration dictionary.  See :class:`BaseConfigurableClass`
        '''
        if not BaseConfigurableClass.isTaurusConfig(configdict): return
        #fill the registered keys
        registeredkeys = configdict.get('__orderedConfigNames__',[])
        valuesdict = configdict.get('__itemConfigurations__',{})
        for k in registeredkeys:
            value = valuesdict[k]
            child = Qt.QStandardItem(k)
            if BaseConfigurableClass.isTaurusConfig(value):
                child.setEditable(False)
                item.appendRow(child)
                
                txt = Qt.from_qvariant(item.data(Qt.Qt.UserRole), str)
                path = Qt.QVariant(txt + ";__itemConfigurations__;" + k)
                child.setData(path, Qt.Qt.UserRole)
                self.fillTaurusConfig(child, value) #recursive call to fill all nodes
            else:
                typeV = Qt.QStandardItem(repr(type(value)))
                valueV =Qt.QStandardItem(repr(value))
                
                typeV.setForeground(Qt.QBrush(Qt.QColor('gray')))
                child.setForeground(Qt.QBrush(Qt.QColor('gray')))
                
                item.appendRow([child,typeV,valueV])
                
                txt = Qt.from_qvariant(item.data(Qt.Qt.UserRole), str)
                path = Qt.QVariant(txt + ";__itemConfigurations__;" + k)
                child.setEditable(False)
                typeV.setEditable(False)
                
                child.setData(path, Qt.Qt.UserRole)
                typeV.setData(path, Qt.Qt.UserRole)
                valueV.setData(path, Qt.Qt.UserRole)

        customkeys = [k for k in configdict if k not in ('__orderedConfigNames__', '__itemConfigurations__', 'ConfigVersion', '__pickable__')]
        if len(customkeys) > 0:

            custom = Qt.QStandardItem('[custom]')
            item.appendRow(custom)
            custom.setEditable(False)
            #custom.setSelectable(False)
            custom.setBackground(Qt.QBrush(Qt.QColor('gray')))
            for k in customkeys:
                value = configdict[k]
                child = Qt.QStandardItem(str(k))
                #item.appendRow(child)
                
                if BaseConfigurableClass.isTaurusConfig(value):
                    child.setEditable(False)
                    item.appendRow(child)
                    txt = Qt.from_qvariant(item.data(Qt.Qt.UserRole), str)
                    path = Qt.QVariant(txt +";" + k)
                    child.setData(path, Qt.Qt.UserRole)
                    self.fillTaurusConfig(child, value) #recursive call to fill all nodes
                else:
                    typeV = Qt.QStandardItem(repr(type(value)))
                    valueV =Qt.QStandardItem(repr(value))
                    typeV.setForeground(Qt.QBrush(Qt.QColor('gray')))
                    child.setForeground(Qt.QBrush(Qt.QColor('gray')))
                    item.appendRow([child,typeV,valueV])
                    txt = Qt.from_qvariant(item.data(Qt.Qt.UserRole), str)
                    path = Qt.QVariant(txt + ";" + k)
    
                    child.setData(path, Qt.Qt.UserRole)
                    child.setEditable(False)
                    typeV.setEditable(False)
                    typeV.setData(path, Qt.Qt.UserRole)
                    valueV.setData(path, Qt.Qt.UserRole)

    def getTaurusConfigFromSettings(self, key='TaurusConfig'):
        '''
        Loads and returns the configuration dictionary from the settings file
        using pickle module.
        
        :param key: (str)
        
        :returns (dict)
        '''
        result = None
        qstate = Qt.from_qvariant(self._settings.value(key), 'toByteArray')
        if qstate is not None and not qstate.isNull():
            try: result = pickle.loads(qstate.data())
            except Exception,e: 
                msg = 'problems loading TaurusConfig: \n%s'%repr(e)
                Qt.QMessageBox.critical(None, 'Error loading settings', msg)
        return result
    
    def reloadFile(self):
        '''
        Reloads the file. Configuration tree is build again.
        '''
        self.loadFile(self.originalFile)

    def saveFile(self):
        '''
        Replaces original file with temporary file (where changes were being saved).
        '''
        if self.markedItems == []:
            return
        shutil.copyfile(self._temporaryFile, self.originalFile)
        self.clearChanges()
        #self.reloadFile()
   
    def saveSettings(self, group=None):
        '''Saves the current state to the temporary file
        
        :param group: (str) a prefix that will be added to the keys to be
                       saved (no prefix by default)
        '''  
        if group is not None: 
            self._settings.beginGroup(group)
        
        #store the config dict
        self._settings.setValue("TaurusConfig", Qt.QVariant(Qt.QByteArray(pickle.dumps(self._configurationDictionaries[group]))))
        if group is not None: 
            self._settings.endGroup()
        #self.info('MainWindow settings saved in "%s"'%self._settings.fileName())


    def restoreOriginal(self):
        '''
        Replaces temporary file with the original file and builds again the
        configuration tree.
        '''
        if self.markedItems == []:
            return
        shutil.copyfile(self.originalFile, self._temporaryFile)
        self.reloadFile()

        
    def clearChanges(self):
        '''
        Clears all changes in style of the modified elements in tree view.
        '''
        for index in self.markedItems:
            itemToMark = self.itemFromIndex(index)
            while(itemToMark != None):    
                itemToMark.setData(Qt.QVariant(Qt.QFont("Arial", 10, Qt.QFont.Normal)), Qt.Qt.FontRole)
                itemToMark.setData(Qt.QVariant(), Qt.Qt.DecorationRole)
                itemToMark=self.itemFromIndex(itemToMark.index().parent())
            
    

class QConfigEditor(TaurusWidget):
    '''A widget that shows a tree view of the contents of Taurus 
    configuration files saved by TaurusMainWindow and lets the user edit 
    the values of the configuration keys'''
    
    def __init__(self, parent = None, designMode = False):
        TaurusWidget.__init__(self, parent = parent, designMode = designMode)
        self.setLayout(Qt.QVBoxLayout())
        self.tree = QConfigEditorModel()
        self.treeview = Qt.QTreeView()
        self.tree.setHorizontalHeaderLabels(['Configuration key', 'type', 'value'])
        self.layout().addWidget(self.treeview)
        self._toolbar = Qt.QToolBar("QConfigViewer Main toolBar")
        self._toolbar.addAction(getThemeIcon("document-open"), "Open File", self.loadFile)
        self._toolbar.addAction(getThemeIcon("document-save"), "Save File", self.saveFile)
        self._toolbar.addAction(getThemeIcon("edit-undo"), "Reload from file", self.restoreOriginal)
        self.layout().setMenuBar(self._toolbar)
        self.setWindowTitle('TaurusConfigEditor')
        self.connect(self.tree, Qt.SIGNAL("showError"), self._showError)
        
    def contextMenuEvent(self, event):
        '''Reimplemented from :meth:`QWidget.contextMenuEvent`'''
  
        self.tree._toDeleteIndex = self.treeview.selectedIndexes()[0]
        text = Qt.from_qvariant(self.tree._toDeleteIndex.data(), str)
        if self.tree._toDeleteIndex.column() in [1,2] or text in ['LAST', '[custom]'] or text in self.tree.perspectives:
            return
        menu = Qt.QMenu()
        menu.addAction(getThemeIcon('process-stop'), "Delete branch: "+text, self.tree.deleteBranch)
        menu.addSeparator()
        menu.addAction(getThemeIcon('help-browser') ,"Help")
        menu.exec_(event.globalPos())
        event.accept()
           
    def _showError(self,title, body):
        '''
        Opens a warning dialog with a given title and body.
        
        :title: (str) title
        :body: (str) body
        '''
        Qt.QMessageBox.warning(self,title,body,Qt.QMessageBox.Ok)
    
    def loadFile(self, iniFileName=None):
        '''
        Loads a configuration stored in a file and creates the tree.
        
        :iniFileName: (str) Name of the file. If None is given the user is prompted for a file.
        '''
        if iniFileName is None:
            if self.tree.originalFile is None: path = Qt.QDir.homePath()
            else: path = self.tree.originalFile
            iniFileName = Qt.QFileDialog.getOpenFileName ( self, 'Select a settings file', path, 'Ini Files (*.ini)')
            if not iniFileName:
                return
        self.tree.loadFile(iniFileName)
        self.treeview.setModel(self.tree)
        self.setWindowTitle('TaurusConfigEditor - %s'%os.path.basename(self.tree.originalFile))
        
    def saveFile(self):
        '''
        Replaces original file with temporary file (where changes were being saved).
        '''
        self.tree.saveFile()
        
    def restoreOriginal(self):
        '''
        Replaces temporary file with the original file and builds again the
        configuration tree.
        '''
        self.tree.restoreOriginal()  

def main():
    from taurus.qt.qtgui.application import TaurusApplication
    from taurus.core.util import argparse
    from taurus import Release
    import sys
    
    parser = argparse.get_taurus_parser()
    parser.set_usage("%prog [options] [INIFILENAME]")
    parser.set_description("taurus configuration editor")
    app = TaurusApplication(cmd_line_parser=parser,
                            app_name="taurusconfigeditor",
                            app_version= Release.version)
    args = app.get_command_line_args()
    w = QConfigEditor()
    w.setMinimumSize(500,500)
    w.show()
    if len(args) == 1:
        w.loadFile(args[0])
    
    sys.exit(app.exec_())
        
if __name__ == '__main__':
    main()
    
