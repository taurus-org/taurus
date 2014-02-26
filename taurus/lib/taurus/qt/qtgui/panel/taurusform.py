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

"""This module contains taurus Qt form widgets"""

__all__ = ["TaurusAttrForm", "TaurusCommandsForm", "TaurusForm"]

__docformat__ = 'restructuredtext'

from datetime import datetime

from taurus.qt import Qt
import PyTango

import taurus.core

from taurus.qt.qtcore.mimetypes import (TAURUS_ATTR_MIME_TYPE, TAURUS_DEV_MIME_TYPE, 
                                       TAURUS_MODEL_LIST_MIME_TYPE, TAURUS_MODEL_MIME_TYPE)
from taurus.qt.qtgui.container import TaurusWidget, TaurusScrollArea
from taurus.qt.qtgui.button import QButtonBox, TaurusCommandButton
from taurusmodelchooser import TaurusModelChooser


class ParameterCB(Qt.QComboBox):
    '''A custom combobox'''
    def __init__(self, parent=None):
        Qt.QComboBox.__init__(self, parent)
        self.setEditable(True)
        
    def rememberCurrentText(self):
        '''Adds the current text to the combobox items list (unless it is already there)'''
        text = self.currentText()
        if self.findText(text) < 0:
            self.addItem(text)


