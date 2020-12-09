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

"""Extension of :mod:`guiqwt.curve`"""
from __future__ import print_function

from builtins import next

from taurus.external.qt import Qt
from taurus.qt.qtgui.base import TaurusBaseComponent
from taurus.qt.qtcore.util import baseSignal
import taurus
from guiqwt.curve import CurveItem
from taurus.qt.qtgui.extra_guiqwt.styles import TaurusCurveParam, TaurusTrendParam

from taurus.core.util.containers import ArrayBuffer
import numpy

__all__ = ["TaurusCurveItem"]


class TaurusCurveItem(CurveItem, TaurusBaseComponent):
    '''A CurveItem that autoupdates its values & params when x or y components change'''

    dataChanged = baseSignal('dataChanged')

    def __init__(self, curveparam=None, taurusparam=None):
        CurveItem.__init__(self, curveparam=curveparam)
        TaurusBaseComponent.__init__(self, self.__class__.__name__)
        # I need to do this because I am not using the standard model attach
        # mechanism
        self.taurusEvent.connect(self.filterEvent)
        self._xcomp = None
        self._ycomp = None
        if taurusparam is None:
            taurusparam = TaurusCurveParam()
        self.taurusparam = taurusparam

    def setModels(self, x, y):
        # create/get new components
        if x is None:
            newX = None
        else:
            newX = taurus.Attribute(x)
        newY = taurus.Attribute(y)

        # stop listening to previous components (if they are not the same as
        # the new)
        if self._xcomp is not None and self._xcomp is not newX:
            self._xcomp.removeListener(self)
        self._xcomp = newX
        if self._ycomp is not None and self._ycomp is not newY:
            self._ycomp.removeListener(self)
        self._ycomp = newY

        # start listening to new components
        if self._xcomp is not None:
            self._xcomp.addListener(self)
        self._ycomp.addListener(self)
        self.onCurveDataChanged()
        self.taurusparam.xModel = x
        self.taurusparam.yModel = y

    def getModels(self):
        return self.taurusparam.xModel, self.taurusparam.yModel

    def handleEvent(self, evt_src, ect_type, evt_value):
        if evt_value is None or getattr(evt_value, 'rvalue', None) is None:
            self.debug('Ignoring event from %s' % repr(evt_src))
            return
        if evt_src is self._xcomp or evt_src is self._ycomp:
            self.onCurveDataChanged()
            self.dataChanged.emit()

    def onCurveDataChanged(self):
        # TODO: Take units into account for displaying curves, axis, etc.
        try:
            if self._ycomp.isNumeric():
                yvalue = self._ycomp.read().rvalue.magnitude
            else:
                yvalue = self._ycomp.read().rvalue
        except:
            yvalue = None

        if yvalue is None:
            return

        # TODO: Take units into account for displaying curves, axis, etc.
        try:
            if self._xcomp.isNumeric():
                xvalue = self._xcomp.read().rvalue.magnitude
            else:
                xvalue = self._xcomp.read().rvalue
        except:
            xvalue = None

        if xvalue is None:
            xvalue = numpy.arange(len(yvalue))

        self.set_data(xvalue, yvalue)
        p = self.plot()
        if p is not None:
            p.replot()

    def get_item_parameters(self, itemparams):
        CurveItem.get_item_parameters(self, itemparams)
        itemparams.add("TaurusParam", self, self.taurusparam)

    def updateTaurusParams(self):
        self.taurusparam.update_curve(self)

    def set_item_parameters(self, itemparams):
        CurveItem.set_item_parameters(self, itemparams)
        self.updateTaurusParams()


