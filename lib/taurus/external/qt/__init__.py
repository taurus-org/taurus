# -*- coding: utf-8 -*-

##############################################################################
##
## This file is part of Taurus
##
## http://taurus-scada.org
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
##############################################################################

"""This module exposes PyQt4/PyQt5/PySide module"""

__all__ = ["initialize", "API_NAME",
           "getQtName", "getQt", "requires"]

import os
import sys
import platform
from distutils.version import LooseVersion
from taurus.core.util import log as __log
from taurus import tauruscustomsettings as __config


class PythonQtError(RuntimeError):
    """Error raised if no bindings could be selected."""
    pass


#: Qt API environment variable name
QT_API = 'QT_API'
#: names of the PyQt5 api
PYQT5_API = ['pyqt5']
#: names of the PyQt4 api
PYQT4_API = [
    'pyqt',  # name used in IPython.qt
    'pyqt4'  # pyqode.qt original name
]
#: names of the PySide api
PYSIDE_API = ['pyside']

#: names of the PySide2 api
PYSIDE2_API = ['pyside2']

#: The constants PYQT5, PYQT4, PYSIDE, PYSIDE2, PYSIDE_VERSION and PYQT_VERSION
#: will be updated depending on the selected binding
PYQT5 = PYQT4 = PYSIDE = PYSIDE2 = False
PYSIDE_VERSION = PYQT_VERSION = None

# First, check if some binding is already in use (and, if so, select it)
if 'PyQt5' in sys.modules:
    API = 'pyqt5'
elif 'PySide2' in sys.modules:
    API = 'pyside2'
elif 'PyQt4' in sys.modules:
    API = 'pyqt4'
elif 'PySide' in sys.modules:
    API = 'pyside'
else:
    # if no binding is already loaded, use (in this order):
    #   - QT_API environment variable
    #   - tauruscustomsettings.DEFAULT_QT_API
    #   - first successful import of 'pyqt5', 'pyqt4', 'pyside2', 'pyside'
    API = os.environ.get(QT_API, getattr(__config, 'DEFAULT_QT_API', ''))
    API = API.lower()


if API not in (PYQT5_API + PYQT4_API + PYSIDE_API + PYSIDE2_API + ['']):
    raise ImportError("Unknown Qt API '{}'".format(API))


if not API or API in PYQT5_API:
    try:
        from PyQt5.QtCore import PYQT_VERSION_STR as PYQT_VERSION
        from PyQt5.QtCore import QT_VERSION_STR as QT_VERSION

        PYSIDE_VERSION = None
        PYQT4 = PYSIDE = PYSIDE2 = False
        PYQT5 = True
        API = os.environ['QT_API'] = 'pyqt5'

        if sys.platform == 'darwin':
            macos_version = LooseVersion(platform.mac_ver()[0])
            if macos_version < LooseVersion('10.10'):
                if LooseVersion(QT_VERSION) >= LooseVersion('5.9'):
                    raise PythonQtError("Qt 5.9 or higher only works in "
                                       + "macOS 10.10 or higher. Your "
                                       + "program will fail in this "
                                       + "system.")
            elif macos_version < LooseVersion('10.11'):
                if LooseVersion(QT_VERSION) >= LooseVersion('5.11'):
                    raise PythonQtError("Qt 5.11 or higher only works in "
                                       + "macOS 10.11 or higher. Your "
                                       + "program will fail in this "
                                       + "system.")

            del macos_version
    except ImportError:
        if API:  # if an specific API was requested, fail with import error
            raise ImportError('Cannot import PyQt5')
        # if no specific API was requested, allow trying other bindings
        __log.debug('Cannot import PyQt5')

if not API or API in PYQT4_API:
    try:
        import sip

        sip.setapi('QString', 2)
        sip.setapi('QVariant', 2)
        sip.setapi('QDate', 2)
        sip.setapi('QDateTime', 2)
        sip.setapi('QTextStream', 2)
        sip.setapi('QTime', 2)
        sip.setapi('QUrl', 2)
        from PyQt4.QtCore import PYQT_VERSION_STR as PYQT_VERSION  # analysis:ignore
        from PyQt4.QtCore import QT_VERSION_STR as QT_VERSION  # analysis:ignore

        PYSIDE_VERSION = None
        PYQT5 = PYSIDE = PYSIDE2 = False
        PYQT4 = True
        API = os.environ['QT_API'] = 'pyqt'  # "pyqt4" is forced to "pyqt"
    except ImportError:
        if API:  # if an specific API was requested, fail with import error
            raise ImportError('Cannot import PyQt4')
        # if no specific API was requested, allow trying other bindings
        __log.debug('Cannot import PyQt4')

if not API or API in PYSIDE2_API:
    try:
        from PySide2 import __version__ as PYSIDE_VERSION  # analysis:ignore
        from PySide2.QtCore import __version__ as QT_VERSION  # analysis:ignore

        PYQT_VERSION = None
        PYQT5 = PYQT4 = PYSIDE = False
        PYSIDE2 = True
        API = os.environ['QT_API'] = 'pyside2'

        if sys.platform == 'darwin':
            macos_version = LooseVersion(platform.mac_ver()[0])
            if macos_version < LooseVersion('10.11'):
                if LooseVersion(QT_VERSION) >= LooseVersion('5.11'):
                    raise PythonQtError("Qt 5.11 or higher only works in "
                                       + "macOS 10.11 or higher. Your "
                                       + "program will fail in this "
                                       + "system.")

            del macos_version
    except ImportError:
        if API:  # if an specific API was requested, fail with import error
            raise ImportError('Cannot import PySide2')
        # if no specific API was requested, allow trying other bindings
        __log.debug('Cannot import PySide2')