class TaurusForm(TaurusWidget):
    '''A form containing specific widgets for interacting with
    a given list of taurus attributes and/or devices.
    
    Its model is a list of attribute and/or device names to be shown. Each item
    is represented in a row consisting of a label, a read widget, a write
    widget, a units widget and an "extra" widget (some of them may not be shown)
    which are vertically aligned with their counterparts from other items.
    
    By default a :class:`TaurusValue` object is used for each item, but this
    can be changed and specific mappings can be defined using the
    :meth:`setCustomWidgetMap` method.
    
    Item objects can be accessed by index using a list-like notation::
    
      form = TaurusForm()
      form.model = ['sys/tg_test/1'+a for a in ('short_image','/float_scalar','/double_scalar')] 
      form[0].labelConfig = 'dev_alias'
      form[-1].writeWidgetClass = 'TaurusWheelEdit'
      print(len(form))  # --> outputs '3' (the length of the form is the number of items)
    
    By default, the form provides global Apply and Cancel buttons.
    
    You can also see some code that exemplifies the use of TaurusForm in :ref:`Taurus
    coding examples <examples>` '''
    
    def __init__(self, parent = None,
                 formWidget = None,
                 buttons = None,
                 withButtons = True, 
                 designMode = False):
        TaurusWidget.__init__(self, parent, designMode)
        
        if buttons == None: buttons = Qt.QDialogButtonBox.Apply| \
                                        Qt.QDialogButtonBox.Reset
        self._customWidgetMap = {}
        self._model = []
        self._children = []
        self.setFormWidget(formWidget)
        
        self.setLayout(Qt.QVBoxLayout())
        
        frame = TaurusWidget()
        frame.setLayout(Qt.QGridLayout())
        
        self.scrollArea = TaurusScrollArea(self)
        self.scrollArea.setWidget(frame)
        self.scrollArea.setWidgetResizable(True)
        self.layout().addWidget(self.scrollArea)
        self.__modelChooserDlg = None
        
        self.buttonBox = QButtonBox(buttons = buttons, parent = self)
        self.layout().addWidget(self.buttonBox)
        
        self._connectButtons()
        
        
        #Actions (they automatically populate the context menu)
        self.setContextMenuPolicy(Qt.Qt.ActionsContextMenu)
        
        self.chooseModelsAction = Qt.QAction('Modify Contents', self)
        self.addAction(self.chooseModelsAction)
        self.connect(self.chooseModelsAction, Qt.SIGNAL("triggered()"), self.chooseModels)
        
        self.showButtonsAction = Qt.QAction('Show Buttons', self)
        self.showButtonsAction.setCheckable(True)
        self.addAction(self.showButtonsAction)
        self.connect(self.showButtonsAction, Qt.SIGNAL("triggered(bool)"), self.setWithButtons)
        self.setWithButtons(withButtons)
        
        self.changeLabelsAction = Qt.QAction('Change labels (all items)', self)
        self.addAction(self.changeLabelsAction)
        self.connect(self.changeLabelsAction, Qt.SIGNAL("triggered()"), self.onChangeLabelsAction)
        
        self.resetModifiableByUser()
        self.setSupportedMimeTypes([TAURUS_MODEL_LIST_MIME_TYPE, TAURUS_DEV_MIME_TYPE, TAURUS_ATTR_MIME_TYPE, TAURUS_MODEL_MIME_TYPE, 'text/plain'])

        #properties
        self.registerConfigProperty(self.isWithButtons, self.setWithButtons, 'withButtons')

    def __getitem__(self, key):
        '''provides a list-like interface: items of the form can be accessed using slice notation'''
        return self.getItemByIndex(key)
    
    def __len__(self):
        '''returns the number of items contained by the form'''
        return len(self.getItems())
    
    def _splitModel(self, modelNames):
        '''convert str to list if needed (commas and whitespace are considered as separators)'''
        if isinstance(modelNames,(basestring,Qt.QString)): 
            modelNames = str(modelNames).replace(',',' ')
            modelNames = modelNames.split()
        return modelNames 
    
    def setCustomWidgetMap(self, cwmap):
        '''Sets a map map for custom widgets.
        
        :param cwmap: (dict<str,tuple>) a dictionary whose keys are device
                      type strings (i.e. see :class:`PyTango.DeviceInfo`) and
                      whose values are tuples of classname,args,kwargs
        '''
        self._customWidgetMap = cwmap
        
    def getCustomWidgetMap(self):
        '''Returns the map used to create custom widgets.
        
        :return: (dict<str,tuple>) a dictionary whose keys are device
                 type strings (i.e. see :class:`PyTango.DeviceInfo`) and whose
                 values are tuples of classname,args,kwargs
        '''
        return self._customWidgetMap
      
    @Qt.pyqtSignature("modelChanged(const QString &)")
    def parentModelChanged(self, parentmodel_name):
        self.info("Parent model changed to '%s'" % parentmodel_name)
        parentmodel_name = str(parentmodel_name)
        if self.getUseParentModel():
            #reset the model of childs
            for obj,model in zip(self.getItems(), self.getModel()):
                obj.setModel('%s/%s'%(parentmodel_name, str(model)))
        else:
            self.debug("received event from parent although not using parent model")
    
    def chooseModels(self):
        '''launches a model chooser dialog to modify the contents of the form'''
        if self.__modelChooserDlg is None: 
            self.__modelChooserDlg = Qt.QDialog(self)
            self.__modelChooserDlg.setWindowTitle("%s - Model Chooser"%unicode(self.windowTitle()))
            self.__modelChooserDlg.modelChooser = TaurusModelChooser()
            layout = Qt.QVBoxLayout()
            layout.addWidget(self.__modelChooserDlg.modelChooser)
            self.__modelChooserDlg.setLayout(layout)
            self.connect(self.__modelChooserDlg.modelChooser, Qt.SIGNAL("updateModels"), self.setModel)
            
        models_and_labels = []
        models = [m.lower() for m in self.getModel()]
        indexdict = {}
        for m in models:
            indexdict[m]=indexdict.get(m,-1)+1
            item = self.getItemByModel(m,indexdict[m])
            if item is None:
                label = None
            else:
                try: 
                    label = str(item.labelWidget().text()) #this assumes that the readwidget is a QLabel subclass (or something that has text())
                except:
                    label = None
            models_and_labels.append((m,label))
            
        self.__modelChooserDlg.modelChooser.setListedModels(models_and_labels)
        self.__modelChooserDlg.show()
        self.__modelChooserDlg.raise_()
        
    def chooseAttrs(self):
        self.info('TaurusForm.chooseAttrs() ahs been deprecated. Use TaurusForm.chooseModels() instead')
        self.chooseModels()
        
    def sizeHint(self):
        return Qt.QWidget.sizeHint(self)
        
    def _connectButtons(self):
        Qt.QObject.connect(self.buttonBox, Qt.SIGNAL("applyClicked()"), self.apply)
        Qt.QObject.connect(self.buttonBox, Qt.SIGNAL("resetClicked()"), self.reset)
        
    def getModel(self):
        return self._model
    
    @Qt.pyqtSignature("addModels(QStringList)")
    def addModels(self, modelNames):
        '''Adds models to the existing ones:
        
        :param modelNames:  (sequence<str>) the names of the models to be added
        
        .. seealso:: :meth:`removeModels`
        '''
        modelNames = self._splitModel(modelNames)
        self.setModel(self.getModel()+modelNames)
    
    @Qt.pyqtSignature("removeModels(QStringList)")
    def removeModels(self, modelNames):
        '''Removes models from those already in the form.
        
        :param modelNames:  (sequence<str>) the names of the models to be removed
        
        .. seealso:: :meth:`addModels`
        '''
        modelNames = self._splitModel(modelNames)
        currentModels = self.getModel()
        for name in modelNames:
            try: currentModels.remove(name)
            except: self.warning("'%s' not in model list"%name)
        self.setModel(currentModels)
    
    def setModelCheck(self, model, check=True):
        if model is None:
            model = []
        model = [str(m or '') for m in self._splitModel(model)]
        self.destroyChildren()
        self._model = model
        self.fillWithChildren()
        #update the modelchooser list
        if self.__modelChooserDlg is not None:
            self.__modelChooserDlg.modelChooser.setListedModels(self._model)
                
    def resetModel(self):
        self.destroyChildren()
        self._model = []
        
    def getFormWidget(self, model=None):
        '''Returns a tuple that can be used for creating a widget for a given model.
        
        :param model: (str) a taurus model name for which the new item of the
                      form will be created
        
        :return: (tuple<type,list,dict>) a tuple containing a class, a list of
                 args and a dict of keyword args. The args and the keyword args
                 can be passed to the class constructor
        '''
        if model is None:
            return self._defaultFormWidget,(),{}
        #If a model is given, check if is in the custom widget map
        try: 
            obj=taurus.Attribute(model) #if it is not an attribute, it will get an exception here
            return self._defaultFormWidget,(),{}
        except:
            try:
                obj=taurus.Device(model)
            except:
                self.warning('Cannot handle model "%s". Using default widget.'%(model))
                return self._defaultFormWidget,(),{}
            try:
                key = obj.getHWObj().info().dev_class
            except:
                return self._defaultFormWidget,(),{}
            #value = self._formWidgetsMap.get(key, self._defaultFormWidget)
            cwmap = self.getCustomWidgetMap()
            value = cwmap.get(key, self._defaultFormWidget)
            if isinstance(value, type): #for backwards compatibility
                if issubclass(value, self._defaultFormWidget):
                    return value,(),{}
                else:
                    return self._defaultFormWidget,(), {'customWidgetMap':{key:value}}
            #we expect a tuple of str,list,dict --> (classname_including_full_module, args, kwargs)
            name,args,kwargs = value
            pkgname,klassname = name.rsplit('.',1)
            try:
                pkg = __import__(pkgname, fromlist=[klassname])
                klass = getattr(pkg,klassname)
            except:
                self.warning('Cannot import "%s". Using default widget for "%s".'%(name, model))
                return self._defaultFormWidget,(),{}
            if not issubclass(klass, self._defaultFormWidget):
                cwmap = kwargs.get('customWidgetMap',{})
                cwmap.update({key:klass})
                kwargs['customWidgetMap'] = cwmap
                klass = self._defaultFormWidget
            return klass,args,kwargs    
                
    def setFormWidget(self, formWidget):
        if formWidget is None:
            from taurus.qt.qtgui.panel import TaurusValue
            self._defaultFormWidget = TaurusValue
        elif issubclass(formWidget, Qt.QWidget):
            self._defaultFormWidget = formWidget
        else:
            raise TypeError('formWidget must be one of None, QWidget. %s passed'%repr(type(formWidget)))
        
    def resetFormWidget(self):
        self.setFormWidget(self, None)
        
    def isWithButtons(self):
        return self._withButtons
    
    def setWithButtons(self, trueFalse):
        self._withButtons = trueFalse
        self.buttonBox.setVisible(self._withButtons)
        self.showButtonsAction.setChecked(self._withButtons)
        
    def resetWithButtons(self):
        self.setWithButtons(True)
    
    def dropEvent(self, event):
        '''reimplemented to support dropping of modelnames in forms'''
        mtype = self.handleMimeData(event.mimeData(),self.addModels)
        if mtype is None:
            self.info('Invalid model in dropped data')
        else:
            event.acceptProposedAction() 
      
    def setModifiableByUser(self, modifiable):
        '''
        sets whether the user can change the contents of the form
        (e.g., via Modify Contents in the context menu)
        Reimplemented from :meth:`TaurusWidget.setModifiableByUser`
        
        :param modifiable: (bool)
        
        .. seealso:: :meth:`TaurusWidget.setModifiableByUser`
        '''
        TaurusWidget.setModifiableByUser(self, modifiable)
        self.chooseModelsAction.setEnabled(modifiable)
        self.showButtonsAction.setEnabled(modifiable)
        self.changeLabelsAction.setEnabled(modifiable)
        for item in self.getItems():
            try: 
                item.setModifiableByUser(modifiable)
            except:
                pass
        
    def setRegExp(self, regExp):
        pass
    
    def getRegExp(self):
        pass
    
    def destroyChildren(self):
        for child in self._children:
            self.unregisterConfigurableItem(child)
            #child.destroy()
            child.setModel(None)
            child.deleteLater()
        self._children = []
                
    def fillWithChildren(self):
        frame = TaurusWidget()
        frame.setLayout(Qt.QGridLayout())
        frame.layout().addItem(Qt.QSpacerItem(0,0,Qt.QSizePolicy.Minimum,Qt.QSizePolicy.MinimumExpanding))
        
        parent_name = None
        if self.getUseParentModel():
            parent_model = self.getParentModelObj()
            if parent_model:
                parent_name = parent_model.getFullName()
        
        for i,model in enumerate(self.getModel()):
            if not model:
                continue
            if parent_name: model = "%s/%s" % (parent_name, model) #@todo: Change this (it assumes tango model naming!)
            klass, args, kwargs = self.getFormWidget(model=model)
            widget = klass(frame,*args,**kwargs)
            widget.setMinimumHeight(20)  #@todo UGLY... See if this can be done in other ways... (this causes trouble with widget that need more vertical space , like PoolMotorTV)
            try: 
                widget.setModel(model)
                widget.setParent(frame)
            except: 
                #raise
                self.warning('an error occurred while adding the child "%s". Skipping'%model)
                self.traceback(level=taurus.Debug)
            try: widget.setModifiableByUser(self.isModifiableByUser())
            except: pass
            widget.setObjectName("__item%i"%i)
            self.registerConfigDelegate(widget)
            self._children.append(widget)
       
        frame.layout().addItem(Qt.QSpacerItem(0,0,Qt.QSizePolicy.Minimum,Qt.QSizePolicy.MinimumExpanding))
        self.scrollArea.setWidget(frame)
