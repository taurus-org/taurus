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

"""Extension of :mod:`guiqwt.tools`"""


__docformat__ = 'restructuredtext'

import weakref
from taurus.external.qt import Qt
from guiqwt.tools import (CommandTool, ToggleTool, DefaultToolbarID,
                          QActionGroup, add_actions)
from taurus.core.taurusbasetypes import TaurusElementType
from taurus.qt.qtcore.configuration import BaseConfigurableClass
from taurus.qt.qtgui.extra_guiqwt.builder import make
from taurus.qt.qtgui.extra_guiqwt.curve import TaurusCurveItem, TaurusTrendItem
from taurus.qt.qtgui.extra_guiqwt.image import TaurusTrend2DItem
from taurus.qt.qtgui.extra_guiqwt.curvesmodel import CurveItemConfDlg
from taurus.qt.qtgui.panel import TaurusModelChooser
from taurus.qt.qtgui.extra_guiqwt.scales import DateTimeScaleEngine


class TaurusCurveChooserTool(CommandTool):
    """
    A tool that shows the Taurus Model Chooser to create/edit the taurus curves
    of a plot
    """

    def __init__(self, manager, toolbar_id=DefaultToolbarID):
        super(TaurusCurveChooserTool, self).__init__(
                manager, "Taurus Models...", Qt.QIcon("logos:taurus.png"),
                toolbar_id=toolbar_id)

    def activate_command(self, plot, checked):
        """Activate tool"""
        # retrieve current Taurus curves
        tauruscurves = [item for item in plot.get_public_items(
        ) if isinstance(item, TaurusCurveItem)]
        # show a dialog
        confs, ok = CurveItemConfDlg.showDlg(parent=plot, curves=tauruscurves)
        if ok:
            # remove previous taurus curves
            plot.del_items(tauruscurves)
            # create curve items and add them to the plot
            for c in confs:
                if c.taurusparam.yModel:
                    item = make.pcurve(c.taurusparam.xModel or None,
                                       c.taurusparam.yModel, c.curveparam)
                    plot.add_item(item)
                    if c.axesparam is not None:
                        c.axesparam.update_axes(item)


class TaurusImageChooserTool(CommandTool):
    """
    A tool that shows the Taurus Model Chooser and adds new taurus image items
    to a plot
    """

    def __init__(self, manager, toolbar_id=DefaultToolbarID):
        super(TaurusImageChooserTool, self).__init__(
                manager, "Add Taurus images...", Qt.QIcon("logos:taurus.png"),
                toolbar_id=toolbar_id)

    def activate_command(self, plot, checked):
        """Activate tool"""
        # show a dialog
        models, ok = TaurusModelChooser.modelChooserDlg(
            parent=plot, selectables=[TaurusElementType.Attribute])
        if ok:
            # create image items and add them to the plot
            for m in models:
                item = make.image(taurusmodel=m)
                plot.add_item(item)


class TaurusModelChooserTool(CommandTool):
    """
    A tool that shows the Taurus Model Chooser and sets the chosen model on
    the manager
    """

    def __init__(self, manager, toolbar_id=DefaultToolbarID, singleModel=False):
        super(TaurusModelChooserTool, self).__init__(
                manager, "Change Taurus Model...", Qt.QIcon("logos:taurus.png"),
                toolbar_id=toolbar_id)
        self.singleModel = singleModel

    def activate_command(self, plot, checked):
        """Activate tool"""
        # show a dialog
        models, ok = TaurusModelChooser.modelChooserDlg(
                parent=plot,
                selectables=[TaurusElementType.Attribute],
                singleModel=self.singleModel
        )
        if ok:
            if self.singleModel:
                if models:
                    self.manager.setModel(models[0])
                else:
                    self.manager.setModel('')
            else:
                self.manager.setModel(models)


