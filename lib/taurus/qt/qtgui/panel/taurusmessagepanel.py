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

from future import standard_library
standard_library.install_aliases()
from builtins import object

import sys
import traceback
import datetime

try:
    import pygments
    from pygments import highlight
    from pygments.formatters import HtmlFormatter
    from pygments.lexers import PythonTracebackLexer
except:
    pygments = None

from taurus.core.util.report import TaurusMessageReportHandler
from taurus.external.qt import Qt
from taurus.qt.qtgui.util.ui import UILoadable


__all__ = ["TaurusMessagePanel", "TaurusMessageErrorHandler",
           "TangoMessageErrorHandler", "MacroServerMessageErrorHandler"]

__docformat__ = 'restructuredtext'


class TaurusMessageErrorHandler(object):
    """This class is designed to handle a generic error into a
    :class:`TaurusMessagePanel`"""

    def __init__(self, msgbox):
        self._msgbox = msgbox
        msgbox.setWindowTitle("Taurus Error")
        self.setError(*msgbox.getError())

    def setError(self, err_type=None, err_value=None, err_traceback=None):
        """Translates the given error object into an HTML string and places it
        in the message panel

        :param error: an error object (typically an exception object)
        :type error: object"""

        msgbox = self._msgbox
        error = "".join(traceback.format_exception_only(err_type, err_value))
        msgbox.setText(error)
        msg = "<html><body><pre>%s</pre></body></html>" % error
        msgbox.setDetailedHtml(msg)

        html_orig = '<html><head><style type="text/css">{style}</style>' \
                    '</head><body>'
        exc_info = "".join(traceback.format_exception(err_type, err_value,
                                                      err_traceback))
        style = ""
        if pygments is not None:
            formatter = HtmlFormatter()
            style = formatter.get_style_defs()
        html = html_orig.format(style=style)
        if pygments is None:
            html += "<pre>%s</pre>" % exc_info
        else:
            formatter = HtmlFormatter()
            html += highlight(exc_info, PythonTracebackLexer(), formatter)
        html += "</body></html>"
        msgbox.setOriginHtml(html)


class TangoMessageErrorHandler(TaurusMessageErrorHandler):
    """This class is designed to handle :class:`PyTango.DevFailed` error into
    a :class:`TaurusMessagePanel`"""
    # TODO: tango-centric

    def setError(self, err_type=None, err_value=None, err_traceback=None):
        """Translates the given error object into an HTML string and places it
        it the message panel

        :param error: an error object (typically an exception object)
        :type error: object"""

        msgbox = self._msgbox
        html_orig = '<html><head><style type="text/css">{style}</style>' \
                    '</head><body>'
        style, formatter = "", None
        if pygments is not None:
            formatter = HtmlFormatter()
            style = formatter.get_style_defs()
        html = html_orig.format(style=style)
        for de in err_value.args:
            e_html = """<pre>{reason}: {desc}</pre>{origin}<hr>"""
            origin, reason, desc = de.origin, de.reason, de.desc
            if reason.startswith("PyDs_") and pygments is not None:
                origin = highlight(origin, PythonTracebackLexer(), formatter)
            else:
                origin = "<pre>%s</pre>" % origin
            html += e_html.format(desc=desc, origin=origin, reason=reason)
        html += "</body></html>"
        msgbox.setText(err_value.args[0].desc)
        msgbox.setDetailedHtml(html)

        exc_info = "".join(traceback.format_exception(err_type, err_value,
                                                      err_traceback))
        html = html_orig.format(style=style)
        if pygments is None:
            html += "<pre>%s</pre>" % exc_info
        else:
            html += highlight(exc_info, PythonTracebackLexer(), formatter)
        html += "</body></html>"
        msgbox.setOriginHtml(html)


