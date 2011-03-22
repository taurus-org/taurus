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

__docformat__ = 'restructuredtext'


import os, sys
import weakref, inspect, copy
from PyQt4 import Qt

from taurus.qt.qtcore.configuration import BaseConfigurableClass
from taurus.qt.qtcore.communication import SharedDataManager
from taurus.qt.qtgui.util import TaurusWidgetFactory
from taurus.qt.qtgui.base import TaurusBaseWidget, TaurusBaseComponent
from taurus.qt.qtgui.container import TaurusMainWindow
from taurus.qt.qtgui.plot import TaurusTrend, TaurusMonitorTiny
from taurus.qt.qtgui.input import GraphicalChoiceDlg

try:
    from taurus.qt.qtgui.extra_pool import PoolMotorSlim, PoolChannel
    HAS_EXTRA_POOL = True
except ImportError:
    HAS_EXTRA_POOL = False

from taurus.qt.qtgui.taurusgui.utils import PanelDescription, ExternalApp
from PermanentCustomPanelsDlg import PermanentCustomPanelsDlg
import taurus.qt.qtgui.resource
from taurus.core.util import etree


class DockWidgetPanel(Qt.QDockWidget, TaurusBaseWidget):
    '''
    This is an extended QDockWidget which provides some methods for being used
    as a "panel" of a TaurusGui application. Widgets of TaurusGui are inserted
    in the application by adding them to a DockWidgetPanel.
    '''
    def __init__(self, parent, widget, name, mainwindow):
        Qt.QDockWidget.__init__(self, None)
        TaurusBaseWidget.__init__(self, name, parent=parent)
        
        self.setWidget(widget)
        self._widget = self.widget()  #keep a pointer that may change if the widget changes
        name = unicode(name)
        self.setWindowTitle(name)
        self.setObjectName(name)
        self._custom = False
        
        #store a weakref of the main window
        self._mainwindow =  weakref.proxy(mainwindow)
        
        #create and connect the toggleViewAction associated with this panel
        self.connect(self,Qt.SIGNAL('visibilityChanged(bool)'), self.onVisibilityChanged)
    
    def onVisibilityChanged(self, visible):
        if visible:
            self.onSelected()
            
    def onSelected(self):
        self.debug('panel "%s" selected'%unicode(self.objectName()))
        w = self.widget()
        if w is not None:
            w.emit(Qt.SIGNAL("panelSelected"), unicode(self.objectName()))
    
    def isCustom(self):
        return self._custom
    
    def setCustom(self, custom):
        self._custom = custom
        
    def isPermanent(self):
        return self._permanent
    
    def setPermanent(self, permanent):
        self._permanent = permanent
    
    def setWidgetFromClassName(self, classname):
        if self.getWidgetClassName() != classname:
            klass = TaurusWidgetFactory().getWidgetClass(classname)
            w = klass()
            #set customwidgetmap if necessary
            if hasattr(w,'setCustomWidgetMap'):
                w.setCustomWidgetMap(self._mainwindow.getCustomWidgetMap())
            self.setWidget(w)
            wname="%s-%s"%(str(self.objectName()), str(classname))
            w.setObjectName(wname)
            
    def getWidgetClassName(self):
        w = self.widget()
        if w is None:
            return ''
        return w.__class__.__name__
        
    def applyConfig(self, configdict, depth=-1):
        #create the widget
        try: 
            self.setWidgetFromClassName(configdict.get('widgetClassName'))
            if isinstance(self.widget(),BaseConfigurableClass):
                self.widget().applyConfig(configdict['widget'])
        except Exception,e:
            self.info('Failed to set the widget for this panel. Reason: %s'%repr(e)) 
            return
        TaurusBaseWidget.applyConfig(self, configdict, depth)
        
    def createConfig(self, *args, **kwargs):
        configdict = TaurusBaseWidget.createConfig(self, *args, **kwargs)
        configdict['widgetClassName'] = self.getWidgetClassName()
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
    
    ..note:: 
        Please be aware that TaurusGui has only recently being developed and it
        is still under intense development. The syntax of the configuration files
        may change at some point and more features and bug fixes are likely to
        be added in the near future.
    '''
    
    def __init__(self, parent=None, confname=None, xmlconffile=None):
        TaurusMainWindow.__init__(self, parent, False, True)
        
        self.__panels = {}   
        self.__synoptics = []
        
        self.setDockNestingEnabled(True)
        
        self.registerConfigProperty(self._getPermanentCustomPanels, self._setPermanentCustomPanels, 'permanentCustomPanels')
        
        if HAS_EXTRA_POOL:
            self.info('extra_pool available: using PoolMotorSlim and PoolChannel widgets')
            self._customWidgetMap ={'SimuMotor':PoolMotorSlim,
                                    'Motor':PoolMotorSlim,
                                    'PseudoMotor':PoolMotorSlim,
                                    'PseudoCounter':PoolChannel,
                                    'CTExpChannel':PoolChannel,
                                    'ZeroDExpChannel':PoolChannel,
                                    'OneDExpChannel':PoolChannel,
                                    'TwoDExpChannel':PoolChannel}
        else:
            self.info('extra_pool not available: using generic widgets for motors and channels')
        
        #Create a global SharedDataManager
        Qt.qApp.SDM =  SharedDataManager(self)
        
        self.__initViewMenu()
        self.__initPanelsToolBar()
        self.__initQuickAccessToolBar()
        self.__initJorgBar()  
        self.__initSharedDataConnections()
        self.__initToolsMenu()
                
        if confname is not None:
            self.loadConfiguration(confname)
        if xmlconffile is not None:            
            self.loadXmlConfigurationFile(xmlconffile)
        
        self.updatePerspectivesMenu()
        self.splashScreen().finish(self)
        self.statusBar().showMessage('%s is ready'%Qt.qApp.applicationName())
            
    def __initViewMenu(self):        
        #Panels view menu
        self.__panelsMenu =  Qt.QMenu('Panels',self)
        self.viewMenu.addSeparator()
        self.hideAllPanelsAction = self.__panelsMenu.addAction(taurus.qt.qtgui.resource.getIcon(':/actions/hide.svg'),"Hide all panels", self.hideAllPanels)
        self.showAllPanelsAction = self.__panelsMenu.addAction(taurus.qt.qtgui.resource.getIcon(':/actions/show.svg'),"Show all panels", self.showAllPanels)
        self.viewMenu.addSeparator()
        self.viewMenu.addMenu(self.__panelsMenu)
        self.newPanelAction = self.__panelsMenu.addAction(taurus.qt.qtgui.resource.getThemeIcon("window-new"),"New Panel...", self.createCustomPanel)
        self.__panelsMenu.addSeparator()
        #Perspectives
        self.viewMenu.addSeparator()
#        self.viewMenu.addAction(self.loadPerspectiveAction)
        self.viewMenu.addMenu(self.perspectivesMenu)
        self.viewMenu.addAction(self.savePerspectiveAction)
        
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
        
    def createMacroInfrastructure(self, msname='', doorname='', meditpath=''):
        '''
        Put here code for initializing infrastructure needed for macro execution 
        '''
        from taurus.qt.qtgui.extra_macroexecutor import TaurusMacroExecutorWidget, TaurusSequencerWidget, TaurusMacroConfigurationDialog, \
                                                     TaurusMacroDescriptionViewer, DoorOutput, DoorDebug, DoorResult
        from taurus.qt.qtgui.extra_macroexecutor.macroparameterseditor.macroparameterseditor import ParamEditorManager
        
        #Create macroconfiguration dialog & action
        self.splashScreen().showMessage("setting up Macro config dialog")
        self.__macroConfigurationDialog = TaurusMacroConfigurationDialog(self)
        self.macroConfigurationAction = self.taurusMenu.addAction(taurus.qt.qtgui.resource.getThemeIcon("preferences-system-session"), "Macro execution configuration...", self.__macroConfigurationDialog.show)
        Qt.qApp.SDM.connectReader("macroserverName", self.__macroConfigurationDialog.selectMacroServer)
        Qt.qApp.SDM.connectReader("doorName", self.__macroConfigurationDialog.selectDoor)
        Qt.qApp.SDM.connectWriter("macroserverName", self.__macroConfigurationDialog, 'macroserverNameChanged')
        Qt.qApp.SDM.connectWriter("doorName", self.__macroConfigurationDialog, 'doorNameChanged')
        
        #put a Macro Executor
        self.splashScreen().showMessage('setting up macro-related components')
        self.__macroExecutor = TaurusMacroExecutorWidget()
        Qt.qApp.SDM.connectReader("macroserverName", self.__macroExecutor.setModel)
        Qt.qApp.SDM.connectReader("doorName", self.__macroExecutor.onDoorChanged)
        Qt.qApp.SDM.connectReader("macroStatus", self.__macroExecutor.onMacroStatusUpdated)
        Qt.qApp.SDM.connectWriter("macroName", self.__macroExecutor, "macroNameChanged")
        Qt.qApp.SDM.connectWriter("executionStarted", self.__macroExecutor, "macroStarted")
        Qt.qApp.SDM.connectWriter("plotablesFilter", self.__macroExecutor, "plotablesFilterChanged")
        self.createPanel(self.__macroExecutor, 'Macros', Qt.Qt.TopDockWidgetArea, registerconfig=True)
        
        #put a Sequencer
        self.__sequencer = TaurusSequencerWidget()
        Qt.qApp.SDM.connectReader("macroserverName", self.__sequencer.setModel)
        Qt.qApp.SDM.connectReader("doorName", self.__sequencer.onDoorChanged)
        Qt.qApp.SDM.connectReader("macroStatus", self.__sequencer.onMacroStatusUpdated)
        Qt.qApp.SDM.connectWriter("macroName", self.__sequencer.tree, "macroNameChanged")
        Qt.qApp.SDM.connectWriter("macroName", self.__sequencer, "macroNameChanged")
        Qt.qApp.SDM.connectWriter("executionStarted", self.__sequencer, "macroStarted")
        Qt.qApp.SDM.connectWriter("plotablesFilter", self.__sequencer, "plotablesFilterChanged")
        self.createPanel(self.__sequencer, 'Sequences', Qt.Qt.TopDockWidgetArea, registerconfig=True)
        
        #puts a macrodescriptionviewer
        self.__macroDescriptionViewer = TaurusMacroDescriptionViewer(self)
        Qt.qApp.SDM.connectReader("macroserverName", self.__macroDescriptionViewer.setModel)
        Qt.qApp.SDM.connectReader("macroName", self.__macroDescriptionViewer.onMacroNameChanged)
        self.createPanel(self.__macroDescriptionViewer, 'MacroDescription', Qt.Qt.BottomDockWidgetArea, registerconfig=True)
        
        #puts a doorOutput
        self.__doorOutput = DoorOutput(self)
        Qt.qApp.SDM.connectReader("doorOutputChanged", self.__doorOutput.onDoorOutputChanged)
        Qt.qApp.SDM.connectReader("doorInfoChanged", self.__doorOutput.onDoorInfoChanged)
        Qt.qApp.SDM.connectReader("doorWarningChanged", self.__doorOutput.onDoorWarningChanged)
        Qt.qApp.SDM.connectReader("doorErrorChanged", self.__doorOutput.onDoorErrorChanged)
        self.createPanel(self.__doorOutput, 'DoorOutput', Qt.Qt.BottomDockWidgetArea, registerconfig=False)
        
        #puts doorDebug
        self.__doorDebug = DoorDebug(self)
        Qt.qApp.SDM.connectReader("doorDebugChanged", self.__doorDebug.onDoorDebugChanged)
        self.createPanel(self.__doorDebug, 'DoorDebug', Qt.Qt.BottomDockWidgetArea, registerconfig=False)
        
        #puts doorResult
        self.__doorResult = DoorResult(self)
        Qt.qApp.SDM.connectReader("doorResultChanged", self.__doorResult.onDoorResultChanged)
        self.createPanel(self.__doorResult, 'DoorResult', Qt.Qt.BottomDockWidgetArea, registerconfig=False)
        
        #puts a TaurusTrend connected to the door for showing scan trends
        self.__scanTrend = TaurusTrend()
        self.__scanTrend.setXIsTime(False)
        self.__scanTrend.setScansAutoClear(False)
        Qt.qApp.SDM.connectReader("doorName", self.__scanTrend.setScanDoor)
        Qt.qApp.SDM.connectReader("plotablesFilter", self.__scanTrend.onScanPlotablesFilterChanged)
        self.createPanel(self.__scanTrend, '1D Scans', Qt.Qt.RightDockWidgetArea, registerconfig=True)
        
        #The app-wide door
        self.__qdoor = None
        
        #connect to macroserver and door if given
        if msname: self.emit(Qt.SIGNAL("macroserverNameChanged"), msname)
        if doorname: self.emit(Qt.SIGNAL("doorNameChanged"), doorname)
        if meditpath:
            ParamEditorManager().parsePaths(meditpath)
            ParamEditorManager().browsePaths()
        
    def __initSharedDataConnections(self):        
        #register the TAURUSGUI itself as a writer/reader for several shared data items
        self.splashScreen().showMessage("setting up shared data connections")
        Qt.qApp.SDM.connectWriter("macroserverName", self, 'macroserverNameChanged')
        Qt.qApp.SDM.connectWriter("doorName", self, 'doorNameChanged')
        Qt.qApp.SDM.connectReader("doorName", self.onDoorNameChanged)
        Qt.qApp.SDM.connectReader("SelectedInstrument", self.setFocusToPanel)
        Qt.qApp.SDM.connectReader("executionStarted", self.setFocusToPanel)

    def __initToolsMenu(self):
        if self.toolsMenu is None:
            self.toolsMenu = Qt.QMenu("Tools")
        
        self.toolsMenu.addAction(taurus.qt.qtgui.resource.getThemeIcon("preferences-desktop-personal"),"select panel Configuration", self.updatePermanentCustomPanels)
        
    def setCustomWidgetMap(self, map):
        self._customWidgetMap = map
        
    def getCustomWidgetMap(self):
        return self._customWidgetMap   
       
    def createConfig(self, *args, **kwargs):
        '''reimplemented from TaurusMainWindow.createConfig'''
        self.updatePermanentCustomPanels(showAlways=False)
        return TaurusMainWindow.createConfig(self, *args, **kwargs)        
 
    def removePanel(self, name):
        ''' remove the given panel from the GUI
        
        :param name: (str) the name of the panel to be removed'''
        name = unicode(name)
        if name not in self.__panels: return
        panel = self.__panels.pop(name)
        self.__panelsMenu.removeAction(panel.toggleViewAction())
        self.unregisterConfigurableItem(name, raiseOnError=False)
        panel.setParent(None)
        panel.destroy()
    
    def createPanel(self, widget, name, area, registerconfig=True, custom=False, permanent=False):
        '''
        Creates a panel in the given area containing the given widget.
        
        :param wiget: (QWidget) the widget to be contained in the panel
        :param name: (str) the name of the panel. It will be used in tabs as well as for configuration
        :param area: (QDockWidgetArea or None) the area in which the panel is to be created. If None, The TopDockWidgetArea will be used and the panel will be floating
        :param registerconfig: (bool) if True, the panel will be registered as a delegate for configuration
        :param custom: (bool) if True the panel is to be considered a "custom panel"
        :param permanent: (bool) set this to True for custom panels that need to be recreated when restoring the app  
        
        :return: (DockWidgetPanel) the created panel
         
        '''
        name = unicode(name)
        if name in self.__panels:
            self.info('Panel with name "%s" already exists. Reusing.'%name)
            return self.__panels[name]  
        
        if area is None:
            area = Qt.Qt.RightDockWidgetArea
            floating = True
        else: 
            floating = False
        
        # create a panel
        otherpanels = self.findPanelsInArea(area)
        panel = DockWidgetPanel(None, widget, name, self)
        if len(otherpanels)== 0:
            self.addDockWidget(area, panel)
        else:
            self.tabifyDockWidget(otherpanels[-1], panel)
            
        panel.setFloating(floating)

        #add toggle view action for this panel to the panels menu  
        self.__panelsMenu.addAction(panel.toggleViewAction())
        
        #set flags
        panel.setCustom(custom)
        panel.setPermanent(permanent)    
                       
        #register the panel for configuration
        if registerconfig: 
            self.registerConfigDelegate(panel, name=name)
        self.__panels[name] = panel
            
#        #connect the "relocationRequested" signal
#        self.connect(panel, Qt.SIGNAL('relocationRequested'), self.movePanel)
        return panel

   
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
                self.createPanel(None, name, None, custom=True, permanent=True) #at this point we still don't know where to put the widget... 
        
    def _getPermanentCustomPanels(self):
        ''' 
        returns a list of panel names for which the custom and permanent flags
        are True (i.e., those custom panels that should be stored in
        configuration and/pr perspectives)
        
        :return: (list<str>) 
        '''        
        return [n for n,p in self.__panels.iteritems() if (p.isCustom() and  p.isPermanent())]
        
    def updatePermanentCustomPanels(self, showAlways=True):
        '''
        Shows a dialog for selecting which custom panels should be permanently
        stored in the configuration. If showAlways is False, the dialog is only
        shown if there are custom panels which may be not saved.
        
        :param showAlways: (bool) forces showing the dialog even if there are no new custom Panels  
        '''
        #check if there are some newly created panels that may be made permanent
        perm = self._getPermanentCustomPanels()
        temp = [n for n,p in self.__panels.iteritems() if (p.isCustom() and not p.isPermanent())]
        if len(temp)>0 or showAlways:
            dlg = PermanentCustomPanelsDlg(temporaryList=temp, permanentList=perm)
            result = dlg.exec_()
            if result == Qt.QDialog.Accepted:
                #update the permanent Custom Panels
                registered = self.getConfigurableItemNames()
                perm = dlg.getPermanentPanels()
                for name in perm:
                    if name not in registered:
                        self.__panels[name].setPermanent(True)
                        self.registerConfigDelegate(self.__panels[name], name)
                #unregister any panel that is temporary
                for name in dlg.getTemporaryPanels():
                    self.__panels[name].setPermanent(False)
                    self.unregisterConfigurableItem(name, raiseOnError=False)
            
    def createCustomPanel(self, paneldesc=None):
        '''
        Creates a panel which can be filled with a widget.
        
        :param paneldesc: (PanelDescription) description of the panel to be created
                     
        .. seealso:: :meth:`createPanel`
        '''

        if paneldesc is None:
            from taurus.qt.qtgui.taurusgui import PanelDescriptionWizard
            paneldesc,ok = PanelDescriptionWizard.getDialog(self)
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
        

        self.createPanel(w, paneldesc.name, paneldesc.area, custom=True, registerconfig=False)
        self.statusBar().showMessage('Panel %s created. Drag items to it or use the context menu to customize it'%w.name)
        
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
            print repr(e)
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
            
        synopticpanel = self.createPanel(synoptic, name, Qt.Qt.BottomDockWidgetArea)
        toggleSynopticAction = synopticpanel.toggleViewAction()
        toggleSynopticAction.setIcon(taurus.qt.qtgui.resource.getThemeIcon('image-x-generic'))
        self.quickAccessToolBar.addAction(toggleSynopticAction)
                
    def createInstrumentsFromPool(self, macroservername):
        '''creates a list of instrument objects
        
        :return: (list<object>) A list of instrument objects. Each instrument
                 object has "name" (str) and "model" (list<str>) members
                 
        '''      
        instrument_dict = {}
        try:
            ms = taurus.Device(macroservername)
            instruments = ms['InstrumentList'].value
            if instruments is None: raise
        except Exception,e:
            msg = 'Could not fetch Instrument list from "%s"'%macroservername
            self.error(msg)
            result = Qt.QMessageBox.critical(self,'Initialization error', '%s\n\n%s'%(msg,repr(e)), Qt.QMessageBox.Abort|Qt.QMessageBox.Ignore)
            if result == Qt.QMessageBox.Abort:
                sys.exit()
            return []
        for i in instruments:
            i_name, i_unknown, i_type, i_pools = i.split()
            i_view = PanelDescription(i_name,classname='TaurusForm', area=Qt.Qt.LeftDockWidgetArea, model=[])
            instrument_dict[i_name] = i_view
        
        motors = ms.getElementNamesOfType('Motor')
        channels = ms.getElementNamesOfType('ExpChannel')
        pool_elements = motors + channels
        for e_name in pool_elements:
            e = taurus.Device(e_name)
            instrument = e['Instrument'].value
            if instrument != '':
                i_name = instrument[:instrument.find('(')]
                e_name = e.alias()
                instrument_dict[i_name].model.append(e_name)
                
        return instrument_dict.values()
    
    
    def __getVarFromXML(self, root, nodename, default=None):
        name = root.find(nodename)
        if name is None or name.text is None:
            return default
        else:
            return name.text
    
    def loadXmlConfigurationFile(self, fname=None):    
        if (fname is None) or len(fname)==0:
            fname = Qt.QFileDialog.getOpenFileName(self, self.tr("Open File"),Qt.QDir.homePath(), self.tr("XML (*.xml); All files (*.*)" ))
            if fname is None:
                sys.exit(1)
            else:
                fname=unicode(fname)        
        try:
            xmlFile = open(fname, 'r')
            xml = xmlFile.read()
            xmlFile.close()
            self._confDirectory = os.path.dirname(fname)
            self._confFileName = os.path.basename(fname)
        except Exception, e:
            msg = 'Cannot read the file: "%s"' % fname
            self.error(msg)
            self.traceback(level=taurus.Info)
            fname =None
            result = Qt.QMessageBox.critical(self,'Initialization error', '%s\nReason:"%s"'% (msg,repr(e)), Qt.QMessageBox.Abort)
            sys.exit()
            
        self.loadXmlConfiguration(xml)
    

    
    def loadXmlConfiguration(self, xml):
        #
        try:
            root = etree.fromstring(xml)
        except:
            msg = 'XML Syntax Error'
            self.error(msg)
            self.traceback(level=taurus.Info)
            Qt.QMessageBox.critical(self,'Initialization error', msg, Qt.QMessageBox.Abort)
            sys.exit()
            
        APPNAME = self.__getVarFromXML(root,"GUI_NAME", None)
        if APPNAME is None:
            msg = 'Could not find the GUI_NAME'
            self.error(msg)
            Qt.QMessageBox.critical(self,'Initialization error', msg, Qt.QMessageBox.Abort)
            sys.exit()
       
        ORGNAME = self.__getVarFromXML(root,"ORGANIZATION", 'Taurus')
        CUSTOMLOGO = self.__getVarFromXML(root,"CUSTOM_LOGO", ':/taurus.png')
        
        Qt.qApp.setApplicationName(APPNAME)
        Qt.qApp.setOrganizationName(ORGNAME)
        self.resetQSettings()
        
        self.setWindowTitle(APPNAME)
        windowIcon = taurus.qt.qtgui.resource.getIcon(CUSTOMLOGO)
        self.setWindowIcon(windowIcon)
        self.jorgsBar.addAction(taurus.qt.qtgui.resource.getIcon(":/logo.png"),ORGNAME)
        self.jorgsBar.addAction(taurus.qt.qtgui.resource.getIcon(CUSTOMLOGO),APPNAME)
        
        #configure the macro infrastructure
        MACROSERVER_NAME = self.__getVarFromXML(root,"MACROSERVER_NAME", None)
        DOOR_NAME = self.__getVarFromXML(root,"DOOR_NAME", '')
        MACROEDITORS_PATH = self.__getVarFromXML(root,"MACROEDITORS_PATH", '')
        if MACROSERVER_NAME is not None:
            self.createMacroInfrastructure(msname=MACROSERVER_NAME, doorname=DOOR_NAME, meditpath=MACROEDITORS_PATH)
         
        SYNOPTIC = []
        synoptic = root.find("SYNOPTIC")
        if (synoptic is not None) and (synoptic.text is not None):
            for child in synoptic:
                if (child.get("str") is not None):
                    if len(child.get("str")):
                        SYNOPTIC.append(child.get("str"))
                    
        for s in SYNOPTIC:
            self.createMainSynoptic(s)
        
             
        #create instrument panels and custom panels
        CUSTOM_PANELS = []
        
        panelDescriptions = root.find("PanelDescriptions")
        if (panelDescriptions is not None):
            for child in panelDescriptions:
                    if (child.tag == "PanelDescription"):
                        pd = PanelDescription.fromXml(etree.tostring(child))
                        if pd is not None:
                            CUSTOM_PANELS.append(pd)
                            
        INSTRUMENTS_FROM_POOL = (self.__getVarFromXML(root,"INSTRUMENTS_FROM_POOL", 'False').lower() == 'true')                   
        if INSTRUMENTS_FROM_POOL:
            POOLINSTRUMENTS = self.createInstrumentsFromPool(MACROSERVER_NAME) #auto create instruments from pool 
        else:
            POOLINSTRUMENTS = []

        for p in CUSTOM_PANELS + POOLINSTRUMENTS:
            try:
                w = p.getWidget(sdm=Qt.qApp.SDM, setModel=False)
                if hasattr(w,'setCustomWidgetMap'):
                    w.setCustomWidgetMap(self.getCustomWidgetMap())
                if p.model is not None:
                    w.setModel(p.model)
                #create a panel
                self.createPanel(w, p.name, p.area)
                #connect the widget
                Qt.qApp.SDM.connectWriter("SelectedInstrument", w, "panelSelected")
                
            except Exception,e:
                msg='Cannot create panel %s'%getattr(p,'name','__Unknown__')
                self.error(msg)
                self.traceback(level=taurus.Info)
                result = Qt.QMessageBox.critical(self,'Initialization error', '%s\n\n%s'%(msg,repr(e)), Qt.QMessageBox.Abort|Qt.QMessageBox.Ignore)
                if result == Qt.QMessageBox.Abort:
                    sys.exit()
                    
        
        #add external applications
        EXTERNAL_APPS = [] 
        
        externalAppsNode = root.find("ExternalApps")
        if (externalAppsNode is not None):
            for child in externalAppsNode:
                    if (child.tag == "ExternalApp"):
                        ea = ExternalApp.fromXml(etree.tostring(child))
                        if ea is not None:
                            EXTERNAL_APPS.append(ea)
        
        for a in EXTERNAL_APPS:
            self.addExternalAppLauncher(a.getAction())
        
        #add a beam monitor  
            
        MONITOR = self.__getVarFromXML(root,"MONITOR", '')
        monitorNode = root.find("MONITOR")
        
        if MONITOR:
            self.__monitor = TaurusMonitorTiny()
            self.__monitor.setModel(MONITOR)
            self.jorgsBar.addWidget(self.__monitor)
            self.registerConfigDelegate(self.__monitor, 'monitor')
        
        #read QSettings 
        self.loadSettings()
        #If no valid ini file is found in the standard locations, try with a fallback ini file
        if self.getQSettings().allKeys().isEmpty(): 
            #open the fall back file (aka "factory" settings)
            rname,ext = os.path.splitext(self._confFileName)
            iniFileName = self.__getVarFromXML(root,"INIFILENAME", '%s.ini'%rname) #the name of the fallback file can be specified in the conf file using "INIFILE". It defaults to <confname>.ini
            factorySettings = Qt.QSettings(iniFileName, Qt.QSettings.IniFormat)
            #clone the perspectives found in the "factory" settings
            for p in self.getPerspectivesList(settings=factorySettings):
                self.loadPerspective(name=p, settings=factorySettings)
                self.savePerspective(name=p)
            #finally load the settings
            self.loadSettings(settings=factorySettings)
        
    
    def loadConfiguration(self, confname):
        '''Reads a configuration file
        
        :param confname: (str) the  name of a conf module located in the PYTHONPATH
                         or in the conf subdirectory of the directory in which 
                         taurusgui.py file is installed.
                         This method will try to import <confname>.  If that fails, 
                         it will try to import "TaurusGUI_conf_<confname>".
        '''
        altconfname = "tgconf_%s"%confname
        
        confsubdir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'conf') #the path to a conf subdirectory
        oldpath = sys.path
        sys.path = [confsubdir] + sys.path #add the config dir to the pythonpath
        try:
            try: 
                conf = __import__(confname)
            except ImportError:
                try:
                    conf = __import__(altconfname)
                except ImportError:
                    msg = 'Could not find %s or %s in %s or the Python path'%(confname, altconfname, confsubdir)
                    self.error(msg)
                    Qt.QMessageBox.critical(self,'Initialization error', msg, Qt.QMessageBox.Abort)
                    sys.exit()
        except Exception, e:
            msg = 'Error loading configuration file: %s'%repr(e)
            self.error(msg)
            Qt.QMessageBox.critical(self,'Initialization error', msg, Qt.QMessageBox.Abort)
            sys.exit()
        sys.path = oldpath #restore the previous sys.path
        self._confDirectory = os.path.dirname(conf.__file__)
        
        APPNAME = getattr(conf,'GUI_NAME', confname)
        ORGNAME = getattr(conf,'ORGANIZATION', 'Taurus')
        CUSTOMLOGO =  getattr(conf, 'CUSTOM_LOGO', getattr(conf,'LOGO', ":/taurus.png"))
        if not CUSTOMLOGO.startswith(':'):
            CUSTOMLOGO = os.path.join(self._confDirectory, CUSTOMLOGO)
        Qt.qApp.setApplicationName(APPNAME)
        Qt.qApp.setOrganizationName(ORGNAME)
        self.resetQSettings() 
        
        self.setWindowTitle(APPNAME)
        windowIcon = taurus.qt.qtgui.resource.getIcon(CUSTOMLOGO)
        self.setWindowIcon(windowIcon)
        self.jorgsBar.addAction(taurus.qt.qtgui.resource.getIcon(":/logo.png"),ORGNAME)
        self.jorgsBar.addAction(taurus.qt.qtgui.resource.getIcon(CUSTOMLOGO),APPNAME)
                    
        #configure the macro infrastructure
        MACROSERVER_NAME = getattr(conf,'MACROSERVER_NAME', None)
        DOOR_NAME = getattr(conf,'DOOR_NAME','')
        MACROEDITORS_PATH = getattr(conf,'MACROEDITORS_PATH','')
        if MACROSERVER_NAME is not None:
            self.createMacroInfrastructure(msname=MACROSERVER_NAME, doorname=DOOR_NAME, meditpath=MACROEDITORS_PATH)
            
        #Synoptic  
        SYNOPTIC = getattr(conf, 'SYNOPTIC', [])
        if isinstance(SYNOPTIC, basestring):
            self.warning('Deprecated usage of SYNOPTIC keyword (now it expects a list of paths). Please update your configuration file to: "SYNOPTIC=[\'%s\']".'%SYNOPTIC)
            SYNOPTIC = [SYNOPTIC]
        for s in SYNOPTIC:
            self.createMainSynoptic(s)
            
        #create instrument panels and custom panels
        CUSTOM_PANELS = [obj for name,obj in inspect.getmembers(conf) if isinstance(obj, PanelDescription)]
        if getattr(conf,'INSTRUMENTS_FROM_POOL',False):
            POOLINSTRUMENTS = self.createInstrumentsFromPool(MACROSERVER_NAME) #auto create instruments from pool 
        else:
            POOLINSTRUMENTS = []

        for p in CUSTOM_PANELS + POOLINSTRUMENTS:
            try:
                w = p.getWidget(sdm=Qt.qApp.SDM, setModel=False)
                if hasattr(w,'setCustomWidgetMap'):
                    w.setCustomWidgetMap(self.getCustomWidgetMap())
                if p.model is not None:
                    w.setModel(p.model)
                #create a panel
                self.createPanel(w, p.name, p.area)
                #connect the widget
                Qt.qApp.SDM.connectWriter("SelectedInstrument", w, "panelSelected")
                
            except Exception,e:
                msg='Cannot create panel %s'%getattr(p,'name','__Unknown__')
                self.error(msg)
                self.traceback(level=taurus.Info)
                result = Qt.QMessageBox.critical(self,'Initialization error', '%s\n\n%s'%(msg,repr(e)), Qt.QMessageBox.Abort|Qt.QMessageBox.Ignore)
                if result == Qt.QMessageBox.Abort:
                    sys.exit()
                
        
        #add external applications
        EXTERNAL_APPS = [obj for name,obj in inspect.getmembers(conf) if isinstance(obj, ExternalApp)]
        for a in EXTERNAL_APPS:
            self.addExternalAppLauncher(a.getAction())
        
        #add a beam monitor
        MONITOR = getattr(conf, 'MONITOR', [])
        if MONITOR:
            self.__monitor = TaurusMonitorTiny()
            self.__monitor.setModel(MONITOR)
            self.jorgsBar.addWidget(self.__monitor)
            self.registerConfigDelegate(self.__monitor, 'monitor')
        
        #read QSettings 
        self.loadSettings()
        #If no valid ini file is found in the standard locations, try with a fallback ini file
        if self.getQSettings().allKeys().isEmpty(): 
            #open the fall back file (aka "factory" settings)
            iniFileName = os.path.join(self._confDirectory, getattr(conf, 'INIFILE', "%s.ini"%conf.__name__)) #the name of the fallback file can be specified in the conf file using "INIFILE". It defaults to <confdir>/<confname>.ini
            factorySettings = Qt.QSettings(iniFileName, Qt.QSettings.IniFormat)
            #clone the perspectives found in the "factory" settings
            for p in self.getPerspectivesList(settings=factorySettings):
                self.loadPerspective(name=p, settings=factorySettings)
                self.savePerspective(name=p)
            #finally load the settings
            self.loadSettings(settings=factorySettings)
            
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
        
                          
    
    def onDoorNameChanged(self, doorname):
        ''' Slot to be called when the door name has changed
        
        :param doorname: (str) the tango name of the door device 
        '''
        if self.__qdoor is not None: #disconnect it from *all* shared data providing
            Qt.qApp.SDM.disconnectWriter("macroStatus", self.__qdoor, "macroStatusUpdated")
            Qt.qApp.SDM.disconnectWriter("doorOutputChanged", self.__qdoor, "outputUpdated")
            Qt.qApp.SDM.disconnectWriter("doorInfoChanged", self.__qdoor, "infoUpdated")
            Qt.qApp.SDM.disconnectWriter("doorWarningChanged", self.__qdoor, "warningUpdated")
            Qt.qApp.SDM.disconnectWriter("doorErrorChanged", self.__qdoor, "errorUpdated")
            Qt.qApp.SDM.disconnectWriter("doorDebugChanged", self.__qdoor, "debugUpdated")
            Qt.qApp.SDM.disconnectWriter("doorResultChanged", self.__qdoor, "resultUpdated")
             
        if doorname == "": return #@todo send signal with doorName to macroExecutorWidget in case of "" also send it to disconnect doorstateled
        door = taurus.Device(doorname)
        if not isinstance(door, Qt.QObject):
            msg= "cannot connect to door %s"%doorname
            Qt.QMessageBox.critical(self,'Door connection error', msg)
            return
        self.__qdoor = door
        Qt.qApp.SDM.connectWriter("macroStatus", self.__qdoor, "macroStatusUpdated")
        Qt.qApp.SDM.connectWriter("doorOutputChanged", self.__qdoor, "outputUpdated")
        Qt.qApp.SDM.connectWriter("doorInfoChanged", self.__qdoor, "infoUpdated")
        Qt.qApp.SDM.connectWriter("doorWarningChanged", self.__qdoor, "warningUpdated")
        Qt.qApp.SDM.connectWriter("doorErrorChanged", self.__qdoor, "errorUpdated")
        Qt.qApp.SDM.connectWriter("doorDebugChanged", self.__qdoor, "debugUpdated")
        Qt.qApp.SDM.connectWriter("doorResultChanged", self.__qdoor, "resultUpdated")
        #@todo: connect as a writer of other data as well
    
#    def onSelectedInstrumentChanged(self, instrumentname):
#        ''' Slot to be called when the selected instrument has changed (e.g. by user
#        clicking in the synoptic)
#        
#        :param instrumentname: (str) The name that identifies the instrument.
#                               This name must be unique within the panels in the
#                               GUI. This is also the name to be used for the
#                               corresponding object in the jdraw synoptic
#        '''
#        instrumentname=unicode(instrumentname)
#        try:
#            inst = self.__panels[instrumentname]
#            inst.show()
#            inst.setFocus()
#            inst.raise_()
#        except KeyError:
#            pass
    
    def hideAllPanels(self):
        '''hides all current panels'''
        for panel in self.__panels.itervalues():
            panel.hide()
            
    def showAllPanels(self):
        '''shows all current panels'''
        for panel in self.__panels.itervalues():
            panel.show()
        
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
        '''
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
        
        
        '''
        if area == 'FLOATING':
            return [p for p in self.__panels.values() if p.isFloating()]
        else:
            return [p for p in self.__panels.values() if self.dockWidgetArea(p)==area]
        
    @classmethod
    def getQtDesignerPluginInfo(cls):
        '''TaurusGui is not to be in designer '''
        return None
    

#------------------------------------------------------------------------------ 
def main():    
    import sys
    from taurus.core.util import argparse
    from taurus.qt.qtgui.application import TaurusApplication
        
    parser = argparse.get_taurus_parser()
    parser.set_usage("%prog [options] confname")
    parser.set_description("The taurus GUI application")
    parser.add_option("--config-file", "--config-file", dest="config_file", default=None,
                  help="use the given XML configuration file for initialization")
    
    app = TaurusApplication(cmd_line_parser=parser, app_name="taurusgui",
                            app_version=taurus.Release.version)
    args = app.get_command_line_args()
    options = app.get_command_line_options()

    if options.config_file is None:
        if len(args) != 1:
            parser.print_help(sys.stderr)
            sys.exit(1)
        confname = args[0] 
        gui = TaurusGui(None, confname=confname)
    else:
        gui = TaurusGui(None, xmlconffile=options.config_file)
    gui.show()
    sys.exit(app.exec_())
   
       
if __name__ == "__main__":
    main()
    #xmlTest()
    

