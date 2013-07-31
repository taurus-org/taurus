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
configbrowser.py: 
"""

__all__ = ["QConfigViewer"]

__docformat__ = 'restructuredtext'

raise DeprecationWarning("QConfigViewer is deprecated. Use QConfigEditor instead")

from taurus.qt import Qt
import cPickle as pickle
import os
from taurus.qt.qtcore.configuration import BaseConfigurableClass
import taurus.qt.qtgui.resource

getThemeIcon = taurus.qt.qtgui.resource.getThemeIcon

class QConfigViewer(Qt.QWidget):
    '''A widget that shows a tree view of the contents of Taurus 
    configuration files saved by TaurusMainWindow'''
    def __init__(self, parent=None, designerMode=False):
        Qt.QWidget.__init__(self, parent)
        self.setLayout(Qt.QVBoxLayout())
        self.tree = Qt.QTreeWidget()
        self.tree.setColumnCount(3)
        self.tree.setHeaderLabels(['Configuration key', 'type', 'value'])
        self.layout().addWidget(self.tree)
        self.currentFile = None
        self._toolbar = Qt.QToolBar("QConfigViewer Main toolBar")
        self.layout().setMenuBar(self._toolbar)
        self._toolbar.addAction(getThemeIcon("document-open"), "Open File", self.loadFile)
        self._toolbar.addAction(getThemeIcon("view-refresh"), "Reload File", self.reloadFile)
        self.setWindowTitle('TaurusConfigBrowser')

    def reloadFile(self):
        self.loadFile(self.currentFile)
        
    def loadFile(self, iniFileName=None):
        if iniFileName is None:
            if self.currentFile is None: path = Qt.QDir.homePath()
            else: path = self.currentFile
            iniFileName = Qt.QFileDialog.getOpenFileName ( self, 'Select a settings file', path, 'Ini Files (*.ini)')
        self.currentFile = unicode(iniFileName)
        self.settings = Qt.QSettings(iniFileName, Qt.QSettings.IniFormat)
        self.fillTopLevel()
        self.setWindowTitle('TaurusConfigBrowser - %s'%os.path.basename(self.currentFile))
               
    def fillTopLevel(self):
        self.tree.clear()
        item = Qt.QTreeWidgetItem(['LAST'])
        self.tree.addTopLevelItem(item)
        configdict = self.getTaurusConfigFromSettings()
        if configdict is not None:  self.fillTaurusConfig(item, configdict)
        
        self.settings.beginGroup("Perspectives")
        self.perspectives = self.settings.childGroups()
        for name in self.perspectives:
            item = Qt.QTreeWidgetItem([name])
            self.tree.addTopLevelItem(item)
            self.settings.beginGroup(name)
            configdict = self.getTaurusConfigFromSettings()
            if configdict is not None:  self.fillTaurusConfig(item, configdict)
            self.settings.endGroup()
        self.settings.endGroup()

    def getTaurusConfigFromSettings(self, key='TaurusConfig'):
        result = None
        qstate = Qt.from_qvariant(self.settings.value(key), 'toByteArray')
        if not qstate.isNull(): 
            try: result = pickle.loads(qstate.data())
            except Exception,e: 
                msg = 'problems loading TaurusConfig: \n%s'%repr(e)
                print msg
                Qt.QMessageBox.critical(self, 'Error loading settings', msg)
        return result
    
    def fillTaurusConfig(self, item, configdict):
        if not BaseConfigurableClass.isTaurusConfig(configdict): return
        #fill the registered keys
        registeredkeys = configdict.get('__orderedConfigNames__',[])
        valuesdict = configdict.get('__itemConfigurations__',{})
        for k in registeredkeys:
            value = valuesdict[k]
            child = Qt.QTreeWidgetItem([k])
            item.addChild(child)
            if BaseConfigurableClass.isTaurusConfig(value):
                self.fillTaurusConfig(child, value) #recursive call to fill all nodes
            else:
                child.setText(1,repr(type(value)))
                child.setText(2,repr(value))
        #now deal with custom keys (not registered)
        customkeys = [k for k in configdict if k not in ('__orderedConfigNames__', '__itemConfigurations__', 'ConfigVersion', '__pickable__')]
        if len(customkeys) > 0:
            custom = Qt.QTreeWidgetItem(['[custom]'])
            item.addChild(custom)
            for k in customkeys:
                value = configdict[k]
                child = Qt.QTreeWidgetItem([k])
                item.addChild(child)
                if BaseConfigurableClass.isTaurusConfig(value):
                    self.fillTaurusConfig(child, value) #recursive call to fill all nodes
                else:
                    child.setText(1,repr(type(value)))
                    child.setText(2,repr(value))


def main():
    from taurus.qt.qtgui.application import TaurusApplication
    from taurus.core.util import argparse
    import sys
    
    parser = argparse.get_taurus_parser()
    parser.set_usage("%prog [options] [INIFILENAME]")
    parser.set_description("taurus configuration viewer")
    app = TaurusApplication(cmd_line_parser=parser,
                            app_name="taurusconfigbrowser",
                            app_version=taurus.Release.version)
    args = app.get_command_line_args()
    
    w = QConfigViewer()
    w.show()
    
    if len(args) == 1:
        w.loadFile(args[0])
    
    sys.exit(app.exec_())
        
if __name__ == '__main__':
    main()
    
