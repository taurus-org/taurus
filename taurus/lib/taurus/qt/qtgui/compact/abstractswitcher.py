#!/usr/bin/env python

#############################################################################
##
## This file is part of Taurus, a Tango User Interface Library
## 
## http://www.tango-controls.org/static/taurus/latest/doc/html/index.html
##
## Copyright 2013 CELLS / ALBA Synchrotron, Bellaterra, Spain
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

"""This module provides base classes from which the compact widgets should inherit 
"""

__all__ = ["TaurusReadWriteSwitcher"]

__docformat__ = 'restructuredtext'

from taurus.qt import Qt
from taurus.qt.qtgui.container import TaurusWidget

class TaurusReadWriteSwitcher(TaurusWidget):
    '''
    This is a base class for creating widgets that can switch 
    beetween read and write mode by combining a Taurus widget for reading
    and a Taurus Widget for writing.
    
    For example, if you want to combine a TaurusLabel with a 
    TaurusValueLineEdit, you can implement it as follows::
    
        class MyRWSwitcher(TaurusReadWriteSwitcher):
            readWClass = TaurusLabel
            writeWClass = TaurusValueLineEdit 
            
    The class will normally show the read widget, but it will allow to 
    switch to "edit mode" (where the write widget is shown instead).
    
    The default implementation sets pressing F2 or doubleclicking the read 
    widget as the triggers for entering edit mode, and pressing Escape or 
    losing the focus on the write widget as the triggers for leaving the 
    edit mode. This can be customized in derived classes by changing
    the contents of the `enterEditTriggers` and `exitEditTriggers` class 
    members:
    
        - `enterEditTriggers` is a tuple containing one or more of the following:
        
            - key shortcut (either a Qt.Qt.Key or a QKeySequence)
            - event type on the read widget (a Qt.QEvent.Type)
            - signal from the read widget (a str representing a Signal signature)
        
        - `exitEditTriggers` is a tuple containing one or more of the following:
        
            - key shortcut (either a Qt.Qt.Key or a QKeySequence)
            - event type on the write widget (a Qt.QEvent.Type)
            - signal from the write widget (a str representing a Signal signature)

    #@todo: propagate the pending operations from the writeW
    
    '''    
    readWClass = None
    writeWClass = None
    
    enterEditTriggers = (Qt.Qt.Key_F2, Qt.QEvent.MouseButtonDblClick)
    exitEditTriggers = (Qt.Qt.Key_Escape, Qt.QEvent.FocusOut)

    def __init__(self, parent=None):
        TaurusWidget.__init__(self, parent=parent)
        
        self.setLayout(Qt.QStackedLayout())
        self.readWidget = None
        self.writeWidget = None
        
        #classify the triggers
        sc, et, sig = self._classifyTriggers(self.enterEditTriggers)
        self.enterEditShortCuts = sc
        self.enterEditEventTypes = et
        self.enterEditSignals = sig
        sc, et, sig = self._classifyTriggers(self.exitEditTriggers)
        self.exitEditShortCuts = sc
        self.exitEditEventTypes = et
        self.exitEditSignals = sig
                
        #Actions for entering and exiting the edit
        self.enterEditAction = Qt.QAction("Start Editing", self)
        self.enterEditAction.setShortcuts(self.enterEditShortCuts)
        self.addAction(self.enterEditAction)
        self.exitEditAction = Qt.QAction("Abort Editing", self)
        self.exitEditAction.setShortcuts(self.exitEditShortCuts)
        self.addAction(self.exitEditAction)
        self.connect(self.enterEditAction, Qt.SIGNAL("triggered()"), self._onEnterEditActionTriggered)
        self.connect(self.exitEditAction, Qt.SIGNAL("triggered()"), self._onExitEditActionTriggered)
        
        #add read and write widgets
        if self.readWClass is not None:
            self.setReadWidget(self.readWClass())
        if self.writeWClass is not None:
            self.setWriteWidget(self.writeWClass())
    
    def _classifyTriggers(self, triggers):
        '''classifies the diferent types of triggers
        
        :return: (tuple) a tuple of 3 lists: shortcuts,enventypes,signals
        '''
        shortcuts = []
        eventTypes = []
        signals = []
        for e in triggers:
            if isinstance(e, (Qt.Qt.Key, Qt.QKeySequence)):
                shortcuts.append(Qt.QKeySequence(e))
            elif isinstance(e, Qt.QEvent.Type):
                eventTypes.append(e)
            elif isinstance(e, (basestring, Qt.QString)):
                signals.append(Qt.SIGNAL(e))
            else:
                raise TypeError('Unsupported trigger type: %s'%repr(type(e)))
        return shortcuts, eventTypes, signals
            
    def eventFilter(self, obj, event):
        '''reimplemented to intercept events from the read and write widgets''' 
        if obj is self.readWidget and event.type() in self.enterEditEventTypes:
            self.enterEdit()
            return True # Note that we do not let it propagate further!
        if obj is self.writeWidget and event.type() in self.exitEditEventTypes:
            self.exitEdit()
            return True # Note that we do not let it propagate further!
        #default fallback
        return obj.eventFilter(obj, event)
        
    def setReadWidget(self, widget):
        '''set the read Widget to be used
        
        :param widget: (QWidget) This should be Taurus widget
        '''
        if self.readWidget is not None:
            raise RuntimeError('ReadWidget already set') #@todo: relax this limitation
        self.readWidget = widget
        self.layout().insertWidget(0, self.readWidget)
        self.readWidget.setCursor(Qt.Qt.IBeamCursor)
        self.readWidget.setModel(self.getModelName())
        if self.enterEditEventTypes:
            self.readWidget.installEventFilter(self)
        for sig in self.enterEditSignals:
            self.connect(self.readWidget, sig, self.enterEdit)
    
    def setWriteWidget(self, widget):
        '''set the write Widget to be used
        
        :param widget: (Qt.QWidget) This should be Taurus widget
                       (typically a TaurusBaseWritableWidget)
        '''
        if self.writeWidget is not None:
            raise RuntimeError('WriteWidget already set') #@todo: relax this limitation
        self.writeWidget = widget
        self.layout().insertWidget(1, self.writeWidget)
        self.writeWidget.setModel(self.getModelName())
        if self.exitEditEventTypes:
            self.writeWidget.installEventFilter(self)
        for sig in self.exitEditSignals:
            self.connect(self.writeWidget, sig, self.exitEdit)
        
    def enterEdit(self, *args, **kwargs):
        '''Slot for entering Edit mode
        
        .. note:: args and kwargs are ignored
        ''' 
        self.enterEditAction.trigger()
    
    def exitEdit(self, *args, **kwargs):
        '''Slot for entering Edit mode
        
        .. note:: args and kwargs are ignored
        '''
        self.exitEditAction.trigger()
    
    def _onEnterEditActionTriggered(self):
        self.layout().setCurrentIndex(1)
    
    def _onExitEditActionTriggered(self):
        self.layout().setCurrentIndex(0)
        
    def setModel(self, model):
        '''This implementation propagates the model to the read and write widgets.
        You may reimplement it to do things like passing different models to each.
        '''
        if self.readWidget is not None:
            self.readWidget.setModel(model)
        if self.writeWidget is not None:
            self.writeWidget.setModel(model)
        TaurusWidget.setModel(self, model)


    model = Qt.pyqtProperty("QString", TaurusWidget.getModel,
                            setModel,
                            TaurusWidget.resetModel)

