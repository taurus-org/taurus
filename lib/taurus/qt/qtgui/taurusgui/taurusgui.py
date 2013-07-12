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
###########################################################################

"""This package provides the TaurusGui class"""

__all__=["DockWidgetPanel", "TaurusGui"]

__docformat__ = 'restructuredtext'


import os, sys
import weakref, inspect, copy
from taurus.qt import Qt

from taurus.qt.qtcore.configuration import BaseConfigurableClass
from taurus.qt.qtcore.communication import SharedDataManager
from taurus.qt.qtgui.util import TaurusWidgetFactory
from taurus.qt.qtgui.base import TaurusBaseWidget, TaurusBaseComponent
from taurus.qt.qtgui.container import TaurusMainWindow
from taurus.qt.qtgui.taurusgui.utils import ExternalApp, PanelDescription, ToolBarDescription, AppletDescription
from taurus.qt.qtgui.panel import QDoubleListDlg
import taurus.qt.qtgui.resource
from lxml import etree


class AssociationDialog(Qt.QDialog):
    '''A dialog for viewing and editing the associations between instruments and panels''' 
    def __init__(self, parent, flags= None):
        if flags is None: flags = Qt.Qt.Widget
        Qt.QDialog.__init__(self, parent, flags)
        
        from ui.ui_PanelAssociationsDlg import Ui_PanelAssociationsDlg
        self.ui = Ui_PanelAssociationsDlg()
        self.ui.setupUi(self)
        
        self.refresh()
        self.connect(self.ui.instrumentCB, Qt.SIGNAL('activated (QString)'), self.onInstrumentChanged)
        self.connect(self.ui.buttonBox, Qt.SIGNAL("clicked(QAbstractButton *)"), self.onDialogButtonClicked)
        self.connect(self.ui.refreshBT, Qt.SIGNAL("clicked()"), self.refresh)
        
    def refresh(self):
        currentinstrument = self.ui.instrumentCB.currentText()
        mainwindow = self.parent()
        
        self.associations = mainwindow.getAllInstrumentAssociations()
        
        #fill the comboboxes
        self.ui.instrumentCB.clear()
        self.ui.panelCB.clear()
        self.ui.instrumentCB.addItems(sorted(self.associations.keys()))
        self.ui.panelCB.addItems(['__[None]__']+mainwindow.getPanelNames())
        
        #restore the index
        idx = self.ui.instrumentCB.findText(currentinstrument)
        if idx == -1 and self.ui.instrumentCB.count()>0:
            idx = 0
        self.ui.instrumentCB.setCurrentIndex(idx)
        self.onInstrumentChanged(self.ui.instrumentCB.currentText())
    
    def onInstrumentChanged(self, instrumentname):
        instrumentname = unicode(instrumentname)
        panelname = self.associations.get(instrumentname)
        if panelname is None:
            self.ui.panelCB.setCurrentIndex(0)
            return
        else:
            idx = self.ui.panelCB.findText(panelname)
            self.ui.panelCB.setCurrentIndex(idx)
        
    def onDialogButtonClicked(self, button):
        role = self.ui.buttonBox.buttonRole(button)
        if role in (Qt.QDialogButtonBox.AcceptRole,Qt.QDialogButtonBox.ApplyRole) :
            if self.ui.panelCB.currentIndex() > 0:
                panelname = unicode(self.ui.panelCB.currentText())
            else:
                panelname = None
            instrumentname = unicode(self.ui.instrumentCB.currentText())
            self.associations[instrumentname] = panelname
            self.parent().setInstrumentAssociation(instrumentname,panelname)
        

class DockWidgetPanel(Qt.QDockWidget, TaurusBaseWidget):
    '''
    This is an extended QDockWidget which provides some methods for being used
    as a "panel" of a TaurusGui application. Widgets of TaurusGui are inserted
    in the application by adding them to a DockWidgetPanel.
    '''
    def __init__(self, parent, widget, name, mainwindow):
        Qt.QDockWidget.__init__(self, None)
        TaurusBaseWidget.__init__(self, name, parent=parent)
        
        self.setAllowedAreas(Qt.Qt.TopDockWidgetArea)
        
        self.setWidget(widget)
        #self._widget = self.widget()  #keep a pointer that may change if the widget changes
        name = unicode(name)
        self.setWindowTitle(name)
        self.setObjectName(name)
        self._custom = False
        
        #store a weakref of the main window
        self._mainwindow =  weakref.proxy(mainwindow)
    
    def isCustom(self):
        return self._custom
    
    def setCustom(self, custom):
        self._custom = custom
        
    def isPermanent(self):
        return self._permanent
    
    def setPermanent(self, permanent):
        self._permanent = permanent
    
    def setWidgetFromClassName(self, classname, modulename=None):
        if self.getWidgetClassName() != classname:
            try:
                klass = TaurusWidgetFactory().getWidgetClass(classname)
                w = klass()
            except:
                try:
                    if classname is not None and '.' in classname:
                        mn,classname = classname.rsplit('.',1)
                        modulename = ("%s.%s"%(modulename or '',mn)).strip('. ')
                    module = __import__(modulename, fromlist=[''])
                    klass = getattr(module, classname)
                    w = klass()
                except Exception, e:
                    raise RuntimeError('Cannot create widget from classname "%s". Reason: %s'%(classname, repr(e)))
            #set customwidgetmap if necessary
            if hasattr(w,'setCustomWidgetMap'):
                w.setCustomWidgetMap(self._mainwindow.getCustomWidgetMap())
            self.setWidget(w)
            wname="%s-%s"%(str(self.objectName()), str(classname))
            w.setObjectName(wname)
            
    def getWidgetModuleName(self):
        w = self.widget()
        if w is None:
            return ''
        return w.__module__
            
    def getWidgetClassName(self):
        w = self.widget()
        if w is None:
            return ''
        return w.__class__.__name__
        
    def applyConfig(self, configdict, depth=-1):
        #create the widget
        try:
            self.setWidgetFromClassName(configdict.get('widgetClassName'), modulename=configdict.get('widgetModuleName',None))
            if isinstance(self.widget(),BaseConfigurableClass):
                self.widget().applyConfig(configdict['widget'])
        except Exception,e:
            self.info('Failed to set the widget for this panel. Reason: %s'%repr(e))
            self.traceback(self.Debug)
            return
        TaurusBaseWidget.applyConfig(self, configdict, depth)
        
    def createConfig(self, *args, **kwargs):
        configdict = TaurusBaseWidget.createConfig(self, *args, **kwargs)
        configdict['widgetClassName'] = self.getWidgetClassName()
        configdict['widgetModuleName'] = self.getWidgetModuleName()
        if isinstance(self.widget(),BaseConfigurableClass):
            configdict['widget'] = self.widget().createConfig()
        return configdict
    