class TaurusTrendItem(CurveItem, TaurusBaseComponent):
    '''A CurveItem that listens to events from a Taurus scalar attribute and appends new values to it'''

    dataChanged = baseSignal('dataChanged')
    scrollRequested = baseSignal('scrollRequested', object, object, object)

    def __init__(self, curveparam=None, taurusparam=None):
        CurveItem.__init__(self, curveparam=curveparam)
        TaurusBaseComponent.__init__(self, self.__class__.__name__)

        self.__xBuffer = None
        self.__yBuffer = None

        self.__timeOffset = None

        if taurusparam is None:
            taurusparam = TaurusTrendParam()
        self.taurusparam = taurusparam
        self.updateTaurusParams()

    def setBufferSize(self, buffersize):
        '''sets the size of the stack.

        :param buffersize: (int) size of the stack
        '''
        self.taurusparam.maxBufferSize = buffersize
        try:
            if self.__xBuffer is not None:
                self.__xBuffer.setMaxSize(buffersize)
            if self.__yBuffer is not None:
                self.__yBuffer.setMaxSize(buffersize)
        except ValueError:
            self.info(
                'buffer downsizing  requested. Current contents will be discarded')
            self.__xBuffer = None
            self.__yBuffer = None

    def setModel(self, model):
        # do the standard stuff
        TaurusBaseComponent.setModel(self, model)
        # update the taurusparam
        self.taurusparam.model = self.getModelName()
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

        # initialization\
        if self.__xBuffer is None:
            self.__xBuffer = ArrayBuffer(numpy.zeros(min(
                128, self.taurusparam.maxBufferSize), dtype='d'), maxSize=self.taurusparam.maxBufferSize)
        if self.__yBuffer is None:
            self.__yBuffer = ArrayBuffer(numpy.zeros(min(
                128, self.taurusparam.maxBufferSize), dtype='d'), maxSize=self.taurusparam.maxBufferSize)

        # update x values
        if self.taurusparam.stackMode == 'datetime':
            if self.__timeOffset is None:
                self.__timeOffset = evt_value.time.totime()
                if plot is not None:
                    plot.set_axis_title('bottom', 'Time')
                    plot.set_axis_unit('bottom', '')
            self.__xBuffer.append(evt_value.time.totime())

        elif self.taurusparam.stackMode == 'deltatime':
            try:
                self.__xBuffer.append(
                    evt_value.time.totime() - self.__timeOffset)
            except TypeError:  # this will happen if self.__timeOffset has not been initialized
                self.__timeOffset = evt_value.time.totime()
                self.__xBuffer.append(0)
                if plot is not None:
                    plot.set_axis_title('bottom', 'Time since %s' %
                                        evt_value.time.isoformat())
                    plot.set_axis_unit('bottom', '')
        else:
            try:
                # +numpy.random.randint(0,4) #for debugging we can put a variable step
                step = 1
                self.__xBuffer.append(self.__xBuffer[-1] + step)
            except IndexError:  # this will happen when the x buffer is empty
                self.__xBuffer.append(0)
                if plot is not None:
                    plot.set_axis_title('bottom', 'Event #')
                    plot.set_axis_unit('bottom', '')

        # update y
        # TODO: Take units into account for displaying curves, axis, etc.
        if self.__yBuffer.isNumeric():
            self.__yBuffer.append(evt_value.rvalue.magnitude)
        else:
            self.__yBuffer.append(evt_value.rvalue)

        # update the plot data
        x, y = self.__xBuffer.contents(), self.__yBuffer.contents()
        self.set_data(x, y)

        # signal data changed and replot
        self.dataChanged.emit()

        if plot is not None:
            value = x[-1]
            axis = self.xAxis()
            xmin, xmax = plot.get_axis_limits(axis)
            if value > xmax or value < xmin:
                self.scrollRequested.emit(plot, axis, value)
            plot.replot()

    def get_item_parameters(self, itemparams):
        CurveItem.get_item_parameters(self, itemparams)
        itemparams.add("TaurusParam", self, self.taurusparam)

    def updateTaurusParams(self):
        self.taurusparam.update_curve(self)

    def set_item_parameters(self, itemparams):
        CurveItem.set_item_parameters(self, itemparams)
        self.updateTaurusParams()


