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
__all__ = ["TaurusPlot"]

import copy
from taurus.core.util.containers import LoopList
from taurus.qt.qtgui.base import TaurusBaseComponent
from curvespropertiestool import CurvesPropertiesTool
from taurusmodelchoosertool import TaurusXYModelChooserTool
from legendtool import PlotLegendTool
from taurusplotdataitem import TaurusPlotDataItem
from y2axis import Y2ViewBox

from taurus.external.qt import QtGui, Qt
from pyqtgraph import PlotWidget


CURVE_COLORS = [Qt.QPen(Qt.Qt.red),
                Qt.QPen(Qt.Qt.blue),
                Qt.QPen(Qt.Qt.green),
                Qt.QPen(Qt.Qt.magenta),
                Qt.QPen(Qt.Qt.cyan),
                Qt.QPen(Qt.Qt.yellow),
                Qt.QPen(Qt.Qt.white)]


class TaurusPlot(PlotWidget, TaurusBaseComponent):
    """
    TaurusPlot is a general widget for plotting 1D data sets. It is an extended
    taurus-aware version of :class:`pyqtgraph.PlotWidget`.

    Apart from all the features already available in a regulat PlotWidget,
    TaurusPGPlot incorporates the following tools/features:

        - Secondary Y axis (right axis)
        - A plot configuration dialog, and save/restore configuration facilities
        - A menu option for adding/removing models
        - A menu option for showing/hiding the legend
        - Automatic color change of curves for newly added models

    """

    def __init__(self, parent=None,  **kwargs):

        TaurusBaseComponent.__init__(self, 'TaurusPlot')
        PlotWidget.__init__(self, parent=parent, **kwargs)

        # set up cyclic color generator
        self._curveColors = LoopList(CURVE_COLORS)
        self._curveColors.setCurrentIndex(-1)

        # add save & retrieve configuration actions
        menu = self.getPlotItem().getViewBox().menu
        saveConfigAction = QtGui.QAction('Save configuration', menu)
        saveConfigAction.triggered[()].connect(self.saveConfigFile)
        menu.addAction(saveConfigAction)

        loadConfigAction = QtGui.QAction('Retrieve saved configuration', menu)
        loadConfigAction.triggered[()].connect(self.loadConfigFile)
        menu.addAction(loadConfigAction)

        self.registerConfigProperty(self._getState,
                                    self.restoreState, 'state')

        # add legend tool
        legend_tool = PlotLegendTool(self)
        legend_tool.attachToPlotItem(self.getPlotItem())

        # add model chooser
        model_chooser_tool = TaurusXYModelChooserTool(self)
        model_chooser_tool.attachToPlotItem(self.getPlotItem(), self,
                                            self._curveColors)

        # add Y2 axis
        self._y2 = Y2ViewBox()
        self._y2.attachToPlotItem(self.getPlotItem())

        # add plot configuration dialog
        cprop_tool = CurvesPropertiesTool(self)
        cprop_tool.attachToPlotItem(self.getPlotItem(), y2=self._y2)

        # Register config properties
        self.registerConfigDelegate(self._y2, 'Y2Axis')
        self.registerConfigDelegate(legend_tool, 'legend')

    def setModel(self, models):
        """Set a list of models"""
        # TODO: remove previous models!
        # TODO: support setting xmodels as well
        # TODO: Consider supporting a space-separated string as a model
        for model in models:
            curve = TaurusPlotDataItem(name=model)
            curve.setModel(model)
            curve.setPen(self._curveColors.next().color())
            self.addItem(curve)

    def createConfig(self, allowUnpickable=False):
        """
        Reimplemented from BaseConfigurableClass to manage the config
        properties of the curves attached to this plot
        """

        try:
            # Temporarily register curves as delegates
            tmpreg = []
            curve_list = self.getPlotItem().listDataItems()
            for idx, curve in enumerate(curve_list):
                if isinstance(curve, TaurusPlotDataItem):
                    name = '__TaurusPlotDataItem_%d__' % idx
                    tmpreg.append(name)
                    self.registerConfigDelegate(curve, name)

            configdict = copy.deepcopy(TaurusBaseComponent.createConfig(
                self, allowUnpickable=allowUnpickable))

        finally:
            # Ensure that temporary delegates are unregistered
            for n in tmpreg:
                self.unregisterConfigurableItem(n, raiseOnError=False)
        return configdict

    def applyConfig(self, configdict, depth=None):
        """
        Reimplemented from BaseConfigurableClass to manage the config
        properties of the curves attached to this plot
        """
        try:
            # Temporarily register curves as delegates
            tmpreg = []
            curves = []
            for name in configdict['__orderedConfigNames__']:
                if name.startswith('__TaurusPlotDataItem_'):
                    # Instantiate empty TaurusPlotDataItem
                    curve = TaurusPlotDataItem()
                    curves.append(curve)
                    self.registerConfigDelegate(curve, name)
                    tmpreg.append(name)

            # remove the curves from the second axis (Y2) for avoid dups
            self._y2.clearItems()

            TaurusBaseComponent.applyConfig(
                self, configdict=configdict, depth=depth)

            # keep a dict of existing curves (to use it for avoiding dups)
            currentCurves = dict()
            for curve in self.getPlotItem().listDataItems():
                if isinstance(curve, TaurusPlotDataItem):
                    currentCurves[curve.getFullModelNames()] = curve

            # remove curves that exists in currentCurves, also remove from
            # the legend (avoid duplicates)
            for curve in curves:
                c = currentCurves.get(curve.getFullModelNames(), None)
                if c is not None:
                    self.getPlotItem().legend.removeItem(c.name())
                    self.getPlotItem().removeItem(c)

            # Add to plot **after** their configuration has been applied
            for curve in curves:
                # First we add all the curves in self. This way the plotItem
                # can keeps a list of dataItems (plotItem.listDataItems())
                self.addItem(curve)

                # Add curves to Y2 axis, when the curve configurations
                # have been applied.
                # Ideally, the Y2ViewBox class must handle the action of adding
                # curves to itself, but we want add the curves when they are
                # restored with all their properties.
                if curve.getFullModelNames() in self._y2.getCurves():
                    self.getPlotItem().getViewBox().removeItem(curve)
                    self._y2.addItem(curve)



        finally:
            # Ensure that temporary delegates are unregistered
            for n in tmpreg:
                self.unregisterConfigurableItem(n, raiseOnError=False)

    def _getState(self):
        """Same as PlotWidget.saveState but removing viewRange conf to force
        a refresh with targetRange when loading
        """
        state = copy.deepcopy(self.saveState())
        # remove viewRange conf
        del state['view']['viewRange']
        return state


