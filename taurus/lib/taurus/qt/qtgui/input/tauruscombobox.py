#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

"""This module provides a set of basic taurus widgets based on QCheckBox"""

__all__ = ["TaurusAttrListComboBox", "TaurusValueComboBox"]

__docformat__ = 'restructuredtext'

from taurus.qt import Qt

import PyTango
import taurus.core
from taurus.qt.qtgui.base import TaurusBaseWidget, TaurusBaseWritableWidget
from taurus.core.util import eventfilters


class TaurusValueComboBox(Qt.QComboBox, TaurusBaseWritableWidget):
    '''This widget shows a combobox that offers a limited choice of values that
    can be set on an attribute.'''
    
    __pyqtSignals__ = ("modelChanged(const QString &)",)

    def __init__(self, parent = None, designMode = False):
        self._previousModelName = None
        self._lastValueByUser = None
        
        name = self.__class__.__name__
        self.call__init__wo_kw(Qt.QComboBox, parent)
        self.call__init__(TaurusBaseWritableWidget, name, designMode=designMode)

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # Helper methods
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    def _setCurrentIndex(self, index):
        bs = self.blockSignals(True)
        try:
            self.setCurrentIndex(index)
        finally:
            self.blockSignals(bs)

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # TaurusBaseWidget overwriting
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    def preAttach(self):
        '''reimplemented from :class:`TaurusBaseWritableWidget`'''
        TaurusBaseWritableWidget.preAttach(self)
        Qt.QObject.connect(self, Qt.SIGNAL("currentIndexChanged(int)"),
                               self.writeIndexValue)
        Qt.QObject.connect(self, Qt.SIGNAL("applied()"),
                               self.writeValue)

    def postDetach(self):
        '''reimplemented from :class:`TaurusBaseWritableWidget`'''
        TaurusBaseWritableWidget.postDetach(self)
        Qt.QObject.disconnect(self, Qt.SIGNAL("currentIndexChanged(int)"),
                                  self.writeIndexValue)
        Qt.QObject.disconnect(self, Qt.SIGNAL("applied()"),
                                  self.writeValue)

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # TaurusBaseWritableWidget overwriting / Pending operations
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    def getValue(self):
        """
        Get the value that the widget is displaying now, not the value
        of the attribute.
        """
        model = self.getModelObj()
        if model is None:
            return None

        new_value = self.itemData(self.currentIndex())
        if new_value is None:
            return None

        if PyTango.is_int_type(model.data_type):
            func = int
        elif PyTango.is_float_type(model.data_type):
            func = float
        elif model.data_type in (PyTango.DevString,):
            func = str
        elif model.data_type in (PyTango.DevBoolean,):
            func = bool
        else:
            return None
        new_value = Qt.from_qvariant(new_value, func)
        return new_value

    def setValue(self, value):
        """
        Set the value for the widget to display, not the value of the
        attribute.
        """
        index = self.findData(Qt.QVariant(value))
        self._setCurrentIndex(index)
    
    def updateStyle(self):
        '''reimplemented from :class:`TaurusBaseWritableWidget`'''
        if self.hasPendingOperations():
            self.setStyleSheet('TaurusValueComboBox {color: blue; }')
        else:
            self.setStyleSheet('TaurusValueComboBox {}')
        super(TaurusValueComboBox, self).updateStyle()

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # signals, gui events... things related to "write" in the end
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    @Qt.pyqtSignature("currentIndexChanged(int)")
    def writeIndexValue(self, index):
        '''slot called to emit a valueChanged signal when the currentIndex is changed'''
        self.emitValueChanged()
        if self.getAutoApply():
            self.emit(Qt.SIGNAL("applied()"))

    def keyPressEvent(self, event):
        '''reimplemented to emit an 'applied()' signal when Enter (or Return) 
        key is pressed'''
        if event.key() in [Qt.Qt.Key_Return,Qt.Qt.Key_Enter]:
            self.emit(Qt.SIGNAL("applied()"))
            event.accept()
        else:
            return Qt.QComboBox.keyPressEvent(self,event)

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # TaurusValueComboBox own interface
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    def setValueNames(self, names):
        '''
        Sets the correspondence between the values to be applied and their 
        associated text to show in the combobox.
        
        :param names: (sequence<tuple>) A sequence of (name,value) tuples, 
                      where each attribute value gets a name for display
        '''
        bs = self.blockSignals(True)
        self.clear()
        self.blockSignals(bs)
        self.addValueNames(names)
        
    def addValueNames(self, names):
        '''
        Add new value-name associations to the combobox.
        
        ... seealso: :meth:`setValueNames`
        
        :param names: (sequence<tuple>) A sequence of (name,value) tuples, 
                      where each attribute value gets a name for display
        '''
        bs = self.blockSignals(True)
        try:
            for k, v in names:
                self.addItem(k, Qt.QVariant(v))

            # Ok, now we should see if the current value matches any
            # of the newly added names. This is kinda a refresh:
            mv = self.getModelValueObj()
            if mv is not None:
                self.setValue(mv.w_value)
        finally:
            self.blockSignals(bs)
            
        self.emitValueChanged()
        
    def getValueString(self, value, default='UNKNOWN(%s)'):
        """Returns the corresponding name in the combobox out of a value 
        (or a default value if not found).
        
        :param value: value to look up
        :param default: (str) value in case it is not found. It accepts 
                        a '%s' placeholder which will be substituted with
                        str(value). It defaults to 'UNKNOWN(%s)'.        
        """
        item = self.findData(Qt.QVariant(value))
        if item < 0:
            if '%s' in default:
                return default % str(value)
            else:
                return default
        return str(self.itemText(item))
        
    def teachDisplayTranslationToWidget(self, widget, default='UNKNOWN(%s)'):
        """
        Makes a label object change the displayed text by the corresponding
        value of the combobox. This is implemented for the general case
        and may be not what you expect in some cases (as for example, it
        fires a fake periodic event which may be problematic if these
        are being filtered out).
        """
        # We reimplement label.displayValue so that instead of the normal
        # value it displays the string it has associated in the combobox.
        widget.displayValue = lambda v: self.getValueString(v, default)

        # Simulate a first event. Otherwise the displayValue will be
        # the default, not modified by us
        model = widget.getModelObj()
        if model:
            widget.fireEvent( model,
                             taurus.core.taurusbasetypes.TaurusEventType.Periodic,
                             model.getValueObj()
            )

    def setQModel(self, *args, **kwargs):
        '''access to :meth:`QCombobox.setModel`
        
        .. seealso: :meth:`setModel`
        '''
        Qt.QComboBox.setModel(self, *args, **kwargs)

    def setModel(self, m):
        '''Reimplemented from :meth:`TaurusBaseWritableWidget.setModel` '''
        if isinstance(m, Qt.QAbstractItemModel):
            self.warning("Deprecation warning: use setQModel() if you want to set a Qt Item Model. The setModel() method is reserved for Taurus models")
            return Qt.QComboBox.setModel(self, m)
        return TaurusBaseWritableWidget.setModel(self, m)

    @classmethod
    def getQtDesignerPluginInfo(cls):
        '''reimplemented from :class:`TaurusBaseWritableWidget`'''
        ret = TaurusBaseWritableWidget.getQtDesignerPluginInfo()
        ret['module'] = 'taurus.qt.qtgui.input'
        ret['icon'] = ":/designer/combobox.png"
        return ret
    
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # QT properties
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    model = Qt.pyqtProperty("QString",
                                TaurusBaseWidget.getModel,
                                TaurusBaseWidget.setModel,
                                TaurusBaseWidget.resetModel)

    useParentModel = Qt.pyqtProperty("bool",
                                         TaurusBaseWidget.getUseParentModel,
                                         TaurusBaseWidget.setUseParentModel,
                                         TaurusBaseWidget.resetUseParentModel)

    autoApply = Qt.pyqtProperty("bool",
                                    TaurusBaseWritableWidget.getAutoApply,
                                    TaurusBaseWritableWidget.setAutoApply,
                                    TaurusBaseWritableWidget.resetAutoApply)
    
    forcedApply = Qt.pyqtProperty("bool", TaurusBaseWritableWidget.getForcedApply,
                                 TaurusBaseWritableWidget.setForcedApply,
                                 TaurusBaseWritableWidget.resetForcedApply)

    