class TaurusGui(TaurusMainWindow):
    '''
    This is main class for constructing the dynamic GUIs. Specific GUIs are
    supposed to be created by providing a configuration file which is loaded by
    this class (instead of subclassing it). TaurusGui is a specialised
    TaurusMainWindow which is able to handle "panels" and load configuration
    files.
    
    .. note:: 
        Please be aware that TaurusGui has only recently being developed and it
        is still under intense development. The syntax of the configuration files
        may change at some point and more features and bug fixes are likely to
        be added in the near future.
    '''
    
    IMPLICIT_ASSOCIATION = '__[IMPLICIT]__'
    
    def __init__(self, parent=None, confname=None, configRecursionDepth=None):
        TaurusMainWindow.__init__(self, parent, False, True)
        
        if configRecursionDepth is not None:
            self.defaultConfigRecursionDepth = configRecursionDepth
            
        self.__panels = {}   
        self.__synoptics = []
        self.__instrumentToPanelMap = {}
        self.__panelToInstrumentMap = {}
        self.setDockNestingEnabled(True)
        
        self.registerConfigProperty(self._getPermanentCustomPanels, self._setPermanentCustomPanels, 'permanentCustomPanels')
        self.registerConfigProperty(self.getAllInstrumentAssociations, self.setAllInstrumentAssociations, 'instrumentAssociation')
                
        from taurus import tauruscustomsettings
        self.setCustomWidgetMap(getattr(tauruscustomsettings,'T_FORM_CUSTOM_WIDGET_MAP',{}))
        
        #Create a global SharedDataManager
        Qt.qApp.SDM =  SharedDataManager(self)
                
        self.__initPanelsMenu()
        self.__initViewMenu()
        self.__initPanelsToolBar()
        self.__initQuickAccessToolBar()
        self.__initJorgBar()  
        self.__initSharedDataConnections()
        self.__initToolsMenu()
                    
        self.loadConfiguration(confname)
                
        #connect the main window itself as a reader/writer of "short messages"
        Qt.qApp.SDM.connectReader("shortMessage", self.onShortMessage) 
        Qt.qApp.SDM.connectWriter("shortMessage", self, 'newShortMessage')
        
        #emit a short message informing that we are ready to go
        msg = '%s is ready'%Qt.qApp.applicationName()
        self.emit(Qt.SIGNAL('newShortMessage'), msg)
        
        if self.defaultConfigRecursionDepth >=0:
            Qt.QMessageBox.information(self, "Fail-proof mode", 
                                   ('Running in fail-proof mode.'+
                                    '\nLoading of potentially problematic settings is disabled.'+ 
                                    '\nSome panels may not be loaded or may ignore previous user configuration'+
                                    '\nThis will also apply when loading perspectives'), 
                                   Qt.QMessageBox.Ok, Qt.QMessageBox.NoButton)
        
    def closeEvent(self, event):
        try:
            self.__macroBroker.removeTemporaryPanels()
        except:
            pass
        TaurusMainWindow.closeEvent(self,event)
        
    def __updatePanelsMenu(self):
        '''dynamically fill the panels menus'''
        panelsmenu = self.sender()
        permanent = (panelsmenu == self.__permPanelsMenu)
        panelsmenu.clear()
        panelnames =  sorted([n for n,p in self.__panels.items() if (p.isPermanent() == permanent)])
        for name in panelnames:
            panelsmenu.addAction(self.__panels[name].toggleViewAction())        
            
    def __initPanelsMenu(self):        
        #Panels menu
        self.__panelsMenu =  Qt.QMenu('Panels', self)
        self.menuBar().insertMenu(self.helpMenu.menuAction(), self.__panelsMenu)
        self.hideAllPanelsAction = self.__panelsMenu.addAction(taurus.qt.qtgui.resource.getIcon(':/actions/hide.svg'),"Hide all panels", self.hideAllPanels)
        self.showAllPanelsAction = self.__panelsMenu.addAction(taurus.qt.qtgui.resource.getIcon(':/actions/show.svg'),"Show all panels", self.showAllPanels)
        self.newPanelAction = self.__panelsMenu.addAction(taurus.qt.qtgui.resource.getThemeIcon("window-new"),"New Panel...", self.createCustomPanel)
        self.removePanelAction = self.__panelsMenu.addAction(taurus.qt.qtgui.resource.getThemeIcon("edit-clear"), "Remove Panel...", self.removePanel)
        self.__panelsMenu.addAction(taurus.qt.qtgui.resource.getThemeIcon("preferences-desktop-personal"),"Switch temporary/permanent status...", self.updatePermanentCustomPanels)
        #temporary and permanent panels submenus
        self.__panelsMenu.addSeparator()
        self.__permPanelsMenu = Qt.QMenu('Permanent Panels', self)
        self.__panelsMenu.addMenu(self.__permPanelsMenu)
        self.connect(self.__permPanelsMenu, Qt.SIGNAL('aboutToShow()'), self.__updatePanelsMenu)
        self.__tempPanelsMenu = Qt.QMenu('Temporary Panels', self)
        self.__panelsMenu.addMenu(self.__tempPanelsMenu)
        self.connect(self.__tempPanelsMenu, Qt.SIGNAL('aboutToShow()'), self.__updatePanelsMenu)
        self.__panelsMenu.addSeparator()
        
    def __initViewMenu(self):
        self.viewMenu.addSeparator() #the superclass may already have added stuff to the viewMenu
        #view locking
        self.viewMenu.addSeparator()
        self._lockviewAction = Qt.QAction(taurus.qt.qtgui.resource.getThemeIcon("system-lock-screen"),"Lock View", self)
        self._lockviewAction.setCheckable(True)
        self.connect(self._lockviewAction,Qt.SIGNAL("toggled(bool)"), self.setLockView)
        self._lockviewAction.setChecked(not self.isModifiableByUser())
        self.viewMenu.addAction(self._lockviewAction)
             
    def __initPanelsToolBar(self):
        #Panels toolbar  
        self.panelsToolBar = self.addToolBar("Panels")
        self.panelsToolBar.setObjectName("PanelsToolbar")
        self.panelsToolBar.addAction(self.newPanelAction)
        self.viewToolBarsMenu.addAction(self.panelsToolBar.toggleViewAction())
    
    def __initQuickAccessToolBar(self):
        self.quickAccessToolBar = self.addToolBar("Quick Access")
        self.quickAccessToolBar.setObjectName("quickAccessToolbar")
        self.quickAccessToolBar.setToolButtonStyle(Qt.Qt.ToolButtonTextBesideIcon)
        self.viewToolBarsMenu.addAction(self.quickAccessToolBar.toggleViewAction())

    def __initJorgBar(self):
        #Fancy Stuff ToolBar (aka Jorg's Bar ;) )
        self.jorgsBar = Qt.QToolBar('Fancy ToolBar')
        self.jorgsBar.setObjectName('jorgsToolBar')
        self.addToolBar(Qt.Qt.RightToolBarArea, self.jorgsBar)
        self.jorgsBar.setIconSize(Qt.QSize(60,60))
        self.jorgsBar.setMovable(False)
        
    def __initSharedDataConnections(self):        
        #register the TAURUSGUI itself as a writer/reader for several shared data items
        splashScreen = self.splashScreen()
        if splashScreen is not None:
            self.splashScreen().showMessage("setting up shared data connections")
        Qt.qApp.SDM.connectWriter("macroserverName", self, 'macroserverNameChanged')
        Qt.qApp.SDM.connectWriter("doorName", self, 'doorNameChanged')
        Qt.qApp.SDM.connectReader("SelectedInstrument", self.onSelectedInstrument)
        Qt.qApp.SDM.connectWriter("SelectedInstrument", self, 'SelectedInstrument')
        Qt.qApp.SDM.connectReader("executionStarted", self.setFocusToPanel)
        Qt.qApp.SDM.connectReader("selectedPerspective", self.loadPerspective)
        Qt.qApp.SDM.connectWriter("perspectiveChanged", self, 'perspectiveChanged')
        
    def __initToolsMenu(self):
        if self.toolsMenu is None:
            self.toolsMenu = Qt.QMenu("Tools")
        self.toolsMenu.addAction(taurus.qt.qtgui.resource.getIcon(":/apps/preferences-system-session.svg"),"manage instrument-panel associations", self.onShowAssociationDialog)
        self.toolsMenu.addAction(taurus.qt.qtgui.resource.getThemeIcon("document-save"),"Export current Panel configuration to XML", self.onExportCurrentPanelConfiguration)
        self.toolsMenu.addAction(taurus.qt.qtgui.resource.getIcon(":/actions/data-transfer.svg"),"Show Shared Data Manager connections", self.showSDMInfo)
        
    def setCustomWidgetMap(self, map):
        '''
        Sets the widget map that is used application-wide. This widget map will
        be used by default in all TaurusForm Panels belonging to this gui.
        
        :param map: (dict<str,Qt.QWidget>) a dictionary whose keys are device
                    type strings (e.g. see :class:`PyTango.DeviceInfo`) and
                    whose values are widgets to be used
                    
        .. seealso:: :meth:`TaurusForm.setCustomWidgetMap`, :meth:`getCustomWidgetMap`
        '''
        self._customWidgetMap = map
        
    def getCustomWidgetMap(self):
        '''
        Returns the default map used to create custom widgets by the TaurusForms
        belonging to this GUI
        
        :return: (dict<str,Qt.QWidget>) a dictionary whose keys are device
                 type strings (i.e. see :class:`PyTango.DeviceInfo`) and whose
                 values are widgets to be used
        
        .. seealso:: :meth:`setCustomWidgetMap`
        '''
        return self._customWidgetMap   
       
    def createConfig(self, *args, **kwargs):
        '''reimplemented from TaurusMainWindow.createConfig'''
        self.updatePermanentCustomPanels(showAlways=False)
        return TaurusMainWindow.createConfig(self, *args, **kwargs)   
    
    def removePanel(self, name=None):
        ''' remove the given panel from the GUI.
        
        .. note:: The panel; is actually removed from the current perspective.
                  If the panel is saved in other perspectives, it should be removed from
                  them as well.
        
        :param name: (str or None) the name of the panel to be removed
                     If None given, the user will be prompted
        '''
        if name is None:
            items = sorted([n for n,p in self.__panels.iteritems() if p.isCustom()])
            name,ok = Qt.QInputDialog.getItem (self, "Remove Panel", 
                                               "Panel to be removed (only custom panels can be removed).\n Important: you may want to save the perspective afterwards,\n and maybe remove the panel from other perspectives as well", items, 0, False)
            if not ok:
                return
        name = unicode(name)
        if name not in self.__panels: 
            self.debug('Cannot remove panel "%s" (not found)'%name)
            return
        panel = self.__panels.pop(name)
        try:
            panel.widget().setModel(None) #in case the widget is a Taurus one and does some cleaning when setting model to None
        except:
            pass
        
        self.unregisterConfigurableItem(name, raiseOnError=False)
        self.removeDockWidget(panel)
        panel.setParent(None)
        panel.setAttribute(Qt.Qt.WA_DeleteOnClose)
        panel.close()
        self.debug('Panel "%s" removed'%name)
        
    def createPanel(self, widget, name, floating=False, registerconfig=True, custom=False, 
                    permanent=False, icon=None, instrumentkey=None):
        '''
        Creates a panel containing the given widget.
        
        :param wiget: (QWidget) the widget to be contained in the panel
        :param name: (str) the name of the panel. It will be used in tabs as well as for configuration
        :param floating: (bool) whether the panel should be docked or floating. (see note below)
        :param registerconfig: (bool) if True, the panel will be registered as a delegate for configuration
        :param custom: (bool) if True the panel is to be considered a "custom panel"
        :param permanent: (bool) set this to True for panels that need to be recreated when restoring the app 
        :param icon: (QIcon) icon for the panel  
        :param instrumentkey: (str) name of an instrument to which this panel is to be associated
        
        :return: (DockWidgetPanel) the created panel
        
        .. note:: On a previous version, there was a mandatory parameter called
                  `area` (which accepted a Qt.DockWidgetArea or None as values)
                  this parameter has now been substituted by the keyword
                  argument `floating`. In order to provide backwards
                  compatibility, the "floating" keyword argument stays at the
                  same position as the old `area` argument and if a Qt.DockWidgetArea
                  value is given, it will be interpreted as floating=True (while if
                  `None` is passed, it will be interpreted as floating=False.
        '''
        
        #backwards compatibility:
        if not isinstance(floating, bool):
            self.info('Deprecation warning: please note that the "area" argument is deprecated. See TaurusGui.createPanel doc')
            floating = not(floating)
        
        name = unicode(name)
        if name in self.__panels:
            self.info('Panel with name "%s" already exists. Reusing.'%name)
            return self.__panels[name]  
        
        # create a panel
        panel = DockWidgetPanel(None, widget, name, self)
        if len(self.__panels)== 0:
            self.addDockWidget(Qt.Qt.TopDockWidgetArea, panel) #we will only place panels in this area
        else:
            self.tabifyDockWidget(self.__panels.values()[-1], panel)
            
        panel.setFloating(floating)
        
        #associate this panel with an instrument
        if instrumentkey is not None:
            if instrumentkey == self.IMPLICIT_ASSOCIATION:
                #see if there is an item whose name is the same as that of the panel
                for syn in self.__synoptics:
                    if name in syn.get_item_list():
                        self.setInstrumentAssociation(name, name)
                        break
            else:
                self.setInstrumentAssociation(instrumentkey, name)
        
        if icon is not None:
            panel.toggleViewAction().setIcon(icon)
        
        #set flags
        panel.setCustom(custom)
        panel.setPermanent(permanent)    
                       
        #register the panel for configuration
        if registerconfig: 
            self.registerConfigDelegate(panel, name=name)
        self.__panels[name] = panel
        
        #connect the panel visibility changes
        self.connect(panel,Qt.SIGNAL('visibilityChanged(bool)'),self._onPanelVisibilityChanged)

        return panel
    
    def getPanel(self,name):
        '''get a panel object by name
        
        :return: (DockWidgetPanel)
        '''
        return self.__panels[unicode(name)]
    
    def getPanelNames(self):
        '''returns the names of existing panels
        
        :return: (list<str>)
        '''
        return copy.deepcopy(self.__panels.keys())

    def _setPermanentCustomPanels(self, permCustomPanels):
        '''creates empty panels for restoring custom panels.
        
        :param permCustomPanels: (list<str>) list of names of custom panels
        '''  
        #first create the panels if they don't actually exist
        for name in permCustomPanels:
            if name not in self.__panels:
                self.createPanel(None, name, custom=True, permanent=True) 
        
    def _getPermanentCustomPanels(self):
        ''' 
        returns a list of panel names for which the custom and permanent flags
        are True (i.e., those custom panels that should be stored in
        configuration and/or perspectives)
        
        :return: (list<str>) 
        '''        
        return [n for n,p in self.__panels.iteritems() if (p.isCustom() and  p.isPermanent())]
        
    def updatePermanentCustomPanels(self, showAlways=True):
        '''
        Shows a dialog for selecting which custom panels should be permanently
        stored in the configuration. 
        
        :param showAlways: (bool) forces showing the dialog even if there are no new custom Panels  
        '''
        #check if there are some newly created panels that may be made permanent
        perm = self._getPermanentCustomPanels()
        temp = [n for n,p in self.__panels.iteritems() if (p.isCustom() and not p.isPermanent())]
        if len(temp)>0 or showAlways:
            dlg = QDoubleListDlg(winTitle='Stored panels', 
                     mainLabel='Select which of the panels should be stored',
                     label1='Temporary (to be discarded)', label2='Permanent (to be stored)', 
                     list1=temp, list2=perm )
            result = dlg.exec_()
            if result == Qt.QDialog.Accepted:
                #update the permanent Custom Panels
                registered = self.getConfigurableItemNames()
                for name in dlg.getAll2():
                    if name not in registered:
                        self.__panels[name].setPermanent(True)
                        self.registerConfigDelegate(self.__panels[name], name)
                #unregister any panel that is temporary
                for name in dlg.getAll1():
                    self.__panels[name].setPermanent(False)
                    self.unregisterConfigurableItem(name, raiseOnError=False)
            
    def createCustomPanel(self, paneldesc=None):
        '''
        Creates a panel from a Panel Description and sets it as "custom panel".
        
        :param paneldesc: (PanelDescription) description of the panel to be created
                     
        .. seealso:: :meth:`createPanel`
        '''

        if paneldesc is None:
            from taurus.qt.qtgui.taurusgui import PanelDescriptionWizard
            paneldesc,ok = PanelDescriptionWizard.getDialog(self, extraWidgets=self._extraCatalogWidgets)
            if not ok: 
                return
        w = paneldesc.getWidget(sdm=Qt.qApp.SDM, setModel=False)
        if hasattr(w,'setCustomWidgetMap'):
            w.setCustomWidgetMap(self.getCustomWidgetMap())
        if paneldesc.model is not None:
            w.setModel(paneldesc.model)
        if isinstance(w, TaurusBaseComponent):
            w.setModifiableByUser(True)
            w.setModelInConfig(True)
        
        self.createPanel(w, paneldesc.name, floating=paneldesc.floating, custom=True, 
                         registerconfig=False, instrumentkey=paneldesc.instrumentkey,
                         permanent=False)
        msg = 'Panel %s created. Drag items to it or use the context menu to customize it'%w.name
        self.emit(Qt.SIGNAL('newShortMessage'), msg)
        
    def createMainSynoptic(self, synopticname):
        '''
        Creates a synoptic panel and registers it as "SelectedInstrument" 
        reader and writer (allowing  selecting instruments from synoptic
        '''
        try:
            jdwFileName = os.path.join(self._confDirectory, synopticname)
            from taurus.qt.qtgui.graphic import TaurusJDrawSynopticsView
            synoptic = TaurusJDrawSynopticsView()
            synoptic.setModel(jdwFileName)
            self.__synoptics.append(synoptic)
        except Exception,e:
            #print repr(e)
            msg='Error loading synoptic file "%s".\nSynoptic won\'t be available'%jdwFileName
            self.error(msg)
            self.traceback(level=taurus.Info)
            result = Qt.QMessageBox.critical(self,'Initialization error', '%s\n\n%s'%(msg,repr(e)) , Qt.QMessageBox.Abort|Qt.QMessageBox.Ignore)
            if result == Qt.QMessageBox.Abort:
                sys.exit()
            
        Qt.qApp.SDM.connectWriter("SelectedInstrument", synoptic, "graphicItemSelected(QString)")
        Qt.qApp.SDM.connectReader("SelectedInstrument", synoptic.selectGraphicItem)
        
        #find an unique (and short) name
        name = os.path.splitext(os.path.basename(synopticname))[0]
        if len(name) > 10:
            name = 'Syn'
        i=2
        prefix = name
        while name in self.__panels:
            name = '%s_%i'%(prefix, i)
            i+=1
            
        synopticpanel = self.createPanel(synoptic, name, permanent=True,
                                         icon=taurus.qt.qtgui.resource.getThemeIcon('image-x-generic'))
        toggleSynopticAction = synopticpanel.toggleViewAction()
        self.quickAccessToolBar.addAction(toggleSynopticAction)
    
    def createConsole(self, kernels):
        try:
            from taurus.qt.qtgui.console import TaurusConsole
        except ImportError:
            self.warning('Cannot import taurus.qt.qtgui.console. The Console Panel will not be available')
            return
        console = TaurusConsole(kernels=kernels)
        consolePanel = self.createPanel(console, "Console", permanent=True,
            icon=taurus.qt.qtgui.resource.getThemeIcon('utilities-terminal'))
        toggleConsoleAction = consolePanel.toggleViewAction()
        self.quickAccessToolBar.addAction(toggleConsoleAction)
    
    def createInstrumentsFromPool(self, macroservername):
        '''
        Creates a list of instrument panel descriptions by gathering the info
        from the Pool. Each panel is a TaurusForm grouping together all those
        elements that belong to the same instrument according to the Pool info
        
        :return: (list<PanelDescription>)                 
        '''      
        instrument_dict = {}
        try:
            ms = taurus.Device(macroservername)
            instruments = ms.getElementsOfType('Instrument')
            if instruments is None: raise
        except Exception,e:
            msg = 'Could not fetch Instrument list from "%s"'%macroservername
            self.error(msg)
            result = Qt.QMessageBox.critical(self,'Initialization error', '%s\n\n%s'%(msg,repr(e)), Qt.QMessageBox.Abort|Qt.QMessageBox.Ignore)
            if result == Qt.QMessageBox.Abort:
                sys.exit()
            return []
        for i in instruments.values():
            i_name = i.full_name
            #i_name, i_unknown, i_type, i_pools = i.split()
            i_view = PanelDescription(i_name,classname='TaurusForm', floating=False, model=[])
            instrument_dict[i_name] = i_view
        
        from operator import attrgetter
        pool_elements =  sorted(ms.getElementsWithInterface('Moveable').values(), key=attrgetter('name'))
        pool_elements += sorted(ms.getElementsWithInterface('ExpChannel').values(), key=attrgetter('name'))
        pool_elements += sorted(ms.getElementsWithInterface('IORegister').values(), key=attrgetter('name'))
        for elem in pool_elements:
            instrument = elem.instrument
            if instrument:
                i_name = instrument
                e_name = elem.full_name
                instrument_dict[i_name].model.append(e_name)
        #filter out empty panels
        ret =  [instrument for instrument in instrument_dict.values() if len(instrument.model)>0]
        return ret

    def __getVarFromXML(self, root, nodename, default=None):
        name = root.find(nodename)
        if name is None or name.text is None:
            return default
        else:
            return name.text
    
    def loadConfiguration(self, confname):
        '''Reads a configuration file
        
        :param confname: (str) the  name of module located in the PYTHONPATH
                         or in the conf subdirectory of the directory in which 
                         taurusgui.py file is installed.
                         This method will try to import <confname>.  If that fails, 
                         it will try to import "tgconf_<confname>.
                         Alternatively, confname can be the path to the configuration 
                         directory (not necessarily in the python path).
        '''
        
        #import the python config file
        try:
            if os.path.isdir(confname): #if confname is a dir name
                import imp
                path, name = os.path.split(confname)
                name, ext = os.path.splitext(name) 
                f, filename, data = imp.find_module(name, [path])
                conf = imp.load_module(name, f, filename, data)
            else: #if confname is not a dir name, we assume it is a module name in the python path
                confsubdir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'conf') #the path to a conf subdirectory of the place where taurusgui.py is
                oldpath = sys.path
                sys.path = [confsubdir] + sys.path #add the conf subdirectory dir to the pythonpath
                try: 
                    conf = __import__(confname)
                except ImportError:
                    altconfname = "tgconf_%s"%confname
                    try:
                        conf = __import__(altconfname)
                    except ImportError:
                        msg = 'cannot import %s or %s'%(confname, altconfname)
                        self.error(msg)
                        Qt.QMessageBox.critical(self,'Initialization error', msg, Qt.QMessageBox.Abort)
                        sys.exit()
                sys.path = oldpath #restore the previous sys.path
        except Exception, e:
            import traceback
            msg = 'Error loading configuration: %s'%traceback.format_exc() #repr(e)
            self.error(msg)
            Qt.QMessageBox.critical(self,'Initialization error', msg, Qt.QMessageBox.Abort)
            sys.exit()
            
        #In any case, once we have imported it we can get the configuration directory:
        self._confDirectory = os.path.dirname(conf.__file__)
        
        #Get the xml root node from the xml configuration file 
        XML_CONFIG = getattr(conf,'XML_CONFIG', None)
        if XML_CONFIG is None:
            self._xmlConfigFileName = None
        else:
            self._xmlConfigFileName = os.path.join(self._confDirectory, XML_CONFIG)
        xmlroot = etree.fromstring('<root></root>') #default fallback (in case of I/O or parse errors)
        if XML_CONFIG is not None:
            try:
                xmlfname = os.path.join(self._confDirectory, XML_CONFIG) # If a relative name was given, the conf directory will be used as base path
                xmlFile = open(xmlfname, 'r')
                xmlstring = xmlFile.read()
                xmlFile.close()
                xmlroot = etree.fromstring(xmlstring)
            except Exception, e:
                msg = 'Error reading the XML file: "%s"' % xmlfname
                self.error(msg)
                self.traceback(level=taurus.Info)
                result = Qt.QMessageBox.critical(self,'Initialization error', '%s\nReason:"%s"'% (msg,repr(e)), Qt.QMessageBox.Abort|Qt.QMessageBox.Ignore)
                if result == Qt.QMessageBox.Abort:
                    sys.exit()
                    
        #General Qt application settings and jorgs bar logos
        APPNAME = getattr(conf,'GUI_NAME', self.__getVarFromXML(xmlroot,"GUI_NAME", confname))
        ORGNAME = getattr(conf,'ORGANIZATION', self.__getVarFromXML(xmlroot,"ORGANIZATION", 'Taurus'))
        CUSTOMLOGO =  getattr(conf, 'CUSTOM_LOGO', getattr(conf,'LOGO', self.__getVarFromXML(xmlroot,"CUSTOM_LOGO", ':/taurus.png')))
        if CUSTOMLOGO.startswith(':'):
            customIcon = taurus.qt.qtgui.resource.getIcon(CUSTOMLOGO)
        else:
            customIcon = Qt.QIcon(os.path.join(self._confDirectory, CUSTOMLOGO))
        Qt.qApp.setApplicationName(APPNAME)
        Qt.qApp.setOrganizationName(ORGNAME)
        Qt.QApplication.instance().basicConfig()

        ORGANIZATIONLOGO =  getattr(conf, 'ORGANIZATION_LOGO', self.__getVarFromXML(xmlroot,"ORGANIZATION_LOGO", ':/logo.png'))
        ##
        if ORGANIZATIONLOGO.startswith(':'):
            organizationIcon = taurus.qt.qtgui.resource.getIcon(ORGANIZATIONLOGO)
        else:
            organizationIcon = Qt.QIcon(os.path.join(self._confDirectory, ORGANIZATIONLOGO))
        
        #if required, enforce that only one instance of this GUI can be run
        SINGLEINSTANCE = getattr(conf,'SINGLE_INSTANCE', (self.__getVarFromXML(xmlroot,"SINGLE_INSTANCE", 'True').lower() == 'true') )
        if SINGLEINSTANCE:
            if not self.checkSingleInstance():
                msg = 'Only one istance of %s is allowed to run the same time'%(APPNAME)
                self.error(msg)
                Qt.QMessageBox.critical(self,'Multiple copies', msg, Qt.QMessageBox.Abort)
                sys.exit(1)
        
        #some initialization 
        self.resetQSettings() 
        self.setWindowTitle(APPNAME)
        self.setWindowIcon(customIcon)
        self.jorgsBar.addAction(organizationIcon,ORGNAME)
        self.jorgsBar.addAction(customIcon,APPNAME)
        
        #get custom widget catalog entries
        EXTRA_CATALOG_WIDGETS = getattr(conf,'EXTRA_CATALOG_WIDGETS', []) #@todo: support also loading from xml
        self._extraCatalogWidgets = []
        for classname,pixmapname in EXTRA_CATALOG_WIDGETS:
            if pixmapname and not pixmapname.startswith(":"): # If a relative file name is given, the conf directory will be used as base path
                pixmapname = os.path.join(self._confDirectory,pixmapname)
            self._extraCatalogWidgets.append((classname, pixmapname))
                
        
        #manual panel
        MANUAL_URI = getattr(conf,'MANUAL_URI', self.__getVarFromXML(xmlroot,"MANUAL_URI", None))
        if MANUAL_URI is not None:
            self.setHelpManualURI(MANUAL_URI)
            self.createPanel(self.helpManualBrowser, 'Manual', permanent=True, 
                             icon = taurus.qt.qtgui.resource.getThemeIcon('help-browser'))
                    
        #configure the macro infrastructure       
        MACROSERVER_NAME = getattr(conf,'MACROSERVER_NAME', self.__getVarFromXML(xmlroot,"MACROSERVER_NAME", None))
        MACRO_PANELS = getattr(conf,'MACRO_PANELS', self.__getVarFromXML(xmlroot,"MACRO_PANELS", True))
        if MACRO_PANELS and MACROSERVER_NAME is not None:# macro infrastructure will only be created if MACROSERVER_NAME is set
            from taurus.qt.qtgui.taurusgui import MacroBroker
            self.__macroBroker =  MacroBroker(self)
        if MACROSERVER_NAME: 
            self.emit(Qt.SIGNAL("macroserverNameChanged"), MACROSERVER_NAME)
        
        DOOR_NAME = getattr(conf,'DOOR_NAME', self.__getVarFromXML(xmlroot,"DOOR_NAME", ''))
        if DOOR_NAME:
            self.emit(Qt.SIGNAL("doorNameChanged"), DOOR_NAME)
        
        MACROEDITORS_PATH = getattr(conf,'MACROEDITORS_PATH', self.__getVarFromXML(xmlroot,"MACROEDITORS_PATH", ''))
        if MACROEDITORS_PATH:
            from taurus.qt.qtgui.extra_macroexecutor.macroparameterseditor.macroparameterseditor import ParamEditorManager
            ParamEditorManager().parsePaths(MACROEDITORS_PATH)
            ParamEditorManager().browsePaths()
        
        #Synoptics          
        SYNOPTIC = getattr(conf, 'SYNOPTIC', None)
        if isinstance(SYNOPTIC, basestring): #old config file style
            self.warning('Deprecated usage of SYNOPTIC keyword (now it expects a list of paths). Please update your configuration file to: "SYNOPTIC=[\'%s\']".'%SYNOPTIC)
            SYNOPTIC = [SYNOPTIC]
        if SYNOPTIC is None: #we look in the xml config file if not present in the python config
            SYNOPTIC = []
            node = xmlroot.find("SYNOPTIC")
            if (node is not None) and (node.text is not None):
                for child in node:
                    s = child.get("str")
                    if s is not None and len(s): #we do not append empty strings
                        SYNOPTIC.append(s)
        for s in SYNOPTIC:
            self.createMainSynoptic(s)
            
        #Get panel descriptions from pool if required            
        INSTRUMENTS_FROM_POOL = getattr(conf,'INSTRUMENTS_FROM_POOL', (self.__getVarFromXML(xmlroot,"INSTRUMENTS_FROM_POOL", 'False').lower() == 'true') )                   
        if INSTRUMENTS_FROM_POOL:
            try: self.splashScreen().showMessage("Gathering Instrument info from Pool")
            except AttributeError: pass            
            POOLINSTRUMENTS = self.createInstrumentsFromPool(MACROSERVER_NAME) #auto create instruments from pool 
        else:
            POOLINSTRUMENTS = []

        CONSOLE = getattr(conf,'CONSOLE', self.__getVarFromXML(xmlroot,"CONSOLE", ['ipython']))
        if CONSOLE:
            self.createConsole(CONSOLE)
       
        #get custom panel descriptions from the python config file      
        CUSTOM_PANELS = [obj for name,obj in inspect.getmembers(conf) if isinstance(obj, PanelDescription)]
        
        #add custom panel descriptions from xml config
        panelDescriptions = xmlroot.find("PanelDescriptions")
        if (panelDescriptions is not None):
            for child in panelDescriptions:
                if (child.tag == "PanelDescription"):
                    pd = PanelDescription.fromXml(etree.tostring(child))
                    if pd is not None:
                        CUSTOM_PANELS.append(pd)
        
        #create panels based on the panel descriptions gathered before
        for p in CUSTOM_PANELS + POOLINSTRUMENTS:
            try:
                try: self.splashScreen().showMessage("Creating panel %s"%p.name)
                except AttributeError: pass 
                w = p.getWidget(sdm=Qt.qApp.SDM, setModel=False)
                if hasattr(w,'setCustomWidgetMap'):
                    w.setCustomWidgetMap(self.getCustomWidgetMap())
                if p.model is not None:
                    w.setModel(p.model)
                if p.instrumentkey is None:
                    instrumentkey = self.IMPLICIT_ASSOCIATION 
                registerconfig = p not in POOLINSTRUMENTS #the pool instruments may change when the pool config changes, so we do not store their config
                #create a panel
                self.createPanel(w, p.name, floating=p.floating, registerconfig=registerconfig, instrumentkey=instrumentkey, permanent=True)
            except Exception,e:
                msg='Cannot create panel %s'%getattr(p,'name','__Unknown__')
                self.error(msg)
                self.traceback(level=taurus.Info)
                result = Qt.QMessageBox.critical(self,'Initialization error', '%s\n\n%s'%(msg,repr(e)), Qt.QMessageBox.Abort|Qt.QMessageBox.Ignore)
                if result == Qt.QMessageBox.Abort:
                    sys.exit()
        
        #get custom toolbars descriptions from the python config file      
        CUSTOM_TOOLBARS = [obj for name,obj in inspect.getmembers(conf) if isinstance(obj, ToolBarDescription)]
        
        #add custom toolbar descriptions from xml config
        toolBarDescriptions = xmlroot.find("ToolBarDescriptions")
        if (toolBarDescriptions is not None):
            for child in toolBarDescriptions:
                if (child.tag == "ToolBarDescription"):
                    d = ToolBarDescription.fromXml(etree.tostring(child))
                    if d is not None:
                        CUSTOM_TOOLBARS.append(d)
        
        #create toolbars based on the descriptions gathered before
        for d in CUSTOM_TOOLBARS:
            try:
                try: self.splashScreen().showMessage("Creating Toolbar %s"%d.name)
                except AttributeError: pass 
                w = d.getWidget(sdm=Qt.qApp.SDM, setModel=False)
                if d.model is not None:
                    w.setModel(d.model)
                w.setWindowTitle(d.name)
                #add the toolbar to the window
                self.addToolBar(w)
                #add the toggleview action to the view menu
                self.viewToolBarsMenu.addAction(w.toggleViewAction())
                #register the toolbar as delegate if it supports it
                if isinstance(w,BaseConfigurableClass):
                    self.registerConfigDelegate(w, d.name)
                
            except Exception,e:
                msg='Cannot add toolbar %s'%getattr(d,'name','__Unknown__')
                self.error(msg)
                self.traceback(level=taurus.Info)
                result = Qt.QMessageBox.critical(self,'Initialization error', '%s\n\n%s'%(msg,repr(e)), Qt.QMessageBox.Abort|Qt.QMessageBox.Ignore)
                if result == Qt.QMessageBox.Abort:
                    sys.exit()

        CUSTOM_APPLETS = []
        #for backwards compatibility
        MONITOR = getattr(conf, 'MONITOR', self.__getVarFromXML(xmlroot,"MONITOR", []))
        if MONITOR:
            CUSTOM_APPLETS.append(AppletDescription('monitor', classname='TaurusMonitorTiny', model=MONITOR) )
        
        #get custom applet descriptions from the python config file      
        CUSTOM_APPLETS += [obj for name,obj in inspect.getmembers(conf) if isinstance(obj, AppletDescription)]
        
        #add applet descriptions from xml config
        appletDescriptions = xmlroot.find("AppletDescriptions")
        if (appletDescriptions is not None):
            for child in appletDescriptions:
                if (child.tag == "AppletDescription"):
                    d = AppletDescription.fromXml(etree.tostring(child))
                    if d is not None:
                        CUSTOM_APPLETS.append(d)
        
        #create applet based on the descriptions gathered before
        for d in CUSTOM_APPLETS:
            try:
                try: self.splashScreen().showMessage("Creating applet %s"%d.name)
                except AttributeError: pass 
                w = d.getWidget(sdm=Qt.qApp.SDM, setModel=False)
                if d.model is not None:
                    w.setModel(d.model)
                #add the widget to the applets toolbar
                self.jorgsBar.addWidget(w)
                #register the toolbar as delegate if it supports it
                if isinstance(w,BaseConfigurableClass):
                    self.registerConfigDelegate(w, d.name)                
            except Exception,e:
                msg='Cannot add applet %s'%getattr(d,'name','__Unknown__')
                self.error(msg)
                self.traceback(level=taurus.Info)
                result = Qt.QMessageBox.critical(self,'Initialization error', '%s\n\n%s'%(msg,repr(e)), Qt.QMessageBox.Abort|Qt.QMessageBox.Ignore)
                if result == Qt.QMessageBox.Abort:
                    sys.exit()

        #add external applications from both the python and the xml config files
        EXTERNAL_APPS = [obj for name,obj in inspect.getmembers(conf) if isinstance(obj, ExternalApp)]
                
        externalAppsNode = xmlroot.find("ExternalApps")
        if (externalAppsNode is not None):
            for child in externalAppsNode:
                if (child.tag == "ExternalApp"):
                    ea = ExternalApp.fromXml(etree.tostring(child))
                    if ea is not None:
                        EXTERNAL_APPS.append(ea)
        
        for a in EXTERNAL_APPS:
            self.addExternalAppLauncher(a.getAction())
        
        
        
        #get the "factory settings" filename. By default, it is called "default.ini" and resides in the configuration dir
        INIFILE = getattr(conf, 'INIFILE', self.__getVarFromXML(xmlroot,"INIFILE", "default.ini")) 
        iniFileName = os.path.join(self._confDirectory, INIFILE) #if a relative name is given, the conf dir is used as the root path
        
        #read the settings (or the factory settings if the regular file is not found)
        msg = "Loading previous state"
        if self.defaultConfigRecursionDepth >=0:
            msg += " in Fail Proof mode"
        try: self.splashScreen().showMessage(msg)
        except AttributeError: pass
        self.loadSettings(factorySettingsFileName=iniFileName)
            
    def setLockView(self, locked):
        self.setModifiableByUser(not locked)
                
    def setModifiableByUser(self, modifiable):
        if modifiable: 
            dwfeat = Qt.QDockWidget.AllDockWidgetFeatures
        else:
            dwfeat = Qt.QDockWidget.NoDockWidgetFeatures
        for panel in self.__panels.values():
            panel.toggleViewAction().setEnabled(modifiable)
            panel.setFeatures(dwfeat)
        for action in (self.newPanelAction, self.showAllPanelsAction, self.hideAllPanelsAction):
            action.setEnabled(modifiable)
        
        self._lockviewAction.setChecked(not modifiable)
        TaurusMainWindow.setModifiableByUser(self, modifiable)                      

    def onShortMessage(self, msg):
        ''' Slot to be called when there is a new short message. Currently, the only action 
        taken when there is a new message is to display it in the main window status bar.
        
        :param msg: (str) the short descriptive message to be handled 
        '''
        self.statusBar().showMessage(msg)
    
    def hideAllPanels(self):
        '''hides all current panels'''
        for panel in self.__panels.itervalues():
            panel.hide()
            
    def showAllPanels(self):
        '''shows all current panels'''
        for panel in self.__panels.itervalues():
            panel.show()
    
    def onShowAssociationDialog(self):
        '''launches the instrument-panel association dialog (modal)'''
        dlg = AssociationDialog(self)
        Qt.qApp.SDM.connectWriter("SelectedInstrument", dlg.ui.instrumentCB, "activated(QString)")
        dlg.exec_()
        Qt.qApp.SDM.disconnectWriter("SelectedInstrument", dlg.ui.instrumentCB, "activated(QString)")
            
    def getInstrumentAssociation(self, instrumentname):
        '''
        Returns the panel name associated to an instrument name 
        
        :param instrumentname: (str or None) The name of the instrument whose associated panel is wanted
                
        :return: (str or None) the associated panel name (or None).
        '''
        return self.__instrumentToPanelMap.get(instrumentname, None)
    
    def setInstrumentAssociation(self, instrumentname, panelname):
        '''
        Sets the panel name associated to an instrument 
        
        :param instrumentname: (str) The name of the instrument 
        :param panelname: (str or None) The name of the associated 
                          panel or None to remove the association 
                          for this instrument.
        '''
        instrumentname = unicode(instrumentname)
        #remove a previous association if it exists
        oldpanelname = self.__instrumentToPanelMap.get(instrumentname,None)
        self.__panelToInstrumentMap.pop(oldpanelname, None)
                
        #create the new association
        self.__instrumentToPanelMap[instrumentname] = panelname
        if panelname is not None:
            self.__panelToInstrumentMap[panelname] = instrumentname
    
    def getAllInstrumentAssociations(self):
        '''
        Returns the dictionary of instrument-panel associations
                
        :return: (dict<str,str>) a dict whose keys are the instruments known to the gui 
                 and whose values are the corresponding associated panels (or None).
        '''
        return copy.deepcopy(self.__instrumentToPanelMap) 
    
    def setAllInstrumentAssociations(self, associationsdict, clearExisting=False):
        '''
        Sets the dictionary of instrument-panel associations. 
        By default, it keeps any existing association not present in the associationsdict.
        
        :param associationsdict: (dict<str,str>) a dict whose keys are the instruments names
                                 and whose values are the corresponding associated panels (or None)
        :param clearExisting: (bool) if True, the the existing asociations are cleared. 
                              If False (default) existing associations are 
                              updated with those in associationsdict
        '''
        if clearExisting:
            self.__instrumentToPanelMap=copy.deepcopy(associationsdict)
        else:
            self.__instrumentToPanelMap.update(copy.deepcopy(associationsdict))
        self.__panelToInstrumentMap = {}
        for k,v in self.__instrumentToPanelMap.iteritems():
            self.__panelToInstrumentMap[v]=k
    
    def _onPanelVisibilityChanged(self,visible):
        if visible:
            panelname = unicode(self.sender().objectName())
            instrumentname = self.__panelToInstrumentMap.get(panelname)
            if instrumentname is not None:
                self.emit(Qt.SIGNAL('SelectedInstrument'), instrumentname)
          
    def onSelectedInstrument(self, instrumentname):
        ''' Slot to be called when the selected instrument has changed (e.g. by user
        clicking in the synoptic)
        
        :param instrumentname: (str) The name that identifies the instrument.
        '''
        instrumentname = unicode(instrumentname)
        panelname = self.getInstrumentAssociation(instrumentname)
        self.setFocusToPanel(panelname)
         
    def setFocusToPanel(self, panelname):
        ''' Method that sets a focus for panel passed via an argument
        
        :param panelname: (str) The name that identifies the panel.
                               This name must be unique within the panels in the GUI.
        '''
        panelname=unicode(panelname)
        try:
            panel = self.__panels[panelname]
            panel.show()
            panel.setFocus()
            panel.raise_()
        except KeyError:
            pass
     
    def tabifyArea(self, area):
        ''' tabifies all panels in a given area.
        
        :param area: (Qt.DockWidgetArea)
        
        .. warning:: This method is deprecated
        '''
        raise DeprecationWarning('tabifyArea is no longer supported (now all panels reside in the same DockWidget Area)')
        panels = self.findPanelsInArea(area)
        if len(panels)<2: return
        p0 = panels[0]
        for p in panels[1:]:
            self.tabifyDockWidget(p0, p)
            
    def findPanelsInArea(self, area):
        ''' returns all panels in the given area
        
        :param area: (QMdiArea, Qt.DockWidgetArea, 'FLOATING' or None). If
                     area=='FLOATING', the dockwidgets that are floating will be
                     returned.
        :param area:  (Qt.DockWidgetArea or str )
        
        .. warning:: This method is deprecated
        '''
        raise DeprecationWarning('findPanelsInArea is no longer supported (now all panels reside in the same DockWidget Area)')
        if area == 'FLOATING':
            return [p for p in self.__panels.values() if p.isFloating()]
        else:
            return [p for p in self.__panels.values() if self.dockWidgetArea(p)==area]
        
    @classmethod
    def getQtDesignerPluginInfo(cls):
        '''TaurusGui is not to be in designer '''
        return None
    
    def onShowManual(self, anchor=None):
        '''reimplemented from :class:`TaurusMainWindow` to show the manual in a panel (not just a dockwidget)'''
        self.setFocusToPanel('Manual')

    def onExportCurrentPanelConfiguration(self, fname=None):
        
        if fname is None:
            fname = self._xmlConfigFileName
                
        if self._xmlConfigFileName is None:
            xmlroot = etree.Element("taurusgui_config")
        else:
            try:
                f = open(self._xmlConfigFileName,'r')
                xmlroot = etree.fromstring(f.read())
                f.close()
            except Exception,e:
                self.error('Cannot parse file "%s": %s',self._xmlConfigFileName, str(e))
                return
        
        #retrieve/create the PanelDescriptions node
        panelDescriptionsNode = xmlroot.find("PanelDescriptions")
        if panelDescriptionsNode is None:
            panelDescriptionsNode = etree.SubElement(xmlroot, "PanelDescriptions")
        
        #Get all custom panels
        dlg = QDoubleListDlg(winTitle='Export Panels to XML', 
                             mainLabel='Select which of the custom panels you want to export as xml configuration',
                             label1='Not Exported', label2='Exported', 
                             list1=[n for n,p in self.__panels.iteritems() if p.isCustom()], list2=[] )
        result = dlg.exec_()
        if result != Qt.QDialog.Accepted:
            return
        exportlist = dlg.getAll2()
        
        #create xml for those to be exported
        registered = self.getConfigurableItemNames()
        for name in exportlist:
            panel = self.__panels[name]
            if name not in registered:
                panel.setPermanent(True)
                self.registerConfigDelegate(panel, name)
            panelxml = PanelDescription.fromPanel(panel).toXml()
            panelDescriptionsNode.append(etree.fromstring(panelxml))
        xml = etree.tostring(xmlroot, pretty_print=True)
        
        #write to file
        while True: 
            if fname is None:
                fname = Qt.QFileDialog.getOpenFileName(self, "Open File", fname or self._confDirectory, self.tr("XML files (*.xml)"))
                if not fname:
                    return
            fname = str(fname)
            #backup the file   
            if os.path.exists(fname):
                import shutil
                try:
                    bckname = "%s.orig"%fname
                    shutil.copy(fname,bckname)
                except:
                    self.warning("%s will be overwritten but I could not create a backup in %s", fname,bckname)
            #write the data
            try:     
                f = open(fname,'w')
                f.write(xml)
                f.close()
                break
            except Exception,e:
                msg = 'Cannot write to %s: %s'%(fname,str(e))
                self.error(msg)
                Qt.QMessageBox.warning(self, "I/O problem", msg+'\nChoose a different location.', Qt.QMessageBox.Ok, Qt.QMessageBox.NoButton)
                fname = None
        
        
        hint = "XML_CONFIG = %s"%os.path.relpath(fname, self._confDirectory)
        msg = 'Configuration written in %s'%fname 
        self.info(msg)
        Qt.QMessageBox.information(self, "Configuration updated", 
                                   msg+'\nMake sure that the .py configuration file in %s contains\n%s'%(self._confDirectory, hint), 
                                   Qt.QMessageBox.Ok, Qt.QMessageBox.NoButton)
        
        return
    
    def showSDMInfo(self):
        '''pops up a dialog showing the current information from the Shared Data Manager'''
        #w = Qt.QMessageBox( self)
        text = 'Currently managing %i shared data objects:\n%s'%(len(Qt.qApp.SDM.activeDataUIDs()),', '.join(Qt.qApp.SDM.activeDataUIDs()) )
        nfo = Qt.qApp.SDM.info()
        w = Qt.QMessageBox ( Qt.QMessageBox.Information, 'Shared Data Manager Information', text, 
                             buttons = Qt.QMessageBox.Close, parent = self )
        w.setDetailedText(nfo)
        w.show()
        self.info(nfo)
        
        
