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

__all__ = ["ClipboardReportHandler", "SMTPReportHandler"]

__docformat__ = 'restructuredtext'

from taurus.core.util.report import TaurusMessageReportHandler
from taurus.external.qt import Qt
from taurus.qt.qtgui.util.ui import UILoadable


class ClipboardReportHandler(TaurusMessageReportHandler):
    """Report a message by copying it to the clipboard"""

    Label = "Copy to Clipboard"

    def report(self, message):
        app = Qt.QApplication.instance()
        clipboard = app.clipboard()
        clipboard.setText(message)

        Qt.QMessageBox.information(None, "Done!",
                                   "Message Copied to clipboard")


@UILoadable(with_ui='ui')
class SendMailDialog(Qt.QDialog):

    def __init__(self, parent=None):
        Qt.QDialog.__init__(self, parent)
        self.loadUi(filename="SendMailForm.ui")
        self.ui.buttonBox.accepted.connect(self.accept)
        self.ui.buttonBox.rejected.connect(self.reject)
        self.ui.editMessage.setFont(Qt.QFont("Monospace"))

    def setFrom(self, efrom):
        self.ui.lineEditFrom.setText(efrom)

    def setTo(self, eto):
        self.ui.editTo.setText(eto)

    def setSubject(self, subject):
        self.ui.editSubject.setText(subject)

    def setMessage(self, message):
        self.ui.editMessage.setPlainText(message)

    def getFrom(self):
        return str(self.ui.editFrom.text())

    def getTo(self):
        return str(self.ui.editTo.text())

    def getSubject(self):
        return str(self.ui.editSubject.text())

    def getMessage(self):
        return str(self.ui.editMessage.toPlainText())

    def getMailInfo(self):
        return self.getFrom(), self.getTo(), self.getSubject(), \
            self.getMessage()


class SMTPReportHandler(TaurusMessageReportHandler):
    """Report a message by sending an email"""

    Label = "Send email"

    def report(self, message):

        app = Qt.QApplication.instance()

        subject = "Error in " + app.applicationName()
        dialog = self.createDialog(subject=subject, message=message)

        if not dialog.exec_():
            return

        mail_info = dialog.getMailInfo()

        try:
            self.sendMail(*mail_info)
            Qt.QMessageBox.information(None, "Done!",
                                       "Email has been sent!")
        except:
            import sys
            import traceback
            einfo = sys.exc_info()[:2]
            msg = "".join(traceback.format_exception_only(*einfo))
            Qt.QMessageBox.warning(None, "Failed to send email",
                                   "Failed to send email. Reason:\n\n" + msg)

    def sendMail(self, efrom, eto, subject, message):
        import smtplib
        import email.mime.text
        msg = email.mime.text.MIMEText(message)
        msg['From'] = efrom
        msg['To'] = eto
        msg['Subject'] = subject

        s = smtplib.SMTP('localhost')
        s.sendmail(efrom, eto, msg.as_string())
        s.quit()

    def getDialogClass(self):
        return SendMailDialog

    def createDialog(self, efrom=None, eto=None, subject=None, message=None):
        dialog = self.getDialogClass()()
        dialog.setWindowTitle("Compose message")
        if efrom is not None:
            dialog.setFrom(efrom)
        if eto is not None:
            dialog.setFrom(eto)
        if subject is not None:
            dialog.setSubject(subject)
        if message is not None:
            dialog.setMessage(message)
        return dialog


def main():
    app = Qt.QApplication([])
    w = SendMailDialog()
    w.exec_()

if __name__ == "__main__":
    main()