class TaurusAttrListComboBox(Qt.QComboBox, TaurusBaseWidget):
    
    __pyqtSignals__ = ("modelChanged(const QString &)",)
    
    def __init__(self, parent = None, designMode = False):
        name = self.__class__.__name__
        self.call__init__wo_kw(Qt.QComboBox, parent)
        self.call__init__(TaurusBaseWidget, name)
        self.insertEventFilter(eventfilters.IGNORE_CONFIG)
        self.setSizeAdjustPolicy(Qt.QComboBox.AdjustToContents)
        self.defineStyle()
    
    def defineStyle(self):
        """ Defines the initial style for the widget """
        self.updateStyle()

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # TaurusBaseWidget over writing
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    
    def getModelClass(self):
        '''reimplemented from :class:`TaurusBaseWidget`'''
        return taurus.core.taurusattribute.TaurusAttribute
            
    def handleEvent(self, evt_src, evt_type, evt_value):
        '''reimplemented from :class:`TaurusBaseWidget`'''
        self.clear()
        if evt_type == taurus.core.taurusbasetypes.TaurusEventType.Error:
            return
        if not (evt_src is None or evt_value is None) :
            attrList = list(evt_value.value)
            attrList.sort()
            self.addItems(attrList)
            self.updateStyle()
    
    def updateStyle(self):
        '''reimplemented from :class:`TaurusBaseWidget`'''
        self.update()
    
    def setQModel(self, *args, **kwargs):
        '''access to :meth:`QAbstractItemView.setModel`
        
        .. seealso: :meth:`setModel`
        '''
        return Qt.QAbstractItemView.setModel(self, *args, **kwargs)
    
    def setModel(self, m):
        '''reimplemented from :class:`TaurusBaseWidget`'''
        if isinstance(m, Qt.QAbstractItemModel):
            self.warning("Deprecation warning: use setQModel() if you want to set a Qt Item Model. The setModel() method is reserved for Taurus models")
            return Qt.QAbstractItemView.setQModel(self, m)
        return TaurusBaseWidget.setModel(self, m)

    @classmethod
    def getQtDesignerPluginInfo(cls):
        '''reimplemented from :class:`TaurusBaseWidget`'''
        ret = TaurusBaseWidget.getQtDesignerPluginInfo()
        ret['group'] = 'Taurus Input'
        ret['module'] = 'taurus.qt.qtgui.input'
        ret['icon'] = ":/designer/combobox.png"
        return ret
    
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # QT properties 
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    model = Qt.pyqtProperty("QString", TaurusBaseWidget.getModel, 
                                           TaurusBaseWidget.setModel,
                                           TaurusBaseWidget.resetModel)
                                
    useParentModel = Qt.pyqtProperty("bool",
                                         TaurusBaseWidget.getUseParentModel, 
                                         TaurusBaseWidget.setUseParentModel,
                                         TaurusBaseWidget.resetUseParentModel)


#####################################################################
## Testing
#####################################################################
def taurusAttrListTest():
    '''tests taurusAttrList. Model: an attribute containing a list of strings'''
    model = sys.argv[1]
    a = Qt.QApplication([])
    w = TaurusAttrListComboBox()
    w.setModel(model) 
    w.show()
    return a.exec_()
        
        
def TaurusValueComboboxTest():
    '''tests TaurusValueCombobox '''
    model = sys.argv[1]
    names = [
        ('name0', 0),
        ('name1', 1),
        ('name2', 2),
        ('name3', 3)
    ]
    a = Qt.QApplication([])
    w = TaurusValueComboBox()
    w.setModel(model)
    w.addValueNames(names)
    #w.setModel(model)
    #w.autoApply = True
    w.show()
    return a.exec_()

if __name__ == '__main__':
    import sys
    #main = TaurusValueComboboxTest #uncomment to test TaurusValueCombobox
    main = taurusAttrListTest #uncomment to testtaurusAttrList
    sys.exit(main())
