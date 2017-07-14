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
from taurus.qt.qtgui.base.taurusbase import TaurusBaseComponent
from taurus.qt.qtgui.extra_pyqtgraph.curvesPropertiesTool import CurvesPropertiesTool
from taurus.qt.qtgui.extra_pyqtgraph.taurusmodelchoosertool import TaurusModelChooserTool
from taurus.qt.qtgui.extra_pyqtgraph.taurusplotdataitem import TaurusPlotDataItem
from taurus.external.qt import QtGui
from pyqtgraph import PlotWidget


class TaurusPlot(PlotWidget, TaurusBaseComponent):

    def __init__(self, parent=None, background='default',
                 legend=True, **kwargs):
        TaurusBaseComponent.__init__(self, 'TaurusPlot')

        PlotWidget.__init__(self, parent=parent,
                            background=background, **kwargs)

        if legend:
            self.addLegend()

        self._initActions(self.getPlotItem().getViewBox().menu)

        curve_prop_tool = CurvesPropertiesTool()
        curve_prop_tool.attachToPlotItem(self.getPlotItem(), self)
        taurus_model_chooser_tool = TaurusModelChooserTool()
        taurus_model_chooser_tool.attachToPlotItem(self.getPlotItem(), self)

    def setModel(self, models):
        for model in models:
            # model = Attribute(model)
            curve = TaurusPlotDataItem(name=model)
            curve.setModel(model)
            self.addItem(curve)

            self.registerConfigDelegate(curve, model)


            # Here we have dependences from Qwt module
            # from taurus.qt.qtgui.extra_guiqwt.curvesmodel import CurveItemConfDlg
            # tauruscurves = self.getPlotItem().items
            # confs, ok = CurveItemConfDlg.showDlg(parent=self,
            #                                      curves=tauruscurves)

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

    app = TaurusApplication()
    w = TaurusPlot()

    w.setModel(['eval:rand(256)', 'sys/tg_test/1/wave'])

    w.show()
    sys.exit(app.exec_())

