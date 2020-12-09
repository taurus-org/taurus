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
taurusplot.py: Generic graphical plotting widget for Taurus
"""

from __future__ import print_function
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
from builtins import next
from builtins import str
from builtins import range
from builtins import object

import os
import copy
from datetime import datetime
import time
import numpy
from future.utils import string_types
from functools import partial
from taurus.external.qt import Qt, Qwt5, compat

import taurus
import taurus.core
from taurus.core.taurusmanager import getSchemeFromName
from taurus.core.taurusbasetypes import DataFormat
# TODO: Tango-centric
from taurus.core.util.containers import LoopList, CaselessDict, CaselessList
from taurus.core.util.safeeval import SafeEvaluator
from taurus.qt.qtcore.util import baseSignal
from taurus.qt.qtcore.mimetypes import TAURUS_MODEL_LIST_MIME_TYPE, TAURUS_ATTR_MIME_TYPE
from taurus.qt.qtgui.base import TaurusBaseComponent, TaurusBaseWidget
from taurus.qt.qtgui.qwt5 import TaurusPlotConfigDialog, FancyScaleDraw,\
    DateTimeScaleEngine, FixedLabelsScaleEngine, FixedLabelsScaleDraw
from .curvesAppearanceChooserDlg import CurveAppearanceProperties


__all__ = ["TaurusCurve", "TaurusCurveMarker",
           "TaurusXValues", "TaurusPlot", "isodatestr2float"]


def isodatestr2float(s, sep='_'):
    """
    converts a date string in iso format to a timestamp (seconds since epoch)
    with microseconds precision if available
    """
    try:
        # with microseconds
        d = datetime.strptime(s, '%Y-%m-%d' + sep + '%H:%M:%S.%f')
    except:
        # without microseconds
        d = datetime.strptime(s, '%Y-%m-%d' + sep + '%H:%M:%S')
    return time.mktime(d.timetuple()) + d.microsecond * 1e-6


#import threading
class DummyLock(object):

    def acquire(self):
        pass

    def release(self):
        pass

# for debugging. Comment out in production
#from taurus.core.util.log import TraceIt, DebugIt, InfoIt, WarnIt


DFT_CURVE_PENS = [Qt.QPen(Qt.Qt.red),
                  Qt.QPen(Qt.Qt.blue),
                  Qt.QPen(Qt.Qt.green),
                  Qt.QPen(Qt.Qt.magenta),
                  Qt.QPen(Qt.Qt.cyan),
                  Qt.QPen(Qt.Qt.yellow),
                  Qt.QPen(Qt.Qt.black)]

for __p in DFT_CURVE_PENS:
    __p.setWidth(1)  # TODO: we would like this to be 2, but bug #171 forces 1


class TaurusZoomer(Qwt5.QwtPlotZoomer):
    '''A QwtPlotZoomer that displays the label assuming that X values are timestamps'''

    def __init__(self, *args):
        Qwt5.QwtPlotZoomer.__init__(self, *args)
        self._xIsTime = False

    def setXIsTime(self, xistime):
        '''If xistime is True, the x values will be interpreted as timestamps

        :param xistime: (bool)
        '''
        self._xIsTime = xistime

    def trackerText(self, pos):
        '''reimplemented from :meth:`Qwt5.QwtPicker.trackerText`'''
        pos = self.invTransform(pos)
        if self._xIsTime:
            x = datetime.fromtimestamp(pos.x()).isoformat(' ')
        else:
            x = '%g' % pos.x()
        y = '%g' % pos.y()
        return Qwt5.QwtText(', '.join((x, y)))


class TaurusCurveMarker(Qwt5.QwtPlotMarker, TaurusBaseComponent):
    '''Taurus-enabled custom version of QwtPlotMarker
    '''

    def __init__(self, name, parent=None, labelOpacity=0.7):
        self.call__init__wo_kw(Qwt5.QwtPlotMarker)
        self.call__init__(TaurusBaseComponent, self.__class__.__name__)
        self.labelOpacity = labelOpacity
        self.setLineStyle(Qwt5.QwtPlotMarker.NoLine)
        self.setLabelAlignment(Qt.Qt.AlignRight | Qt.Qt.AlignBottom)
        text = Qwt5.QwtText('')
        text.setColor(Qt.Qt.black)
        # a semi-transparent green background for the label
        text.setBackgroundBrush(
            Qt.QBrush(Qt.QColor(0, 255, 0, int(255 * labelOpacity))))
        self.setLabel(text)
        self.setSymbol(Qwt5.QwtSymbol(Qwt5.QwtSymbol.Diamond,
                                      Qt.QBrush(Qt.Qt.yellow),
                                      Qt.QPen(Qt.Qt.green),
                                      Qt.QSize(7, 7)))

    def alignLabel(self):
        '''Sets the label alignment in a "smart" way (depending on the current
        marker's position in the canvas).
        '''
        xmap = self.plot().canvasMap(self.xAxis())
        ymap = self.plot().canvasMap(self.yAxis())
        xmiddlepoint = xmap.p1() + xmap.pDist() / 2  # p1,p2 are left,right here
        # p1,p2 are bottom,top here (and pixel coords start from top!)
        ymiddlepoint = ymap.p2() + ymap.pDist() / 2
        xPaintPos = xmap.transform(self.xValue())
        yPaintPos = ymap.transform(self.yValue())

        if xPaintPos > xmiddlepoint:  # the point in the right side
            hAlign = Qt.Qt.AlignLeft
        else:
            hAlign = Qt.Qt.AlignRight

        if yPaintPos > ymiddlepoint:  # the point is in the bottom side
            vAlign = Qt.Qt.AlignTop
        else:
            vAlign = Qt.Qt.AlignBottom

        self.setLabelAlignment(hAlign | vAlign)


class TaurusXValues(TaurusBaseComponent):
    '''
    Class for managing abscissas values in a TaurusCurve
    '''

    def __init__(self, name, parent=None):
        self._xValues = None
        self.call__init__(TaurusBaseComponent, self.__class__.__name__)
        self._listeners = []
        self.setModel(name)

    def getModelClass(self):
        '''see :meth:`TaurusBaseComponent.getModelClass`'''
        return taurus.core.taurusattribute.TaurusAttribute

    def eventHandle(self, src, evt_type, val):
        '''see :meth:`TaurusBaseComponent.eventHandle`'''
        model = src if src is not None else self.getModelObj()
        if model is None:
            self._xValues = numpy.zeros(0)
            for l in self._listeners:
                l.fireEvent(model, evt_type, val)
            return

        format = getattr(val, 'data_format', model.getDataFormat())
        if format == DataFormat._1D:
            value = val if val is not None else self.getModelValueObj()
            if value:
                self._xValues = numpy.array(value.value)
            else:
                self._xValues = numpy.zeros(0)
        for l in self._listeners:
            # all listeners are notified via fireEvent when the X changes
            l.fireEvent(src, evt_type, val)

    def registerDataChanged(self, listener):
        '''see :meth:`TaurusBaseComponent.registerDataChanged`'''
        self._listeners.append(listener)

    def unregisterDataChanged(self, listener):
        '''see :meth:`TaurusBaseComponent.unregisterDataChanged`'''
        self._listeners.remove(listener)

    def isReadOnly(self):
        '''see :meth:`TaurusBaseComponent.isReadOnly`'''
        return True

    def getValues(self):
        ''' returns the X values.

        :return: (numpy.array)
        '''
        model = self.getModelObj()
        if model is None:
            self._xValues = numpy.zeros(0)
        else:
            value = self.getModelValueObj()
            if value:
                self._xValues = numpy.array(value.value)
            else:
                self._xValues = numpy.zeros(0)
        return self._xValues


class TaurusCurve(Qwt5.QwtPlotCurve, TaurusBaseComponent):
    '''
    Taurus-enabled custom version of QwtPlotCurve.

    TaurusCurves are attached to :class:`TaurusPlot` objects for displaying
    1D data sets.

    A TaurusCurve is more complex than simple QwtPlotCurve in that:

        - It is taurus-aware (i.e., it is associated to a taurus model (an attribute)
          and listens to Taurus events to update its data
        - They may have an associated :class:`TaurusXValues` object that controls
          the values for its abscissas.
        - It uses a :class:`CurveAppearanceProperties` object to manage how it looks

    **Important**:

    The TaurusPlot is in charge of attaching and detaching its TaurusCurves, and keeps
    information about which TaurusCurves are attached. Therefore the programmer
    should never attach/detach a TaurusCurve manually.
    '''
    consecutiveDroppedEventsWarning = 3  # number consecutive of dropped events before issuing a warning (-1 for disabling)
    # absolute number of dropped events before issuing a warning (-1 for
    # disabling)
    droppedEventsWarning = -1

    dataChanged = baseSignal('dataChanged', 'QString')

    def __init__(self, name, xname=None, parent=None, rawData=None, optimized=False):

        Qwt5.QwtPlotCurve.__init__(self)
        TaurusBaseComponent.__init__(self, 'TaurusCurve')
        self._rawData = rawData
        self._xValues = None
        self._yValues = None
        self._showMaxPeak = False
        self._showMinPeak = False
        #self._markerFormatter = self.defaultMarkerFormatter
        self._filteredWhenLog = True
        self._history = []
        self._titleText = '<label>'
        self.setXValuesBuilder()
        self._maxPeakMarker = TaurusCurveMarker(name, self)
        self._minPeakMarker = TaurusCurveMarker(name, self)
        self.__curveName = name
        self.isRawData = not(rawData is None)
        self.droppedEventsCount = 0
        self.consecutiveDroppedEventsCount = 0
        if optimized:
            self.setPaintAttribute(self.PaintFiltered, True)
            self.setPaintAttribute(self.ClipPolygons, True)

        if xname is not None:
            self.__xFromAttr = TaurusXValues(xname, parent)
            self.__xFromAttr.registerDataChanged(self)
            self.setXValuesBuilder(lambda yVals: self.__xFromAttr.getValues())
        else:
            self.__xFromAttr = None

        if name and not self.isRawData:
            try:
                self.setModel(name)
            except Exception:
                self.error("Problems when adding curve " + str(name))
                self.traceback()


#    @staticmethod
#    def defaultMarkerFormatter(self,curve,label,i,x,y,xIsTime):
#        """
#        Returns the text to be shown in  plot tooltips/markers.
#        :param curve: the name of the curve
#        :param label: the label to be displayed
#        :param i: the index of the point in the curve
#        :param x: x axis position
#        :param y: y axis position
#        :param xIsTime: To adapt format to time if needed
#        :return: (str)
#        """
#        #@todo: Check: is this method ever called??? It seems it is not since it is buggy and we don't see problems
#        if self.getXIsTime():
#            infotxt = "'%s'[%i]:\n\t (t=%s, y=%.3g)"%(pickedCurveName,pickedIndex,datetime.fromtimestamp(picked.x()).ctime(),picked.y())
#        else:
#            infotxt = "'%s'[%i]:\n\t (x=%.3g, y=%.3g)"%(pickedCurveName,pickedIndex,picked.x(),picked.y())
#        return infotxt
#
#    def setMarkerFormatter(self,formatter):
#        """
#        Sets formatter method for plot tooltips/markers.
#        The method must have at least 4 arguments:
#        :param curve: the name of the curve
#        :param label: the label to be displayed
#        :param i: the index of the point in the curve
#        :param x: x axis position
#        :param y: y axis position
#        :param xIsTime: To adapt format to time if needed
#        """
#        self._markerFormatter = formatter
#
#    def markerFormatter(self):
#        """
#        Returns the method used to format plot tooltips
#
#        :return: (function)
#        """
#        return self._formatter

    def getCurveName(self):
        '''Returns the name of the curve (in the case of non RawDataCurves, it
        is the same as the model name)

        :return: (str)
        '''
        return self.__curveName

    def setTitleText(self, titletext):
        '''
        Sets the title text for this curve.

        :param titletext:   (str) A string which can contain predefined
                            placeholders (which make sense in the case of non-rawdata curves)

        See Also : compileTitleText
        '''
        self._titleText = titletext
        self.updateTitle()

    def titleText(self, compiled=False):
        '''Returns the titleText string. If compiled == True, the returned string
        will be processed through compileTitleText

        :param compiled: (bool) Whether to process the return value or not
                         (default is compiled=False)

        :return: (basestring) the title

        .. seealso:: :meth:`compileTitleText`
        '''
        if compiled:
            return self.compileTitleText(self._titleText)
        else:
            return self._titleText

    def updateTitle(self):
        '''Updates the title of the curve, according to the titleText property'''
        titleText = self.compileTitleText(self._titleText)
        title = self.title()
        title.setText(titleText)
        self.setTitle(title)
        self.itemChanged()

    def compileTitleText(self, titletext):
        """Substitutes the known placeholders by the current equivalent values
        for a titleText.

        *Note*: Some placeholders may not make sense for certain curves (e.g.
        <label> for a RawData curve). In these cases, they are left unprocessed
        (without warning).

        :param titletext:   (str)
                            A string which can contain any of the following
                            predefined placeholders:

                            - <label> the attribute label (default)
                            - <model> the model name
                            - <attr_name> attribute name
                            - <attr_fullname> full attribute name (for backwards
                              compatibility, <attr_full_name> is also accepted)
                            - <dev_alias> device alias
                            - <dev_name> device name
                            - <dev_fullname> full device name (for backwards
                              compatibility, <dev_full_name> is also accepted)
                            - <current_title> The current title

        :return: (str) a title string where the placeholders have been
                 substituted by their corresponding values
        """
        # All TaurusCurves can deal with at least these placeholders
        titletext = titletext.replace('<current_title>',
                                      str(self.title().text()))
        titletext = titletext.replace('<model>', self.getModel())
        attr = self.getModelObj()
        if attr is None:
            return titletext
        # TaurusCurves for which we can get the Attribute...
        titletext = titletext.replace('<label>', attr.label or '---')
        titletext = titletext.replace('<attr_name>', attr.name or '---')
        titletext = titletext.replace('<attr_fullname>',
                                      attr.getFullName() or '---')
        titletext = titletext.replace('<attr_full_name>',
                                      attr.getFullName() or '---')

        dev = attr.getParentObj()
        if dev is not None:
            # TaurusCurves for which we can get the Device object...
            titletext = titletext.replace('<dev_alias>',
                                          dev.getSimpleName() or '---')
            titletext = titletext.replace('<dev_name>',
                                          dev.getNormalName() or '---')
            titletext = titletext.replace('<dev_fullname>',
                                          dev.getFullName() or '---')
            titletext = titletext.replace('<dev_full_name>',
                                          dev.getFullName() or '---')
        return titletext

    # -~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~
    # Convenience attach/detach methods
    # -~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~

    def attachMarkers(self, plot):
        '''attach markers to the plot

        :param plot: the plot (typically, the TaurusPlot instance)
        '''
        self._maxPeakMarker.attach(plot)
        self._minPeakMarker.attach(plot)

    def attachMaxMarker(self, plot):
        '''attach marker of max value to the plot

        :param plot: the plot (typically, the TaurusPlot instance)
        '''
        self._maxPeakMarker.attach(plot)

    def attachMinMarker(self, plot):
        '''attach markers of min value to the plot

        :param plot: the plot (typically, the TaurusPlot instance)
        '''
        self._minPeakMarker.attach(plot)

    def detach(self):
        '''reimplemented from :class:`QwtPlotCurve`. In addition to dettaching
        the curve, it dettaches the associated min/max markers. '''
        self.detachMarkers()
        self.resetModel()
        Qwt5.QwtPlotCurve.detach(self)

    def detachMarkers(self):
        '''detaches the min/max markers of this curve'''
        self._maxPeakMarker.detach()
        self._minPeakMarker.detach()

    def detachMaxMarker(self):
        '''detaches the max marker of this curve'''
        self._maxPeakMarker.detach()

    def detachMinMarker(self):
        '''detaches the min marker of this curve'''
        self._minPeakMarker.detach()

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # Overwrite from TaurusBaseComponent
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    def getModelClass(self):
        '''See :meth:`TaurusBaseComponent.getModelClass`'''
        return taurus.core.taurusattribute.TaurusAttribute

    def getRawData(self):
        '''Returns the rawData

        :return: (dict or None) a RawData dict or None if the curve is not
                 RawData

        .. seealso:: :meth:`TaurusPlot.attachRawData`
        '''
        return self._rawData

    def setXValuesBuilder(self, fn=None):
        """
        Sets the callback to be used for creating the 'X' array values for a
        curve. If None given, the default is that the abscissas are int indexes
        (from 0 to len(Y)).

        :param fn: (callable) a callable that gets the Y values as a parameter and returns X values

        E.g., the default::

            curve.setXValuesBuilder()

        is equivalent to::

            curve.setXValuesBuilder(lambda yVals: numpy.arange(len(yVals)))
        """
        if fn is None:
            fn = lambda yVals: numpy.arange(len(yVals))
        self._xValuesBuilder = fn

    def getXValues(self):
        '''Returns X values using the XValuesBuilder.

        :return: (sequence)

        .. seealso:: :meth:`setXValuesBuilder`
        '''
        xBuilder = self._xValuesBuilder
        if not hasattr(self, "_yValues"):
            return xBuilder([])
        if self._yValues is None:
            return xBuilder([])
        assert(isinstance(self._yValues, numpy.ndarray))
        # ob=numpy.array(None) has len(ob.shape) = 0, but the worst part
        # is that len(ob) throws exception!
        if len(self._yValues.shape) == 0:
            return xBuilder([])
        return xBuilder(self._yValues)

    def handleEvent(self, src, evt_type, val):
        '''Handles Taurus Events for this curve

        See: :meth:`TaurusBaseComponent.handleEvent`
        '''
        if self.isRawData:
            #self.warning('fireEvent of a RawData curve has been called by %s'%repr(self.sender()))
            raise Exception('called handleEvent of a RawData curve')
            return
        model = src if src is not None else self.getModelObj()
        if model is None:
            self._xValues = numpy.zeros(0)
            self._yValues = numpy.zeros(0)
            self.dataChanged.emit(str(self.getModel()))
            return

        if evt_type == taurus.core.taurusbasetypes.TaurusEventType.Config:
            self.updateTitle()

        value = val if isinstance(
            val, taurus.core.taurusbasetypes.TaurusAttrValue) else self.getModelValueObj()
        if not isinstance(value, taurus.core.taurusbasetypes.TaurusAttrValue):
            self._onDroppedEvent(reason="Could not get attribute value")
            return
        try:
            self.setXYFromModel(value)
        except Exception as e:
            self._onDroppedEvent(reason=str(e))
            return
        self._updateMarkers()
        self.dataChanged.emit(str(self.getModel()))

    def _onDroppedEvent(self, reason='Unknown'):
        '''inform the user about a dropped event

        :param reason: (str) The reason of the drop
        '''
        self.debug("Droping event. Reason %s", reason)
        self.droppedEventsCount += 1
        self.consecutiveDroppedEventsCount += 1
        mustwarn = False
        if self.droppedEventsCount == self.droppedEventsWarning:
            mustwarn = True
            msg = ('At least %i events from model "%s" have being dropped. This attribute may have problems\n' +
                   'Future occurrences will be silently ignored') % (self.droppedEventsWarning, self.modelName)
            # disable the consecutive Dropped events warning (we do not want it
            # if we got this one)
            self.consecutiveDroppedEventsWarning = -1
        if self.consecutiveDroppedEventsCount == self.consecutiveDroppedEventsWarning:
            mustwarn = True
            msg = ('At least %i consecutive events from model "%s" have being dropped. This attribute may have problems\n' +
                   'Future occurrences will be silently ignored') % (self.consecutiveDroppedEventsWarning, self.modelName)
            # disable the consecutive Dropped events warning
            self.consecutiveDroppedEventsWarning = -1
        if mustwarn:
            self.warning(msg)
            p = self.plot()
            if p:
                c = p.canvas()
                msg2 = "Errors reading %s (%s)" % (
                    self.titleText(compiled=True), self.modelName)
                Qt.QToolTip.showText(c.mapToGlobal(c.pos()), msg2, c)
                #Qt.QMessageBox.warning(p, "Errors in curve %s"%self.titleText(compiled=True), msg, Qt.QMessageBox.Ok)

        if self.droppedEventsCount == self.droppedEventsWarning:
            mustwarn = True
            msg = ('At least %i events from model "%s" have being dropped. This attribute may have problems\n' +
                   'Future occurrences will be silently ignored') % (self.droppedEventsWarning, self.modelName)
            self.warning(msg)
            p = self.plot()
            if p:
                c = p.canvas()
                msg = ''
                Qt.QToolTip.showText(c.pos(), msg, c)
                #Qt.QMessageBox.warning(p, "Errors in curve %s"%self.titleText(compiled=True), msg, Qt.QMessageBox.Ok)

    def _updateMarkers(self):
        '''updates min & max markers if needed'''
        if self.isVisible():
            if self._showMaxPeak:
                try:
                    maxpoint = [self._xValues[
                        self._yValues.argmax()], self._yValues.max()]
                except:
                    maxpoint = [0, 0]
                self._maxPeakMarker.setValue(*maxpoint)
                label = self._maxPeakMarker.label()
                if self.plot().getXIsTime():
                    label.setText("Max. " + str(self.title().text()) + " " + repr(
                        maxpoint[1]) + ' at t = ' + datetime.fromtimestamp(maxpoint[0]).ctime())
                else:
                    label.setText("Max. " + str(self.title().text()) + " " +
                                  repr(maxpoint[1]) + ' at x = ' + repr(maxpoint[0]))

                self._maxPeakMarker.setLabel(label)
            if self._showMinPeak:
                try:
                    minpoint = [self._xValues[
                        self._yValues.argmin()], self._yValues.min()]
                except:
                    minpoint = [0, 0]
                self._minPeakMarker.setValue(*minpoint)
                label = self._minPeakMarker.label()
                if self.plot().getXIsTime():
                    label.setText("Min. " + str(self.title().text()) + " " + repr(
                        minpoint[1]) + ' at t = ' + datetime.fromtimestamp(minpoint[0]).ctime())
                else:
                    label.setText("Min. " + str(self.title().text()) + " " +
                                  repr(minpoint[1]) + ' at x = ' + repr(minpoint[0]))
                self._minPeakMarker.setLabel(label)

    def setXYFromModel(self, value):
        """ sets the X (self._xValues) and Y (self._yValues) values from the
        given model. This method can be reimplemented by subclasses of Taurusplot
        that behave differently (e.g. TaurusTrend)

        :param value: (TaurusAttrValue) the value object from the model
        """
        attr = self.getModelObj()
        if attr.data_format == DataFormat._1D:
            # TODO: Adapt all values to be plotted to the same Unit
            if value:
                if attr.isNumeric():
                    self._yValues = numpy.array(value.rvalue.magnitude)
                else:
                    self._yValues = numpy.array(value.rvalue)
            else:
                self._yValues = numpy.zeros(0)
            self._xValues = self.getXValues()
        else:
            raise ValueError('TaurusCurve only supports SPECTRUM attributes '
                             '(a %s was passed). \n'
                             'Note: if you want a trend plot, use '
                             'TaurusTrendCurve instead of '
                             'TaurusCurve.' % str(DataFormat[attr.data_format]))

    def setPaused(self, paused=True):
        '''Pauses itself and other listeners depending on it

        .. seealso:: :meth:`TaurusBaseComponent.setPaused`
        '''
        TaurusBaseComponent.setPaused(self, paused)
        for ob in (self.__xFromAttr, self._maxPeakMarker, self._minPeakMarker):
            try:
                ob.setPaused(paused)
            except AttributeError:
                pass

    def setAppearanceProperties(self, prop):
        """Applies the given CurveAppearanceProperties object (prop) to the curve.
        If a given property is set to None, it is not applied

        :param prop: (CurveAppearanceProperties)
        """
        prop = copy.deepcopy(prop)
        s = Qwt5.QwtSymbol(self.symbol())
        if prop.sStyle is not None:
            s.setStyle(Qwt5.QwtSymbol.Style(prop.sStyle))
        if prop.sSize is not None:
            s.setSize(prop.sSize)
        if prop.sColor is not None:
            b = s.brush()
            p = s.pen()
            color = Qt.QColor(prop.sColor)
            p.setColor(color)
            b.setColor(color)
            b.setStyle(Qt.Qt.NoBrush)
            s.setBrush(b)
            s.setPen(p)
        if prop.sFill is not None:
            b = s.brush()
            if prop.sFill:
                b.setStyle(Qt.Qt.SolidPattern)
                s.setBrush(b)
            else:
                s.brush().setStyle(Qt.Qt.NoBrush)
                s.setBrush(b)
        p = Qt.QPen(self.pen())
        if prop.lStyle is not None:
            p.setStyle(prop.lStyle)
        if prop.lWidth is not None:
            p.setWidth(prop.lWidth)
        if prop.lColor is not None:
            p.setColor(Qt.QColor(prop.lColor))
        if prop.cStyle is not None:
            self.setStyle(prop.cStyle)
        if prop.cFill is not None:
            b = Qt.QBrush(self.brush())
            if prop.cFill:  # The area under the curve is filled with the same color as the curve but with 50% transparency
                color = p.color()
                color.setAlphaF(0.5)
                b.setColor(color)
                b.setStyle(Qt.Qt.SolidPattern)
            else:
                b.setStyle(Qt.Qt.NoBrush)
            self.setBrush(b)
        if prop.yAxis is not None:
            self.setYAxis(prop.yAxis)
        if getattr(prop, "visible", None) is not None:
            self.setVisible(prop.visible)
        if prop.title is not None:
            self.setTitleText(prop.title)
        self.setSymbol(s)
        self.setPen(p)

    def getAppearanceProperties(self):
        """Returns the appearance properties of the curve (color, symbol, width,...).

        :return: (CurveAppearanceProperties)
        """
        prop = CurveAppearanceProperties()
        s = self.symbol()
        prop.sStyle = s.style()
        prop.sSize = s.size().width()  # We are only supporting symbols with width==heigh
        prop.sColor = s.brush().color()
        prop.sFill = (s.brush().style() != Qt.Qt.NoBrush)
        p = self.pen()
        prop.lStyle = p.style()
        prop.lWidth = p.width()
        prop.lColor = p.color()
        prop.cStyle = self.style()
        prop.cFill = (self.brush().style() != Qt.Qt.NoBrush)
        prop.yAxis = self.yAxis()
        prop.visible = self.isVisible()
        # We are forced to save only the text (and not the QwtText) because
        # Pickle chokes with the QwtText
        prop.title = self.title().text()
        return copy.deepcopy(prop)

    def setYAxis(self, axis):
        """changes the Y axis to which the curve is associated

        :param axis: (Qwt5.QwtPlot.Axis) the axis to which it should associate
        """
        Qwt5.QwtPlotCurve.setYAxis(self, axis)
        # this way we make sure that the filtering is correct (in case of
        # change of scale type)
        self.safeSetData()

    def setFilteredWhenLog(self, filtered=True):
        '''Set whether non-possitive values should be discarded or not when
        plotting in log mode.

        :param filtered: (bool) if True, filtering is done
        '''
        self._filteredWhenLog = filtered

    def isFilteredWhenLog(self):
        '''returns True if non-possitive values are being discarded when plotting in log mode.

        return: (bool)

        .. seealso:: :meth:`setFilteredWhenLog`
        '''
        return self._filteredWhenLog

    def setData(self, x, y):
        '''Sets the X and Y data for the curve (possibly filtering non-possitive
        values if in log mode). Reimplemented from Qwt5.QwtPlotCurve.setData.

        :param x: (sequence) X values
        :param y: (sequence) Y values

        .. seealso:: :meth:`safeSetData`, :meth:`setFilteredWhenLog`
        '''
        if self.isFilteredWhenLog():
            # filter out the nonpossitive elements if the scale is logarithmic
            if self.plot():
                type_ = self.plot().getAxisTransformationType(self.xAxis())
                if type_ == Qwt5.QwtScaleTransformation.Log10:
                    x, y = numpy.array(x), numpy.array(y)
                    valid = x > 0  # this is an array of bools representing valid entries
                    x, y = x[valid], y[valid]
                type_ = self.plot().getAxisTransformationType(self.yAxis())
                if type_ == Qwt5.QwtScaleTransformation.Log10:
                    x, y = numpy.array(x), numpy.array(y)
                    valid = y > 0  # this is an array of bools representing valid entries
                    x, y = x[valid], y[valid]
            else:
                self.debug("Curve is not connected but still receiving data")

        if len(x) != len(y):
            self.warning(
                "setData(x[%d],y[%d]): array sizes don't match!" % (len(x), len(y)))

        # now proceed as usual
        Qwt5.QwtPlotCurve.setData(self, x, y)

    def safeSetData(self):
        '''Calls setData with x= self._xValues and y=self._yValues

        .. seealso:: :meth:`setData`
        '''
        if self._xValues is None:
            self.setData(numpy.zeros(0), numpy.zeros(0))
        elif self._yValues is None or len(self._yValues.shape) == 0:
            self.setData(self._xValues, numpy.zeros(0))
        else:
            self.setData(self._xValues, self._yValues)

    def getParentTaurusComponent(self):
        '''Searches the closest ancestor (in the Qt parenting hyerarchy) that is
        which inherits from TaurusBaseComponent. It returns None if None found.

        :return: (widget or None)
        '''
        p = self.plot()
        while p and not isinstance(p, TaurusBaseComponent):
            if isinstance(p, (Qt.QDialog, Qt.QMainWindow)):
                p = None
                break
            p = p.parentWidget()
        return p

    def registerDataChanged(self, listener, meth):
        ''' registers a listener to the DataChangedSignal of this curve

        :param listener: (QWidget) listener object
        :param meth: (callable) callback method
        '''
        self.dataChanged.connect(meth)

    def unregisterDataChanged(self, listener, meth):
        '''unregisters the given listener and method from the DataChangedSignal
        of this curve

        :param listener: (QWidget) listener object
        :param meth: (callable) callback method
        '''
        self.dataChanged.disconnect(meth)

    def isReadOnly(self):
        '''see :meth:`TaurusBaseComponent.isReadOnly`'''
        return True

    def getStats(self, limits=None, inclusive=(True, True), imin=None, imax=None, ignorenans=True):
        '''
        returns a dict containing several descriptive statistics of a region of
        the curve defined by the limits given by the keyword arguments. It also
        contains a copy of the data in the considered region. The keys of the
        returned dictionary correspond to:

                 -'x' : the abscissas for the considered points (numpy.array)
                 -'y' : the ordinates for the considered points (numpy.array)
                 -'points': number of considered points (int)
                 -'min' : (x,y) pair of the minimum of the curve (float,float)
                 -'max' : (x,y) pair of the maximum of the curve (float,float)
                 -'mean' : arithmetic average of y (float)
                 -'std' : (biased)standard deviation of y (float)
                 -'rms' : root mean square of y (float)

        Note that some of the values may be None if that cannot be computed.

        Also,

        :param limits: (None or tuple<float,float>) tuple containing (min,max) limits.
                        Points of the curve whose abscisa value is outside of
                        these limits are ignored. If None is passed, the limit is not enforced
        :param inclusive: (tuple<bool,bool>). A tuple consisting of the (lower flag, upper flag).
                          These flags determine whether values exactly equal to the lower or
                          upper limits are included. The default value is (True, True).
        :param imin: (int) lowest index to be considered. If None is given,
                     the limit is not enforced
        :param imax: (int) higest index to be considered. If None is given,
                     the limit is not enforced
        :param ignorenans: (bool) if True (defaul), the points with NaN values are stripped
                     before calculating the stats

        :return: (dict) A dict containing the stats.
        '''

        data = self.data()
        if imin is None:
            imin = 0
        if imax is None:
            imax = data.size()

        x = numpy.array([data.x(i) for i in range(imin, imax)])
        y = numpy.array([data.y(i) for i in range(imin, imax)])

        if limits is not None:
            xmin, xmax = limits
            if xmax is None:
                xmax = numpy.inf
            if inclusive:
                mask = (x >= xmin) * (x <= xmax)
            else:
                mask = (x > xmin) * (x < xmax)
            x = x[mask]
            y = y[mask]

        if ignorenans:
            # we remove points where either x or y are Nan
            mask = numpy.invert(numpy.isnan(x + y))
            x = x[mask]
            y = y[mask]

        ret = {'x': x,
               'y': y,
               'points': x.size,
               'min': None,
               'max': None,
               'mean': None,
               'std': None,
               'rms': None}

        if x.size > 0:
            argmin = y.argmin()
            argmax = y.argmax()
            ret.update({'min': (x[argmin], y[argmin]),
                        'max': (x[argmax], y[argmax]),
                        'mean': y.mean(),
                        'std': y.std(),
                        'rms': numpy.sqrt(numpy.mean(y ** 2))})
        return ret

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # Methods necessary to show/hide peak values
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    def showMaxPeak(self, show):
        """Specififes if we want to show or not the max peak of the curve

        :param show: (bool)
        """
        self._showMaxPeak = show
        # self.fireEvent(taurus.core.taurusbasetypes.TaurusEventType.Change)
        # #force re-reading attribute to update peak values

    def showMinPeak(self, show):
        """Specififes if we want to show or not the min peak of the curve.

        :param show: (bool)
        """
        self._showMinPeak = show
        # self.fireEvent(taurus.core.taurusbasetypes.TaurusEventType.Change)
        # #force re-reading attribute to update peak values

    def getYAxisStatus(self):
        '''returns either None (if the curve is not visible) or its yAxis (if it
        is visible)

        :return: (Qwt5.QwtPlot.Axis or None)
        '''
        if not self.isVisible():
            return None
        return self.yAxis()


