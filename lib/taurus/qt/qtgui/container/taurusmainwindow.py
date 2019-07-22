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

"""
mainwindow.py: a main window implementation with many added features by default
"""

from __future__ import absolute_import

from builtins import str

import os
import sys

from functools import partial

from future.utils import string_types

from taurus import tauruscustomsettings
from taurus.core.util import deprecation_decorator
from taurus.external.qt import Qt, compat
from .taurusbasecontainer import TaurusBaseContainer

from taurus.qt.qtcore.configuration import BaseConfigurableClass
from taurus.qt.qtgui.util import ExternalAppAction
from taurus.qt.qtgui.dialog import protectTaurusMessageBox


__all__ = ["TaurusMainWindow"]

__docformat__ = 'restructuredtext'


class CommandArgsLineEdit(Qt.QLineEdit):
    ''' An specialized QLineEdit that can transform its text from/to command argument lists'''

    def __init__(self, extapp, *args):
        Qt.QLineEdit.__init__(self, *args)
        self._extapp = extapp
        self.textEdited.connect(self.setCmdText)

    def setCmdText(self, cmdargs):
        if not isinstance(cmdargs, string_types):
            cmdargs = " ".join(cmdargs)
        self.setText(cmdargs)
        self._extapp.setCmdArgs(self.getCmdArgs(), False)

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
            self._tabwidget.addTab(self.externalAppsPage,
                                   "External Application Paths")
        label = "Command line for %s" % str(extapp.text())
        editWidget = CommandArgsLineEdit(extapp, " ".join(extapp.cmdArgs()))
        #editWidget = Qt.QLineEdit(" ".join(extapp.cmdArgs()))
        self.externalAppsPage.widget().layout().addRow(label, editWidget)
        extapp.cmdArgsChanged.connect(editWidget.setCmdText)

    def deleteExternalAppConfig(self, extapp):
        '''Remove the given external application configuration from
        the "External Apps" tab of the configuration dialog

        :param extapp: (ExternalAppAction) the external application that is to
                       be included in the configuration menu.
        '''
        from taurus.external.qt import Qt
        layout = self.externalAppsPage.widget().layout()
        for cnt in reversed(range(layout.count())):
            widget = layout.itemAt(cnt).widget()
            if widget is not None:
                text = str(widget.text())  # command1
                if isinstance(widget, Qt.QLabel):
                    dialog_text = "Command line for %s" % str(extapp.text())
                    if text == dialog_text:
                        layout.removeWidget(widget)
                        widget.close()
                else:
                    cmdargs = " ".join(extapp.cmdArgs())
                    if text == cmdargs:
                        layout.removeWidget(widget)
                        widget.close()

    def show(self):
        ''' calls :meth:`Qt.QDialog.show` only if there is something to configure'''
        if self._tabwidget.count():
            Qt.QDialog.show(self)


class Rpdb2Thread(Qt.QThread):

    def run(self):
        dialog = Rpdb2WaitDialog(parent=self.parent())
        dialog.exec_()


class Rpdb2WaitDialog(Qt.QMessageBox):

    def __init__(self, title=None, text=None, parent=None):
        if text is None:
            text = "Waitting for a debugger console to attach..."
        if title is None:
            title = "Rpdb2 waitting..."
        Qt.QMessageBox.__init__(self)
        self.addButton(Qt.QMessageBox.Ok)
        self.setWindowTitle(title)
        self.setText(text)
        self.button(Qt.QMessageBox.Ok).setEnabled(False)

        parent.rpdb2Started.connect(self.onStarted)

    def onStarted(self):
        self.setWindowTitle("Rpdb2 running!")
        self.setText("A rpdb2 debugger was started successfully!")
        self.button(Qt.QMessageBox.Ok).setEnabled(True)


