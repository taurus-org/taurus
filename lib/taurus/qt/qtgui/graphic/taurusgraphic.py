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
taurusgraphic.py: 
"""

#__all__ = []

__docformat__ = 'restructuredtext'

import time
import sys
import signal
import re
from threading import Thread 
import os
import subprocess
import traceback
import operator
import types

import Queue

from PyQt4 import Qt
import taurus.core
import taurus.core.util

from taurus.qt.qtgui.base import TaurusBaseComponent
from taurus.qt.qtgui.util import QT_ATTRIBUTE_QUALITY_PALETTE, QT_DEVICE_STATE_PALETTE


class TaurusGraphicsUpdateThread(Qt.QThread):
    
    def __init__(self, parent=None):
        """Parent most not be None and must be a TaurusGraphicsScene!"""
        if not isinstance(parent, TaurusGraphicsScene):
            raise RuntimeError("Illegal parent for TaurusGraphicsUpdateThread")
        Qt.QThread.__init__(self, parent)
        self.log = taurus.core.util.Logger('TaurusGraphicsUpdateThread')

    def _updateView(self,v):
        # The first one is the prefered one because it improves performance
        # since updates don't come very often in comparison to with the refresh
        # rate of the monitor (~70Hz)
        if v.viewportUpdateMode() == Qt.QGraphicsView.NoViewportUpdate:
            # We call the update to the viewport instead of the view 
            #itself because apparently there is a bug in QT 4.3 that
            #prevents a proper update when the view is inside a QTab 
            v.viewport().update()
        else:
            v.updateScene(item_rects)
            #v.invalidateScene(item.boundingRect())
        return

    def run(self):
        self.log.debug("run... - TaurusGraphicsUpdateThread")
        emitter = Qt.QObject()
        emitter.moveToThread(Qt.QApplication.instance().thread())
        emitter.setParent(Qt.QApplication.instance())
        Qt.QObject.connect(emitter, Qt.SIGNAL("updateView"), self._updateView)

        p = self.parent()
        while True:
            item = p.getQueue().get(True)
            if type(item) in types.StringTypes:
                if item == "exit":
                    break
                else:
                    continue
            if not operator.isSequenceType(item):
                item = (item,)
            item_rects = [ i.boundingRect() for i in item ]
            
            for v in p.views():
                emitter.emit(Qt.SIGNAL("updateView"), v)
            #End of while
        #End of Thread


class newDialog(Qt.QDialog):
    """ This class create the dialog """
    def __init__(self, parent = None):
        #print "newDialog init ....."
        Qt.QDialog.__init__(self, parent)

    def initComponents(self,newWidget,dev_name,title):
        #print "init Components ...."
        self.setWindowTitle(Qt.QApplication.translate("",title, None, Qt.QApplication.UnicodeUTF8))
        self.resize(Qt.QSize(Qt.QRect(0,0,300,300).size()).expandedTo(self.minimumSizeHint()))
        palette = Qt.QPalette()

        brush = Qt.QBrush(Qt.QColor(143,165,203))
        brush.setStyle(Qt.Qt.SolidPattern)
        palette.setBrush(Qt.QPalette.Active,Qt.QPalette.Button,brush)

        brush = Qt.QBrush(Qt.QColor(255,255,255))
        brush.setStyle(Qt.Qt.SolidPattern)
        palette.setBrush(Qt.QPalette.Inactive,Qt.QPalette.Base,brush)

        self.setPalette(palette)

        widgetLayout = Qt.QVBoxLayout(self)
        widgetLayout.setContentsMargins(10,10,10,10)

        if not dev_name is None:
            lineText = Qt.QLabel("   Device Name:  ")
            editText = Qt.QTextEdit()
            editText.setText(dev_name)
            editText.setMaximumHeight(24)
            self.hboxlayout = Qt.QHBoxLayout()
            self.hboxlayout.setObjectName("hboxlayout")
            self.hboxlayout.addWidget(lineText)
            self.hboxlayout.addWidget(editText)
            widgetLayout.addLayout(self.hboxlayout)
            #gridLayout.addLayout(self.hboxlayout,0,0,1,1)

        widgetLayout.addWidget(newWidget)

    def closeEvent(self,QCloseEvent):
        #print "Closing new Dialog ................."
        pass

    
class TaurusGraphicsScene(Qt.QGraphicsScene):
    '''
    This class encapsulates TaurusJDrawSynopticsView and TaurusGraphicsScene signals/slots
    
    External events::
    
     Slot selectGraphicItem(const QString &) displays a selection
     mark around the TaurusGraphicsItem that matches the argument passed.
    
    Mouse Left-button events::
    
     Signal graphicItemSelected(QString) is triggered, passing the
     selected TaurusGraphicsItem.name() as argument.
    
    Mouse Right-button events::
    
     TaurusGraphicItem.setContextMenu([(ActionName,ActionMethod(device_name))]
     allows to configure custom context menus for graphic items using a list
     of tuples. Empty tuples will insert separators in the menu.
    '''
    __pyqtSignals__ = ("refreshTree2","graphicItemSelected(QString)","graphicSceneClicked(QPoint)")
    
    def __init__(self, parent = None, strt = True):
        name = self.__class__.__name__
        #self.call__init__(taurus.core.util.Logger, name, parent) #Inheriting from Logger caused exceptions in CONNECT
        Qt.QGraphicsScene.__init__(self, parent)
        self.updateQueue = None
        self.updateThread = None
        self.threads = []
        self.pids = []
        
        try:
            self.logger = taurus.core.util.Logger(name)
            #self.logger.setLogLevel(self.logger.Info)
            self.debug = lambda l: self.logger.debug(l)
            self.info = lambda l: self.logger.info(l)
            self.warning = lambda l: self.logger.warning(l)
            self.error = lambda l: self.logger.error(l)
        except:
            print 'Unable to initialize TaurusGraphicsSceneLogger: %s'%traceback.format_exc()       
        if strt:
            self.start()
            
    def mousePressEvent(self,mouseEvent):
        try: 
            x = mouseEvent.scenePos().x()
            y = mouseEvent.scenePos().y()
            self.emit(Qt.SIGNAL("graphicSceneClicked(QPoint)"),Qt.QPoint(x,y))
            obj = self.itemAt(x,y)
            obj_name = hasattr(obj,'_name') and obj._name or ''        
            
            if (mouseEvent.button() == Qt.Qt.LeftButton):
                self.selectGraphicItem(obj_name) # A null obj_name should deselect all
                self.emit(Qt.SIGNAL("graphicItemSelected(QString)"),obj_name) # A null obj_name should deselect all
                
                if hasattr(obj,'_extensions') and obj._extensions:
                    self.getExtList(obj)
                    if obj._extensions.has_key('shellCommand'):
                        self.getShellCommand(obj)
                    if obj._extensions.get('className',None):
                        self.debug('launching className extension object')
                        self.getClassName(obj)
                    else: pass 
                    #   self.getTaurusDevicePanel(obj)
                else: pass
                #   self.getTaurusDevicePanel(obj)
                
            if (mouseEvent.button() == Qt.Qt.RightButton):
                ''' This function is called when right clicking on TaurusDevTree area. A pop up menu will be shown with the available options. '''
                
                if obj_name: self.selectGraphicItem(obj_name)        
                if isinstance(obj,TaurusGraphicsItem):
                    menu = Qt.QMenu(None)#self.parent)     
                    if obj.contextMenu():
                        menu.addSeparator()
                        last_was_separator = True
                        for t in obj.contextMenu(): #It must be a list of tuples (ActionName,ActionMethod)
                            try:
                                k,action = t
                                if k:
                                    configDialogAction = menu.addAction(k)
                                    if action: self.connect(configDialogAction, Qt.SIGNAL("triggered()"), lambda dev=obj_name,act=action: act(dev))
                                    else: configDialogAction.setEnabled(False)
                                    last_was_separator = False
                                elif not last_was_separator: 
                                    menu.addSeparator()
                                    last_was_separator = True
                            except Exception,e: 
                                self.warning('Unable to add Menu Action: %s:%s'%(t,e))
                    elif obj_name.count('/')>=2:
                        def test_device(device): self.launchProcess('tg_devtest %s &'%device)
                        def show_atkpanel(device): self.launchProcess('atkpanelALBA %s &'%device)                     
                        action = menu.addAction('Show %s Panel'%obj._name)
                        self.connect(action, Qt.SIGNAL("triggered()"), lambda dev=obj._name: show_atkpanel(dev))
                        action = menu.addAction('Test %s'%obj._name)
                        self.connect(action, Qt.SIGNAL("triggered()"), lambda dev=obj._name: test_device(dev))    
                    if not menu.isEmpty():
                        menu.addSeparator()
                        menu.exec_(Qt.QPoint(mouseEvent.screenPos().x(),mouseEvent.screenPos().y()))
                    del menu
        except Exception,e:
            self.error( traceback.format_exc())            
            
    def launchProcess(self,process):
        if not hasattr(self,'ChildrenProcesses'): self.ChildrenProcesses = {}
        if process in self.ChildrenProcesses: 
            self.warning( 'Process %s is already running!'%process)
            return
        self.ChildrenProcesses[process] = subprocess.Popen(process,shell=True)
        return
        
    def killProcess(self,regexp):
        if '*' in regexp and not '.*' in regexp:
            regexp = regexp.replace('*','.*')
        for name,process in self.ChildrenProcesses.iteritems():
            try:
                if re.match(regexp,name): process.terminate()
            except Exception,e: self.error( 'Unable to stop %s process: %s' % (name,str(e)))
        return
        
    @Qt.pyqtSignature("selectGraphicItem(const QString &)")
    def selectGraphicItem(self,item_name):
        if not hasattr(self,'SelectionCircle'):
            self.SelectionCircle = Qt.QGraphicsEllipseItem()
            self.addItem(self.SelectionCircle)
        self.SelectionCircle.hide()
        
        if item_name:
            item_name = str(item_name).lower().strip().split()[0]
            for item in self.items():
                if hasattr(item,'_name') and str(item._name).lower() == item_name:
                    try:
                        if hasattr(item,'_extensions') and item._extensions and 'noSelect' in item._extensions:
                            return False
                        
                        rect = item.boundingRect()
                        
                        ## I'm assuming that coordinates are always positive!
                        x,y = item.x(),item.y() #For some elements item position is not well mapped and rect bound must be used instead
                        if not x and not y:
                            x,y = rect.topLeft().x(),rect.topLeft().y() #If the object is in the corner it will be also 0
                        h,w = rect.height(),rect.width()                        
                        
                        self.debug('%s has parent %s' % (item_name,getattr(item.parentItem(),'_name','ung')  if item.parentItem() else 'None'))
                        self.debug('center and width,height are: (%d,%d),(%d,%d)' % (x,y,h,w))

                        self.SelectionCircle.setRect(x-(.5*w),y-(.5*h),w*2,h*2)
                        color = Qt.QColor(Qt.Qt.blue)
                        color.setAlphaF(.10)
                        self.SelectionCircle.setBrush(color)
                        pen = Qt.QPen(Qt.Qt.CustomDashLine)
                        pen.setWidth(4)
                        pen.setColor(Qt.QColor(Qt.Qt.blue))
                        self.SelectionCircle.setPen(pen)
                        self.SelectionCircle.setZValue(9999)
                        #self.SelectionCircle.setVisible(True)
                        #self.update(self.SelectionCircle.rect())
                        self.SelectionCircle.show()
                        
                        for v in self.views(): 
                            v.viewport().update()
                            #v.invalidateScene(self.SelectionCircle.boundingRect())
                        
                        return True
                    except Exception,e:
                        self.warning('selectGraphicsItem(%s) failed! %s' % (item_name,str(e)))
                        print traceback.format_exc()
                        return False
        self.warning('No matching object found for "%s"'%item_name)

    def getExtList(self,obj):
        self.standAlone = False
        self.noPrompt = False
        ExtList = ''
        if obj._extensions.has_key('ExtensionsList'):
            ExtList = obj._extensions['ExtensionsList']    
        ExtList = ExtList.split(',')
        self.noPrompt = obj._extensions.has_key('noPrompt') or 'noPrompt' in ExtList
        self.standAlone = obj._extensions.has_key('standAlone') or 'standAlone' in ExtList
        #for ext in ExtList:
            #if ext == "noPrompt":
                #self.noPrompt = True
            #if ext == "standAlone":
                #self.standAlone = True

    def getShellCommand(self,obj):
        shellCom = obj._extensions['shellCommand']
        if self.noPrompt ==True:
            subprocess.call(shellCom,shell=True)
        else:
            yes = Qt.QMessageBox.Ok
            no = Qt.QMessageBox.Cancel
            result = Qt.QMessageBox.question(self.parent(),"Shell command","Would you like to call shell command '" +shellCom+ "' ?",yes, no)
            if result == yes:
                    subprocess.call(shellCom,shell=True) 

    def getClassName(self,obj):
        clName = obj._extensions['className']
        if clName == 'atkpanel.MainPanel' or clName =="atkpanel":
            #subprocess.Popen(['atkpanel', obj._name])
            self.getAtkPanel(obj)
        elif clName == 'noPanel': 
            #do nothing
            #print "        className = ",clName
            pass
        else:
            if obj._extensions.has_key('classParams'):
                clParam = obj._extensions['classParams']
                self.getClass(clName,clParam,obj._name)
            else:
                self.getClass(clName,obj._name,obj._name)

    def getAtkPanel(self,obj):
        tg_host = os.environ.get('TANGO_HOST')
        #print os.environ.get('JAVALIB')#return None but it should work?
        javalib = '/homelocal/sicilia/lib/java'
        classpath = '%s/atkpanel.jar:%s/ATKCore.jar:%s/ATKWidget.jar:%s/TangORB.jar'%(javalib,javalib,javalib,javalib)
        command = ['/usr/bin/java','-classpath', classpath, '-DTANGO_HOST=%s' % tg_host,'atkpanel.MainPanel',obj._name]
        p = subprocess.Popen(command)
        if self.standAlone == False:
            self.pids.append(p.pid)

    def getClass(self,clName,clParam,objName):
        if clName in globals():
            myclass = globals()[clName]
            #print "The class ",clName, " found in globals!"
        elif clName in locals():
            myclass = locals()[clName]
            #print "The class ",clName, " found in locals!"
        else:
            try:
                myclass = getattr(Qt,clName)
                #print "The class ",clName, " found in Qt!"
            except:
                try:
                    wf = taurus.qt.qtgui.util.TaurusWidgetFactory()
                    myclass = wf.getTaurusWidgetClass(clName)
                    #print "The class ",clName, " found in taurus.widget!"
                except:
                    self.warning( "The class ",clName, "can not be found!\n" + '-'*80)
                    return

        nameclass = myclass()
        try:nameclass.setClasses(clParam)
        except:pass
        try:nameclass.setModel(clParam)
        except:pass
        try: nameclass.setTable(clParam)
        except:pass

        if isinstance(nameclass,Qt.QObject):
            if self.standAlone == False:
                obj = newDialog(self.parent())
            else:
                obj = newDialog()
    
            obj.initComponents(nameclass,objName,clName)
            obj.setModal(False)
            obj.setVisible(True)
            obj.exec_()
        return

    def getTaurusDevicePanel(self,obj):
        try:
            from taurusDevicePanel import taurusDevicePanel
        except:
            from taurusPanel.taurusDevicePanel import taurusDevicePanel
        nameclass = taurusDevicePanel()
        name = "TaurusDevicePanel"
        nameclass.setModel(obj._name)
        nameclass.setSpectraAtkMode(True)
        if self.standAlone == False:
            obj = newDialog(self.parent())
        else:
            obj = newDialog()

        dev_name = None
        obj.initComponents(nameclass,dev_name,name)
        obj.setModal(False)
        obj.setVisible(True)
        obj.exec_()

    def start(self):
        if self.updateThread:
            return
        self.updateQueue = Queue.Queue()
        self.updateThread = TaurusGraphicsUpdateThread(self)
        self.updateThread.start()#Qt.QThread.HighPriority)
    
    def getQueue(self):
        return self.updateQueue
    
    def updateSceneItem(self, item):
        self.updateQueue.put(item)

    def updateSceneItems(self, items):
        self.updateQueue.put(items)

    def updateScene(self):
        self.update()


class TaurusGraphicsItem(TaurusBaseComponent):
    """Base class for all Taurus Graphics Items"""
    
    def __init__(self, name = None, parent = None):
        self._name = name or self.__class__.__name__ #srubio@cells.es: modified to store ._name since initialization (even if a model is not set)
        self.call__init__(TaurusBaseComponent, name, parent)
        self._contextMenu = []
        
    def setContextMenu(self,menu):
        '''Context Menu must be a list of tuples (ActionName,ActionMethod), empty tuples insert separators between options.'''
        self._contextMenu = menu
        
    def contextMenu(self):
        return self._contextMenu
        
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # Mandatory methods to be implemented in any subclass of TaurusComponent
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    def getParentTaurusComponent(self):
        """ Returns a parent Taurus component or None if no parent TaurusBaseComponent 
            is found."""
        p = self.parentItem()
        while p and not isinstance(p, TaurusGraphicsItem):
            p = self.parentItem()
        return p

    #def fireEvent(self, type):
    def fireEvent(self, evt_src = None, evt_type = None, evt_value = None):
        """fires a value changed event to all listeners"""
        self.updateStyle()

    def updateStyle(self):
        """ Method called when the component detects an event that triggers a change
            in the style."""
        if self.scene():
            self.scene().updateSceneItem(self)

    def isReadOnly(self):
        return True

    def __str__(self):
        return self.log_name + "(" + self.modelName + ")"

    def getModelClass(self):
        return taurus.core.TaurusAttribute

class TaurusGraphicsStateItem2(TaurusGraphicsItem):

    def __init__(self, name = None, parent = None):
        name = name or self.__class__.__name__
        self.call__init__(TaurusGraphicsItem, name, parent)
        self._name = None
        self._currFgBrush = None
        self._currBgBrush = None
        self._currText = None
        self._map = None
        self._default = None
        self._visible = None
        self._extensions = None
        self.noTooltip = False
        self.ignoreRepaint = False
        self._currHtmlText = None
        self._unitVisible = True

    def updateStyle(self):
        v = self.getModelValueObj()

        self._currText = self.getDisplayValue()

        if  not self._map is None:
            #print  "    map is not null"
            if list[self._currText] == self._map[1]:
                self.setVisible(self._map[2])
                self._visible = self._map[2]
            else:
                self.setVisible(self._default)
                self._visible = self._default
        #else:
            #print "    map is null"
        TaurusGraphicsItem.updateStyle(self)

    def setModel(self, model):
        model = str(model)    
        self._name = model
        TaurusGraphicsItem.setModel(self, model)        

    def getDisplayValue(self):
        value = None
        try:
            attrvalue = self.getModelValueObj()
            if attrvalue:
                try: value = float(attrvalue.value) and "%.2e" %attrvalue.value
                except: value = "%s"%attrvalue.value
            else: value = self.getNoneValue()
        except Exception,e:
            self.error('Unexpected exception in getDisplayValue:' + str(e))
            self.traceback()
        return value

    def setExtensions(self):
        if self._extensions:
                ExtList = ''
                if self._extensions.has_key('ExtensionsList'):
                    ExtList = self._extensions['ExtensionsList']
                    ExtList = ExtList.split(',')
                    for ext in ExtList:
                        if ext == "noTooltip":
                            self.noTooltip = True
                        if ext == "ignoreRepaint":
                            self.ignoreRepaint = True
                if self.noTooltip == False:
                    self.setToolTip(self._name)
        else:
            self.setToolTip(self._name)

    def setUnitVisible(self,yesno):
        pass

class TaurusGraphicsAttributeItem(TaurusGraphicsItem):

    def __init__(self, name = None, parent = None):
        name = name or self.__class__.__name__
        self.call__init__(TaurusGraphicsItem, name, parent)
        self._currFgBrush = None
        self._currBgBrush = None
        self._currText = None
        self._currHtmlText = None
        self._unitVisible = True
        self._name = None
        self._map = None
        self._default = None
        self._visible = None
        self._extensions = None
        self.noTooltip = False
        self.ignoreRepaint = False
        self._currValue = None

    def getUnit(self):
        unit = ''
        modelObj = self.getModelObj()
        if not modelObj is None:
            unit = modelObj.getUnit() or '-'
        return unit

    def updateStyle(self):
        v = self.getModelValueObj()
        self._currText = self.getDisplayValue()
        
        if self.getShowQuality():
            quality = None
            if v:
                quality = v.quality
            self._currHtmlText = QT_ATTRIBUTE_QUALITY_PALETTE.htmlStyle('TD',quality)
            self._currHtmlText += "<table cellpadding='1'><tr><td class='%s'>%s</td>" % (quality,self._currText)
            if self._unitVisible:
                self._currHtmlText += "<td>%s</td>" % self.getUnit()
            self._currHtmlText += "</tr></table>"
            self._currHtmlText = self._currHtmlText.decode('unicode-escape')
        else:
            self._currText += ' ' + unit
            self._currText = self._currText.decode('unicode-escape')
            self._currHtmlText = self.currText
        
        TaurusGraphicsItem.updateStyle(self)

    def setUnitVisible(self,yesno):
        self._unitVisible = yesno

    def setModel(self, model):
        model = str(model)
        self._name = model
        TaurusGraphicsItem.setModel(self, model)

    def getDisplayValue(self):
        attrvalue = self.getModelValueObj()
        if not attrvalue:
            return self.getNoneValue()
        return str(attrvalue.value)

class TaurusGraphicsStateItem(TaurusGraphicsItem):

    def __init__(self, name = None, parent = None):
        name = name or self.__class__.__name__
        self.call__init__(TaurusGraphicsItem, name, parent)
        self._name = None
        self._currFgBrush = None
        self._currBgBrush = None
        self._currText = None
        self._map = None
        self._default = None
        self._visible = None
        self._extensions = None
        self.noTooltip = False
        self.ignoreRepaint = False

    def updateStyle(self):
        v = self.getModelValueObj()
        if v:
            v = v.value
        self._currText = self.getDisplayValue()
        bg_brush, fg_brush = QT_DEVICE_STATE_PALETTE.qbrush(v)

        if self.getShowQuality():
            self._currBgBrush = bg_brush
            self._currFgBrush = fg_brush
        else:
            self._currBrush = Qt.QBrush(Qt.Qt.NoBrush)

        list = {'ON':0,'OFF':1,'CLOSE':2,'OPEN':3,'INSERT':4,'EXTRACT':5,'MOVING':6,'STANDBY':7,'FAULT':8,'INIT':9,'RUNNING':10,'ALARM':11,'DISABLE':12,'UNKNOWN':13}

        if  not self._map is None:
            if list[self._currText] == self._map[1]:
                self.setVisible(self._map[2])
                self._visible = self._map[2]
            else:
                self.setVisible(self._default)
                self._visible = self._default

        TaurusGraphicsItem.updateStyle(self)

    def setModel(self, model):
        model = str(model)
        self._name = model

        if not model.lower().endswith('/state'):
            model += '/state'

        TaurusGraphicsItem.setModel(self, model)

    def getDisplayValue(self):
        attrvalue = self.getModelValueObj()
        if not attrvalue:
            return self.getNoneValue()
        return str(attrvalue.value)

    def setExtensions(self):
        if self._extensions:
                ExtList = ''
                if self._extensions.has_key('ExtensionsList'):
                    ExtList = self._extensions['ExtensionsList']
                    ExtList = ExtList.split(',')
                    for ext in ExtList:
                        if ext == "noTooltip":
                            self.noTooltip = True
                        if ext == "ignoreRepaint":
                            self.ignoreRepaint = True
                if self.noTooltip == False:
                    self.setToolTip(self._name)
        else:
            self.setToolTip(self._name)

    def setUnitVisible(self,yesno):
        pass

class TaurusEllipseStateItem(Qt.QGraphicsEllipseItem, TaurusGraphicsStateItem):

    def __init__(self, name = None, parent = None, scene = None):
        name = name or self.__class__.__name__
        Qt.QGraphicsEllipseItem.__init__(self, parent, scene)
        self.call__init__(TaurusGraphicsStateItem, name, parent)

    def paint(self,painter,option,widget = None):
        self.setExtensions()
        if self._currBgBrush:
            self.setBrush(self._currBgBrush)
        Qt.QGraphicsEllipseItem.paint(self,painter,option,widget)


class TaurusRectStateItem(Qt.QGraphicsRectItem, TaurusGraphicsStateItem):

    def __init__(self, name = None, parent = None, scene = None):
        name = name or self.__class__.__name__
        Qt.QGraphicsRectItem.__init__(self, parent, scene)
        self.call__init__(TaurusGraphicsStateItem, name, parent)

    def paint(self,painter,option,widget):
        self.setExtensions()
        if self._currBgBrush:
            self.setBrush(self._currBgBrush)
        Qt.QGraphicsRectItem.paint(self,painter,option,widget)

class TaurusGroupStateItem(Qt.QGraphicsItemGroup, TaurusGraphicsStateItem):

    def __init__(self, name = None, parent = None, scene = None):
        name = name or self.__class__.__name__
        Qt.QGraphicsItemGroup.__init__(self, parent, scene)
        self.call__init__(TaurusGraphicsStateItem, name, parent)

    def paint(self,painter,option,widget):
        Qt.QGraphicsItemGroup.paint(self,painter,option,widget)

        
class TaurusPolygonStateItem(Qt.QGraphicsPolygonItem,TaurusGraphicsStateItem):
    
    def __init__(self, name = None, parent = None, scene = None):
        name = name or self.__class__.__name__
        #Qt.QGraphicsRectItem.__init__(self, parent, scene)
        Qt.QGraphicsPolygonItem.__init__(self, parent, scene)
        self.call__init__(TaurusGraphicsStateItem, name, parent)
        
    def paint(self,painter,option,widget):
        self.setExtensions()
        if self._currBgBrush:
            self.setBrush(self._currBgBrush)
        Qt.QGraphicsPolygonItem.paint(self,painter,option,widget)


class TaurusTextStateItem(Qt.QGraphicsTextItem, TaurusGraphicsStateItem):
    
    def __init__(self, name = None, parent = None, scene = None):
        name = name or self.__class__.__name__
        Qt.QGraphicsTextItem.__init__(self, parent, scene)
        self.call__init__(TaurusGraphicsStateItem, name, parent)
        
    def paint(self,painter,option,widget):
        self.setPlainText(self._currText)
        Qt.QGraphicsTextItem.paint(self,painter,option,widget)


class TaurusTextAttributeItem(Qt.QGraphicsTextItem, TaurusGraphicsStateItem2, Qt.QGraphicsRectItem):
    """A QGraphicsItem that represents the text"""
    
    def __init__(self, name = None, parent = None, scene = None):
        name = name or self.__class__.__name__
        Qt.QGraphicsTextItem.__init__(self, parent, scene)
        self.call__init__(TaurusGraphicsStateItem2, name, parent)
        
    def paint(self,painter,option,widget):
        if self._currText:
            text2 = "<body bgcolor='lime' style ='font-size:14px;margin-top:60px;'>"+self._currText+"</font></body>"
            self.setHtml(text2)
        Qt.QGraphicsTextItem.paint(self,painter,option,widget)


import taurus.core

TYPE_TO_GRAPHICS = { 
    None : { "Rectangle"      : Qt.QGraphicsRectItem,
             "RoundRectangle" : Qt.QGraphicsRectItem,
             "Ellipse"        : Qt.QGraphicsEllipseItem,
             "Polyline"       : Qt.QGraphicsPolygonItem,
             "Label"          : Qt.QGraphicsTextItem,
             "Line"           : Qt.QGraphicsLineItem,
             "Group"          : Qt.QGraphicsItemGroup, 
             "SwingObject"    : Qt.QGraphicsRectItem, 
             "Image"          : Qt.QGraphicsPixmapItem, },
             
    taurus.core.TaurusDevice : { "Rectangle"      : TaurusRectStateItem,
                           "RoundRectangle" : TaurusRectStateItem,
                           "Ellipse"        : TaurusEllipseStateItem,
                           "Polyline"       : TaurusPolygonStateItem, 
                           "Label"          : TaurusTextStateItem,
                           "Line"           : Qt.QGraphicsLineItem,
                           "Group"          : TaurusGroupStateItem, 
                           "SwingObject"    : TaurusTextStateItem,
                           "Image"          : Qt.QGraphicsPixmapItem, },

    taurus.core.TaurusAttribute : { "Rectangle"      : Qt.QGraphicsRectItem,
                              "RoundRectangle" : Qt.QGraphicsRectItem,
                              "Ellipse"        : Qt.QGraphicsEllipseItem,
                              "Polyline"       : Qt.QGraphicsPolygonItem, 
                              "Label"          : Qt.QGraphicsTextItem,
                              "Line"           : Qt.QGraphicsLineItem,
                              "Group"          : Qt.QGraphicsItemGroup,
                              "SwingObject"    : TaurusTextAttributeItem,
                              "Image"          : Qt.QGraphicsPixmapItem, },
}


class TaurusBaseGraphicsFactory:
    
    def __init__(self):
        pass
    
    def getSceneObj(self):   
        raise RuntimeError("Invalid call to AbstractGraphicsFactory::getSceneObj()")
    
    def getObj(self,name,params):
        raise RuntimeError("Invalid call to AbstractGraphicsFactory::getObj()")

    def getRectangleObj(self,params):
        raise RuntimeError("Invalid call to AbstractGraphicsFactory::getRectangleObj()")

    def getRoundRectangleObj(self,params):
        raise RuntimeError("Invalid call to AbstractGraphicsFactory::getRoundRectangleObj()")

    def getLineObj(self,params):
        raise RuntimeError("Invalid call to AbstractGraphicsFactory::getLineObj()")
    
    def getEllipseObj(self,params):
        raise RuntimeError("Invalid call to AbstractGraphicsFactory::getEllipseObj()")

    def getPolylineObj(self,params):
        raise RuntimeError("Invalid call to AbstractGraphicsFactory::getPolylineObj()")
    
    def getLabelObj(self,params):
        raise RuntimeError("Invalid call to AbstractGraphicsFactory::getLabelObj()")
    
    def getGroupObj(self,params):
        raise RuntimeError("Invalid call to AbstractGraphicsFactory::getGroupObj()")
    
    def getSwingObjectObj(self,params):
        raise RuntimeError("Invalid call to AbstractGraphicsFactory::getSwingObjectObj()")
    
    def getImageObj(self,parms):
        raise RuntimeError("Invalid call to AbstractGraphicsFactory::getImageObj()")
    
    def getGraphicsClassItem(self,cls,type):
        try:
            if   issubclass(cls, taurus.core.TaurusDevice):    cls = taurus.core.TaurusDevice
            elif issubclass(cls, taurus.core.TaurusAttribute): cls = taurus.core.TaurusAttribute
        except:
            pass
        return TYPE_TO_GRAPHICS.get(cls,TYPE_TO_GRAPHICS.get(None)).get(type)

    def getGraphicsItem(self,type,params):
        name = params.get(self.getNameParam())
        #applying alias
        for k,v in getattr(self,'alias',{}).items():
            if k in name:
                print 'getGraphicsItem(): Replacing %s by %s in %s' % (k,v,name)
                name = str(name).replace(k,v)
                params[self.getNameParam()] = name
        cls = None
        if '/' in name:
            cls = taurus.core.TaurusManager().findObjectClass(name)
        else: 
            if name: self.debug('%s does not match a tango name'%name)
        klass = self.getGraphicsClassItem(cls, type)
        item = klass()
        ## It's here were Attributes are subscribed
        self.set_common_params(item,params)
        return item

    def getNameParam(self):
        """Returns the name of the parameter which contains the name identifier.
           Default implementation returns 'name'.
           Overwrite has necessary."""
        return 'name'
    
    def set_common_params(self,item,params):
        """Sets the common parameters. Default implementation does nothing.
           Overwrite has necessary."""
        pass
    
#if __name__ == "__main__":
#    import sys
#    app = Qt.QApplication(sys.argv)
#    try:
#        from taurusDevicePanel import *
#    except:
#        from taurusPanel.taurusDevicePanel import *
#    cos = taurusDevicePanel()
#    print "ala ma kota"
#    cos.show()
#    sys.exit(app.exec_())
