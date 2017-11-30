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
__all__ = ["PlotLegendTool"]

from taurus.external.qt import QtGui
from taurus.qt.qtcore.configuration.configuration import BaseConfigurableClass


class PlotLegendTool(QtGui.QWidgetAction, BaseConfigurableClass):
    """
    This tool adds a legend to the PlotItem to which it is attached, and it
    inserts a checkable menu action for showing/hiding the legend.

    Implementation note: this is implemented as a QWidgetAction+QCheckBox
    instead of a checkable QAction to avoid closing the menu when toggling it
    """
    def __init__(self, parent=None):
        BaseConfigurableClass.__init__(self)
        QtGui.QWidgetAction.__init__(self, parent)
        self._cb = QtGui.QCheckBox()
        self._cb.setText('Show legend')
        self.setDefaultWidget(self._cb)
        self.registerConfigProperty(self._cb.isChecked, self._cb.setChecked,
                                    'checked')
        # TODO: register config prop for legend position
        self._cb.toggled.connect(self._onToggled)
        self._legend = None

    def attachToPlotItem(self, plotItem):
        """
        Use this method to add this tool to a plot

        :param plot_item: (PlotItem)
        """
        self._legend = plotItem.addLegend()
        self._cb.setChecked(True)
        menu = plotItem.getViewBox().menu
        menu.addAction(self)

    def _onToggled(self, checked):
        if checked:
            self._legend.show()
        else:
            self._legend.hide()