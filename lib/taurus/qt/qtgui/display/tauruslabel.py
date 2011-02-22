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

"""This module provides a set of basic Taurus widgets based on QLabel"""

__all__ = ["TaurusLabel"]

__docformat__ = 'restructuredtext'

import weakref
import operator

# shame of me for importing PyTango!
import PyTango

from PyQt4 import Qt

import taurus.core.util
from taurus.qt.qtgui.util import QT_ATTRIBUTE_QUALITY_PALETTE, QT_DEVICE_STATE_PALETTE
from taurus.qt.qtgui.base import TaurusBaseWidget
from taurus.qt.qtgui.base import TaurusBaseController
from taurus.qt.qtgui.base import TaurusScalarAttributeControllerHelper
from taurus.qt.qtgui.base import TaurusConfigurationControllerHelper
from taurus.qt.qtgui.base import updateLabelBackground

_QT_PLUGIN_INFO = {
    'module' : 'taurus.qt.qtgui.display',
    'group' : 'Taurus Display Widgets',
    'icon' : ":/designer/label.png",
}

TaurusModelType = taurus.core.TaurusElementType
EventType = taurus.core.TaurusEventType


class TaurusLabelController(TaurusBaseController):
    
    StyleSheetTemplate = """border-style: outset; border-width: 2px; border-color: {0}; {1}"""

    def __init__(self, label):
        self._text = ''
        self._trimmedText = False
        TaurusBaseController.__init__(self, label)

    def _setStyle(self):
        TaurusBaseController._setStyle(self)
        label = self.label()
        label.setAlignment(Qt.Qt.AlignRight | Qt.Qt.AlignVCenter)
        # if update as palette
        if self.usePalette():
            label.setFrameShape(Qt.QFrame.Box)
            label.setFrameShadow(Qt.QFrame.Raised)
            label.setLineWidth(1)
    
    def label(self):
        return self.widget()

    def showValueDialog(self, label):
        Qt.QMessageBox.about(label,  "Full text", self._text)

    def _needsStateConnection(self):
        label = self.label()
        ret = 'state' in (label.fgRole, label.bgRole)
        return ret
    
    def _updateForeground(self, label):
        fgRole, value = label.fgRole, ""
        if fgRole == 'value':
            value += self.getDisplayValue()
        elif fgRole == 'w_value':
            value += self.getDisplayValue(True)
        elif fgRole == 'state':
            stateObj = self.stateObj()
            value += stateObj and stateObj.getDisplayValue() or label.getNoneValue()
        elif fgRole == 'quality':
            quality = self.quality()
            if quality is None:
                value += label.getNoneValue()
            else:
                value += str(quality)
        elif fgRole in ('', 'none'):
            pass
        else:
            label.setText("undef")
            return
        
        self._text = label.prefixText + value + label.suffixText
        label.setText(self._text)

        # Checks that the display fits in the widget and sets it to "..." if
        # it does not fit the widget
        self._trimmedText = self._shouldTrim(label, self._text)
        if self._trimmedText:
            label.setText("<a href='...'>...</a>")
    
    def _shouldTrim(self, label, text):
        pointsPerChar = label.font().pointSize()
        size, textSize = label.size(), len(text)*pointsPerChar
        return textSize > size

    def _updateToolTip(self, label):
        toolTip = label.getFormatedToolTip()
        if self._trimmedText:
            toolTip = u"<p><b>Value:</b> %s</p><hr>%s" % (self._text, toolTip)
        label.setToolTip(toolTip)

    _updateBackground = updateLabelBackground

            
class TaurusLabelControllerAttribute(TaurusScalarAttributeControllerHelper, TaurusLabelController):

    def __init__(self, label):
        TaurusScalarAttributeControllerHelper.__init__(self)
        TaurusLabelController.__init__(self, label)

    def _setStyle(self):
        TaurusLabelController._setStyle(self)
        label = self.label()
        label.setTextInteractionFlags(Qt.Qt.TextSelectableByMouse | Qt.Qt.LinksAccessibleByMouse)

        
