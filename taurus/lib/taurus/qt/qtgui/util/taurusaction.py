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

"""This module is designed to provide a library of taurus Qt actions"""

#__all__ = []

__docformat__ = 'restructuredtext'

import os
import xml.dom.minidom

from taurus.qt import Qt
from taurus.qt.qtcore.configuration import BaseConfigurableClass
from taurus.qt.qtgui.resource import getThemeIcon

class ExternalAppAction(Qt.QAction, BaseConfigurableClass):
    """ An specialized QAction for launching external applications
    
    Signals: apart of those from QAction, it emits a  "cmdArgsChanged" signal
    with the current cmdArgs list as its argument.
    """
    DEFAULT_ICON_NAME = 'application-x-executable'
    def __init__(self, cmdargs, text=None, icon=None, parent=None, interactive=True):
        '''creator
        
        :param cmdargs: (list<str> or str) A list of strings to be passed to
                        :meth:`subprocess.Popen` for launching the external
                        application. It can also be a single string containing a
                        command. See :meth:`setCmdArgs`
        :param text: (str) see :class:`Qt.QAction`
        :param icon: (QIcon or any other object that can be passed to QIcon creator) see :class:`Qt.QAction`
        :param parent: (QObject) The parent object
        '''
        if isinstance(cmdargs, (basestring, Qt.QString)):
            import shlex
            cmdargs = shlex.split(str(cmdargs))
        self.path = os.path.realpath(cmdargs and cmdargs[0] or '')
        if text is None: text = os.path.basename(cmdargs and cmdargs[0] or '')
        if icon is None:
            icon = getThemeIcon(self.DEFAULT_ICON_NAME)
        elif isinstance(icon,basestring):
            tmp = getThemeIcon(icon) 
            if not tmp.isNull(): icon=tmp

        Qt.QAction.__init__(self, Qt.QIcon(icon), text, parent)
        BaseConfigurableClass.__init__(self)
        self.interactive = interactive
        self._process = []
        self.setCmdArgs(cmdargs)
        self.connect(self, Qt.SIGNAL("triggered()"), self.actionTriggered)
        self.setToolTip("Launches %s (external application)"%text)
        self.registerConfigProperty(self.cmdArgs, self.setCmdArgs, 'cmdArgs')
    
    def setCmdArgs(self, cmdargs):
        '''Sets the command args for executing this external application.
        
        It emits the "cmdArgsChanged" signal with the new cmdArgs list 
        
        :param cmdargs: (list<str> or str) A list of strings to be passed to
                        :meth:`subprocess.Popen` for launching the external
                        application. It can also be a string containing a
                        command, which will be automatically converted to a list
        '''
        if isinstance(cmdargs, (basestring, Qt.QString)):
            import shlex
            cmdargs = shlex.split(str(cmdargs))
        self.__cmdargs = cmdargs
        self.emit(Qt.SIGNAL("cmdArgsChanged"), self.__cmdargs)
        
    def cmdArgs(self):
        return self.__cmdargs
    
    @Qt.pyqtSignature("triggered()")
    def actionTriggered(self,args=None):
        '''launches the external application as a subprocess'''
        import subprocess
        try:
            if args is not None:
                if isinstance(args, (basestring, Qt.QString)):
                    import shlex
                    args = shlex.split(str(args))
                args = self.cmdArgs()+args
            else: 
                args = self.cmdArgs()
            if any(args):
                #Qt.QMessageBox.warning(self.parentWidget(),'Warning','In ExternalAppAction(%s)'%args)
                self._process.append(subprocess.Popen(args))
                return True
            else:
                return False
        except OSError:
            err = "Error launching %s"%unicode(self.text())
            msg = "Cannot launch application:\n" + \
                  " ".join(self.__cmdargs) + \
                  "\nHint: Check that %s is installed and in the path"%unicode(self.text())
            if self.interactive: 
                Qt.QMessageBox.warning(self.parentWidget(), err, msg)
            from taurus.core.util import Logger
            Logger().warning('%s:\n%s'%(err,msg))
            return False
    
    def kill(self):
        #Kills all processes opened by this application
        [p.kill() for p in self._process]
                                   
    def check(self):
        '''Returns True if the application is available for executing
        
        :return: (bool)
        '''
        #raise NotImplementedError  #@todo: implement a checker (check if self.cmdargs[0] is in the execution path and is executable
        path = os.path.realpath(self.cmdArgs()[0])
        try: 
            os.stat(path)
            return True
        except:
            return False

