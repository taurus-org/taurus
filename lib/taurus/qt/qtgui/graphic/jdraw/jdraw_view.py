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

"""This module contains the graphics view widget for jdraw files"""

__all__ = ["TaurusJDrawSynopticsView"]

__docformat__ = 'restructuredtext'

import os
import traceback

from PyQt4 import Qt

from taurus.qt.qtgui.base import TaurusBaseWidget
import jdraw_parser

class TaurusJDrawSynopticsView(Qt.QGraphicsView, TaurusBaseWidget):
    '''
    TaurusJDrawSynopticsView and TaurusGraphicsScene signals/slots
    
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
    __pyqtSignals__ = ("itemsChanged","graphicItemSelected(QString)","graphicSceneClicked(QPoint)")

    def __init__(self, parent = None, designMode = False, updateMode=None, alias = None):
        name = self.__class__.__name__
        self.call__init__wo_kw(Qt.QGraphicsView, parent)
        self.call__init__(TaurusBaseWidget, name, designMode=designMode)
        self._currF = self.modelName
        self.path = ''
        self.w_scene = None
        self.h_scene = None
        self._fileName ="Root"
        self.setInteractive(True)
        self.setAlias(alias)
        
        # By default the items will update the view when necessary.
        # This default value is much more efficient then the QQraphicsView default
        # value, so if you decide to change then expect a lot of processor to be
        # used by your application.
        if updateMode is None:
            self.setViewportUpdateMode(Qt.QGraphicsView.NoViewportUpdate)
        else:
            self.setViewportUpdateMode(updateMode)

    def defineStyle(self):
        self.updateStyle()

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # TaurusBaseWidget over writing
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    def isReadOnly(self):
        return True

    def update(self):
        #self.emit_signal()
        self.emitColors()

    def openJDraw(self):
        ifile = Qt.QFileDialog.getOpenFileName( self, 'Load JDraw File', '', 'JDraw File (*.jdw)')
        if ifile.isEmpty(): return
        if not isinstance(ifile,file):
            #clear TaurusPLot - emit sygnal
            #self.emit(Qt.SIGNAL("clearTaurusPlot"))
            fileName = ifile.split("/")
            #self.emit(Qt.SIGNAL("setTopItemName"),fileName[-1])
            self._fileName = fileName[-1]
            self.setModel(ifile)
        return fileName[-1]
        
    def setAlias(self,alias):
        """ Assigning a dictionary like {'Tag':'Value'} with tags to be replaced in object names while parsing. """
        if (isinstance(alias,dict) or hasattr(alias,'items')) and alias:
            self.alias = alias
        else:
            self.alias = None
        return

    def get_item_list(self):
        return [item._name for item in self.scene().items() if hasattr(item,'_name') and item._name]
    
    def get_item_colors(self,emit = False):
        item_colors = {}
        for item in self.scene().items():
            if not getattr(item,'_name','') or not getattr(item,'_currBgBrush',None):
                continue
            item_colors[item._name] = item._currBgBrush.color().name()
        if emit: self.emit(Qt.SIGNAL("itemsChanged"),self.modelName.split('/')[-1].split('.')[0],item_colors)
        return item_colors
        
    #@Qt.pyqtSignature("selectGraphicItem(QString)")
    @Qt.pyqtSignature("selectGraphicItem(const QString &)")
    def selectGraphicItem(self,item_name):
        self.scene().selectGraphicItem(item_name)
        return False
    
    @Qt.pyqtSignature("graphicItemSelected(QString)")
    def graphicItemSelected(self,item_name):
        self.emit(Qt.SIGNAL("graphicItemSelected(QString)"),item_name)
        
    @Qt.pyqtSignature("graphicSceneClicked(QPoint)")
    def graphicSceneClicked(self,point):
        self.emit(Qt.SIGNAL("graphicSceneClicked(QPoint)"),point)        
        
    
    #@Qt.pyqtSignature("emitColors")
    def emitColors(self): 
        '''emit signal which is used to refresh the tree and colors of icons depend of the current status in jdrawSynoptic'''
        self.get_item_colors(True)

    def resizeEvent(self, event):
        if isinstance(self.parent(),Qt.QScrollArea):
            return
        try:
            if self.parent(): 
                ws = float(self.w_scene or self.width())
                hs = float(self.h_scene or self.height())                
                wp = float(self.parent().width())
                hp =  float(self.parent().height())
                #This correction is needed to avoid "cutting" the borders when the view is small
                wp,hp = wp-min(0.1*wp,30),hp-min(0.1*hp,40)
            else:
                if not hasattr(self,'prevwp'): 
                    #Size is calculated to parent ... if there's no parent or no previous size there's no resize to calcullate!
                    return
                ws,hs = self.prevwp
                wp,hp = float(self.w_scene or self.width()),float(self.h_scene or self.height())
            w =wp/ws
            h = hp/hs
            self.scale(w,h)
            self.w_scene = wp
            self.h_scene = hp
            self.prevwp = (ws,hs)
            self.emitColors()
        except Exception,e:
            self.warning('Exception in JDrawView.resizeEvent: %s' % traceback.format_exc())
            pass

    def refreshModel(self):
        self.setModel(self.getModelName())

    def updateStyle(self):
        self.repaint()

    def getGraphicsFactory(self):
        import jdraw
        return jdraw.TaurusJDrawGraphicsFactory(self,alias=(self.alias or None)) #self.parent())

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # QT properties 
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    @Qt.pyqtSignature("setModel(QString)")
    def setModel(self, model, alias = None):
        self.modelName = str(model)
        self._currF = str(model)
        if alias is not None: self.setAlias(alias)
        if self._currF:
            #filename = str(self._currFile.absoluteFilePath())
            filename = self._currF
            filename = os.path.realpath(filename)
            if os.path.isfile(filename):            
                self.debug("Starting to parse %s" % filename)
                self.path = os.path.dirname(filename)
                factory = self.getGraphicsFactory()
                scene = jdraw_parser.parse(filename, factory)
                if not scene:
                    self.warning("TaurusJDrawSynopticsView.setModel(%s): Unable to parse %s!!!"%(model,filename))
                elif self.w_scene is None and scene.sceneRect():
                    self.w_scene = scene.sceneRect().width()
                    self.h_scene = scene.sceneRect().height()
                else: self.debug('JDrawView.sceneRect() is NONE!!!')
                self.setScene(scene)
                Qt.QObject.connect(self.scene(), Qt.SIGNAL("graphicItemSelected(QString)"), self, Qt.SLOT("graphicItemSelected(QString)"))
                Qt.QObject.connect(self.scene(), Qt.SIGNAL("graphicSceneClicked(QPoint)"), self, Qt.SLOT("graphicSceneClicked(QPoint)"))
                #self.emit_signal()
            else:
                self.setScene(None)
                #self.emit_signal()
            #The emitted signal contains the filename and a dictionary with the name of items and its color
            self.emitColors()#get_item_colors(emit=True)

    def getModel(self):
        return self._currF

    @classmethod
    def getQtDesignerPluginInfo(cls):
        ret = TaurusBaseWidget.getQtDesignerPluginInfo()
        ret['group'] = 'Taurus Display Widgets'
        ret['module'] = 'taurus.qt.qtgui.graphic'
        ret['icon'] = ":/designer/graphicsview.png"
        return ret
    
    model = Qt.pyqtProperty("QString", getModel, setModel)
    
    
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
if __name__ == "__main__":
    import sys
    import taurus.qt.qtgui.graphic
    taurus.setLogLevel(taurus.Info)
    app = Qt.QApplication(sys.argv)
    
    #form = Qt.QDialog()
    #ly=Qt.QVBoxLayout(form)
    #container=Qt.QWidget()
    #ly.addWidget(container)   
    #for m in sys.argv[1:]:
        #tv=TaurusJDrawSynopticsView(container, designMode=False)
        #tv.setModel(m)
        
    form = taurus.qt.qtgui.graphic.TaurusJDrawSynopticsView(designMode=False)
    form.setModel(sys.argv[1])
    
    def kk(*args):print "!!!!!!!!!", args
    form.connect(form,Qt.SIGNAL("graphicItemSelected(QString)"), kk)
    
    SCROLL_BARS_WORK_PROPERLY = True
    if SCROLL_BARS_WORK_PROPERLY:
        panel = Qt.QFrame()
        layout = Qt.QGridLayout()
        layout.addWidget(form)        
        panel.setLayout(layout)    
        panel.show()
    else:
        form.show()
    
    sys.exit(app.exec_())
