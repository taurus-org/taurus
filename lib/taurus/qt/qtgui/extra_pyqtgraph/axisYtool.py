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
from taurus.qt.qtcore.configuration.configuration import BaseConfigurableClass

class Y2ViewBox(ViewBox, BaseConfigurableClass):

    def __init__(self, *args, **kwargs):
        BaseConfigurableClass.__init__(self)
        ViewBox.__init__(self, *args, **kwargs)

        # this property handle the curves added in self. Returns a list with
        # models names (xModelName, yModelName) from each curve in this view.
        # This class doesn't add the curves when we restore the configuration,
        # just retrieve a list of modelNames and we have to create the curves
        # and add to self from outside the class.
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
            # add Y2 to main scene(), show the axis and link X axis to self.
            self.plotItem.showAxis('right')
            self.plotItem.scene().addItem(self)
            self.plotItem.getAxis('right').linkToView(self)
            self.setXLink(self.plotItem)

        if len(self.addedItems) > 0 and item.getFullModelNames() not in self._curvesModelNames:
            self._curvesModelNames.append(item.getFullModelNames())

    def getCurves(self):
        return self._curvesModelNames

    def setCurves(self, curves):
        self._curvesModelNames = curves

    def _getState(self):
        """Same as ViewBox.getState but removing viewRange conf to force
        a refresh with targetRange when loading
        """
        state = self.getState(copy=True)
        del state['viewRange']
        return state

    def clearCurves(self):
        for c in self.addedItems:
            self.removeItem(c)