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

"""This module exposes QtGui module"""

from taurus.external.qt import API_NAME, _updateQtSubModule

__backend = API_NAME

_updateQtSubModule(globals(), "QtGui")

if __backend == 'PyQt5':
    _updateQtSubModule(globals(), "QtWidgets")
else:
    # early import of qtpy.QtWidgets as a workaround for
    # https://github.com/taurus-org/taurus/issues/401
    import qtpy.QtWidgets as __qtpy_QtWidgets

del _updateQtSubModule, API_NAME