#        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setMinimumWidth(frame.layout().sizeHint().width()+20)

    def getItemByModel(self, model, index=0):
        '''returns the child item with given model. If there is more than one item
        with the same model, the index parameter can be used to distinguish among them
        Please note that his index is only relative to same-model items!'''
        for child in self._children:
            if child.getModel().lower() == model.lower():
                if index <= 0:
                    return child
                else:
                    index -= 1
    
    def getItemByIndex(self, index):
        '''returns the child item with at the given index position. '''
        return self.getItems()[index]
    
    def getItems(self):
        '''returns a list of the objects that have been created as childs of the form'''
        return self._children
    
#    def _manageButtonBox(self):
#        if self.isWithButtons():
#            self.buttonBox.setVisible(True)
#        else:
#            self.buttonBox.setVisible(False)

    def onChangeLabelsAction(self):
        '''changes the labelConfig of all its items'''
        keys = ['label', 'attr_name', 'attr_fullname', 'dev_alias', 'dev_name', 'dev_fullname']
            
        msg = 'Choose new source for the label. \n'+\
              'You can also write a more complex text\n'+\
              'using any of the proposed sources as a\n'+\
              'placeholder by enclosing it in "< >" brackets'
        labelConfig, ok = Qt.QInputDialog.getItem(self, 'Change Label', msg, keys, 0, True)
        if ok:
            for item in self.getItems():
                item.labelConfig=str(labelConfig)

    @Qt.pyqtSignature("apply()")        
    def apply(self):
        self.safeApplyOperations()
                
    @Qt.pyqtSignature("reset()")
    def reset(self):
        self.resetPendingOperations()

    @classmethod
    def getQtDesignerPluginInfo(cls):
        ret = TaurusWidget.getQtDesignerPluginInfo()
        ret['module'] = 'taurus.qt.qtgui.panel'
        ret['container'] = False
        return ret
    
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # QT properties 
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
   
    model = Qt.pyqtProperty("QStringList", getModel, 
                                                TaurusWidget.setModel, 
                                                resetModel)

    useParentModel = Qt.pyqtProperty("bool", 
                                         TaurusWidget.getUseParentModel, 
                                         TaurusWidget.setUseParentModel,
                                         TaurusWidget.resetUseParentModel)
    
    withButtons = Qt.pyqtProperty("bool", isWithButtons, 
                                                setWithButtons,
                                                resetWithButtons)
    
    modifiableByUser = Qt.pyqtProperty("bool", TaurusWidget.isModifiableByUser, 
                                               setModifiableByUser,
                                               TaurusWidget.resetModifiableByUser)
      
    