# class TaurusPlot(Qwt5.QwtPlot, Logger):
class TaurusPlot(Qwt5.QwtPlot, TaurusBaseWidget):
    '''
    TaurusPlot is a general widget for plotting 1D data sets. It is an extended
    taurus-aware version of :class:`QwtPlot`.

    .. image:: /_static/taurusplot04.png
       :align: center

    TaurusPlot already incorporates by default many features that can be added to a
    regular QwtPlot:

        - Zoomming, panning, and magnifier are enabled by default
        - Autoscaling is enabled and associated to the ESC key
        - Methods are available to add new curves which can either be associated
          to taurus attributes or be "raw data" (i.e., values that are not directly
          aware of control system events)
        - Context menu offers access to many options
        - A plot configuration dialog, and save/restore configuration facilities
        - Date-time scales and linear/log scales support
        - Methods for importing/exporting curves from/to ASCII data
        - Methods for printing and exporting the plot to PDF
        - Methods for creating curves from arbitrary functions
        - Data inspection facilities
        - ...


    For an overview of the features from an user point of view, see the
    :ref:`TaurusPlot User's Interface Guide <taurusplot_ui>`.

    You can also see some code that exemplifies the use of TaurusPlot in :ref:`the
    TaurusPlot coding examples <examples_taurusplot>`

    **Important**: although TaurusPlot subclasses QwtPlot and therefore it is
    possible to use QwtPlot's lower level methods for attaching QwtPlotItems
    (such as QwtPlotCurves) to the plot, it is *highly* recommended to use the
    higher-level methods provided by TaurusPlot to interact with the datasets
    attached to a TaurusPlot (e.g., `addModels()`, `attachRawData()`).
    This is because TaurusPlot keeps records of the items attached via its own
    methods.

    .. seealso:: :class:`TaurusTrend`,
                 :ref:`TaurusPlot User's Interface Guide <taurusplot_ui>`,
                 :ref:`The TaurusPlot coding examples <examples_taurusplot>`
    '''

    #: Override the default modelChanged('QString') signal
    modelChanged = Qt.pyqtSignal()

    dataChanged = Qt.pyqtSignal('QString')
    CurvesYAxisChanged = Qt.pyqtSignal('QStringList', int)

    def __init__(self, parent=None, designMode=False):
        name = "TaurusPlot"
        # book-keeping of attached tauruscurves
        self.curves = CaselessDict()  # TODO: Tango-centric

        Qwt5.QwtPlot.__init__(self, parent)
        TaurusBaseWidget.__init__(self, name)

        self._designMode = designMode
        self._modelNames = []
        self._useParentModel = False
        self._isPaused = False
        self._defaultCurvesTitle = '<label>'
        self._curvePens = LoopList(DFT_CURVE_PENS)
        self._gridPen = Qt.QPen(Qt.Qt.gray, 1)
        # the latest element of this list is considered the current version
        self._supportedConfigVersions = ["tpc-1", "tpc-1.1"]