class TimeAxisTool(CommandTool):
    """
    A tool that allows the user to change the type of scales to/from time mode
    """

    def __init__(self, manager):
        super(TimeAxisTool, self).__init__(
                manager, "Time Scale", icon=Qt.QIcon("status:awaiting.svg"),
                tip=None, toolbar_id=None)
        self.action.setEnabled(True)

    def create_action_menu(self, manager):
        """Create and return menu for the tool's action"""
        menu = Qt.QMenu()
        group = QActionGroup(manager.get_main())
        y_x = manager.create_action("y(x)", triggered=self.set_scale_y_x)
        y_t = manager.create_action("y(t)", triggered=self.set_scale_y_t)
        t_x = manager.create_action("t(x)", triggered=self.set_scale_t_x)
        t_t = manager.create_action("t(t)", triggered=self.set_scale_t_t)
        self.scale_menu = {(False, False): y_x, (True, False): y_t,
                           (False, True): t_x, (True, True): t_t}
        # I need to do this because the manager.create_action does not accept
        # the "checkable" keyword.
        for action in (y_x, y_t, t_x, t_t):
            # see http://code.google.com/p/guiqwt/issues/detail?id=41
            action.setCheckable(True)
        for obj in (group, menu):
            add_actions(obj, (y_x, y_t, t_x, t_t))

        return menu

    def _getAxesUseTime(self, plot):
        """
        Returns a tuple (xIsTime, yIsTime) where xIsTime is True if the plot's
        active x axis uses a TimeScale. yIsTime is True if plot's active y axis
        Scale. Otherwise they are False.
        """
        if plot is None:
            return False, False
        xaxis, yaxis = plot.get_active_axes()
        xEngine = plot.axisScaleEngine(xaxis)
        yEngine = plot.axisScaleEngine(yaxis)
        return (isinstance(xEngine, DateTimeScaleEngine),
                isinstance(yEngine, DateTimeScaleEngine))

    def update_status(self, plot):
        active_scale = self._getAxesUseTime(plot)
        for scale_type, scale_action in self.scale_menu.items():
            scale_action.setEnabled(True)
            if active_scale == scale_type:
                scale_action.setChecked(True)
            else:
                scale_action.setChecked(False)

    def _setPlotTimeScales(self, xIsTime, yIsTime):
        plot = self.get_active_plot()
        if plot is not None:
            for axis, isTime in zip(plot.get_active_axes(), (xIsTime, yIsTime)):
                if isTime:
                    DateTimeScaleEngine.enableInAxis(plot, axis, rotation=-45)
                else:
                    DateTimeScaleEngine.disableInAxis(plot, axis)
            plot.replot()

    def set_scale_y_x(self, checked):
        if not checked:
            return
        self._setPlotTimeScales(False, False)

    def set_scale_t_x(self, checked):
        if not checked:
            return
        self._setPlotTimeScales(False, True)

    def set_scale_y_t(self, checked):
        if not checked:
            return
        self._setPlotTimeScales(True, False)

    def set_scale_t_t(self, checked):
        if not checked:
            return
        self._setPlotTimeScales(True, True)


class AutoScrollTool(ToggleTool, BaseConfigurableClass):
    """A tool that puts the plot in "AutoScroll" mode.
    This makes sense in trend plots where we want to keep the last value
    always visible"""

    def __init__(self, manager, scrollFactor=0.2, toolbar_id=None):
        ToggleTool.__init__(self, manager, title='Auto Scroll', icon=None,
                tip='Force X scale to always show the last value',
                toolbar_id=toolbar_id)
        BaseConfigurableClass.__init__(self)
        self.scrollFactor = scrollFactor
        self.registerConfigProperty(self.action.isChecked,
                                    self.setChecked,
                                    'actionChecked')

    def setChecked(self, checked):
        self.action.setChecked(checked)
        self.activate_command(self.__plot(), checked)

    def register_plot(self, baseplot):
        ToggleTool.register_plot(self, baseplot)
        # TODO: drop support for guiqwt2 once we support guiqwt3
        import guiqwt
        _guiqwt_major_version = int(guiqwt.__version__.split('.')[0])
        if _guiqwt_major_version < 3:
            from guiqwt.signals import SIG_ITEMS_CHANGED
            baseplot.connect(baseplot, SIG_ITEMS_CHANGED, self.items_changed)
        else:
            baseplot.SIG_ITEMS_CHANGED.connect(self.items_changed)

        self.__plot = weakref.ref(baseplot)

    def activate_command(self, plot, checked):
        """Activate tool"""
        # retrieve current Taurus curves
        for item in self.getScrollItems(plot):
            try:
                item.scrollRequested.disconnect(self.onScrollRequested)
            except:
                pass
            if checked:
                item.scrollRequested.connect(self.onScrollRequested)

    def getScrollItems(self, plot):
        return [item for item in plot.get_items()
                if isinstance(item, (TaurusTrendItem, TaurusTrend2DItem))]

    def onScrollRequested(self, plot, axis, value):
        scalemin, scalemax = plot.get_axis_limits(axis)
        scaleRange = abs(scalemax - scalemin)
        # ignore requests that imply setting a null range
        if scaleRange == 0:
            return
        xmin = value - scaleRange * (1. - self.scrollFactor)
        xmax = value + scaleRange * self.scrollFactor
        plot.set_axis_limits(axis, xmin, xmax)

    def items_changed(self, plot):
        self.activate_command(plot, self.action.isChecked())


