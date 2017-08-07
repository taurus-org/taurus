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

from taurus.external.qt import QtGui
from taurus.qt.qtcore.configuration.configuration import BaseConfigurableClass


class PlotLegendTool(QtGui.QAction, BaseConfigurableClass):
    """
    This tool adds an action to a menu for show/hide the legend
    within the parent item (widget, view, plotItem)
    """
    def __init__(self, parent=None):
        BaseConfigurableClass.__init__(self)
        QtGui.QAction.__init__(self, 'Show legend', parent)
        self.registerConfigProperty(self.isChecked, self.setChecked, 'checked')
        self.setCheckable(True)
        self.toggled.connect(self.onToggled)
        self._legend = None

    def attachToPlotItem(self, plotItem, parentWidget=None):
        self._legend = plotItem.addLegend()
        self.setChecked(True)
        menu = plotItem.getViewBox().menu
        menu.addAction(self)
        self.setParent(parentWidget or menu)


    def onToggled(self, checked):
        if checked:
            self._legend.show()
        else:
            self._legend.hide()