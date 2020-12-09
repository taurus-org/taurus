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
model in a table widget"""

from __future__ import absolute_import

from taurus.qt.qtgui.model import TaurusBaseModelWidget
from .qtable import QBaseTableWidget


__all__ = ["TaurusBaseTableWidget"]

__docformat__ = 'restructuredtext'


class TaurusBaseTableWidget(QBaseTableWidget, TaurusBaseModelWidget):
    """A class:`taurus.qt.qtgui.tree.QBaseTableWidget` that connects to a
    taurus model.

    Filters can be inserted into this widget to restrict the items that are
    seen."""

    def __init__(self, parent=None, designMode=False, with_filter_widget=True,
                 perspective=None, proxy=None):
        self.call__init__(QBaseTableWidget, parent, designMode=designMode,
                          with_filter_widget=with_filter_widget,
                          perspective=perspective, proxy=proxy)
        self.call__init__(TaurusBaseModelWidget, designMode=designMode)