if not API or API in PYSIDE_API:
    try:
        from PySide import __version__ as PYSIDE_VERSION  # analysis:ignore
        from PySide.QtCore import __version__ as QT_VERSION  # analysis:ignore

        PYQT_VERSION = None
        PYQT5 = PYQT4 = PYSIDE = False
        PYSIDE = True
        API = os.environ['QT_API'] = 'pyside'

    except ImportError:
        if API:  # if an specific API was requested, fail with import error
            raise ImportError('Cannot import PySide')
        # if no specific API was requested, allow trying other bindings
        __log.debug('Cannot import PySide')

if not API:
    raise ImportError('No Qt bindings could be imported')

API_NAME = {'pyqt5': 'PyQt5', 'pyqt': 'PyQt4', 'pyqt4': 'PyQt4',
            'pyside': 'PySide', 'pyside2': 'PySide2'}[API]

# Update the environment so that other libraries that also use the same
# convention (such as guidata or spyder) do a consistent choice
os.environ['QT_API'] = API


def __initializeQtLogging():
    from importlib import import_module
    QtCore = import_module(API_NAME + '.QtCore')

    QT_LEVEL_MATCHER = {
        QtCore.QtDebugMsg: __log.debug,
        QtCore.QtWarningMsg: __log.warning,
        QtCore.QtCriticalMsg: __log.critical,
        QtCore.QtFatalMsg: __log.fatal,
        QtCore.QtSystemMsg: __log.critical,
    }

    if hasattr(QtCore, "qInstallMessageHandler"):
        # Qt5
        def taurusMessageHandler(msg_type, log_ctx, msg):
            f = QT_LEVEL_MATCHER.get(msg_type)
            return f("Qt%s %s.%s[%s]: %s", log_ctx.category, log_ctx.file,
                     log_ctx.function, log_ctx.line, msg)

        QtCore.qInstallMessageHandler(taurusMessageHandler)
    elif hasattr(QtCore, "qInstallMsgHandler"):
        # Qt4
        def taurusMsgHandler(msg_type, msg):
            f = QT_LEVEL_MATCHER.get(msg_type)
            return f("Qt: " + msg)

        QtCore.qInstallMsgHandler(taurusMsgHandler)


def __removePyQtInputHook():
    from importlib import import_module
    QtCore = import_module(API_NAME + '.QtCore')
    if hasattr(QtCore, "pyqtRemoveInputHook"):
        QtCore.pyqtRemoveInputHook()


def __addExceptHook():
    """
    Since PyQt 5.5 , unhandled python exceptions cause the application to
    abort:

    http://pyqt.sf.net/Docs/PyQt5/incompatibilities.html#unhandled-python-exceptions

    By calling __addExceptHook, we restore the old behaviour (just print the
    exception trace).
    """
    import traceback
    sys.excepthook = traceback.print_exception


if getattr(__config, 'QT_AUTO_INIT_LOG', True):
    __initializeQtLogging()

if getattr(__config, 'QT_AUTO_REMOVE_INPUTHOOK', True):
    __removePyQtInputHook()

if PYQT5 and getattr(__config, 'QT_AVOID_ABORT_ON_EXCEPTION', True):
    # TODO: check if we also want to do this for PySide(2)
    __addExceptHook()

__log.info('Using %s (v%s with Qt %s and Python %s)',
           API_NAME,
           PYQT_VERSION or PYSIDE_VERSION,
           QT_VERSION,
           sys.version.split()[0])


# --------------------------------------------------------------------------
# Deprecated (in Jul17) pending to be removed later on


def getQt(name=None, strict=True):
    __log.deprecated(dep='taurus.external.qt.getQt', rel='4.0.4')
    from importlib import import_module
    return import_module(API_NAME)


def getQtName(name=None, strict=True):
    __log.deprecated(dep='taurus.external.qt.getQtName',
                     alt='taurus.external.qt.API_NAME', rel='4.0.4')
    return API_NAME


def initialize(name=None, strict=True, logging=True,
               resources=True, remove_inputhook=True):
    __log.deprecated(dep='taurus.external.qt.initialize', rel='4.0.4')
    return getQt()


def requires(origin=None, exc_class=ImportError, **kwargs):
    __log.deprecated(dep='taurus.external.qt.requires', rel='4.0.4')
    return True


# Handle rename of DEFAULT_QT_AUTO_API -->  DEFAULT_QT_API
if hasattr(__config, 'DEFAULT_QT_AUTO_API'):
    __log.deprecated(dep='DEFAULT_QT_AUTO_API', alt='DEFAULT_QT_API',
                     rel='4.0.4')
    if not hasattr(__config, 'DEFAULT_QT_API'):
        __config.DEFAULT_QT_API = __config.DEFAULT_QT_AUTO_API

# --------------------------------------------------------------------------
