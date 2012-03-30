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

"""This module provides a panel to display taurus messages"""

__all__ = ["ClipboardReportHandler", "SmtpReportHandler"]

__docformat__ = 'restructuredtext'

from taurus.core.util.report import TaurusMessageReportHandler
from taurus.qt import Qt

class ClipboardReportHandler(TaurusMessageReportHandler):
    """Report a message by copying it to the clipboard"""
    
    Label = "Copy to Clipboard"
    
    def report(self, message):
        app = Qt.QApplication.instance()
        clipboard = app.clipboard()
        clipboard.setText(message)
        
        Qt.QMessageBox.information(self.parent, "Done!", "Message Copied to clipboard")
    

class SmtpReportHandler(TaurusMessageReportHandler):
    """Report a message by sending an email"""
    
    Label = "Send email"
    
    def report(self, message):
        import smtplib
        import email.mime.text
        
        app = Qt.QApplication.instance()
        efrom, ok = Qt.QInputDialog.getText(None, "Email From", "From:")
        efrom = str(efrom)
        if not ok:
            return
        
        eto, ok = Qt.QInputDialog.getText(None, "Email To", "To:")
        eto = str(eto).split(",")
        if not ok:
            return
        
        subject, ok = Qt.QInputDialog.getText(None, "Subject",
                                              "Subject:",Qt.QLineEdit.Normal,
                                              "Error in " + app.applicationName())
        subject = str(subject)
        if not ok:
            return
        
        msg = email.mime.text.MIMEText(message)
        app = Qt.QApplication.instance()
        msg['From'] = efrom
        msg['To'] = eto[0]
        msg['Subject'] = subject
        
        s = smtplib.SMTP('localhost')
        s.sendmail(efrom, eto, msg.as_string())
        s.quit()

if False:
    class TicketReportHandler(TaurusMessageReportHandler):
        """Report a message by sending an email"""
        
        Label = "Send ticket"
        
        def report(self, message):
            import smtplib
            import email.mime.text
            
            app = Qt.QApplication.instance()
            efrom, ok = Qt.QInputDialog.getText(None, "Email From", "From:")
            efrom = str(efrom)
            if not ok:
                return
            
            options = [ i+"@rt.cells.es" for i in ["controls", "mis", "electronics", "systems"] ]
            eto, ok = Qt.QInputDialog.getItem(None, "Email To", "To:", options)
            eto = str(eto)
            if not ok:
                return
            
            subject, ok = Qt.QInputDialog.getText(None, "Subject",
                                                  "Subject:",Qt.QLineEdit.Normal,
                                                  "Error in " + app.applicationName())
            subject = str(subject)
            if not ok:
                return
            
            msg = email.mime.text.MIMEText(message)
            app = Qt.QApplication.instance()
            msg['From'] = efrom
            msg['To'] = eto[0]
            msg['Subject'] = subject
            
            s = smtplib.SMTP('localhost')
            s.sendmail(efrom, eto, msg.as_string())
            s.quit()