#        Logger.__init__(self)
#        Qwt5.QwtPlot.__init__(self, parent)

        # dictionary for default axes naming
        self._axesnames = {Qwt5.QwtPlot.xBottom: 'X', Qwt5.QwtPlot.xTop: 'X2',
                           Qwt5.QwtPlot.yLeft: 'Y1', Qwt5.QwtPlot.yRight: 'Y2'}
        # cache for the values of the axis transformation
        self.__transformations = {}

        # Data Import Dialog (it will only be initialised if required)
        self.DataImportDlg = None

        # Values to be managed with/from the TaurusPlotConfigDialog time
        # configuration
        self._xIsTime = False
        self._xMax = None
        self._xMin = None
        self._xDynScale = False
        self._xDynScaleSupported = False

        # enable dropping (see also dragEnterEvent and dropEvent methods)
        self.setAcceptDrops(True)

        #self.curves_lock = threading.RLock()
        self.curves_lock = DummyLock()

        # background
        # self.setCanvasBackground(Qt.Qt.white)

        # attach a grid
        self._grid = Qwt5.QwtPlotGrid()
        self._grid.setPen(self._gridPen)
        self._grid.attach(self)

        # configure axes
        for axis in [Qwt5.QwtPlot.xBottom, Qwt5.QwtPlot.yLeft, Qwt5.QwtPlot.yRight, Qwt5.QwtPlot.xTop]:
            self.setAxisScaleDraw(axis, FancyScaleDraw())
        self.y2AxisPalette = Qt.QPalette(Qt.QColor("blue"), Qt.QColor("black"), Qt.QColor(
            "blue"), Qt.QColor("blue"), Qt.QColor("blue"), Qt.QColor("blue"), Qt.QColor("blue"))
        self.axisScaleDraw(Qwt5.QwtPlot.yRight).setPalette(self.y2AxisPalette)

        # set initial show/hide peaks configuration
        self._showMaxPeaks = False
        self._showMinPeaks = False

        # zoom. One zoomer for Y1 and another for Y2 (but only one will be
        # active at each time)
        self._max_zoom_stack = 15
        self._zoomer1 = TaurusZoomer(self.canvas())
        self._zoomer2 = TaurusZoomer(self.canvas())
        self._zoomer2.setRubberBandPen(Qt.Qt.blue)
        self._zoomer2.setTrackerPen(Qt.Qt.blue)
        self._zoomer2.setAxis(Qwt5.QwtPlot.xBottom, Qwt5.QwtPlot.yRight)
        self._zoomer2.setEnabled(False)
        self._zoomer = self._zoomer1
        self._allowZoomers = True
        for z in (self._zoomer1, self._zoomer2):
            z.setMaxStackDepth(self._max_zoom_stack)
            # this disables the escape key for going to the top of the zoom
            # stack (we use escape via an action for autoscaling)
            z.setKeyPattern(z.KeyHome, Qt.Qt.Key_unknown)

        # point picker
        self._pointPicker = Qwt5.QwtPicker(self.canvas())
        self._pointPicker.setSelectionFlags(Qwt5.QwtPicker.PointSelection)

        self._pickedMarker = TaurusCurveMarker("Picked", labelOpacity=0.8)
        self._pickedCurveName = ""
        self._pointPicker.selected.connect(self.pickDataPoint)

        # xRegion picker
        self._xRegionPicker = Qwt5.QwtPlotPicker(Qwt5.QwtPlot.xBottom,
                                                 Qwt5.QwtPlot.yLeft,
                                                 Qwt5.QwtPicker.PointSelection,
                                                 Qwt5.QwtPicker.VLineRubberBand,
                                                 Qwt5.QwtPicker.AlwaysOn, self.canvas())
        self._xRegionPicker.setEnabled(False)
        self._xRegionPicker.selected.connect(self._onXRegionEvent)

        # magnifier
        self._magnifier = Qwt5.QwtPlotMagnifier(self.canvas())
        self._magnifier.setMouseButton(Qt.Qt.NoButton)

        # panner
        self._panner = Qwt5.QwtPlotPanner(self.canvas())
        self._panner.setMouseButton(Qt.Qt.LeftButton, Qt.Qt.ControlModifier)

        # legend
        self._legendPos = Qwt5.QwtPlot.RightLegend
        self._showLegend = False
        self._legendDecissionIsForever = False
        self.updateLegend()
        self.legendClicked.connect(self.toggleCurveState)

        # datainspector mode
        self._inspectorMode = False
        self.toggleDataInspectorMode(False)

        # optimization
        self._optimizationEnabled = True

        # modifiable by user
        self.setModifiableByUser(True)

        # drag&drop
        self.setSupportedMimeTypes(
            [TAURUS_MODEL_LIST_MIME_TYPE, TAURUS_ATTR_MIME_TYPE])

        # initialize actions
        self.__initActions()

        # final stuff
        self.setObjectName(name)
        # self.defineStyle()

    def __initActions(self):
        '''Create and attach TaurusPlot actions'''

        #======================================================================
        # This action is for debug only. Comment out when not debugging
        #self._debugAction = Qt.QAction("Calculate statistics", None)
        # self._debugAction.setShortcut(Qt.Qt.Key_D)
        #self.connect(self._debugAction, Qt.SIGNAL("triggered()"), self.__debug)
        # self.canvas().addAction(self._debugAction)
        #======================================================================

        self._dataInspectorAction = Qt.QAction("Data &Inspector mode", None)
        self._dataInspectorAction.setShortcut(Qt.Qt.Key_I)
        self._dataInspectorAction.setCheckable(True)
        self._dataInspectorAction.setChecked(self._pointPicker.isEnabled())
        self._dataInspectorAction.toggled[bool].connect(self.toggleDataInspectorMode)

        self._setFormatterAction = Qt.QAction("Set Formatter...", None)
        self._setFormatterAction.triggered.connect(self.onSetFormatter)

        self._curveStatsAction = Qt.QAction("Calculate statistics", None)
        self._curveStatsAction.setShortcut(Qt.Qt.Key_S)
        self._curveStatsAction.triggered.connect(self.onCurveStatsAction)

        self._pauseAction = Qt.QAction("&Pause", None)
        self._pauseAction.setShortcuts([Qt.Qt.Key_P, Qt.Qt.Key_Pause])
        self._pauseAction.setCheckable(True)
        self._pauseAction.setChecked(self.isPaused())
        self._pauseAction.toggled[bool].connect(self.setPaused)

        self._autoscaleAllAxisAction = Qt.QAction("Autoscale all axes", None)
        self._autoscaleAllAxisAction.setShortcut(Qt.Qt.Key_Escape)
        self._autoscaleAllAxisAction.triggered.connect(self.autoScaleAllAxes)

        self._toggleZoomAxisAction = Qt.QAction("Toggle Zoom-aware axis", None)
        self._toggleZoomAxisAction.setShortcut(Qt.Qt.Key_Z)
        self._toggleZoomAxisAction.triggered.connect(
            partial(self.toggleZoomer, axis=None))

        self._configDialogAction = Qt.QAction("Plot configuration...", None)
        self._configDialogAction.setShortcut(Qt.QKeySequence("Alt+C"))
        self._configDialogAction.triggered.connect(self.showConfigDialog)

        self._inputDataAction = Qt.QAction("Input data selection...", None)
        self._inputDataAction.setShortcut(Qt.QKeySequence.New)
        self._inputDataAction.triggered.connect(self.showDataImportDlg)

        self._saveConfigAction = Qt.QAction("Save current settings...", None)
        self._saveConfigAction.setShortcut(Qt.QKeySequence.Save)
        self._saveConfigAction.triggered.connect(
            partial(self.saveConfig, ofile=None, curvenames=None))

        self._loadConfigAction = Qt.QAction(
            "&Retrieve saved settings...", None)
        self._loadConfigAction.setShortcut(Qt.QKeySequence.Open)
        self._loadConfigAction.triggered.connect(
            partial(self.loadConfig, ifile=None))

        self._showLegendAction = Qt.QAction("Show &Legend", None)
        self._showLegendAction.setShortcut(Qt.QKeySequence("Ctrl+L"))
        self._showLegendAction.setCheckable(True)
        self._showLegendAction.setChecked(self._showLegend)
        self._showLegendAction.triggered[bool].connect(self.showLegend)
        self.canvas().addAction(self._showLegendAction)

        self._showMaxAction = Qt.QAction("Show Max", None)
        self._showMaxAction.setCheckable(True)
        self._showMaxAction.setChecked(self._showMaxPeaks)
        self._showMaxAction.toggled.connect(self.showMaxPeaks)

        self._showMinAction = Qt.QAction("Show Min", None)
        self._showMinAction.setCheckable(True)
        self._showMinAction.setChecked(self._showMinPeaks)
        self._showMinAction.toggled[bool].connect(self.showMinPeaks)

        self._printAction = Qt.QAction("&Print plot...", None)
        self._printAction.triggered.connect(self.exportPrint)

        self._exportPdfAction = Qt.QAction("Export plot to PD&F...", None)
        self._exportPdfAction.triggered.connect(
            partial(self.exportPdf, fileName=None))

        self._exportAsciiAction = Qt.QAction("Export data to &ASCII...", None)
        self._exportAsciiAction.triggered.connect(
            partial(self.exportAscii, curves=None))

        self._setCurvesTitleAction = Qt.QAction(
            "Change Curves Titles...", None)
        self._setCurvesTitleAction.triggered.connect(
            partial(self.changeCurvesTitlesDialog, curveNamesList=None))

        self._closeWindowAction = Qt.QAction(
            Qt.QIcon.fromTheme("process-stop"), 'Close Plot', self)
        self._closeWindowAction.triggered.connect(self.close)

        # add all actions and limit the scope of the key shortcuts to the
        # widget (default is Window)
        for action in (self._dataInspectorAction, self._pauseAction,
                       self._autoscaleAllAxisAction,
                       self._toggleZoomAxisAction, self._configDialogAction,
                       self._inputDataAction, self._saveConfigAction,
                       self._loadConfigAction, self._showLegendAction,
                       self._showMaxAction, self._showMinAction,
                       self._printAction, self._exportPdfAction,
                       self._exportAsciiAction, self._setCurvesTitleAction,
                       self._curveStatsAction, self._setFormatterAction):
            # this is needed to avoid ambiguity when more than one TaurusPlot
            # is used in the same window
            action.setShortcutContext(Qt.Qt.WidgetShortcut)
            # because of the line above, we must add the actions to the widget
            # that gets the focus (the canvas instead of self)
            self.canvas().addAction(action)

    def setFormat(self, format):
        """Reimplemented from TaurusBaseComponent"""
        for name in self.curves:
            curve = self.curves.get(name, None)
            w = getattr(curve, 'owner', curve)
            w.setFormat(format)
        TaurusBaseComponent.setFormat(self, format)

    def dropEvent(self, event):
        '''reimplemented to support dropping of modelnames in taurusplots'''
        mtype = self.handleMimeData(event.mimeData(), self.addModels)
        if mtype is None:
            self.info('Invalid model')
        else:
            event.acceptProposedAction()