def taurusTrendMain():
    from taurus.qt.qtgui.extra_guiqwt.builder import make
    from taurus.qt.qtgui.application import TaurusApplication
    from guiqwt.plot import CurveDialog
    from guiqwt.tools import HRangeTool
    import taurus.core.util.argparse
    import sys

    parser = taurus.core.util.argparse.get_taurus_parser()
    parser.set_usage("%prog [options] [<model1> [<model2>] ...]")
    parser.set_description("a taurus application for plotting 1D data sets")
    parser.add_option("-x", "--x-axis-mode", dest="x_axis_mode", default='d', metavar="t|d|e",
                      help="interpret X values as timestamps (t), time deltas (d) or event numbers (e). Accepted values: t|d|e")
    parser.add_option("-b", "--buffer", dest="max_buffer_size", default='16384',
                      help="maximum number of values to be plotted (when reached, the oldest values will be discarded)")
    parser.add_option("-a", "--use-archiving",
                      action="store_true", dest="use_archiving", default=False)
    parser.add_option("--demo", action="store_true", dest="demo",
                      default=False, help="show a demo of the widget")
    app = TaurusApplication(
        cmd_line_parser=parser, app_name="taurusplot2", app_version=taurus.Release.version)
    args = app.get_command_line_args()
    options = app.get_command_line_options()

    # check & process options
    stackModeMap = dict(t='datetime', d='deltatime', e='event')
    if options.x_axis_mode.lower() not in stackModeMap:
        parser.print_help(sys.stderr)
        sys.exit(1)

    stackMode = stackModeMap[options.x_axis_mode.lower()]

    if options.demo:
        args.append('eval:rand()')

    w = CurveDialog(edit=False, toolbar=True, wintitle="Taurus Trend")

    # set archiving
    if options.use_archiving:
        raise NotImplementedError('Archiving support is not yet implemented')
        w.setUseArchiving(True)

    w.add_tool(HRangeTool)
    # w.add_tool(TaurusCurveChooserTool)
    # w.add_tool(TimeAxisTool)

    if len(args) == 0:
        parser.print_help(sys.stderr)
        sys.exit(1)

    plot = w.get_plot()
    for a in args:
        item = TaurusTrendItem(stackMode=stackMode,
                               buffersize=int(options.max_buffer_size))
        plot.add_item(item)
        item.setModel(a)

    w.show()
    sys.exit(app.exec_())


def taurusCurveMain():
    from taurus.qt.qtgui.extra_guiqwt.builder import make
    from taurus.qt.qtgui.application import TaurusApplication
    from guiqwt.plot import CurveDialog
    from guiqwt.tools import HRangeTool
    from taurus.qt.qtgui.extra_guiqwt.tools import TaurusCurveChooserTool, TimeAxisTool
    import taurus.core.util.argparse
    import sys

    parser = taurus.core.util.argparse.get_taurus_parser()
    parser.set_usage("%prog [options] [<model1> [<model2>] ...]")
    parser.set_description("a taurus application for plotting 1D data sets")
    app = TaurusApplication(
        cmd_line_parser=parser, app_name="taurusplot2", app_version=taurus.Release.version)
    args = app.get_command_line_args()

    win = CurveDialog(edit=False, toolbar=True, wintitle="TaurusPlot2",
                      options=dict(title="", xlabel="xlabel", ylabel="ylabel"))
    win.add_tool(HRangeTool)
    win.add_tool(TaurusCurveChooserTool)
    win.add_tool(TimeAxisTool)

    plot = win.get_plot()

    for a in args:
        mx_my = a.split('|')
        n = len(mx_my)
        if n == 1:
            mx, my = None, mx_my[0]
        elif n == 2:
            mx, my = mx_my
        else:
            print("Invalid model: %s\n" % mx_my)
            parser.print_help(sys.stderr)
            sys.exit(1)
        # cycle colors
        style = next(make.style)
        color = style[0]
        linestyle = style[1:]
        plot.add_item(make.curve(mx, my, color=color,
                                 linestyle=linestyle, linewidth=2))

    win.get_itemlist_panel().show()
    plot.set_items_readonly(False)
    win.show()
    win.exec_()


if __name__ == "__main__":
    #    test1()
    #    taurusCurveMain()
    taurusTrendMain()