class TaurusCommandsForm(TaurusWidget):
    '''A form that shows commands available for a Device Server'''
    def __init__(self, parent = None, designMode = False):
        TaurusWidget.__init__(self, parent, designMode)
        
        self.setLayout(Qt.QVBoxLayout())
                
        self._splitter = Qt.QSplitter()
        self._splitter.setOrientation(Qt.Qt.Vertical)
        self.layout().addWidget(self._splitter)
        
        self._frame = TaurusWidget(self)
        self._frame.setLayout(Qt.QGridLayout())
        
        self._scrollArea = TaurusScrollArea(self)
        self._scrollArea.setWidget(self._frame)
        self._scrollArea.setWidgetResizable(True)
        self._splitter.addWidget(self._scrollArea)
        
        self._outputTE = Qt.QTextEdit()
        self._outputTE.setReadOnly(True)
        self._splitter.addWidget(self._outputTE)
        #self._splitter.moveSplitter(self._splitter.getRange(0)[-1], 0)
        
        self._cmdWidgets = []
        self._paramWidgets = []
        self._viewFilters = []
        self._defaultParameters = []
        self._sortKey = lambda x:x.cmd_name
        
        self._operatorViewFilter = lambda x: x.disp_level == PyTango.DispLevel.OPERATOR
        
        #self.setLayout(Qt.QGridLayout())
        self.connect(self, Qt.SIGNAL('modelChanged(const QString &)'),self._updateCommandWidgets )
        
    def createConfig(self, allowUnpickable=False):
        '''
        extending  :meth:`TaurusBaseWidget.createConfig`                
        :param alllowUnpickable:  (bool) 
        
        :return: (dict<str,object>) configurations (which can be loaded with :meth:`applyConfig`).
        
        .. seealso: :meth:`TaurusBaseWidget.createConfig`, :meth:`applyConfig` 
        '''
        #get the basic config
        configdict = TaurusWidget.createConfig(self, allowUnpickable=allowUnpickable)
        #store the splitter config
        configdict['splitter/state'] = self._splitter.saveState().data()        
        return configdict
    
    def applyConfig(self, configdict, **kwargs):
        """extending :meth:`TaurusBaseWidget.applyConfig` to restore the splitter config
     
        :param configdict: (dict)
        
        .. seealso:: :meth:`TaurusBaseWidget.applyConfig`, :meth:`createConfig`
        """
        #first do the basic stuff...
        TaurusWidget.applyConfig(self, configdict, **kwargs)
        #restore the splitter config
        self._splitter.restoreState(Qt.QByteArray(configdict['splitter/state']))
        
    def getModelClass(self):
        '''see :meth:`TaurusBaseComponent.getModelClass`'''
        return taurus.core.taurusdevice.TaurusDevice
        
    def _updateCommandWidgets(self, *args):
        '''
        Inserts command buttons and parameter widgets in the layout, according to
        the commands from the model
        '''
        #self.debug('In TaurusCommandsForm._updateCommandWidgets())')
        dev = self.getModelObj()
        if dev is None or dev.getSWState() != taurus.core.taurusbasetypes.TaurusSWDevState.Running:
            self.debug('Cannot connect to device')
            self._clearFrame()
            return
        commands = sorted(dev.command_list_query(), key=self._sortKey)
        
        for f in self.getViewFilters():
            commands = filter(f, commands)
        
        self._clearFrame()
        
        layout = self._frame.layout()

        for row,c in enumerate(commands):
            self.debug('Adding button for command %s'%c.cmd_name)
            button = TaurusCommandButton(command=c.cmd_name,text=c.cmd_name)
            layout.addWidget(button, row, 0)
            button.setUseParentModel(True)
            self._cmdWidgets.append(button)
            self.connect(button, Qt.SIGNAL('commandExecuted'), self._onCommandExecuted)
            
            if c.in_type != PyTango.CmdArgType.DevVoid:
                self.debug('Adding arguments for command %s'%c.cmd_name)
                pwidget = ParameterCB()
                if c.cmd_name.lower() in self._defaultParameters:
                    for par in self._defaultParameters.get(c.cmd_name.lower(),[]): pwidget.addItem(par)
                    #pwidget.setEditable( (self._defaultParameters[c.cmd_name.lower()] or [''])[0] == '' )
                    if (self._defaultParameters[c.cmd_name.lower()] or [''])[0] == '':
                        pwidget.setEditable(True)
                    else:
                        pwidget.setEditable(False)
                        button.setParameters(self._defaultParameters[c.cmd_name.lower()][0])
                self.connect(pwidget, Qt.SIGNAL('editTextChanged (const QString&)'),button.setParameters)
                self.connect(pwidget, Qt.SIGNAL('currentIndexChanged (const QString&)'),button.setParameters)
                self.connect(pwidget, Qt.SIGNAL('activated (int)'), button.setFocus)
                self.connect(button, Qt.SIGNAL('commandExecuted'), pwidget.rememberCurrentText)
                layout.addWidget(pwidget, row, 1)
                self._paramWidgets.append(pwidget)
    
    def _clearFrame(self):
        '''destroys all widgets in the scroll area frame'''
        self._frame = TaurusWidget(self)
        self._frame.setLayout(Qt.QGridLayout())
        self._frame.setModel(self.getModelName()) # hack because useParentModel does not work!
        self._scrollArea.setWidget(self._frame)
        self._cmdWidgets = []
        self._paramWidgets = []
        
    def _onCommandExecuted(self, result):
        '''Slot called when the command is executed, to manage the output
        
        :param result: return value from the command. The type depends on the command
        '''
        timestamp = datetime.now()
        cmdbutton = self.sender()
        output = '<i>%s</i><br>'%timestamp.strftime('%Y-%m-%d %H:%M:%S') +\
                 '<b>Command:</b> %s<br>'%cmdbutton.getCommand() +\
                 '<b>Pars:</b> %s<br>'%repr(cmdbutton.getParameters()) +\
                 '<b>Return Value:</b><br>%s'%str(result)
        self._outputTE.append(output)
        separator = '<table width=\"100%\"><tr><td><hr /></td></tr></table>' # ugly workaround for bug in html rendering in Qt
        self._outputTE.append(separator)                                     # see http://lists.trolltech.com/qt-interest/2008-04/thread00224-0.html
        #self._outputTE.append('%s'%timestamp)
        #self._outputTE.append('<b>Command:</b> "%s"'%cmdbutton.getCommand())
        #self._outputTE.append('<b>Pars:</b> %s'%repr(cmdbutton.getParameters()))
        #self._outputTE.append('<b>Return Value:</b><br>%s<hr>'%str(result))
        
    def setSortKey(self, sortkey):
        '''sets the method used to sort the commands (cmd_name by default)
        
        :param sortkey: (callable) a function that takes a :class:`CommandInfo`
                        as argument and returns a key to use for sorting purposes
                        (e.g. the default sortKey is ``lambda x:x.cmd_name``)
        '''
        self._sortKey = sortkey
        self._updateCommandWidgets()

    def setDefaultParameters(self, params):
        '''sets the values that will appear by default in the parameters combo box,
        the command combo box for the command will be editable only if the first parameter is an empty string
        
        :param params: (dict<str,list>) { 'cmd_name': ['parameters string 1', 'parameters string 2' ] }
 
        '''
        self._defaultParameters = dict((k.lower(),v) for k,v in params.items())
        self._updateCommandWidgets()

    def setViewFilters(self, filterlist):
        '''sets the filters to be applied when displaying the commands
        
        :param filterlist: (sequence<callable>) a sequence of command filters.
                           All filters will be applied to each command to decide
                           whether to display it or not.
                           for a command to be plotted, the following condition
                           must be true for all filters:
                           bool(filter(command))==True
        '''
        self._viewFilters = filterlist
        self._updateCommandWidgets()
    
    def getViewFilters(self):
        '''returns the filters used in deciding which commands are displayed
        
        :return: (sequence<callable>) a sequence of filters
        '''
        return self._viewFilters
    
    @Qt.pyqtSignature("setCommand(bool)")
    def setExpertView(self,expert):
        '''sets the expert view mode
        
        :param expert: (bool) If expert is True, commands won't be filtered. If
                       it is False, commands with  display level Expert won't be shown
        '''
        currentfilters = self.getViewFilters()
        if expert:
            if self._operatorViewFilter in currentfilters:
                currentfilters.remove(self._operatorViewFilter)
        else:
            if self._operatorViewFilter not in currentfilters:
                currentfilters.insert(0, self._operatorViewFilter)
        self.setViewFilters(currentfilters)
        self._expertView = expert
    
    def getSplitter(self):
        '''returns the splitter that separates the command buttons area from 
        the output area
        
        :return: (QSplitter)'''
        return self._splitter

    @classmethod
    def getQtDesignerPluginInfo(cls):
        ret = TaurusWidget.getQtDesignerPluginInfo()
        ret['module'] = 'taurus.qt.qtgui.panel'
        ret['container'] = False
        return ret


