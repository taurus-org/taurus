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
macrodescriptionviewer.py: 
"""

from taurus.qt import Qt

from taurus.qt.qtgui.base import TaurusBaseWidget
import taurus.core

class TaurusMacroDescriptionViewer(Qt.QTextEdit, TaurusBaseWidget):
    __pyqtSignals__ = ("modelChanged(const QString &)",)
    
    def __init__(self, parent = None, designMode = False):
        name = "TaurusMacroDescriptionView"
        self.call__init__wo_kw(Qt.QTextEdit, parent)
        self.call__init__(TaurusBaseWidget, name)
        self.setReadOnly(True)
        self.setFont(Qt.QFont("Courier",9))
        
    def defineStyle(self):
        """ Defines the initial style for the widget """
        self.updateStyle()

    def getModelClass(self):
        return taurus.core.taurusdevice.TaurusDevice

    def updateStyle(self):
        self.update()
        
    def onMacroNameChanged(self, macroName):
        """Can be connected to an event emitted after macro name was changed.
           As an argument receives macroName and ask BaseMacroServer object 
           about already prepared and stored in MacroInfoObj object macro description"""
        macroServer = self.getModelObj()
        
        if macroServer is None or macroName is None or macroName == "":
            self.setText("")
            return
        
        self.setText(str(macroServer.getMacroInfoObj(macroName).doc))

    def getFormatedToolTip(self,cache=True):
        """This method was overridden to get rid of the default tooltip of TaurusWidget"""
        return ""
        
        
    model = Qt.pyqtProperty("QString", 
                                TaurusBaseWidget.getModel, 
                                TaurusBaseWidget.setModel, 
                                TaurusBaseWidget.resetModel)
    
    useParentModel = Qt.pyqtProperty("bool", 
                                         TaurusBaseWidget.getUseParentModel, 
                                         TaurusBaseWidget.setUseParentModel,
                                         TaurusBaseWidget.resetUseParentModel)
    
def test():
    from taurus.core.tango.sardana.macroserver import registerExtensions
    import sys    
    registerExtensions()
    app = Qt.QApplication(sys.argv)
    taurusMacroDescriptionView = TaurusMacroDescriptionViewer(designMode=1)
    if len(sys.argv) != 2:
        taurusMacroDescriptionView.setModel("macroserver/zreszela/1")
    else:
        taurusMacroDescriptionView.setModel(sys.argv[1])
    taurusMacroDescriptionView.onMacroChanged("mv")
    taurusMacroDescriptionView.show()
    sys.exit(app.exec_())
    
       
if __name__ == "__main__":
    test()