def TaurusPlotMain():
    import sys
    import taurus.qt.qtgui.application
    import taurus.core.util.argparse

    parser = taurus.core.util.argparse.get_taurus_parser()
    parser.set_usage("%prog [options] [<model1> [<model2>] ...]")
    parser.set_description("a taurus application for plotting 1D data sets")
    parser.add_option("--config", "--config-file", dest="config_file",
                      default=None,
                      help="use the given config file for initialization"
                      )
    parser.add_option ("-x", "--x-axis-mode", dest="x_axis_mode", default='n',
                       metavar="t|n",
                       help=('X axis mode. "t" implies using a Date axis' +
                             '"n" uses the regular axis'
                             )
                       )
    parser.add_option ("--demo", action="store_true", dest="demo",
                       default=False, help="show a demo of the widget")
    parser.add_option("--window-name", dest="window_name",
                      default="TaurusPlot (pg)", help="Name of the window")

    app = taurus.qt.qtgui.application.TaurusApplication(
        cmd_line_parser=parser,
        app_name="taurusplot(pg)",
        app_version=taurus.Release.version
    )

    args = app.get_command_line_args()
    options = app.get_command_line_options()

    models = args
    w = TaurusPlot()

    # w.loadConfigFile('tmp/TaurusPlot.pck')

    w.setWindowTitle(options.window_name)

    if options.demo:
        args.extend(['eval:rand(100)', 'eval:0.5*sqrt(arange(100))'])

    if options.x_axis_mode.lower() == 't':
        from taurus.qt.qtgui.tpg import DateAxisItem
        axis = DateAxisItem(orientation='bottom')
        axis.attachToPlotItem(w.getPlotItem())

    if options.config_file is not None:
        w.loadConfigFile(options.config_file)

    if models:
        w.setModel(models)

    w.show()
    ret = app.exec_()

    # import pprint
    # pprint.pprint(w.createConfig())

    sys.exit(ret)


if __name__ == '__main__':
    TaurusPlotMain()