class TaurusMainWindow(Qt.QMainWindow, TaurusBaseContainer):
    '''
    A Taurus-aware QMainWindow with several customizations:

        - It takes care of (re)storing its geometry and state (see :meth:`loadSettings`)
        - Supports perspectives (programmatic access and, optionally,
          accessible by user), and allows defining a set of "factory settings"
        - It provides a customizable splashScreen (optional)
        - Supports spawning remote consoles and remote debugging
        - Supports full-screen mode toggling
        - Supports adding launchers to external applications
        - It provides a statusBar with an optional heart-beat LED
        - The following Menus are optionally provided and populated with basic actions:
            - File  (accessible by derived classes  as `self.fileMenu`)
            - View (accessible by derived classes  as `self.viewMenu`)
            - Taurus (accessible by derived classes  as `self.taurusMenu`)
            - Tools (accessible by derived classes  as `self.toolsMenu`)
            - Help (accessible by derived classes  as `self.helpMenu`)

    '''
    modelChanged = Qt.pyqtSignal('const QString &')
    perspectiveChanged = Qt.pyqtSignal('QString')

    # customization options:
    #: Heartbeat LED blinking semi-period in ms. Set to None for not showing it
    HEARTBEAT = 1500
    #: Whether to show the File menu
    FILE_MENU_ENABLED = True
    #: Whether to show the View menu
    VIEW_MENU_ENABLED = True
    #: Whether to show the Taurus menu
    TAURUS_MENU_ENABLED = True
    #: Whether to show the Tools menu
    TOOLS_MENU_ENABLED = True
    #: Whether to show the Help menu
    HELP_MENU_ENABLED = True
    #: Whether to show the Full Screen Toolbar
    FULLSCREEN_TOOLBAR_ENABLED = True
    #: Whether to show actions for user perspectives
    USER_PERSPECTIVES_ENABLED = True
    #: Whether add a dockwidget with the logger widget
    LOGGER_WIDGET_ENABLED = True
    #: Name of logo image for splash screen. Set to None for disabling splash
    SPLASH_LOGO_NAME = "large:TaurusSplash.png"
    #: Message for splash screen
    SPLASH_MESSAGE = "Initializing Main window..."

    _old_options_api = {
        '_heartbeat': 'HEARTBEAT',
        '_showFileMenu': 'FILE_MENU_ENABLED',
        '_showViewMenu': 'VIEW_MENU_ENABLED',
        '_showTaurusMenu': 'TAURUS_MENU_ENABLED',
        '_showToolsMenu': 'TOOLS_MENU_ENABLED',
        '_showHelpMenu': 'HELP_MENU_ENABLED',
        '_showLogger': 'LOGGER_WIDGET_ENABLED',
        '_supportUserPerspectives': 'USER_PERSPECTIVES_ENABLED',
        '_splashLogo': 'SPLASH_LOGO_NAME',
        '_splashMessage': 'SPLASH_MESSAGE',
    }

    def __init__(self, parent=None, designMode=False, splash=None):
        name = self.__class__.__name__
        self.call__init__wo_kw(Qt.QMainWindow, parent)
        self.call__init__(TaurusBaseContainer, name, designMode=designMode)

        # Provide bck-compat with old options API
        for old, new in self._old_options_api.items():
            if hasattr(self, old):
                self.deprecated(dep=old, alt=new, rel='4.5.3a')
                setattr(self, new, getattr(self, old))

        if splash is None:
            splash = bool(self.SPLASH_LOGO_NAME)

        self.__splashScreen = None
        if splash and not designMode:
            self.__splashScreen = Qt.QSplashScreen(
                Qt.QPixmap(self.SPLASH_LOGO_NAME))
            self.__splashScreen.show()
            self.__splashScreen.showMessage(self.SPLASH_MESSAGE)

        self.__tangoHost = ""
        self.__settings = None

        self.extAppsBar = None

        self.helpManualDW = None
        self.helpManualBrowser = None

        if self.HELP_MENU_ENABLED:
            self.resetHelpManualURI()

        # Heartbeat
        if self.HEARTBEAT is not None:
            from taurus.qt.qtgui.display import QLed
            self.heartbeatLed = QLed()
            self.heartbeatLed.setToolTip(
                'Heartbeat: if it does not blink, the application is hung')
            self.statusBar().addPermanentWidget(self.heartbeatLed)
            self.resetHeartbeat()

        # The configuration Dialog (which is launched with the
        # configurationAction)
        self.configurationDialog = ConfigurationDialog(self)

        # create a few common Application-wide actions
        #Qt.QTimer.singleShot(0, self.__createActions())
        self.__createActions()

        # logger dock widget
        if self.LOGGER_WIDGET_ENABLED:
            self.addLoggerWidget()

        # Create Menus
        if self.FILE_MENU_ENABLED:  # File menu
            self.createFileMenu()
        if self.VIEW_MENU_ENABLED:  # View menu
            self.createViewMenu()
        if self.TAURUS_MENU_ENABLED:  # Taurus Menu
            self.createTaurusMenu()
        if self.TOOLS_MENU_ENABLED:  # Tools Menu
            self.createToolsMenu()
        if self.HELP_MENU_ENABLED:  # Help Menu
            self.createHelpMenu()

        # View Toolbar
        if self.FULLSCREEN_TOOLBAR_ENABLED:
            self.viewToolBar = self.addToolBar("View")
            self.viewToolBar.setObjectName("viewToolBar")
            self.viewToolBar.addAction(self.toggleFullScreenAction)

        # Perspectives Toolbar
        if self.USER_PERSPECTIVES_ENABLED:
            self.createPerspectivesToolBar()

        # disable the configuration action if there is nothing to configure
        self.configurationAction.setEnabled(
            self.configurationDialog._tabwidget.count())

    def __setattr__(self, key, value):
        super(TaurusMainWindow, self).__setattr__(key, value)
        if key in self._old_options_api:
            new = self._old_options_api[key]
            setattr(self, new, value)
            self.deprecated(dep=key, alt=new, rel='4.5.3a')

    def contextMenuEvent(self, event):
        """Reimplemented to avoid deprecation warning related to:
        https://github.com/taurus-org/taurus/issues/905
        """
        # TODO: Remove this once the deprecation of the Popup menu is enforced
        event.ignore()

    def addLoggerWidget(self, hidden=True):
        '''adds a QLoggingWidget as a dockwidget of the main window (and hides it by default)'''
        from taurus.qt.qtgui.table import QLoggingWidget
        loggingWidget = QLoggingWidget()
        self.__loggerDW = Qt.QDockWidget("Taurus logs", self)
        self.__loggerDW.setWidget(loggingWidget)
        self.__loggerDW.setObjectName("loggerDW")
        self.addDockWidget(Qt.Qt.BottomDockWidgetArea, self.__loggerDW)
        if hidden:
            self.__loggerDW.hide()

    def createFileMenu(self):
        '''adds a "File" Menu'''
        self.fileMenu = self.menuBar().addMenu("File")
        if self.USER_PERSPECTIVES_ENABLED:
            self.fileMenu.addAction(self.importSettingsFileAction)
            self.fileMenu.addAction(self.exportSettingsFileAction)
            # self.fileMenu.addAction(self.resetSettingsAction)
            self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.quitApplicationAction)

    def createViewMenu(self):
        '''adds a "View" Menu'''
        self.viewMenu = self.menuBar().addMenu("View")
        if self.LOGGER_WIDGET_ENABLED:
            self.viewMenu.addAction(self.__loggerDW.toggleViewAction())
        self.viewToolBarsMenu = self.viewMenu.addMenu("Tool Bars")
        self.viewMenu.addSeparator()
        self.viewMenu.addAction(self.toggleFullScreenAction)
        if self.USER_PERSPECTIVES_ENABLED:
            self.viewMenu.addSeparator()
            self.perspectivesMenu = Qt.QMenu("Load Perspectives", self)
            self.viewMenu.addMenu(self.perspectivesMenu)
            self.viewMenu.addAction(self.savePerspectiveAction)
            self.viewMenu.addAction(self.deletePerspectiveAction)

    def createTaurusMenu(self):
        '''adds a "Taurus" Menu'''
        self.taurusMenu = self.menuBar().addMenu("Taurus")
        self.taurusMenu.addAction(self.changeTangoHostAction)

    def createToolsMenu(self):
        '''adds a "Tools" Menu'''
        self.toolsMenu = self.menuBar().addMenu("Tools")
        self.externalAppsMenu = self.toolsMenu.addMenu("External Applications")
        self.toolsMenu.addAction(self.configurationAction)

    def createHelpMenu(self):
        '''adds a "Help" Menu'''
        self.helpMenu = self.menuBar().addMenu("Help")
        self.helpMenu.addAction("About ...", self.showHelpAbout)
        self.helpMenu.addAction(Qt.QIcon.fromTheme(
            "help-browser"), "Manual", self.onShowManual)

    def createPerspectivesToolBar(self):
        '''adds a Perspectives ToolBar'''
        self.perspectivesToolBar = self.addToolBar("Perspectives")
        self.perspectivesToolBar.setObjectName("perspectivesToolBar")
        pbutton = Qt.QToolButton()
        # it may have been created earlier (for the view menu)
        if not hasattr(self, 'perspectivesMenu'):
            self.perspectivesMenu = Qt.QMenu("Load Perspectives", self)
        self.perspectivesMenu.setIcon(Qt.QIcon.fromTheme("document-open"))
        pbutton.setToolTip("Load Perspectives")
        pbutton.setText("Load Perspectives")
        pbutton.setPopupMode(Qt.QToolButton.InstantPopup)
        pbutton.setMenu(self.perspectivesMenu)
        self.perspectivesToolBar.addWidget(pbutton)
        self.perspectivesToolBar.addAction(self.savePerspectiveAction)
        if self.VIEW_MENU_ENABLED:
            self.viewToolBarsMenu.addAction(
                self.perspectivesToolBar.toggleViewAction())

    def updatePerspectivesMenu(self):
        '''re-checks the perspectives available to update self.perspectivesMenu

        .. note:: This method may need be called by derived classes at the end
                  of their initialization.

        :return: (QMenu) the updated perspectives menu (or None if
                 self.USER_PERSPECTIVES_ENABLED is False)
        '''
        if not self.USER_PERSPECTIVES_ENABLED:
            return None
        self.perspectivesMenu.clear()
        for pname in self.getPerspectivesList():
            a = self.perspectivesMenu.addAction(
                pname, self.__onPerspectiveSelected)
            # -------------------------------------------------------
            # Work around for https://bugs.kde.org/show_bug.cgi?id=345023
            # TODO: make better solution for this
            a.perspective_name = pname  # <-- ugly monkey-patch!
            # -------------------------------------------------------
        return self.perspectivesMenu

    def __onPerspectiveSelected(self):
        '''slot to be called by the actions in the perspectivesMenu'''
        # -------------------------------------------------------
        # Work around for https://bugs.kde.org/show_bug.cgi?id=345023
        # TODO: make better solution for this
        # pname = self.sender().text()  # <-- this fails because of added "&"
        pname = self.sender().perspective_name  # <-- this was monkey-patched
        # -------------------------------------------------------
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
        logo = getattr(tauruscustomsettings, 'ORGANIZATION_LOGO',
                       "logos:taurus.png")
        tb.addAction(Qt.QIcon(logo), Qt.qApp.organizationName())
        tb.setIconSize(Qt.QSize(50, 50))
        return tb

    def __createActions(self):
        '''initializes the application-wide actions'''
        self.quitApplicationAction = Qt.QAction(
            Qt.QIcon.fromTheme("process-stop"), 'Exit Application', self)
        self.quitApplicationAction.triggered.connect(self.close)
        self.changeTangoHostAction = Qt.QAction(Qt.QIcon.fromTheme(
            "network-server"), 'Change Tango Host ...', self)
        self.changeTangoHostAction.triggered.connect(self._onChangeTangoHostAction)
        # make this action invisible since it is deprecated
        self.changeTangoHostAction.setVisible(False)

        self.loadPerspectiveAction = Qt.QAction(Qt.QIcon.fromTheme(
            "document-open"), 'Load Perspective ...', self)
        self.loadPerspectiveAction.triggered.connect(
            partial(self.loadPerspective, name=None, settings=None))

        self.savePerspectiveAction = Qt.QAction(Qt.QIcon.fromTheme(
            "document-save"), 'Save Perspective ...', self)
        self.savePerspectiveAction.triggered.connect(
            partial(self.savePerspective, name=None))

        self.deletePerspectiveAction = Qt.QAction(
            Qt.QIcon("actions:edit-delete.svg"), 'Delete Perspective ...', self)
        self.deletePerspectiveAction.triggered.connect(
            partial(self.removePerspective, name=None, settings=None))

        self.exportSettingsFileAction = Qt.QAction(
            Qt.QIcon.fromTheme("document-save"), 'Export Settings ...', self)
        self.exportSettingsFileAction.triggered.connect(
            partial(self.exportSettingsFile, fname=None))

        self.importSettingsFileAction = Qt.QAction(
            Qt.QIcon.fromTheme("document-open"), 'Import Settings ...', self)
        self.importSettingsFileAction.triggered.connect(
            partial(self.importSettingsFile, fname=None))

        #self.resetSettingsAction = Qt.QAction(Qt.QIcon.fromTheme("edit-undo"),'Reset Settings', self)
        #self.connect(self.resetSettingsAction, Qt.SIGNAL("triggered()"), self.resetSettings)

        self.configurationAction = Qt.QAction(Qt.QIcon.fromTheme(
            "preferences-system"), 'Configurations ...', self)
        self.configurationAction.triggered.connect(
            self.configurationDialog.show)

        #self.rpdb2Action = Qt.QAction("Spawn rpdb2", self)
        self.spawnRpdb2Shortcut = Qt.QShortcut(self)
        self.spawnRpdb2Shortcut.setKey(Qt.QKeySequence(Qt.Qt.Key_F9))
        self.spawnRpdb2Shortcut.activated.connect(self._onSpawnRpdb2)

        #self.rpdb2Action = Qt.QAction("Spawn rpdb2", self)
        self.spawnRpdb2Shortcut = Qt.QShortcut(self)
        rpdb2key = Qt.QKeySequence(
            Qt.Qt.CTRL + Qt.Qt.ALT + Qt.Qt.Key_0, Qt.Qt.Key_1)
        self.spawnRpdb2Shortcut.setKey(rpdb2key)
        self.spawnRpdb2Shortcut.activated.connect(self._onSpawnRpdb2)

        self.spawnRConsoleShortcut = Qt.QShortcut(self)
        rconsolekey = Qt.QKeySequence(
            Qt.Qt.CTRL + Qt.Qt.ALT + Qt.Qt.Key_0, Qt.Qt.Key_2)
        self.spawnRConsoleShortcut.setKey(rconsolekey)
        self.spawnRConsoleShortcut.activated.connect(self._onSpawnRConsole)

        self.toggleFullScreenAction = Qt.QAction(
            Qt.QIcon("actions:view-fullscreen.svg"), 'Show FullScreen', self)
        self.toggleFullScreenAction.setCheckable(True)
        self.toggleFullScreenAction.toggled.connect(self._onToggleFullScreen)

        # In Qt <= 4.4 setting the QAction shortcut at the application level
        # doesn't work when trying to get out of fullscreen so we create a
        # QShortcut manually to solve the problem.
        # self.toggleFullScreenAction.setShortcut(Qt.QKeySequence(Qt.Qt.Key_F11))
        # self.toggleFullScreenAction.setShortcutContext(Qt.Qt.ApplicationShortcut)
        self.fullScreenShortcut = Qt.QShortcut(self)
        self.fullScreenShortcut.setKey(Qt.QKeySequence(Qt.Qt.Key_F11))
        self.fullScreenShortcut.activated.connect(self._onToggleFullScreen)

    @protectTaurusMessageBox
    def _onSpawnRpdb2(self):
        try:
            import rpdb2
        except ImportError:
            Qt.QMessageBox.warning(self, "Rpdb2 not installed",
                                   "Cannot spawn debugger: Rpdb2 is not "
                                   "installed on your system.")
            return
        if hasattr(self, "_rpdb2"):
            Qt.QMessageBox.information(self, "Rpdb2 running",
                                       "A rpdb2 debugger is already started")
            return

        pwd, ok = Qt.QInputDialog.getText(self, "Rpdb2 password", "Password:",
                                          Qt.QLineEdit.Password)
        if not ok:
            return

        Qt.QMessageBox.warning(self, "Rpdb2 freeze",
                               "The application will freeze until a "
                               "debugger attaches.")

        self._rpdb2 = rpdb2.start_embedded_debugger(str(pwd))

        Qt.QMessageBox.information(self, "Rpdb2 running",
                                   "rpdb2 debugger started successfully!")

    @protectTaurusMessageBox
    def _onSpawnRConsole(self):
        try:
            import rfoo.utils.rconsole
        except ImportError:
            Qt.QMessageBox.warning(self, "rfoo not installed",
                                   "Cannot spawn debugger: rfoo is not "
                                   "installed on your system.")
            return

        if hasattr(self, "_rconsole_port"):
            Qt.QMessageBox.information(self, "rconsole running",
                                       "A rconsole is already running on "
                                       "port %d" % self._rconsole_port)
            return

        port, ok = Qt.QInputDialog.getInteger(self, "rconsole port", "Port:",
                                              rfoo.utils.rconsole.PORT,
                                              0, 65535)
        if not ok:
            return

        rfoo.utils.rconsole.spawn_server(port=port)
        self._rconsole_port = port
        Qt.QMessageBox.information(self, "Rpdb2 running",
                                   "<html>rconsole started successfully!<br>"
                                   "Type:<p>"
                                   "<b>rconsole -p %d</b></p>"
                                   "to connect to it" % port)

    # I put the yesno=None keyword arg so it may be called by both toggled(bool)
    # activated() Qt signals. There is no problem as long as we don't use the
    # parameter internally in the method
    def _onToggleFullScreen(self, yesno=None):
        if self.isFullScreen():
            self.showNormal()
            self._toggleToolBarsAndMenu(True)
        else:
            self._toggleToolBarsAndMenu(False)
            self.showFullScreen()

    def _toggleToolBarsAndMenu(self, visible, toolBarAreas=Qt.Qt.TopToolBarArea):
        for toolbar in self.findChildren(Qt.QToolBar):
            if bool(self.toolBarArea(toolbar) & toolBarAreas):
                toolbar.setVisible(visible)

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
        # using the ALBA-Controls Coding Convention on how to store application
        # settings
        format = Qt.QSettings.IniFormat
        scope = Qt.QSettings.UserScope
        appname = Qt.QApplication.applicationName()
        orgname = Qt.QApplication.organizationName()
        return Qt.QSettings(format, scope, orgname, appname)
        # Note: for Qt v>=4.4, the five previous lines could have been substituted by the following two:
        # self.__settings = Qt.QSettings() #this uses QCoreApplication.applicationName() and QCoreApplication.organizationName()
        # self.__settings.setDefaultFormat(Qt.QSettings.IniFormat)

    def getFactorySettingsFileName(self):
        '''returns the file name of the "factory settings" (the ini file with default settings).
        The default implementation returns "<path>/<appname>.ini", where <path>
        is the path of the module where the main window class is defined and
        <appname> is the application name (as obtained from QApplication).

        :return: (str) the absolute file name.
        '''
        root, tail = os.path.split(os.path.abspath(
            sys.modules[self.__module__].__file__))
        basename = "%s.ini" % str(Qt.qApp.applicationName())
        return os.path.join(root, basename)

    def loadSettings(self, settings=None, group=None, ignoreGeometry=False, factorySettingsFileName=None):
        '''restores the application settings previously saved with :meth:`saveSettings`.

        .. note:: This method should be called explicitly from derived classes after all
                  initialization is done

        :param settings: (QSettings or None) a QSettings object. If None given,
                         the default one returned by :meth:`getQSettings` will
                         be used
        :param group: (str) a prefix that will be added to the keys to be
                       loaded (no prefix by default)
        :param ignoreGeometry: (bool) if True, the geometry of the MainWindow
                               won't be restored
        :param factorySettingsFileName: (str) file name of a ini file containing the default
                                        settings to be used as a fallback in
                                        case the settings file is not found
                                        (e.g., the first time the application is
                                        launched after installation)
        '''
        if settings is None:
            settings = self.getQSettings()
            if len(settings.allKeys()) == 0:
                fname = factorySettingsFileName or self.getFactorySettingsFileName()
                if os.path.exists(fname):
                    self.info('Importing factory settings from "%s"' % fname)
                    self.importSettingsFile(fname)
                return

        if group is not None:
            settings.beginGroup(group)
        if not ignoreGeometry:
            ba = settings.value("MainWindow/Geometry") or Qt.QByteArray()
            self.restoreGeometry(ba)
        # restore the Taurus config
        try:
            ba = settings.value("TaurusConfig") or Qt.QByteArray()
            self.applyQConfig(ba)
        except Exception as e:
            msg = ('Problem loading configuration from "{}". '
                   + 'Some settings may not be restored.\n'
                   + ' Reason: {}'
                   ).format(str(settings.fileName()), e)
            self.error(msg)
            Qt.QMessageBox.warning(
                self, 'Error Loading settings', msg, Qt.QMessageBox.Ok)
        ba = settings.value("MainWindow/State") or Qt.QByteArray()
        self.restoreState(ba)
        # hide all dockwidgets (so that they are shown only if they were
        # present in the settings)
        dockwidgets = [c for c in self.children(
        ) if isinstance(c, Qt.QDockWidget)]
        for d in dockwidgets:
            r = self.restoreDockWidget(d)
            d.hide()
        ba = settings.value("MainWindow/State") or Qt.QByteArray()
        self.restoreState(ba)

        if group is not None:
            settings.endGroup()
        self.updatePerspectivesMenu()
        self.info('MainWindow settings restored')

    def saveSettings(self, group=None):
        '''saves the application settings (so that they can be restored with :meth:`loadSettings`)

        .. note:: this method is automatically called by default when closing the
                  window, so in general there is no need to call it from derived classes

        :param group: (str) a prefix that will be added to the keys to be
                       saved (no prefix by default)
        '''
        settings = self.getQSettings()
        if not settings.isWritable():
            self.info('Settings cannot be saved in "%s"', settings.fileName())
            return

        if group is not None:
            settings.beginGroup(group)
        # main window geometry
        settings.setValue("MainWindow/State", self.saveState())
        settings.setValue("MainWindow/Geometry", self.saveGeometry())

        # store the config dict
        settings.setValue("TaurusConfig", self.createQConfig())
        if group is not None:
            settings.endGroup()
        self.info('Settings saved in "%s"' % settings.fileName())

    @Qt.pyqtSlot()
    @Qt.pyqtSlot('QString')
    def savePerspective(self, name=None):
        '''Stores current state of the application as a perspective with the given name

        :param name: (str) name of the perspective
        '''
        perspectives = self.getPerspectivesList()
        if name is None:
            name, ok = Qt.QInputDialog.getItem(
                self, "Save Perspective",
                "Store current settings as the following perspective:",
                perspectives, 0, True
            )
            if not ok:
                return
        if name in perspectives:
            ans = Qt.QMessageBox.question(
                self, "Overwrite perspective?",
                "overwrite existing perspective %s?" % str(name),
                Qt.QMessageBox.Yes, Qt.QMessageBox.No
            )
            if ans != Qt.QMessageBox.Yes:
                return
        self.saveSettings(group="Perspectives/%s" % name)
        self.updatePerspectivesMenu()

    @Qt.pyqtSlot()
    @Qt.pyqtSlot('QString')
    def loadPerspective(self, name=None, settings=None):
        '''Loads the settings saved for the given perspective.
        It emits a 'perspectiveChanged' signal with name as its parameter

        :param name: (str) name of the perspective
        :param settings: (QSettings or None) a QSettings object. If None given,
                         the default one returned by :meth:`getQSettings` will
                         be used
        '''
        if name is None:
            perspectives = self.getPerspectivesList()
            if len(perspectives) == 0:
                return
            name, ok = Qt.QInputDialog.getItem(self, "Load Perspective", "Change perspective to:",
                                               perspectives, 0, False)
            if not ok:
                return
        self.loadSettings(settings=settings,
                          group="Perspectives/%s" % name, ignoreGeometry=True)
        self.perspectiveChanged.emit(name)

    def getPerspectivesList(self, settings=None):
        '''Returns the list of saved perspectives

        :param settings: (QSettings or None) a QSettings object. If None given,
                         the default one returned by :meth:`getQSettings` will
                         be used

        :return: (QStringList) the list of the names of the currently saved
                 perspectives
        '''
        if settings is None:
            settings = self.getQSettings()
        settings.beginGroup("Perspectives")
        names = settings.childGroups()
        settings.endGroup()
        return names

    @Qt.pyqtSlot()
    @Qt.pyqtSlot('QString')
    def removePerspective(self, name=None, settings=None):
        '''removes the given perspective from the settings

        :param name: (str) name of the perspective
        :param settings: (QSettings or None) a QSettings object. If None given,
                         the default one returned by :meth:`getQSettings` will
                         be used
        '''
        if settings is None:
            settings = self.getQSettings()
        if name is None:
            perspectives = self.getPerspectivesList()
            if len(perspectives) == 0:
                return
            name, ok = Qt.QInputDialog.getItem(self, "Delete Perspective", "Choose perspective to be deleted:",
                                               perspectives, 0, False)
            if not ok:
                return
        if name not in perspectives:
            self.warning(
                "Cannot remove perspective %s (not found)" % str(name))
            return
        settings.beginGroup("Perspectives")
        settings.remove(name)
        settings.endGroup()
        self.updatePerspectivesMenu()

    @Qt.pyqtSlot()
    @Qt.pyqtSlot('QString')
    def exportSettingsFile(self, fname=None):
        '''copies the current settings file into the given file name.

        :param fname: (str) name of output file. If None given, a file dialog will be shown.
        '''
        if fname is None:
            fname, _ = compat.getSaveFileName(
                self, 'Choose file where the current settings should be saved',
                '', "Ini files (*.ini);;All files (*)"
            )
            if not fname:
                return
        self.saveSettings()
        ok = Qt.QFile.copy(self.getQSettings().fileName(), fname)
        if ok:
            self.info('MainWindow settings saved in "%s"' % str(fname))
        else:
            msg = 'Settings could not be exported to %s' % str(fname)
            Qt.QMessageBox.warning(self, 'Export error', msg)

    @Qt.pyqtSlot()
    @Qt.pyqtSlot('QString')
    def importSettingsFile(self, fname=None):
        '''
        loads settings (including importing all perspectives) from a given ini
        file. It warns before overwriting an existing perspective.

        :param fname: (str) name of ini file. If None given, a file dialog will be shown.
        '''
        if fname is None:
            fname, _ = compat.getOpenFileName(
                self, 'Select a ini-format settings file',
                '', "Ini files (*.ini);;All files (*)"
            )
            if not fname:
                return
        s = Qt.QSettings(fname, Qt.QSettings.IniFormat)
        # clone the perspectives found in the "factory" settings
        for p in self.getPerspectivesList(settings=s):
            self.loadPerspective(name=p, settings=s)
            self.savePerspective(name=p)
        # finally load the settings
        self.loadSettings(settings=s)

