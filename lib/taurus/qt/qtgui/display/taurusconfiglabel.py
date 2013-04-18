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

__all__ = ["TaurusConfigLabel"]

__docformat__ = 'restructuredtext'

from taurus.qt import Qt

import taurus.core
from taurus.qt.qtgui.util import QT_DEVICE_STATE_PALETTE
from taurus.qt.qtgui.base import TaurusBaseWidget


class TaurusConfigLabel(Qt.QLabel, TaurusBaseWidget):
    """
       A label widget displaying the tango attribute configuration.
       
    .. deprecated:: 2.0
           Use :class:`taurus.qt.qtgui.display.TaurusLabel` instead.
    """
    __pyqtSignals__ = ("modelChanged(const QString &)",)

    def __init__(self, parent = None, designMode = False):
        name = "TaurusConfigLabel"
        self._prefix = ''
        self._suffix = ''
        self._configParam = None
        self._extra_style = ''
        self.call__init__wo_kw(Qt.QLabel, parent)
        self.call__init__(TaurusBaseWidget, name, designMode=designMode)
        
        self.setAlignment(Qt.Qt.AlignVCenter)
        
    def defineStyle(self):
        
        palette = self.palette()
        
        # define a default background color in case the model is not connected
        bg_brush, fg_brush = QT_DEVICE_STATE_PALETTE.qbrush(None)
        palette.setBrush(Qt.QPalette.Window,bg_brush)
        palette.setBrush(Qt.QPalette.Base,bg_brush)
        palette.setBrush(Qt.QPalette.WindowText,fg_brush)
        self.setPalette(palette) # mandatory since PyQt 4.5
        self.updateStyle()

    def sizeHint(self):
        return Qt.QSize(60, 24)

    def getConfigurationAttributeValue(self):
        """Helper method to get the proper parameter value from the configuration"""
        model = self.getModelObj()
        if model is None:
            return self.getNoneValue()
        try:
            val = getattr(model, str(self._configParam))
            try:
                no_val = getattr(model, "no_" + str(self._configParam))
                if val.lower() == no_val.lower():
                    val = self.getNoneValue()
            except:
                pass
        except:
            self.debug("Invalid configuration parameter %s" % self._configParam)
            val = self.getNoneValue()
        return val

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # TaurusBaseWidget overwriting
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    
    def getModelClass(self):
        return taurus.core.taurusconfiguration.TaurusConfiguration

    def getDisplayValue(self):
        cfg_value = self.getConfigurationAttributeValue()
        cfg_value = (self._prefix or '') + (cfg_value or '') + (self._suffix or '')
        return cfg_value

    def getFormatedToolTip(self,cache=True):
        obj = self.getModelObj()
        if obj is None:
            return Qt.QString.fromLatin1(self.getNoneValue())
        p = obj.getParentObj()
        if p is None:
            return Qt.QString.fromLatin1(self.getNoneValue())
        return Qt.QString.fromLatin1("<HTML>" + self._configParam + ' for ' + p.getDisplayName())
    
    def isReadOnly(self):
        return True
    
    def setStyleSheet(self, ss):
        ss = str(ss)
        self._extra_style = ss
        if not self.getModelValueObj():
            ss = """TaurusConfigLabel { 
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                              stop: 0.00 rgb(240,240,240),
                              stop: 0.33 rgb(200,200,200),
                              stop: 0.66 rgb(240,240,240),
                              stop: 1.00 rgb(200,200,200));
                color: gray;
            %s}""" % (ss)
        else:
            ss = """TaurusConfigLabel { %s }""" % ss
        Qt.QLabel.setStyleSheet(self, ss)
        
    def updateStyle(self):
        self.setStyleSheet(self._extra_style)
        self.updatePendingOpsStyle()
    
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # QT properties 
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
   
    @Qt.pyqtSignature("setModel(QString)")
    def setModel(self, model):
        model = str(model)
        try:
            self._configParam = model[model.rfind('=')+1:].lower()
        except:
            self._configParam = ''
        TaurusBaseWidget.setModel(self,model)
    
    def getPrefixText(self):
        return self._prefix
    
    @Qt.pyqtSignature("setPrefixText(QString)")
    def setPrefixText(self,prefix):
        self._prefix = prefix
        self.fireEvent(evt_type = taurus.core.taurusbasetypes.TaurusEventType.Change)

    def resetPrefixText(self):
        self.setPrefixText('')
        
    def getSuffixText(self):
        return self._suffix
    
    @Qt.pyqtSignature("setSuffixText(QString)")
    def setSuffixText(self,suffix):
        self._suffix = suffix
        self.fireEvent(evt_type = taurus.core.taurusbasetypes.TaurusEventType.Change)
    
    def resetSuffixText(self):
        self.setSuffixText('')

    @classmethod
    def getQtDesignerPluginInfo(cls):
        return None
#        ret = TaurusBaseWidget.getQtDesignerPluginInfo()
#        ret['module'] = 'taurus.qt.qtgui.display'
#        ret['group'] = 'Taurus Widgets [Old]'
#        ret['icon'] = ":/designer/label.png"
#        return ret
    
    model = Qt.pyqtProperty("QString", TaurusBaseWidget.getModel, setModel, 
                            TaurusBaseWidget.resetModel)
                                
    useParentModel = Qt.pyqtProperty("bool", TaurusBaseWidget.getUseParentModel, 
                                     TaurusBaseWidget.setUseParentModel,
                                     TaurusBaseWidget.resetUseParentModel)
                                         
    prefixText = Qt.pyqtProperty("QString", getPrefixText, setPrefixText, 
                                 resetPrefixText, doc="prefix text (optional)")
                                     
    suffixText = Qt.pyqtProperty("QString", getSuffixText, setSuffixText, 
                                 resetSuffixText, doc="suffix text (optional)")


def main():
    """hello"""
    import sys
    import taurus.qt.qtgui.application
    Application = taurus.qt.qtgui.application.TaurusApplication
    
    app = Application.instance()
    owns_app = app is None
    
    if owns_app:
        import taurus.core.util.argparse
        parser = taurus.core.util.argparse.get_taurus_parser()
        parser.usage = "%prog [options] <full configuration_name(s)>"
        app = Application(sys.argv, cmd_line_parser=parser)
        
    args = app.get_command_line_args()

    if len(args) > 0:
        models = map(str.lower, args)
    else:
        models = [ 'sys/tg_test/1/%s?configuration=label' % a for a in ('state', 'status', 'double_scalar' ) ]

    w = Qt.QWidget()
    layout = Qt.QGridLayout()
    w.setLayout(layout)
    for model in models:
        label = TaurusConfigLabel()
        label.model = model
        layout.addWidget(label)
    w.show()
    
    if owns_app:
        sys.exit(app.exec_())
    else:
        return w

if __name__ == '__main__':
    main()
