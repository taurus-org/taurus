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

"""
This module provides utilities to smooth differences between different
Qt APIs
"""

# provide substitutes for QFileDialog's getSaveFileName, getOpenFileName
# and getOpenFileNames that return the selected filter regardless of Qt API
from taurus.external.qt.Qt import QFileDialog

getSaveFileName = getattr(QFileDialog, 'getSaveFileNameAndFilter',
                          QFileDialog.getSaveFileName)

getOpenFileName = getattr(QFileDialog, 'getOpenFileNameAndFilter',
                          QFileDialog.getOpenFileName)

getOpenFileNames = getattr(QFileDialog, 'getOpenFileNamesAndFilter',
                          QFileDialog.getOpenFileNames)

# Provide a common constant for the PyObject name (to be used in signal
# signatures)
from taurus.external.qt import PYQT5, PYQT4
if PYQT5 or PYQT4:
    PY_OBJECT = 'PyQt_PyObject'
else:
    PY_OBJECT = 'PyObject'

del QFileDialog, PYQT5, PYQT4