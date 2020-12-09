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

"""This module provides a set of dialog based widgets"""

from future import standard_library
standard_library.install_aliases()

from builtins import object

import sys

from taurus.external.qt import Qt
from taurus.core.util.excepthook import BaseExceptHook
from taurus.core.util.log import LogExceptHook
from taurus.core.util.wrap import wraps


__all__ = ["TaurusMessageBox", "protectTaurusMessageBox",
           "ProtectTaurusMessageBox", "TaurusExceptHookMessageBox"]

__docformat__ = 'restructuredtext'


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

    def __init__(self, err_type=None, err_value=None, err_traceback=None,
                 parent=None, designMode=False):
        Qt.QDialog.__init__(self, parent)
        layout = Qt.QVBoxLayout()
        self.setLayout(layout)
        import taurus.qt.qtgui.panel
        MsgPanel = taurus.qt.qtgui.panel.TaurusMessagePanel
        self._panel = MsgPanel(err_type, err_value, err_traceback,
                               self, designMode)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._panel)
        self.panel().buttonBox().accepted.connect(self.accept)
        self._panel.toggledDetails.connect(self._onShowDetails)

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

    def getText(self):
        """Returns the current text of this panel

        :return: the text for this panel
        :rtype: str"""
        return self._panel.getText()

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

        :param err_type: the exception type of the exception being handled
                         (a class object)
        :type error: class object
        :param err_value: exception object
        :type err_value: object
        :param err_traceback: a traceback object which encapsulates the call
                              stack at the point where the exception originally
                              occurred
        :type err_traceback: TracebackType"""
        self._panel.setError(err_type, err_value, err_traceback)


_PROTECT_MESSAGE_BOX = None


def _ProtectMessageBox(err_type=None, err_value=None, err_traceback=None,
                       parent=None):
    global _PROTECT_MESSAGE_BOX
    box = _PROTECT_MESSAGE_BOX
    if box is None:
        _PROTECT_MESSAGE_BOX = box = TaurusMessageBox(err_type=err_type,
                                                      err_value=err_value, err_traceback=err_traceback, parent=parent)
        box.panel().setCheckBoxVisible(True)
    else:
        box.setError(err_type=err_type, err_value=err_value,
                     err_traceback=err_traceback)
    if box.panel().checkBoxState() == Qt.Qt.Checked:
        return
    return box


def protectTaurusMessageBox(fn):
    """The idea of this function is to be used as a decorator on any method
    you which to protect against exceptions. The handle of the exception is to
    display a :class:`TaurusMessageBox` with the exception information.
    Example::

        @protectTaurusMessgeBox
        def turnBeamOn(device_name):
            d = taurus.Device(device_name)
            d.TurnOn()
    """

    @wraps(fn)
    def wrapped(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except:
            msgbox = _ProtectMessageBox(*sys.exc_info())
            if msgbox is None:
                return
            msgbox.exec_()
    return wrapped


class ProtectTaurusMessageBox(object):
    """The idea of this class is to be used as a decorator on any method
    you which to protect against exceptions. The handle of the exception is to
    display a :class:`TaurusMessageBox` with the exception information. The
    optional parameter title gives the window bar a customized title. The
    optional parameter msg allows you to give a customized message in the
    dialog. Example::

        @ProtectTaurusMessgeBox(title="Error trying to turn the beam on")
        def turnBeamOn(device_name):
            d = taurus.Device(device_name)
            d.TurnOn()
    """

    def __init__(self, title=None, msg=None):
        self._title = title
        self._msg = msg

    def __call__(self, fn):
        @wraps(fn)
        def wrapped(*args, **kwargs):
            try:
                return fn(*args, **kwargs)
            except:
                msgbox = _ProtectMessageBox(*sys.exc_info())
                if msgbox is None:
                    return
                if self._title is not None:
                    msgbox.setWindowTitle(self._title)
                if self._msg is not None:
                    msgbox.setText(self._msg)
                msgbox.exec_()
        return wrapped


class TaurusExceptHookMessageBox(BaseExceptHook):
    """A callable class that acts as an excepthook that displays an unhandled
    exception in a :class:`~taurus.qt.qtgui.dialog.TaurusMessageBox`.

    :param hook_to: callable excepthook that will be called at the end of
                    this hook handling [default: None]
    :type hook_to: callable
    :param title: message box title [default: None meaning use exception value]
    :type name: str
    :param msg: message box text [default: None meaning use exception]"""

    MSG_BOX = None

    def __init__(self, hook_to=None, title=None, msg=None):
        BaseExceptHook.__init__(self, hook_to=hook_to)
        self._title = title
        self._msg = msg

    def _getMessageBox(self, err_type=None, err_value=None, err_traceback=None,
                       parent=None):
        box = self.__class__.MSG_BOX

        if box is None:
            self.__class__.MSG_BOX = box = TaurusMessageBox(err_type=err_type,
                                                            err_value=err_value, err_traceback=err_traceback, parent=parent)
            box.panel().setCheckBoxVisible(True)
        else:
            box.setError(err_type=err_type, err_value=err_value,
                         err_traceback=err_traceback)
        if box.panel().checkBoxState() == Qt.Qt.Checked:
            return
        return box

    def report(self, *exc_info):
        app = Qt.QApplication.instance()
        if app is None:
            import taurus.core.util
            LogExceptHook().report(*exc_info)
            return
        msgbox = self._getMessageBox(*exc_info)
        if msgbox is None:
            return
        if self._title is not None:
            msgbox.setWindowTitle(self._title)
        if self._msg is not None:
            msgbox.setText(self._msg)
        msgbox.exec_()


class DemoException(Exception):
    pass


def s1():
    return s2()


def s2():
    return s3()


def s3():
    raise DemoException("A demo exception occurred")


def py_exc():
    try:
        s1()
    except:
        msgbox = TaurusMessageBox(*sys.exc_info())
        msgbox.exec_()


def tg_exc():
    import PyTango  # TODO: tango-centric
    try:
        PyTango.Except.throw_exception('TangoException',
                                       'A simple tango exception', 'right here')
    except PyTango.DevFailed:
        msgbox = TaurusMessageBox(*sys.exc_info())
        msgbox.exec_()


def tg_serv_exc():
    import PyTango  # TODO: tango-centric
    import taurus
    dev = taurus.Device("sys/tg_test/1")
    try:
        dev.read_attribute("throw_exception")
    except PyTango.DevFailed:
        msgbox = TaurusMessageBox(*sys.exc_info())
        msgbox.exec_()
    except:
        msgbox = TaurusMessageBox(*sys.exc_info())
        msgbox.exec_()


def py_tg_serv_exc():
    import PyTango  # TODO: tango-centric
    try:
        PyTango.Except.throw_exception('TangoException',
                                       'A simple tango exception', 'right here')
    except PyTango.DevFailed as df1:
        try:
            import traceback
            # ---------------------------------------------------------------
            # workaround for unicode issues on py2 when using io instead of
            # StringIO
            try:
                import StringIO as io  # py2
            except ImportError:
                import io  # py3
            # ----------------------------------------------------------------
            origin = io.StringIO()
            traceback.print_stack(file=origin)
            origin.seek(0)
            origin = origin.read()
            PyTango.Except.re_throw_exception(df1, 'PyDs_Exception',
                                              'DevFailed: A simple tango '
                                              'exception', origin)
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
    m1.clicked.connect(py_exc)
    m2 = Qt.QPushButton("Tango exception")
    layout.addWidget(m2)
    m2.clicked.connect(tg_exc)
    layout.addWidget(m2)
    m3 = Qt.QPushButton("Tango server exception")
    layout.addWidget(m3)
    m3.clicked.connect(tg_serv_exc)
    layout.addWidget(m3)
    m4 = Qt.QPushButton("Python tango server exception")
    layout.addWidget(m4)
    m4.clicked.connect(py_tg_serv_exc)
    layout.addWidget(m4)

    panel.show()
    return panel


def main():
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
        return w

if __name__ == "__main__":
    main()
