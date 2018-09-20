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
           "getQtName", "getQt", "_updateQtSubModule", "requires"]

import os
from taurus.core.util import log as __log
from taurus import tauruscustomsettings as __config

# --------------------------------------------------------------------------
# Deprecated (in Jul17) pending to be removed later on

def getQtName(name=None, strict=True):
    __log.deprecated (dep='taurus.external.qt.getQtName',
                      alt='taurus.external.qt.API_NAME', rel='4.0.4')
    return API_NAME


def initialize(name=None, strict=True, logging=True,
               resources=True, remove_inputhook=True):
    __log.deprecated (dep='taurus.external.qt.initialize', rel='4.0.4')
    return getQt()


def requires(origin=None, exc_class=ImportError, **kwargs):
    __log.deprecated (dep='taurus.external.qt.requires', rel='4.0.4')
    return True


# Handle rename of DEFAULT_QT_AUTO_API -->  DEFAULT_QT_API
if hasattr(__config, 'DEFAULT_QT_AUTO_API'):
    __log.deprecated(dep='DEFAULT_QT_AUTO_API', alt='DEFAULT_QT_API',
                     rel='4.0.4')
    if not hasattr(__config, 'DEFAULT_QT_API'):
        __config.DEFAULT_QT_API = __config.DEFAULT_QT_AUTO_API

# --------------------------------------------------------------------------

#: Qt API environment variable name
QT_API = 'QT_API'
#: names of the expected PyQt5 api
PYQT5_API = ['pyqt5']
#: names of the expected PyQt4 api
PYQT4_API = [
    'pyqt',  # name used in IPython.qt
    'pyqt4'  # pyqode.qt original name
]
#: names of the expected PySide api
PYSIDE_API = ['pyside']

os.environ.setdefault(QT_API, getattr(__config, 'DEFAULT_QT_API', 'pyqt'))
API = os.environ[QT_API].lower()
assert API in (PYQT5_API + PYQT4_API + PYSIDE_API)

is_old_pyqt = is_pyqt46 = False
PYQT5 = True
PYQT4 = PYSIDE = False


class PythonQtError(Exception):
    """Error raise if no bindings could be selected"""
    pass


if API in PYQT5_API:
    try:
        from PyQt5.Qt import PYQT_VERSION_STR as PYQT_VERSION  # analysis:ignore
        from PyQt5.Qt import QT_VERSION_STR as QT_VERSION  # analysis:ignore
        PYSIDE_VERSION = None
    except ImportError:
        API = os.environ['QT_API'] = 'pyqt'

if API in PYQT4_API:
    try:
        import sip
        try:
            sip.setapi('QString', 2)
            sip.setapi('QVariant', 2)
            sip.setapi('QDate', 2)
            sip.setapi('QDateTime', 2)
            sip.setapi('QTextStream', 2)
            sip.setapi('QTime', 2)
            sip.setapi('QUrl', 2)
        except AttributeError:
            # PyQt < v4.6
            pass
        from PyQt4.Qt import PYQT_VERSION_STR as PYQT_VERSION  # analysis:ignore
        from PyQt4.Qt import QT_VERSION_STR as QT_VERSION  # analysis:ignore
        PYSIDE_VERSION = None
        PYQT5 = False
        PYQT4 = True
        API = os.environ['QT_API'] = 'pyqt'  # in case the original was "pyqt4"
    except ImportError:
        API = os.environ['QT_API'] = 'pyside'
    else:
        is_old_pyqt = PYQT_VERSION.startswith(('4.4', '4.5', '4.6', '4.7'))
        is_pyqt46 = PYQT_VERSION.startswith('4.6')

if API in PYSIDE_API:
    try:
        from PySide import __version__ as PYSIDE_VERSION  # analysis:ignore
        from PySide.QtCore import __version__ as QT_VERSION  # analysis:ignore
        PYQT_VERSION = None
        PYQT5 = False
        PYSIDE = True
    except ImportError:
        raise PythonQtError('No Qt bindings could be found')

API_NAME = {'pyqt5': 'PyQt5', 'pyqt': 'PyQt4', 'pyqt4': 'PyQt4',
            'pyside': 'PySide'}[API]


def __initializeQtLogging():
    # from . import QtCore
    QtCore = __importQt ('QtCore')

    QT_LEVEL_MATCHER = {
        QtCore.QtDebugMsg:     __log.debug,
        QtCore.QtWarningMsg:   __log.warning,
        QtCore.QtCriticalMsg:  __log.critical,
        QtCore.QtFatalMsg:     __log.fatal,
        QtCore.QtSystemMsg:    __log.critical,
    }

    if hasattr(QtCore, "qInstallMessageHandler"):
        def taurusMessageHandler(msg_type, log_ctx, msg):
            f = QT_LEVEL_MATCHER.get(msg_type)
            return f("Qt%s %s.%s[%s]: %a", log_ctx.category, log_ctx.file,
                     log_ctx.function, log_ctx.line, msg)
        QtCore.qInstallMessageHandler(taurusMessageHandler)
    elif hasattr(QtCore, "qInstallMsgHandler"):
        def taurusMsgHandler(msg_type, msg):
            f = QT_LEVEL_MATCHER.get(msg_type)
            return f("Qt: " + msg)
        QtCore.qInstallMsgHandler(taurusMsgHandler)



def __removePyQtInputHook():
    try:
        from . import QtCore
        QtCore.pyqtRemoveInputHook()
    except AttributeError:
        pass


def _updateQtSubModule(glob_dict, qt_sub_module_name):
    glob_dict.update(__importQt(qt_sub_module_name).__dict__)

def __import(name):
    import sys
    __import__(name)
    return sys.modules[name]


def __importQt(name):
    return __import(API_NAME + "." + name)


def getQt(name=None, strict=True):
    __log.deprecated (dep='taurus.external.qt.getQt', rel='4.0.4')
    if PYQT5:
        import PyQt5 as _qt
    elif PYQT4:
        import PyQt4 as _qt
    elif PYSIDE:
        import PySide as _qt
    else:
        raise ImportError("No suitable Qt found")
    return _qt


if getattr(__config, 'QT_AUTO_INIT_LOG', True):
    __initializeQtLogging()

if getattr(__config, 'QT_AUTO_REMOVE_INPUTHOOK', True):
    __removePyQtInputHook()


__log.info('Using "%s" for Qt', API_NAME)
