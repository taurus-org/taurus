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
from taurus.external.qt import QtGui, QtCore
import pyqtgraph as pg


class FixedRangeScale(QtGui.QAction):

    def __init__(self, parent=None):
        QtGui.QAction.__init__(self, 'Fixed range scale', parent)
        self.setCheckable(True)
        self.toggled.connect(self.onToggled)
        self._timer = QtCore.QTimer()
        self._timer.timeout.connect(self.updateRange)
        self._originalXAutoRange = None
        self._viewBox = None
        self._scrollStep = 0.2


    def attachToPlotItem(self, plot_item):
        self._viewBox = plot_item.getViewBox()
        menu = self._viewBox.menu
        menu.addAction(self)
        self.setParent(menu)
        self._originalXAutoRange = self._viewBox.autoRangeEnabled()[0]
        self._viewBox.sigXRangeChanged.connect(self._onXRangeChanged)

    def onToggled(self, checked):
        if checked:
            self._originalXAutoRange = self._viewBox.autoRangeEnabled()[0]
            self._viewBox.enableAutoRange(x=False)

            axisXrange = self._viewBox.state['viewRange'][0]
            x_range = axisXrange[1] - axisXrange[0]

            t = int(x_range/10.)*1000
            t = min(3000, t)
            t = max(50, t)

            self._timer.start(t)
        else:
            self._timer.stop()
            self._viewBox.enableAutoRange(x=self._originalXAutoRange)

    def _onXRangeChanged(self, viewBox, viewRange):
        self.setChecked(False)


    def updateRange(self):
        if len(self._viewBox.addedItems) < 1:
            self._timer.stop()




        children_bounds = self._viewBox.childrenBounds()
        _, boundMax = children_bounds[0]
        axis_range = self._viewBox.state['viewRange']
        axis_Xrange = axis_range[0]

        x_range = axis_Xrange[1] - axis_Xrange[0]


        if boundMax > axis_Xrange[1] or boundMax < axis_Xrange[0]:
            x_min = boundMax - axis_Xrange[1]
            x_max = boundMax - axis_Xrange[0]
            step = min(max(x_range * self._scrollStep, x_min), x_max)

            self._viewBox.sigXRangeChanged.disconnect(self._onXRangeChanged)
            self._viewBox.setXRange(axis_Xrange[0]+step, axis_Xrange[1]+step, padding=0.0, update=False)
            self._viewBox.sigXRangeChanged.connect(self._onXRangeChanged)



