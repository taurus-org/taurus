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

"""
scales.py: Custom scales used by taurus.qt.qtgui.plot module
"""
from __future__ import print_function

import numpy
from datetime import datetime, timedelta
from time import mktime
from taurus.external.qt import Qt

import guiqwt
__guiqwt_version = list(map(int, guiqwt.__version__.split('.')[:3]))

if __guiqwt_version <= [2, 3, 1]:
    import taurus.external.qt.Qwt5 as qwt
else:
    import qwt

__all__ = ["DateTimeScaleEngine", "DeltaTimeScaleEngine", "FixedLabelsScaleEngine",
           "FancyScaleDraw", "TaurusTimeScaleDraw", "DeltaTimeScaleDraw",
           "FixedLabelsScaleDraw"]


def _getDefaultAxisLabelsAlignment(axis, rotation):
    '''return a "smart" alignment for the axis labels depending on the axis
    and the label rotation

    :param axis: (qwt.QwtPlot.Axis) the axis
    :param rotation: (float) The rotation (in degrees, clockwise-positive)

    :return: (Qt.Alignment) an alignment
    '''
    if axis == qwt.QwtPlot.xBottom:
        if rotation == 0:
            return Qt.Qt.AlignHCenter | Qt.Qt.AlignBottom
        elif rotation < 0:
            return Qt.Qt.AlignLeft | Qt.Qt.AlignBottom
        else:
            return Qt.Qt.AlignRight | Qt.Qt.AlignBottom
    elif axis == qwt.QwtPlot.yLeft:
        if rotation == 0:
            return Qt.Qt.AlignLeft | Qt.Qt.AlignVCenter
        elif rotation < 0:
            return Qt.Qt.AlignLeft | Qt.Qt.AlignBottom
        else:
            return Qt.Qt.AlignLeft | Qt.Qt.AlignTop
    elif axis == qwt.QwtPlot.yRight:
        if rotation == 0:
            return Qt.Qt.AlignRight | Qt.Qt.AlignVCenter
        elif rotation < 0:
            return Qt.Qt.AlignRight | Qt.Qt.AlignTop
        else:
            return Qt.Qt.AlignRight | Qt.Qt.AlignBottom
    elif axis == qwt.QwtPlot.xTop:
        if rotation == 0:
            return Qt.Qt.AlignHCenter | Qt.Qt.AlignTop
        elif rotation < 0:
            return Qt.Qt.AlignLeft | Qt.Qt.AlignTop
        else:
            return Qt.Qt.AlignRight | Qt.Qt.AlignTop


class FancyScaleDraw(qwt.QwtScaleDraw):

    '''This is a scaleDraw with a tuneable palette and label formats'''

    def __init__(self, format=None, palette=None):
        qwt.QwtScaleDraw.__init__(self)
        self._labelFormat = format
        self._palette = palette

    def setPalette(self, palette):
        '''pass a QPalette or None to use default'''
        self._palette = palette

    def getPalette(self):
        return self._palette

    def setLabelFormat(self, format):
        '''pass a format string (e.g. "%g") or None to use default (it uses the locale)'''
        self._labelFormat = format
        self.invalidateCache()  # to force repainting of the labels

    def getLabelFormat(self):
        '''pass a format string (e.g. "%g") or None to use default (it uses the locale)'''
        return self._labelFormat

    def label(self, val):
        if str(self._labelFormat) == "":
            return qwt.QwtText()
        if self._labelFormat is None:
            return qwt.QwtScaleDraw.label(self, val)
        else:
            return qwt.QwtText(self._labelFormat % val)

    def draw(self, painter, palette):
        if self._palette is None:
            qwt.QwtScaleDraw.draw(self, painter, palette)
        else:
            qwt.QwtScaleDraw.draw(self, painter, self._palette)