class TaurusMenu(Qt.QMenu):
    """Base class for Taurus Menus"""
    
    def __init__(self, parent):
        Qt.QMenu.__init__(self, parent)
    
    def build(self, data):
        m_node = xml.dom.minidom.parseString(data).childNodes[0]
        self.buildFromXML(m_node)
    
    def getActionFactory(self):
        import taurusactionfactory
        return taurusactionfactory.ActionFactory()
        
    def buildFromXML(self, m_node):
        widget = self.parent()
        if m_node.hasAttribute('label'):
            self.setTitle(m_node.getAttribute('label'))
            
        for node in m_node.childNodes:
            name = node.nodeName
            if name == 'Menu':
                m = self.getActionFactory().buildMenu(widget, node)
                if m:
                    self.addMenu(m)
            else:
                a = self.getActionFactory().buildAction(widget, node)
                if a:
                    self.addAction(a)


class TaurusAction(Qt.QAction):
    """Base class for Taurus Actions"""
    
    def __init__(self, parent):
        import taurus.qt.qtgui.base
        
        if (parent is None) or \
            (not isinstance(parent, Qt.QWidget)) or \
            (not isinstance(parent, taurus.qt.qtgui.base.TaurusBaseComponent)):
            raise RuntimeError("Invalid parent. Must be a valid Taurus widget.") 
        
        Qt.QAction.__init__(self, parent)
        
        self.connect(parent, Qt.SIGNAL('modelChanged(const QString &)'), self.modelChanged)
        self.connect(self, Qt.SIGNAL("triggered()"), self.actionTriggered)
        
        self.update()
        
    def update(self):
        model = self.parent().getModelObj()
        self.setDisabled(model is None)
        
    @Qt.pyqtSignature("modelChanged(const QString &)")
    def modelChanged(self, modelName):
        self.update()
        
    @Qt.pyqtSignature("triggered()")
    def actionTriggered(self):
        pass


class SeparatorAction(TaurusAction):
    
    menuID = "_Separator_"
    
    def __init__(self, parent=None):
        Qt.QAction.__init__(self, parent)
        self.setSeparator(True)


class AttributeHistoryAction(TaurusAction):
    
    menuID = "AttrHistory"
    
    def __init__(self, parent=None):
        TaurusAction.__init__(self, parent)
        self.setText("Show history...")
        
    def actionTriggered(self):
        dialog = Qt.QDialog()
        dialog.exec_()
    

class AttributeAllConfigAction(TaurusAction):
    
    menuID = "AttrConfig"
    
    def __init__(self, parent=None):
        TaurusAction.__init__(self, parent)
        self.setText("All...")
        
    def actionTriggered(self):
        #raise NotImplementedError('This action is not yet implemented')
        taurus_widget = self.parent()
        from taurus.qt.qtgui.dialog.taurusconfigurationdialog import TaurusConfigurationDialog
        d = TaurusConfigurationDialog()
        d.setModel(taurus_widget.getModelName())
        d.exec_()


class AttributeMonitorDeviceAction(TaurusAction):
    
    menuID = "MonitorDevice"
    
    def __init__(self, parent=None):
        TaurusAction.__init__(self, parent)
        self.setText("&Monitor device ...")
        
    def actionTriggered(self):
        taurus_widget = self.parent()
        model_name = taurus_widget.getModelName()
        w = model_name.split("/")
        if len(w) == 3:
            dev_name = model_name
        elif len(w) == 4:
            dev_name = w[0] + "/" + w[1] + "/" + w[2]
        elif len(w) == 5:#FB: If the first parameter is the database
            dev_name = w[1] + "/" + w[2] + "/" + w[3]
        else:
            return
        
        cmd = "atkpanel " + dev_name + " &"
        os.system(cmd)
        
        
class AttributeImageDisplayAction(TaurusAction):
    
    menuID = "ImageDisplay"
    
    def __init__(self, parent=None):
        TaurusAction.__init__(self, parent)
        self.setText("&Image Display ...")
        
    def actionTriggered(self):
        taurus_widget = self.parent()
        model_name = taurus_widget.getModelName()
        w = model_name.split("/")
        if len(w) == 3:
            dev_name = model_name
        elif len(w) == 4:
            dev_name = w[0] + "/" + w[1] + "/" + w[2]
        else:
            return
        
        attr_name = dev_name + "/Image"
        
        import qub
        im = qub._TaurusQubDataImageDisplay(data=attr_name)
        im.show()
       

class AttributeMenu(TaurusMenu):
    
    menuID = "AttrMenu"
    menuData = "<Menu label='Attribute'>" \
    "<MenuItem class='AttrHistory'/>"\
    "<MenuItem class='_Separator_'/>"\
    "<Menu class='AttrConfig'/>"\
    "</Menu>"
    
    def __init__(self, parent):
        TaurusMenu.__init__(self, parent)
        self.build(self.menuData)
        
        
class ConfigurationMenu(TaurusMenu):
    menuID = "AttrConfigMenu"
    menuData = "<Menu label='Configuration'>" \
    "<MenuItem class='AttrConfig'/>"\
    "</Menu>"
    
    def __init__(self, parent):
        TaurusMenu.__init__(self, parent)
        self.build(self.menuData)
        