class TaurusLabelControllerConfiguration(TaurusConfigurationControllerHelper, TaurusLabelController):

    def __init__(self, label):
        TaurusConfigurationControllerHelper.__init__(self)
        TaurusLabelController.__init__(self, label)

    def _setStyle(self):
        TaurusLabelController._setStyle(self)
        label = self.label()
        label.setTextInteractionFlags(Qt.Qt.NoTextInteraction)


#-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
# Design time controllers for label
#-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

class TaurusLabelControllerDesignMode(object):
    
    def _updateLength(self, lcd):
        lcd.setNumDigits(6)
        
    def getDisplayValue(self, write=False):
        v = self.w_value()
        if not write:
            v = self.value()
        return "%6.2f" % v
    
    def value(self):
        return 99.99
    
    def w_value(self):
        return 0.0
        
    def quality(self):
        return PyTango.AttrQuality.ATTR_VALID
    
    def state(self):
        return PyTango.DevState.ON

    def _updateToolTip(self, lcd):
        lcd.setToolTip("Some random value for design purposes only")


class TaurusLabelControllerAttributeDesignMode(TaurusLabelControllerDesignMode, TaurusLabelControllerAttribute):
    
    def __init__(self, label):
        TaurusLabelControllerDesignMode.__init__(self)
        TaurusLabelControllerAttribute.__init__(self, label)


class TaurusLabelControllerConfigurationDesignMode(TaurusLabelControllerDesignMode, TaurusLabelControllerConfiguration):

    def __init__(self, label):
        TaurusLabelControllerDesignMode.__init__(self)
        TaurusLabelControllerConfiguration.__init__(self, label)
    
    def getDisplayValue(self, write=False):
        return "%6.2f" % -99.99
        
    def _updateToolTip(self, lcd):
        lcd.setToolTip("Some random configuration value for design purposes only")


_CONTROLLER_MAP = {
                         None : TaurusLabelController,
      TaurusModelType.Unknown : TaurusLabelController,
    TaurusModelType.Attribute : TaurusLabelControllerAttribute,
TaurusModelType.Configuration : TaurusLabelControllerConfiguration,
}

_DESIGNER_CONTROLLER_MAP = {
                         None : TaurusLabelControllerAttributeDesignMode,
      TaurusModelType.Unknown : TaurusLabelControllerAttributeDesignMode,
    TaurusModelType.Attribute : TaurusLabelControllerAttributeDesignMode,
TaurusModelType.Configuration : TaurusLabelControllerConfigurationDesignMode,
}