class TaurusAttrForm(TaurusWidget):
    '''A form that displays the attributes of a Device Server'''
    def __init__(self, parent = None, designMode = False):
        TaurusWidget.__init__(self, parent, designMode)
        
        self._viewFilters = []
        self._operatorViewFilter = lambda x: x.disp_level == PyTango.DispLevel.OPERATOR
        
        self.setLayout(Qt.QVBoxLayout())
   
        self._form = TaurusForm(parent = self)
        self.layout().addWidget(self._form)
        self.registerConfigDelegate(self._form)
        
        self.connect(self, Qt.SIGNAL('modelChanged(const QString &)'),self._updateAttrWidgets )
        
        self._sortKey = lambda x:x.name

    def setSortKey(self, sortkey):
        '''sets the key function used to sort the attributes in the form 
        
        :param sortkey: (callable) a function that takes a :class:`AttributeInfo`
                        as argument and returns a key to use for sorting purposes
                        (e.g. the default sortKey is ``lambda x:x.name``)
        
        '''
        self._sortKey = sortkey
        self._updateAttrWidgets()        
        
    def getModelClass(self):
        '''see :meth:`TaurusBaseComponent.getModelClass`'''
        return taurus.core.taurusdevice.TaurusDevice
    
    def _updateAttrWidgets(self):
        '''Populates the form with an item for each of the attributes shown
        '''
        dev = self.getModelObj()
        if dev is None or dev.getSWState() != taurus.core.taurusbasetypes.TaurusSWDevState.Running:
            self.debug('Cannot connect to device')
            self._form.setModel([])
            return
        attrlist = sorted(dev.attribute_list_query(), key=self._sortKey)
        for f in self.getViewFilters():
            attrlist = filter(f, attrlist)
        attrnames = []
        devname = self.getModelName()
        for a in attrlist:
            attrnames.append("%s/%s"%(devname,a.name)) #ugly hack . But setUseParentModel does not work well
        self.debug('Filling with attribute list: %s'%("; ".join(attrnames))) 
        self._form.setModel(attrnames)
        
    def setViewFilters(self, filterlist):
        '''sets the filters to be applied when displaying the attributes
        
        :param filterlist: (sequence<callable>) a sequence of attr filters. All
                           filters will be applied to each attribute name to
                           decide whether to display it or not. for an attribute
                           to be plotted, the following condition must be true
                           for all filters: ``bool(filter(attrname))==True``
        '''
        self._viewFilters = filterlist
        self._updateAttrWidgets()
    
    def getViewFilters(self):
        '''returns the filters used in deciding which attributes are displayed
        
        :return: (sequence<callable>) a sequence of filters
        '''
        return self._viewFilters
    
    @Qt.pyqtSignature("setExpertView(bool)")
    def setExpertView(self, expert):
        '''sets the expert view mode
        
        :param expert: (bool) If expert is True, attributes won't be filtered. If
                       it is False, attributes with display level Expert won't
                       be shown
        '''
        currentfilters = self.getViewFilters()
        if expert:
            if self._operatorViewFilter in currentfilters:
                currentfilters.remove(self._operatorViewFilter)
        else:
            if self._operatorViewFilter not in currentfilters:
                currentfilters.insert(0, self._operatorViewFilter)
        self.setViewFilters(currentfilters)
        self._expertView = expert
    
    @classmethod
    def getQtDesignerPluginInfo(cls):
        ret = TaurusWidget.getQtDesignerPluginInfo()
        ret['module'] = 'taurus.qt.qtgui.panel'
        ret['container'] = False
        return ret
    
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # QT properties 
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
   
    model = Qt.pyqtProperty("QString", TaurusWidget.getModel, 
                                       TaurusWidget.setModel, 
                                       TaurusWidget.resetModel)
    
    useParentModel = Qt.pyqtProperty("bool", 
                                         TaurusWidget.getUseParentModel, 
                                         TaurusWidget.setUseParentModel,
                                         TaurusWidget.resetUseParentModel)



