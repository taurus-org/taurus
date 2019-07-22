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
taurustrend.py: Generic trend widget for Taurus
"""

from __future__ import print_function
from builtins import str

from datetime import datetime
import time
import numpy
import re
import gc
import weakref
from functools import partial
from taurus.external.qt import Qt, Qwt5

import taurus.core
from taurus.core.taurusattribute import TaurusAttribute
from taurus.core.util.containers import CaselessDict, CaselessList, ArrayBuffer
from taurus.qt.qtgui.base import TaurusBaseComponent
from taurus.qt.qtgui.qwt5 import TaurusPlot


__all__ = ["ScanTrendsSet", "TaurusTrend", "TaurusTrendsSet"]


def getArchivedTrendValues(*args, **kwargs):
    try:
        import PyTangoArchiving  # TODO: tango-centric
        return PyTangoArchiving.getArchivedTrendValues(*args, **kwargs)
    except:
        return []


def stripShape(s):
    '''
    returns a shape (a list) based on the given one. The returned shape will
    have all dimensions with length 1 removed, and it will be a list regardless
    of the input shape
    '''
    return [e for e in s if e != 1]


class TaurusTrendsSet(Qt.QObject, TaurusBaseComponent):
    """A collection of TaurusCurves generated from a Taurus Attribute.

    If the attribute is a scalar, The Trend Set consists of only one curve
    representing the evolution of the value of the attribute. If the attribute
    is a SPECTRUM, as many curves as the length of the spectrum are created,
    each representing the evolution of the value of a component of the array.

    When an event is received, all curves belonging to a TaurusTrendSet are updated.

    TaurusTrendSet objects can be considered as containers of (sorted) curves. As
    such, the curves contained by them can be accessed with item notation, as in
    the following example::

        attrname = 'a/b/c/d'       #consider this attribute is a SPECTRUM of 3 elements
        ts=TaurusTrendSet(attrname)
        ...                        # wait for a Taurus Event arriving so that the curves are created
        ncurves = len(ts)          #ncurves will be 3 (assuming the event already arrived)
        curve0 = ts[0]             #you can access the curve by index
        curve1 = ts['a/b/c/d[1]']  #and also by name


    Note that internally each curve is treated as a RawData curve (i.e., it is
    not aware of events by itself, but it relies on the TaurusTrendSet object to
    update its values)

    """
    consecutiveDroppedEventsWarning = 3  # number consecutive of dropped events before issuing a warning (-1 for disabling)
    # absolute number of dropped events before issuing a warning (-1 for
    # disabling)
    droppedEventsWarning = -1

    dataChanged = Qt.pyqtSignal('QString')

    def __init__(self, name, parent=None, curves=None):
        Qt.QObject.__init__(self, parent)
        self.call__init__(TaurusBaseComponent, self.__class__.__name__)
        self._xBuffer = None
        self._yBuffer = None
        self.forcedReadingTimer = None
        self.droppedEventsCount = 0
        self.consecutiveDroppedEventsCount = 0
        self.compiledTitle = name
        try:
            self._maxBufferSize = self.parent().getMaxDataBufferSize()
        except:
            self._maxBufferSize = TaurusTrend.DEFAULT_MAX_BUFFER_SIZE
        if curves is None:
            self._curves = {}
            self._orderedCurveNames = []
        else:
            self._curves = curves
            self._orderedCurveNames = list(curves)
        self._titleText = None
        self.setModel(name)

    def __getitem__(self, key):
        if isinstance(key, int):
            key = self._orderedCurveNames[key]
        return self._curves[key]

    def __len__(self):
        return len(self._orderedCurveNames)

    def __contains__(self, k):
        return self._curves.__contains__(k)

    def index(self, curveName):
        '''Returns the index in the trend for the given curve name. It gives an
        exception if the curve is not in the set.

        :param curveName: (str) the curvename to find

        :return: (int) The index associated to the given curve in the TrendSet
        '''
        return self.getCurveNames().index(curveName)

    def setTitleText(self, basetitle):
        '''Sets the title text of the trends this trendset. The name will be
        constructed by appending "[%i]" to the basetitle, where %i is the index
        position of the trend in the trendset. As a particular case, nothing is
        appended if the trendset consists of only one trend.

        :param basetitle: (str) The title text to use as a base for constructing
                          the title of each trend belonging to this trendset. It
                          may contain placeholders as those used in
                          :meth:`TaurusCurve.setTitleText`

        .. seealso:: :meth:`TaurusCurve.setTitleText`
        '''
        self._titleText = basetitle
        titles = self.compileTitles(basetitle)
        for t, (n, c) in zip(titles, self.getCurves()):
            c.setTitleText(t)

    def compileTitles(self, basetitle):
        '''Return a list of titles. Each title corresponds to a trend of the
        trendset (ordered). Substitution of known placeholders is performed.

        :param basetitle: (str) A string to be used as base title. It may
                          contain any of the following placeholders (which will
                          be substituted by their corresponding value):

            - <label> the attribute label (default)
            - <model> the model name
            - <attr_name> attribute name
            - <attr_fullname> full attribute name (for backwards compatibility, <attr_full_name> is also accepted)
            - <dev_alias> device alias
            - <dev_name> device name
            - <dev_fullname> full device name (for backwards compatibility, <dev_full_name> is also accepted)
            - <current_title> The current title
            - <trend_index> The index of the trend in the trendset
            - <[trend_index]> Same as: `"[<trend_index>]" if Ntrends>1 else ""`

        :return: (string_list) a list of title strings that correspond to the
                 list of trends in the set.

        .. seealso:: :meth:`compileBaseTitle`
        '''
        basetitle = self.compileBaseTitle(basetitle)
        ntrends = len(self._curves)
        if '<trend_index>' in basetitle:
            ret = [basetitle.replace('<trend_index>', "%i" % i)
                   for i in range(ntrends)]
        else:
            ret = [basetitle] * ntrends
        return ret

    def compileBaseTitle(self, basetitle):
        '''Return a base tile for a trend in whichs substitution of known
        placeholders has been performed.

        :param basetitle: (str) String on which the substitutions will be
                          performed. The following placeholders are supported:

            - <label> the attribute label (default)
            - <model> the model name
            - <attr_name> attribute name
            - <attr_fullname> full attribute name (for backwards compatibility, <attr_full_name> is also accepted)
            - <dev_alias> device alias
            - <dev_name> device name
            - <dev_fullname> full device name (for backwards compatibility, <dev_full_name> is also accepted)
            - <current_title> The current title
            - <[trend_index]> Same as: `"[<trend_index>]" if Ntrends>1 else ""`

        **Note** that <trend_index> itself is not substituted!

        :return: (str) the compiled base title.

        .. seealso:: :meth:`compileTitles`
        '''
        attr = self.getModelObj()
        basetitle = basetitle.replace('<current_title>', self._titleText)
        basetitle = basetitle.replace('<model>', self.getModel())
        if isinstance(attr, taurus.core.taurusattribute.TaurusAttribute):
            basetitle = basetitle.replace('<label>', attr.label or '---')
            basetitle = basetitle.replace(
                '<attr_name>', attr.getSimpleName() or '---')
            basetitle = basetitle.replace(
                '<attr_fullname>', attr.getFullName() or '---')
            basetitle = basetitle.replace(
                '<attr_full_name>', attr.getFullName() or '---')

        dev = attr.getParentObj()
        if dev is not None:
            basetitle = basetitle.replace(
                '<dev_alias>', dev.getSimpleName() or '---')
            basetitle = basetitle.replace(
                '<dev_name>', dev.getNormalName() or '---')
            basetitle = basetitle.replace(
                '<dev_fullname>', dev.getFullName() or '---')
            basetitle = basetitle.replace(
                '<dev_full_name>', dev.getFullName() or '---')

        if len(self._curves) == 1:
            basetitle = basetitle.replace('<[trend_index]>', '')
        else:
            basetitle = basetitle.replace('<[trend_index]>', '[<trend_index>]')

        self.compiledTitle = basetitle
        return basetitle

    def addCurve(self, name, curve):
        '''add a curve (with the given name) to the internal curves dictionary of this TaurusTrendSet

        :param name: (str) the name of the curve
        :param curve: (TaurusCurve) the curve object to be added
        '''
        # provide the curve with a weakref to the trendset (the owner)
        curve.owner = weakref.proxy(self)
        self._curves[name] = curve
        self._orderedCurveNames.append(name)

    def getCurves(self):
        '''returns an iterator of (curveName,curveObject) tuples associated to
        this TaurusTrendSet. The curves will always be returned in the order they
        were added to the set

        :return: (iterator<str,TaurusCurve>)
        '''
        return iter([(n, self._curves[n]) for n in self._orderedCurveNames])

    def getCurveNames(self):
        '''returns a list of the names of the curves associated to this
        TaurusTrendSet. The curve names will always be returned in the order they
        were added to the set

        :return: (list<str>) the names of the curves
        '''
        return self._orderedCurveNames

    def getModelClass(self):
        '''see :meth:`TaurusBaseComponent.getModelClass`'''
        return TaurusAttribute

    def registerDataChanged(self, listener, meth):
        '''see :meth:`TaurusBaseComponent.registerDataChanged`'''
        self.dataChanged.connect(meth)

    def unregisterDataChanged(self, listener, meth):
        '''see :meth:`TaurusBaseComponent.unregisterDataChanged`'''
        self.dataChanged.disconnect(meth)

    def _updateHistory(self, model, value):
        '''Update the history data buffers using the latest value from the event

        :param model: (str) the source of the event (needed to retrieve data from archiving)
        :param value: (TaurusAttrValue) the value from the event

        :return: (tuple<numpy.ndarray, numpy.ndarray>) Tuple of two arrays
                 containing the X data and Y data, respectively, from the
                 history buffers:
                 - The dtype of both arrays is "double".
                 - The X array will contain timestamps if the parent is in
                   XisTime mode, and a sequential event number otherwise.
                 - The Y array may be two-dimensional if the attribute value is
                   a spectrum

        **Example of return values:** Consider history of 10 events for a
        SPECTRUM attribute with dim_x=8. Then the return value will be (X,Y)
        where X.shape=(10,) and Y.shape=(10,8); X.dtype = Y.dtype = <dtype('float64')>
        '''
        attr = self.getModelObj()
        if value is not None:
            if attr.isNumeric():
                v = value.rvalue.magnitude  # TODO: check unit consistency
            else:
                v = value.rvalue
            if numpy.isscalar(v):
                ntrends = 1
            else:
                try:
                    v = float(v)
                    ntrends = 1
                except:
                    try:
                        # Trying with spectrums
                        ntrends = len(v)
                    except:
                        # Simply unreadable
                        value = None
                        ntrends = len(self._curves)
        else:
            ntrends = len(self._curves)

        if self._xBuffer is None:
            self._xBuffer = ArrayBuffer(numpy.zeros(
                min(128, self._maxBufferSize), dtype='d'), maxSize=self._maxBufferSize)
        if self._yBuffer is None:
            self._yBuffer = ArrayBuffer(numpy.zeros(
                (min(128, self._maxBufferSize), ntrends), dtype='d'), maxSize=self._maxBufferSize)
        if value is not None:
            if attr.isNumeric():
                v = value.rvalue.magnitude
            else:
                v = value.rvalue
            try:
                self._yBuffer.append(v)
            except Exception as e:
                self.warning('Problem updating history (%s=%s):%s',
                             model, v, e)
                value = None

        if self.parent().getXIsTime():
            # add the timestamp to the x buffer
            if value is not None:
                self._xBuffer.append(value.time.totime())
            # Adding archiving values
            if self.parent().getUseArchiving():
                # open a mysql connection for online trends or any not
                # autoscaled plots
                if self.parent().getXDynScale() or not self.parent().axisAutoScale(Qwt5.QwtPlot.xBottom):
                    try:
                        getArchivedTrendValues(self, model, insert=True)
                    except Exception as e:
                        import traceback
                        self.warning('%s: reading from archiving failed: %s' % (
                            datetime.now().isoformat('_'), traceback.format_exc()))
        elif value is not None:
            # add the event number to the x buffer
            try:
                self._xBuffer.append(1. + self._xBuffer[-1])
            except IndexError:  # this will happen when the x buffer is empty
                self._xBuffer.append(0)
        return self._xBuffer.contents(), self._yBuffer.contents()

    def clearTrends(self, replot=True):
        '''clears all stored data (buffers and copies of the curves data)

        :param replot: (bool) do a replot after clearing
        '''
        # clean previous curves
        for subname in self.getCurveNames():
            self.parent().detachRawData(subname)
        self._curves = {}
        self._orderedCurveNames = []
        # clean history Buffers
        self._xBuffer = None
        self._yBuffer = None
        # clean x,ydata
        self._xValues = None
        self._yValues = None
        # replot
        if replot:
            self.parent().replot()
        # Force immediate garbage collection (otherwise the buffered data
        # remains in memory)
        gc.collect()

    def handleEvent(self, evt_src, evt_type, evt_value):
        ''' processes Change (and Periodic) Taurus Events: updates the data of all
        curves in the set according to the value of the attribute.

        For documentation about the parameters of this method, see
        :meth:`TaurusBaseComponent.handleEvent`
        '''
        if evt_type == taurus.core.taurusbasetypes.TaurusEventType.Config:
            # self.setTitleText(self._titleText or
            # self.parent().getDefaultCurvesTitle()) #this did not work well
            # (it overwrites custom titles!)
            return
        else:
            if isinstance(evt_src, TaurusAttribute):
                model = evt_src
            else:
                model = self.getModelObj()
            if evt_type == taurus.core.taurusbasetypes.TaurusEventType.Error:
                self._onDroppedEvent(reason='Error event')
                if not self.parent().getUseArchiving():
                    return
                else:
                    value = None
            elif model is None:
                self._onDroppedEvent(reason='unknown model')
                if not self.parent().getUseArchiving():
                    return
                else:
                    value = None
            else:
                value = evt_value if isinstance(
                    evt_value, taurus.core.taurusbasetypes.TaurusAttrValue) else self.getModelValueObj()
                if value is None or value.rvalue is None:
                    self._onDroppedEvent(reason='invalid value')
                    if not self.parent().getUseArchiving():
                        return
                elif model.isNumeric():
                    if not hasattr(value.rvalue, 'magnitude'):
                        self._onDroppedEvent(reason='rvalue has no .magnitude')
                        return
                    else:
                        self._checkDataDimensions(value.rvalue.magnitude)
                else:
                    self._checkDataDimensions(value.rvalue)

        # get the data from the event
        try:
            self._xValues, self._yValues = self._updateHistory(
                model=model or self.getModel(), value=value)
        except Exception as e:
            self._onDroppedEvent(reason=str(e))
            raise

        # this was a good event, so we reset the consecutive dropped events
        # count
        self.consecutiveDroppedEventsCount = 0

        # assign xvalues and yvalues to each of the curves in self._curves
        for i, (n, c) in enumerate(self.getCurves()):
            c._xValues, c._yValues = self._xValues, self._yValues[:, i]
            c._updateMarkers()

        self.dataChanged.emit(str(self.getModel()))

    def _checkDataDimensions(self, value):
        '''
        Check that the data dimensions are consistent with what was plotted before
        '''
        if value is None:
            return len(self._curves)
        try:
            float(value)
            ntrends = 1
        except:
            ntrends = len(value)
        if ntrends != len(self._curves):
            # clean previous curves
            self.clearTrends(replot=False)
            # create as many curves as the dim_x of the given model and add
            # them to the TrendSet
            name = self.getModelName()
            rawdata = {'x': numpy.zeros(0), 'y': numpy.zeros(0)}
            for i in range(ntrends):
                subname = "%s[%i]" % (name, i)
                self.parent().attachRawData(rawdata, id=subname)
                self.addCurve(subname, self.parent().curves[subname])
            self.setTitleText(
                self._titleText or self.parent().getDefaultCurvesTitle())
            self.parent().autoShowYAxes()
        return ntrends

    def _onDroppedEvent(self, reason='Unknown'):
        '''inform the user about a dropped event

        :param reason: (str) The reason of the drop
        '''
        self.debug("Dropping event. Reason %s", reason)
        self.droppedEventsCount += 1
        self.consecutiveDroppedEventsCount += 1
        mustwarn = False
        if self.droppedEventsCount == self.droppedEventsWarning:
            mustwarn = True
            msg = ('At least %i events from model "%s" have been dropped. This attribute may have problems\n' +
                   'Future occurrences will be silently ignored') % (self.droppedEventsWarning, self.modelName)
            # disable the consecutive Dropped events warning (we do not want it
            # if we got this one)
            self.consecutiveDroppedEventsWarning = -1
        if self.consecutiveDroppedEventsCount == self.consecutiveDroppedEventsWarning:
            mustwarn = True
            msg = ('At least %i consecutive events from model "%s" have been dropped. This attribute may have problems\n' +
                   'Future occurrences will be silently ignored') % (self.consecutiveDroppedEventsWarning, self.modelName)
            # disable the consecutive Dropped events warning
            self.consecutiveDroppedEventsWarning = -1
        if mustwarn:
            self.warning(msg)
            p = self.parent()
            if p:
                c = p.canvas()
                msg2 = "Errors reading %s (%s)" % (
                    self._titleText, self.modelName)
                Qt.QToolTip.showText(c.mapToGlobal(c.pos()), msg2, c)
                #Qt.QMessageBox.warning(p, "Errors in %s"%self._titleText, msg, Qt.QMessageBox.Ok)

    def isReadOnly(self):
        return True

    def setMaxDataBufferSize(self, maxSize):
        '''sets the maximum number of events that are stored in the internal
        buffers of the trend. Note that this sets the maximum amount of memory
        used by the data in this trend set to:

            ~(1+ntrends)*2*8*maxSize bytes

        (the data is stored as float64, and two copies of it are kept: one at
        the x and y buffers and another at the QwtPlotCurve.data)

        :param maxSize: (int) the maximum limit
        '''
        if self._xBuffer is not None:
            self._xBuffer.setMaxSize(maxSize)
        if self._yBuffer is not None:
            self._yBuffer.setMaxSize(maxSize)
        self._maxBufferSize = maxSize

    def maxDataBufferSize(self):
        return self._maxBufferSize

    def setForcedReadingPeriod(self, msec):
        '''
        Forces periodic reading of the subscribed attribute in order to show
        get new points even if no events are received. It will create fake events as
        needed with the read value. Note that setting a period may yield
        unwanted results when the x axis is set to show event numbers
        (xIsTime==False)since there is no way of distinguishing the real from
        the fake events.

        :param msec: (int) period in milliseconds. Use msec<0 to stop the
                     forced periodic reading
        '''
        if self.forcedReadingTimer is None:
            self.forcedReadingTimer = Qt.QTimer()
            self.forcedReadingTimer.timeout.connect(self.forceReading)

        # stop the timer and remove the __ONLY_OWN_EVENTS filter
        self.forcedReadingTimer.stop()
        filters = self.getEventFilters()
        if self.__ONLY_OWN_EVENTS in filters:
            filters.remove(self.__ONLY_OWN_EVENTS)
            self.setEventFilters(filters)

        # if msec is positive, set the filter and start
        if msec >= 0:
            self.insertEventFilter(self.__ONLY_OWN_EVENTS)
            self.forcedReadingTimer.start(msec)

    def getForcedReadingPeriod(self):
        if self.forcedReadingTimer is None or not self.forcedReadingTimer.isActive():
            return -1
        else:
            return self.forcedReadingTimer.interval()

    def __ONLY_OWN_EVENTS(self, s, t, v):
        '''An event filter that rejects all events except those that originate from this object'''
        if s is self:
            return s, t, v
        else:
            return None

    def forceReading(self, cache=False):
        '''Forces a read of the attribute and generates a fake event with it.
        By default it ignores the cache

        :param cache: (bool) set to True to do cache'd reading (by default is False)
        '''
        vobj = self.getModelValueObj(cache=False)
        self.fireEvent(
            self, taurus.core.taurusbasetypes.TaurusEventType.Periodic, vobj)


class ScanTrendsSet(TaurusTrendsSet):
    """
    An specialized TaurusTrendSet that instead of being updated via events, it
    receives new data directly via a PyQt slot

    receives signal containing record data from a scan.

    When an event is received, all curves belonging to a TaurusTrendSet are updated.

    Note that internally each curve is treated as a RawData curve (i.e., it is
    not aware of events by itself, but it relies on the ScanTrendSet object to
    update its values)

    .. seealso:: :class:`TaurusTrendSet`
    """
    DEFAULT_X_DATA_KEY = 'point_nb'

    dataChanged = Qt.pyqtSignal('QString')

    def __init__(self, name, parent=None, autoClear=True, xDataKey=None):
        '''
        Creator

        :param autoClear: (bool) If True, (default) :meth:`clearTrends` will be
                          called every time a "data_desc" packet is received
        :param xDataKey:  (str) a the name of the data to be used for the x value
                          in the scan curves (e.g., a motor name, a counter
                          name,...) By default, "point_nb" is used. The special key
                          "__SCAN_TREND_INDEX__" will associate an internal integer index
                          that starts in 0, increases on each record_data received
                          and is reset by :meth:`clearTrends`.
        '''
        TaurusTrendsSet.__init__(self, None, parent=parent, curves=None)
        self._xDataKey = xDataKey
        self._autoXDataKey = xDataKey
        self._autoClear = autoClear
        #self._usePointNumber = usePointNumber
        self._currentpoint = -1
        self._plotablesFilter = lambda x: True
        self.__datadesc = None
        self._endMarkers = []
        self.setModel(name)
        self._endMacroMarkerEnabled = True

    def setAutoClear(self, enable):
        self._autoClear = enable

    def setXDataKey(self, key):
        if key == self._xDataKey:
            return
        self._xDataKey = key
        self.clearTrends()

    def setEndMacroMarkerEnabled(self, enable):
        '''Sets whether a marker should be put at the end of each macro or not

        :param enabled: (bool)
        '''
        self._endMacroMarkerEnabled = enable

    def scanDataReceived(self, packet):
        '''
        packet is a dict with {type:str, "data":object} and the accepted types are: data_desc, record_data, record_end
        and the data objects are: seq<ColumnDesc.Todict()>, record.data dict and dict , respectively
        '''
        if packet is None:
            self.debug('Ignoring empty scan data packet')
            return
        pkgid, packet = packet
        pcktype = packet.get("type", "__UNKNOWN_PCK_TYPE__")
        if pcktype == "data_desc":
            self._dataDescReceived(packet["data"])
        elif pcktype == "record_data":
            self._scanLineReceived(packet["data"])
        elif pcktype == "record_end":
            self._addEndMarker()
        else:
            self.debug("Ignoring packet of type %s" % repr(pcktype))

    def clearTrends(self, replot=True):
        '''
        Reimplemented from :meth:`TaurusTrendsSet.clearTrends`.

        .. note:: If the autoClear property is True for this trend set, this method is
                  called automatically every time a data_desc package is received.
        '''
        # clean the datadesc
        self.__datadesc = None
        # clean markers
        for m in self._endMarkers:
            m.detach()
        self._endMarkers = []
        # reset current point counter
        self._currentpoint = -1
        # call the superclass
        TaurusTrendsSet.clearTrends(self, replot=replot)

    def onPlotablesFilterChanged(self, flt):
        '''
        slot to be called whenever the plotables filter is changed. It will call
        :meth:`clearTrends` if flt is None

        :param flt:  (list<method>)
        '''
        if flt is None:
            self.clearTrends()
        else:
            self.setPlotablesFilter(flt)

    def setPlotablesFilter(self, flt):
        self._plotablesFilter = flt

    def _addEndMarker(self):
        if self._endMacroMarkerEnabled:
            m = Qwt5.QwtPlotMarker()
            m.setLineStyle(m.VLine)
            m.setXValue(self._currentpoint)
            m.attach(self.parent())
            pen = Qt.QPen(Qt.Qt.DashLine)
            pen.setWidth(2)
            m.setLinePen(pen)
            self._endMarkers.append(m)
            self._currentpoint -= 1
            self.parent().replot()

    def getDataDesc(self):
        return self.__datadesc

    def _dataDescReceived(self, datadesc):
        '''prepares the plot according to the info in the datadesc dictionary'''
        # backwards compatibility (datadesc was a list and now is a dict)
        if isinstance(datadesc, list):
            datadesc = {'column_desc': datadesc}
        # clear existing curves if required
        if self._autoClear:
            self.clearTrends()
        # decide which data to use for x
        if self._xDataKey is None or self._xDataKey == "<mov>":  # @todo use a standard key for <mov> and <idx>
            try:
                self._autoXDataKey = datadesc['ref_moveables'][0]
            except (KeyError, IndexError):
                self._autoXDataKey = self.DEFAULT_X_DATA_KEY
        elif self._xDataKey == "<idx>":
            self._autoXDataKey = 'point_nb'
        else:
            self._autoXDataKey = self._xDataKey
        # set the x axis
        columndesc = datadesc.get('column_desc', [])
        xinfo = {'min_value': None, 'max_value': None}
        for e in columndesc:
            if e['label'] == self._autoXDataKey:
                xinfo = e
                break
        self.parent().setAxisTitle(self.parent().xBottom, self._autoXDataKey)
        xmin, xmax = xinfo.get('min_value'), xinfo.get('max_value')
        self.parent().setXDynScale(False)
        if xmin is None or xmax is None:
            # autoscale if any limit is unknown
            self.parent().setAxisAutoScale(self.parent().xBottom)
        else:
            self.parent().setAxisScale(self.parent().xBottom, xmin, xmax)
        # create trends
        self._createTrends(datadesc["column_desc"])

    def _createTrends(self, datadesc):
        '''
        Creates the needed curves using the information from the DataDesc

        For now, it only creates trends for those "columns" containing scalar values

        :param datadesc: (seq<dict>) each dict is a ColumnDesc.toDict()
        '''
        self.__datadesc = datadesc
        # create as many curves as columns containing scalars
        rawdata = {'x': numpy.zeros(0), 'y': numpy.zeros(0)}
        self.parent()._curvePens.setCurrentIndex(0)
        for dd in self.__datadesc:
            if len(stripShape(dd['shape'])) == 0:  # an scalar
                name = dd["name"]
                if name not in self._curves and self._plotablesFilter(name) and name != self._autoXDataKey:
                    rawdata["title"] = dd["label"]
                    curve = self.parent().attachRawData(rawdata, id=name)
                    prop = curve.getAppearanceProperties()
                    prop.sColor = prop.lColor
                    prop.sStyle = Qwt5.QwtSymbol.Ellipse
                    prop.sSize = 7
                    prop.lWidth = 1
                    prop.lStyle = Qt.Qt.DotLine
                    curve.setAppearanceProperties(prop)
                    self.addCurve(name, curve)
        self.parent().autoShowYAxes()
        self.dataChanged.emit(str(self.getModel()))

    def _scanLineReceived(self, recordData):
        '''Receives a recordData dictionary and updates the curves associated to it

        .. seealso:: <Sardana>/MacroServer/scan/scandata.py:Record.data

        '''
        # obtain the x value
        if self._autoXDataKey == "__SCAN_TREND_INDEX__":
            self._currentpoint += 1
        else:
            try:
                self._currentpoint = recordData[self._autoXDataKey]
            except KeyError:
                self.warning(
                    'Cannot find data "%s" in the current scan record. Ignoring' % self._autoXDataKey)
                return
            if not numpy.isscalar(self._currentpoint):
                self.warning('Data for "%s" is of type "%s". Cannot use it for the X values. Ignoring' % (
                    self._autoXDataKey, type(self._currentpoint)))
                return

        # If autoclear is True, we use buffers
        if self._autoClear:
            curvenames = self.getCurveNames()
            if self._xBuffer is None:
                self._xBuffer = ArrayBuffer(numpy.zeros(
                    128, dtype='d'), maxSize=self.maxDataBufferSize())
            if self._yBuffer is None:
                self._yBuffer = ArrayBuffer(numpy.zeros(
                    (128, len(curvenames)), dtype='d'), maxSize=self.maxDataBufferSize())
            # x values
            self._xBuffer.append(self._currentpoint)
            # y values
            y = numpy.array([recordData.get(n, numpy.NaN) for n in curvenames])
            self._yBuffer.append(y)

            self._xValues, self._yValues = self._xBuffer.contents(), self._yBuffer.contents()

            # assign xvalues and yvalues to each of the curves in self._curves
            for i, (n, c) in enumerate(self.getCurves()):
                c._xValues = self._xValues
                # this is an assigment by reference
                c._yValues = self._yValues[:, i]
                c._updateMarkers()

        # if autoclear is False we have to work directly with each curve (and
        # cannot buffer)
        else:
            for n, v in recordData.items():
                c = self._curves.get(n, None)
                if c is None:
                    continue
                c._xValues = numpy.append(c._xValues, self._currentpoint)
                c._yValues = numpy.append(c._yValues, v)
                c._updateMarkers()

        self.dataChanged.emit(str(self.getModel()))

    def connectWithQDoor(self, qdoor):
        '''connects this ScanTrendsSet to a QDoor

        :param qdoor: (QDoor or str) either a QDoor instance or the QDoor name
        '''
        from sardana.taurus.qt.qtcore.tango.sardana.macroserver import QDoor
        if not isinstance(qdoor, QDoor):
            qdoor = taurus.Device(qdoor)
        qdoor.recordDataUpdated.connect(self.scanDataReceived)

    def disconnectQDoor(self, qdoor):
        '''connects this ScanTrendsSet to a QDoor

        :param qdoor: (QDoor or str) either a QDoor instance or the QDoor name
        '''
        from sardana.taurus.qt.qtcore.tango.sardana.macroserver import QDoor
        if not isinstance(qdoor, QDoor):
            qdoor = taurus.Device(qdoor)
        qdoor.recordDataUpdated.disconnect(self.scanDataReceived)

    def getModel(self):
        return self.__model

    def setModel(self, model):
        self.__model = model


class TaurusTrend(TaurusPlot):
    '''
    A :class:`TaurusPlot` -derived widget specialised in plotting trends (i.e.,
    evolution of parameters).

    .. image:: /_static/taurustrend01.png
       :align: center

    TaurusTrend inherits all the features from TaurusPlot (zooming,
    exporting/importing, data inspection,...) and also provides some specific
    features (e.g. fixed-range X scale mode and Archiving support).

    For an overview of the features from an user point of view, see the
    :ref:`TaurusTrend User's Interface Guide <trend_ui>`.

    You can also see some code that exemplifies the use of TaurusTrend in :ref:`the
    TaurusTrend coding examples <examples_taurustrend>`

    Note: if you pass a model that is a 1D attribute (instead of a
    scalar), TaurusTrend will interpret it as a collection of scalar values and
    will plot a separate trend line for each.

    Note 2: As an special case, you can pass a model of the type
    scan://doorname. This will link the TaurusTrend to the given Taurus door and will
    listen to it for scan record events, which will be plotted.



    .. seealso:: :class:`TaurusPlot`,
                 :ref:`TaurusTrend User's Interface Guide <trend_ui>`,
                 :ref:`The TaurusTrend coding examples <examples_taurustrend>`
    '''

    DEFAULT_MAX_BUFFER_SIZE = 65536  # (=2**16, i.e., 64K events))

    dataChanged = Qt.pyqtSignal('QString')

    def __init__(self, parent=None, designMode=False):
        TaurusPlot.__init__(self, parent=parent, designMode=designMode)
        self.trendSets = CaselessDict()
        self._supportedConfigVersions = ["ttc-1"]
        self._xDynScaleSupported = True
        self._useArchiving = False
        self._usePollingBuffer = False
        self.setDefaultCurvesTitle('<label><[trend_index]>')
        self._maxDataBufferSize = self.DEFAULT_MAX_BUFFER_SIZE
        self.__qdoorname = None
        self._scansXDataKey = None
        self.__initActions()
        self._startingTime = time.time()
        self._archivingWarningLocked = False
        self._forcedReadingPeriod = None
        self._replotTimer = None
        self.setXIsTime(True)
        # Use a rotated labels x timescale by default
        rotation = -45
        alignment = self.getDefaultAxisLabelsAlignment(self.xBottom, rotation)
        self.setAxisLabelRotation(self.xBottom, rotation)
        self.setAxisLabelAlignment(self.xBottom, alignment)
        # use dynamic scale by default
        self.setXDynScale(True)
        self._scrollStep = 0.2

    def __initActions(self):
        '''Create TaurusTrend actions'''
        self._useArchivingAction = Qt.QAction("Use Archiver", None)
        self._useArchivingAction.setCheckable(True)
        self._useArchivingAction.setChecked(self.getUseArchiving())
        self._useArchivingAction.toggled.connect(self._onUseArchivingAction)
        self._usePollingBufferAction = Qt.QAction("Use Polling Buffer", None)
        self._usePollingBufferAction.setCheckable(True)
        self._usePollingBufferAction.setChecked(self.getUsePollingBuffer())
        self._usePollingBufferAction.toggled.connect(self.setUsePollingBuffer)
        self._setForcedReadingPeriodAction = Qt.QAction(
            "Set forced reading period...", None)
        self._setForcedReadingPeriodAction.triggered.connect(
            partial(self.setForcedReadingPeriod, msec=None, tsetnames=None))
        self._clearBuffersAction = Qt.QAction("Clear Buffers", None)
        self._clearBuffersAction.triggered.connect(self.clearBuffers)
        self._setMaxBufferSizeAction = Qt.QAction(
            "Change buffers size...", None)
        self._setMaxBufferSizeAction.triggered.connect(
            partial(self.setMaxDataBufferSize, maxSize=None))
        self._autoClearOnScanAction = Qt.QAction(
            "Auto-clear on new scans", None)
        self._autoClearOnScanAction.setCheckable(True)
        self._autoClearOnScanAction.setChecked(True)
        self._autoClearOnScanAction.toggled.connect(self._onAutoClearOnScanAction)

    def isTimerNeeded(self, checkMinimized=True):
        '''checks if it makes sense to activate the replot timer.
        The following conditions must be met:

        - the replot timer must exist
        - the area of the plot must be non-zero
        - at least one trendset must be attached
        - the plot should be visible
        - the plot should not be minimized (unless checkMinimized=False)

        :param checkMinimized: (bool) whether to include the check of minimized (True by default)

        :return: (bool)
        '''
        return self._replotTimer is not None and \
            not self.size().isEmpty() and \
            bool(len(self.trendSets)) and \
            self.isVisible() and \
            not (checkMinimized and self.isMinimized())

    def showEvent(self, event):
        '''reimplemented from :meth:`TaurusPlot.showEvent` so that
        the replot timer is active only when needed'''
        TaurusPlot.showEvent(self, event)
        if self.isTimerNeeded(checkMinimized=False):
            self.debug('(re)starting the timer (in showEvent)')
            self._replotTimer.start()
            # call a replot now (since it may not have been done while hidden)
            self.doReplot()

    def hideEvent(self, event):
        '''reimplemented from :meth:`TaurusPlot.showEvent` so that
        the replot timer is active only when needed'''
        TaurusPlot.hideEvent(self, event)
        if self._replotTimer is not None:
            self.debug('stopping the timer (in hideEvent)')
            self._replotTimer.stop()

    def resizeEvent(self, event):
        '''reimplemented from :meth:`TaurusPlot.resizeEvent` so that
        the replot timer is active only when needed'''
        TaurusPlot.resizeEvent(self, event)
        if event.oldSize().isEmpty():  # do further checks only if previous size was 0
            if self.isTimerNeeded():
                self.debug('(re)starting the timer (in resizeEvent)')
                self._replotTimer.start()
            else:
                if self._replotTimer is not None:
                    self.debug('stopping the timer (in resizeEvent)')
                    self._replotTimer.stop()

    def setXIsTime(self, enable, axis=Qwt5.QwtPlot.xBottom):
        '''Reimplemented from :meth:`TaurusPlot.setXIsTime`'''
        # set a reasonable scale
        if enable:
            self.setAxisScale(axis, self._startingTime - 60,
                              self._startingTime)  # Set a range of 1 min
        else:
            self.setAxisScale(axis, 0, 10)  # Set a range of 10 events
            w = self.axisWidget(axis)
            try:
                # disconnect the previous axis
                w.scaleDivChanged.disconnect(self.rescheduleReplot)
            except TypeError:
                pass  # ignore exception if signal was not previously connected
        # enable/disable the archiving action
        self._useArchivingAction.setEnabled(enable)
        # call the parent class method
        # the axis is changed here
        TaurusPlot.setXIsTime(self, enable, axis=axis)
        # set the replot timer if needed
        if enable and not self._designMode:
            if self._replotTimer is None:
                self._dirtyPlot = True
                self._replotTimer = Qt.QTimer()
                self._replotTimer.timeout.connect(self.doReplot)
            self.rescheduleReplot(axis)
            self.axisWidget(axis).scaleDivChanged.connect(self.rescheduleReplot)  # connects the new axis
        else:
            self._replotTimer = None

    def onScanPlotablesFilterChanged(self, flt, scanname=None):
        if scanname is None:
            if self.__qdoorname is None:
                return
            scanname = "scan://%s" % self.__qdoorname
        tset = self.getTrendSet(scanname)
        tset.onPlotablesFilterChanged(flt)

    def setScansAutoClear(self, enable):
        '''
        sets whether the trend sets associated to scans should be reset every
        time a data_desc packet is received from the door.

        :param enable: (bool)

        .. seealso:: :meth:`setScanDoor` and :class:`ScanTrendsSet`
        '''
        self._autoClearOnScanAction.setChecked(enable)

    def _onAutoClearOnScanAction(self, enable, scanname=None):
        self.info('Autoclear on Scan set to %s', bool(enable))
        if scanname is None:
            if self.__qdoorname is None:
                return
            scanname = "scan://%s" % self.__qdoorname
        tset = self.getTrendSet(scanname)
        tset.setAutoClear(enable)

    def getScansAutoClear(self):
        return self._autoClearOnScanAction.isChecked()

    def setScansUsePointNumber(self, enable):
        '''
        .. note:: This method is deprecated. Please use :meth:`setScansXDataKey` instead

        sets whether the trend sets associated to scans should use the point
        number from the data record for the abscissas (default).

        :param enable: (bool)

        '''
        self.info(
            'setScansUsePointNumber is deprecated. Please use setScansXDataKey instead')
        if enable:
            key = 'point_nb'
        else:
            key = '__SCAN_TREND_INDEX__'
        self.setScansXDataKey(key)

    def setScansXDataKey(self, key, scanname=None):
        '''
        selects the source for the data to be used as abscissas in the scan plot.

        :param key: (str) a string corresponding to a data label for data
                    present in the scan. Alternatively, "__SCAN_TREND_INDEX__"
                    can be used for an internal integer count of scan records

        :param scanname: (str or None) name of the model for the scan. If None,
                         the default scan is selected

        .. seealso:: the constructor of :class:`ScanTrendsSet`
        '''
        if scanname is None:
            if self.__qdoorname is None:
                return
            scanname = "scan://%s" % self.__qdoorname
        tset = self.getTrendSet(scanname)
        tset.setXDataKey(key)
        if key is None:
            key = ''
        self.setAxisTitle(self.xBottom, key)
        self._scansXDataKey = key

    def setScanDoor(self, qdoorname):
        '''
        sets the door to which TaurusTrend will listen for scans.
        This removes any previous scan set using this method, but respects scans set with setModel
        '''
        if self.__qdoorname is not None:
            self.removeModels(["scan://%s" % self.__qdoorname])
        self.addModels(["scan://%s" % qdoorname])
        self.__qdoorname = qdoorname

    def clearScan(self, scanname):
        '''resets the curves associated to the given scan

        :param scanname: (str) the scan model name (e.g. "scan://a/b/c")
        '''
        tset = self.getTrendSet(scanname)
        tset.clearTrends()

    def clearBuffers(self):
        '''clears the buffers of existing trend sets (note that this does
        not remove the models, it simply removes all stored data)'''
        self.curves_lock.acquire()
        try:
            for ts in self.trendSets.values():
                ts.clearTrends(replot=False)
        finally:
            self.curves_lock.release()
        self.replot()

    def updateCurves(self, names):
        '''Defines the curves that need to be plotted. For a TaurusTrend, the
        models can refer to:

        - scalar data: they are to be plotted in a trend
        - on-dimensional data: each element of the spectrum is considered
          independently

        Note that passing an attribute for X values makes no sense in this case

        Internally, every curve is grouped in a TaurusTrendSet. For each SPECTRUM
        attribute, a TrendSet is created, containing as many curves as the
        lenght of the spectrum For eacha SCALAR attribute, a TrendSet containing
        just one curve is created.

        :param names: (sequence<str>) a sequence of model names

        .. note:: Adding/removing a model will add/remove a whole set. No
                  sub-set adding/removing is allowed.
                  Still, each curve will be independent regarding its
                  properties, and can be hidden/shown independently.

        .. seealso:: :meth:`TaurusPlot.updateCurves`
        '''
        self.curves_lock.acquire()
        try:
            # For it to work properly, 'names' must be a CaselessList, just as
            # self.trendSets is a CaselessDict
            if not isinstance(names, CaselessList):
                names = CaselessList(names)
            del_sets = [name for name in self.trendSets.keys()
                        if name not in names]

            # if all trends were removed, reset the color palette
            if len(del_sets) == len(self.trendSets):
                self._curvePens.setCurrentIndex(0)

            # update new/existing trendsets
            for name in names:
                name = str(name)
                if "|" in name:
                    raise ValueError(
                        'composed ("X|Y") models are not supported by TaurusTrend')
                # create a new TrendSet if not already there
                if name not in self.trendSets:
                    # check if the model name is of scan type and provides a
                    # door
                    matchScan = re.search(r"scan:\/\/(.*)", name)
                    if matchScan:
                        tset = ScanTrendsSet(name, parent=self, autoClear=self.getScansAutoClear(
                        ), xDataKey=self._scansXDataKey)
                        self.__qdoorname = matchScan.group(
                            1)  # the name of the door
                        tset.connectWithQDoor(self.__qdoorname)
                    else:
                        tset = TaurusTrendsSet(name, parent=self)
                        if self._forcedReadingPeriod is not None:
                            tset.setForcedReadingPeriod(
                                self._forcedReadingPeriod)
                    self.trendSets[name] = tset
                    tset.registerDataChanged(self, self.curveDataChanged)
            # Trend Sets to be removed
            for name in del_sets:
                name = str(name)
                tset = self.trendSets.pop(name)
                tset.setModel(None)
                tset.unregisterDataChanged(self, self.curveDataChanged)
                tset.forcedReadingTimer = None
                tset.clearTrends(replot=False)
                matchScan = re.search(r"scan:\/\/(.*)", name)
                if matchScan:
                    olddoorname = matchScan.group(1)
                    tset.disconnectQDoor(olddoorname)
            if del_sets:
                self.autoShowYAxes()

            # legend
            self.showLegend(len(self.curves) > 1, forever=False)
            self.replot()

            # keep the replotting timer active only if there is something to
            # refresh
            if self.isTimerNeeded():
                self.debug('(re)starting the timer (in updateCurves)')
                self._replotTimer.start()
            else:
                if self._replotTimer is not None:
                    self.debug('stopping the timer (in updateCurves)')
                    self._replotTimer.stop()

        finally:
            self.curves_lock.release()

    def getTrendSetNames(self):
        '''returns the names of all TrendSets attached to this TaurusTrend.

        :return: (list<str>) a copy of self.trendSets.keys()
        '''
        return self.getModel()

    def getTrendSet(self, name):
        '''gets a trend set object by name.

        **Important**: Note that the TrendSet object is not thread safe.
        Therefore, if you access it you must do it protected by the
        TaurusTrend.curves_lock reentrant lock.

        :param name: (str) the trend set name

        :return: (TaurusTrendSet) the trend set object corresponding to name
        '''
        self.curves_lock.acquire()
        try:
            ret = self.trendSets.get(str(name))
        finally:
            self.curves_lock.release()
        return ret

    def getCurveTitle(self, name, index=None):
        '''reimplemented from :class:`TaurusPlot`.
        Returns the title of a curve from a trendset

        :param name: (str) The name of the trendset. If the name is not a known
                     trendset name and index is None, we will try with tsetname and
                     index obtained from parsing the given name (assuming the
                     format '<tsetname>[<index>]').
        :param index: (int or None) the index of the curve in the trend set.
                      If None is passed, it returns the base title of the trendset

        :return: (str) the title
        '''
        self.curves_lock.acquire()
        try:
            tset = self.trendSets.get(name)
            if tset is None:  # name not found...
                if index is None:  # maybe name was actually a curve name including the index?
                    match = re.match(r'^(.*)\[([0-9]+)\]$', name)
                    if match:
                        name, index = match.groups()
                        index = int(index)
                        # recursive call with parsed tsetname and index
                        return self.getCurveTitle(name, index=index)
                return None
            if index is None:
                if len(tset) == 1:
                    index = 0
                else:
                    return tset.compiledTitle
            title = str(tset[index].title().text())
        finally:
            self.curves_lock.release()
        return title

    def changeCurvesTitlesDialog(self, curveNamesList=None):
        '''Shows a dialog to set the curves titles (it will change the current
        curves titles and the default curves titles)

        :param curveNamesList: (string_sequence or string_iterator) names of the
                               curves to which the title will be changed (if
                               None given , it will apply to all the TrendsSets
                               and it will also be used as default for newly
                               created ones)

        :return: (caselessDict<str,str> or None) The return value will be
                 `None` if `curveNamesList` is None. Otherwise it will be a
                 dictionary with key=curvename and value=newtitle.

        .. seealso:: :meth:`setCurvesTitle`, :meth:`setDefaultCurvesTitle`
        '''
        newTitlesDict = None

        placeholders = ['<label>', '<model>', '<attr_name>', '<attr_fullname>',
                        '<dev_alias>', '<dev_name>', '<dev_fullname>', '<current_title>',
                        '<trend_index>', '<[trend_index]>']
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
                self.setTrendSetsTitles(titletext)
            else:
                self.curves_lock.acquire()
                try:
                    newTitlesDict = CaselessDict()
                    for curveName in curveNamesList:
                        curvetitle = titletext
                        for ts in self.trendSets.values():
                            if curveName in ts:
                                curvetitle = ts.compileBaseTitle(curvetitle)
                                curvetitle = curvetitle.replace(
                                    '<trend_index>', "%i" % ts.index(curveName))
                                break
                        curve = self.curves.get(curveName)
                        curve.setTitleText(curvetitle)
                        newTitlesDict[curveName] = curve.title().text()
                    self.updateLegend(self.legend())
                    return newTitlesDict
                finally:
                    self.curves_lock.release()
        return newTitlesDict

    def setTrendSetsTitles(self, basetitle, setNames=None):
        '''Calls setTitleText(basetitle) for each Trend Set set in setNames

        :param basetitle: (str) the base title
        :param setNames: (sequence<str> or iterator<str>) names of the sets to be changed

        See: TaurusTrendsSet.setTitleText
        '''
        self.curves_lock.acquire()
        try:
            if setNames is None:
                setNames = self.getModel()
            for tname in setNames:
                if tname in self.trendSets:
                    self.trendSets[tname].setTitleText(basetitle)
        finally:
            self.curves_lock.release()
        self.updateLegend(self.legend())

    @Qt.pyqtSlot('QString', name='dataChanged')
    def curveDataChanged(self, name):
        '''slot that is called whenever a curve emits a dataChanged signal

        :emits: "dataChanged(const QString &)"

        :param name: (str) curve name
        '''
        name = str(name)
        self.curves_lock.acquire()
        try:
            curve = None
            for n, curve in self.trendSets[name].getCurves():
                curve.setData(curve._xValues, curve._yValues)
            # self._zoomer.setZoomBase()
            # keep the scale width constant, but translate it to get the last
            # value
            if curve is not None and self.getXDynScale() and len(curve._xValues) > 0:
                sdiv = self.axisScaleDiv(self.xBottom)
                currmin, currmax = sdiv.lowerBound(), sdiv.upperBound()
                datamax = curve._xValues[-1]
                if datamax > currmax or datamax < currmin:
                    minstep = datamax - currmax  # the new scale max must be above the latest point
                    maxstep = datamax - currmin  # the new scale min must be below the latest point
                    step = min(max(self.getXAxisRange() *
                                   self._scrollStep, minstep), maxstep)
                    self.setAxisScale(
                        self.xBottom, currmin + step, currmax + step)
        finally:
            self.curves_lock.release()
        self.dataChanged.emit(str(name))
        if not self.xIsTime:
            self.replot()
        else:
            self._dirtyPlot = True

    def doReplot(self):
        '''calls :meth:`replot` only if there is new data to be plotted'''
        #self.trace('Replotting? %s',self._dirtyPlot)
        if self._dirtyPlot:
            self.replot()
            self._dirtyPlot = False

    def rescheduleReplot(self, axis=Qwt5.QwtPlot.xBottom, width=1080):
        '''calculates the replotting frequency based on the time axis range.
        It assumes that it is unnecessary to replot with a period less than the
        time per pixel.

        :param axis: (Qwt5.QwtPlot.Axis) the axis to which it should associate
        :param width: (int) the approx canvas width (in pixels). The exact value
                      could be obtained from the widget, but an order of
                      magnitude approximation is usually ok (and cheaper). The
                      default value is 1080 (HD ready!)

        '''
        if self.xIsTime:
            sdiv = self.axisScaleDiv(axis)
            currmin, currmax = sdiv.lowerBound(), sdiv.upperBound()
            plot_refresh = int(1000 * (currmax - currmin) / width)
            # enforce limits
            plot_refresh = min((max((plot_refresh, 250)), 1800000))
            if self._replotTimer.interval() != plot_refresh:
                # note: calling QTimer.setInterval() very often seems to eventually trigger some bug
                #      that stops the timer from emitting the timeout signal. We avoid this by
                #      calling setInterval only when really needed.
                self._replotTimer.setInterval(plot_refresh)
                self.debug('New replot period is %1.2f seconds',
                           (plot_refresh / 1000.))

        else:
            self.warning(
                'rescheduleReplot() called but X axis is not in time mode')

    def setPaused(self, paused=True):
        '''Pauses itself and other listeners (e.g. the trendsets) depending on it

        .. seealso:: :meth:`TaurusBaseComponent.setPaused`
        '''
        for ts in self.trendSets.values():
            ts.setPaused(paused)
        self._isPaused = paused

    def createConfig(self, tsnames=None, **kwargs):
        '''Returns a pickable dictionary containing all relevant information
        about the current plot.
        For Taurus attributes it stores the attribute name and the curve properties
        For raw data curves, it stores the data as well.

        Hint: The following code allows you to serialize the configuration
        dictionary as a string (which you can store as a QSetting, or as a Taurus
        Attribute)::

            import pickle
            c = pickle.dumps(taurusplot.createConfig())  #c is a string that can be stored

        :param names:  (sequence<str>) a sequence of TrendSet names for which the
                       configuration will be stored (all by default).

        :return: (dict) configurations (which can be loaded with applyConfig)
        '''
        configdict = TaurusPlot.createConfig(
            self, curvenames=None)  # use the superclass configdict as a starting point
        if tsnames is None:
            tsnames = CaselessList(self.getModel())
        model = CaselessList([m for m in self.getModel() if m in tsnames])
        # overwrite the value created by TaurusPlot.createConfig()
        configdict["model"] = model
        # delete the TangoCurves key since it is meaningless in a TaurusTrend
        configdict.pop("TangoCurves")
        tsetsdict = CaselessDict()
        rawdatadict = CaselessDict(configdict["RawData"])
        miscdict = CaselessDict(configdict["Misc"])
        miscdict["ForcedReadingPeriod"] = self.getForcedReadingPeriod()
        miscdict["MaxBufferSize"] = self.getMaxDataBufferSize()
        self.curves_lock.acquire()
        try:
            for tsname, ts in self.trendSets.items():
                if tsname in tsnames:
                    # store a dict containing just model names (key and value
                    # are the same)
                    tsetsdict[tsname] = tsname
                for cname in CaselessList(ts.getCurveNames()):
                    # clean the rawdatadict of rawdata curves that come from
                    # trendsets (but we keep the properties!)
                    rawdatadict.pop(cname)
        finally:
            self.curves_lock.release()
        configdict["TrendSets"] = tsetsdict
        configdict["RawData"] = rawdatadict
        configdict["Misc"] = miscdict
        return configdict

    def applyConfig(self, configdict, **kwargs):
        """applies the settings stored in a configdict to the current plot.

        :param configdict: (dict)

        .. seealso:: :meth:`createConfig`
        """
        if not self.checkConfigVersion(configdict):
            return
        # set the max Buffer data size (we do it before ataching the curves to
        # avoid useless reallocations of buffers)
        maxBufferSize = configdict["Misc"].get("MaxBufferSize")
        if maxBufferSize is not None:
            self.setMaxDataBufferSize(maxBufferSize)
        # attach the curves
        for rd in configdict["RawData"].values():
            self.attachRawData(rd)
        # for backwards compatibility, if the ordered list of models is not
        # stored, it uses the unsorted dict values
        models = configdict.get("model", list(configdict["TrendSets"].values()))
        self.addModels(models)
        for m in models:
            tset = self.trendSets[m]
            # a fake event to force generating the curves
            tset.fireEvent(
                None, taurus.core.taurusbasetypes.TaurusEventType.Change, None)
        # set curve properties
        self.setCurveAppearanceProperties(configdict["CurveProp"])
        self.updateLegend(force=True)
        # set the axes
        self.applyAxesConfig(configdict["Axes"])
        # set other misc configurations
        self.applyMiscConfig(configdict["Misc"])
        forcedreadingperiod = configdict["Misc"].get("ForcedReadingPeriod")
        if forcedreadingperiod is not None:
            self.setForcedReadingPeriod(forcedreadingperiod)

    @classmethod
    def getQtDesignerPluginInfo(cls):
        """Returns pertinent information in order to be able to build a valid
        QtDesigner widget plugin

        :return: (dict) a map with pertinent designer information"""
        return {
            'module': 'taurus.qt.qtgui.qwt5',
            'group': 'Taurus Display',
            'icon': 'designer:qwtplot.png',
            'container': False}

    def setEventFilters(self, filters=None, tsetnames=None, preqt=False):
        '''propagates a list of taurus filters to the trendsets given by tsetnames.
        See :meth:`TaurusBaseComponent.setEventFilters`
        '''
        if tsetnames is None:
            tsetnames = self.getModel()
        self.curves_lock.acquire()
        try:
            for name in tsetnames:
                self.trendSets[name].setEventFilters(filters, preqt=preqt)
        finally:
            self.curves_lock.release()

    def setUsePollingBuffer(self, enable):
        '''enables/disables looking up in the PollingBuffer for data

        :param enable: (bool) if True, PollingBuffer values will be used if available
        '''
        self._usePollingBuffer = enable
        self.replot()

    def getUsePollingBuffer(self):
        '''whether TaurusTrend is looking for data in the PollingBuffer

        :return: (bool)

        .. seealso:: :meth:`setUsePollingBuffer`
        '''
        return self._usePollingBuffer

    def resetUsePollingBuffer(self):
        '''Same as setUsePollingBuffer(True)'''
        self.setUsePollingBuffer(True)

    def setUseArchiving(self, enable):
        '''enables/disables looking up in the archiver for data stored before
        the Trend was started

        :param enable: (bool) if True, archiving values will be used if available
        '''
        if not self.getXIsTime():
            self.info('ignoring setUseArchiving. Reason: not in X time scale')
        self._useArchivingAction.setChecked(enable)

    def getUseArchiving(self):
        '''whether TaurusTrend is looking for data in the archiver when needed

        :return: (bool)

        .. seealso:: :meth:`setUseArchiving`
        '''
        return self._useArchiving

    def resetUseArchiving(self):
        '''Same as setUseArchiving(True)'''
        self.setUseArchiving(True)

    def _onUseArchivingAction(self, enable):
        '''slot being called when toggling the useArchiving action

        .. seealso:: :meth:`setUseArchiving`
        '''
        if enable:
            self._archivingWarningThresshold = self._startingTime - \
                600  # 10 min before the widget was created
            self.axisWidget(self.xBottom).scaleDivChanged.connect(self._scaleChangeWarning)
        else:
            self.axisWidget(self.xBottom).scaleDivChanged.disconnect(self._scaleChangeWarning)
            self._archivingWarningThresshold = None
        self._useArchiving = enable
        self.replot()

    def _scaleChangeWarning(self):
        '''slot that may be called when the x axis changes the scale'''
        sdiv = self.axisScaleDiv(self.xBottom)
        smin = sdiv.lowerBound()
        if smin < self._archivingWarningThresshold:
            self.showArchivingWarning()
            # lower the thresshold by twice the current range
            self._archivingWarningThresshold = smin - 2 * sdiv.range()

    def showArchivingWarning(self):
        '''shows a dialog warning of the potential isuues with
        archiving performance. It offers the user to disable archiving retrieval'''
        # stop the scale change notification temporally (to avoid duplicate
        # warnings)
        self.setUseArchiving(False)
        try:
            self.axisWidget(self.xBottom).scaleDivChanged.disconnect(
                self._scaleChangeWarning)
        except:
            self.warning('Failed to disconnect ScaleChangeWarning dialog')        

        # show a dialog
        dlg = Qt.QDialog(self)
        dlg.setModal(True)
        dlg.setLayout(Qt.QVBoxLayout())
        dlg.setWindowTitle('Archiving warning')
        msg = 'Archiving retrieval is enabled.\n' +\
              'Rescaling to previous date/times may cause performance loss.\n' +\
              '\nDisable archiving retrieval?\n'
        dlg.layout().addWidget(Qt.QLabel(msg))
        rememberCB = Qt.QCheckBox('Do not ask again')
        buttonbox = Qt.QDialogButtonBox()
        buttonbox.addButton(Qt.QPushButton(
            '&Keep enabled'), buttonbox.RejectRole)
        buttonbox.addButton(Qt.QPushButton('&Disable'), buttonbox.AcceptRole)
        dlg.layout().addWidget(buttonbox)
        buttonbox.accepted.connect(dlg.accept)
        buttonbox.rejected.connect(dlg.reject)
        dlg.layout().addWidget(rememberCB)
        dlg.exec_()
        # disable archiving if the user said so
        if dlg.result() == dlg.Accepted:
            self.setUseArchiving(False)
        # restore the scale change notification only if the user chose to keep
        # archiving AND did not want to disable warnings
        else:
            self.setUseArchiving(True)
            if not rememberCB.isChecked():
                self.axisWidget(self.xBottom).scaleDivChanged.connect(self._scaleChangeWarning)

    def setMaxDataBufferSize(self, maxSize=None):
        '''sets the maximum number of events that can be plotted in the trends

        :param maxSize: (int or None) the maximum limit. If None is passed,
                        the user is prompted for a value.

        .. seealso:: :meth:`TaurusTrendSet.setMaxDataBufferSize`
        '''
        if maxSize is None:
            maxSize = self._maxDataBufferSize
            try:  # API changed in QInputDialog since Qt4.4
                qgetint = Qt.QInputDialog.getInt
            except AttributeError:
                qgetint = Qt.QInputDialog.getInteger
            maxSize, ok = qgetint(self, 'New buffer data size',
                                  'Enter the number of points to be kept in memory for each curve',
                                  maxSize, 2, 10000000, 1000)
            if not ok:
                return

        choiceOnClear = None

        self.curves_lock.acquire()
        try:
            for n, ts in self.trendSets.items():
                try:
                    ts.setMaxDataBufferSize(maxSize)
                except ValueError:
                    if choiceOnClear is None:
                        choiceOnClear = Qt.QMessageBox.question(
                            self, "Clear buffers?", "Clear the curves that contain too many points for the selected buffer size?", Qt.QMessageBox.No | Qt.QMessageBox.Yes)
                    if choiceOnClear == Qt.QMessageBox.Yes:
                        ts.clearTrends(replot=False)
                        ts.setMaxDataBufferSize(maxSize)
        finally:
            self.curves_lock.release()
        self._maxDataBufferSize = maxSize

    def getMaxDataBufferSize(self):
        '''returns the maximum number of events that can be plotted in the trend

        :return: (int)
        '''
        return self._maxDataBufferSize

    def resetMaxDataBufferSize(self):
        '''Same as setMaxDataBufferSize(self.DEFAULT_MAX_BUFFER_SIZE)'''
        self.setMaxDataBufferSize(self.DEFAULT_MAX_BUFFER_SIZE)

    def _canvasContextMenu(self):
        ''' see :meth:`TaurusPlot._canvasContextMenu` '''
        menu = TaurusPlot._canvasContextMenu(self)
        menu.insertAction(self._setCurvesTitleAction, self._useArchivingAction)
        menu.insertAction(self._setCurvesTitleAction,
                          self._usePollingBufferAction)
        menu.insertAction(self._setCurvesTitleAction,
                          self._setForcedReadingPeriodAction)
        menu.insertAction(self._setCurvesTitleAction,
                          self._setMaxBufferSizeAction)
        menu.insertAction(self._setCurvesTitleAction, self._clearBuffersAction)
        if self.__qdoorname is not None:
            menu.insertAction(self._setCurvesTitleAction,
                              self._autoClearOnScanAction)
        return menu

    def _axisContextMenu(self, axis=None):
        ''' see :meth:`TaurusPlot._axisContextMenu` '''
        menu = TaurusPlot._axisContextMenu(self, axis=axis)
        if axis in (Qwt5.QwtPlot.xBottom, Qwt5.QwtPlot.xTop) and self.__qdoorname is not None:
            menu.addAction('Source of X values...',
                           self.onChangeXDataKeyAction)
        return menu

    def onChangeXDataKeyAction(self):
        options = ['[Auto Selection]', '[Internal Scan Index]']
        if self.__qdoorname is not None:
            scanname = "scan://%s" % self.__qdoorname
            tset = self.getTrendSet(scanname)
            datadesc = tset.getDataDesc()
            if datadesc is not None:
                for dd in datadesc:
                    if len(stripShape(dd['shape'])) == 0:  # an scalar
                        options.append(dd["label"])

        key, ok = Qt.QInputDialog.getItem(self, 'X data source selection',
                                          'Which data is to be used for the abscissas in scans?',
                                          options, 0, True)
        if ok:
            key = str(key)
            if key == options[0]:
                key = None
            elif key == options[1]:
                key = '__SCAN_TREND_INDEX__'
            self.setScansXDataKey(key, scanname)

    def setForcedReadingPeriod(self, msec=None, tsetnames=None):
        '''Sets the forced reading period for the trend sets given by tsetnames.

        :param msec: (int or None) period in milliseconds. If None passed, the user will be
                     prompted
        :param tsetnames: (seq<str> or None) names of the curves for which the forced
                          reading is set. If None passed, this will be set for all
                          present *and future* curves added to this trend

        .. seealso: :meth:`TaurusTrendSet.setForcedReadingPeriod`
        '''
        if msec is None:
            msec = self._forcedReadingPeriod
            try:  # API changed in QInputDialog since Qt4.4
                qgetint = Qt.QInputDialog.getInt
            except AttributeError:
                qgetint = Qt.QInputDialog.getInteger
            msec, ok = qgetint(self, 'New forced reading period',
                               'Enter the new period for forced reading (in ms).\n Enter "0" for disabling',
                               max(0, msec), 0, 604800000, 100)
            if not ok:
                return
            if msec == 0:
                msec = -1

        self._forcedReadingPeriod = msec

        if tsetnames is None:
            tsetnames = self.getModel()
        self.curves_lock.acquire()
        try:
            for name in tsetnames:
                self.trendSets[name].setForcedReadingPeriod(msec)
        finally:
            self.curves_lock.release()

    def getForcedReadingPeriod(self, tsetname=None):
        '''returns the forced reading period for the given trend (or the general period
        if None is given)

        :param tsetname: (str or None) name of the trend set for which the forced
                          reading should be returned. If None passed, the
                          default period for all curves is returned

        .. seealso: :meth:`setForcedReadingPeriod`
        '''
        if tsetname is None:
            return self._forcedReadingPeriod
        else:
            self.curves_lock.acquire()
            try:
                return self.trendSets[tsetname].getForcedReadingPeriod()
            finally:
                self.curves_lock.release()

    def resetForcedReadingPeriod(self):
        '''Equivalent to setForcedReadingPeriod(msec=-1, tsetnames=None)'''
        self.setForcedReadingPeriod(msec=-1, tsetnames=None)

    def setScrollStep(self, scrollStep):
        '''
        Sets the scroll step when in Dynamic X mode. This is used to avoid
        excessive replotting, which may be a problem when plotting a lot of points.

        :param scrollStep: (float) portion of the current range that will
                             be added when scrolling.  For example, 0.1 means
                             that 10% of the current range will be added when
                             scrolling. A value of 0 means that no extra
                             space will be added (thus the scroll is not in
                             "steps"). Large scroll steps mean rough scrolls,
                             but also less CPU usage.

        .. seealso:: :meth:`setXDynScale`
        '''
        self._scrollStep = scrollStep

    def getScrollStep(self):
        '''returns the value of the scroll step

        :return: (float)
        '''
        return self._scrollStep

    def resetScrollStep(self):
        '''equivalent to setScrollStep(0.2)'''
        self.setScrollStep(0.2)

    useArchiving = Qt.pyqtProperty(
        "bool", getUseArchiving, setUseArchiving, resetUseArchiving)
    usePollingBuffer = Qt.pyqtProperty(
        "bool", getUsePollingBuffer, setUsePollingBuffer, resetUsePollingBuffer)
    maxDataBufferSize = Qt.pyqtProperty(
        "int", getMaxDataBufferSize, setMaxDataBufferSize, resetMaxDataBufferSize)
    scrollstep = Qt.pyqtProperty(
        "double", getScrollStep, setScrollStep, resetScrollStep)
    forcedReadingPeriod = Qt.pyqtProperty(
        "int", getForcedReadingPeriod, setForcedReadingPeriod, resetForcedReadingPeriod)


def test():
    import sys
    from taurus.qt.qtgui.application import TaurusApplication
    app = TaurusApplication(cmd_line_parser=None)
    w = Qt.QWidget()
    w.setLayout(Qt.QVBoxLayout())
    s = Qt.QSplitter()
    w.layout().addWidget(s)
    t = TaurusTrend()
    l = Qt.QLabel('asdasdasdasdasd')
    s.addWidget(l)
    s.addWidget(t)
    s.setSizes([1, 0])
    w.show()
    t.setModel(['bl97/pc/dummy-01/voltage'])
    sys.exit(app.exec_())


def trend_main(models=(), config_file=None, x_axis_mode='n',
               use_archiving=False,
               max_buffer_size=None,
               forced_read_period=-1,
               demo=False,
               window_name='TaurusTrend (qwt5)'):
    import sys
    from taurus.qt.qtgui.application import TaurusApplication

    app = TaurusApplication(cmd_line_parser=None, app_name="taurustrend(qwt5)")

    w = TaurusTrend()

    w.setWindowTitle(window_name)

    # demo option
    if demo:
        models = list(models)
        models.extend(['eval:rand()', 'eval:1+rand(2)'])

    # xistime option
    w.setXIsTime(x_axis_mode.lower() == 't')

    # max buffer size option
    if max_buffer_size is not None:
        w.setMaxDataBufferSize(max_buffer_size)

    # configuration file option
    if config_file is not None:
        w.loadConfig(config_file)

    # set models
    if models:
        w.setModel(list(models))

    # period option
    if forced_read_period > 0:
        w.setForcedReadingPeriod(forced_read_period)

    # archiving option
    w.setUseArchiving(use_archiving)

    # show the widget
    w.show()

    # if no models are passed, show the data import dialog
    if not models and config_file is None:
        w.showDataImportDlg()

    sys.exit(app.exec_())


if __name__ == "__main__":
    trend_main()
