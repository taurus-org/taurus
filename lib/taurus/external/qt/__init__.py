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

__all__ = ["initialize", "getQtName", "getQt", "_updateQtSubModule", "requires"]


from taurus import tauruscustomsettings as __config
from taurus.core.util import log as __log

import os

__QT = None
__QT_NAME = None
__QT_KNOWN_APIS = "PyQt4", "PyQt5", "PySide"
__QT_PREFERED_APIS = None

__QT_INIT = False
__QT_LOG_INIT = False
__QT_RES_INIT = False


def __getPreferedAPIs():
    return [__config.QT_AUTO_API] + \
      [api for api in __QT_KNOWN_APIS if api != __config.QT_AUTO_API]


def __assertQt(name, qt=None, strict=True):
    qt = qt or __QT
    if name is None or qt is None:
        return
    qt_name = qt.__name__
    if qt_name != name:
        msg = "Cannot use %s because %s already in use" % (name, qt_name)
        if strict:
            raise Exception(msg)
        else:
            __log.error(msg)


def __hasBinding(qt_name):
    """Safely check for known qt apis without importing submodules"""
    import imp
    try:
        _, pth, _ = imp.find_module(qt_name)
        imp.find_module('QtCore', pth)
        imp.find_module('QtGui', pth)
    except ImportError:
        return False
    return True


def __import(name):
    import sys
    __import__(name)
    return sys.modules[name]


def __importQt(name):
    return __import(getQtName() + "." + name)


def __initializeQtLogging():
    QtCore = __importQt("QtCore")

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


def __getTheme():
    QtGui = __importQt("QtGui")
    return QtGui.QIcon.themeName()


def __hasTheme():
    return len(__getTheme()) > 0


def __get_taurus_resource_path():
    import os
    this_dir = os.path.abspath(os.path.dirname(__file__))
    taurus_dir = os.path.join(this_dir, os.path.pardir, os.path.pardir)
    base_resource_dir = os.path.join(taurus_dir, "qt", "qtgui", "resource")
    return os.path.realpath(base_resource_dir)


def __get_taurus_tango_theme_path():
    import os
    return os.path.join(__get_taurus_resource_path(), "tango-icons")


def __themeDirectories():
    """Returns valid theme directories for the current theme
    **Requires QApplication to be created**"""
    import os
    QtGui = __importQt("QtGui")
    theme = __getTheme()
    theme_paths = QtGui.QIcon.themeSearchPaths()
    result = []
    for theme_path in theme_paths:
        theme_path = os.path.join(theme_path, theme)
        if os.path.isdir(theme_path) and not theme_path in result:
            result.append(theme_path)
    return result


def __initializeTheme():
    """Currently not used"""
    import os
    QtGui = __importQt("QtGui")

    # Can only resources if QApplication already exists
    app = QtGui.QApplication.instance()
    if app is None:
        raise SystemError("QApplication object must exist before "
                          "initializing Qt resources")

    tango_theme_dir = __get_taurus_tango_theme_path()

    # initialize theme if necessary
    theme = __getTheme()
    has_theme = len(theme) > 0
    if not has_theme:
        __log.info("No native theme support. Using local tango-theme-icons")
        if os.path.isdir(tango_theme_dir):
            # If themes are not supported (windows, for example), taurus
            # initializes local Tango theme
            theme_search_path = QtGui.QIcon.themeSearchPaths()
            theme_search_path.append(tango_theme_dir)
            QtGui.QIcon.setThemeSearchPaths(theme_search_path)
            QtGui.QIcon.setThemeName("Tango")
        else:
            __log.warning("Local tango-theme-icons not found: Theme not initialized")


def __initializeQtResources():
    import os
    QtCore = __importQt("QtCore")
    base_resource_dir = __get_taurus_resource_path()

    # add taurus resources
    namespace = __config.NAMESPACE
    search_paths = QtCore.QDir.searchPaths(namespace) or []
    for elem in os.listdir(base_resource_dir):
        abs_elem = os.path.join(base_resource_dir, elem)
        if os.path.isdir(abs_elem) and not abs_elem in search_paths:
            search_paths.append(abs_elem)
    QtCore.QDir.setSearchPaths(namespace, search_paths)


def __removePyQtInputHook():
    try:
        __importQt("QtCore").pyqtRemoveInputHook()
    except AttributeError:
        pass


def _updateQtSubModule(glob_dict, qt_sub_module_name):
    glob_dict.update(__importQt(qt_sub_module_name).__dict__)


#------------------------------------------------------------------------------
# PyQt4
#------------------------------------------------------------------------------

def __get_sip():
    try:
        import sip
    except ImportError:
        sip = None
    return sip


def __setPyQt4API(element, api_version=2):
    sip = __get_sip()
    try:
        ver = sip.getapi(element)
    except ValueError:
        ver = -1

    if ver < 0:
        try:
            sip.setapi(element, api_version)
            __log.debug("%s API set to version %d",
                      element, sip.getapi(element))
        except ValueError:
            __log.warning("Error setting %s API to version %s", element,
                        api_version, exc_info=1)
            return False
    elif ver < api_version:
        __log.info("%s API set to version %s (advised: version >= %s)",
                 element, ver, api_version)
    return True


