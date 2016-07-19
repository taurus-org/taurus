# !/usr/bin/env python

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

"""This module provides a set of dialog based widgets"""

__all__ = ["TaurusConfigurationDialog"]

__docformat__ = 'restructuredtext'

from taurus.external.qt import Qt
from taurus.qt.qtgui.panel.taurusconfigurationpanel import TaurusConfigurationPanel


class TaurusConfigurationDialog(Qt.QDialog):

    def __init__(self, parent=None, designMode=False):
        Qt.QDialog.__init__(self, parent)
        self.setWindowTitle('TaurusConfigurationDialog')
        layout = Qt.QVBoxLayout()
        self.setLayout(layout)
        ConfigPanel = TaurusConfigurationPanel
        self._panel = ConfigPanel(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._panel)
        self._panel._ui.pushButtonOk.setVisible(True)
        self._panel._ui.pushButtonCancel.setVisible(True)
        self._panel._ui.pushButtonOk.clicked.connect(self._onOk)
        self._panel._ui.pushButtonCancel.clicked.connect(self._onCancel)
        self.adjustSize()
        self.show()

    def _onOk(self):
        self._panel._onOk()
        self._onCancel()

    def _onCancel(self):
        self.close()

    def setModel(self, model):
        self._panel.setModel(model)


def main():
    import sys
    attr_name = sys.argv[1]
    a = Qt.QApplication([])
    d = TaurusConfigurationDialog()
    d.setModel(attr_name)
    return a.exec_()

if __name__ == "__main__":
    import sys
    sys.exit(main())
