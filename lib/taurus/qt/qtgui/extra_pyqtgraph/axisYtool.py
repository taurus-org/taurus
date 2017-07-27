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


class Y2ViewBox(ViewBox):

    def __init__(self, *args, **kwargs):
        ViewBox.__init__(self, *args, **kwargs)
        self._isAttached = False
        self.plotItem = None

    @staticmethod
    def getY2ViewBox(plot_item):
        scene_items = plot_item.scene().items()

        for item in scene_items:
            if isinstance(item, Y2ViewBox):
                return item
        ret = Y2ViewBox()
        ret.attachToPlotItem(plot_item)
        return ret

    def attachToPlotItem(self, plot_item):
        if self._isAttached:
            return  # TODO: log a message it's already attached
        self._isAttached = True

        mainViewBox = plot_item.getViewBox()
        mainViewBox.sigResized.connect(self.updateViews)

        # make sure Y2 is shown
        # plot_item.showAxis('right')
        # add self to plotItem scene and link right and bottom axis to self
        # plot_item.scene().addItem(self)
        plot_item.getAxis('right').linkToView(self)
        self.setXLink(plot_item)

        self.plotItem = plot_item

    def updateViews(self, viewBox):
        self.setGeometry(viewBox.sceneBoundingRect())
        self.linkedViewChanged(viewBox, self.XAxis)

    def removeItem(self, item):
        ViewBox.removeItem(self, item)

        # if this axis dont have any curve associated, we may remove the
        # axis (Y2) from scene
        if len(self.addedItems) < 1:
            self.plotItem.scene().removeItem(self)
            self.plotItem.hideAxis('right')

    def addItem(self, item, ignoreBounds=False):
        ViewBox.addItem(self, item, ignoreBounds=ignoreBounds)

        if len(self.addedItems) == 1:
            self.plotItem.showAxis('right')
            self.plotItem.scene().addItem(self)



