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

"""This module exposes the QtUiTools module (deprecated in taurus).
It only makes sense when using PySide(2) (which were not supported before
taurus 4.5)
"""


from . import PYSIDE, PYSIDE2, API_NAME
from taurus.core.util import log as __log

__log.deprecated(dep="taurus.external.qt.QtUiTools", rel="4.5",
                 alt='PySide(2).QtUiTools or PyQt(4,5).loadUi')

if PYSIDE2:
    from PySide2.QtUiTools import *
elif PYSIDE:
    from PySide.QtUiTools import *
else:
    raise ImportError('QtUiTools not supported for {}'.format(API_NAME))