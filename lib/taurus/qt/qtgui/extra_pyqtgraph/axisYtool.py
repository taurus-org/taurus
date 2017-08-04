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

from pyqtgraph import ViewBox
from taurus.qt.qtgui.base.taurusbase import TaurusBaseComponent

class Y2ViewBox(ViewBox, TaurusBaseComponent):

    def __init__(self, *args, **kwargs):
        TaurusBaseComponent.__init__(self, 'Y2ViewBox')
        ViewBox.__init__(self, *args, **kwargs)
        self.registerConfigProperty(self.getCurves, self.setCurves, 'Y2Curves')
        self.registerConfigProperty(self._getState, self.setState, 'viewState')
        self._isAttached = False
        self.plotItem = None
        self._curvesModelNames = []

    def attachToPlotItem(self, plot_item):
        if self._isAttached:
            return  # TODO: log a message it's already attached
        self._isAttached = True

        mainViewBox = plot_item.getViewBox()
        mainViewBox.sigResized.connect(self.updateViews)

        plot_item.getAxis('right').linkToView(self)
        self.setXLink(plot_item)
        self.plotItem = plot_item

    def updateViews(self, viewBox):
        self.setGeometry(viewBox.sceneBoundingRect())
        self.linkedViewChanged(viewBox, self.XAxis)

    def removeItem(self, item):
        ViewBox.removeItem(self, item)

        # when last curve is removed from self (axis Y2), we must remove the
        # axis from scene and hide the axis.
        if len(self.addedItems) < 1:
            self.plotItem.scene().removeItem(self)
            self.plotItem.hideAxis('right')

        self._curvesModelNames.remove(item.getFullModelNames())


    def addItem(self, item, ignoreBounds=False):
        ViewBox.addItem(self, item, ignoreBounds=ignoreBounds)

        if len(self.addedItems) == 1:
            # when the first curve is added to self (axis Y2), we must
            # add Y2 to main scene() and show the axis.
            self.plotItem.showAxis('right')
            self.plotItem.scene().addItem(self)

        if len(self.addedItems) > 0 and item.getFullModelNames() not in self._curvesModelNames:
            self._curvesModelNames.append(item.getFullModelNames())


    def getCurves(self):
        return self._curvesModelNames

    def setCurves(self, curves):
        self._curvesModelNames = curves

    def _getState(self):
        state = self.getState(copy=True)
        del state['viewRange']
        return state
