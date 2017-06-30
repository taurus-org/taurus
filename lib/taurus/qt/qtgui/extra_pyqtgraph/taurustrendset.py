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


# TODO: Document

from taurus.qt.qtgui.base import TaurusBaseComponent
from taurus.core.util.containers import ArrayBuffer, LoopList
from taurus.external.qt import Qt
from taurus.external.pint import Q_
from pyqtgraph import PlotDataItem
import numpy

import taurus


CURVE_COLORS = [Qt.QPen(Qt.Qt.red),
                Qt.QPen(Qt.Qt.blue),
                Qt.QPen(Qt.Qt.green),
                Qt.QPen(Qt.Qt.magenta),
                Qt.QPen(Qt.Qt.cyan),
                Qt.QPen(Qt.Qt.yellow),
                Qt.QPen(Qt.Qt.white)]


class TaurusTrendSet(PlotDataItem, TaurusBaseComponent):


    def __init__(self, *args, **kwargs):
        PlotDataItem.__init__(self, *args, **kwargs)
        TaurusBaseComponent.__init__(self, 'TaurusBaseComponent')

        self._UImodifiable = False

        self._maxBufferSize = 65536  # (=2**16, i.e., 64K events))
        self._xBuffer = None
        self._yBuffer = None
        self._curveColors = LoopList(CURVE_COLORS)
        self._args = args
        self._kwargs = kwargs
        self._curves = None


    def _initBuffers(self, ntrends):

        self._yBuffer = ArrayBuffer(numpy.zeros(
            (min(128, self._maxBufferSize), ntrends), dtype='d'),
            maxSize=self._maxBufferSize)

        self._xBuffer = ArrayBuffer((numpy.zeros(
            min(128, self._maxBufferSize), dtype='d')),
            maxSize=self._maxBufferSize)

    def _initCurves(self, ntrends):
        # clean previous curves
        # viewBox = self.getViewBox()


        # if viewBox is not None:
        #     viewBox.removeItem(self)
        #

        self._curves = []
        self._curveColors.setCurrentIndex(-1)

        # create as many curves as the dim_x of the given model and add
        # them to the TrendSet
        a = self._args
        kw = self._kwargs.copy()

        name = taurus.Attribute(self.getModel()).getSimpleName()
        print name


        for i in xrange(0, ntrends):
            subname = "%s[%i]" % (name, i)
            kw['name'] = subname
            curve = PlotDataItem(*a, **kw)
            if 'pen' not in kw:
                curve.setPen(self._curveColors.next().color())
            self._curves.append(curve)
        self._updateViewBox()

    def _updateViewBox(self):
        """Add/remove the "extra" curves from the viewbox if needed"""
        if self._curves is not None:
            curves = self._curves
            viewBox = self.getViewBox()

            self.forgetViewBox()
            for curve in curves:
                curve.forgetViewBox()
                curve_viewBox = curve.getViewBox()

                if curve_viewBox is not None and viewBox is None:
                    curve_viewBox.removeItem(curve)
                if viewBox is not None:
                    viewBox.addItem(curve)

    def _updateBuffers(self, evt_value):

        # TODO: we use .magnitude below to avoid issue #509 in pint
        # https://github.com/hgrecco/pint/issues/509
        ntrends = numpy.size(evt_value.rvalue.magnitude)

        if not self._isDataCompatible(evt_value, ntrends):
            self._initBuffers(ntrends)
            self._yUnits = evt_value.rvalue.units
            self._initCurves(ntrends)

        try:
            self._yBuffer.append(evt_value.rvalue.to(self._yUnits).magnitude)
        except Exception, e:
            self.warning('Problem updating buffer Y (%s):%s',
                         evt_value.rvalue, e)
            evt_value = None

        try:
            self._xBuffer.append(evt_value.time.totime())
        except Exception, e:
            self.warning('Problem updating buffer X (%s):%s',
                         evt_value, e)

        return self._xBuffer.contents(), self._yBuffer.contents()

    def _isDataCompatible(self, evt_value, ntrends):
        """
        Check that the new evt_value is compatible with the current data in the
        buffers. Check shape and unit compatibility.
        """
        if self._xBuffer is None or self._yBuffer is None:
            return False
        rvalue = evt_value.rvalue

        if rvalue.dimensionality != self._yUnits.dimensionality:
            return False

        current_trends = numpy.prod(self._yBuffer.contents().shape[1:])

        if ntrends != current_trends:
            return False

        return True

    def addData(self, x, y):
        for i, curve in enumerate(self._curves):
            curve.setData(x=x, y=y[:, i])

    def handleEvent(self, evt_src, evt_type, evt_value):
        # model = evt_src if evt_src is not None else self.getModelObj()

        # TODO: support booleans values from evt_value.rvalue
        if evt_value is None or evt_value.rvalue is None:
            self.info("Invalid value. Ignoring.")
            return
        else:
            try:
                xValues, yValues = self._updateBuffers(evt_value)
            except Exception:
                # TODO: handle dropped events see: TaurusTrend._onDroppedEvent
                raise

        self.addData(xValues, yValues)

    def parentChanged(self):
        self._updateViewBox()
        PlotDataItem.parentChanged(self)


if __name__ == '__main__':
    import sys
    import numpy
    import pyqtgraph as pg
    from taurus.qt.qtgui.application import TaurusApplication
    from taurus.qt.qtgui.extra_pyqtgraph.taurustrendset import TaurusTrendSet
    from taurus.qt.qtgui.extra_pyqtgraph.dateaxisitem import DateAxisItem
    from taurus.qt.qtgui.extra_pyqtgraph.oscmodetool import FixedRangeScale

    from taurus.qt.qtgui.extra_pyqtgraph.taurusmodelchoosertool import(
        TaurusModelChooserTool)
    from taurus.qt.qtgui.extra_pyqtgraph.curvesPropertiesTool import (
        CurvesPropertiesTool)


    from taurus.core.taurusmanager import TaurusManager
    taurusM = TaurusManager()
    taurusM.changeDefaultPollingPeriod(1000)  # ms


    app = TaurusApplication()



    # a standard pyqtgraph plot_item
    axis = DateAxisItem(orientation='bottom')
    w = pg.PlotWidget()
    axis.attachToPlotItem(w.getPlotItem())

    cp = CurvesPropertiesTool()
    cp.attachToPlotItem(w.getPlotItem())



    oscMode = FixedRangeScale()
    oscMode.attachToPlotItem(w.getPlotItem())

    # add legend to the plot, for that we have to give a name to plot items
    # w.addLegend()

    # adding a taurus data item
    c2 = TaurusTrendSet(name='ffff')

    w.addItem(c2)

    c2.setModel('eval:rand(5)')

    # c2.setModel('sys/tg_test/1/wave')




    tmct = TaurusModelChooserTool(itemClass=TaurusTrendSet)
    tmct.attachToPlotItem(w.getPlotItem())


    w.show()


    sys.exit(app.exec_())