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

"""This module provides a base widget that can be used to display a taurus
model in a tree widget"""

from __future__ import absolute_import

from taurus.qt.qtgui.model import TaurusBaseModelWidget
from .qtree import QBaseTreeWidget


__all__ = ["TaurusBaseTreeWidget"]

__docformat__ = 'restructuredtext'


class TaurusBaseTreeWidget(QBaseTreeWidget, TaurusBaseModelWidget):

    def __init__(self, parent=None, designMode=False, with_navigation_bar=True,
                 with_filter_widget=True, perspective=None, proxy=None):
        self.call__init__(QBaseTreeWidget, parent, designMode=designMode,
                          with_navigation_bar=with_navigation_bar,
                          with_filter_widget=with_filter_widget,
                          perspective=perspective, proxy=proxy)
        self.call__init__(TaurusBaseModelWidget, designMode=designMode)

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # TaurusBaseWidget overwriting
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    def updateStyle(self):
        """overwritten from class:`taurus.qt.qtgui.base.TaurusBaseWidget`. It is called when
        the taurus model changes."""
        self.resizeColumns()
