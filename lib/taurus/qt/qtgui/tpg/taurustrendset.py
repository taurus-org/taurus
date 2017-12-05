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
__all__ = ["TaurusTrendSet"]

"""This provides the pyqtgraph implementation of :class:`TaurusTrendSet`"""

import copy
import numpy
from taurus.core import TaurusEventType, TaurusTimeVal
from taurus.qt.qtgui.base import TaurusBaseComponent
from taurus.core.util.containers import ArrayBuffer, LoopList
from taurus.external.qt import Qt
from pyqtgraph import PlotDataItem

from forcedreadtool import ForcedReadTool

import taurus

CURVE_COLORS = [Qt.QPen(Qt.Qt.red),
                Qt.QPen(Qt.Qt.blue),
                Qt.QPen(Qt.Qt.green),
                Qt.QPen(Qt.Qt.magenta),
                Qt.QPen(Qt.Qt.cyan),
                Qt.QPen(Qt.Qt.yellow),
                Qt.QPen(Qt.Qt.white)]


class TaurusTrendSet(PlotDataItem, TaurusBaseComponent):
    """
    A PlotDataItem for displaying trend curve(s) associated to a
    TaurusAttribute. The TaurusTrendSet itself does not contain any data,
    but acts as a manager that dynamically adds/removes curve(s) (other
    PlotDataItems) to its associated plot.

    If the attribute is a scalar, the Trend Set generates only one curve
    representing the evolution of the value of the attribute. If the attribute
    is an array, as many curves as the attribute size are created,
    each representing the evolution of the value of a component of the array.

    When an event is received, all curves belonging to a TaurusTrendSet
    are updated.

    TaurusTrendSet can be considered used as a container of (sorted) curves.
    As such, the curves contained by it can be accessed by index::

        ts = TaurusTrendSet('eval:rand(3)')
        # (...) wait for a Taurus Event arriving so that the curves are created
        ncurves = len(ts)  # ncurves will be 3 (assuming the event arrived)
        curve0 = ts[0]     # you can access the curve by index


    Note that internally each curve is a :class:`pyqtgraph.PlotDataItem` (i.e.,
    it is not aware of events by itself, but it relies on the TaurusTrendSet
    object to update its values)
    """

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
        self._curves = []
        self._timer = Qt.QTimer()
        self._timer.timeout.connect(self._forceRead)
        self._legend = None

        # register config properties
        self.setModelInConfig(True)
        self.registerConfigProperty(self._getCurvesOpts, self._setCurvesOpts,
                                    'opts')
        # TODO: store forceReadPeriod config
        # TODO: store _maxBufferSize config

    def name(self):
        """Reimplemented from PlotDataItem to avoid having the ts itself added
        to legends.

        .. seealso:: :meth:`basename`
        """
        return None

    def base_name(self):
        """Returns the name of the trendset, which is used as a prefix for
        constructing the associated curves names

        .. seealso:: :meth:`name`
        """
        return PlotDataItem.name(self)

    def __getitem__(self, k):
        return self._curves[k]

    def __len__(self):
        return len(self._curves)

    def __contains__(self, k):
        return k in self._curves

    def setModel(self, name):
        """Reimplemented from :meth:`TaurusBaseComponent.setModel`"""
        TaurusBaseComponent.setModel(self, name)
        # force a read to ensure that the curves are created
        self._forceRead()

    def _initBuffers(self, ntrends):
        """initializes new x and y buffers"""

        self._yBuffer = ArrayBuffer(numpy.zeros(
            (min(128, self._maxBufferSize), ntrends), dtype='d'),
            maxSize=self._maxBufferSize)

        self._xBuffer = ArrayBuffer((numpy.zeros(
            min(128, self._maxBufferSize), dtype='d')),
            maxSize=self._maxBufferSize)

    def _initCurves(self, ntrends):
        """ Initializes new curves """

        # self._removeFromLegend(self._legend)
        self._curves = []
        self._curveColors.setCurrentIndex(-1)

        a = self._args
        kw = self._kwargs.copy()

        base_name = (self.base_name()
                or taurus.Attribute(self.getModel()).getSimpleName())

        for i in xrange(ntrends):
            subname = "%s[%i]" % (base_name, i)
            kw['name'] = subname
            curve = PlotDataItem(*a, **kw)
            if 'pen' not in kw:
                curve.setPen(self._curveColors.next().color())
            self._curves.append(curve)
        self._updateViewBox()

    def _addToLegend(self, legend):
        # ------------------------------------------------------------------
        # In theory, TaurusTrendSet only uses viewBox.addItem to add its
        # sub-curves to the plot. In theory this should not add the curves
        # to the legend, and therefore we should do it here.
        # But somewhere the curves are already being added to the legend, and
        # if we re-add them here we get duplicated legend entries
        # TODO: Find where are the curves being added to the legend
        pass
        #if legend is None:
        #    return
        #for c in self._curves:
        #    legend.addItem(c, c.name())
        # -------------------------------------------------------------------

    def _removeFromLegend(self, legend):
        if legend is None:
            return
        for c in self._curves:
            legend.removeItem(c.name())

    def _updateViewBox(self):
        """Add/remove the "extra" curves from the viewbox if needed"""
        if self._curves:
            viewBox = self.getViewBox()
            self.forgetViewBox()
        for curve in self._curves:
            curve.forgetViewBox()
            curve_viewBox = curve.getViewBox()

            if curve_viewBox is not None:
                curve_viewBox.removeItem(curve)
            if viewBox is not None:
                viewBox.addItem(curve)

    def _updateBuffers(self, evt_value):
        """Update the x and y buffers with the new data. If the new data is
        not compatible with the existing buffers, the buffers are reset
        """

        # TODO: we use .magnitude below to avoid issue #509 in pint
        # https://github.com/hgrecco/pint/issues/509

        ntrends = numpy.size(evt_value.rvalue.magnitude)

        if not self._isDataCompatible(evt_value, ntrends):
            self._initBuffers(ntrends)
            self._yUnits = evt_value.rvalue.units
            self._initCurves(ntrends)

        try:
            self._yBuffer.append(evt_value.rvalue.to(self._yUnits).magnitude)
        except Exception as e:
            self.warning('Problem updating buffer Y (%s):%s',
                         evt_value.rvalue, e)
            evt_value = None

        try:
            self._xBuffer.append(evt_value.time.totime())
        except Exception as e:
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

    def _addData(self, x, y):
        for i, curve in enumerate(self._curves):
            curve.setData(x=x, y=y[:, i])

    def handleEvent(self, evt_src, evt_type, evt_value):
        """Reimplementation of :meth:`TaurusBaseComponent.handleEvent`"""

        # model = evt_src if evt_src is not None else self.getModelObj()

        # TODO: support boolean values from evt_value.rvalue
        if evt_value is None or evt_value.rvalue is None:
            self.info("Invalid value. Ignoring.")
            return
        else:
            try:
                xValues, yValues = self._updateBuffers(evt_value)
            except Exception:
                # TODO: handle dropped events see: TaurusTrend._onDroppedEvent
                raise

        self._addData(xValues, yValues)

    def parentChanged(self):
        """Reimplementation of :meth:`PlotDataItem.parentChanged` to handle
        the change of the containing viewbox
        """
        PlotDataItem.parentChanged(self)

        self._updateViewBox()

        # update legend if needed
        try:
            legend =  self.getViewWidget().getPlotItem().legend
        except Exception:
            legend = None
        if legend is not self._legend:
            self._removeFromLegend(self._legend)
            self._addToLegend(legend)
            self._legend = legend

        # Set period from ForcedReadTool (if found)
        try:
            for a in self.getViewBox().menu.actions():
                if isinstance(a, ForcedReadTool) and a.autoconnect():
                    self.setForcedReadPeriod(a.period())
                    break
        except Exception as e:
            self.debug('cannot set period from ForcedReadTool: %r', e)

    @property
    def forcedReadPeriod(self):
        """Returns the forced reading period (in ms). A value <= 0 indicates
        that the forced reading is disabled
        """
        return self._timer.interval()

    def setForcedReadPeriod(self, period):
        """
        Forces periodic reading of the subscribed attribute in order to show
        new points even if no events are received.
        It will create fake events as needed with the read value.
        It will also block the plotting of regular events when period > 0.

        :param period: (int) period in milliseconds. Use period<=0 to stop the
                       forced periodic reading
        """

        # stop the timer and remove the __ONLY_OWN_EVENTS filter
        self._timer.stop()
        filters = self.getEventFilters()
        if self.__ONLY_OWN_EVENTS in filters:
            filters.remove(self.__ONLY_OWN_EVENTS)
            self.setEventFilters(filters)

        # if period is positive, set the filter and start
        if period > 0:
            self.insertEventFilter(self.__ONLY_OWN_EVENTS)
            self._timer.start(period)

    def _forceRead(self, cache=True):
        """Forces a read of the associated attribute.

        :param cache: (bool) If True, the reading will be done with cache=True
                      but the timestamp of the resulting event will be replaced
                      by the current time. If False, no cache will be used at
                      all.
        """
        value = self.getModelValueObj(cache=cache)
        if cache:
            value = copy.copy(value)
            value.time = TaurusTimeVal.now()
        self.fireEvent(self, TaurusEventType.Periodic, value)

    def __ONLY_OWN_EVENTS(self, s, t, v):
        """An event filter that rejects all events except those that originate
        from this object
        """
        if s is self:
            return s, t, v
        else:
            return None

    def _getCurvesOpts(self):
        """returns a list of serialized opts (one for each curve)"""
        from taurus.qt.qtgui.tpg import serialize_opts
        return [serialize_opts(copy.copy(c.opts)) for c in self._curves]

    def _setCurvesOpts(self, all_opts):
        """restore options to curves"""
        # If no curves are yet created, force a read to create them
        if not self._curves:
            self._forceRead(cache=True)
        # Check consistency in the number of curves
        if len(self._curves) != len(all_opts):
            self.warning(
                'Cannot apply curve options (mismatch in curves number)')
            return
        from taurus.qt.qtgui.tpg import deserialize_opts
        for c, opts in zip(self._curves, all_opts):
            c.opts = deserialize_opts(opts)

            # This is a workaround for the following pyqtgraph's bug:
            # https://github.com/pyqtgraph/pyqtgraph/issues/531
            if opts['connect'] == 'all':
                c.opts['connect'] = 'all'
            elif opts['connect'] == 'pairs':
                c.opts['connect'] = 'pairs'
            elif opts['connect'] == 'finite':
                c.opts['connect'] = 'finite'




if __name__ == '__main__':
    import sys
    import pyqtgraph as pg
    from taurus.qt.qtgui.application import TaurusApplication
    from taurus.qt.qtgui.tpg import (TaurusTrendSet, DateAxisItem,
                                     XAutoPanTool, TaurusModelChooserTool,
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

    autopan = XAutoPanTool()
    autopan.attachToPlotItem(w.getPlotItem())

    # add legend to the plot, for that we have to give a name to plot items
    w.addLegend()

    # adding a taurus data item...
    c2 = TaurusTrendSet(name='foo')
    c2.setModel('eval:rand(2)')
    # c2.setForcedReadPeriod(500)

    w.addItem(c2)

    # ...and remove it after a while
    def rem():
        w.removeItem(c2)
    Qt.QTimer.singleShot(2000, rem)


    # modelchooser = TaurusModelChooserTool(itemClass=TaurusTrendSet)
    # modelchooser.attachToPlotItem(w.getPlotItem())

    w.show()

    ret = app.exec_()

    import pprint
    # pprint.pprint(c2.createConfig())

    sys.exit(ret)