#    def dropEvent(self, event):
#        '''reimplemented to support dropping of modelnames in taurusplots'''
#        supported = self.getSupportedMimeTypes()
#        formats = event.mimeData().formats()
#        for mtype in supported:
#            if mtype in formats:
#                modelname = str(event.mimeData().data(mtype))
#                if modelname is None:
#                    return
#                try:
#                    self.addModels([modelname])
#                    event.acceptProposedAction()
#                except:
#                    self.info('Dropped data is invalid (%s)'%repr(modelname))
#                return

    def getAxisTransformationType(self, axis):
        """Retrieve the transformation type for a given axis (cached)

        :param axis: (Qwt5.QwtPlot.Axis) the axis

        :return: (Qwt5.QwtScaleTransformation.Type)

        .. note:: this method helps to avoid a memory leak in Qwt (see
                  http://sf.net/p/tauruslib/tickets/171 )
        """
        try:
            return self.__transformations[axis]
        except KeyError:
            t = self.axisScaleEngine(axis).transformation().type()
            self.__transformations[axis] = t
            return t

    def setAxisScaleEngine(self, axis, scaleEngine):
        """ reimplemented from :meth:`Qwt5.QwtPlot.setAxisScaleEngine` to store
         a cache of the transformation type """
        self.__transformations[axis] = scaleEngine.transformation().type()
        return Qwt5.QwtPlot.setAxisScaleEngine(self, axis, scaleEngine)

    def getCurveTitle(self, curvename):
        '''return the current title associated to a given curve name

        :param curvename: (str) the name of the curve

        :return:(str)
        '''
        self.curves_lock.acquire()
        try:
            curve = self.getCurve(curvename)
            if curve is None:
                title = None
            else:
                title = str(curve.title().text())
        finally:
            self.curves_lock.release()
        return title

    def getCurveNames(self):
        '''returns the names of all TaurusCurves attached to the plot (in arbitrary
        order, if you need a sorted list, see :meth:`getCurveNamesSorted`).

        :return: (list<str>) a copy of self.curves.keys()

        .. seealso:: :meth:`getCurveNamesSorted`
        '''
        self.curves_lock.acquire()
        try:
            ret = copy.deepcopy(list(self.curves.keys()))
        finally:
            self.curves_lock.release()
        return ret

    def getCurveNamesSorted(self):
        '''returns the names of the curves in z order (which is the one used in
        the legend, and in showing the curves).

        :return: (list<str>) curve names

        .. seealso:: :meth:`getCurveNames`
        '''
        self.curves_lock.acquire()
        try:
            names = [o.getCurveName()
                     for o in self.itemList() if isinstance(o, TaurusCurve)]
        finally:
            self.curves_lock.release()
        return copy.deepcopy(names)

    def sortCurves(self, ordered=None):
        '''Sorts the attached curves in a given z order. This affects both the
        ordering in the legend and the visibility order when curves overlap in
        the plotting area. The order is governed by the `ordered` parameter (or
        alphabetically if no parameter is passed).

        :param ordered: (list<str> or None) A list of curve names in the desired
                        order. If None passed, the items will be ordered
                        alphabetically according to their title.
        '''
        self.curves_lock.acquire()
        try:
            if ordered is None:
                orderedObjs = sorted(
                    self.curves.values(),
                    key=lambda curve: curve.titleText(compiled=True)
                )
            else:
                #current = self.curves.keys()
                # if len(ordered) != len(current) or set(map(str.lower,current)) - set(map(str.lower, ordered)):
                #    raise ValueError('Invalid value for the "ordered" parameter')
                orderedObjs = [self.curves[n] for n in ordered]
            for curve in orderedObjs:
                Qwt5.QwtPlotCurve.detach(curve)
                Qwt5.QwtPlotCurve.attach(curve, self)
        finally:
            self.curves_lock.release()

    def toggleZoomer(self, axis=None):
        '''changes the current zoomer to that associated to the given axis
        (zoomer1 is attached to Y1 and zoomer2 to Y2).
        If no axis is passed, the zoomers are toggled.

        :param axis: (Qwt.QwtPlot.Axis or None) axis to activate for zooming. If None passed, the zoomers are toggled.

        :return: (Qwt.QwtPlot.Axis) the Y axis of the enabled zoomer
        '''
        if not self._allowZoomers:
            for z in (self._zoomer1, self._zoomer2):
                z.setEnabled(False)
            return
        if axis is None:
            # find the axis of the currently disabled zoomer
            for z in (self._zoomer1, self._zoomer2):
                if not z.isEnabled():
                    break
            axis = z.yAxis()
        # enable the zoomer corresponding to axis and disable the other one
        for z in (self._zoomer1, self._zoomer2):
            z.setEnabled(z.yAxis() == axis)
        self._zoomer = self.getZoomers(axis)[0]
        self.debug('Now Zooming on %s' % str(self.getAxisName(axis)))
        return self._zoomer.yAxis()

    def getAxisName(self, axis):
        '''If set, it returns the axis title text, otherwise returns the default
        axis name

        :param axis: (Qwt.QwtPlot.Axis)

        :return: (unicode)
        '''
        name = str(self.axisTitle(axis).text())
        if name == '':
            name = self._axesnames[axis]
        return name

    def setPaused(self, paused=True):
        '''delegates the pausing to the curves

        :param paused: (bool) if True, the plot will be paused
        '''
        for c in self.curves.values():
            c.setPaused(paused)
        self._isPaused = paused

    def isPaused(self):
        '''Returns the pause state

        :return: (bool)
        '''
        return self._isPaused

    def __debug(self, *args, **kwargs):
        '''put code here that you want to debug'''
        print("!!!!!!!!!!!!!!!1", self.pos())
        Qt.QToolTip.showText(self.mapToGlobal(self.pos()),
                             "ASDASDASDASD DASDAS ASDA", self)

        return

    def getDefaultAxisLabelsAlignment(self, axis, rotation):
        '''return a "smart" alignment for the axis labels depending on the axis
        and the label rotation

        :param axis: (Qwt5.QwtPlot.Axis) the axis
        :param rotation: (float) The rotation (in degrees, clockwise-positive)

        :return: (Qt.Alignment) an alignment
        '''
        # print "!!!!", {Qwt5.QwtPlot.xBottom:"B" , Qwt5.QwtPlot.yLeft:"L",
        # Qwt5.QwtPlot.yRight:"R", Qwt5.QwtPlot.xTop:"T"}[axis]
        if axis == Qwt5.QwtPlot.xBottom:
            if rotation == 0:
                return Qt.Qt.AlignHCenter | Qt.Qt.AlignBottom
            elif rotation < 0:
                return Qt.Qt.AlignLeft | Qt.Qt.AlignBottom
            else:
                return Qt.Qt.AlignRight | Qt.Qt.AlignBottom
        elif axis == Qwt5.QwtPlot.yLeft:
            if rotation == 0:
                return Qt.Qt.AlignLeft | Qt.Qt.AlignVCenter
            elif rotation < 0:
                return Qt.Qt.AlignLeft | Qt.Qt.AlignBottom
            else:
                return Qt.Qt.AlignLeft | Qt.Qt.AlignTop
        elif axis == Qwt5.QwtPlot.yRight:
            if rotation == 0:
                return Qt.Qt.AlignRight | Qt.Qt.AlignVCenter
            elif rotation < 0:
                return Qt.Qt.AlignRight | Qt.Qt.AlignTop
            else:
                return Qt.Qt.AlignRight | Qt.Qt.AlignBottom
        elif axis == Qwt5.QwtPlot.xTop:
            if rotation == 0:
                return Qt.Qt.AlignHCenter | Qt.Qt.AlignTop
            elif rotation < 0:
                return Qt.Qt.AlignLeft | Qt.Qt.AlignTop
            else:
                return Qt.Qt.AlignRight | Qt.Qt.AlignTop

    def setAxisCustomLabels(self, axis, pos_and_labels, rotation=0, alignment=None):
        '''By calling this method, the scale vaues can be substituted  by custom
        labels at arbitrary positions. In general, it is a good idea to let the
        alignment to be autocalculated.

        :param axis:           (Qwt5.QwtPlot.Axis) the axis
        :param pos_and_labels: (sequence<tuple>) a sequence of
                               position(<float>),label(<str>) tuples
        :param rotation:       (float) rotation value for the labels (in degrees,
                               clockwise-positive, by default it is 0)
        :param alignment:      (Qt.Alignment) an alignment for the labels.
                               If None given, it will be autocalculated

        '''
        positions, labels = list(zip(*pos_and_labels))  # "unzipping"
        positions = list(positions)

        self.setAxisScaleEngine(axis, FixedLabelsScaleEngine(positions))

        sd = FixedLabelsScaleDraw(positions, labels)
        sd.setLabelRotation(rotation)
        if alignment is None:
            alignment = self.getDefaultAxisLabelsAlignment(axis, rotation)
        sd.setLabelAlignment(alignment)
        self.setAxisScaleDraw(axis, sd)

        self.replot()

    def getPickedMarker(self):
        '''returns the marker for the picked points for this plot

        :return: (TaurusCurveMarker)
        '''
        return self._pickedMarker

    def getZoomers(self, axis=None):
        '''returns a list of the zoomer(s) associated to the given axis.
        If None is passed, it returns a list containing the current zoomer

        :param axis: (Qwt5.QwtPlot.Axis) the axis
        '''
        if axis is None:
            return [self._zoomer]
        elif axis == Qwt5.QwtPlot.yLeft:
            return [self._zoomer1]
        elif axis == Qwt5.QwtPlot.yRight:
            return [self._zoomer2]
        elif axis == Qwt5.QwtPlot.xBottom:
            return [self._zoomer1, self._zoomer2]
        else:
            raise ValueError('Invalid axis for getZoomers()')

    def getGrid(self):
        ''' returns the grid of the plot

        :return: (Qwt5.QwtPlotGrid)
        '''
        return self._grid

    def getPlot(self):
        '''deprecated method . Only here for backwards compatibility. It will be
        removed, eventually. Now you should use the TaurusPlot instance instead of
        TaurusPlot.getPlot()'''
        self.info(
            'DEPRECATION WARNING!: Calling TaurusPlot.getPlot() is deprecated. Use the TaurusPlot object itself instead')
        print(self.sender())
        return self

    def getCurve(self, name):
        '''gets a curve object by name.

        **Important**: Note that the curve object is not thread safe. Therefore,
        if you access to the curve object you must do it protected by the
        TaurusPlot.curves_lock reentrant lock.

        :param name: (str) the curve name

        :return: (TaurusCurve) the curve object corresponding to name
        '''
        self.curves_lock.acquire()
        try:
            ret = self.curves.get(str(name))
        finally:
            self.curves_lock.release()
        return ret

    def setAxesLabelFormat(self, format=None, xformat=None, y1format=None, y2format=None):
        '''Convenience method for setting the format of any or all axes
        if format=None, specific formats for x, y1 and y2 can be explicitly set,
        e.g::

            setAxesLabelFormat("%6.2f") #<--sets the "%6.2f" format for all axes
            setAxesLabelFormat(xformat=None, y1format="%i") #<--sets the default format for x and an integer format fotr y1

        :param format: (str) format string to be applied to all axes. If None, the default format is used
        :param xformat: (str) format string to be applied to the X axis. If None, the default format is used
        :param y1format: (str) format string to be applied to the Y1 axis. If None, the default format is used
        :param y2format: (str) format string to be applied to the Y2 axis. If None, the default format is used

        .. seealso:: :meth:`setAxisLabelFormat`
        '''
        if format is None:
            formats = [xformat, y1format, y2format]
        else:
            formats = [format] * 3
        axes = [Qwt5.QwtPlot.xBottom, Qwt5.QwtPlot.yLeft, Qwt5.QwtPlot.yRight]
        for axis, format in zip(axes, formats):
            self.setAxisLabelFormat(axis, format)

    def setAxisLabelFormat(self, axis, format=None):
        '''changes the format of an axis label. format is a python format string
        (e.g., "%6.2f"), . If format=None, the default behaviour is set
        (which uses QLocale.system().toString(value))

        :param axis: (Qwt5.QwtPlot.Axis) the axis
        :param format: (str) format string to be applied to all axes. If None, the default format is used
        '''
        self.axisScaleDraw(axis).setLabelFormat(format)

    def getAxisLabelFormat(self, axis):
        '''Returns the label format for the given axis

        :param axis: (Qwt5.QwtPlot.Axis) the axis

        :return: (str or None)

        .. seealso:: :meth:`setAxisLabelFormat`
        '''
        try:
            return self.axisScaleDraw(axis).getLabelFormat()
        except AttributeError:
            return None

    def resetAxisLabelFormat(self, axis):
        '''equivalent to setAxisLabelFormat(axis, None)

        :param axis: (Qwt5.QwtPlot.Axis) the axis

        See also:setAxisLabelFormat
        '''
        self.setAxisLabelFormat(axis, None)

    def showMaxPeaks(self, show):
        """This function will set the showMaxPeak flag of all the curves in the
        plot.

        :param show: (bool) if True, the max values of the displayed curve(s)
                     will be shown on the plot. Otherwise, they will be hidden.
        """
        self.curves_lock.acquire()
        try:
            self._showMaxPeaks = show
            for curveName in self.curves.keys():
                curve = self.curves.get(str(curveName))
                if show:
                    curve.showMaxPeak(True)
                    curve.attachMaxMarker(self)
                else:
                    curve.showMaxPeak(False)
                    curve.detachMaxMarker()
        finally:
            self.curves_lock.release()
        self.replot()

    def showMinPeaks(self, show):
        """This function will set the showMinPeak flag of all the curves in the plot.

        :param show: (bool) if True, the min values of the displayed curve(s)
                     will be shown on the plot. Otherwise, they will be hidden.
        """
        self.curves_lock.acquire()
        try:
            self._showMinPeaks = show
            for curveName in self.curves.keys():
                curve = self.curves.get(str(curveName))
                if show:
                    curve.showMinPeak(True)
                    curve.attachMinMarker(self)
                else:
                    curve.showMinPeak(False)
                    curve.detachMinMarker()
        finally:
            self.curves_lock.release()
        self.replot()

    def showCurve(self, curve, on):
        '''switch visibility of a curve (as well as any markers associated to
        it) on/off

        **Important**: This is a non-thread safe method. Do not manipulate curve
        objects without protecting the access with Taurusplot.curves_lock

        :param curve: (TaurusCurve) the curve object
        :param on: (bool) if True, the curve will be shown otherwise it will be
                   hidden
        '''
        curve.setVisible(on)
        legend = self.legend()
        if legend:
            widget = legend.find(curve)
            if isinstance(curve, TaurusCurve):
                title = curve.title()
                # if hidding the curve, hide peaks also
                # change legend color too
                if on is False:
                    title.setColor(Qt.Qt.darkGray)
                    curve.showMaxPeak(False)
                    curve.showMinPeak(False)
                    curve.detachMarkers()
                # if the curve is shown, show the markers as well (if required)
                # and change the color in the legend too!
                else:
                    if curve.yAxis() == Qwt5.QwtPlot.yLeft:
                        title.setColor(Qt.Qt.black)
                    else:
                        title.setColor(Qt.Qt.darkBlue)
                    if self._showMaxPeaks:
                        curve.showMaxPeak(True)
                        curve.attachMarkers(self)
                    if self._showMinPeaks:
                        curve.showMinPeak(True)
                        curve.attachMarkers(self)
                curve.setTitle(title)
                widget.setText(title)
        self.replot()

    def toggleCurveState(self, curve):
        '''cycles through 3 possible states for a curve:

            - invisible
            - attached to Y1
            - attached to Y2

        :param curve: (TaurusCurve) the curve object
        '''
        self.curves_lock.acquire()
        try:
            # get the key in the self.curves directory
            curveName = None
            for curveName, c in self.curves.items():
                if c is curve:
                    break
            axis = curve.yAxis()
            # Toggle state
            if not curve.isVisible():
                self.setCurvesYAxis([curveName], Qwt5.QwtPlot.yLeft)
            elif axis == Qwt5.QwtPlot.yLeft:
                self.setCurvesYAxis([curveName], Qwt5.QwtPlot.yRight)
            elif axis == Qwt5.QwtPlot.yRight:
                self.showCurve(curve, False)
                self.autoShowYAxes()
        finally:
            self.curves_lock.release()
        self.replot()

    @Qt.pyqtSlot("QString", name="dataChanged")
    def curveDataChanged(self, name):
        '''slot that is called whenever a curve emits a dataChanged signal

        :emits: "dataChanged(const QString &)"

        :param name: (str) curve name
        '''
        self.curves_lock.acquire()
        try:
            curve = self.curves.get(str(name))
            curve.safeSetData()
            # self._zoomer.setZoomBase()
            if self.getXDynScale():  # keep the scale width constant, but translate it to get the last value
                max = curve._xValues[-1]
                min = max - self.getXAxisRange()
                self.setAxisScale(Qwt5.QwtPlot.xBottom, min, max)
        finally:
            self.curves_lock.release()
        self.dataChanged.emit(str(name))
        self.replot()

    def attachRawData(self, rawdata, properties=None, id=None):
        """attaches a curve to the plot formed from raw data that comes in a dict

        :param rawdata: (dict) A dictionary defining a rawdata curve. It has the
                        following structure (all keys are optional, but either
                        "y" or "f(x)" must be present. Also, the value of x, y
                        and f(x) can be None):

                        {"title":<str>, "x":list<float>, "y":list<float>,
                        "f(x)": <str (an expression to evaluate on the x values)>}

        :param properties: (CurveAppearanceProperties) appearance properties for
                           the curve
        :param id: (str) This will be the internal name identifier used for the
                   curve. If not given, it defaults to the title or to "rawdata"
                   if no title is given.

        :return: (QwtPlotCurve) the attached curve

        *Note*: every member of the rawdata dictionary is optional except for the y values (or, alternatively, f(x) AND x)

        *Note*: using "name" in the rawdata dictionary is a still-supported-but-deprecated synonim of "title".
        """
        if properties is None:
            properties = CurveAppearanceProperties(
                lColor=self._curvePens.next().color(), lWidth=2)
        # Deprecation Warning:
        if "pen" in rawdata or "style" in rawdata:
            raise DeprecationWarning(
                "'pen' or 'style' are no longer supported. Use the properties parameter instead")
        if "name" in rawdata:
            if "title" in rawdata:
                self.error(
                    'Inconsistence: both "name" and "title" passed for rawdata. Use "title" only')
            else:
                self.warning(
                    'The use of "name" (=%s) for attaching rawdata is deprecated. Use "title" instead' % rawdata["name"])
                rawdata["title"] = rawdata["name"]

        y = rawdata.get("y", None)
        fx = rawdata.get("f(x)", None)
        x = rawdata.get("x", None)
        if fx is None:
            if y is None:
                raise ValueError('Either "f(x)" or "y" keys must be present')
            title = str(rawdata.get("title", "rawdata"))
            if x is None:
                # if no x is given, the indices will be used
                x = numpy.arange(len(y))
            else:
                x = numpy.array(x)
        else:
            if y is not None:
                raise ValueError(
                    'only one of "f(x)" or "y" keys can be present')
            if x is None:
                # we need x values in which to evaluate
                raise ValueError('Missing "x" values')
            title = str(rawdata.get("title", fx))
            x = numpy.array(x)
            sev = SafeEvaluator({'x': x})
            try:
                y = sev.eval(fx)
            except:
                # TODO: deal with this exception properly.
                self.warning(
                    "the function '%s' could not be evaluated (skipping)" % title)
                return
        #@todo: support error bars