######################################
## This block (and something more would be needed if we decide  
## to implement TaurusReadWriteSwitcher as a TaurusBaseWritableWidget
######################################
#        
#    def setDangerMessage(self, dangerMessage=None):
#        '''propagate to writeWidget'''
#        TaurusWidget.setDangerMessage(self, dangerMessage)
#        try:
#            return self.writeWidget.setDangerMessage(dangerMessage)
#        except AttributeError:
#            pass
#    
#    def setForceDangerousOperations(self, yesno):
#        '''propagate to writeWidget'''
#        TaurusWidget.setForceDangerousOperations(self, yesno)
#        try:
#            return self.writeWidget.setForceDangerousOperations(yesno)
#        except AttributeError:
#            pass
#        
#    def hasPendingOperations(self):
#        '''self.getPendingOperations will always return an empty list, but still
#        self.hasPendingOperations will look at the writeWidget's operations.
#        If you want to ask the TaurusReadWriteSwitcher for its pending operations, call
#        self.writeWidget.getPendingOperations()'''
#        if self.writeWidget is None: return False
#        return self.writeWidget.hasPendingOperations()
#                
#######################################
    

        
def demo1():
    '''Simple demo'''
    import sys
    from taurus.qt.qtgui.application import TaurusApplication
    
    from taurus.qt.qtgui.display import TaurusLabel
    from taurus.qt.qtgui.input import TaurusValueLineEdit
    class DemoSwitcher(TaurusReadWriteSwitcher):
            readWClass = TaurusLabel
            writeWClass = TaurusValueLineEdit 
            exitEditTriggers = ('editingFinished()',Qt.Qt.Key_Escape)

    app = TaurusApplication()
        
    w = DemoSwitcher()
    w.model = "sys/tg_test/1/long_scalar"
    
    w.show()
    sys.exit(app.exec_())

def demo2():
    '''demo of integrability in a form'''
    import sys
    from taurus.qt.qtgui.panel import TaurusForm
    from taurus.qt.qtgui.application import TaurusApplication
    from taurus.qt.qtgui.display import TaurusLabel
    from taurus.qt.qtgui.input import TaurusValueLineEdit
    class DemoSwitcher(TaurusReadWriteSwitcher):
            readWClass = TaurusLabel
            writeWClass = TaurusValueLineEdit 
            exitEditTriggers = ('editingFinished()',Qt.Qt.Key_Escape)

    
    app = TaurusApplication()
    
    f = TaurusForm()
    f.model = ['sys/tg_test/1/long_scalar', 'sys/tg_test/1/long_scalar']
    
    f[0].setReadWidgetClass(DemoSwitcher)
    f[0].setWriteWidgetClass(None)
    
    f.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    #demo1()
    demo2()
    