class MacroServerMessageErrorHandler(TaurusMessageErrorHandler):

    def setError(self, err_type=None, err_value=None, err_traceback=None):
        """Translates the given error object into an HTML string and places it
        in the message panel

        :param error: an error object (typically an exception object)
        :type error: object"""

        msgbox = self._msgbox
        msgbox.setText(err_value)
        msg = "<html><body><pre>%s</pre></body></html>" % err_value
        msgbox.setDetailedHtml(msg)

        html_orig = """<html><head><style type="text/css">{style}</style></head><body>"""
        exc_info = "".join(err_traceback)
        style = ""
        if pygments is not None:
            formatter = HtmlFormatter()
            style = formatter.get_style_defs()
        html = html_orig.format(style=style)
        if pygments is None:
            html += "<pre>%s</pre>" % exc_info
        else:
            formatter = HtmlFormatter()
            html += highlight(exc_info, PythonTracebackLexer(), formatter)
        html += "</body></html>"
        msgbox.setOriginHtml(html)


def is_report_handler(report, abs_file=None):
    """Helper function to determine if a certain python object is a valid
    report handler"""
    import inspect
    if not inspect.isclass(report):
        return False
    if not issubclass(report, TaurusMessageReportHandler):
        return False
    try:
        if inspect.getabsfile(report) != abs_file:
            return False
    except:
        return False
    return True

_REPORT_HANDLERS = None


def get_report_handlers():
    global _REPORT_HANDLERS
    if not _REPORT_HANDLERS is None:
        return _REPORT_HANDLERS

    import os.path
    import functools
    import inspect

    this = os.path.abspath(__file__)
    report_path = os.path.join(os.path.dirname(this), "report")
    sys.path.insert(0, report_path)

    _REPORT_HANDLERS = {}
    try:
        for elem in os.listdir(report_path):
            if not elem[0].isalpha():
                continue
            full_elem = os.path.join(report_path, elem)
            if not os.path.isfile(full_elem):
                continue
            if not elem.endswith('.py'):
                continue
            elem, _ = os.path.splitext(elem)
            _is_report_handler = functools.partial(
                is_report_handler, abs_file=full_elem)
            report_lib = __import__(elem, globals(), locals(), [], 0)
            for name, obj in inspect.getmembers(report_lib, _is_report_handler):
                _REPORT_HANDLERS[name] = obj
    finally:
        sys.path.pop(0)

    return _REPORT_HANDLERS

_REPORT = """\
-- Description -----------------------------------------------------------------
An error occured in '{appName} {appVersion}' on {time}
{text}

-- Details ---------------------------------------------------------------------
{detail}

-- Origin ----------------------------------------------------------------------
{origin}
--------------------------------------------------------------------------------
"""


