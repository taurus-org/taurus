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
mainwindow.py: a main window implementation with many added features by default
"""

__all__ = ["TaurusMainWindow"]

__docformat__ = 'restructuredtext'

from PyQt4 import Qt

from taurusbasecontainer import TaurusBaseContainer

from taurus.qt.qtcore.configuration import BaseConfigurableClass
from taurus.qt.qtgui.util import ExternalAppAction
from taurus.qt.qtgui.resource import getIcon, getThemeIcon

import cPickle as pickle

class CommandArgsLineEdit(Qt.QLineEdit):
    ''' An specialized QLineEdit that can transform its text from/to command argument lists'''
    def __init__(self, *args):
        Qt.QLineEdit.__init__(self, *args)
    
    def setCmdText(self, cmdargs):
        if not isinstance(cmdargs, (basestring, Qt.QString)): 
            cmdargs = " ".join(cmdargs)
        self.setText(cmdargs)
    def getCmdArgs(self):
        import shlex
        return shlex.split(str(self.text()))
        

class ConfigurationDialog(Qt.QDialog, BaseConfigurableClass):
    ''' A Configuration Dialog'''
    def __init__(self, parent):
        Qt.QDialog.__init__(self, parent)
        BaseConfigurableClass.__init__(self)
        self._tabwidget = Qt.QTabWidget()
        self.setModal(True)
        self.externalAppsPage = None
        self.setLayout(Qt.QVBoxLayout())
        self.layout().addWidget(self._tabwidget) 
            
    
    def addExternalAppConfig(self, extapp):
        '''
        Creates an entry in the "External Apps" tab of the configuration dialog 
        
        :param extapp: (ExternalAppAction) the external application that is to
                       be included in the configuration menu.
        '''
        if self.externalAppsPage is None:
            self.externalAppsPage = Qt.QScrollArea()
            w = Qt.QWidget()
            w.setLayout(Qt.QFormLayout()) 
            self.externalAppsPage.setWidget(w)
            self.externalAppsPage.setWidgetResizable(True)
            self._tabwidget.addTab(self.externalAppsPage, "External Application Paths")
        label = "Command line for %s"%unicode(extapp.text())
        editWidget = CommandArgsLineEdit(" ".join(extapp.cmdArgs()))
        #editWidget = Qt.QLineEdit(" ".join(extapp.cmdArgs()))
        self.externalAppsPage.widget().layout().addRow(label, editWidget)
        self.connect(editWidget, Qt.SIGNAL("textEdited(QString)"), extapp.setCmdArgs)
        self.connect(extapp, Qt.SIGNAL("cmdArgsChanged"), editWidget.setCmdText)
        
    def show(self):
        ''' calls :meth:`Qt.QDialog.show` only if there is something to configure'''
        if self._tabwidget.count():
                Qt.QDialog.show(self)

        
class TaurusMainWindow(Qt.QMainWindow, TaurusBaseContainer):
    '''A Taurus-aware QMainWindow with several customizations:
    
        - It takes care of (re)storing its geometry and state
        - It provides a splashScreen (which can be disabled)
        - It provides a statusBar (@TODO)
        - It provides basic Taurus menus and actions:
            The following Menus are already Provided:
                - Help (self.helpMenu)
                - About
                - View (self.viewMenu)
                - Taurus (self.taurusMenu)
            The following actions are already provided:
                -Help-->About
        - It incorporates a TaurusLogo (@TODO)
    '''
    __pyqtSignals__ = ("modelChanged(const QString &)",)
        
    def __init__(self, parent = None, designMode = False, splash=True):
        name = self.__class__.__name__
        self.call__init__wo_kw(Qt.QMainWindow, parent)
        self.call__init__(TaurusBaseContainer, name, designMode=designMode)
        
        self.__splashScreen = None
        if splash and not designMode:      
            self.__splashScreen = Qt.QSplashScreen(Qt.QPixmap(":/logo.png"))
            self.__splashScreen.show()
            self.__splashScreen.showMessage("Initializing Main window...")
        
        self.__tangoHost = ""
        self.__settings = None
        
        self.extAppsBar = None
        
                
        #The configuration Dialog (which is launched with the configurationAction)
        self.configurationDialog = ConfigurationDialog(self)
        
        #create a few common Application-wide actions
        #Qt.QTimer.singleShot(0, self.__createActions())
        self.__createActions()
        
        #logger dock widget
        import taurus.qt.qtgui.table
        loggingWidget = taurus.qt.qtgui.table.QLoggingWidget()
        self.__loggerDW = Qt.QDockWidget("Taurus logs", self)
        self.__loggerDW.setWidget(loggingWidget)
        self.__loggerDW.setObjectName("loggerDW")
        self.addDockWidget(Qt.Qt.BottomDockWidgetArea, self.__loggerDW)
        self.__loggerDW.hide()
        
        #Create Menus
        #File menu
        self.fileMenu = self.menuBar().addMenu("File")
        self.fileMenu.addAction(self.quitApplicationAction)
        
        #View menu
        self.viewMenu = self.menuBar().addMenu("View")
        self.viewMenu.addAction(self.__loggerDW.toggleViewAction())
        self.viewToolBarsMenu = self.viewMenu.addMenu("Tool Bars")
        
        #Taurus Menu
        self.taurusMenu = self.menuBar().addMenu("Taurus")
        self.taurusMenu.addAction(self.changeTangoHostAction)
        
        #Tools Menu
        self.toolsMenu = self.menuBar().addMenu("Tools")
        self.externalAppsMenu = self.toolsMenu.addMenu("External Applications")
        self.toolsMenu.addAction(self.configurationAction)
        
        #Help Menu
        self.helpMenu = self.menuBar().addMenu("Help")
        self.helpMenu.addAction(self.helpAboutAction)
        
        #Perspectives Toolbar
        self.perspectivesMenu = Qt.QMenu("Load Perspectives")
        self.perspectivesToolBar = self.addToolBar("Perspectives")
        self.perspectivesToolBar.setObjectName("perspectivesToolBar")
        self.viewToolBarsMenu.addAction(self.perspectivesToolBar.toggleViewAction())
        pbutton = Qt.QToolButton()
        self.perspectivesMenu.setIcon(getThemeIcon("document-open"))
        pbutton.setToolTip("Load Perspectives")
        pbutton.setText("Load Perspectives")
        pbutton.setPopupMode(Qt.QToolButton.InstantPopup)
        pbutton.setMenu(self.perspectivesMenu)
        self.perspectivesToolBar.addWidget(pbutton)
        self.perspectivesToolBar.addAction(self.savePerspectiveAction)
        
        #disable the configuration action if there is nothing to configure
        self.configurationAction.setEnabled(self.configurationDialog._tabwidget.count())
        
    def updatePerspectivesMenu(self):
        '''re-checks the perspectives available to update self.perspectivesMenu
        
        .. note:: This method may need be called by derived classes at the end
                  of their initialization.
        
        :return: (QMenu) the updated perspectives menu
        '''
        self.perspectivesMenu.clear()
        for pname in self.getPerspectivesList():
            self.perspectivesMenu.addAction(pname, self.__onPerspectiveSelected)
        return self.perspectivesMenu
    
    def __onPerspectiveSelected(self):
        '''slot to be called by the actions in the perspectivesMenu'''
        pname = self.sender().text()
        self.loadPerspective(name=pname)
        
    def splashScreen(self):
        '''returns a the splashScreen
        
        :return: (QSplashScreen)
        '''
        return self.__splashScreen
        
    def basicTaurusToolbar(self):
        '''returns a QToolBar with few basic buttons (most important, the logo)
        
        :return: (QToolBar)
        '''
        tb = Qt.QToolBar('Taurus Toolbar')
        tb.setObjectName('Taurus Toolbar')
#        tb.addAction(self.changeTangoHostAction)
#        tb.addWidget(self.taurusLogo)
        tb.addAction(getIcon(":/logo.png"),Qt.qApp.organizationName())
        tb.setIconSize(Qt.QSize(50,50))
        return tb

    def __createActions(self):
        '''initializes the application-wide actions'''
        self.quitApplicationAction =  Qt.QAction(getThemeIcon("process-stop"),'Exit Application', self)
        self.connect(self.quitApplicationAction, Qt.SIGNAL("triggered()"), self.close)
        self.changeTangoHostAction =  Qt.QAction(getThemeIcon("network-server"),'Change Tango Host ...', self)
        self.changeTangoHostAction.setShortcut(Qt.QKeySequence("Ctrl+P"))
        self.connect(self.changeTangoHostAction, Qt.SIGNAL("triggered()"), self._onChangeTangoHostAction)
        
        self.loadPerspectiveAction = Qt.QAction(getThemeIcon("document-open"), 'Load Perspective ...', self)
        self.connect(self.loadPerspectiveAction, Qt.SIGNAL("triggered()"), self.loadPerspective)
        
        self.savePerspectiveAction = Qt.QAction(getThemeIcon("document-save"),'Save Perspective ...', self)
        self.connect(self.savePerspectiveAction, Qt.SIGNAL("triggered()"), self.savePerspective)
        
        self.configurationAction = Qt.QAction(getThemeIcon("preferences-system"), 'Configurations ...', self)
        self.connect(self.configurationAction, Qt.SIGNAL("triggered()"), self.configurationDialog.show)
        
        self.helpAboutAction = Qt.QAction('About ...', self)
        #self.helpUserManual = Qt.QAction('')
    
    
    def setQSettings(self, settings):
        '''sets the main window settings object
        
        :param settings: (QSettings or None)
        
        .. seealso:: :meth:`getQSettings`
        '''
        self.__settings = settings
        
    def resetQSettings(self):
        '''equivalent to setQSettings(None) '''
        self.setQSettings(None)
        
    def getQSettings(self):
        '''Returns the main window settings object.
        If it was not previously set, it will create a new QSettings object
        following the Taurus convention i.e., it using Ini format and userScope)
        
        :return: (QSettings) the main window QSettings object
        '''
        if self.__settings is None:
            self.__settings = self.newQSettings()
        return self.__settings 
    
    def newQSettings(self):
        '''Returns a settings taurus-specific QSettings object.
        The returned QSettings object will comply with the Taurus defaults for
        storing application settings (i.e., it uses Ini format and userScope)
        
        :return: (QSettings) a taurus-specific QSettings object
        '''
        #using the ALBA-Controls Coding Convention on how to store application settings
        format=Qt.QSettings.IniFormat
        scope = Qt.QSettings.UserScope
        appname = Qt.QApplication.applicationName()
        orgname = Qt.QApplication.organizationName()
        return Qt.QSettings(format, scope, orgname, appname)
        ##Note: for Qt v>=4.4, the five previous lines could have been substituted by the following two: 
        #self.__settings = Qt.QSettings() #this uses QCoreApplication.applicationName() and QCoreApplication.organizationName()
        #self.__settings.setDefaultFormat(Qt.QSettings.IniFormat)
            
    def loadSettings(self, settings=None, group=None, ignoreGeometry=False):
        '''restores the application settings previously saved with saveSettings.
        
        This method should be called explicitly from derived classes after all
        initialization is done
        
        :param settings: (QSettings or None) a QSettings object. If None given,
                         the default one returned by :meth:`getQSettings` will
                         be used
        :param group: (str) a prefix that will be added to the keys to be
                       loaded (no prefix by default)
        :param ignoreGeometry: (str) if True, the geometry of the MainWindow
                               won't be restored
        '''
        if settings is None: settings = self.getQSettings()
        #hide all current dockwidgets (so that they are shown only if they are present in the settings)
        dockwidgets = [c for c in self.children() if isinstance(c, Qt.QDockWidget)]
        for d in dockwidgets:
            d.hide()
        if group is not None: 
            settings.beginGroup(group)
        self.restoreState(settings.value("MainWindow/State").toByteArray())
        if not ignoreGeometry: 
            self.restoreGeometry(settings.value("MainWindow/Geometry").toByteArray()) 
        #restore the Taurus config
        try:
            self.applyQConfig(settings.value('TaurusConfig').toByteArray())
        except Exception,e:
            msg = 'Problem loading configuration from "%s". Some settings may not be restored.\n Details: %s'%(unicode(settings.fileName()), repr(e))
            self.error(msg)
            Qt.QMessageBox.warning(self,'Error Loading settings', msg, Qt.QMessageBox.Ok)
        if group is not None: 
            settings.endGroup()
        self.info('MainWindow settings restored')
        
    
    def saveSettings(self, group=None):
        '''saves the application settings (so that they can be restored with loadSettings)
        
        :param group: (str) a prefix that will be added to the keys to be
                       saved (no prefix by default)
        '''
        settings = self.getQSettings()
        if group is not None: 
            settings.beginGroup(group)
        #main window geometry
        settings.setValue("MainWindow/State",Qt.QVariant(self.saveState()))
        settings.setValue("MainWindow/Geometry", Qt.QVariant(self.saveGeometry()))
        
        #store the config dict
        settings.setValue("TaurusConfig", Qt.QVariant(self.createQConfig()))
        if group is not None: 
            settings.endGroup()
        self.info('MainWindow settings saved in "%s"'%settings.fileName())
        
        
    def savePerspective(self, name=None):
        '''Stores current state of the application as a perspective with the given name
        
        :param name: (str) name of the perspective
        '''
        perspectives = self.getPerspectivesList()
        if name is None:
            name,ok = Qt.QInputDialog.getItem(self, "Save Perspective", "Store current settings as the following perspective:",
                                              perspectives, 0, True) 
            if not ok: 
                return
        if name in perspectives:
            ans= Qt.QMessageBox.question(self, "Overwrite perspective?", "overwrite existing perspective %s?"%unicode(name),
                                         Qt.QMessageBox.Yes, Qt.QMessageBox.No)
            if ans != Qt.QMessageBox.Yes: 
                return
        self.saveSettings(group="Perspectives/%s"%name)
        self.updatePerspectivesMenu()
        
    def loadPerspective(self, name=None, settings=None):
        '''Loads the settings saved for the given perspective
                
        :param name: (str) name of the perspective            
        :param settings: (QSettings or None) a QSettings object. If None given,
                         the default one returned by :meth:`getQSettings` will
                         be used
        '''
        if name is None:
            perspectives = self.getPerspectivesList()
            if perspectives.isEmpty(): return
            name,ok = Qt.QInputDialog.getItem(self, "Load Perspective", "Change perspective to:",
                                              perspectives, 0, False) 
            if not ok: return
        self.loadSettings(settings=settings, group="Perspectives/%s"%name, ignoreGeometry=True)
    
    def getPerspectivesList(self, settings=None):
        '''Returns the list of saved perspectives 
        
        :param settings: (QSettings or None) a QSettings object. If None given,
                         the default one returned by :meth:`getQSettings` will
                         be used
        
        :return: (QStringList) the list of the names of the currently saved
                 perspectives
        '''
        if settings is None: settings = self.getQSettings()
        settings.beginGroup("Perspectives")
        names = settings.childGroups()
        settings.endGroup()
        return names

    def closeEvent(self,event):
        '''This event handler receives widget close events'''
        self.saveSettings() #save current window state before closing
        
        #print "\n\n------ MAIN WINDOW CLOSED ------ \n\n"
    
    def addExternalAppLauncher(self, extapp, toToolBar=True, toMenu=True):
        '''
        Adds launchers for an external application to the Tools Menu
        and/or to the Tools ToolBar.
        
        :param extapp: (ExternalAppAction or list<str>) the external application
                       to be launched passed as a :class:`ExternalAppAction`
                       (recommended because it allows to specify custom text and
                       icon) or, alternatively, as a list of strings (sys.argv-
                       like) that will be passed to :meth:`subprocess.Popen`.
        :param toToolBar: (bool) If True (default) a button will be added in the 
                          Tools toolBar
        :param toMenu: (bool) If True (default) an entry will be added in the 
                          Tools Menu, under the "External Applications" submenu
                          
        ..seealso:: :class:`ExternalAppAction`
        '''
        if not isinstance(extapp, ExternalAppAction):
            extapp = ExternalAppAction(extapp, parent = self)
        if extapp.parentWidget() is None: extapp.setParent(self)
        
        self.configurationDialog.addExternalAppConfig(extapp)
        self.configurationAction.setEnabled(True)
        
        if toToolBar:
            if self.extAppsBar is None:
                self.extAppsBar = self.addToolBar("External Applications")
                self.extAppsBar.setObjectName("External Applications")
                self.extAppsBar.setToolButtonStyle(Qt.Qt.ToolButtonTextBesideIcon)
                self.viewToolBarsMenu.addAction(self.extAppsBar.toggleViewAction())
            self.extAppsBar.addAction(extapp)
            
        if toMenu:
            if self.toolsMenu is None:
                self.toolsMenu = Qt.QMenu("Tools")
                self.menuBar().insertMenu(self.helpMenu.menuAction(), self.toolsMenu) #insert it before the Help menu
            if self.externalAppsMenu is None:
                self.externalAppsMenu = self.toolsMenu.addMenu("External Applications")
            self.externalAppsMenu.addAction(extapp)
        #register this action for config
        self.registerConfigDelegate(extapp, "_extApp[%s]"%str(extapp.text()))
        
    def _onChangeTangoHostAction(self):
        '''
        slot called when the Change Tango Host is triggered. It prompts for a
        Tango host name and calls :meth:`setTangoHost`
        '''
        host, valid = Qt.QInputDialog.getText  ( self, 'Change Tango Host', 'New Tango Host', Qt.QLineEdit.Normal,  str(self.getTangoHost()))
        if valid:
            self.setTangoHost(str(host))
            
    def setTangoHost(self, host):
        self.__tangoHost = host
        
    def getTangoHost(self):
        return self.__tangoHost
    
    def resetTangoHost(self):
        self.setTangoHost(None)
        
    @classmethod
    def getQtDesignerPluginInfo(cls):
        # Current versions of designer don't work with MainWindow as custom
        # widgets. Therefore until this is solved, the widget will not appear
        # in the designer
        return None
        
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # Public slots for apply/restore changes
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    @Qt.pyqtSignature("applyPendingChanges()")
    def applyPendingChanges(self):
        self.applyPendingOperations()
    
    @Qt.pyqtSignature("resetPendingChanges()")
    def resetPendingChanges(self):
        self.resetPendingOperations()
        
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # QT properties 
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
   
    model = Qt.pyqtProperty("QString", TaurusBaseContainer.getModel, 
                                TaurusBaseContainer.setModel, 
                                TaurusBaseContainer.resetModel)
    
    useParentModel = Qt.pyqtProperty("bool", 
                                         TaurusBaseContainer.getUseParentModel, 
                                         TaurusBaseContainer.setUseParentModel,
                                         TaurusBaseContainer.resetUseParentModel)
    
    showQuality = Qt.pyqtProperty("bool", TaurusBaseContainer.getShowQuality, 
                                      TaurusBaseContainer.setShowQuality, 
                                      TaurusBaseContainer.resetShowQuality)
    
    tangoHost = Qt.pyqtProperty("QString", getTangoHost, 
                                        setTangoHost, 
                                        resetTangoHost)

#---------

if __name__ == "__main__":
    
    import sys
    app = Qt.QApplication(sys.argv)
    app.setApplicationName('TaurusMainWindow-test')
    app.setOrganizationName('ALBA')
    
    form = TaurusMainWindow()
    form.loadSettings()
    
    form.setCentralWidget(Qt.QMdiArea()) #just for testing
    
#    form.addExternalAppLauncher('pwd')
    
    form.show()
    
    form.splashScreen().finish(form)
    sys.exit(app.exec_())
    