#        ex=rawdata.get("ex",numpy.zeros(len(y)))
#        ey=rawdata.get("ey",numpy.zeros(len(y)))

        # at this point, both x and y must be valid
        y = numpy.array(y)

        if id is None:
            name = title
        else:
            name = id
        self.curves_lock.acquire()
        try:
            if name in self.curves:
                curve = self.curves.get(name)
                if curve.isRawData:
                    self.detachRawData(name)
                else:
                    curve.unregisterDataChanged(self, self.curveDataChanged)
                    curve.detach()
                    self.curves.pop(name)
                self.debug('overwriting curve %s with raw data' % name)
            self.debug('attaching raw data with name %s' % name)
            curve = TaurusCurve(name, rawData=rawdata,
                                optimized=self.isOptimizationEnabled())
            # curve.fireEvent = lambda arg:None  #!!! reimplementing FireEvent
            # on the fly! (ugly-lazy hack)
            curve.attach(self)
            if self._showMaxPeaks:
                curve.attachMaxMarker(self)
            if self._showMinPeaks:
                curve.attachMinMarker(self)
            curve._xValues, curve._yValues = x, y
            curve.setData(x, y)
            # note that the title and the name may differ
            curve.setTitle(title)
            curve.setAppearanceProperties(properties)
            self.curves[name] = curve
            self.showCurve(curve, True)
            self.showLegend(len(self.curves) > 1, forever=False)
            self._zoomer1.setZoomBase()
            self._zoomer2.setZoomBase()
            self.replot()
        finally:
            self.curves_lock.release()
        return curve

    def detachRawData(self, name):
        '''dettaches a raw data curve

        :param name: (str) name (identifier) of the curve to dettach
        '''
        name = str(name)
        self.debug("detaching raw data with name %s" % name)
        self.curves_lock.acquire()
        try:
            curve = self.curves.get(name)
            if curve is None or not curve.isRawData:
                self.error(
                    "detachRawData failed: '%s' is not a rawData curve" % name)
                return
            curve.detach()
            self.curves.pop(name)
        finally:
            self.curves_lock.release()
        self.replot()

    def clearAllRawData(self):
        """
        removes all rawdata curves from the plot.

        :return: (list<str>) the list of removed curve names
        """
        self.curves_lock.acquire()
        try:
            names = [name for name in self.curves if self.curves[
                name].isRawData]
        finally:
            self.curves_lock.release()

        for name in names:
            self.detachRawData(name)
        return names

    def getCurveData(self, curvename, numpy=False):
        """returns the data in the curve as two lists (x,y) of values

        :param curvename: (str) the curve name
        :param numpy: (bool) if True, the result is returned as numpy arrays instead of lists

        :return: (tuple<list,list>) tuple of two lists (x,y) containing the curve data
        """
        self.curves_lock.acquire()
        try:
            if curvename in self.curves:
                data = self.curves[curvename].data()
                x = [data.x(i) for i in range(data.size())]
                y = [data.y(i) for i in range(data.size())]
            else:
                self.error("Curve '%s' not found" % curvename)
                raise KeyError()
        finally:
            self.curves_lock.release()
        if numpy:
            x, y = numpy.array(x), numpy.array(y)
        return x, y

    def updateCurves(self, names):
        '''
        Updates the TaurusCurves being plotted. It adds a new curve for each new
        curve model passed and removes curves if they are not in the names.

        :param names:   (sequence<str>) a sequence of curve models. One curve
                        will be created for each element of names.
                        Each  curve model can consist of a single attribute name
                        (which will be used for the Y values) or by two
                        attribute names separated by a '|' (in which case, the
                        left-hand attribute is used for the X values and the
                        right hand value for the Y values)
        '''

        self.curves_lock.acquire()
        try:
            xnames, ynames = [], []
            for name in names:
                n = name.split("|")
                yname = n[-1]
                xname = None
                if len(n) > 1:
                    xname = n[0]
                xnames.append(xname)
                ynames.append(yname)

            del_curves = [name for name in self.curves
                          if name not in ynames]

            # if all curves were removed, reset the color palette
            if len(del_curves) == len(self.curves):
                self._curvePens.setCurrentIndex(0)

            for i, name in enumerate(ynames):
                xname = xnames[i]
                name = str(name)
                self.debug('updating curve %s' % name)
                if name not in self.curves:
                    curve = TaurusCurve(name, xname, self,
                                        optimized=self.isOptimizationEnabled())
                    curve.attach(self)
                    self.curves[name] = curve
                    self.showCurve(curve, True)

                    if self._showMaxPeaks:
                        curve.attachMaxMarker(self)
                    if self._showMinPeaks:
                        curve.attachMinMarker(self)
                    curve.setPen(next(self._curvePens))
                    curve.setUseParentModel(self.getUseParentModel())
                    curve.setTitleText(self.getDefaultCurvesTitle())
                    curve.registerDataChanged(self, self.curveDataChanged)
                    self.curveDataChanged(name)

            # curves to be removed
            for name in del_curves:
                name = str(name)
                #curve = self.curves.pop(name)
                curve = self.curves.get(name)
                if not curve.isRawData:  # The rawdata curves should not be dettached by updateCurves. Call detachRawdata insted
                    curve.unregisterDataChanged(self, self.curveDataChanged)
                    curve.detach()
                    self.curves.pop(name)
            if del_curves:
                self.autoShowYAxes()

            # legend
            self.showLegend(len(self.curves) > 1, forever=False)
            self.replot()

        finally:
            self.curves_lock.release()

    def getLegend(self):
        '''Returns the legend object of this plot

        :return: (QwtLegend)
        '''
        return self._legend

    def updateLegend(self, force=False):
        '''Updates the legend object of the plot (if it does not exist, it may
        create a fresh one)

        :param force: (bool) if True, the legend will be updated even if it is
                      not being shown. (default=False)
        '''
        if self._showLegend:
            if force or not self.legend():
                self._legend = Qwt5.QwtLegend()
                self._legend.setItemMode(Qwt5.QwtLegend.ClickableItem)
                self._legend.setDisplayPolicy(Qwt5.QwtLegend.FixedIdentifier,
                                              Qwt5.QwtLegendItem.ShowLine |
                                              Qwt5.QwtLegendItem.ShowSymbol |
                                              Qwt5.QwtLegendItem.ShowText)
                self.insertLegend(self._legend, self._legendPos)
                self._legend.setToolTip(
                    "Clicking on a legend item changes\n the associated Y axis for the curve.")
        else:
            self._legend = None
            self.insertLegend(None)

    def showLegend(self, show, forever=True):
        '''whether to show or not the legend.

        :param show: (bool) if True, the legend will be shown
        :param forever: (bool) if True, the setting will be permant (e.g., the
                        legend won't be hidden even if only one curve is
                        plotted) (default=True)
        '''
        if forever:
            self._legendDecissionIsForever = forever
            self._showLegend = show
        else:
            if not self._legendDecissionIsForever:
                self._showLegend = show
        self.updateLegend()
        self._showLegendAction.setChecked(self._showLegend)

    def getModelObj(self, idx):
        '''See :meth:`TaurusBaseComponent.getModelObj`'''
        return self.getCurve(self._modelNames[idx]).getModelObj()

    # def defineStyle(self):
    #    pass

    def minimumSizeHint(self):
        '''See :meth:`QWidget.minimumSizeHint`'''
        return Qt.QSize(48, 26)

    def sizeHint(self):
        '''See :meth:`QWidget.sizeHint`'''
        return Qt.QSize(300, 200)

    @Qt.pyqtSlot('QString', name='modelChanged')
    def parentModelChanged(self, parentmodel_name):
        '''See :meth:`TaurusBaseComponent.parentModelChanged`'''
        self.curves_lock.acquire()
        try:
            for curve in self.curves.values():
                curve.setModelCheck(curve.getModel(), False)
        finally:
            self.curves_lock.release()

    def getParentTaurusComponent(self):
        '''See :meth:`TaurusBaseComponent.getParentTaurusComponent`'''
        p = self.parentWidget()
        while p and not isinstance(p, TaurusBaseComponent):
            if isinstance(p, Qt.QDialog) or isinstance(p, Qt.QMainWindow):
                p = None
                break
            p = p.parentWidget()
        return p

    # def keyPressEvent(self,keyEvent):
    #    """This function will capture any key press and react on ESC key pressed to set autoscale on all axis"""
    #    #Leave this commented unless you want to debug
    #    #elif (keyEvent.key() == Qt.Qt.Key_D):
    #    #    self.__debug()
    #    #    keyEvent.accept()
    #    #
    #    #else:
    #    #    keyEvent.ignore()
    #    return

    def closeEvent(self, event):
        '''See :meth:`Qwidget.closeEvent`'''
        # make sure no dialogs are left open
        if self.DataImportDlg is not None:
            self.DataImportDlg.close()

    def contextMenuEvent(self, event):
        """ This function is called when there is context menu event. See
        :meth:`Qwidget.closeEvent` A pop up menu will be shown with the
        available options. Different parts of the plot (canvas, axes,...) behave
        differently"""

        # print "!!!!!!!!",  self.canvas().underMouse(),
        # self.axisWidget(self.yLeft).underMouse(),
        # self.axisWidget(self.yRight).underMouse(),
        # self.axisWidget(self.xBottom).underMouse()
        if self.canvas().underMouse():
            self._canvasContextMenu().exec_(event.globalPos())
        elif self.axisWidget(self.yLeft).underMouse():
            self._axisContextMenu(self.yLeft).exec_(event.globalPos())
        elif self.axisWidget(self.yRight).underMouse():
            self._axisContextMenu(self.yRight).exec_(event.globalPos())
        elif self.axisWidget(self.xBottom).underMouse():
            self._axisContextMenu(self.xBottom).exec_(event.globalPos())
        else:
            # default catch-all #@TODO FOR SOME REASON, the underMouse() method
            # used above fails sometimes !!!???
            self._canvasContextMenu().exec_(event.globalPos())
        event.accept()

    def _canvasContextMenu(self):
        """Returns a contextMenu for the canvas

        :return: (Qt.QMenu) the context menu for the canvas
        """

        menu = Qt.QMenu(self)

        menu.addAction(self._configDialogAction)
        menu.addAction(self._inputDataAction)
        menu.addAction(self._saveConfigAction)
        menu.addAction(self._loadConfigAction)
        menu.addAction(self._setCurvesTitleAction)
        menu.addSeparator()

        scalesSubMenu = menu.addMenu("&Scales")
        scalesSubMenu.addAction(self._autoscaleAllAxisAction)
        scalesSubMenu.addSeparator()
        for axis in (Qwt5.QwtPlot.xBottom, Qwt5.QwtPlot.yLeft, Qwt5.QwtPlot.yRight):
            if self.axisEnabled(axis):
                scalesSubMenu.addMenu(self._axisContextMenu(axis=axis))

        menu.addAction(self._showMaxAction)
        menu.addAction(self._showMinAction)

        menu.addAction(self._showLegendAction)
        menu.addAction(self._dataInspectorAction)
        menu.addAction(self._setFormatterAction)

        menu.addSeparator()
        exportSubMenu = menu.addMenu("&Export && Print")
        menu.addAction(self._curveStatsAction)
        exportSubMenu.addAction(self._printAction)
        exportSubMenu.addAction(self._exportPdfAction)
        exportSubMenu.addAction(self._exportAsciiAction)

        menu.addSeparator()
        menu.addAction(self._pauseAction)

        if self.isWindow():
            menu.addAction(self._closeWindowAction)

        return menu

    def _axisContextMenu(self, axis=None):
        '''Returns a context menu for the given axis

        :param axis: (Qwt5.QwtPlot.Axis) the axis

        :return: (Qt.QMenu) the context menu for the given axis
        '''
        menu = Qt.QMenu(self)
        axisname = self.getAxisName(axis)
        menu.setTitle("Options for axis %s" % axisname)

        autoScaleThisAxis = lambda: self.setAxisAutoScale(axis=axis)
        autoscaleAction = menu.addAction("AutoScale %s" % axisname)
        autoscaleAction.triggered.connect(autoScaleThisAxis)

        if not self.getXIsTime():
            switchThisAxis = lambda: self.setAxisScaleType(
                axis=axis, scale=None)
            switchThisAxisAction = menu.addAction(
                "Toggle linear/log for %s" % axisname)
            switchThisAxisAction.triggered.connect(switchThisAxis)

        if axis in (Qwt5.QwtPlot.yLeft, Qwt5.QwtPlot.yRight):
            zoomOnThisAxis = lambda: self.toggleZoomer(axis=axis)
            zoomOnThisAxisAction = menu.addAction(
                "Zoom-to-region acts on %s" % axisname)
            zoomOnThisAxisAction.triggered.connect(zoomOnThisAxis)

        elif axis in (Qwt5.QwtPlot.xBottom, Qwt5.QwtPlot.xTop):
            if self.isXDynScaleSupported():
                xDynAction = menu.addAction("&Auto-scroll %s" % axisname)
                xDynAction.setToolTip(
                    'If enabled, the scale of %s will be autoadjusted to provide a fixed window moving to show always the last value')
                xDynAction.setCheckable(True)
                xDynAction.setChecked(self.getXDynScale())
                xDynAction.toggled.connect(self.setXDynScale)
        return menu

    def showConfigDialog(self):
        """Slot for the showConfigMenuAction. Launches the plot configuration
        dialog.
        """
        self._configDialog = TaurusPlotConfigDialog(self)
        self._configDialog.exec_()
        # destroy the dialog (it may probably not be used anymore)
        del self._configDialog

    def getCurveAppearancePropertiesDict(self):
        '''Returns the appearance properties of all curves in the plot.

        :return: (dict<str,CurveAppearanceProperties>) a dictionary whose keys
                 are the curve names and whose values are the corresponding
                 CurveAppearanceProperties object

        .. seealso:: :meth:`setCurveAppearanceProperties`
        '''
        self.curves_lock.acquire()
        try:
            propdict = {}
            for name, curve in self.curves.items():
                propdict[name] = copy.deepcopy(curve.getAppearanceProperties())
        finally:
            self.curves_lock.release()
        return propdict

    def setCurveAppearanceProperties(self, propDict):
        """It gets a dictionary of namecurvenames,properties and applies the
        properties to the corresponding curves.

        :param propDict: (dict<str,CurveAppearanceProperties>) a dictionary whose keys
                         are the curve names and whose values are the corresponding
                         CurveAppearanceProperties object

        .. seealso:: :meth:`getCurveAppearancePropertiesDict`
        """
        self.curves_lock.acquire()
        try:
            for name, prop in propDict.items():
                c = self.curves[name]
                c.setAppearanceProperties(copy.deepcopy(prop))
                visible = getattr(prop, 'visible', True)
                if visible is not None:
                    self.showCurve(c, visible)
        finally:
            self.curves_lock.release()
        self.autoShowYAxes()
        self.replot()

    def onCurveAppearanceChanged(self, prop, names):
        """Applies the properties given in prop to all the curves named in names.
        This functions is called from the config dialog when changes are applied.

        :param prop: (CurveAppearanceProperties) the properties object
        :param names: (sequence<str>) a sequence of names of curves to which the
                      properties should be applied
        """
        propDict = {}
        for name in names:
            propDict[name] = prop
        self.setCurveAppearanceProperties(propDict)

    def _createAxesDict(self):
        '''returns a dictionary containing relevant information about the current axes

        :return: (dict) Configurations that can be loaded with applyAxesConfig
        '''
        xMin, xMax = self.getAxisScale(Qwt5.QwtPlot.xBottom)
        y1Min, y1Max = self.getAxisScale(Qwt5.QwtPlot.yLeft)
        y2Min, y2Max = self.getAxisScale(Qwt5.QwtPlot.yRight)
        axesdict = {'xMin': xMin, 'xMax': xMax, 'y1Min': y1Min, 'y1Max': y1Max, 'y2Min': y2Min, 'y2Max': y2Max,
                    'xMode': int(self.getAxisTransformationType(Qwt5.QwtPlot.xBottom)),
                    'y1Mode': int(self.getAxisTransformationType(Qwt5.QwtPlot.yLeft)),
                    'y2Mode': int(self.getAxisTransformationType(Qwt5.QwtPlot.yRight)),
                    'xDyn': self.getXDynScale(),
                    'xIsTime': self.getXIsTime()
                    }
        return axesdict

    def _createMiscDict(self):
        '''returns a dictionary containing misc information about the plot

        :return: (dict) configurations that can be loaded with applyMiscConfig
        '''
        miscdict = {'defaultCurvesTitle': self.getDefaultCurvesTitle(),
                    'canvasBackground': self.canvasBackground(),
                    'orderedCurveNames': self.getCurveNamesSorted(),
                    'plotTitle': str(self.title().text()),
                    'formatter': self.getFormat()}
        if self.isWindow():
            miscdict["Geometry"] = self.saveGeometry()
        return miscdict

    def checkConfigVersion(self, configdict, showDialog=False, supportedVersions=None):
        '''
        Check if the version of configdict is supported.

        :param configdict: (dict) configuration dictionary to check
        :param showDialog: (bool) whether to show a QtWarning dialog if check
                           failed (false by default)
        :param supportedVersions: (sequence<str>, or None) supported version
                                  numbers, if None given, the versions supported
                                  by this widget will be used (i.e., those
                                  defined in self._supportedConfigVersions)

        :return: (bool) returns True if the configdict is of the right version

        .. seealso:: :meth:`TaurusBaseComponent.checkConfigVersion`
        '''
        if supportedVersions is None:
            supportedVersions = self._supportedConfigVersions
        version = configdict.get("ConfigVersion", "__UNVERSIONED__")
        if version not in supportedVersions:
            msg = 'Unsupported Config Version %s. (Supported: %s)' % (
                version, repr(supportedVersions))
            self.warning(msg)
            if showDialog:
                Qt.QMessageBox.warning(
                    self, "Wrong Configuration Version", msg, Qt.QMessageBox.Ok)
            return False
        return True

    def createConfigDict(self, allowUnpickable=False, curvenames=None):
        self.info(
            "Deprecation warning: createConfigDict is deprecated. Please use createConfig instead")
        return self.createConfig(allowUnpickable=False, curvenames=None)

    def createConfig(self, allowUnpickable=False, curvenames=None, **kwargs):
        '''Returns a pickable dictionary containing all relevant information
        about the current plot. Implemented as in :meth:`TaurusBaseComponent.createConfig`
        For Tango attributes it stores the attribute name and the curve properties
        For raw data curves, it stores the data as well.

        Hint: The following code allows you to serialize the configuration
        dictionary as a string (which you can store as a QSetting, or as a Tango
        Attribute)::

            import pickle
            c = pickle.dumps(taurusplot.createConfig())  #c is a string that can be stored


        :param curvenames:  (sequence<str>) a sequence of curve names for which the
                            configuration will be stored (all by default).

        :return: (dict) configurations (which can be loaded with applyConfig)


        .. seealso:: :meth:`createConfig`, :meth:`TaurusBaseComponent.createConfig`
        '''
        axesdict = self._createAxesDict()
        rawdatadict = CaselessDict()
        tangodict = CaselessDict()
        propdict = {}
        miscdict = self._createMiscDict()
        self.curves_lock.acquire()
        try:
            if curvenames is None:
                curvenames = list(self.curves)
            curvenames = self._lowerIfInsensitive(curvenames)
            for name in curvenames:
                curve = self.curves.get(name)
                propdict[name] = copy.deepcopy(curve.getAppearanceProperties())
                if curve.isRawData:
                    rawdatadict[name] = curve.getRawData()
                else:
                    tangodict[name] = curve.getModel()
        except Exception as e:
            self.error(
                'Exception while gathering curves configuration info' + str(e))
        finally:
            self.curves_lock.release()
        curvenames = CaselessList(curvenames)
        model = CaselessList([m for m in self.getModel() if m in curvenames])
        configdict = {"Axes": axesdict, "Misc": miscdict, "RawData": rawdatadict,
                      "TangoCurves": tangodict, "CurveProp": propdict,
                      "ConfigVersion": self._supportedConfigVersions[-1],
                      "model": model}
        return configdict

    def applyConfig(self, configdict, **kwargs):
        """implemented as in :meth:`TaurusBaseComponent.applyConfig`

        :param configdict: (dict<str,object>)

        .. seealso:: :meth:`createConfig`, :meth:`TaurusBaseComponent.applyConfig`
        """
        if not self.checkConfigVersion(configdict):
            return
        # attach the curves
        for rd in configdict["RawData"].values():
            self.attachRawData(rd)
        # for backwards compatibility, if the ordered list of models is not
        # stored, it uses the unsorted dict values
        models = configdict.get("model", list(configdict["TangoCurves"].values()))
        self.addModels(models)
        # set curve properties
        self.setCurveAppearanceProperties(configdict["CurveProp"])
        self.updateLegend(force=True)
        # set the axes
        self.applyAxesConfig(configdict["Axes"])
        # set other misc configurations
        self.applyMiscConfig(configdict["Misc"])

    def applyMiscConfig(self, miscdict):
        '''sets the configurations according to settings stored in the misc dict,
        which can be generated with _createMiscDict()

        :param miscdict: (dict) Dictionary of properties
        '''
        self.setDefaultCurvesTitle(miscdict["defaultCurvesTitle"])
        self.setCanvasBackground(miscdict["canvasBackground"])
        self.sortCurves(ordered=miscdict.get("orderedCurveNames", None))
        if "plotTitle" in miscdict:
            self.setTitle(miscdict['plotTitle'])
        # set geometry (if this is a top level window)
        if self.isWindow() and 'Geometry' in miscdict:
            self.restoreGeometry(miscdict['Geometry'])
        if "formatter" in miscdict:
            self.setFormat(miscdict['formatter'])

    def applyAxesConfig(self, axes):
        '''sets the axes according to settings stored in the axes dict,
        which can be generated with _createAxesDict()

        :param axes: (dict) contains axes properties
        '''
        self.setXIsTime(axes["xIsTime"])
        self.setXDynScale(axes["xDyn"])
        self.setAxisScale(Qwt5.QwtPlot.xBottom, axes["xMin"], axes["xMax"])
        self.setAxisScale(Qwt5.QwtPlot.yLeft, axes["y1Min"], axes["y1Max"])
        self.setAxisScale(Qwt5.QwtPlot.yRight, axes["y2Min"], axes["y2Max"])
        if not self.getXIsTime():
            self.setAxisScaleType(Qwt5.QwtPlot.xBottom, axes["xMode"])
        self.setAxisScaleType(Qwt5.QwtPlot.yLeft, axes["y1Mode"])
        self.setAxisScaleType(Qwt5.QwtPlot.yRight, axes["y2Mode"])

    def saveConfig(self, ofile=None, curvenames=None):
        """Stores the current curves and their display properties in a file for
        later retrieval.

        :param ofile: (file or string) file or filename to store the configuration. If None passed,
        :param curvenames:  (list<str>) a list of curve names for which the
                            configuration will be stored (all by default).

        :return: (str) file name used
        """
        import pickle
        if ofile is None:
            ofile, _ = compat.getSaveFileName(
                self, 'Save Taurusplot Configuration',
                'TaurusplotConfig.pck',
                'TaurusPlot Curve Properties File (*.pck)'
            )
            if not ofile:
                return
        if isinstance(ofile, string_types):
            ofile = open(ofile, 'wb')
        configdict = self.createConfig(curvenames=curvenames)
        self.info("Saving current settings in '%s'" % ofile.name)
        pickle.dump(configdict, ofile)
        return ofile.name

    def loadConfig(self, ifile=None):
        """Reads a file stored by saveConfig() and applies the settings

        :param ifile: (file or string) file or filename from where to read the configuration

        :return: (str) file name used
        """
        import pickle
        if ifile is None:
            ifile, _ = compat.getOpenFileName(
                self, 'Load Taurusplot Configuration', '',
                'TaurusPlot Curve Properties File (*.pck)')
            if not ifile:
                return
        if isinstance(ifile, string_types):
            ifile = open(ifile, 'rb')
        configdict = pickle.load(ifile)
        self.applyConfig(configdict)
        return ifile.name

    def setEventFilters(self, filters=None, curvenames=None, preqt=False):
        '''propagates a list of taurus filters to the curves given by curvenames.
        See :meth:`TaurusBaseComponent.setEventFilters`
        '''
        if curvenames is None:
            curvenames = self.curves.keys()
        self.curves_lock.acquire()
        try:
            for name in curvenames:
                self.curves[name].setEventFilters(filters, preqt=preqt)
        finally:
            self.curves_lock.release()

    def setAxisAutoScale(self, axis):
        """Sets the axis to autoscale and resets the zoomer for that axis if needed

        :param axis: (Qwt5.QwtPlot.Axis) the axis

        .. seealso:: :meth:`autoScaleAllAxes`
        """
        Qwt5.QwtPlot.setAxisAutoScale(self, axis)
        for z in self.getZoomers(axis):
            z.setZoomBase()
        self.replot()

    def autoScaleAllAxes(self):
        '''Optimized autoscale of whole plot'''
        minX = float('inf')
        maxX = float('-inf')
        if self.getXDynScale():
            originalXRange = self.getXAxisRange()
            self.curves_lock.acquire()
            try:
                for c in self.curves.values():
                    if c.minXValue() < minX:
                        minX = c.minXValue()
                    if c.maxXValue() > maxX:
                        maxX = c.maxXValue()
                    if minX != maxX:
                        break
            finally:
                self.curves_lock.release()

        for axis in range(Qwt5.QwtPlot.axisCnt):
            if axis == Qwt5.QwtPlot.xBottom and minX == maxX:
                Qwt5.QwtPlot.setAxisScale(
                    self, axis, minX - 0.5 * originalXRange, minX + 0.5 * originalXRange)
            else:
                Qwt5.QwtPlot.setAxisAutoScale(self, axis)
        self.replot()
        # Update the zoom stacks
        self._zoomer1.setZoomBase()
        self._zoomer2.setZoomBase()

    def setAxisScale(self, axis, min, max):
        """Rescales the given axis to the range defined by min and max. If min
        and max are None, autoscales. It also takes care of resetting the
        affected zoomer(s)

        :param axis: (Qwt5.QwtPlot.Axis) the axis
        :param min: (float or None) minimum value for the axis
        :param max: (float or None) maximum value for the axis

        **Example**::

            tt=TaurusTrend()
            tt.setAxisScale(tt.yLeft, 0, 10) #this will set the Y1 axis range from 0 to 10
            tt.setAxisScale(tt.xBottom, None, None) #This will autoscale the X axis

        """
        if min is None and max is None:
            self.setAxisAutoScale(axis)
        else:
            Qwt5.QwtPlot.setAxisScale(self, axis, min, max)
            self.replot()
        for z in self.getZoomers(axis):
            z.setZoomBase()

    def getAxisScale(self, axis):
        """returns the lower and higher bounds for the given axis, or None,None
        if the axis is in autoscale mode

        :param axis: (Qwt5.QwtPlot.Axis) the axis

        :return: (float,float) atuple of floats (or None,None)
        """
        if self.axisAutoScale(axis):
            return None, None
        return self.axisScaleDiv(axis).lowerBound(), self.axisScaleDiv(axis).upperBound()

    def getXAxisRange(self, axis=Qwt5.QwtPlot.xBottom):
        '''same as self.axisScaleDiv(axis).range()

        :param axis: (Qwt5.QwtPlot.Axis) the (X) axis. (default=Qwt5.QwtPlot.xBottom)

        :return: (float) the absolute difference between the higher and lower limits of the axis scale
        '''
        return self.axisScaleDiv(axis).range()

    def setAxisScaleType(self, axis, scale=None):
        '''sets the type of scale, (log or linear) for a given axis, If scale is None, the scale
        type will be toggled

        :param axis: (Qwt5.QwtPlot.Axis) the axis
        :param scale: (Qwt5.QwtScaleTransformation.Type) the scale
                      transformation. For convenience, the strings "Linear"
                      and "Logarithmic" can be used as well'''

        if self.getXIsTime() and isinstance(self.axisScaleEngine(axis), DateTimeScaleEngine):
            raise ValueError(
                'TaurusPlot.setAxisScaleType cannot be called with time scales')
        if not Qwt5.QwtPlot.axisValid(axis):
            self.error("TaurusPlot.setScale() invalid axis: " + axis)
        if scale is None:
            currentType = self.getAxisTransformationType(axis)
            if currentType == Qwt5.QwtScaleTransformation.Linear:
                scale = Qwt5.QwtScaleTransformation.Log10
            elif currentType == Qwt5.QwtScaleTransformation.Log10:
                scale = Qwt5.QwtScaleTransformation.Linear

        if scale in ("Linear", Qwt5.QwtScaleTransformation.Linear, int(Qwt5.QwtScaleTransformation.Linear)):
            newScale = Qwt5.QwtLinearScaleEngine()
        elif scale in ("Logarithmic", Qwt5.QwtScaleTransformation.Log10, int(Qwt5.QwtScaleTransformation.Log10)):
            newScale = Qwt5.QwtLog10ScaleEngine()
        else:
            self.error(
                "TaurusPlot.setAxisScaleType() invalid scale: %s" % str(scale))
            return
        self.setAxisScaleEngine(axis, newScale)
        # update the data in the curves (because of the filtering done for
        # possitive values in log mode)
        self.__updateCurvesData()
        return

    def axisScaleDiv(self, axis):
        """ Return the scale division of a specified axis.

        :param axis: (Qwt5.QwtPlot.Axis) the axis

        :return: (Qwt5.QwtScaleDiv) scale division
        """
        div = Qwt5.QwtPlot.axisScaleDiv(self, axis)
        # fix compatibility issue with Qwt < 5.2 (contributed by A. Persson)
        if Qwt5.QWT_VERSION < 0x050200:
            div.lowerBound = div.lBound
            div.upperBound = div.hBound
        return div

    def __updateCurvesData(self):
        '''call safeSetData again on all curves to force a refiltering in case the scale changed its type'''
        self.curves_lock.acquire()
        try:
            for c in self.curves.values():
                c.safeSetData()
        finally:
            self.curves_lock.release()
        self.replot()

    def exportPdf(self, fileName=None):
        """Export the plot to a PDF. slot for the _exportPdfAction.

        :param fileName: (str) The name of the file to which the plot will be
                         exported. If None given, the user will be prompted for
                         a file name.
        """
        if fileName is None:
            fileName, _ = compat.getSaveFileName(
                self, 'Export File Name', 'plot.pdf', 'PDF Documents (*.pdf)')
        fileName = str(fileName)
        if fileName:
            try:
                # check if the file is actually writable
                f = open(fileName, 'w')
                f.close()
            except:
                self.error("Can't write to '%s'" % fileName)
                Qt.QMessageBox.warning(self, "File Error",
                                       "Can't write to\n'%s'" % fileName,
                                       Qt.QMessageBox.Ok)
                return
            printer = Qt.QPrinter()
            printer.setOutputFormat(Qt.QPrinter.PdfFormat)
            printer.setOrientation(Qt.QPrinter.Landscape)
            printer.setOutputFileName(fileName)
            printer.setCreator('TaurusPlot')
            self.print_(printer)

    def exportPrint(self):
        '''Launches a QPrintDialog for printing the plot'''
        printer = Qt.QPrinter(Qt.QPrinter.HighResolution)
        printer.setOutputFileName('taurusplot.ps')
        printer.setCreator('TaurusPlot')
        printer.setOrientation(Qt.QPrinter.Landscape)
        printer.setColorMode(Qt.QPrinter.Color)
        docName = str(self.title().text())
        if docName:
            docName.replace('\n', ' -- ')
            printer.setDocName(docName)
        dialog = Qt.QPrintDialog(printer)
        if dialog.exec_():
            filter = Qwt5.QwtPlotPrintFilter()
            if (Qt.QPrinter.GrayScale == printer.colorMode()):
                filter.setOptions(Qwt5.QwtPlotPrintFilter.PrintAll
                                  & ~Qwt5.QwtPlotPrintFilter.PrintBackground
                                  | Qwt5.QwtPlotPrintFilter.PrintFrameWithScales)
            self.print_(printer, filter)

    def exportAscii(self, curves=None):
        '''Opens a dialog for exporting curves to ASCII files.

        :param curves:  (sequence<str>) the curves curves that will be
                        exportable. if None given, all curves are offered for
                        export.
        '''
        self.curves_lock.acquire()
        try:
            if curves is None:
                curves = self.getCurveNamesSorted()
            frozendata = {}
            for k in curves:
                frozendata[k] = self.getCurveData(k)
        finally:
            self.curves_lock.release()
        klass = getattr(self, 'exportDlgClass', None)
        if klass is None:
            from taurus.qt.qtgui.panel import QDataExportDialog
            klass = QDataExportDialog
        dialog = klass(parent=self, datadict=frozendata,
                       sortedNames=curves)
        dialog.setXIsTime(self.getXIsTime())
        return dialog.exec_()

    def importAscii(self, filenames=None, xcol=None, **kwargs):
        '''imports curves from ASCII files. It uses :meth:numpy.loadtxt
        The data in the file(s) must be formatted in columns, with possibly a
        header and/or commented lines. Each column in a file will be imported as
        an independent RawData curve (except for the column whose index is
        passed in xcol)

        :param filenames: (sequence<str> or None) the names of the files to be read. If
                          None passed, the user will be allowed to select them
                          from a dialog. (default=None)

        :param xcol: (int or None) index of the column (starting at 0)
                     containing the abscissas data. If None passed, the abcissa
                     is generated as indexes starting from 0.

        :param `**kwargs`: Other keyword arguments can be passed to this method,
                           which will be passed to :meth:`numpy.loadtxt` when
                           reading each file. Accepted keywords are:

                         - dtype=<type 'float'>
                         - comments='#'
                         - delimiter=None
                         - converters=None
                         - skiprows=0
                         - usecols=None
                         - unpack=False

        .. seealso:: :meth:`numpy.loadtxt`
        '''
        if filenames is None:
            filenames, _ = compat.getOpenFileNames(
                self, 'Choose input files', '', 'Ascii file (*)')
        if not filenames:
            return False
        rawdata = {}
        for fname in filenames:
            fname = str(fname)
            if self.xIsTime and xcol is not None:
                converters = kwargs.get('converters', {})
                converters[xcol] = isodatestr2float
                kwargs['converters'] = converters
            M = numpy.loadtxt(fname, **kwargs)
            if len(M.shape) == 1:
                # make sure we are dealing with a 2D matrix even if it is just
                # a colum
                M = M.reshape(M.size, 1)
            if xcol is None:
                rawdata["x"] = None
            else:
                rawdata["x"] = M[:, xcol]

            for col in range(M.shape[1]):
                if col == xcol:
                    continue  # ignore the xcol (it has already been set)
                rawdata["y"] = M[:, col]
                rawdata["title"] = "%s[%i]" % (os.path.basename(fname), col)
                self.attachRawData(copy.deepcopy(rawdata))

    def showDataImportDlg(self):
        '''Launches the data import dialog. This dialog lets the user manage
        which attributes are attached to the plot (using
        :class:`TaurusModelChooser`) and also to generate raw data or import it
        from files
        '''
        if self.DataImportDlg is None:
            from taurus.qt.qtgui.panel import TaurusModelChooser
            self.DataImportDlg = Qt.QDialog(self)
            self.DataImportDlg.setWindowTitle(
                "%s - Import Data" % (str(self.windowTitle())))
            self.DataImportDlg.modelChooser = TaurusModelChooser(
                selectables=[taurus.core.taurusbasetypes.TaurusElementType.Attribute])
            from taurus.qt.qtgui.panel import QRawDataWidget
            self.DataImportDlg.rawDataChooser = QRawDataWidget()

            tabs = Qt.QTabWidget()
            tabs.addTab(self.DataImportDlg.modelChooser, "&Attributes")
            tabs.addTab(self.DataImportDlg.rawDataChooser, "&Raw Data")
            mainlayout = Qt.QVBoxLayout(self.DataImportDlg)
            mainlayout.addWidget(tabs)

            self.DataImportDlg.modelChooser.updateModels.connect(self.setModel)
            self.DataImportDlg.rawDataChooser.ReadFromFiles.connect(self.readFromFiles)
            self.DataImportDlg.rawDataChooser.AddCurve.connect(self.attachRawData)

        models_and_display = [(m, self.getCurveTitle(
            m.split('|')[-1])) for m in self._modelNames]

        self.DataImportDlg.modelChooser.setListedModels(models_and_display)
        self.DataImportDlg.show()

    def readFromFiles(self, xcol, skiprows):
        '''helper slot. Calls self.importAscii(xcol=xcol, skiprows=skiprows )
        See meth:`importAscii`'''
        self.importAscii(xcol=xcol, skiprows=skiprows)

    def isXDynScaleSupported(self):
        '''Whether this widget offers xDynScale-related options. Useful for
        showing-hiding them in menus and dialogs

        :return: (bool)

        .. seealso:: :meth:`setXDynScaleSupported`, :meth:`getXDynScale`
        '''
        return self._xDynScaleSupported

    def setXDynScaleSupported(self, supported):
        '''Whether this widget should offer xDynScale-related options in menus
        and dialogs.

        :param supported: (bool) if True, the options related to xDynScale will
                          be shown

        .. seealso:: :meth:`isXDynScaleSupported`, :meth:`getXDynScale`'''
        self._xDynScaleSupported = False

    def setXDynScale(self, enabled=True):
        '''it enables/disables the Dynamic scaling feature (also known as
        Fixed-range X scale, or "auto-scroll mode"). The Dynamic scaling
        consists in ensuring that:

        - the range (=max-min) is always constant
        - the latest point plotted is always within range.

        :param enabled: (bool) if True, the Dynamic scaling is enabled for the
                        X axis. Otherwise it is disabled. (Default=True)

        .. seealso:: :meth:`getXDynScale`, :meth:`setXDynScaleSupported`'''
        self._xDynScale = enabled

    def getXDynScale(self):
        '''Whether the current X scale is in Dynamic scaling mode

        :return: (bool)

        .. seealso:: :meth:`setXDynScale`, meth:`isXDynScaleSupported`
        '''
        return self._xDynScale

    def setCurvesYAxis(self, curvesNamesList, axis):
        """Change the Y axis of the given curves to the given axis.

        :param curvesNamesList: (list<str>) the names of the curves whose Y axis
                                is to be changed
        :param axis: (Qwt5.QwtPlot.Axis) the axis
        """
        if not Qwt5.QwtPlot.axisValid(axis):
            raise ValueError("TaurusPlot::setCurvesYAxis. Invalid axis ID: " + \
                repr(axis))
        self.curves_lock.acquire()
        try:
            for curveName in curvesNamesList:
                curve = self.curves.get(curveName)
                curve.setYAxis(axis)
                curve._maxPeakMarker.setYAxis(axis)
                curve._minPeakMarker.setYAxis(axis)
                self.showCurve(curve, True)
        finally:
            self.curves_lock.release()

        # disable the other axis if no curves are assigned to it
        self.autoShowYAxes()
        # change the axis of the picked marker if needed
        if self._pickedCurveName in curvesNamesList:
            self._pickedMarker.setYAxis(axis)

        self.CurvesYAxisChanged.emit(curvesNamesList, axis)

        self.replot()

    def autoShowYAxes(self):
        """shows/hides Y1 and Y2 depending of whether there are curves
        associated to them. Also takes care of changing the zoomer if needed"""
        self.curves_lock.acquire()
        try:
            # get a list of *unique* axes with visible curves attached
            axes = list(
                set([curve.yAxis() for curve in self.curves.values() if curve.isVisible()]))

            n = len(axes)
            if n == 0:
                self.enableAxis(Qwt5.QwtPlot.yLeft, False)
                self.enableAxis(Qwt5.QwtPlot.yRight, False)
            elif n == 1:
                for axis in [Qwt5.QwtPlot.yLeft, Qwt5.QwtPlot.yRight]:
                    self.enableAxis(axis, (axis == axes[0]))
                # enable the zoom of the axis that has contents
                self.toggleZoomer(axes[0])
            else:
                self.enableAxis(Qwt5.QwtPlot.yLeft, True)
                self.enableAxis(Qwt5.QwtPlot.yRight, True)
        finally:
            self.curves_lock.release()

    def pickDataPoint(self, pos, scope=20, showMarker=True, targetCurveNames=None):
        '''Finds the pyxel-wise closest data point to the given position. The
        valid search space is constrained by the scope and targetCurveNames
        parameters.

        :param pos: (Qt.QPoint or Qt.QPolygon) the position around which to look
                    for a data point. The position should be passed as a
                    Qt.QPoint (if a Qt.QPolygon is given, the first point of the
                    polygon is used). The position is expected in pixel units,
                    with (0,0) being the top-left corner of the plot
                    canvas.

        :param scope: (int) defines the area around the given position to be
                      considered when searching for data points. A data point is
                      considered within scope if its manhattan distance to
                      position (in pixels) is less than the value of the scope
                      parameter. (default=20)

        :param showMarker: (bool) If True, a marker will be put on the picked
                           data point. (default=True)

        :param targetCurveNames: (sequence<str>) the names of the curves to be
                                 searched. If None passed, all curves will be
                                 searched

        :return: (tuple<Qt.QPointF,str,int> or tuple<None,None,None>) if a point
                 was picked within the scope, it returns a tuple containing the
                 picked point (as a Qt.QPointF), the curve name and the index of
                 the picked point in the curve data. If no point was found
                 within the scope, it returns None,None,None
        '''
        if isinstance(pos, Qt.QPolygon):
            pos = pos.first()
        scopeRect = Qt.QRect(0, 0, scope, scope)
        scopeRect.moveCenter(pos)
        mindist = scope
        picked = None
        pickedCurveName = None
        pickedIndex = None
        self.curves_lock.acquire()
        try:
            if targetCurveNames is None:
                targetCurveNames = self.curves.keys()
            for name in targetCurveNames:
                curve = self.curves.get(name, None)
                if curve is None:
                    self.error("Curve '%s' not found" % name)
                if not curve.isVisible():
                    continue
                data = curve.data()
                for i in range(data.size()):
                    point = Qt.QPoint(self.transform(curve.xAxis(), data.x(
                        i)), self.transform(curve.yAxis(), data.y(i)))
                    if scopeRect.contains(point):
                        dist = (pos - point).manhattanLength()
                        if dist < mindist:
                            mindist = dist
                            picked = Qt.QPointF(data.x(i), data.y(i))
                            pickedCurveName = name
                            pickedIndex = i
                            pickedAxes = curve.xAxis(), curve.yAxis()
                            _displayValue = getattr(curve, 'owner', curve
                                                    ).displayValue
        finally:
            self.curves_lock.release()

        if showMarker and picked is not None:
            self._pickedMarker.detach()
            self._pickedMarker.setValue(picked)
            self._pickedMarker.setAxis(*pickedAxes)
            self._pickedMarker.attach(self)
            self._pickedCurveName = pickedCurveName
            self._pickedMarker.pickedIndex = pickedIndex
            pickedCurveTitle = self.getCurveTitle(pickedCurveName)
            self.replot()
            label = self._pickedMarker.label()
            display_y = _displayValue(picked.y())
            if self.getXIsTime():
                infotxt = "'%s'[%i]:\n\t (t=%s, y=%s)" % (
                    pickedCurveTitle, pickedIndex,
                    datetime.fromtimestamp(picked.x()).ctime(), display_y )
            else:
                infotxt = "'%s'[%i]:\n\t (x=%.5g, y=%s)" % (
                    pickedCurveTitle, pickedIndex, picked.x(), display_y )
            label.setText(infotxt)
            fits = label.textSize().width() < self.size().width()
            if fits:
                self._pickedMarker.setLabel(Qwt5.QwtText(label))
                self._pickedMarker.alignLabel()
                self.replot()
            else:
                popup = Qt.QWidget(self, Qt.Qt.Popup)
                popup.setLayout(Qt.QVBoxLayout())
                # @todo: make the widget background semitransparent green!
                popup.layout().addWidget(Qt.QLabel(infotxt))
                popup.setWindowOpacity(self._pickedMarker.labelOpacity)
                popup.show()
                popup.move(self.pos().x() -
                           popup.size().width(), self.pos().y())
                popup.move(self.pos())
                Qt.QTimer.singleShot(5000, popup.hide)

        return picked, pickedCurveName, pickedIndex

    def toggleDataInspectorMode(self, enable=None):
        ''' Enables/Disables the Inspector Mode. When "Inspector Mode" is
        enabled, the zoomer is disabled and clicking on the canvas triggers a
        search of a nearby data point using pickDataPoint (the cursor changes to
        indicate the mode).

        :param enable: (bool or None) If True, it enables the Inspector Mode. If
                       False, it disables it. If None passed, it toggles the
                       mode.

        :return: (bool) whether the inspector mode has been enabled (True) or
                 disabled (False)
        '''
        if enable is None:
            enable = not(self._inspectorMode)

        self._pointPicker.setEnabled(enable)  # enables/disables the picker
        self._zoomer.setEnabled(self._allowZoomers and not(
            enable))  # disables/enables the zoomers

        if enable:
            cursor = Qt.Qt.WhatsThisCursor
        else:
            cursor = Qt.Qt.CrossCursor
            self._pickedMarker.detach()  # clears previous marker
            self.replot()

        self.canvas().setCursor(cursor)
        self._inspectorMode = enable

        return self._inspectorMode

    def onCurveStatsAction(self):
        '''
        slot for the curveStatsAction. Allows the user to select a range and
        then shows curve statistics on that range.
        '''
        if getattr(self, '_curveStatsDialog', None) is None:
            from taurus.qt.qtgui.qwt5 import CurveStatsDialog
            self._curveStatsDialog = CurveStatsDialog(self)
            self._curveStatsDialog.closed.connect(self._onCurveStatsDialogClosed)
            self._curveStatsDialog.finished.connect(self._onCurveStatsDialogClosed)
        elif not self._curveStatsDialog.isVisible():
            self._curveStatsDialog.refreshCurves()
        # it will be reenabed by _onCurveStatsDialogClosed
        self._curveStatsAction.setEnabled(False)
        self._curveStatsDialog.show()

    def _onCurveStatsDialogClosed(self, *args):
        '''slot called when the Curve Stats dialog is closed'''
        self._curveStatsAction.setEnabled(True)

    def selectXRegion(self, axis=Qwt5.QwtPlot.xBottom, callback=None):
        '''Changes the input mode to allow the user to select a region of the X axis

        :param axis: (Qwt5.QwtPlot.xBottom or Qwt5.QwtPlot.xTop) on which the
                     region will be defined (Default=Qwt5.QwtPlot.xBottom)
        :param callback: (method) a function that will be called when the user
                        finishes selecting the region. If None passed (default)
                        nothing is done
        '''
        self.__xRegionCallback = callback
        self._xRegionPicker.setAxis(axis, Qwt5.QwtPlot.yLeft)
        self._beginXRegionMode()

    def _onXRegionEvent(self, pos):
        '''slot called when the _xRegionPicker picks a point'''
        if self.__xRegionEnd is not None:
            self.debug('Ignoring xRegionEvent. Reason: not-reset region')
            return
        x = pos.x()
        if self.__xRegionStart is None:
            self.__xRegionStart = x
            self.__xRegionStartMarker.setXValue(x)
            self.__xRegionStartMarker.attach(self)
            self.replot()
        else:
            self.__xRegionEnd = x
            self.__xRegionEndMarker.setXValue(x)
            self.__xRegionEndMarker.attach(self)

            xmin, xmax = self.__xRegionStart, self.__xRegionEnd
            if xmin > xmax:
                xmin, xmax = xmax, xmin

            self.__xRegionCallback((xmin, xmax))

            self.replot()
            self._endXRegionMode()

    def _beginXRegionMode(self):
        '''pre-region selection tasks'''
        self.__xRegionStart = None
        self.__xRegionEnd = None
        self.__xRegionStartMarker = Qwt5.QwtPlotMarker()
        self.__xRegionStartMarker.setLineStyle(Qwt5.QwtPlotMarker.VLine)
        self.__xRegionStartMarker.setLinePen(Qt.QPen(Qt.Qt.green, 2))
        self.__xRegionEndMarker = Qwt5.QwtPlotMarker()
        self.__xRegionEndMarker.setLineStyle(Qwt5.QwtPlotMarker.VLine)
        self.__xRegionEndMarker.setLinePen(Qt.QPen(Qt.Qt.green, 2))

        self._zoomer.setEnabled(False)  # disables the zoomers
        self.canvas().setCursor(Qt.Qt.SplitHCursor)
        self._xRegionPicker.setEnabled(True)

    def _endXRegionMode(self):
        '''post-region selection tasks'''
        self._xRegionPicker.setEnabled(False)
        self.canvas().setCursor(Qt.Qt.CrossCursor)
        self._zoomer.setEnabled(self._allowZoomers)
        self.__xRegionStartMarker.detach()
        self.__xRegionEndMarker.detach()
        self.replot()

    def getCurveStats(self, limits=None, curveNames=None):
        '''Shows a dialog containing descriptive statistics on curves

        :param limits: (None or tuple<float,float>) tuple containing (min,max) limits.
                       Points of the curve whose abscisa value is outside of
                       these limits are ignored. If None is passed, the limit is not enforced
        :param curveNames: (seq<str>) sequence of curve names for which
                           statistics are requested. If None passed (default), all curves are
                           considered

        :return: (dict) Returns a dictionary whose keys are the curve names and
                        whose values are the dictionaries returned by
                        :meth:`TaurusCurve.getStats`
        '''
        if limits is not None and limits[0] is None and limits[1] is None:
            limits = None
        if curveNames is None:
            curveNames = self.getCurveNamesSorted()

        stats = {}
        self.curves_lock.acquire()
        try:
            for name in curveNames:
                curve = self.curves.get(name, None)
                stats[name] = curve.getStats(limits=limits)
                stats[name]['title'] = str(curve.title().text())
        finally:
            self.curves_lock.release()
        return stats

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # QT property definition
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    #-~-~-~-~-~-~-~-~-~-~-~-~
    # grid properties
    #-~-~-~-~-~-~-~-~-~-~-~-~

    @Qt.pyqtSlot('QColor')
    def setGridColor(self, color):
        '''Changes the color of the plot grid and refreshes the plot

        :param color:(Qt.QColor) the new color for the grid
        '''
        self._gridPen.setColor(color)
        self._grid.setPen(self._gridPen)
        self.replot()

    def getGridColor(self):
        '''Returns the color of the plot grid

        :return: (Qt.QColor)
        '''
        return self._gridPen.color()

    def resetGridColor(self):
        '''equivalent to self.setGridColor(Qt.Qt.gray)'''
        self.setGridColor(Qt.Qt.gray)

    @Qt.pyqtSlot(int)
    def setGridWidth(self, width):
        '''Changes the width of the plot grid lines and refreshes the plot

        :param width: (int) with in pixels for the grid lines
        '''
        self._gridPen.setWidth(width)
        self._grid.setPen(self._gridPen)
        self.replot()

    def getGridWidth(self):
        '''Returns the width of the grid lines

        :return: (int) with of the gridlines (in pixels)
        '''
        return self._gridPen.width()

    def resetGridWidth(self):
        '''equivalent to self.setGridWidth(1)'''
        self.setGridWidth(1)

    #-~-~-~-~-~-~-~-~-~-~-~-~
    # model properties
    #-~-~-~-~-~-~-~-~-~-~-~-~
    def _splitModel(self, modelNames):
        '''convert str to list if needed (commas and whitespace are considered as separators)'''
        if isinstance(modelNames, string_types):
            modelNames = str(modelNames).replace(',', ' ')
            modelNames = modelNames.split()
        return modelNames

    def _lowerIfInsensitive(self, modelNames):
        """filter a model name list converting to lowercase the names belonging
         to case-insensitive schemes"""
        models = []
        for m in modelNames:
            scheme = getSchemeFromName(m)
            # scan is not a scheme, but a "legacy" way in which Sardana plots
            # the scan data comming from the door; as Tango scheme it is
            # case insensitive
            if scheme == "scan" or not taurus.Factory(scheme).caseSensitive:
                models.append(str(m).lower())
            else:
                models.append(str(m))
        return models

    @Qt.pyqtSlot('QStringList')
    def setModel(self, modelNames):
        '''sets the models of the Tango attributes that should be displayed in
        this TaurusPlot.

        :param modelNames: (sequence<str> or str) the names of the models to be
                           plotted. For convenience, strings are also accepted
                           (instead of a sequence of strings), in which case the
                           string will be internally converted to a sequence by
                           splitting it on whitespace.

        .. seealso:: :meth:`addModels`, :meth:`removeModels`
        '''
        if modelNames is None:
            modelNames = []
        modelNames = self._splitModel(modelNames)
        self._modelNames = self._lowerIfInsensitive(modelNames)
        self.updateCurves(self._modelNames)
        self.modelChanged.emit()
        # update the modelchooser list
        if self.DataImportDlg is not None:
            self.DataImportDlg.modelChooser.setListedModels(self._modelNames)

    def getModel(self):
        '''returns the list of model names.

        :return: (CaselessList<str>)

        .. seealso:: :meth:`setModel`
        '''
        return self._modelNames

    def resetModel(self):
        '''equivalent to setModel([])'''
        self.setModel([])

    @Qt.pyqtSlot('QStringList')
    def addModels(self, modelNames):
        '''Adds models to the existing ones:

        :param modelNames:  (sequence<str>) the names of the models to be added
                           to the plot.

        .. seealso:: :meth:`setModels`, :meth:`removeModels`
        '''
        modelNames = self._lowerIfInsensitive(self._splitModel(modelNames))
        modelNames = [str(m) for m in modelNames if m not in self._modelNames]
        self.setModel(self._modelNames + modelNames)

    @Qt.pyqtSlot('QStringList')
    def removeModels(self, modelNames):
        '''Removes models from those already in the plot.

        :param modelNames:  (sequence<str>) the names of the models to be added
                           to the plot.

        .. seealso:: :meth:`setModels`, :meth:`addModels`
        '''
        modelNames = self._lowerIfInsensitive(self._splitModel(modelNames))
        for name in modelNames:
            try:
                self._modelNames.remove(name)
            except:
                self.warning("'%s' not in model list" % name)
        self.setModel(self._modelNames)

    @Qt.pyqtSlot(bool)
    def setUseParentModel(self, yesno):
        '''Sets whether the TaurusCurves of this plot should use the plot's parent model

        :param yesno: (bool) if True, the curves in the plot will use the Plot's
                      parent model

        .. seealso:: :meth:`TaurusBaseComponent.setParentModel` '''
        if yesno:
            self.deprecated(dep='setUseParentModel(True)', rel="4.3.2",
                            alt='explicit models including the parent model')
        if yesno and self._designMode:
            Qt.QMessageBox.information(self, "UseParentModel usage note",
                                       "Using the UseParentModel feature may require you to call " +
                                       "recheckTaurusParent() manually for this widget after calling " +
                                       "setupUi in your code." +
                                       "See the documentation of TaurusBaseWidget.recheckTaurusParent()")

        self._useParentModel = yesno

        parent_widget = self.getParentTaurusComponent()
        if parent_widget:
            if yesno:
                parent_widget.modelChanged.connect(self.parentModelChanged)
            else:
                parent_widget.modelChanged.disconnect(self.parentModelChanged)

        self.curves_lock.acquire()
        try:
            for curve in self.curves.values():
                curve.setUseParentModel(yesno)
        finally:
            self.curves_lock.release()

    def getUseParentModel(self):
        '''See: :meth:`TaurusBaseComponent.getParentModel`'''
        return self._useParentModel

    def resetUseParentModel(self):
        '''equivalent to setUseParentModel(False)'''
        self.setUseParentModel(False)

    #-~-~-~-~-~-~-~-~-~-~-~-~
    # legend properties
    #-~-~-~-~-~-~-~-~-~-~-~-~

    @Qt.pyqtSlot(int)
    def setLegendPosition(self, pos):
        '''Specify the position of the legend relative to the plot

        :param pos: (Qwt5.QwtPlot.LegendPosition)

        .. seealso:: :meth:`Qwt5.QwtPlot.LegendPosition`
        '''
        if pos == 0:
            self._legendPos = Qwt5.QwtPlot.LeftLegend
        elif pos == 1:
            self._legendPos = Qwt5.QwtPlot.RightLegend
        elif pos == 2:
            self._legendPos = Qwt5.QwtPlot.BottomLegend
        elif pos == 3:
            self._legendPos = Qwt5.QwtPlot.TopLegend
        elif pos == 4:
            self._legendPos = Qwt5.QwtPlot.ExternalLegend

        l = self.legend()
        if l:
            self.insertLegend(l, self._legendPos)
        self.replot()

    def getLegendPosition(self):
        '''returns the current legend position

        :return: (Qwt5.QwtPlot.LegendPosition)
        '''
        if self._legendPos == Qwt5.QwtPlot.LeftLegend:
            return 0
        elif self._legendPos == Qwt5.QwtPlot.RightLegend:
            return 1
        elif self._legendPos == Qwt5.QwtPlot.BottomLegend:
            return 2
        elif self._legendPos == Qwt5.QwtPlot.TopLegend:
            return 3
        elif self._legendPos == Qwt5.QwtPlot.ExternalLegend:
            return 4

    def resetLegendPosition(self):
        '''equivalent to setLegendPosition(Qwt5.QwtPlot.RightLegend)'''
        self.setLegendPosition(Qwt5.QwtPlot.RightLegend)

    def setDefaultCurvesTitle(self, titletext):
        '''sets the default title to be used for curves attached to this plot
        (the title is used, for example in the legend). Note that this does not
        affect to already existing curves. If you want that, see setCurvesTitle.

        :param titletext: (str) the default text to be used for the titles of curves. It may contain any of the placeholders described in TaurusCurve.setTitleText

        .. seealso:: :meth:`setCurvesTitle`, :meth:`TaurusCurve.setTitleText`
        '''
        self._defaultCurvesTitle = titletext

    def getDefaultCurvesTitle(self):
        '''See setDefaultCurvesTitle'''
        return self._defaultCurvesTitle

    def resetDefaultCurvesTitle(self):
        '''resets the defaultCurvesTitle property to '<label>'

        .. seealso:: :meth:`setDefaultCurvesTitle`'''
        self.setDefaultCurvesTitle('<label>')

    def setCurvesTitle(self, titletext, curveNamesList=None):
        '''Changes the titles of current curves.

        :param titletext:      (str) string to use as title for the curves. It may
                               include placeholders as those defined in TaurusCurve.compileTitleText()
        :param curveNamesList: (sequence<str> or iterator<str>) names of the
                               curves to which the title will be changed (if None given , it will apply
                               to all the curves except the raw data ones)

        :return: (caselessDict<str,str>) dictionary with key=curvename and value=newtitle

        .. seealso:: :meth:`changeCurvesTitlesDialog`,
                     :meth:`setDefaultCurvesTitle`, :meth:`TaurusCurve.setTitleText`
        '''
        self.curves_lock.acquire()
        try:
            if curveNamesList is None:
                curveNamesList = [
                    n for n, c in self.curves.items() if not c.isRawData]
            newTitlesDict = CaselessDict()
            for curveName in curveNamesList:
                curve = self.curves.get(curveName)
                curve.setTitleText(titletext)
                newTitlesDict[curveName] = str(curve.title().text())
            self.updateLegend(self.legend())
            return newTitlesDict
        finally:
            self.curves_lock.release()

    def changeCurvesTitlesDialog(self, curveNamesList=None):
        '''Shows a dialog to set the curves titles (it will change the current
        curves titles and the default curves titles)

        :param curveNamesList: (sequence<str> or iterator<str>) names of the
                               curves to which the title will be changed (if
                               None given , it will apply to all the curves
                               except the raw data ones and it will also be used
                               as default for newly created ones)

        :return: (caselessDict<str,str>) dictionary with key=curvename and value=newtitle

        .. seealso:: :meth:`setCurvesTitle`, :meth:`setDefaultCurvesTitle`
        '''
        newTitlesDict = None
        placeholders = ['<label>', '<model>', '<attr_name>', '<attr_fullname>',
                        '<dev_alias>', '<dev_name>', '<dev_fullname>', '<current_title>']
        try:
            current = placeholders.index(self._defaultCurvesTitle)
            items = placeholders
        except:
            current = len(placeholders)
            items = placeholders + [self._defaultCurvesTitle]

        msg = 'New text to be used for the curves.\nYou can use any of the following placeholders:\n%s' % ", ".join(
            placeholders)
        titletext, ok = Qt.QInputDialog.getItem(
            self, 'New Title for Curves', msg, items, current, True)
        if ok:
            titletext = str(titletext)
            if curveNamesList is None:
                self.setDefaultCurvesTitle(titletext)
            newTitlesDict = self.setCurvesTitle(
                titletext, curveNamesList=curveNamesList)
        return newTitlesDict

    #-~-~-~-~-~-~-~-~-~-~-~-~
    # Axes properties
    #-~-~-~-~-~-~-~-~-~-~-~-~
    def setXIsTime(self, enable, axis=Qwt5.QwtPlot.xBottom):
        '''Specifies whether we the plot is in Time or in normal mode (i.e,
        whether the abscissas should be interpreted as unix epoch values or not)

        :param enable:  (bool) if True, the plot will be in Time Mode
        :param axis: (Qwt5.QwtPlot.xBottom or Qwt5.QwtPlot.xTop) the X axis to
                     which this setting applies. (Default=Qwt5.QwtPlot.xBottom)

        .. seealso:: :ref:`TaurusPlot user manual <taurusplottime>`
        '''
        if enable:
            DateTimeScaleEngine.enableInAxis(self, axis)
            self._axesnames[Qwt5.QwtPlot.xBottom] = "T"
        else:
            DateTimeScaleEngine.disableInAxis(self, axis)
            self._axesnames[Qwt5.QwtPlot.xBottom] = "X"

        self._zoomer1.setXIsTime(enable)
        self._zoomer2.setXIsTime(enable)
        self._xIsTime = enable
        self.replot()

    def getXIsTime(self):
        '''Returns whether the X axis is in "Time mode"

        :return: (bool) True means the X axis is in Time mode, False

        .. seealso:: :meth:`setXIsTime`
        '''
        return self._xIsTime

    def resetXIsTime(self):
        '''equivalent to setXIsTime(False)'''
        self.setXIsTime(False)

    def setXAxisMode(self, x_axis_mode):
        """Required generic TaurusPlot API """
        self.setXIsTime(x_axis_mode.lower() == "t")

    @Qt.pyqtSlot(bool)
    def setAllowZoomers(self, allow):
        '''enable/disable the zoomers for the plot. (The zoomers provide zooming
        by selecting a region of the plot)

        :param allow: (bool) If True, zoomers are enabled, otherwise, they are disabled
        '''
        self._allowZoomers = allow
        self._zoomer.setEnabled(allow)

    @Qt.pyqtSlot(result=bool)
    def getAllowZoomers(self):
        '''Whether the Zoomers are enabled for this plot

        :return: (bool)

        .. seealso:: :meth:`setAllowZoomers`
        '''
        return self._allowZoomers

    @Qt.pyqtSlot()
    def resetAllowZoomers(self):
        '''same as setAllowZoomers(True)'''
        self.setAllowZoomers(True)

    @Qt.pyqtSlot(bool)
    def setPannerEnabled(self, enable):
        '''Specify whether the plot can be panned (i.e., dragged around to navigate it)

        :param enable: (bool) If True, panning is enabled, otherwise, it is disabled
        '''
        self._panner.setEnabled(enable)

    @Qt.pyqtSlot(result=bool)
    def isPannerEnabled(self):
        '''Whether the Panner is enabled for this plot

        :return: (bool)

        .. seealso:: :meth:`setPannerEnabled`
        '''
        return self._panner.isEnabled()

    @Qt.pyqtSlot()
    def resetPannerEnabled(self):
        '''same as setPannerEnabled(True)'''
        self.setPannerEnabled(True)

    @Qt.pyqtSlot(bool)
    def setMagnifierEnabled(self, enable):
        '''Specify whether the plot can be magnified (i.e. zoomed in and out
        with the mousewheel)

        :param enable: (bool) If True, magnifying is enabled, otherwise, it is disabled
        '''
        self._magnifier.setEnabled(enable)

    @Qt.pyqtSlot(result=bool)
    def isMagnifierEnabled(self):
        '''Whether the magnifier is enabled for this plot

        :return: (bool)

        .. seealso:: :meth:`setMagnifierEnabled`
        '''
        return self._magnifier.isEnabled()

    @Qt.pyqtSlot()
    def resetMagnifierEnabled(self):
        '''same as `setMagnifierEnabled(True)`'''
        self.setMagnifierEnabled(True)

    @Qt.pyqtSlot(bool)
    def setOptimizationEnabled(self, enable):
        '''Specify whether the plot should use paint optimizations

        :param enable: (bool) If True, optimization is enabled, otherwise, it is disabled
        '''
        # set the optimized flag for use with new curves
        self._optimizationEnabled = enable
        # make sure that already-created curves are also optimized
        try:
            for curveName in self.curves:
                curve = self.curves.get(str(curveName))
                curve.setPaintAttribute(curve.PaintFiltered, enable)
                curve.setPaintAttribute(curve.ClipPolygons, enable)
        finally:
            self.curves_lock.release()

    @Qt.pyqtSlot(result=bool)
    def isOptimizationEnabled(self):
        '''Whether painting optimization is enabled for this plot

        :return: (bool)
        '''
        return self._optimizationEnabled

    @Qt.pyqtSlot()
    def resetOptimizationEnabled(self):
        '''Equivalent to `setOptimizationEnabled(True)`
        '''
        self.setOptimizationEnabled(True)

    @classmethod
    def getQtDesignerPluginInfo(cls):
        """Returns pertinent information in order to be able to build a valid
        QtDesigner widget plugin

        :return: (dict) a map with pertinent designer information"""
        ret = TaurusBaseWidget.getQtDesignerPluginInfo()
        ret['module'] = 'taurus.qt.qtgui.qwt5'
        ret['group'] = 'Taurus Display'
        ret['icon'] = 'designer:qwtplot.png'
        return ret

    ##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    #                      Qt Properties                        #
    ##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

    gridColor = Qt.pyqtProperty(
        "QColor", getGridColor, setGridColor, resetGridColor)
    gridWidth = Qt.pyqtProperty(
        "int", getGridWidth, setGridWidth, resetGridWidth)
    legendPosition = Qt.pyqtProperty(
        "int", getLegendPosition, setLegendPosition, resetLegendPosition)
    model = Qt.pyqtProperty("QStringList", getModel, setModel, resetModel)
    useParentModel = Qt.pyqtProperty(
        "bool", getUseParentModel, setUseParentModel, resetUseParentModel)
    xIsTime = Qt.pyqtProperty("bool", getXIsTime, setXIsTime, resetXIsTime)
    allowZoomers = Qt.pyqtProperty(
        "bool", getAllowZoomers, setAllowZoomers, resetAllowZoomers)
    enablePanner = Qt.pyqtProperty(
        "bool", isPannerEnabled, setPannerEnabled, resetPannerEnabled)
    enableMagnifier = Qt.pyqtProperty(
        "bool", isMagnifierEnabled, setMagnifierEnabled, resetMagnifierEnabled)
    defaultCurvesTitle = Qt.pyqtProperty(
        "QString", getDefaultCurvesTitle, setDefaultCurvesTitle, resetDefaultCurvesTitle)
    enableOptimization = Qt.pyqtProperty(
        "bool", isOptimizationEnabled, setOptimizationEnabled, resetOptimizationEnabled)


def plot_main(models=(), config_file=None, x_axis_mode='n', demo=False,
              window_name='TaurusPlot (qwt)'):
    import sys
    from taurus.qt.qtgui.application import TaurusApplication

    app = TaurusApplication(cmd_line_parser=None, app_name="taurusplot(qwt)")

    w = TaurusPlot()

    w.setWindowTitle(window_name)

    w.setXIsTime(x_axis_mode.lower() == 't')

    if demo:
        models = list(models)
        models.extend(['eval:rand(100)', 'eval:0.5*sqrt(arange(100))'])

    if config_file is not None:
        w.loadConfigFile(config_file)

    if models:
        w.setModel(list(models))

    w.show()

    # if no models are passed, show the data import dialog
    if not models and config_file is None:
        w.showDataImportDlg()

    sys.exit(app.exec_())


if __name__ == "__main__":
    plot_main()
