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
from taurus.external.qt import QtGui, Qt
from taurus.external.qt import QtCore
from curvesAppearanceChooserDlg import (
    CurvePropAdapter, CurvesAppearanceChooser)
import pyqtgraph

from taurus.qt.qtgui.extra_pyqtgraph.taurusplotdataitem import TaurusPlotDataItem


class CurvesPropertiesTool(QtGui.QAction):

    def __init__(self, parent=None):
        QtGui.QAction.__init__(self, 'Plot configuration', parent)
        self.triggered.connect(self.onTriggered)
        self.plot_item = None

    def attachToPlotItem(self,plot_item, parentWidget=None):
        self.plot_item = plot_item
        menu = plot_item.getViewBox().menu
        menu.addAction(self)
        self.setParent(parentWidget or menu)  # Should be to a plot_item!!!

    def onTriggered(self):
        data_items = self.plot_item.listDataItems()
        # checks in all ViewBoxes from plot_item,
        # looking for a data_items (Curves).
        items = self.plot_item.scene().items()
        for item in items:
            if isinstance(item, pyqtgraph.ViewBox):
                for data in item.addedItems:
                    if data not in data_items:
                        data_items.append(data)

        # The dialog allows display and/or change the properties of any curve
        # that doesn't contain the attribute "_UImodifiable"
        for data in data_items:
            if getattr(data,"_UImodifiable", True) is False:
                data_items.remove(data)

        curvePropAdapter = CurvePropAdapter(data_items, self.plot_item)
        curves = curvePropAdapter.getCurveProperties()

        dlg = Qt.QDialog(parent=self.parent())
        layout = Qt.QVBoxLayout()
        w = CurvesAppearanceChooser(parent=dlg, curvePropDict=curves, showButtons=True, curvePropAdapter=curvePropAdapter)
        layout.addWidget(w)
        dlg.setLayout(layout)
        dlg.exec_()




if __name__ == '__main__':
    import sys
    import numpy
    import pyqtgraph as pg
    from taurus.qt.qtgui.extra_pyqtgraph.taurusmodelchoosertool import TaurusModelChooserTool
    from taurus.qt.qtgui.extra_pyqtgraph.taurusplotdataitem import TaurusPlotDataItem
    from taurus.qt.qtgui.application import TaurusApplication
    from taurus.qt.qtgui.extra_pyqtgraph.curvesPropertiesTool import CurvesPropertiesTool


    app = TaurusApplication()

    # a standard pyqtgraph plot_item
    w = pg.PlotWidget()

    #add legend to the plot, for that we have to give a name to plot items
    w.addLegend()

    # adding a regular data item (non-taurus)

    c1 = pg.PlotDataItem(name='st plot',pen=dict(color='y', width=3, style=QtCore.Qt.DashLine), fillLevel=0.3, fillBrush='c')

    c1.setData(numpy.arange(300) / 300.)
    w.addItem(c1)

    # adding a taurus data item
    c2 = TaurusPlotDataItem(name='st2 plot',  pen='r', symbol='o',symbolSize=10)
    c2.setModel('sys/tg_test/1/wave')

    w.addItem(c2)

    # w.addItem(pg.PlotDataItem([10, 20, 40, 80, 40, 20], pen='b', name='st'))
    # w.addItem(pg.PlotDataItem([3200, 1600, 800, 400, 200, 100], pen='r', name='st2'))

    #attach plot item contained in the PlotWidget to a new TaurusModelChooserTool
    curve_dialog = CurvesPropertiesTool()
    curve_dialog.attachToPlotItem(w.getPlotItem(), parentWidget=w);

    w.show()

    sys.exit(app.exec_())