def test1():
    '''tests taurusForm'''
    import sys
    if len(sys.argv)>1: models=sys.argv[1:]
    else: models = None
    app = Qt.QApplication(sys.argv)
    if models is None:
        models = ['sys/tg_test/1/state',
                  'sys/tg_test/1/float_scalar',
                  'sys/tg_test/1/boolean_image',
                  'sys/tg_test/1/float_spectrum',
                  'sys/tg_test/1/status']
    dialog = TaurusForm()
    dialog.setModel(models)
    dialog.setModifiableByUser(True)
    for i,tv in enumerate(dialog.getItems()):
        tv.setDangerMessage("Booooo scaring %d!!!"%i)
    dialog.show()
    
    dialog2 = TaurusForm()
    dialog2.show()
    dialog2.setModifiableByUser(True)
    sys.exit(app.exec_())

def test2():
    '''tests taurusAttrForm'''
    import sys
    if len(sys.argv)>1: model=sys.argv[1]
    else: model = None
    
    if model is None: model = 'bl97/pc/dummy-01'
    app = Qt.QApplication(sys.argv)
    dialog = TaurusAttrForm()
    dialog.setModel(model)
    dialog.show()
    sys.exit(app.exec_())
    
def test3():
    '''tests taurusCommandsForm'''
    import sys
    if len(sys.argv)>1: model=sys.argv[1]
    else: model = None
    
    if model is None: model = 'bl97/pc/dummy-01'
    app = Qt.QApplication(sys.argv)
    dialog = TaurusCommandsForm()
    dialog.setModel(model)
    dialog.show()