class DateTimeScaleEngine(qwt.QwtLinearScaleEngine):

    def __init__(self, scaleDraw=None):
        qwt.QwtLinearScaleEngine.__init__(self)
        self.setScaleDraw(scaleDraw)

    def setScaleDraw(self, scaleDraw):
        self._scaleDraw = scaleDraw

    def scaleDraw(self):
        return self._scaleDraw

    def divideScale(self, x1, x2, maxMajSteps, maxMinSteps, stepSize):
        ''' Reimplements qwt.QwtLinearScaleEngine.divideScale

        **Important**: The stepSize parameter is **ignored**.

        :return: (qwt.QwtScaleDiv) a scale division whose ticks are aligned with
                 the natural time units '''

        # if stepSize != 0:
        #    scaleDiv = qwt.QwtLinearScaleEngine.divideScale(self, x1, x2, maxMajSteps, maxMinSteps, stepSize)
        #    scaleDiv.datetimeLabelFormat = "%Y/%m/%d %H:%M%S.%f"
        #    return scaleDiv

        interval = qwt.QwtInterval(x1, x2).normalized()
        if interval.width() <= 0:
            return qwt.QwtScaleDiv()

        dt1 = datetime.fromtimestamp(interval.minValue())
        dt2 = datetime.fromtimestamp(interval.maxValue())

        if dt1.year < 1900 or dt2.year > 9999:  # limits in time.mktime and datetime
            return qwt.QwtScaleDiv()

        majticks = []
        medticks = []
        minticks = []

        dx = interval.width()

        # = 3600s*24*(365+366) = 2 years (counting a leap year)
        if dx > 63072001:
            format = "%Y"
            for y in range(dt1.year + 1, dt2.year):
                dt = datetime(year=y, month=1, day=1)
                majticks.append(mktime(dt.timetuple()))

        elif dx > 5270400:  # = 3600s*24*61 = 61 days
            format = "%Y %b"
            d = timedelta(days=31)
            dt = dt1.replace(day=1, hour=0, minute=0,
                             second=0, microsecond=0) + d
            while(dt < dt2):
                # make sure that we are on day 1 (even if always sum 31 days)
                dt = dt.replace(day=1)
                majticks.append(mktime(dt.timetuple()))
                dt += d

        elif dx > 172800:  # 3600s24*2 = 2 days
            format = "%b/%d"
            d = timedelta(days=1)
            dt = dt1.replace(hour=0, minute=0, second=0, microsecond=0) + d
            while(dt < dt2):
                majticks.append(mktime(dt.timetuple()))
                dt += d

        elif dx > 7200:  # 3600s*2 = 2hours
            format = "%b/%d-%Hh"
            d = timedelta(hours=1)
            dt = dt1.replace(minute=0, second=0, microsecond=0) + d
            while(dt < dt2):
                majticks.append(mktime(dt.timetuple()))
                dt += d

        elif dx > 1200:  # 60s*20 =20 minutes
            format = "%H:%M"
            d = timedelta(minutes=10)
            dt = dt1.replace(minute=(dt1.minute // 10) * 10,
                             second=0, microsecond=0) + d
            while(dt < dt2):
                majticks.append(mktime(dt.timetuple()))
                dt += d

        elif dx > 120:  # =60s*2 = 2 minutes
            format = "%H:%M"
            d = timedelta(minutes=1)
            dt = dt1.replace(second=0, microsecond=0) + d
            while(dt < dt2):
                majticks.append(mktime(dt.timetuple()))
                dt += d

        elif dx > 20:  # 20 s
            format = "%H:%M:%S"
            d = timedelta(seconds=10)
            dt = dt1.replace(second=(dt1.second // 10) * 10, microsecond=0) + d
            while(dt < dt2):
                majticks.append(mktime(dt.timetuple()))
                dt += d

        elif dx > 2:  # 2s
            format = "%H:%M:%S"
            majticks = list(range(int(x1) + 1, int(x2)))

        else:  # less than 2s (show microseconds)
            scaleDiv = qwt.QwtLinearScaleEngine.divideScale(
                self, x1, x2, maxMajSteps, maxMinSteps, stepSize)
            self.scaleDraw().setDatetimeLabelFormat("%S.%f")
            return scaleDiv

        # make sure to comply with maxMajTicks
        L = len(majticks)
        if L > maxMajSteps:
            majticks = majticks[::int(numpy.ceil(float(L) / maxMajSteps))]

        scaleDiv = qwt.QwtScaleDiv(interval, minticks, medticks, majticks)
        self.scaleDraw().setDatetimeLabelFormat(format)
        if x1 > x2:
            scaleDiv.invert()

        # START DEBUG
        # print "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
        # for tk in  scaleDiv.ticks(scaleDiv.MajorTick):
        #    print datetime.fromtimestamp(tk).isoformat()
        # print "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
        # END DEBUG

        return scaleDiv

    @staticmethod
    def getDefaultAxisLabelsAlignment(axis, rotation):
        '''return a "smart" alignment for the axis labels depending on the axis
        and the label rotation

        :param axis: (qwt.QwtPlot.Axis) the axis
        :param rotation: (float) The rotation (in degrees, clockwise-positive)

        :return: (Qt.Alignment) an alignment
        '''
        return _getDefaultAxisLabelsAlignment(axis, rotation)

    @staticmethod
    def enableInAxis(plot, axis, scaleDraw=None, rotation=None):
        '''convenience method that will enable this engine in the given
        axis. Note that it changes the ScaleDraw as well.

        :param plot: (qwt.QwtPlot) the plot to change
        :param axis: (qwt.QwtPlot.Axis) the id of the axis
        :param scaleDraw: (qwt.QwtScaleDraw) Scale draw to use. If None given,
                          the current ScaleDraw for the plot will be used if
                          possible, and a :class:`TaurusTimeScaleDraw` will be set if not
        :param rotation: (float or None) The rotation of the labels (in degrees, clockwise-positive)
        '''
        if scaleDraw is None:
            scaleDraw = plot.axisScaleDraw(axis)
            if not isinstance(scaleDraw, TaurusTimeScaleDraw):
                scaleDraw = TaurusTimeScaleDraw()
        plot.setAxisScaleDraw(axis, scaleDraw)
        plot.setAxisScaleEngine(axis, DateTimeScaleEngine(scaleDraw))
        if rotation is not None:
            alignment = DateTimeScaleEngine.getDefaultAxisLabelsAlignment(
                axis, rotation)
            plot.setAxisLabelRotation(axis, rotation)
            plot.setAxisLabelAlignment(axis, alignment)

    @staticmethod
    def disableInAxis(plot, axis, scaleDraw=None, scaleEngine=None):
        '''convenience method that will disable this engine in the given
        axis. Note that it changes the ScaleDraw as well.

        :param plot: (qwt.QwtPlot) the plot to change
        :param axis: (qwt.QwtPlot.Axis) the id of the axis
        :param scaleDraw: (qwt.QwtScaleDraw) Scale draw to use. If None given,
                          a :class:`FancyScaleDraw` will be set
        :param scaleEngine: (qwt.QwtScaleEngine) Scale draw to use. If None given,
                          a :class:`qwt.QwtLinearScaleEngine` will be set
        '''
        if scaleDraw is None:
            scaleDraw = FancyScaleDraw()
        if scaleEngine is None:
            scaleEngine = qwt.QwtLinearScaleEngine()
        plot.setAxisScaleEngine(axis, scaleEngine)
        plot.setAxisScaleDraw(axis, scaleDraw)


class TaurusTimeScaleDraw(FancyScaleDraw):

    def __init__(self, *args):
        FancyScaleDraw.__init__(self, *args)

    def setDatetimeLabelFormat(self, format):
        self._datetimeLabelFormat = format

    def datetimeLabelFormat(self):
        return self._datetimeLabelFormat

    def label(self, val):
        if str(self._labelFormat) == "":
            return qwt.QwtText()
        # From val to a string with time
        t = datetime.fromtimestamp(val)
        try:  # If the scaleDiv was created by a DateTimeScaleEngine it has a _datetimeLabelFormat
            s = t.strftime(self._datetimeLabelFormat)
        except AttributeError as e:
            print("Warning: cannot get the datetime label format (Are you using a DateTimeScaleEngine?)")
            s = t.isoformat(' ')
        return qwt.QwtText(s)


class DeltaTimeScaleEngine(qwt.QwtLinearScaleEngine):

    def __init__(self, scaleDraw=None):
        qwt.QwtLinearScaleEngine.__init__(self)
        self.setScaleDraw(scaleDraw)

    def setScaleDraw(self, scaleDraw):
        self._scaleDraw = scaleDraw

    def scaleDraw(self):
        return self._scaleDraw

    def divideScale(self, x1, x2, maxMajSteps, maxMinSteps, stepSize):
        ''' Reimplements qwt.QwtLinearScaleEngine.divideScale

        :return: (qwt.QwtScaleDiv) a scale division whose ticks are aligned with
                 the natural delta time units '''
        interval = qwt.QwtInterval(x1, x2).normalized()
        if interval.width() <= 0:
            return qwt.QwtScaleDiv()
        d_range = interval.width()
        if d_range < 2:  # 2s
            return qwt.QwtLinearScaleEngine.divideScale(self, x1, x2, maxMajSteps, maxMinSteps, stepSize)
        elif d_range < 20:  # 20 s
            s = 1
        elif d_range < 120:  # =60s*2 = 2 minutes
            s = 10
        elif d_range < 1200:  # 60s*20 =20 minutes
            s = 60
        elif d_range < 7200:  # 3600s*2 = 2 hours
            s = 600
        elif d_range < 172800:  # 3600s24*2 = 2 days
            s = 3600
        else:
            s = 86400  # 1 day
        # calculate a step size that respects the base step (s) and also
        # enforces the maxMajSteps
        stepSize = s * int(numpy.ceil(float(d_range // s) / maxMajSteps))
        return qwt.QwtLinearScaleEngine.divideScale(self, x1, x2, maxMajSteps, maxMinSteps, stepSize)

    @staticmethod
    def getDefaultAxisLabelsAlignment(axis, rotation):
        '''return a "smart" alignment for the axis labels depending on the axis
        and the label rotation

        :param axis: (qwt.QwtPlot.Axis) the axis
        :param rotation: (float) The rotation (in degrees, clockwise-positive)

        :return: (Qt.Alignment) an alignment
        '''
        return _getDefaultAxisLabelsAlignment(axis, rotation)

    @staticmethod
    def enableInAxis(plot, axis, scaleDraw=None, rotation=None):
        '''convenience method that will enable this engine in the given
        axis. Note that it changes the ScaleDraw as well.

        :param plot: (qwt.QwtPlot) the plot to change
        :param axis: (qwt.QwtPlot.Axis) the id of the axis
        :param scaleDraw: (qwt.QwtScaleDraw) Scale draw to use. If None given,
                          the current ScaleDraw for the plot will be used if
                          possible, and a :class:`TaurusTimeScaleDraw` will be set if not
        :param rotation: (float or None) The rotation of the labels (in degrees, clockwise-positive)
        '''
        if scaleDraw is None:
            scaleDraw = plot.axisScaleDraw(axis)
            if not isinstance(scaleDraw, DeltaTimeScaleDraw):
                scaleDraw = DeltaTimeScaleDraw()
        plot.setAxisScaleDraw(axis, scaleDraw)
        plot.setAxisScaleEngine(axis, DeltaTimeScaleEngine(scaleDraw))
        if rotation is not None:
            alignment = DeltaTimeScaleEngine.getDefaultAxisLabelsAlignment(
                axis, rotation)
            plot.setAxisLabelRotation(axis, rotation)
            plot.setAxisLabelAlignment(axis, alignment)

    @staticmethod
    def disableInAxis(plot, axis, scaleDraw=None, scaleEngine=None):
        '''convenience method that will disable this engine in the given
        axis. Note that it changes the ScaleDraw as well.

        :param plot: (qwt.QwtPlot) the plot to change
        :param axis: (qwt.QwtPlot.Axis) the id of the axis
        :param scaleDraw: (qwt.QwtScaleDraw) Scale draw to use. If None given,
                          a :class:`FancyScaleDraw` will be set
        :param scaleEngine: (qwt.QwtScaleEngine) Scale draw to use. If None given,
                          a :class:`qwt.QwtLinearScaleEngine` will be set
        '''
        if scaleDraw is None:
            scaleDraw = FancyScaleDraw()
        if scaleEngine is None:
            scaleEngine = qwt.QwtLinearScaleEngine()
        plot.setAxisScaleEngine(axis, scaleEngine)
        plot.setAxisScaleDraw(axis, scaleDraw)


class DeltaTimeScaleDraw(FancyScaleDraw):

    def __init__(self, *args):
        FancyScaleDraw.__init__(self, *args)

    def label(self, val):
        if val >= 0:
            s = "+%s" % str(timedelta(seconds=val))
        else:
            s = "-%s" % str(timedelta(seconds=-val))
        return qwt.QwtText(s)


class FixedLabelsScaleEngine(qwt.QwtLinearScaleEngine):

    def __init__(self, positions):
        '''labels is a sequence of (pos,label) tuples where pos is the point
        at wich to draw the label and label is given as a python string (or QwtText)'''
        qwt.QwtScaleEngine.__init__(self)
        self._positions = positions
        # self.setAttribute(self.Floating,True)

    def divideScale(self, x1, x2, maxMajSteps, maxMinSteps, stepSize=0.0):
        div = qwt.QwtScaleDiv(x1, x2, self._positions, [], [])
        div.setTicks(qwt.QwtScaleDiv.MajorTick, self._positions)
        return div

    @staticmethod
    def enableInAxis(plot, axis, scaleDraw=None):
        '''convenience method that will enable this engine in the given
        axis. Note that it changes the ScaleDraw as well.

        :param plot: (qwt.QwtPlot) the plot to change
        :param axis: (qwt.QwtPlot.Axis) the id of the axis
        :param scaleDraw: (qwt.QwtScaleDraw) Scale draw to use. If None given,
                          the current ScaleDraw for the plot will be used if
                          possible, and a :class:`FixedLabelsScaleDraw` will be set if not
        '''
        if scaleDraw is None:
            scaleDraw = plot.axisScaleDraw(axis)
            if not isinstance(scaleDraw, FixedLabelsScaleDraw):
                scaleDraw = FixedLabelsScaleDraw()
        plot.setAxisScaleDraw(axis, scaleDraw)
        plot.setAxisScaleEngine(axis, FixedLabelsScaleEngine(scaleDraw))

    @staticmethod
    def disableInAxis(plot, axis, scaleDraw=None, scaleEngine=None):
        '''convenience method that will disable this engine in the given
        axis. Note that it changes the ScaleDraw as well.

        :param plot: (qwt.QwtPlot) the plot to change
        :param axis: (qwt.QwtPlot.Axis) the id of the axis
        :param scaleDraw: (qwt.QwtScaleDraw) Scale draw to use. If None given,
                          a :class:`FancyScaleDraw` will be set
        :param scaleEngine: (qwt.QwtScaleEngine) Scale draw to use. If None given,
                          a :class:`qwt.QwtLinearScaleEngine` will be set
        '''
        if scaleDraw is None:
            scaleDraw = FancyScaleDraw()
        if scaleEngine is None:
            scaleEngine = qwt.QwtLinearScaleEngine()
        plot.setAxisScaleEngine(axis, scaleEngine)
        plot.setAxisScaleDraw(axis, scaleDraw)


class FixedLabelsScaleDraw(FancyScaleDraw):

    def __init__(self, positions, labels):
        '''This is a custom ScaleDraw that shows labels at given positions (and nowhere else)
        positions is a sequence of points for which labels are defined.
        labels is a sequence strings (or QwtText)
        Note that the lengths of positions and labels must match'''

        if len(positions) != len(labels):
            raise ValueError('lengths of positions and labels do not match')

        FancyScaleDraw.__init__(self)
        self._positions = positions
        self._labels = labels
        # self._positionsarray = numpy.array(self._positions) #this is stored
        # just in case

    def label(self, val):
        try:
            index = self._positions.index(val)  # try to find an exact match
        except:
            index = None  # It won't show any label
            # use the index of the closest position
            #index = (numpy.abs(self._positionsarray - val)).argmin()
        if index is not None:
            return qwt.QwtText(self._labels[index])
        else:
            qwt.QwtText()