@UILoadable(with_ui='_ui')
class TaurusMessagePanel(Qt.QWidget):
    """A panel intended to display a taurus error.
    Example::

        dev = taurus.Device("sys/tg_test/1")
        try:
            print dev.read_attribute("throw_exception")
        except PyTango.DevFailed, df:
            msgbox = TaurusMessagePanel()
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
            msgbox = TaurusMessagePanel(*exc_info)
            msgbox.show()"""

    toggledDetails = Qt.pyqtSignal(bool)

    def __init__(self, err_type=None, err_value=None, err_traceback=None, parent=None, designMode=False):
        Qt.QWidget.__init__(self, parent)
        self.loadUi()
        self._exc_info = err_type, err_value, err_traceback

        self._ui._detailsWidget.setVisible(False)
        self._ui._checkBox.setVisible(False)
        self._ui._checkBox.setCheckState(Qt.Qt.Unchecked)
        self._initReportCombo()

        self._ui._showDetailsButton.toggled.connect(self._onShowDetails)
        self._ui._reportComboBox.activated.connect(self._onReportTriggered)

        pixmap = Qt.QIcon.fromTheme("emblem-important").pixmap(48, 48)
        self.setIconPixmap(pixmap)

        if err_value is not None:
            self.setError(*self._exc_info)
        self.adjustSize()

    def _initReportCombo(self):
        report_handlers = get_report_handlers()
        combo = self.reportComboBox()
        for name, report_handler in report_handlers.items():
            combo.addItem(report_handler.Label, name)

    def _onReportTriggered(self, index):
        report_handlers = get_report_handlers()
        combo = self.reportComboBox()
        name = combo.itemData(index)
        report_handler = report_handlers[name]
        report = report_handler(self)
        app = Qt.QApplication.instance()
        txt = _REPORT.format(appName=app.applicationName(),
                             appVersion=app.applicationVersion(),
                             time=datetime.datetime.now().ctime(),
                             text=self.getText(),
                             detail=self.getDetailedText(),
                             origin=self.getOriginText())
        report.report(txt)

    def _onShowDetails(self, show):
        self._ui._detailsWidget.setVisible(show)
        if show:
            text = "Hide details..."
        else:
            text = "Show details..."
        self._ui._showDetailsButton.setText(text)
        self.adjustSize()
        self.toggledDetails.emit(show)

    def reportComboBox(self):
        return self._ui._reportComboBox

    def checkBox(self):
        """Returns the check box from this panel

        :return: the check box from this panel
        :rtype: PyQt4.Qt.QCheckBox"""
        return self._ui._checkBox

    def checkBoxState(self):
        """Returns the check box state

        :return: the check box state
        :rtype: PyQt4.Qt.CheckState"""
        return self.checkBox().checkState()

    def checkBoxText(self):
        """Returns the check box text

        :return: the check box text
        :rtype: str"""
        return str(self.checkBox().text())

    def setCheckBoxText(self, text):
        """Sets the checkbox text.

        :param text: new checkbox text
        :type text: str"""
        self.checkBox().setText(text)

    def setCheckBoxState(self, state):
        """Sets the checkbox state.

        :param text: new checkbox state
        :type text: PyQt4.Qt.CheckState"""
        self.checkBox().setCheckState(state)

    def setCheckBoxVisible(self, visible):
        """Sets the checkbox visibility.

        :param visible: True makes checkbox visible, False hides it
        :type visible: bool"""
        self.checkBox().setVisible(visible)

    def buttonBox(self):
        """Returns the button box from this panel

        :return: the button box from this panel
        :rtype: PyQt4.Qt.QDialogButtonBox"""
        return self._ui._buttonBox

    def addButton(self, button, role=Qt.QDialogButtonBox.ActionRole):
        """Adds the given button with the given to the button box

        :param button: the button to be added
        :type button: PyQt4.QtGui.QPushButton
        :param role: button role
        :type role: PyQt4.Qt.QDialogButtonBox.ButtonRole"""
        self._ui._buttonBox.addButton(button, role)

    def setIconPixmap(self, pixmap):
        """Sets the icon to the dialog

        :param pixmap: the icon pixmap
        :type pixmap: PyQt4.Qt.QPixmap"""
        self._ui._iconLabel.setPixmap(pixmap)

    def setText(self, text):
        """Sets the text of this panel

        :param text: the new text
        :type text: str"""
        self._ui._textLabel.setText(text)

    def getText(self):
        """Returns the current text of this panel

        :return: the text for this panel
        :rtype: str"""
        return self._ui._textLabel.text()

    def setDetailedText(self, text):
        """Sets the detailed text of the dialog

        :param text: the new text
        :type text: str"""
        self._ui._detailsTextEdit.setPlainText(text)

    def setDetailedHtml(self, html):
        """Sets the detailed HTML of the dialog

        :param html: the new HTML text
        :type html: str"""
        self._ui._detailsTextEdit.setHtml(html)

    def getDetailedText(self):
        """Returns the current detailed text of this panel

        :return: the detailed text for this panel
        :rtype: str"""
        return self._ui._detailsTextEdit.toPlainText()

    def getDetailedHtml(self):
        """Returns the current detailed HTML of this panel

        :return: the detailed HTML for this panel
        :rtype: str"""
        return self._ui._detailsTextEdit.toHtml()

    def setOriginText(self, text):
        """Sets the origin text of the dialog

        :param text: the new text
        :type text: str"""
        self._ui._originTextEdit.setPlainText(text)

    def setOriginHtml(self, html):
        """Sets the origin HTML of the dialog

        :param html: the new HTML text
        :type html: str"""
        self._ui._originTextEdit.setHtml(html)

    def getOriginText(self):
        """Returns the current origin text of this panel

        :return: the origin text for this panel
        :rtype: str"""
        return self._ui._originTextEdit.toPlainText()

    def getOriginHtml(self):
        """Returns the current origin HTML of this panel

        :return: the origin HTML for this panel
        :rtype: str"""
        return self._ui._originTextEdit.toHtml()

    def setError(self, err_type=None, err_value=None, err_traceback=None):
        """Sets the exception object.
        Example usage::

            dev = taurus.Device("sys/tg_test/1")
            exc_info = None
            msgbox = TaurusMessagePanel()
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
        i = sys.exc_info()
        self._exc_info = [err_type or i[0],
                          err_value or i[1], err_traceback or i[2]]

        handler_klass = self.findErrorHandler(self._exc_info[0])
        handler_klass(self)

    def getError(self):
        """Returns the current exception information of this panel

        :return: the current exception information (same as type as returned by
                 :func:`sys.exc_info`)
        :rtype: tuple<type, Exception, traceback>"""
        return self._exc_info

    try:
        import PyTango
        ErrorHandlers = {PyTango.DevFailed: TangoMessageErrorHandler}
    except:
        ErrorHandlers = {}

    @classmethod
    def registerErrorHandler(klass, err_type, err_handler):
        klass.ErrorHandlers[err_type] = err_handler

    @classmethod
    def findErrorHandler(klass, err_type):
        """Finds the proper error handler class for the given error

        :param err_type: error class
        :type err_type: class object
        :return: a message box error handler
        :rtype: TaurusMessageBoxErrorHandler class object"""

        for exc, h_klass in klass.ErrorHandlers.items():
            if issubclass(err_type, exc):
                return h_klass
        return TaurusMessageErrorHandler


class DemoException(Exception):
    """Just a plain python exception for demo purposes"""
    pass


def s1():
    """Just a function to make the stack more interesting"""
    return s2()


def s2():
    """Just a function to make the stack more interesting"""
    return s3()


def s3():
    """Just a function to make the stack more interesting"""
    raise DemoException("A demo exception occurred")


class QMessageDialog(Qt.QDialog):
    """Helper class for the demo"""

    def __init__(self, msgbox, parent=None):
        Qt.QDialog.__init__(self, parent)
        l = Qt.QVBoxLayout()
        l.setContentsMargins(0, 0, 0, 0)
        l.addWidget(msgbox)
        l.addStretch(1)
        self.setLayout(l)


def py_exc():
    """Shows a python exception in a TaurusMessagePanel"""
    try:
        s1()
    except:
        msgbox = TaurusMessagePanel(*sys.exc_info())
        QMessageDialog(msgbox).exec_()


def tg_exc():
    """Shows a tango exception in a TaurusMessagePanel"""
    # TODO: This function is Tango centric
    import PyTango
    try:
        PyTango.Except.throw_exception(
            'TangoException', 'A simple tango exception', 'right here')
    except PyTango.DevFailed:
        msgbox = TaurusMessagePanel(*sys.exc_info())
        QMessageDialog(msgbox).exec_()


def tg_serv_exc():
    """Shows a tango exception from a server in a TaurusMessagePanel"""
    # TODO: This function is Tango centric
    import PyTango
    import taurus
    dev = taurus.Device("sys/tg_test/1")
    try:
        dev.read_attribute("throw_exception")
    except PyTango.DevFailed:
        msgbox = TaurusMessagePanel(*sys.exc_info())
        QMessageDialog(msgbox).exec_()
    except:
        msgbox = TaurusMessagePanel(*sys.exc_info())
        QMessageDialog(msgbox).exec_()


def py_tg_serv_exc():
    """Shows a tango exception from a python server in a TaurusMessagePanel"""
    # TODO: This function is Tango centric
    import PyTango
    try:
        PyTango.Except.throw_exception(
            'TangoException', 'A simple tango exception', 'right here')
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
            PyTango.Except.re_throw_exception(
                df1, 'PyDs_Exception', 'DevFailed: A simple tango exception', origin)
        except PyTango.DevFailed:
            msgbox = TaurusMessagePanel(*sys.exc_info())
            QMessageDialog(msgbox).exec_()


def demo():
    """Message panel"""
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
    w.show()
    if owns_app:
        sys.exit(app.exec_())
    else:
        return w

if __name__ == "__main__":
    main()
