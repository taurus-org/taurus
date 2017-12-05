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
__all__ = ["TaurusTrend"]

import copy

from curvespropertiestool import CurvesPropertiesTool
from dateaxisitem import DateAxisItem
from legendtool import PlotLegendTool
from forcedreadtool import ForcedReadTool
from taurus.core.util.containers import LoopList
from taurus.external.qt import QtGui, Qt
from taurus.qt.qtgui.base import TaurusBaseComponent
from taurusmodelchoosertool import TaurusModelChooserTool
from taurustrendset import TaurusTrendSet
from y2axis import Y2ViewBox
from pyqtgraph import PlotWidget

CURVE_COLORS = [Qt.QPen(Qt.Qt.red),
                Qt.QPen(Qt.Qt.blue),
                Qt.QPen(Qt.Qt.green),
                Qt.QPen(Qt.Qt.magenta),
                Qt.QPen(Qt.Qt.cyan),
                Qt.QPen(Qt.Qt.yellow),
                Qt.QPen(Qt.Qt.white)]


class TaurusTrend(PlotWidget, TaurusBaseComponent):
    """
    TaurusTrend is a general widget for plotting the evolution of a value
    over time. It is an extended taurus-aware version of
    :class:`pyqtgraph.PlotWidget`.

    Apart from all the features already available in a regulat PlotWidget,
    TaurusTrend incorporates the following tools/features:

        - Secondary Y axis (right axis)
        - Time X axis
        - A plot configuration dialog, and save/restore configuration facilities
        - A menu option for adding/removing taurus  models
        - A menu option for showing/hiding the legend
        - Automatic color change of curves for newly added models

    """

    def __init__(self, parent=None, **kwargs):

        TaurusBaseComponent.__init__(self, 'TaurusTrend')
        PlotWidget.__init__(self, parent=parent, **kwargs)

        # set up cyclic color generator
        self._curveColors = LoopList(CURVE_COLORS)
        self._curveColors.setCurrentIndex(-1)

        plot_item = self.getPlotItem()
        menu = plot_item.getViewBox().menu

        # add save & retrieve configuration actions
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
        legend_tool.attachToPlotItem(plot_item)

        # add model chooser
        self._model_chooser_tool = TaurusModelChooserTool(
            self, itemClass=TaurusTrendSet)
        self._model_chooser_tool.attachToPlotItem(plot_item)

        # add Y2 axis
        self._y2 = Y2ViewBox()
        self._y2.attachToPlotItem(plot_item)

        # Add time X axis
        axis = DateAxisItem(orientation='bottom')
        axis.attachToPlotItem(plot_item)

        # add plot configuration dialog
        cprop_tool = CurvesPropertiesTool(self)
        cprop_tool.attachToPlotItem(plot_item, y2=self._y2)

        # add force read tool
        fr_tool = ForcedReadTool(self)
        fr_tool.attachToPlotItem(self.getPlotItem())

        # Register config properties
        self.registerConfigDelegate(self._y2, 'Y2Axis')
        self.registerConfigDelegate(legend_tool, 'legend')
        self.registerConfigDelegate(fr_tool, 'forceread')

    def setModel(self, names):
        """Set a list of models"""
        self._model_chooser_tool.updateModels(names or [])

    def createConfig(self, allowUnpickable=False):
        """
        Reimplemented from BaseConfigurableClass to manage the config
        properties of the trendsets attached to this plot
        """
        try:
            # Temporarily register trendsets as delegates
            tmpreg = []
            data_items = self.getPlotItem().listDataItems()
            for idx, item in enumerate(data_items):
                if isinstance(item, TaurusTrendSet):
                    name = '__TaurusTrendSet_%d__' % idx
                    tmpreg.append(name)
                    self.registerConfigDelegate(item, name)

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
        properties of the trendsets attached to this plot
        """
        try:
            # Temporarily register trendsets as delegates
            tmpreg = []
            tsets = []
            for name in configdict['__orderedConfigNames__']:
                if name.startswith('__TaurusTrendSet_'):
                    # Instantiate empty TaurusTrendSet
                    tset = TaurusTrendSet()
                    tsets.append(tset)
                    self.registerConfigDelegate(tset, name)
                    tmpreg.append(name)

            # remove the trendsets from the second axis (Y2) to avoid dups
            self._y2.clearItems()

            TaurusBaseComponent.applyConfig(
                self, configdict=configdict, depth=depth)

            plot_item = self.getPlotItem()
            legend = plot_item.legend

            # keep a dict of existing trendsets (to use it for avoiding dups)
            currentTrendSets = dict()
            curveNames = []
            for tset in plot_item.listDataItems():
                if isinstance(tset, TaurusTrendSet):
                    currentTrendSets[tset.getFullModelName()] = tset
                    curveNames.extend([c.name for c in tset])

            # remove trendsets that exists in currentTrendSets from plot
            # (to avoid duplicates). Also remove curves from the legend
            for tset in tsets:
                ts = currentTrendSets.get(tset.getFullModelName(), None)
                if ts is not None:
                    plot_item.removeItem(ts)

            # Add to plot **after** their configuration has been applied
            for tset in tsets:
                # First we add all the trendsets to self. This way the plotItem
                # can keep a list of dataItems (PlotItem.listDataItems())
                self.addItem(tset)

                # Add trendsets to Y2 axis, when the trendset configurations
                # have been applied.
                # Ideally, the Y2ViewBox class must handle the action of adding
                # trendsets to itself, but we want add the trendsets when they
                # are restored with all their properties.
                if tset.getFullModelName() in self._y2.getCurves():
                    plot_item.getViewBox().removeItem(tset)
                    self._y2.addItem(tset)
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


def TaurusTrendMain():
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
    parser.add_option("--demo", action="store_true", dest="demo",
                      default=False, help="show a demo of the widget")
    parser.add_option("--window-name", dest="window_name",
                      default="TaurusTrend (pg)", help="Name of the window")

    app = taurus.qt.qtgui.application.TaurusApplication(
        cmd_line_parser=parser,
        app_name="taurustrend(pg)",
        app_version=taurus.Release.version
    )

    args = app.get_command_line_args()
    options = app.get_command_line_options()

    models = args
    w = TaurusTrend()

    w.setWindowTitle(options.window_name)

    # options.config_file = 'tmp/TaurusTrend.pck'



    if options.demo:
        args.extend(['eval:rand()', 'eval:1+rand(2)'])

    if options.config_file is not None:
        w.loadConfigFile(options.config_file)

    if models:
        w.setModel(models)

    w.show()
    ret = app.exec_()
    # w.saveConfigFile('tmp/TaurusTrend.pck')
    # import pprint
    # pprint.pprint(w.createConfig())

    sys.exit(ret)


if __name__ == '__main__':
    TaurusTrendMain()