class _BaseAutoScaleTool(ToggleTool, BaseConfigurableClass):
    """Base class for the AutoScale tools"""

    def __init__(self, manager, axis, toolbar_id=None):
        ToggleTool.__init__(
            self,
            manager,
            title='Auto-scale %s axis' % axis,
            icon=None,
            tip='Auto-scale %s axis when data changes',
            toolbar_id=toolbar_id)
        BaseConfigurableClass.__init__(self)
        self.axis = axis
        self.registerConfigProperty(self.action.isChecked,
                                    self.setChecked,
                                    'actionChecked')

    def setChecked(self, checked):
        self.action.setChecked(checked)
        self.activate_command(self.__plot(), checked)

    def register_plot(self, baseplot):
        ToggleTool.register_plot(self, baseplot)
        baseplot.SIG_ITEMS_CHANGED.connect(self.items_changed)
        self.__plot = weakref.ref(baseplot)

    def activate_command(self, plot, checked):
        """Activate tool"""
        for item in self.getWatchableItems(plot):
            try:
                item.dataChanged.disconnect(self.onDataChanged)
            except:
                pass
            if checked:
                item.dataChanged.connect(self.onDataChanged)

    def getWatchableItems(self, plot):
        return [item for item in plot.get_items()
                if hasattr(item, 'dataChanged')]

    def onDataChanged(self):
        plot = self.__plot()
        axis_id = plot.AXIS_NAMES[self.axis]
        plot.do_autoscale(replot=False, axis_id=axis_id)

    def items_changed(self, plot):
        self.activate_command(plot, self.action.isChecked())


class AutoScaleXTool(_BaseAutoScaleTool):
    """ToggleTool that, when checked, autoscales the X scale on data changed"""
    def __init__(self, manager, toolbar_id=None):
        _BaseAutoScaleTool.__init__(self, manager, axis='bottom',
                                    toolbar_id=toolbar_id)


class AutoScaleYTool(_BaseAutoScaleTool):
    """ToggleTool that, when checked, autoscales the Y scale on data changed"""
    def __init__(self, manager, toolbar_id=None):
        _BaseAutoScaleTool.__init__(self, manager, axis='left',
                                    toolbar_id=toolbar_id)


class AutoScaleZTool(_BaseAutoScaleTool):
    """ToggleTool that, when checked, autoscales the Z scale on data changed"""
    def __init__(self, manager, toolbar_id=None):
        _BaseAutoScaleTool.__init__ (self, manager, axis='Z',
                                     toolbar_id=toolbar_id)

    def onDataChanged(self):
        item = self.__items[0]
        item.set_lut_range(item.get_lut_range_full())

    def activate_command(self, plot, checked):
        _BaseAutoScaleTool.activate_command(self, plot, checked)
        self.__items = self.getWatchableItems(plot)



def testTool(tool):
    from taurus.qt.qtgui.application import TaurusApplication
    from guiqwt.plot import CurveDialog

    app = TaurusApplication(cmd_line_parser=None)
    win = CurveDialog(edit=False, toolbar=True)
    win.add_tool(tool)
    win.show()
    win.exec_()


def test_timeAxis():
    testTool(TimeAxisTool)
#    testTool(TaurusCurveChooserTool)


if __name__ == "__main__":
    test_timeAxis()
