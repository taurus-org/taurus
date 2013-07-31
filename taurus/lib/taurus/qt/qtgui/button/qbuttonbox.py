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
qbuttonbox.py: 
"""

__all__ = ["QButtonBox"]

__docformat__ = 'restructuredtext'

from taurus.qt import Qt

class QButtonBox(Qt.QDialogButtonBox):
    __pyqtSignals__ = ("okClicked()","openClicked()", "saveClicked()", "cancelClicked()",
                       "closeClicked()", "discardClicked()", "applyClicked()", "resetClicked()",
                       "restoreDefaultsClicked()","helpClicked()","resetClicked()","saveAllClicked()",
                       "yesClicked()","yesToAllClicked()","noClicked()","abortClicked()",
                       "retryClicked()","ignoreClicked()")
    
    def __init__(self, parent = None, designMode = False, buttons = None,
                 orientation = Qt.Qt.Horizontal):
        
        if buttons is None:
            buttons = Qt.QDialogButtonBox.Ok | Qt.QDialogButtonBox.Cancel
    
        Qt.QDialogButtonBox.__init__(self, buttons, orientation, parent)
        
        Qt.QObject.connect(self, Qt.SIGNAL("clicked(QAbstractButton *)"), self.onClicked)
        
    def onClicked(self, button):
        if self.standardButton(button) == Qt.QDialogButtonBox.Ok:
            self.emit(Qt.SIGNAL("okClicked()"))
        elif self.standardButton(button) == Qt.QDialogButtonBox.Open:
            self.emit(Qt.SIGNAL("openClicked()"))
        elif self.standardButton(button) == Qt.QDialogButtonBox.Save:
            self.emit(Qt.SIGNAL("saveClicked()"))
        elif self.standardButton(button) == Qt.QDialogButtonBox.Cancel:
            self.emit(Qt.SIGNAL("cancelClicked()"))
        elif self.standardButton(button) == Qt.QDialogButtonBox.Close:
            self.emit(Qt.SIGNAL("closeClicked()"))
        elif self.standardButton(button) == Qt.QDialogButtonBox.Discard:
            self.emit(Qt.SIGNAL("discardClicked()"))
        elif self.standardButton(button) == Qt.QDialogButtonBox.Apply:
            self.emit(Qt.SIGNAL("applyClicked()"))
        elif self.standardButton(button) == Qt.QDialogButtonBox.Reset:
            self.emit(Qt.SIGNAL("resetClicked()"))
        elif self.standardButton(button) == Qt.QDialogButtonBox.RestoreDefaults:
            self.emit(Qt.SIGNAL("restoreDefaultsClicked()"))
        elif self.standardButton(button) == Qt.QDialogButtonBox.Help:
            self.emit(Qt.SIGNAL("helpClicked()"))
        elif self.standardButton(button) == Qt.QDialogButtonBox.SaveAll:
            self.emit(Qt.SIGNAL("saveAllClicked()"))
        elif self.standardButton(button) == Qt.QDialogButtonBox.Yes:
            self.emit(Qt.SIGNAL("yesClicked()"))
        elif self.standardButton(button) == Qt.QDialogButtonBox.YesToAll:
            self.emit(Qt.SIGNAL("yesToAllClicked()"))
        elif self.standardButton(button) == Qt.QDialogButtonBox.No:
            self.emit(Qt.SIGNAL("noClicked()"))
        elif self.standardButton(button) == Qt.QDialogButtonBox.NoToAll:
            self.emit(Qt.SIGNAL("noToAllClicked()"))
        elif self.standardButton(button) == Qt.QDialogButtonBox.Abort:
            self.emit(Qt.SIGNAL("abortClicked()"))
        elif self.standardButton(button) == Qt.QDialogButtonBox.Retry:
            self.emit(Qt.SIGNAL("retryClicked()"))
        elif self.standardButton(button) == Qt.QDialogButtonBox.Ignore:
            self.emit(Qt.SIGNAL("ignoreClicked()"))


if __name__ == "__main__":
    import sys
    
    app = Qt.QApplication(sys.argv)
    bb = TaurusButtonBox()
    bb.show()

    sys.exit(app.exec_())