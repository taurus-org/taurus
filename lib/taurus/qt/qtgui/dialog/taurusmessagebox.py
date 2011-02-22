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

"""This module provides a set of dialog based widgets"""

__all__ = ["TaurusMessageBox"]

__docformat__ = 'restructuredtext'

from PyQt4 import Qt

import taurus.core.util
import taurus.qt.qtgui.resource
from taurus.qt.qtgui.panel import TaurusMessagePanel


class TaurusMessageBox(Qt.QDialog):
    """A panel intended to display a taurus error.
    Example::
    
        dev = taurus.Device("sys/tg_test/1")
        try:
            print dev.read_attribute("throw_exception")
        except PyTango.DevFailed, df:
            msgbox = TaurusMessageBox()
            msgbox.show()

    You can show the error outside the exception handling code. If you do this,
    you should keep a record of the exception information as given by
    :func:`sys.exc_info`::
    
        dev = taurus.Device("sys/tg_test/1")
        exc_info = None
        try:
            print dev.read_attribute("throw_exception")
        except PyTango.DevFailed, df:
            exc_info = sys.exc_info()
        
        if exc_info:
            msgbox = TaurusMessageBox(*exc_info)
            msgbox.show()"""
    
    def __init__(self, err_type=None, err_value=None, err_traceback=None, parent=None, designMode=False):
        Qt.QDialog.__init__(self, parent)
        layout = Qt.QVBoxLayout()
        self.setLayout(layout)
        self._panel = TaurusMessagePanel(err_type, err_value, err_traceback, self, designMode)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._panel)
        self.connect(self.panel().buttonBox(), Qt.SIGNAL("accepted()"), self.accept)
        self.connect(self._panel, Qt.SIGNAL("toggledDetails(bool)"), self._onShowDetails)
    
    def _onShowDetails(self, show):
        self.adjustSize()
    
    def panel(self):
        """Returns the :class:`taurus.qt.qtgui.panel.TaurusMessagePanel`.
        
        :return: the internal panel
        :rtype: taurus.qt.qtgui.panel.TaurusMessagePanel"""
        return self._panel
    
    def addButton(self, button, role=Qt.QDialogButtonBox.ActionRole):
        """Adds the given button with the given to the button box
        
        :param button: the button to be added
        :type button: PyQt4.QtGui.QPushButton
        :param role: button role
        :type role: PyQt4.Qt.QDialogButtonBox.ButtonRole"""
        self.panel().addButton(button, role)
    
    def setIconPixmap(self, pixmap):
        """Sets the icon to the dialog
        
        :param pixmap: the icon pixmap
        :type pixmap: PyQt4.Qt.QPixmap"""
        self._panel.setIconPixmap(pixmap)
    
    def setText(self, text):
        """Sets the text of the dialog
        
        :param text: the new text
        :type text: str"""
        self._panel.setText(text)
    
    def setDetailedText(self, text):
        """Sets the detailed text of the dialog
        
        :param text: the new text
        :type text: str"""
        self._panel.setDetailedText(text)
    
    def setError(self, err_type=None, err_value=None, err_traceback=None):
        """Sets the exception object.
        Example usage::
        
            dev = taurus.Device("sys/tg_test/1")
            exc_info = None
            msgbox = TaurusMessageBox()
            try:
                print dev.read_attribute("throw_exception")
            except PyTango.DevFailed, df:
                exc_info = sys.exc_info()
            
            if exc_info:
                msgbox.setError(*exc_info)
                msgbox.show()
        
        :param err_type: the exception type of the exception being handled (a class object)
        :type error: class object
        :param err_value: exception object
        :type err_value: object
        :param err_traceback: a traceback object which encapsulates the call 
                              stack at the point where the exception originally
                              occurred
        :type err_traceback: traceback"""
        self._panel.setError(err_type, err_value, err_traceback)

class DemoException(Exception):
    pass

def s1():
    return s2()

def s2():
    return s3()

def s3():
    raise DemoException("A demo exception occurred")

def py_exc():
    import sys
    try:
        s1()
    except:
        msgbox = TaurusMessageBox(*sys.exc_info())
        msgbox.exec_()

def tg_exc():
    import sys
    import PyTango
    try:
        PyTango.Except.throw_exception('TangoException', 'A simple tango exception', 'right here')
    except PyTango.DevFailed:
        msgbox = TaurusMessageBox(*sys.exc_info())
        msgbox.exec_()

def tg_serv_exc():
    import sys
    import PyTango
    dev = taurus.Device("sys/tg_test/1")
    exc_info = None
    try:
        dev.read_attribute("throw_exception")
    except PyTango.DevFailed, df:
        msgbox = TaurusMessageBox(*sys.exc_info())
        msgbox.exec_()
    except:
        msgbox = TaurusMessageBox(*sys.exc_info())
        msgbox.exec_()

def py_tg_serv_exc():
    import sys
    import PyTango
    try:
        PyTango.Except.throw_exception('TangoException', 'A simple tango exception', 'right here')
    except PyTango.DevFailed, df1:
        try:
            import traceback, StringIO
            origin = StringIO.StringIO()
            traceback.print_stack(file=origin)
            origin.seek(0)
            origin = origin.read()
            PyTango.Except.re_throw_exception(df1, 'PyDs_Exception', 'DevFailed: A simple tango exception', origin)
        except PyTango.DevFailed:
            msgbox = TaurusMessageBox(*sys.exc_info())
            msgbox.exec_()

def demo():
    """Message dialog"""
    panel = Qt.QWidget()
    layout = Qt.QVBoxLayout()
    panel.setLayout(layout)
    
    m1 = Qt.QPushButton("Python exception")
    layout.addWidget(m1)
    Qt.QObject.connect(m1, Qt.SIGNAL("clicked()"), py_exc)
    m2 = Qt.QPushButton("Tango exception")
    layout.addWidget(m2)
    Qt.QObject.connect(m2, Qt.SIGNAL("clicked()"), tg_exc)
    layout.addWidget(m2)
    m3 = Qt.QPushButton("Tango server exception")
    layout.addWidget(m3)
    Qt.QObject.connect(m3, Qt.SIGNAL("clicked()"), tg_serv_exc)
    layout.addWidget(m3)
    m4 = Qt.QPushButton("Python tango server exception")
    layout.addWidget(m4)
    Qt.QObject.connect(m4, Qt.SIGNAL("clicked()"), py_tg_serv_exc)
    layout.addWidget(m4)

    panel.show()
    return panel
    
def main():
    
    import sys
    import taurus.qt.qtgui.application

    Application = taurus.qt.qtgui.application.TaurusApplication
    
    app = Application.instance()
    owns_app = app is None
    
    if owns_app:
        app = Qt.QApplication([])
        app.setApplicationName("Taurus message demo")
        app.setApplicationVersion("1.0")

    w = demo()
    
    if owns_app:
        sys.exit(app.exec_())
    else:
        return panel

if __name__ == "__main__":
    main()
    