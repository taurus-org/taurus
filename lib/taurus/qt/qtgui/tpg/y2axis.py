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

__all__ = ["Y2ViewBox"]

from pyqtgraph import ViewBox

from taurus.qt.qtcore.configuration.configuration import BaseConfigurableClass


class Y2ViewBox(ViewBox, BaseConfigurableClass):
    """
    A tool that inserts a secondary Y axis to a plot item (see
    :meth:`attachToPlotItem`).
    It is implemented as a :class:`pyqtgraph.ViewBox` and provides methods to
    add and remove :class:`pyqtgraph.PlotDataItem` objects to it.
    """

    def __init__(self, *args, **kwargs):
        BaseConfigurableClass.__init__(self)
        ViewBox.__init__(self, *args, **kwargs)

        self.registerConfigProperty(self.getCurves, self.setCurves, 'Y2Curves')
        self.registerConfigProperty(self._getState, self.setState, 'viewState')
        self._isAttached = False
        self.plotItem = None
        self._curvesModelNames = []

    def attachToPlotItem(self, plot_item):
        """Use this method to add this axis to a plot

        :param plot_item: (PlotItem)
        """
        if self._isAttached:
            return  # TODO: log a message it's already attached
        self._isAttached = True

        mainViewBox = plot_item.getViewBox()
        mainViewBox.sigResized.connect(self._updateViews)

        self.plotItem = plot_item

    def _updateViews(self, viewBox):
        self.setGeometry(viewBox.sceneBoundingRect())
        self.linkedViewChanged(viewBox, self.XAxis)

    def removeItem(self, item):
        """Reimplemented from :class:`pyqtgraph.ViewBox`"""
        ViewBox.removeItem(self, item)

        # when last curve is removed from self (axis Y2), we must remove the
        # axis from scene and hide the axis.
        if len(self.addedItems) < 1:
            self.plotItem.scene().removeItem(self)
            self.plotItem.hideAxis('right')

        self._curvesModelNames.remove(item.getFullModelNames())

    def addItem(self, item, ignoreBounds=False):
        """Reimplemented from :class:`pyqtgraph.ViewBox`"""
        ViewBox.addItem(self, item, ignoreBounds=ignoreBounds)

        if len(self.addedItems) == 1:
            # when the first curve is added to self (axis Y2), we must
            # add Y2 to main scene(), show the axis and link X axis to self.
            self.plotItem.showAxis('right')
            self.plotItem.scene().addItem(self)
            self.plotItem.getAxis('right').linkToView(self)
            self.setXLink(self.plotItem)

        if (len(self.addedItems) > 0
                and item.getFullModelNames() not in self._curvesModelNames):
            self._curvesModelNames.append(item.getFullModelNames())

    def getCurves(self):
        """Returns the curve model names of curves associated to the Y2 axis.

        :return: (list) List of tuples of model names (xModelName, yModelName)
                 from each curve in this view
        """
        return self._curvesModelNames

    def setCurves(self, curves):
        """Sets the curve names associated to the Y2 axis (but does not
        create/remove any curve.
        """
        self._curvesModelNames = curves

    def _getState(self):
        """Same as ViewBox.getState but removing viewRange conf to force
        a refresh with targetRange when loading
        """
        state = self.getState(copy=True)
        del state['viewRange']
        return state

    def clearItems(self):
        """Remove the added items"""
        for c in self.addedItems:
            self.removeItem(c)
