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

"""This module exposes QtWebKit module"""

from . import PYQT5, PYQT4, PYSIDE, PYSIDE2, PythonQtError


if PYQT5:
    from PyQt5.QtWebKit import *
    # import * from QtWebkitWidgets for PyQt4 style compat
    from PyQt5.QtWebKitWidgets import *
elif PYSIDE2:
    from PySide2.QtWebKit import *
    # import * from QtWebkitWidgets for PyQt4 style compat
    from PySide2.QtWebKitWidgets import *
elif PYQT4:
    from PyQt4.QtWebKit import *
elif PYSIDE:
    from PySide.QtWebKit import *
else:
    raise PythonQtError('No Qt bindings could be found')