#    def resetSettings(self):
#        '''deletes current settings file and clears all settings'''
#        self.__settings = self.newQSettings()
#        self.saveSettings()

    def showEvent(self, event):
        '''This event handler receives widget show events'''
        if self.__splashScreen is not None and not event.spontaneous():
            self.__splashScreen.finish(self)

    def closeEvent(self, event):
        '''This event handler receives widget close events'''
        self.saveSettings()  # save current window state before closing
        if hasattr(self, "socketServer"):
            self.socketServer.close()
        Qt.QMainWindow.closeEvent(self, event)
        TaurusBaseContainer.closeEvent(self, event)

        # print "\n\n------ MAIN WINDOW CLOSED ------ \n\n"

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

        .. seealso:: :class:`ExternalAppAction`
        '''
        if not isinstance(extapp, ExternalAppAction):
            extapp = ExternalAppAction(extapp, parent=self)
        if extapp.parentWidget() is None:
            extapp.setParent(self)

        self.configurationDialog.addExternalAppConfig(extapp)
        self.configurationAction.setEnabled(True)

        if toToolBar:
            if self.extAppsBar is None:
                self.extAppsBar = self.addToolBar("External Applications")
                self.extAppsBar.setObjectName("External Applications")
                self.extAppsBar.setToolButtonStyle(
                    Qt.Qt.ToolButtonTextBesideIcon)
                if self.VIEW_MENU_ENABLED:
                    self.viewToolBarsMenu.addAction(
                        self.extAppsBar.toggleViewAction())
            self.extAppsBar.addAction(extapp)

        if toMenu and self.TOOLS_MENU_ENABLED:
            if self.toolsMenu is None:
                self.createToolsMenu()
            self.externalAppsMenu.addAction(extapp)
        # register this action for config
        self.registerConfigDelegate(extapp, "_extApp[%s]" % str(extapp.text()))

    def deleteExternalAppLauncher(self, action):
        '''
        Remove launchers for an external application to the Tools Menu
        and/or to the Tools ToolBar.

        :param extapp: (ExternalAppAction) the external application
                       to be removed passed as a :class:`ExternalAppAction`
        '''
        self.configurationDialog.deleteExternalAppConfig(action)
        try:
            # if is in ToolBar
            self.extAppsBar.removeAction(action)
            self.extAppsBar.update()
        except:
            pass
        try:
            # if is in Menu
            self.externalAppsMenu.removeAction(action)
            self.externalAppsMenu.update
        except:
            pass
        # unregister this action for config
        self.unregisterConfigurableItem("_extApp[%s]" % str(action.text()),
                                        raiseOnError=False)

    @deprecation_decorator(dbg_msg="Change Tango Host action is TangoCentric",
                           rel="4.1.2")
    def _onChangeTangoHostAction(self):
        '''
        slot called when the Change Tango Host is triggered. It prompts for a
        Tango host name and calls :meth:`setTangoHost`
        '''
        host, valid = Qt.QInputDialog.getText(
            self, 'Change Tango Host', 'New Tango Host', Qt.QLineEdit.Normal,  str(self.getTangoHost()))
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

    def setHelpManualURI(self, uri):
        self.__helpManualURI = uri
        if self.helpManualBrowser is None:
            try:
                from taurus.external.qt.QtWebKit import QWebView
                self.helpManualBrowser = QWebView()
            except:
                self.helpManualBrowser = Qt.QLabel('QWebkit is not available')

                def dummyload(*args):
                    pass
                self.helpManualBrowser.load = dummyload
                return
        try:
            url = Qt.QUrl.fromUserInput(uri)
        except:
            url = Qt.QUrl(uri)  # fallback for Qt<4.6
        self.helpManualBrowser.load(url)

    def getHelpManualURI(self):
        return self.__helpManualURI

    def resetHelpManualURI(self):
        from taurus.core import release
        uri = getattr(self, 'MANUAL_URI', release.url)
        self.setHelpManualURI(uri)

    def showHelpAbout(self):
        appname = str(Qt.qApp.applicationName())
        appversion = str(Qt.qApp.applicationVersion())
        from taurus.core import release
        abouttext = "%s %s\n\nUsing %s %s" % (
            appname, appversion, release.name, release.version)
        Qt.QMessageBox.about(self, 'About', abouttext)

    def onShowManual(self, anchor=None):
        '''Shows the User Manual in a dockwidget'''
        if self.helpManualDW is None:
            self.helpManualDW = Qt.QDockWidget("Manual", self)
            self.helpManualDW.setWidget(self.helpManualBrowser)
            self.helpManualDW.setObjectName("helpManualDW")
            self.addDockWidget(Qt.Qt.BottomDockWidgetArea, self.helpManualDW)
        else:
            self.helpManualDW.show()

    def checkSingleInstance(self, key=None):
        '''
        Tries to connect via a QLocalSocket to an existing application with the
        given key. If another instance already exists (i.e. the connection succeeds),
        it means that this application is not the only one
        '''
        if key is None:
            from taurus.core.util.user import getSystemUserName
            username = getSystemUserName()
            appname = str(Qt.QApplication.applicationName())
            key = "__socket_%s-%s__" % (username, appname)
        from taurus.external.qt import QtNetwork
        socket = QtNetwork.QLocalSocket(self)
        socket.connectToServer(key)
        alive = socket.waitForConnected(3000)
        if alive:
            self.info('Another application with key "%s" is already running', key)
            return False
        else:
            self.socketServer = QtNetwork.QLocalServer(self)
            self.socketServer.newConnection.connect(self.onIncommingSocketConnection)
            ok = self.socketServer.listen(key)
            if not ok:
                AddressInUseError = QtNetwork.QAbstractSocket.AddressInUseError
                if self.socketServer.serverError() == AddressInUseError:
                    self.info(
                        'Resetting unresponsive socket with key "%s"', key)
                    # removeServer() was added in Qt4.5. (In Qt4.4 a call to
                    # listen() removes a previous server)
                    if hasattr(self.socketServer, 'removeServer'):
                        self.socketServer.removeServer(key)
                    ok = self.socketServer.listen(key)
                if not ok:
                    self.warning('Cannot start local socket with key "%s". Reason: %s ',
                                 key, self.socketServer.errorString())
                    return False
            self.info('Registering as single instance with key "%s"', key)
            return True

    def onIncommingSocketConnection(self):
        '''
        Slot to be called when another application/instance with the same key
        checks if this application exists.

        .. note:: This is a dummy implementation which
                  just logs the connection and discards the associated socket
                  You may want to reimplement this if you want to act on such
                  connections
        '''
        self.info('Incomming connection from application')
        socket = self.socketServer.nextPendingConnection()
        socket.deleteLater()
        self.raise_()
        self.activateWindow()

    def setHeartbeat(self, interval):
        '''sets the interval of the heartbeat LED for the window.
        The heartbeat is displayed by a Led in the status bar unless
        it is disabled by setting the interval to 0

        :param interval: (int) heart beat interval in millisecs. Set to 0 to disable
        '''
        self.heartbeatLed.setBlinkingInterval(interval)
        self.heartbeatLed.setVisible(interval > 0)

    def getHeartbeat(self):
        '''returns the heart beat interval'''
        return self.heartbeatLed.getBlinkingInterval()

    def resetHeartbeat(self):
        '''resets the heartbeat interval'''
        self.setHeartbeat(self.__class__.HEARTBEAT)

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # Public slots for apply/restore changes
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    @Qt.pyqtSlot()
    def applyPendingChanges(self):
        self.applyPendingOperations()

    @Qt.pyqtSlot()
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

    helpManualURI = Qt.pyqtProperty("QString", getHelpManualURI,
                                    setHelpManualURI,
                                    resetHelpManualURI)

    heartbeat = Qt.pyqtProperty("int", getHeartbeat,
                                setHeartbeat,
                                resetHeartbeat)

#---------

if __name__ == "__main__":

    from taurus.qt.qtgui.application import TaurusApplication
    app = TaurusApplication(cmd_line_parser=None)
    app.setApplicationName('TaurusMainWindow-test')
    app.setOrganizationName('ALBA')
    app.basicConfig()

    class MyMainWindow(TaurusMainWindow):
        HEARTBEAT = 300  # blinking semi-period in ms. Set to None for not showing the Heart beat LED
        FILE_MENU_ENABLED = True
        VIEW_MENU_ENABLED = True
        TAURUS_MENU_ENABLED = False
        TOOLS_MENU_ENABLED = True
        HELP_MENU_ENABLED = True
        # Allows the user to change/create/delete perspectives
        USER_PERSPECTIVES_ENABLED = True
        LOGGER_WIDGET_ENABLED = True
        # set to None for disabling splash screen
        SPLASH_LOGO_NAME = "large:TaurusSplash.png"
        _splashMessage = "Initializing Main window..."

        def __init__(self):
            TaurusMainWindow.__init__(
                self, parent=None, designMode=False, splash=None)
            # simulating a lengthy initialization
            import time
            for i in range(5):
                time.sleep(0.5)
                self.splashScreen().showMessage("starting: step %i/5" % (i + 1))

    #MainWindowKlass = TaurusMainWindow

    form = MyMainWindow()

    # ensure only a single instance of this application is running
    single = form.checkSingleInstance()
    if not single:
        sys.exit(1)

    # form.setHelpManualURI('http://google.com')

    form.loadSettings()

    # form.setCentralWidget(Qt.QMdiArea()) #just for testing

    # form.addExternalAppLauncher('pwd')

    form.show()

    sys.exit(app.exec_())