#------------------------------------------------------------------------------ 
def main():
    import sys
    import taurus
    from taurus.core.util import argparse
    from taurus.qt.qtgui.application import TaurusApplication
    
    taurus.info('Starting execution of TaurusGui')
        
    parser = argparse.get_taurus_parser()
    parser.set_usage("%prog [options] confname")
    parser.set_description("The taurus GUI application")
    parser.add_option("", "--config-dir", dest="config_dir", default=None,
                  help="use the given configuration directory for initialization")
    parser.add_option("", "--new-gui", action="store_true", dest="new_gui", default=None,
                  help="launch a wizard for creating a new TaurusGUI application")
    parser.add_option("", "--fail-proof", action="store_true", dest="fail_proof", default=None,
                  help="launch in fail proof mode (it prevents potentially problematic configs from being loaded)")

    app = TaurusApplication(cmd_line_parser=parser, app_name="taurusgui",
                            app_version=taurus.Release.version)
    args = app.get_command_line_args()
    options = app.get_command_line_options()

    if options.new_gui: #launch app settings wizard instead of taurusgui
        from taurus.qt.qtgui.taurusgui import AppSettingsWizard
        wizard = AppSettingsWizard()
        wizard.show()
        sys.exit(app.exec_())
        
    confname = options.config_dir
    if confname is None:
        if len(args) == 1: #for backwards compat, we allow to specify the confname without the "--config-dir" parameter
            confname = args[0]
        else:
            parser.print_help(sys.stderr)
            sys.exit(1)
    
    if options.fail_proof:
        configRecursionDepth = 0
    else:
        configRecursionDepth = None
        
    gui = TaurusGui(None, confname=confname, configRecursionDepth=configRecursionDepth)
    
    gui.show()
    ret = app.exec_()
    
    taurus.info('Finished execution of TaurusGui')
    sys.exit(ret)
   
       
if __name__ == "__main__":
    main()
    #xmlTest()
    

