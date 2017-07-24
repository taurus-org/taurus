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

from taurus import Attribute
from taurus.core.util.containers import LoopList
from taurus.qt.qtgui.base.taurusbase import TaurusBaseComponent
from taurus.qt.qtgui.extra_pyqtgraph.curvesPropertiesTool import CurvesPropertiesTool
from taurus.qt.qtgui.extra_pyqtgraph.taurusmodelchoosertool import TaurusModelChooserTool
from taurus.qt.qtgui.extra_pyqtgraph.taurusXYmodelChooser import TaurusXYModelChooserTool
from taurus.qt.qtgui.extra_pyqtgraph.plotLegendTool import PlotLegendTool
from taurus.qt.qtgui.extra_pyqtgraph.taurusplotdataitem import TaurusPlotDataItem
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

        self._initActions(self.getPlotItem().getViewBox().menu)

        plot_legend_tool = PlotLegendTool()
        plot_legend_tool.attachToPlotItem(self.getPlotItem(), self)

        curve_prop_tool = CurvesPropertiesTool()
        curve_prop_tool.attachToPlotItem(self.getPlotItem(), self)

        # taurus_model_chooser_tool = TaurusModelChooserTool()
        # taurus_model_chooser_tool.attachToPlotItem(self.getPlotItem(), self)

        taurus_XYmodel_chooser_tool = TaurusXYModelChooserTool()
        taurus_XYmodel_chooser_tool.attachToPlotItem(
            self.getPlotItem(), self, self._curveColors)

    def setModel(self, models):
        for model in models:
            # model = Attribute(model)
            curve = TaurusPlotDataItem(name=model)
            curve.setModel(model)
            curve.setPen(self._curveColors.next().color())
            self.addItem(curve)

            self.registerConfigDelegate(curve, model)  # TODO: think about dont use model name e.g. use "__Curve__<model>"



    def _initActions(self, menu):

        saveConfigAction = QtGui.QAction('Save configuration', menu)
        saveConfigAction.triggered[()].connect(self.saveConfigFile)
        menu.addAction(saveConfigAction)

        loadConfigAction = QtGui.QAction('Retrieve saved configuration', menu)
        loadConfigAction.triggered[()].connect(self.loadConfigFile)
        menu.addAction(loadConfigAction)








if __name__ == '__main__':
    import sys
    from taurus.qt.qtgui.application import TaurusApplication
    import pyqtgraph as pg
    import numpy

    app = TaurusApplication()
    w = TaurusPlot()

    w.setModel(['eval:rand(256)', 'sys/tg_test/1/wave'])

    w.show()
    ret = app.exec_()

    # import pprint
    # pprint.pprint(w.createConfig())



    sys.exit(ret)