class TaurusLabel(Qt.QLabel, TaurusBaseWidget):
    
    DefaultPrefix = ''
    DefaultSuffix = ''
    DefaultBgRole = 'quality'
    DefaultFgRole = 'value'
    DefaultShowText = True
    DefaultModelIndex = None
    
    def __init__(self, parent=None, designMode=False):
        self._prefix = self.DefaultPrefix
        self._suffix = self.DefaultSuffix
        self._bgRole = self.DefaultBgRole
        self._fgRole = self.DefaultFgRole
        self._modelIndex = self.DefaultModelIndex
        self._modelIndexStr = ''
        self._controller = None
        name = self.__class__.__name__
        self.call__init__wo_kw(Qt.QLabel, parent)
        self.call__init__(TaurusBaseWidget, name, designMode=designMode)

        self.connect(self, Qt.SIGNAL("linkActivated (const QString &)"), 
                     self.showValueDialog)

        # if we are in design mode there will be no events so we force the
        # creation of a controller object 
        if self._designMode:
            self.controller().update()

    def _calculate_controller_class(self):
        map = _CONTROLLER_MAP
        if self._designMode:
            map = _DESIGNER_CONTROLLER_MAP
            
        model_type = self.getModelType()
        ctrl_klass = map.get(model_type, TaurusLabelController)
        return ctrl_klass
    
    def controller(self):
        ctrl = self._controller
        # if there is a controller object and it is not the base controller...
        if ctrl is not None and not ctrl.__class__ == TaurusLabelController:
            return ctrl
        
        # if there is a controller object and it is still the same class...
        ctrl_klass = self._calculate_controller_class()
        if ctrl is not None and ctrl.__class__ == ctrl_klass:
            return ctrl
    
        self._controller = ctrl = ctrl_klass(self)
        return ctrl

    def showValueDialog(self, *args):
        self.controller().showValueDialog(self)

    def resizeEvent(self,event):
        # recheck the display every time we resize to make sure the text should
        # become trimmed or not
        self.controller().update()
        Qt.QLabel.resizeEvent(self, event)
        
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # TaurusBaseWidget overwriting
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
   
    def handleEvent(self, evt_src, evt_type, evt_value):
        self.controller().handleEvent(evt_src, evt_type, evt_value)
    
    def isReadOnly(self):
        return True

    def setModel(self, m):
        #force to build another controller
        self._controller = None
        TaurusBaseWidget.setModel(self, m)

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # QT property definition
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    def getModelIndexValue(self):
        return self._modelIndex

    def getModelIndex(self):
        return self._modelIndexStr
    
    def setModelIndex(self, modelIndex):
        mi = str(modelIndex)
        if len(mi) == 0:
            self._modelIndex = None
        else:
            try:
                mi_value = eval(str(mi))
            except:
                return
            if type(mi_value) == int:
                mi_value = mi_value,
            if not operator.isSequenceType(mi_value):
                return
            self._modelIndex = mi_value
        self._modelIndexStr = mi
        self.controller().update()

    def resetModelIndex(self):
        self.setModelIndex(self.DefaultModelIndex)

    def getBgRole(self):
        return self._bgRole
    
    def setBgRole(self, bgRole):
        self._bgRole = str(bgRole).lower()
        self.controller().update()

    def resetBgRole(self):
        self.setBgRole(self.DefaultBgRole)

    def getFgRole(self):
        return self._fgRole
    
    def setFgRole(self, fgRole):
        self._fgRole = str(fgRole).lower()
        self.controller().update()

    def resetFgRole(self):
        self.setFgRole(self.DefaultFgRole)
        
    def getPrefixText(self):
        return self._prefix
    
    def setPrefixText(self,prefix):
        self._prefix = str(prefix)
        self.controller().update()

    def resetPrefixText(self):
        self.setPrefixText(self.DefaultPrefix)
        
    def getSuffixText(self):
        return self._suffix
    
    def setSuffixText(self,suffix):
        self._suffix = str(suffix)
        self.controller().update()
    
    def resetSuffixText(self):
        self.setSuffixText(self.DefaultSuffix)

    @classmethod
    def getQtDesignerPluginInfo(cls):
        d = TaurusBaseWidget.getQtDesignerPluginInfo()
        d.update(_QT_PLUGIN_INFO)
        return d

    #: This property holds the unique URI string representing the model name 
    #: with which this widget will get its data from. The convention used for 
    #: the string can be found :ref:`here <model-concept>`.
    #: 
    #: In case the property :attr:`useParentModel` is set to True, the model 
    #: text must start with a '/' followed by the attribute name.
    #:
    #: **Access functions:**
    #:
    #:     * :meth:`TaurusBaseWidget.getModel`
    #:     * :meth:`TaurusLabel.setModel`
    #:     * :meth:`TaurusBaseWidget.resetModel`
    #:
    #: .. seealso:: :ref:`model-concept`
    model = Qt.pyqtProperty("QString", TaurusBaseWidget.getModel, setModel,
                            TaurusBaseWidget.resetModel)

    #: This property holds whether or not this widget should search in the 
    #: widget hierarchy for a model prefix in a parent widget.
    #:
    #: **Access functions:**
    #:
    #:     * :meth:`TaurusBaseWidget.getUseParentModel`
    #:     * :meth:`TaurusBaseWidget.setUseParentModel`
    #:     * :meth:`TaurusBaseWidget.resetUseParentModel`
    #:
    #: .. seealso:: :ref:`model-concept`
    useParentModel = Qt.pyqtProperty("bool", TaurusBaseWidget.getUseParentModel, 
                                     TaurusBaseWidget.setUseParentModel,
                                     TaurusBaseWidget.resetUseParentModel)

    #: This property holds the index inside the model value that should be
    #: displayed
    #:
    #: **Access functions:**
    #:
    #:     * :meth:`TaurusLabel.getModelIndex`
    #:     * :meth:`TaurusLabel.setModelIndex`
    #:     * :meth:`TaurusLabel.resetModelIndex`
    #:
    #: .. seealso:: :ref:`model-concept`
    modelIndex = Qt.pyqtProperty("QString", getModelIndex, setModelIndex, resetModelIndex)

    #: This property holds a prefix text
    #:
    #: **Access functions:**
    #:
    #:     * :meth:`TaurusLabel.getPrefixText`
    #:     * :meth:`TaurusLabel.setPrefixText`
    #:     * :meth:`TaurusLabel.resetPrefixText`
    prefixText = Qt.pyqtProperty("QString", getPrefixText, setPrefixText, 
                                 resetPrefixText, doc="prefix text")
                                     
    #: This property holds a suffix text
    #:
    #: **Access functions:**
    #:
    #:     * :meth:`TaurusLabel.getSuffixText`
    #:     * :meth:`TaurusLabel.setSuffixText`
    #:     * :meth:`TaurusLabel.resetSuffixText`
    suffixText = Qt.pyqtProperty("QString", getSuffixText, setSuffixText,
                                 resetSuffixText, doc="suffix text")

    #: This property holds the foreground role.
    #: Valid values are:
    #:  
    #:     #. ''/'None' - no value is displayed
    #:     #. 'value' - the value is displayed
    #:     #. 'w_value' - the write value is displayed
    #:     #. 'quality' - the quality is displayed
    #:     #. 'state' - the device state is displayed
    #:
    #: **Access functions:**
    #:
    #:     * :meth:`TaurusLabel.getFgRole`
    #:     * :meth:`TaurusLabel.setFgRole`
    #:     * :meth:`TaurusLabel.resetFgRole`
    fgRole = Qt.pyqtProperty("QString", getFgRole, setFgRole,
                             resetFgRole, doc="foreground role")
                                     
    #: This property holds the background role.
    #: Valid values are ''/'None', 'quality', 'state'
    #:
    #: **Access functions:**
    #:
    #:     * :meth:`TaurusLabel.getBgRole`
    #:     * :meth:`TaurusLabel.setBgRole`
    #:     * :meth:`TaurusLabel.resetBgRole`
    bgRole = Qt.pyqtProperty("QString", getBgRole, setBgRole,
                             resetBgRole, doc="background role")

def demo():
    "Label"
    import demo.tauruslabeldemo
    return demo.tauruslabeldemo.main()

def main():
    import sys
    import taurus.qt.qtgui.application
    Application = taurus.qt.qtgui.application.TaurusApplication
    
    app = Application.instance()
    owns_app = app is None
    
    if owns_app:
        import taurus.core.util.argparse
        parser = taurus.core.util.argparse.get_taurus_parser()
        parser.usage = "%prog [options] <full_attribute_name(s) or full configuration_name(s)>"
        app = Application(sys.argv, cmd_line_parser=parser, 
                          app_name="Taurus label demo", app_version="1.0",
                          org_domain="Taurus", org_name="Tango community")
        
    args = app.get_command_line_args()

    if len(args) == 0:
        w = demo()
    else:
        models = map(str.lower, args)

        w = Qt.QWidget()
        layout = Qt.QGridLayout()
        w.setLayout(layout)
        for model in models:
            label = TaurusLabel()
            label.model = model
            layout.addWidget(label)
    w.show()
    
    if owns_app:
        sys.exit(app.exec_())
    else:
        return w

if __name__ == '__main__':
    main()
    