def __preparePyQt4():
    import sys

    # In python 3 APIs are set to level 2 so nothing to do
    if sys.version_info[0] > 2:
        return __import("PyQt4")

    sip = __get_sip()

    # For PySide compatibility, use the new-style string API that
    # automatically converts QStrings to Unicode Python strings. Also,
    # automatically unpack QVariants to their underlying objects.
    if sip is None:
        __log.warning("Could not find sip")
    elif sip.SIP_VERSION < 0x040900:
        sip_ver = sip.SIP_VERSION_STR
        __log.warning("Using old sip %s (advised >= 4.9)", sip_ver)
    else:
        for obj in ("QDate", "QDateTime", "QString", "QTextStream", "QTime",
          "QUrl", "QVariant"):
            __setPyQt4API(obj, 2)

    return __import("PyQt4")


#------------------------------------------------------------------------------
# PyQt5
#------------------------------------------------------------------------------

def __preparePyQt5():
    return __import("PyQt5")


#------------------------------------------------------------------------------
# PySide
#------------------------------------------------------------------------------

def __preparePySide():
    return __import("PySide")


#------------------------------------------------------------------------------
# Global
#------------------------------------------------------------------------------

def getQt(name=None, strict=True):
    global __QT, __QT_NAME
    if __QT:
        __assertQt(name, qt=__QT, strict=strict)
        return __QT

    import sys

    modules = sys.modules
    for api_name in __QT_PREFERED_APIS:
        api = modules.get(api_name)
        if api:
            __assertQt(name, qt=api, strict=strict)
            __QT = api
            __QT_NAME = name
            return __QT

    # no qt imported yet
    if strict and name:
        apis = [name]
    else:
        apis = list(__QT_PREFERED_APIS)
        if name:
            apis.remove(name)
            apis.insert(0, name)
    for api_name in apis:
        f = globals()["__prepare" + api_name]
        try:
            __QT = f()
            __QT_NAME = api_name
            return __QT
        except ImportError:
            continue
    raise ImportError("No suitable Qt found")


def getQtName(name=None, strict=True):
    # force initialization of Qt
    getQt(name=name, strict=strict)
    return __QT_NAME


def initialize(name=None, strict=True, logging=True,
               resources=True, remove_inputhook=True):
    global __QT_INIT

    if __QT_INIT:
        return getQt()

    if not __config.QT_AUTO_API in __QT_KNOWN_APIS:
        raise ImportError("Invalid QT_AUTO_API '%s'. Valid APIs are %s" % \
                          (__config.QT_AUTO_API,
                          ", ".join(__QT_KNOWN_APIS)))

    global __QT_PREFERED_APIS
    __QT_PREFERED_APIS = __getPreferedAPIs()

    qt = getQt(name=name, strict=strict)
    if logging:
        __initializeQtLogging()
    if resources:
        __initializeQtResources()
    if remove_inputhook:
        __removePyQtInputHook()

    __QT_INIT = True

    QT_API = os.environ.get('QT_API')
    if QT_API is None:
        global __QT_NAME
        if __QT_NAME == 'PySide':
            QT_API = 'pyside'
        else:
            QT_API = 'pyqt'

    os.environ['QT_API'] = QT_API

    return qt


def requires(origin=None, exc_class=ImportError, **kwargs):
    """
    Determines if the Qt component fulfills the minimum specified.
    Can take one of the following keyword arguments: Qt, PyQt, PySide.
    Any of these arguments maybe a string in the loose version format
    (see :class:`distutils.version.LooseVersion`)

    If present, *Qt* keyword stands for the minimum Qt C++ version.
    If present, *PyQt* keyword stands for the minimum PyQt version.
    If present, *PySide* keyword stands for the minimum PySide version.

    If a keyword is not present, it means it accepts any version. So, if, for
    example, you are running taurus with PySide and you call requires with
    `requires(PyQt='4.10')` it will **not** fail.

    :param Qt:
    """
    from distutils.version import LooseVersion as V
    QtName = getQtName()
    QtCore = __importQt("QtCore")

    if origin is None:
        msg_prefix = "Required"
    else:
        msg_prefix = origin + " requires"

    # check C++ Qt minimum version
    req_cpp_qt_v_str = kwargs.pop("Qt", None)
    if req_cpp_qt_v_str is not None:
        cpp_qt_v_str = QtCore.QT_VERSION_STR
        if V(req_cpp_qt_v_str) > V(cpp_qt_v_str):
            if exc_class:
                msg = "{0} C++ Qt >= {1}. Installed C++ Qt is {2}".format(
                    msg_prefix, req_cpp_qt_v_str, cpp_qt_v_str)
                raise exc_class(msg)
            else:
                return False

    if QtName.startswith('PyQt'):
        req_v_str = kwargs.get('PyQt', "0")
        qt_v_str = QtCore.PYQT_VERSION_STR
    elif QtName == 'PySide':
        req_v_str = kwargs.get('PySide', "0")
        qt_v_str = QtCore.PYSIDE_VERSION_STR

    if req_v_str:
        if V(req_v_str) > V(qt_v_str):
            if exc_class:
                msg = "{0} {1} >= {2}. Installed {1} is {3}",format(
                    msg_prefix, QtName, req_v_str, qt_v_str)
                raise exc_class(msg)
            else:
                return False
    return True


if __config.QT_AUTO_INIT:
    initialize(name=__config.QT_AUTO_API,
               strict=__config.QT_AUTO_STRICT,
               logging=__config.QT_AUTO_INIT_LOG,
               resources=__config.QT_AUTO_INIT_RES,
               remove_inputhook=__config.QT_AUTO_REMOVE_INPUTHOOK)

    __log.info('Using "%s" for Qt', __QT_NAME)
