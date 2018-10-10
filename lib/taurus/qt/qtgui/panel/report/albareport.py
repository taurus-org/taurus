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

"""This module provides a panel to display taurus messages"""

from taurus.external.qt import Qt
from taurus.qt.qtgui.panel.report.basicreport import (SendMailDialog,
                                                      SMTPReportHandler)


__package__ = 'taurus.qt.qtgui.panel.report'

__all__ = ["TicketReportHandler"]

__docformat__ = 'restructuredtext'


class SendTicketDialog(SendMailDialog):

    def __init__(self, parent=None):
        SendMailDialog.__init__(self, parent=parent)
        self.ui.editTo.setParent(None)
        self.ui.editTo = Qt.QComboBox(self)
        self.ui.editTo.setEditable(True)
        self.ui.editTo.addItems(["controls", "mis", "electronics",
                                 "systems"])
        self.ui.editTo.setCurrentIndex(0)
        self.ui.mainLayout.addWidget(self.ui.editTo, 1, 1, 1, 1)

    def getTo(self):
        return str(self.ui.editTo.currentText() + "@rt.cells.es")


class TicketReportHandler(SMTPReportHandler):
    """Report a message by sending an ALBA ticket"""

    Label = "Send ticket"

    def getDialogClass(self):
        return SendTicketDialog


def main():
    app = Qt.QApplication([])
    w = SendTicketDialog()
    w.exec_()

if __name__ == "__main__":
    main()
