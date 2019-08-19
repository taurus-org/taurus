#!/usr/bin/env python

#############################################################################
##
# This file is part of Taurus
##
# http://taurus-scada.org
##
# Copyright 2011 CELLS / ALBA Synchrotron, Bellaterra, Spain
##
# Taurus is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
##
# Taurus is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
##
# You should have received a copy of the GNU Lesser General Public License
# along with Taurus.  If not, see <http://www.gnu.org/licenses/>.
##
#############################################################################

"""
qbuttonbox.py:
"""

__all__ = ["QButtonBox"]

__docformat__ = 'restructuredtext'

from taurus.external.qt import Qt


class QButtonBox(Qt.QDialogButtonBox):

    # PyQt Signals

    okClicked = Qt.pyqtSignal()
    openClicked = Qt.pyqtSignal()
    saveClicked = Qt.pyqtSignal()
    cancelClicked = Qt.pyqtSignal()
    closeClicked = Qt.pyqtSignal()
    discardClicked = Qt.pyqtSignal()
    applyClicked = Qt.pyqtSignal()
    resetClicked = Qt.pyqtSignal()
    restoreDefaultsClicked = Qt.pyqtSignal()
    helpClicked = Qt.pyqtSignal()
    resetClicked = Qt.pyqtSignal()
    saveAllClicked = Qt.pyqtSignal()
    yesClicked = Qt.pyqtSignal()
    yesToAllClicked = Qt.pyqtSignal()
    noClicked = Qt.pyqtSignal()
    abortClicked = Qt.pyqtSignal()
    retryClicked = Qt.pyqtSignal()
    ignoreClicked = Qt.pyqtSignal()

    def __init__(self, parent=None, designMode=False, buttons=None,
                 orientation=Qt.Qt.Horizontal):

        if buttons is None:
            buttons = Qt.QDialogButtonBox.Ok | Qt.QDialogButtonBox.Cancel

        Qt.QDialogButtonBox.__init__(self, buttons, orientation, parent)

        self.clicked.connect(self.onClicked)

    def onClicked(self, button):
        if self.standardButton(button) == Qt.QDialogButtonBox.Ok:
            self.okClicked.emit()
        elif self.standardButton(button) == Qt.QDialogButtonBox.Open:
            self.openClicked.emit()
        elif self.standardButton(button) == Qt.QDialogButtonBox.Save:
            self.saveClicked.emit()
        elif self.standardButton(button) == Qt.QDialogButtonBox.Cancel:
            self.cancelClicked.emit()
        elif self.standardButton(button) == Qt.QDialogButtonBox.Close:
            self.closeClicked.emit()
        elif self.standardButton(button) == Qt.QDialogButtonBox.Discard:
            self.discardClicked.emit()
        elif self.standardButton(button) == Qt.QDialogButtonBox.Apply:
            self.applyClicked.emit()
        elif self.standardButton(button) == Qt.QDialogButtonBox.Reset:
            self.resetClicked.emit()
        elif self.standardButton(button) == Qt.QDialogButtonBox.RestoreDefaults:
            self.restoreDefaultsClicked.emit()
        elif self.standardButton(button) == Qt.QDialogButtonBox.Help:
            self.helpClicked.emit()
        elif self.standardButton(button) == Qt.QDialogButtonBox.SaveAll:
            self.saveAllClicked.emit()
        elif self.standardButton(button) == Qt.QDialogButtonBox.Yes:
            self.yesClicked.emit()
        elif self.standardButton(button) == Qt.QDialogButtonBox.YesToAll:
            self.yesToAllClicked.emit()
        elif self.standardButton(button) == Qt.QDialogButtonBox.No:
            self.noClicked.emit()
        elif self.standardButton(button) == Qt.QDialogButtonBox.NoToAll:
            self.noToAllClicked.emit()
        elif self.standardButton(button) == Qt.QDialogButtonBox.Abort:
            self.abortClicked.emit()
        elif self.standardButton(button) == Qt.QDialogButtonBox.Retry:
            self.retryClicked.emit()
        elif self.standardButton(button) == Qt.QDialogButtonBox.Ignore:
            self.ignoreClicked.emit()


if __name__ == "__main__":
    import sys

    def on_ok():
        print('OK!')

    def on_cancel():
        print('Cancel!')


    from taurus.qt.qtgui.application import TaurusApplication

    app = TaurusApplication(sys.argv, cmd_line_parser=None)
    bb = QButtonBox()
    bb.okClicked.connect(on_ok)
    bb.cancelClicked.connect(on_cancel)
    bb.show()

    sys.exit(app.exec_())