#    dialog.getSplitter().setSizes([10,220])

    sys.exit(app.exec_()) 
    
def test4():
    '''tests customwidgetma in taurusforms'''
    import sys
    from taurus.qt.qtgui.display import TaurusLabel
    app = Qt.QApplication(sys.argv)
    
    from taurus.qt.qtgui.panel import TaurusValue
    class DummyCW(TaurusValue):
        def setModel(self,model):
            print "!!!!! IN DUMMYCW.SETMODEL", model
            TaurusValue.setModel(self, model+'/double_scalar')
    
    models = ['sys/database/2', 'sys/tg_test/1', 'sys/tg_test/1/short_spectrum', 'sys/tg_test/1/state','sys/tg_test/1/short_scalar_ro']
    models.append('tango://controls02:10000/expchan/bl97_simucotictrl_1/1')
    map={
        'PseudoCounter':('taurus.qt.qtgui.extra_pool.PoolChannelTV', (),{}), #taurusvalue-like classes given as strings
        'CTExpChannel':('taurus.qt.qtgui.extra_pool.PoolChannelTV', (),{}),
        'ZeroDExpChannel':('taurus.qt.qtgui.extra_pool.PoolChannelTV', (),{}),
        'OneDExpChannel':('taurus.qt.qtgui.extra_pool.PoolChannelTV', (),{}),
        'TwoDExpChannel':('taurus.qt.qtgui.extra_pool.PoolChannelTV', (),{}),
        'TangoTest':DummyCW,    #a TaurusValue-like class given as a class (old way)
        'DataBase':TaurusLabel} #a non-TaurusValue-like class given as a class (old way)
    
    dialog = TaurusForm()
    dialog.setCustomWidgetMap(map)
    dialog.setModel(models)
    dialog.show()
    sys.exit(app.exec_())
            

