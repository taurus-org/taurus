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
from taurus.qt.qtgui.base.taurusbase import TaurusBaseComponent
from taurus.qt.qtgui.tpg.curvespropertiestool import CurvesPropertiesTool
from taurus.qt.qtgui.tpg.taurusmodelchoosertool import TaurusModelChooserTool
from taurus.qt.qtgui.tpg.taurusXYmodelChooser import TaurusXYModelChooserTool
from taurus.qt.qtgui.tpg.legendtool import PlotLegendTool
from taurus.qt.qtgui.tpg.taurusplotdataitem import TaurusPlotDataItem
from taurus.qt.qtgui.tpg.y2axis import Y2ViewBox

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

    def __init__(self, parent=None,  **kwargs):
        TaurusBaseComponent.__init__(self, 'TaurusPlot')

        PlotWidget.__init__(self, parent=parent, **kwargs)

        self._curveColors = LoopList(CURVE_COLORS)
        self._curveColors.setCurrentIndex(-1)

        menu = self.getPlotItem().getViewBox().menu
        saveConfigAction = QtGui.QAction('Save configuration', menu)
        saveConfigAction.triggered[()].connect(self.saveConfigFile)
        menu.addAction(saveConfigAction)

        loadConfigAction = QtGui.QAction('Retrieve saved configuration', menu)
        loadConfigAction.triggered[()].connect(self.loadConfigFile)
        menu.addAction(loadConfigAction)

        self.registerConfigProperty(self._getState,
                                    self.restoreState, 'state')

        plot_legend_tool = PlotLegendTool()
        plot_legend_tool.attachToPlotItem(self.getPlotItem(), self)

        taurus_XYmodel_chooser_tool = TaurusXYModelChooserTool()
        taurus_XYmodel_chooser_tool.attachToPlotItem(
            self.getPlotItem(), self, self._curveColors)

        # if we want the option to change curves between Y axes inside
        # the curve properties configuration dialog, we must instantiate
        # a Y2ViewBox object and through for parameters to CurvePropertiesTool
        self._y2ViewBox = Y2ViewBox()
        self._y2ViewBox.attachToPlotItem(self.getPlotItem())

        curve_prop_tool = CurvesPropertiesTool()
        curve_prop_tool.attachToPlotItem(self.getPlotItem(), self,
                                         Y2Axis=self._y2ViewBox)

        self.registerConfigDelegate(self._y2ViewBox, 'Y2Axis')
        self.registerConfigDelegate(plot_legend_tool, 'legend')

    def setModel(self, models):
        for model in models:
            curve = TaurusPlotDataItem(name=model)
            curve.setModel(model)
            curve.setPen(self._curveColors.next().color())
            self.addItem(curve)

    def createConfig(self, allowUnpickable=False):

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
            self._y2ViewBox.clearCurves()

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
                if curve.getFullModelNames() in self._y2ViewBox.getCurves():
                    self.getPlotItem().getViewBox().removeItem(curve)
                    self._y2ViewBox.addItem(curve)



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


if __name__ == '__main__':
    import sys
    from taurus.qt.qtgui.application import TaurusApplication
    import pyqtgraph as pg
    import numpy

    app = TaurusApplication()
    w = TaurusPlot()
    # w.loadConfigFile('tmp/TaurusPlot.pck')


    w.setModel(['eval:rand(256)', 'sys/tg_test/1/wave'])

    w.show()

    ret = app.exec_()

    # import pprint
    # pprint.pprint(w.createConfig())


    sys.exit(ret)

