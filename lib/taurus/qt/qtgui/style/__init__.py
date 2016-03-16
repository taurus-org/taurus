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

"""This module provides Qt styles"""

__all__ = ["setTaurusStyle"]

__docformat__ = 'restructuredtext'

import imp

from taurus.external.qt import Qt


def setTaurusStyle(newStyle):

    app = Qt.QApplication.instance()

    if app is None:
        raise RuntimeError(
            "Must initialize a QApplication before setting style")

    mod = imp.load_module(newStyle, *imp.find_module(newStyle, __path__))

    style = mod.getStyle()
    styleSheet = mod.getStyleSheet()

    if style is not None:
        app.setStyle(style)
    if styleSheet is not None:
        app.setStyleSheet(styleSheet)