def taurusFormMain():
    '''A launcher for TaurusForm.'''
    ## NOTE: DON'T PUT TEST CODE HERE.
    ## THIS IS CALLED FROM THE LAUNCHER SCRIPT (<taurus>/scripts/taurusform)
    ## USE test1() instead.
    from taurus.qt.qtgui.application import TaurusApplication
    from taurus.core.util import argparse
    import sys, os
    
    parser = argparse.get_taurus_parser()
    parser.set_usage("%prog [options] [model1 [model2 ...]]")
    parser.set_description("the taurus form panel application")
    parser.add_option("--window-name", dest="window_name", default="TaurusForm", help="Name of the window")
    parser.add_option("--config", "--config-file", dest="config_file", default=None,
                  help="use the given config file for initialization")
    app = TaurusApplication(cmd_line_parser=parser,
                            app_name="taurusform",
                            app_version=taurus.Release.version)
    args = app.get_command_line_args()
    options = app.get_command_line_options()

    dialog = TaurusForm()
    dialog.setModifiableByUser(True)
    dialog.setModelInConfig(True)
    dialog.setWindowTitle(options.window_name)
            
    from taurus.qt.qtgui.resource import getThemeIcon
    quitApplicationAction =  Qt.QAction(getThemeIcon("process-stop"),'Close Form', dialog)
    dialog.connect(quitApplicationAction, Qt.SIGNAL("triggered()"), dialog.close)
    
    saveConfigAction = Qt.QAction("Save current settings...", dialog)
    saveConfigAction.setShortcut(Qt.QKeySequence.Save)
    dialog.connect(saveConfigAction, Qt.SIGNAL("triggered()"), dialog.saveConfigFile)  
    
    loadConfigAction = Qt.QAction("&Retrieve saved settings...", dialog)
    loadConfigAction.setShortcut(Qt.QKeySequence.Open)
    dialog.connect(loadConfigAction, Qt.SIGNAL("triggered()"), dialog.loadConfigFile)
    
    dialog.addActions ((saveConfigAction, loadConfigAction, quitApplicationAction) )
    
    #set the default map for this installation
    from taurus import tauruscustomsettings
    dialog.setCustomWidgetMap(getattr(tauruscustomsettings,'T_FORM_CUSTOM_WIDGET_MAP',{}))
    
    #set a model list from the command line or launch the chooser  
    if options.config_file is not None: 
        dialog.loadConfigFile(options.config_file)
    elif len(args)>0:
        models=args
        dialog.setModel(models)
    else:
        dialog.chooseModels()

    dialog.show()
    
    sys.exit(app.exec_())

def main():
    #test1()
    #test2()
    #test3()
    #test4()
    taurusFormMain()
    
if __name__ == "__main__":
    main() 
