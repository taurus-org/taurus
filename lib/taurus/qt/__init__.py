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

"""The taurus.qt submodule. It contains qt-specific part of taurus"""

__docformat__ = 'restructuredtext'

""" A Qt API selector that can be used to switch between PyQt and PySide.

This uses the ETS 4.0 selection pattern of:
PySide first, PyQt with API v2. second.

Do not use this if you need PyQt with the old QString/QVariant API.
"""

import os

# Available APIs.
QT_API_PYQT = 'pyqt'
QT_API_PYSIDE = 'pyside'
QT_USE_API2 = False

def __get_logger():
    import taurus.core.util
    return taurus.core.util.Logger(__name__)

def __prepare_pyqt4():
    if not QT_USE_API2:
        return
    # For PySide compatibility, use the new-style string API that automatically
    # converts QStrings to Unicode Python strings. Also, automatically unpack
    # QVariants to their underlying objects.
    import sip
    if sip.SIP_VERSION >= 0x040900:
        try:
            sip.setapi("QString", 2)
        except ValueError, e:
            __get_logger().info("SIP: %s", e)
        try:
            sip.setapi('QVariant', 2)
        except ValueError, e:
            __get_logger().info("SIP: %s", e)
    else:
        __get_logger().info("Using old SIP %s (advised >= 4.9)", sip.SIP_VERSION_STR)
        

# Select Qt binding, using the QT_API environment variable if available.
QT_API = os.environ.get('QT_API')
if QT_API is None:
    try:
        import PySide
        QT_API = QT_API_PYSIDE
    except ImportError:
        try:
            __prepare_pyqt4()
            import PyQt4
            QT_API = QT_API_PYQT
        except ImportError:
            raise ImportError('Cannot import PySide or PyQt4')
        
elif QT_API == QT_API_PYQT:
    # Note: This must be called *before* PyQt4 is imported.
    __prepare_pyqt4()

# Now peform the imports.
if QT_API == QT_API_PYQT:
    from PyQt4 import QtCore, QtGui, QtSvg, Qt

    # Alias PyQt-specific functions for PySide compatibility.
    if hasattr(QtCore, "pyqtSignal"):
        QtCore.Signal = QtCore.pyqtSignal
    if hasattr(QtCore, "pyqtSlot"):
        QtCore.Slot = QtCore.pyqtSlot

elif QT_API == QT_API_PYSIDE:
    from PySide import QtCore, QtGui, QtSvg, Qt

else:
    raise RuntimeError('Invalid Qt API %r, valid values are: %r or %r' % 
                       (QT_API, QT_API_PYQT, QT_API_PYSIDE))

