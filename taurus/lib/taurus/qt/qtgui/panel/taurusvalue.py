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
taurusvalue.py: 
"""

__all__ = ["TaurusValue", "TaurusValuesFrame", "DefaultTaurusValueCheckBox", "DefaultLabelWidget",
           "DefaultUnitsWidget", "TaurusPlotButton", "TaurusArrayEditorButton",
           "TaurusValuesTableButton", "TaurusValuesTableButton_W", "TaurusDevButton"]

__docformat__ = 'restructuredtext'

import weakref
from taurus.qt import Qt
import PyTango
import taurus.core

from taurus.core.taurusbasetypes import TaurusElementType
from taurus.qt.qtcore.mimetypes import TAURUS_ATTR_MIME_TYPE, TAURUS_DEV_MIME_TYPE, TAURUS_MODEL_MIME_TYPE
from taurus.qt.qtcore.configuration import BaseConfigurableClass
from taurus.qt.qtgui.base import TaurusBaseWidget
from taurus.qt.qtgui.container import TaurusFrame
from taurus.qt.qtgui.display import TaurusLabel
from taurus.qt.qtgui.display import TaurusLed
from taurus.qt.qtgui.input import TaurusValueSpinBox, TaurusValueCheckBox
from taurus.qt.qtgui.input import TaurusWheelEdit, TaurusValueLineEdit
from taurus.qt.qtgui.button import TaurusLauncherButton
from taurus.qt.qtgui.util import TaurusWidgetFactory, ConfigurationMenu


class DefaultTaurusValueCheckBox(TaurusValueCheckBox):
    def __init__(self,*args):
        TaurusValueCheckBox.__init__(self,*args)
        self.setShowText(False)

    @classmethod
    def getQtDesignerPluginInfo(cls):
        return None
    
class DefaultLabelWidget(TaurusLabel):
    '''
    The base class used by default for showing the label of a TaurusValue. 
        
    .. note:: It only makes sense to use this class as a part of a TaurusValue,
              since it assumes that it can get a reference to a TaurusValue via 
              the :meth:`getTaurusValueBuddy` member
    '''
    
    _dragEnabled=True
    
    def __init__(self,*args):
        TaurusLabel.__init__(self,*args)
        self.setAlignment(Qt.Qt.AlignRight)
        self.setSizePolicy(Qt.QSizePolicy.Preferred,Qt.QSizePolicy.Maximum)
        self.setBgRole(None)
        self.autoTrim = False
        self.setStyleSheet('DefaultLabelWidget {border-style: solid; border-width: 1px; border-color: transparent; border-radius: 4px;}')
    
    def setModel(self, model):
        if model is None or model=='': 
            return TaurusLabel.setModel(self, None)
        try: config = self.taurusValueBuddy().getLabelConfig()
        except Exception: config = 'label'
        elementtype = self.taurusValueBuddy().getModelType()
        if elementtype == TaurusElementType.Attribute:
            config = self.taurusValueBuddy().getLabelConfig()
            TaurusLabel.setModel(self, model + "?configuration=%s"%config)
        elif elementtype == TaurusElementType.Device:
            TaurusLabel.setModel(self, model + "/state?configuration=dev_alias")
    
    def sizeHint(self):
        return Qt.QSize(Qt.QLabel.sizeHint(self).width(), 18)
    
    def contextMenuEvent(self,event):   
        """ The label widget will be used for handling the actions of the whole TaurusValue
        
        see :meth:`QWidget.contextMenuEvent`"""
        menu = Qt.QMenu(self)  
        menu.addMenu(ConfigurationMenu(self.taurusValueBuddy())) #@todo: This should be done more Taurus-ish 
        if hasattr(self.taurusValueBuddy().writeWidget(), 'resetPendingOperations'):
            r_action = menu.addAction("reset write value",self.taurusValueBuddy().writeWidget().resetPendingOperations)
            r_action.setEnabled(self.taurusValueBuddy().hasPendingOperations())
        if self.taurusValueBuddy().isModifiableByUser():
            menu.addAction("Change label",self.taurusValueBuddy().onChangeLabelConfig)
            menu.addAction("Change Read Widget",self.taurusValueBuddy().onChangeReadWidget)
            cw_action = menu.addAction("Change Write Widget",self.taurusValueBuddy().onChangeWriteWidget)
            cw_action.setEnabled(not self.taurusValueBuddy().isReadOnly()) #disable the action if the taurusValue is readonly
            
        menu.exec_(event.globalPos())
        event.accept()
        
    def getModelMimeData(self):
        '''reimplemented to use the taurusValueBuddy model instead of its own model'''
        mimeData = TaurusLabel.getModelMimeData(self)
        mimeData.setData(TAURUS_MODEL_MIME_TYPE, self.taurusValueBuddy().getModelName())
        if self.taurusValueBuddy().getModelType() == TaurusElementType.Device:
            mimeData.setData(TAURUS_DEV_MIME_TYPE, self.taurusValueBuddy().getModelName())
        elif self.taurusValueBuddy().getModelType() == TaurusElementType.Attribute:
            mimeData.setData(TAURUS_ATTR_MIME_TYPE, self.taurusValueBuddy().getModelName())
        return mimeData
    
    @classmethod
    def getQtDesignerPluginInfo(cls):
        return None


class ExpandingLabel(TaurusLabel):
    '''just a expanding TaurusLabel'''
    def __init__(self,*args):
        TaurusLabel.__init__(self,*args)
        self.setSizePolicy(Qt.QSizePolicy.Expanding, Qt.QSizePolicy.Preferred)


class CenteredLed(TaurusLed):
    '''just a centered TaurusLed'''
    DefaultAlignment = Qt.Qt.AlignHCenter | Qt.Qt.AlignVCenter
        
        
class DefaultUnitsWidget(TaurusLabel):
    def __init__(self,*args):
        TaurusLabel.__init__(self,*args)
        self.setNoneValue('')
        self.setSizePolicy(Qt.QSizePolicy.Preferred,Qt.QSizePolicy.Maximum)
        self.autoTrim = False
        self.setBgRole(None)
    def setModel(self, model):
        if model is None or model=='': 
            return TaurusLabel.setModel(self, None)
        TaurusLabel.setModel(self, model + "?configuration=unit") #@todo: tango-centric!
    def sizeHint(self):
        #print "UNITSSIZEHINT:",Qt.QLabel.sizeHint(self).width(), self.minimumSizeHint().width(), Qt.QLabel.minimumSizeHint(self).width()
        return Qt.QSize(Qt.QLabel.sizeHint(self).width(), 24)
 
    @classmethod
    def getQtDesignerPluginInfo(cls):
        return None
    

class _AbstractTaurusValueButton(TaurusLauncherButton):
    _deleteWidgetOnClose = True
    _text = 'Show'
    def __init__(self, parent = None, designMode = False):
        TaurusLauncherButton.__init__(self, parent = parent, designMode = designMode)
        self.setSizePolicy(Qt.QSizePolicy.Expanding, Qt.QSizePolicy.Maximum)

    @classmethod
    def getQtDesignerPluginInfo(cls):
        return None
    
    
class TaurusPlotButton(_AbstractTaurusValueButton):
    '''A button that launches a TaurusPlot'''
    _widgetClassName = 'TaurusPlot'
    _icon = ':/designer/qwtplot.png'
    

class TaurusArrayEditorButton(_AbstractTaurusValueButton):
    '''A button that launches a TaurusArrayEditor'''
    _widgetClassName = 'TaurusArrayEditor'
    _icon = ':/designer/arrayedit.png'
    _text = 'Edit'
    
    
class TaurusImageButton(_AbstractTaurusValueButton):
    '''A button that launches a TaurusPlot'''
    _widgetClassName = 'TaurusImageDialog'
    _icon = ':/mimetypes/image-x-generic.svg'
    

class TaurusValuesTableButton(_AbstractTaurusValueButton):
    '''A button that launches a TaurusValuesTable'''
    _widgetClassName = 'TaurusValuesTable'
    _icon  = ':/designer/table.png'


class TaurusValuesTableButton_W(TaurusValuesTableButton):
    '''A button that launches a TaurusValuesTable'''
    _text = 'Edit'
    _kwargs={'defaultWriteMode':True}


class TaurusDevButton(_AbstractTaurusValueButton):
    '''A button that launches a TaurusAttrForm'''
    _widgetClassName = 'TaurusDevicePanel'
    _icon = ':/places/folder-remote.svg'
    _text = 'Show Device'


class TaurusStatusLabel(TaurusLabel):
    '''just a taurusLabel but showing the state as its background by default'''
    def __init__(self, parent = None, designMode = False):
        TaurusLabel.__init__(self, parent = parent, designMode = designMode)
        self.setBgRole('state')
        self.setSizePolicy(Qt.QSizePolicy.Expanding,Qt.QSizePolicy.Maximum)
        
    @classmethod
    def getQtDesignerPluginInfo(cls):
        return None


class TaurusValue(Qt.QWidget, TaurusBaseWidget):
    '''
    Internal TaurusValue class
    
    .. warning::
    
        :class:`TaurusValue` (and any derived class from it) should never be instantiated directly. 
        It is designed to be instantiated by a :class:`TaurusForm` class, since it
        breaks some conventions on the way it manages layouts of its parent model.
    '''
    __pyqtSignals__ = ("modelChanged(const QString &)",)
    
    def __init__(self, parent = None, designMode = False, customWidgetMap=None):
        name = self.__class__.__name__
        self.call__init__wo_kw(Qt.QWidget, parent)
        self.call__init__(TaurusBaseWidget, name, designMode=designMode)
        
        self.__modelClass = None
        self._designMode=designMode
        
        #This is a hack to show something usable when in designMode
        if self._designMode:
            layout = Qt.QHBoxLayout(self)
            dummy = ExpandingLabel()
            layout.addWidget(dummy)
            dummy.setUseParentModel(True)
            dummy.setModel("?configuration=attr_fullname") 
            dummy.setPrefixText("< TaurusValue: ")
            dummy.setSuffixText(" >")
        else:
            self.setFixedSize(0,0)
        
        self._labelWidget = None
        self._readWidget = None
        self._writeWidget = None
        self._unitsWidget = None
        self._customWidget = None
        self._extraWidget = None
        
        if customWidgetMap is None:
            customWidgetMap = {}
        self.setCustomWidgetMap(customWidgetMap)
        
        self.labelWidgetClassID = 'Auto'
        self.readWidgetClassID = 'Auto'
        self.writeWidgetClassID = 'Auto'
        self.unitsWidgetClassID = 'Auto'
        self.customWidgetClassID = 'Auto'
        self.extraWidgetClassID = 'Auto'
        self.setPreferredRow(-1)
        self._row = None
        
        self._allowWrite = True
        self._minimumHeight = None
        self._labelConfig = 'label'
        self.setModifiableByUser(False)
        
        if parent is not None:
            self.setParent(parent)
            
        self.registerConfigProperty(self.getLabelConfig, self.setLabelConfig, 'labeConfig')
            
    def setVisible(self, visible):
        for w in (self.labelWidget(), self.readWidget(), self.writeWidget(), self.unitsWidget(), self.customWidget(), self.extraWidget()):
            if w is not None: w.setVisible(visible)
        Qt.QWidget.setVisible(self, visible)
    
    def labelWidget(self):
        return self._labelWidget
    
    def readWidget(self):
        return self._readWidget
    
    def writeWidget(self):
        return self._writeWidget
    
    def unitsWidget(self):
        return self._unitsWidget
    
    def customWidget(self):
        return self._customWidget
    
    def extraWidget(self):
        return self._extraWidget
    
    def setParent(self, parent):
   
        #make sure that the parent has a QGriLayout
        pl=parent.layout()
        if pl is None:
            pl = Qt.QGridLayout(parent) #creates AND sets the parent layout
        if not isinstance(pl, Qt.QGridLayout):
            raise ValueError('layout must be a QGridLayout (got %s)'%type(pl))
        
        if self._row is None:
            self._row = self.getPreferredRow()  #@TODO we should check that the Preferred row is empty in pl
            if self._row < 0:
                self._row = pl.rowCount()
        #print 'ROW:',self, self.getRow()
        
        #insert self into the 0-column
        pl.addWidget(self, self._row, 0) #this widget is invisible (except in design mode)
        
        #Create/update the subwidgets (this also inserts them in the layout)
        if not self._designMode:  #in design mode, no subwidgets are created
            self.updateLabelWidget()
            self.updateReadWidget()
            self.updateWriteWidget()
            self.updateUnitsWidget()
            self.updateExtraWidget()
        
#        self.updateCustomWidget()
        
        #do the base class stuff too    
        Qt.QWidget.setParent(self,parent)
        
    def getAllowWrite(self):
        return self._allowWrite
    
    @Qt.pyqtSignature("setAllowWrite(bool)")
    def setAllowWrite(self, mode):
        self._allowWrite = mode
    
    def resetAllowWrite(self):
        self._allowWrite = True
    
    def getPreferredRow(self):
        return self._preferredRow
    
    @Qt.pyqtSignature("setPreferredRow(int)")
    def setPreferredRow(self,row):
        self._preferredRow=row
        
    def resetPreferredRow(self):
        self.setPreferredRow(-1)
        
    def getRow(self):
        return self._row
    
    def setMinimumHeight(self, minimumHeight):
        self._minimumHeight = minimumHeight
        
    def minimumHeight(self):
        return self._minimumHeight
    
    def getDefaultLabelWidgetClass(self):
        return DefaultLabelWidget
     
    def getDefaultReadWidgetClass(self, returnAll=False):
        '''
        Returns the default class (or classes) to use as read widget for the
        current model.
        
        :param returnAll: (bool) if True, the return value is a list of valid
                          classes instead of just one class
        
        :return: (class or list<class>) the default class  to use for the read
                 widget (or, if returnAll==True, a list of classes that can show
                 the attribute ). If a list is returned, it will be loosely
                 ordered by preference, being the first element always the
                 default one.
        '''
        modelobj = self.getModelObj()
        if modelobj is None: 
            if returnAll: return [ExpandingLabel]
            else: return ExpandingLabel
        
        modeltype = self.getModelType()
        if  modeltype == TaurusElementType.Attribute:
            ##The model is an attribute
            config = modelobj.getConfig()
            #print "---------ATTRIBUTE OBJECT:----------\n",modelobj.read()
            try: configType = config.getType()
            except: configType = None
            try:
                if config.isBoolean():
                    result = [CenteredLed, ExpandingLabel]
            except:
                pass
            if config.isScalar():
                if  configType == PyTango.ArgType.DevBoolean:
                    result = [CenteredLed, ExpandingLabel]
                elif configType == PyTango.ArgType.DevState:
                    result = [CenteredLed, ExpandingLabel]
                elif str(self.getModel()).lower().endswith('/status'): #@todo: tango-centric!!
                    result = [TaurusStatusLabel, ExpandingLabel]
                else:
                    result = [ExpandingLabel]
            elif config.isSpectrum():
                if PyTango.is_numerical_type(configType): #@todo: tango-centric!!
                    result = [TaurusPlotButton, TaurusValuesTableButton, ExpandingLabel]
                else:
                    result = [TaurusValuesTableButton, ExpandingLabel]
            elif config.isImage():
                if PyTango.is_numerical_type(configType): #@todo: tango-centric!!
                    try: 
                        from taurus.qt.qtgui.extra_guiqwt import TaurusImageDialog #unused import but useful to determine if TaurusImageButton should be added
                        result = [TaurusImageButton, TaurusValuesTableButton, ExpandingLabel]
                    except ImportError:
                        result = [TaurusValuesTableButton, ExpandingLabel]
                else:
                    result = [TaurusValuesTableButton, ExpandingLabel]
            else:
                self.warning('Unsupported attribute type %s'%configType)
                result = None

        elif modeltype == TaurusElementType.Device:
            result = [TaurusDevButton]
        else:
            msg = "Unsupported model type ('%s')"%modeltype
            self.warning(msg)
            raise ValueError(msg)

            
        if returnAll: return result
        else: return result[0]
        
    def getDefaultWriteWidgetClass(self, returnAll=False):
        '''
        Returns the default class (or classes) to use as write widget for the
        current model.
        
        :param returnAll: (bool) if True, the return value is a list of valid
                          classes instead of just one class
        
        :return: (class or list<class>) the default class  to use for the write
                 widget (or, if returnAll==True, a list of classes that can show
                 the attribute ). If a list is returned, it will be loosely
                 ordered by preference, being the first element always the
                 default one.
        '''
        modelclass = self.getModelClass()
        if self.isReadOnly() or (modelclass and modelclass.getTaurusElementType() != TaurusElementType.Attribute):
            if returnAll: return []
            else: return None
        modelobj = self.getModelObj()
        if modelobj is None:
            if returnAll: return [TaurusValueLineEdit]
            else: return TaurusValueLineEdit
        config = modelobj.getConfig()
        if config.isScalar():
            configType = config.getType() 
            if configType == PyTango.ArgType.DevBoolean:
                result = [DefaultTaurusValueCheckBox, TaurusValueLineEdit]
            #elif PyTango.is_numerical_type(configType ):
            #    result = TaurusWheelEdit
            else:
                result = [TaurusValueLineEdit, TaurusValueSpinBox, TaurusWheelEdit]
        elif config.isSpectrum():
            configType = config.getType()
            if configType in (PyTango.ArgType.DevDouble, PyTango.ArgType.DevFloat, 
                              PyTango.ArgType.DevInt, PyTango.ArgType.DevLong, 
                              PyTango.ArgType.DevLong64, PyTango.ArgType.DevShort, 
                              PyTango.ArgType.DevULong, PyTango.ArgType.DevULong64, 
                              PyTango.ArgType.DevUShort):
                result = [TaurusArrayEditorButton, TaurusValuesTableButton_W, TaurusValueLineEdit]
            else:
                result = [TaurusValuesTableButton_W, TaurusValueLineEdit]
        elif config.isImage():
            result = [TaurusValuesTableButton_W]
        else:
            self.debug('Unsupported attribute type for writing: %s'% str(config.getType()))
            result = [None]
            
        if returnAll: return result
        else: return result[0]
    
    def getDefaultUnitsWidgetClass(self):
#        if self.getModelClass() != taurus.core.taurusattribute.TaurusAttribute:
#            return DefaultUnitsWidget
        return DefaultUnitsWidget
    
    def getDefaultCustomWidgetClass(self):
        modelclass = self.getModelClass()
        if modelclass and modelclass.getTaurusElementType() != TaurusElementType.Attribute:
            return None
        try:
            key = self.getModelObj().getHWObj().info().dev_class
        except:
            return None
        return self.getCustomWidgetMap().get(key, None)
    
    def getDefaultExtraWidgetClass(self):
        return None
    
    def setCustomWidgetMap(self, cwmap):
        '''Sets a map map for custom widgets.
        
        :param cwmap: (dict<str,Qt.QWidget>) a dictionary whose keys are device
                      class strings (see :class:`PyTango.DeviceInfo`) and
                      whose values are widget classes to be used
        '''
        self._customWidgetMap = cwmap
        
    def getCustomWidgetMap(self):
        '''Returns the map used to create custom widgets.
        
        :return: (dict<str,Qt.QWidget>) a dictionary whose keys are device
                 type strings (i.e. see :class:`PyTango.DeviceInfo`) and whose
                 values are widgets to be used
        '''
        return self._customWidgetMap
     
    def onChangeLabelConfig(self):
        keys = ['label', 'attr_name', 'attr_fullname', 'dev_alias', 'dev_name', 'dev_fullname']
        try:
            current = keys.index(self.labelConfig)
        except:
            current= len(keys)
            keys.append(self.labelConfig)
            
        msg = 'Choose new source for the label. \n'+\
              'You can also write a more complex text\n'+\
              'using any of the proposed sources as a\n'+\
              'placeholder by enclosing it in "< >" brackets'
        labelConfig, ok = Qt.QInputDialog.getItem(self, 'Change Label', msg, keys, current, True)
        if ok:
            self.labelConfig=str(labelConfig)  
             
    def onChangeReadWidget(self):
        classnames = ['None', 'Auto']+[c.__name__ for c in self.getDefaultReadWidgetClass(returnAll=True)]
        cname, ok = Qt.QInputDialog.getItem(self, 'Change Read Widget', 'Choose a new read widget class', classnames, 1, True)
        if ok:
            self.setReadWidgetClass(str(cname))
            
    def onChangeWriteWidget(self):
        classnames = ['None', 'Auto']+[c.__name__ for c in self.getDefaultWriteWidgetClass(returnAll=True)]
        cname, ok = Qt.QInputDialog.getItem(self, 'Change Write Widget', 'Choose a new write widget class', classnames, 1, True)
        if ok:
            self.setWriteWidgetClass(str(cname))

    def _destroyWidget(self, widget):
        '''get rid of a widget in a safe way'''
        widget.hide()
        widget.setParent(None)
        if hasattr(widget,'setModel'):
            widget.setModel(None)
        # COULD NOT INVESTIGATE DEEPER, BUT THE STARTUP-HANGING
        # HAPPENS WITH SOME SIGNALS RELATED WITH THE LINEEDIT...
        # MAYBE OTHER 'WRITE WIDGETS' HAVE THE SAME PROBLEM ?!?!?!
        if isinstance(widget, Qt.QLineEdit):
            widget.blockSignals(True)
        # THIS HACK REDUCES THE STARTUP-HANGING RATE
        widget.deleteLater()
        
    def _newSubwidget(self, oldWidget, newClass):
        '''eliminates oldWidget and returns a new one.
        If newClass is None, None is returned
        If newClass is the same as the olWidget class, nothing happens'''
        if oldWidget.__class__ == newClass: return oldWidget
        if oldWidget is not None:
            self._destroyWidget(oldWidget)
        if newClass is None: result = None
        else: result = newClass()
        return result

    def labelWidgetClassFactory(self, classID):
        if self._customWidget is not None: return None
        if classID is None or classID == 'None': return None
        if isinstance(classID, type): return classID
        elif str(classID) == 'Auto': return self.getDefaultLabelWidgetClass()
        else: return TaurusWidgetFactory().getTaurusWidgetClass(classID)

    def readWidgetClassFactory(self, classID):
        if self._customWidget is not None: return None
        if classID is None or classID == 'None': return None
        if isinstance(classID, type): return classID
        elif str(classID) == 'Auto': return self.getDefaultReadWidgetClass()
        else: return TaurusWidgetFactory().getTaurusWidgetClass(classID)
    
    def writeWidgetClassFactory(self, classID):
        if self._customWidget is not None: return None
        if classID is None or classID == 'None': return None
        if isinstance(classID, type): return classID
        elif str(classID) == 'Auto': return self.getDefaultWriteWidgetClass()
        else: return TaurusWidgetFactory().getTaurusWidgetClass(classID)
        
    def unitsWidgetClassFactory(self, classID):
        if self._customWidget is not None: return None
        if classID is None or classID == 'None': return None
        if isinstance(classID, type): return classID
        elif str(classID) == 'Auto': return self.getDefaultUnitsWidgetClass()
        else: return TaurusWidgetFactory().getTaurusWidgetClass(classID)
        
    def customWidgetClassFactory(self, classID):
        if classID is None or classID == 'None': return None
        if isinstance(classID, type): return classID
        elif str(classID) == 'Auto': return self.getDefaultCustomWidgetClass()
        else: return TaurusWidgetFactory().getTaurusWidgetClass(classID)
        
    def extraWidgetClassFactory(self, classID):
        if self._customWidget is not None: return None
        if classID is None or classID == 'None': return None
        if isinstance(classID, type): return classID
        elif str(classID) == 'Auto': return self.getDefaultExtraWidgetClass()
        else: return TaurusWidgetFactory().getTaurusWidgetClass(classID)
        
    def updateLabelWidget(self):
        #get the class for the widget and replace it if necessary
        klass = self.labelWidgetClassFactory(self.labelWidgetClassID)
        self._labelWidget = self._newSubwidget(self._labelWidget, klass)
        
        #take care of the layout
        self.addLabelWidgetToLayout() 
        
        if self._labelWidget is not None:
            #give the new widget a reference to its buddy TaurusValue object
            self._labelWidget.taurusValueBuddy = weakref.ref(self) 
            
            #tweak the new widget
            if self.minimumHeight() is not None:
                self._labelWidget.setMinimumHeight(self.minimumHeight())
            
            #set the model for the subwidget
            if hasattr(self._labelWidget,'setModel'):
                self._labelWidget.setModel(self.getModelName())
            
    def updateReadWidget(self):
        #get the class for the widget and replace it if necessary
        try:
            klass = self.readWidgetClassFactory(self.readWidgetClassID)
            self._readWidget = self._newSubwidget(self._readWidget, klass)
        except Exception,e:
            self._destroyWidget(self._readWidget)
            self._readWidget = Qt.QLabel('[Error]')
            msg='Error creating read widget:\n'+str(e)
            self._readWidget.setToolTip(msg)
            self.debug(msg)
            #self.traceback(30) #warning level=30
        
        #take care of the layout
        self.addReadWidgetToLayout() 
        
        if self._readWidget is not None:
            #give the new widget a reference to its buddy TaurusValue object
            self._readWidget.taurusValueBuddy = weakref.ref(self)
            
            #tweak the new widget
            if self.minimumHeight() is not None:
                self._readWidget.setMinimumHeight(self.minimumHeight())
            
            #set the model for the subwidget
            if hasattr(self._readWidget,'setModel'):
                self._readWidget.setModel(self.getModelName())

    def updateWriteWidget(self):
        #get the class for the widget and replace it if necessary
        klass = self.writeWidgetClassFactory(self.writeWidgetClassID)
        self._writeWidget = self._newSubwidget(self._writeWidget, klass)
        
        #take care of the layout
        self.addReadWidgetToLayout() #this is needed because the writeWidget affects to the readWritget layout
        self.addWriteWidgetToLayout()
        
        if self._writeWidget is not None:
            #give the new widget a reference to its buddy TaurusValue object
            self._writeWidget.taurusValueBuddy = weakref.ref(self)
            
            #tweak the new widget
            ##hide getPendingOperations of the writeWidget so that containers don't get duplicate lists
            #self._writeWidget._getPendingOperations = self._writeWidget.getPendingOperations 
            #self._writeWidget.getPendingOperations = lambda : [] 
            self.connect(self._writeWidget, Qt.SIGNAL('valueChanged'),self.updatePendingOpsStyle)
            self._writeWidget.setDangerMessage(self.getDangerMessage())
            self._writeWidget.setForceDangerousOperations(self.getForceDangerousOperations())
            if self.minimumHeight() is not None:
                self._writeWidget.setMinimumHeight(self.minimumHeight())
            
            #set the model for the subwidget
            if hasattr(self._writeWidget,'setModel'):
                self._writeWidget.setModel(self.getModelName())
        
    def updateUnitsWidget(self):
        #get the class for the widget and replace it if necessary
        klass = self.unitsWidgetClassFactory(self.unitsWidgetClassID)
        self._unitsWidget = self._newSubwidget(self._unitsWidget, klass)
        
        #take care of the layout
        self.addUnitsWidgetToLayout() 
        
        if self._unitsWidget is not None:
            #give the new widget a reference to its buddy TaurusValue object
            self._unitsWidget.taurusValueBuddy = weakref.ref(self)
            #tweak the new widget
            if self.minimumHeight() is not None:
                self._unitsWidget.setMinimumHeight(self.minimumHeight())
            
            #set the model for the subwidget
            if hasattr(self._unitsWidget,'setModel'):
                self._unitsWidget.setModel(self.getModelName())
                
    def updateCustomWidget(self):
        #get the class for the widget and replace it if necessary
        klass = self.customWidgetClassFactory(self.customWidgetClassID)
        self._customWidget = self._newSubwidget(self._customWidget, klass)
        
        #take care of the layout
        self.addCustomWidgetToLayout()
        
        if self._customWidget is not None:            
            #set the model for the subwidget
            if hasattr(self._customWidget,'setModel'):
                self._customWidget.setModel(self.getModelName())
                
    def updateExtraWidget(self):
        #get the class for the widget and replace it if necessary
        klass = self.extraWidgetClassFactory(self.extraWidgetClassID)
        self._extraWidget = self._newSubwidget(self._extraWidget, klass)
        
        #take care of the layout
        self.addExtraWidgetToLayout() 
        
        if self._extraWidget is not None:
            #give the new widget a reference to its buddy TaurusValue object
            self._extraWidget.taurusValueBuddy = weakref.ref(self)
                        
            #set the model for the subwidget
            if hasattr(self._extraWidget,'setModel'):
                self._extraWidget.setModel(self.getModelName())
                
                
    def addLabelWidgetToLayout(self):
        
        if self._labelWidget is not None and self.parent() is not None:
            self.parent().layout().addWidget(self._labelWidget, self._row, 1)
    
    def addReadWidgetToLayout(self):
        if self._readWidget is not None and self.parent() is not None: 
            if self._writeWidget is None:
                self.parent().layout().addWidget(self._readWidget, self._row, 2,1,2)
            else:
                self.parent().layout().addWidget(self._readWidget, self._row, 2)
    
    def addWriteWidgetToLayout(self):
        if self._writeWidget is not None and self.parent() is not None:
            self.parent().layout().addWidget(self._writeWidget, self._row, 3)
    
    def addUnitsWidgetToLayout(self):
        if self._unitsWidget is not None and self.parent() is not None:
            self.parent().layout().addWidget(self._unitsWidget, self._row, 4)
            
    def addCustomWidgetToLayout(self):
        if self._customWidget is not None and self.parent() is not None:
            self.parent().layout().addWidget(self._customWidget, self._row, 1,1,-1)
    
    def addExtraWidgetToLayout(self):
        if self._extraWidget is not None and self.parent() is not None:
            self.parent().layout().addWidget(self._extraWidget, self._row, 5)

    @Qt.pyqtSignature("parentModelChanged(const QString &)")
    def parentModelChanged(self, parentmodel_name):
        """Invoked when the parent model changes
        
        :param parentmodel_name: (str) the new name of the parent model
        """
        TaurusBaseWidget.parentModelChanged(self, parentmodel_name)
        if not self._designMode:     #in design mode, no subwidgets are created
            self.updateCustomWidget()
            self.updateLabelWidget()
            self.updateReadWidget()
            self.updateWriteWidget()
            self.updateUnitsWidget()
            self.updateExtraWidget()

    @Qt.pyqtSignature("setLabelWidget(QString)")
    def setLabelWidgetClass(self,classID):
        '''substitutes the current widget by a new one. classID can be one of:
        None, 'Auto', a TaurusWidget class name, or any class'''
        self.labelWidgetClassID = classID
        self.updateLabelWidget()
            
    def getLabelWidgetClass(self):
        return self.labelWidgetClassID
    
    def resetLabelWidgetClass(self):
        self.labelWidgetClassID = 'Auto'
    
    @Qt.pyqtSignature("setReadWidget(QString)")
    def setReadWidgetClass(self,classID):
        '''substitutes the current widget by a new one. classID can be one of:
        None, 'Auto', a TaurusWidget class name, or any class'''
        self.readWidgetClassID = classID
        self.updateReadWidget()
            
    def getReadWidgetClass(self):
        return self.readWidgetClassID
    
    def resetReadWidgetClass(self):
        self.readWidgetClassID = 'Auto'
        
    @Qt.pyqtSignature("setWriteWidget(QString)")
    def setWriteWidgetClass(self,classID):
        '''substitutes the current widget by a new one. classID can be one of:
        None, 'Auto', a TaurusWidget class name, or any class'''
        self.writeWidgetClassID = classID
        self.updateWriteWidget()
    
    def getWriteWidgetClass(self):
        return self.writeWidgetClassID
    
    def resetWriteWidgetClass(self):
        self.writeWidgetClassID = 'Auto'
        
    @Qt.pyqtSignature("setUnitsWidget(QString)")
    def setUnitsWidgetClass(self,classID):
        '''substitutes the current widget by a new one. classID can be one of:
        None, 'Auto', a TaurusWidget class name, or any class'''
        self.unitsWidgetClassID = classID
        self.updateUnitsWidget()
    
    def getUnitsWidgetClass(self):
        return self.unitsWidgetClassID
    
    def resetUnitsWidgetClass(self):
        self.unitsWidgetClassID = 'Auto'
    
    @Qt.pyqtSignature("setCustomWidget(QString)")
    def setCustomWidgetClass(self,classID):
        '''substitutes the current widget by a new one. classID can be one of:
        None, 'Auto', a TaurusWidget class name, or any class'''
        self.customWidgetClassID = classID
        self.updateCustomWidget()
    
    def getCustomWidgetClass(self):
        return self.customWidgetClassID
    
    def resetCustomWidgetClass(self):
        self.customWidgetClassID = 'Auto'
        
    @Qt.pyqtSignature("setExtraWidget(QString)")
    def setExtraWidgetClass(self,classID):
        '''substitutes the current widget by a new one. classID can be one of:
        None, 'Auto', a TaurusWidget class name, or any class'''
        self.extraWidgetClassID = classID
        self.updateExtraWidget()
    
    def getExtraWidgetClass(self):
        return self.extraWidgetClassID
    
    def resetExtraWidgetClass(self):
        self.extraWidgetClassID = 'Auto'
        
    def isReadOnly(self):
        if not self.getAllowWrite(): return True 
        modelObj = self.getModelObj()
        if modelObj is None: return False 
        return not modelObj.isWritable()

    def getModelClass(self):
        return self.__modelClass

#    def destroy(self):
#        if not self._designMode:
#            for w in [self._labelWidget, self._readWidget, self._writeWidget, self._unitsWidget, self._extraWidget]:
#                if isinstance(w,Qt.QWidget):
#                    w.setParent(self)   #reclaim the parental rights over subwidgets before destruction
#        Qt.QWidget.setParent(self,None)
#        Qt.QWidget.destroy(self)

    def createConfig(self, allowUnpickable=False):
        '''
        extending  :meth:`TaurusBaseWidget.createConfig` to store also the class names for subwidgets
               
        :param alllowUnpickable:  (bool) 
        
        :return: (dict<str,object>) configurations (which can be loaded with :meth:`applyConfig`).
        
        .. seealso: :meth:`TaurusBaseWidget.createConfig`, :meth:`applyConfig` 
        '''
        configdict = TaurusBaseWidget.createConfig(self, allowUnpickable=allowUnpickable)
        #store the subwidgets classIDs and configs
        for key in ('LabelWidget', 'ReadWidget', 'WriteWidget', 'UnitsWidget', 'CustomWidget', 'ExtraWidget'):
            classID = getattr(self, 'get%sClass'%key)() # calls self.getLabelWidgetClass, self.getReadWidgetClass,...
            if isinstance(classID, (str, Qt.QString)) or allowUnpickable:
                #configdict[key] = classID
                configdict[key] = {'classid':classID}
                widget = getattr(self, key[0].lower()+key[1:])()
                if isinstance(widget, BaseConfigurableClass):
                    configdict[key]['delegate'] = widget.createConfig()
            else:
                self.info('createConfig: %s not saved because it is not Pickable (%s)'%(key, str(classID)))

        return configdict
    
    def applyConfig(self, configdict, **kwargs):
        """extending :meth:`TaurusBaseWidget.applyConfig` to restore the subwidget's classes
        
        :param configdict: (dict)
        
        .. seealso:: :meth:`TaurusBaseWidget.applyConfig`, :meth:`createConfig`
        """
        #first do the basic stuff...
        TaurusBaseWidget.applyConfig(self, configdict, **kwargs)
        #restore the subwidgets classIDs
        for key in ('LabelWidget', 'ReadWidget', 'WriteWidget', 'UnitsWidget', 'CustomWidget', 'ExtraWidget'):
            if key in configdict:
                widget_configdict = configdict[key]
                getattr(self, 'set%sClass'%key)(widget_configdict.get('classid', None))
                if widget_configdict.has_key('delegate'):
                    widget = getattr(self, key[0].lower()+key[1:])()
                    if isinstance(widget, BaseConfigurableClass):
                        widget.applyConfig(widget_configdict['delegate'], **kwargs)
                
    @Qt.pyqtSignature("setModel(QString)")
    def setModel(self, model):
        """extending :meth:`TaurusBaseWidget.setModel` to change the modelclass
        dynamically and to update the subwidgets"""
        self.__modelClass = taurus.Manager().findObjectClass(model or '')
        TaurusBaseWidget.setModel(self,model)
        if not self._designMode:     #in design mode, no subwidgets are created
            self.updateCustomWidget()
            self.updateLabelWidget()
            self.updateReadWidget()
            self.updateWriteWidget()
            self.updateUnitsWidget()
            self.updateExtraWidget()
            
    def handleEvent(self, evt_src, evt_type, evt_value):
        """Reimplemented from :meth:`TaurusBaseWidget.handleEvent` 
        to update subwidgets on config events
        """
        if evt_type == taurus.core.taurusbasetypes.TaurusEventType.Config and not self._designMode:
            self.updateCustomWidget()
            self.updateLabelWidget()
            self.updateReadWidget()
            self.updateWriteWidget()
            self.updateUnitsWidget()
            self.updateExtraWidget()
            
    def isValueChangedByUser(self):
        try:
            return self._writeWidget.isValueChangedByUser()
        except AttributeError:
            return False
    
    def setDangerMessage(self, dangerMessage=None):
        TaurusBaseWidget.setDangerMessage(self, dangerMessage)
        try:
            return self._writeWidget.setDangerMessage(dangerMessage)
        except AttributeError:
            pass
    
    def setForceDangerousOperations(self, yesno):
        TaurusBaseWidget.setForceDangerousOperations(self, yesno)
        try:
            return self._writeWidget.setForceDangerousOperations(yesno)
        except AttributeError:
            pass
        
    def hasPendingOperations(self):
        '''self.getPendingOperations will always return an empty list, but still
        self.hasPendingOperations will look at the writeWidget's operations.
        If you want to ask the TaurusValue for its pending operations, call
        self.writeWidget().getPendingOperations()'''
        w = self.writeWidget()
        if w is None: return False
        return w.hasPendingOperations()
                
    def updatePendingOpsStyle(self):
        if self._labelWidget is None: return
        if self.hasPendingOperations():
            self._labelWidget.setStyleSheet(
                '%s {border-style: solid ; border-width: 1px; border-color: blue; color: blue; border-radius:4px;}'%self._labelWidget.__class__.__name__)
        else:
            self._labelWidget.setStyleSheet(
                '%s {border-style: solid; border-width: 1px; border-color: transparent; color: black;  border-radius:4px;}'%self._labelWidget.__class__.__name__)
            
    def getLabelConfig(self):
        return self._labelConfig
    
    @Qt.pyqtSignature("setLabelConfig(QString)")
    def setLabelConfig(self, config):
        self._labelConfig = config
        self.updateLabelWidget()
        
    def resetLabelConfig(self):
        self._labelConfig = 'label'
        self.updateLabelWidget()
    
    @classmethod
    def getQtDesignerPluginInfo(cls):
        return None
        #ret = TaurusBaseWidget.getQtDesignerPluginInfo()
        #ret['module'] = 'taurus.qt.qtgui.panel'
        #ret['icon'] = ":/designer/label.png"
        #return ret
        
    ########################################################
    ## Qt properties (for designer)
    model = Qt.pyqtProperty("QString", TaurusBaseWidget.getModel,  setModel, TaurusBaseWidget.resetModel)
    preferredRow = Qt.pyqtProperty("int", getPreferredRow, setPreferredRow, resetPreferredRow)
    labelWidgetClass = Qt.pyqtProperty("QString", getLabelWidgetClass, setLabelWidgetClass, resetLabelWidgetClass)
    readWidgetClass = Qt.pyqtProperty("QString", getReadWidgetClass, setReadWidgetClass, resetReadWidgetClass)
    writeWidgetClass = Qt.pyqtProperty("QString", getWriteWidgetClass, setWriteWidgetClass, resetWriteWidgetClass)
    unitsWidgetClass = Qt.pyqtProperty("QString", getUnitsWidgetClass, setUnitsWidgetClass, resetUnitsWidgetClass)
    extraWidgetClass = Qt.pyqtProperty("QString", getExtraWidgetClass, setExtraWidgetClass, resetExtraWidgetClass)
    labelConfig = Qt.pyqtProperty("QString", getLabelConfig, setLabelConfig, resetLabelConfig)
    allowWrite = Qt.pyqtProperty("bool", getAllowWrite, setAllowWrite, resetAllowWrite)
    modifiableByUser = Qt.pyqtProperty("bool", TaurusBaseWidget.isModifiableByUser, TaurusBaseWidget.setModifiableByUser, TaurusBaseWidget.resetModifiableByUser)


class TaurusValuesFrame(TaurusFrame):
    '''This is a container specialized into containing TaurusValue widgets.
    It should be used Only for TaurusValues'''
    
    _model = []
    @Qt.pyqtSignature("setModel(QStringList)")    
    def setModel(self, model):
        self._model = model
        for tv in self.getTaurusValues():
            tv.destroy()
        for m in self._model:
            taurusvalue = TaurusValue(self, self.designMode)
            taurusvalue.setMinimumHeight(20)
            taurusvalue.setModel(str(m))
            taurusvalue.setModifiableByUser(self.isModifiableByUser())
    def getModel(self):
        return self._model
                
    def resetModel(self):
        self.setModel([])
    
    def getTaurusValueByIndex(self, index):
        '''returns the TaurusValue item at the given index position'''
        return self.getTaurusValues()[index]
    
    def getTaurusValues(self):
        '''returns the list of TaurusValue Objects contained by this frame'''
        return [obj for obj in self.children() if isinstance(obj,TaurusValue)]
    
    @classmethod
    def getQtDesignerPluginInfo(cls):
        '''we don't want this widget in designer'''
        return None  
    

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # QT properties 
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
   
    model = Qt.pyqtProperty("QStringList", getModel, setModel, resetModel)


#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
if __name__ == "__main__":
    
    import sys

    app = Qt.QApplication(sys.argv)
    form = Qt.QMainWindow()
    #ly=Qt.QVBoxLayout(form)
    #container=Qt.QWidget()
#    container = TaurusValuesFrame()
    from taurus.qt.qtgui.panel import TaurusForm
    container = TaurusForm()
    #ly.addWidget(container)
    form.setCentralWidget(container)

    try:
        from taurus.qt.qtgui.extra_pool import PoolMotorSlim, PoolChannel
        container.setCustomWidgetMap({'SimuMotor':PoolMotorSlim,
                                'Motor':PoolMotorSlim,
                                'PseudoMotor':PoolMotorSlim,
                                'PseudoCounter':PoolChannel,
                                'CTExpChannel':PoolChannel,
                                'ZeroDExpChannel':PoolChannel,
                                'OneDExpChannel':PoolChannel,
                                'TwoDExpChannel':PoolChannel})
    except:
        pass
    
    ##set a model list  
    if len(sys.argv)>1:
        models=sys.argv[1:]
        container.setModel(models)
    else:
        models = []
        
    #models assigned for debugging.... comment out when releasing
    #models=['bl97/pc/dummy-01/Current','bl97/pysignalsimulator/1/value1','bl97/pc/dummy-02/RemoteMode','bl97/pc/dummy-02/CurrentSetpoint','bl97/pc/dummy-02/Current']
    #models=['bl97/pc/dummy-01/Current']
    #models=['bl97/pc/dummy-01/CurrentSetpoint','bl97/pc/dummy-02/Current','bl97/pc/dummy-02/RemoteMode','bl97/pysignalsimulator/1/value1']
    #models=['bl97/pc/dummy-01/CurrentSetpoint','bl97/pc/dummy-02/RemoteMode']
    #models=['sys/tg_test/1/state','sys/tg_test/1/status','sys/tg_test/1/short_scalar','sys/tg_test/1']
    #models =  ['sys/tg_test/1']+['sys/tg_test/1/%s_scalar'%s for s in ('float','short','string','long','boolean') ]
    #models =  ['sys/tg_test/1/float_scalar','sys/tg#_test/1/double_scalar']
    
    container.setModel(models)
    
    #container.getItemByIndex(0).writeWidget().setDangerMessage('BOOO') #uncomment to test the dangerous operation support
    #container.getItemByIndex(0).readWidget().setShowState(True)
    #container.getItemByIndex(0).setWriteWidgetClass(TaurusValueLineEdit)
    #container[0].setWriteWidgetClass('None')
    #container.setModel(models)
    
    container.setModifiableByUser(True)
    form.show()

        
    
    #show an Attributechooser dialog if no model was given
    if models == []:
        from taurus.qt.qtgui.panel import TaurusModelChooser
        modelChooser = TaurusModelChooser()
        form.connect(modelChooser, Qt.SIGNAL("updateModels"), container.setModel)
        modelChooser.show()
    
    sys.exit(app.exec_())
