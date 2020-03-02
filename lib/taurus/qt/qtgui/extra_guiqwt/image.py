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
Extension of :mod:`guiqwt.image`
"""
__all__ = ["TaurusImageItem", "TaurusRGBImageItem", "TaurusTrend2DItem",
           "TaurusTrend2DScanItem", "TaurusEncodedImageItem",
           "TaurusEncodedRGBImageItem"]

from taurus.core.units import Quantity
from taurus.external.qt import Qt
from taurus.qt.qtgui.base import TaurusBaseComponent
from taurus.qt.qtcore.util import baseSignal
import taurus.core
from taurus.core.util.containers import ArrayBuffer

from guiqwt.image import ImageItem, RGBImageItem, XYImageItem
from guiqwt.image import INTERP_NEAREST, INTERP_LINEAR

import numpy


class TaurusBaseImageItem(TaurusBaseComponent):
    '''A ImageItem that gets its data from a taurus attribute'''

    dataChanged = baseSignal('dataChanged')

    def setModel(self, model):
        # do the standard stuff
        TaurusBaseComponent.setModel(self, model)
        #... and fire a fake event for initialization
        try:
            value = self.getModelObj().read()
            self.fireEvent(
                self, taurus.core.taurusbasetypes.TaurusEventType.Change, value)
        except:
            pass

    def handleEvent(self, evt_src, evt_type, evt_value):
        if evt_value is None or getattr(evt_value, 'rvalue', None) is None:
            self.debug('Ignoring event from %s' % repr(evt_src))
            return
        v = evt_value.rvalue
        if isinstance(v, Quantity):
            v = v.magnitude
            # TODO: units should be used for setting some title in the colorbar
        try:
            v = self.filterData(v)
        except Exception as e:
            self.info('Ignoring event. Reason: %s', e.message)
            return
        # this is the range of the z axis (color scale)
        lut_range = self.get_lut_range()
        # if the range was not set, make it None (autoscale z axis)
        if lut_range[0] == lut_range[1]:
            lut_range = None
        self.set_data(v, lut_range=lut_range)
        self.dataChanged.emit()
        p = self.plot()

        if p is not None:
            p.update_colormap_axis(self)
            p.replot()

    def filterData(self, data):
        '''Reimplement this method if you want to pre-process
        the data that will be passed to set_data.

        It should return something acceptable by :meth:`setData`
        and raise an exception if the data cannot be processed.

        This default implementation casts array types not
        supported by guiqwt to numpy.int32

        See:
          - http://code.google.com/p/guiqwt/issues/detail?id=44 and
          - https://sourceforge.net/tracker/?func=detail&atid=484769&aid=3603991&group_id=57612
          - https://sourceforge.net/p/tauruslib/tickets/33/
        '''
        try:
            dtype = data.dtype
            v = data
        except:
            v = numpy.array(data)  # note that this is potentially expensive
            dtype = v.dtype

        if dtype not in (float, numpy.double, numpy.int32, numpy.uint16,
                         numpy.int16, numpy.uint8, numpy.int8, bool):
            # note: numpy.uint32 was not included because of
            # https://sourceforge.net/p/tauruslib/tickets/33/
            try:
                self.debug('casting to numpy.int32')
                v = numpy.int32(v)
            except OverflowError:
                raise OverflowError(
                    "type %s not supported by guiqwt and cannot be casted to int32" % repr(v.dtype))

        return v


class TaurusEncodedBaseImageItem(TaurusBaseImageItem):
    '''A ImageItem that gets its data from a taurus DevEncoded attribute'''

    def setModel(self, model):
        # do the standard stuff
        TaurusBaseComponent.setModel(self, model)
        #... and fire a fake event for initialization
        try:
            fmt, value = self.codec.decode(self.getModelObj().read())
            self.fireEvent(
                self, taurus.core.taurusbasetypes.TaurusEventType.Change, value)
        except:
            pass

    def filterData(self, data):
        '''reimplementation to decode data using the DevEncoded codecs'''
        if type(data) == tuple:
            from taurus.core.util.codecs import CodecFactory
            codec = CodecFactory().getCodec(data[0])

            try:
                fmt, decoded_data = codec.decode(data)
            except Exception as e:
                self.info('Decoder error: %s', e.message)
                raise e

            try:
                dtype = decoded_data.dtype
                v = decoded_data
            except:
                # note that this is potentially expensive
                v = numpy.array(decoded_data)
                dtype = v.dtype

            if dtype not in (float, numpy.double, numpy.int32, numpy.uint16,
                             numpy.int16, numpy.uint8, numpy.int8, bool):
                # note: numpy.uint32 was not included because of
                # https://sourceforge.net/p/tauruslib/tickets/33/
                try:
                    self.debug('casting to numpy.int32')
                    v = numpy.int32(v)
                except OverflowError:
                    raise OverflowError(
                        "type %s not supported by guiqwt and cannot be casted to int32" % repr(v.dtype))

            return v
        else:
            raise ValueError(
                'Unexpected data type (%s) for DevEncoded attribute (tuple expected)' % type(data))


class TaurusImageItem(ImageItem, TaurusBaseImageItem):
    '''A ImageItem that gets its data from a taurus attribute'''

    def __init__(self, param=None):
        ImageItem.__init__(self, numpy.zeros((1, 1)), param=param)
        TaurusBaseImageItem.__init__(self, self.__class__.__name__)


class TaurusEncodedImageItem(ImageItem, TaurusEncodedBaseImageItem):
    '''A ImageItem that gets its data from a DevEncoded attribute'''

    def __init__(self, param=None):
        ImageItem.__init__(self, numpy.zeros((1, 1)), param=param)
        TaurusEncodedBaseImageItem.__init__(self, self.__class__.__name__)


class TaurusXYImageItem(XYImageItem, TaurusBaseImageItem):
    '''A XYImageItem that gets its data from a taurus attribute'''

    def __init__(self, param=None):
        XYImageItem.__init__(self, numpy.arange(2), numpy.arange(
            2), numpy.zeros((2, 2)), param=param)
        TaurusBaseImageItem.__init__(self, self.__class__.__name__)


class TaurusRGBImageItem(RGBImageItem, TaurusBaseImageItem):
    '''A RGBImageItem that gets its data from a taurus attribute'''

    def __init__(self, param=None):
        RGBImageItem.__init__(self, numpy.zeros((1, 1, 3)), param=param)
        TaurusBaseImageItem.__init__(self, self.__class__.__name__)

    def set_data(self, data, lut_range=None, **kwargs):
        '''dummy reimplementation to accept the lut_range kwarg (just ignoring it)'''
        return RGBImageItem.set_data(self, data, **kwargs)


class TaurusEncodedRGBImageItem(RGBImageItem, TaurusEncodedBaseImageItem):
    '''A RGBImageItem that gets its data from a DevEncoded attribute'''

    def __init__(self, param=None):
        RGBImageItem.__init__(self, numpy.zeros((1, 1, 3)), param=param)
        TaurusEncodedBaseImageItem.__init__(self, self.__class__.__name__)

    def set_data(self, data, lut_range=None, **kwargs):
        '''dummy reimplementation to accept the lut_range kwarg (just ignoring it)'''
        return RGBImageItem.set_data(self, data, **kwargs)


class TaurusTrend2DItem(XYImageItem, TaurusBaseComponent):
    """
    A XYImageItem that is constructed by stacking 1D arrays from events from 
    a Taurus 1D attribute
    """

    scrollRequested = baseSignal('scrollRequested', object, object, object)
    dataChanged = baseSignal('dataChanged')

    def __init__(self, param=None, buffersize=512, stackMode='datetime'):
        """
        :param param: param to be passed to XYImageItem constructor
        :param buffersize: (int) size of the stack
        :param stackMode: (str) can be 'datetime', 'timedelta' or 'event'
        """
        XYImageItem.__init__(self, numpy.arange(2), numpy.arange(
            2), numpy.zeros((2, 2)), param=param)
        TaurusBaseComponent.__init__(self, self.__class__.__name__)
        self.maxBufferSize = buffersize
        self._yValues = None
        self._xBuffer = None
        self._zBuffer = None
        self.stackMode = stackMode
        self.set_interpolation(INTERP_NEAREST)
        self.__timeOffset = None

        # Config properties
        self.registerConfigProperty(self.get_lut_range,
                                    self.set_lut_range,
                                    'lut_range'
                                    )
        self.registerConfigProperty(self._get_interpolation_cfg,
                                    self._set_interpolation_cfg,
                                    'interpolation'
                                    )
        self.registerConfigProperty(self.get_color_map_name,
                                    self.set_color_map,
                                    'color_map'
                                    )

    def _get_interpolation_cfg(self):
        ret = self.get_interpolation()
        if len(ret) == 2:
            ret = (ret[0], len(ret[1]))
        return ret

    def _set_interpolation_cfg(self, interpolate_cfg):
        self.set_interpolation(*interpolate_cfg)

    def setBufferSize(self, buffersize):
        '''sets the size of the stack

        :param buffersize: (int) size of the stack
        '''
        self.maxBufferSize = buffersize
        try:
            if self._xBuffer is not None:
                self._xBuffer.setMaxSize(buffersize)
            if self._zBuffer is not None:
                self._zBuffer.setMaxSize(buffersize)
        except ValueError:
            self.info(
                'buffer downsizing  requested. Current contents will be discarded')
            self._xBuffer = None
            self._zBuffer = None

    def setModel(self, model):
        # do the standard stuff
        TaurusBaseComponent.setModel(self, model)
        #... and fire a fake event for initialization
        try:
            value = self.getModelObj().read()
            self.fireEvent(
                self, taurus.core.taurusbasetypes.TaurusEventType.Change, value)
        except:
            pass

    def handleEvent(self, evt_src, evt_type, evt_value):
        if evt_value is None or getattr(evt_value, 'rvalue', None) is None:
            self.debug('Ignoring event from %s' % repr(evt_src))
            return
        plot = self.plot()
        if plot is None:
            return

        # initialization
        ySize = len(evt_value.rvalue)
        if self._yValues is None:
            self._yValues = numpy.arange(ySize, dtype='d')
        if self._xBuffer is None:
            self._xBuffer = ArrayBuffer(numpy.zeros(
                min(128, self.maxBufferSize), dtype='d'), maxSize=self.maxBufferSize)
        if self._zBuffer is None:
            self._zBuffer = ArrayBuffer(numpy.zeros(
                (min(128, self.maxBufferSize), ySize), dtype='d'), maxSize=self.maxBufferSize)
            return

        # check that new data is compatible with previous data
        if ySize != self._yValues.size:
            self.info('Incompatible shape in data from event (orig=%i, current=%i). Ignoring' % (
                self._yValues.size, ySize))
            return

        # update x values
        if self.stackMode == 'datetime':
            x = evt_value.time.totime()
            if self.__timeOffset is None:
                self.__timeOffset = x
                plot.set_axis_title('bottom', 'Time')
                plot.set_axis_unit('bottom', '')

        elif self.stackMode == 'deltatime':
            try:
                x = evt_value.time.totime() - self.__timeOffset
            except TypeError:  # this will happen if self.__timeOffset has not been initialized
                self.__timeOffset = evt_value.time.totime()
                x = 0
                plot.set_axis_title('bottom', 'Time since %s' %
                                    evt_value.time.isoformat())
                plot.set_axis_unit('bottom', '')
        elif self.stackMode == 'event':
            try:
                # +numpy.random.randint(0,4) #for debugging we can put a variable step
                step = 1
                x = self._xBuffer[-1] + step
            except IndexError:  # this will happen when the x buffer is empty
                x = 0
                plot.set_axis_title('bottom', 'Event #')
                plot.set_axis_unit('bottom', '')
        else:
            raise ValueError('Unsupported stack mode %s' % self.stackMode)

        if len(self._xBuffer) and x <= self._xBuffer[-1]:
            self.info('Ignoring event (non-increasing x value)')
            return
        self._xBuffer.append(x)

        # update z
        rvalue = evt_value.rvalue
        if isinstance(evt_value.rvalue, Quantity):
            rvalue = evt_value.rvalue.magnitude
            # TODO: units should be checked for coherence with previous values
        self._zBuffer.append(rvalue)

        # check if there is enough data to start plotting
        if len(self._xBuffer) < 2:
            self.info('waiting for at least 2 values to start plotting')
            return

        x = self._xBuffer.contents()
        y = self._yValues
        z = self._zBuffer.contents().transpose()

        # Use previous LUT range (z axis range), or set to None (autoscale)
        # if it is uninitialized
        lut_range = self.get_lut_range()
        if lut_range[0] == lut_range[1]:
            lut_range = None

        # update the plot data
        self.set_data(z, lut_range=lut_range)
        self.set_xy(x, y)

        # signal data changed and replot
        self.dataChanged.emit()

        if plot is not None:
            value = x[-1]
            axis = self.xAxis()
            xmin, xmax = plot.get_axis_limits(axis)
            if value > xmax or value < xmin:
                self.scrollRequested.emit(plot, axis, value)
            plot.update_colormap_axis(self)
            plot.replot()


class TaurusTrend2DScanItem(TaurusTrend2DItem):
    _xDataKey = 'point_nb'

    def __init__(self, channelKey, xDataKey, door, param=None, buffersize=512):
        TaurusTrend2DItem.__init__(
            self, param=param, buffersize=buffersize, stackMode=None)
        self._channelKey = channelKey
        self._xDataKey = xDataKey
        self.connectWithQDoor(door)

    def scanDataReceived(self, packet):
        '''
        packet is a dict with {type:str, "data":object} and the accepted types are: data_desc, record_data, record_end
        and the data objects are: seq<ColumnDesc.Todict()>, record.data dict and dict , respectively
        '''
        if packet is None:
            self.debug('Ignoring empty scan data packet')
            return
        id, packet = packet
        pcktype = packet.get("type", "__UNKNOWN_PCK_TYPE__")
        if pcktype == "data_desc":
            self._dataDescReceived(packet["data"])
        elif pcktype == "record_data":
            self._scanLineReceived(packet["data"])
        elif pcktype == "record_end":
            pass
        else:
            self.debug("Ignoring packet of type %s" % repr(pcktype))

    def clearTrend(self):
        self._yValues = None
        self._xBuffer = None
        self._zBuffer = None

    def _dataDescReceived(self, datadesc):
        '''prepares the plot according to the info in the datadesc dictionary'''
        self.clearTrend()
        # decide which data to use for x
        if self._xDataKey is None or self._xDataKey == "<mov>":
            self._autoXDataKey = datadesc['ref_moveables'][0]
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
        plot = self.plot()
        plot.set_axis_title('bottom', self._autoXDataKey)
        xmin, xmax = xinfo.get('min_value'), xinfo.get('max_value')
        if xmin is None or xmax is None:
            pass  # @todo: autoscale if any limit is unknown
        else:
            plot.set_axis_limits('bottom', xmin, xmax)

    def _scanLineReceived(self, recordData):
        '''Receives a recordData dictionary and updates the curves associated to it

        .. seealso:: <Sardana>/MacroServer/scan/scandata.py:Record.data

        '''
        # obtain the x value
        try:
            xval = recordData[self._autoXDataKey]
        except KeyError:
            self.warning(
                'Cannot find data "%s" in the current scan record. Ignoring', self._autoXDataKey)
            return
        if not numpy.isscalar(xval):
            self.warning('Data for "%s" is of type "%s". Cannot use it for the X values. Ignoring',
                         self._autoXDataKey, type(xval))
            return
        # obtain y value
        try:
            chval = recordData[self._channelKey]
        except KeyError:
            self.warning(
                'Cannot find data "%s" in the current scan record. Ignoring', self._channelKey)
        if chval.shape != self._yValues.shape:
            self.warning('Incompatible shape of "%s" (%s). Ignoring',
                         self._channelKey, repr(chval.shape))
            return

        # initialization
        if self._yValues is None:
            self._yValues = numpy.arange(chval.size, dtype='d')
        if self._xBuffer is None:
            self._xBuffer = ArrayBuffer(numpy.zeros(
                min(16, self.maxBufferSize), dtype='d'), maxSize=self.maxBufferSize)
        if self._zBuffer is None:
            self._zBuffer = ArrayBuffer(numpy.zeros(
                (min(16, self.maxBufferSize), chval.size), dtype='d'), maxSize=self.maxBufferSize)

        # update x
        self._xBuffer.append(xval)
        # update z
        self._zBuffer.append(chval)

        # check if there is enough data to start plotting
        if len(self._xBuffer) < 2:
            self.info('waiting for at least 2 values to start plotting')
            return

        x = self._xBuffer.contents()
        y = self._yValues
        z = self._zBuffer.contents().transpose()

        # update the plot data
        lut_range = self.get_lut_range()  # this is the range of the z axis (color scale)
        if lut_range[0] == lut_range[1]:
            # if the range was not set, make it None (autoscale z axis)
            lut_range = None
        self.set_data(z, lut_range=lut_range)
        self.set_xy(x, y)

        # signal data changed and replot
        self.dataChanged.emit()
        plot = self.plot()
        if plot is not None:
            value = x[-1]
            axis = self.xAxis()
            xmin, xmax = plot.get_axis_limits(axis)
            if value > xmax or value < xmin:
                self.scrollRequested.emit(plot, axis, value)
            plot.update_colormap_axis(self)
            plot.replot()

    def connectWithQDoor(self, doorname):
        '''connects this TaurusTrend2DScanItem to a QDoor

        :param doorname: (str) the QDoor name
        '''
        qdoor = taurus.Device(doorname)
        qdoor.recordDataUpdated.connect(self.scanDataReceived)

    def getModel(self):
        return self.__model

    def setModel(self, model):
        self.__model = model


def taurusImageMain():
    from guiqwt.tools import (RectangleTool, EllipseTool, HRangeTool, PlaceAxesTool,
                              MultiLineTool, FreeFormTool, SegmentTool, CircleTool,
                              AnnotatedRectangleTool, AnnotatedEllipseTool,
                              AnnotatedSegmentTool, AnnotatedCircleTool, LabelTool,
                              AnnotatedPointTool, ObliqueRectangleTool,
                              AnnotatedObliqueRectangleTool)
    try:  # In newer guiqwt versions, Annotated*CursorTool have been replaced by *CursorTool
        from guiqwt.tools import AnnotatedVCursorTool, AnnotatedHCursorTool
        VCursorTool, HCursorTool = AnnotatedVCursorTool, AnnotatedHCursorTool
    except ImportError:
        from guiqwt.tools import VCursorTool, HCursorTool

    from taurus.qt.qtgui.extra_guiqwt.tools import TaurusImageChooserTool
    from guiqwt.plot import ImageDialog
    from taurus.qt.qtgui.extra_guiqwt.builder import make
    from taurus.qt.qtgui.application import TaurusApplication
    import taurus.core.util.argparse
    import sys

    parser = taurus.core.util.argparse.get_taurus_parser()
    parser.set_usage("%prog [options] [<model1> [<model2>] ...]")
    parser.set_description("a taurus application for plotting 2D data sets")
    app = TaurusApplication(
        cmd_line_parser=parser, app_name="taurusimage", app_version=taurus.Release.version)
    args = app.get_command_line_args()

    # create a dialog with a plot and add the images
    win = ImageDialog(edit=False, toolbar=True, wintitle="Taurus Image",
                      options=dict(show_xsection=False, show_ysection=False))

    # add tools
    for toolklass in (TaurusImageChooserTool,
                      LabelTool, HRangeTool,
                      MultiLineTool, FreeFormTool, PlaceAxesTool,
                      AnnotatedObliqueRectangleTool,
                      AnnotatedEllipseTool, AnnotatedSegmentTool,
                      AnnotatedPointTool, VCursorTool,
                      HCursorTool):
        win.add_tool(toolklass)

    # add images from given models
    plot = win.get_plot()
    for m in args:
        img = make.image(taurusmodel=m)
        plot.add_item(img)
        # IMPORTANT: connect the cross section plots to the taurusimage so that
        # they are updated when the taurus data changes
        img.dataChanged.connect(win.update_cross_sections)

    win.exec_()


def test1():
    """Adapted from guiqwt cross_section.py example"""
    from guiqwt.plot import ImageDialog
    from taurus.qt.qtgui.extra_guiqwt.builder import make
    from taurus.qt.qtgui.application import TaurusApplication
    app = TaurusApplication(cmd_line_parser=None)

    # define a taurus image
    #model1 = 'sys/tg_test/1/short_image_ro'
    #model1 = 'sys/tg_test/1/long64_image_ro'
    model1 = 'sys/tg_test/1/ulong_image_ro'
    taurusimage = make.image(taurusmodel=model1)
    #taurusrgbimage = make.rgbimage(taurusmodel= 'eval:array([[[ 222, 0, 0], [0, 222, 0]], [[0, 0, 222], [222, 222, 222]]])')
    #taurusxyimage= make.xyimage(taurusmodel= model1)
    #taurusxyimage.set_xy(numpy.arange(251)*10,numpy.arange(251)*100 )

    # define normal image (guiqwt standard)
    #data = numpy.random.rand(100,100)
    #image = make.image(data=data)

    # create a dialog with a plot and add the images
    win = ImageDialog(edit=False, toolbar=True, wintitle="Taurus Cross sections test",
                      options=dict(show_xsection=False, show_ysection=False))
    from taurus.qt.qtgui.extra_guiqwt.tools import TaurusImageChooserTool
    win.add_tool(TaurusImageChooserTool)
    plot = win.get_plot()
    plot.add_item(taurusimage)
#    plot.add_item(taurusxyimage)
#    plot.add_item(image)
#    plot.add_item(taurusrgbimage)

#    win.get_itemlist_panel().show()

    # IMPORTANT: connect the cross section plots to the taurusimage so that they are updated when the taurus data changes
    # taurusimage.dataChanged.connect(win.update_cross_sections)

    win.exec_()

if __name__ == "__main__":
    test1()
    # taurusImageMain()
