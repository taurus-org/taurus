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
from taurus.external.qt import QtGui
from taurus.external.qt import QtCore
from taurus.core import TaurusElementType
from taurus.qt.qtgui.panel.taurusmodelchooser import TaurusModelChooser
from taurusplotdataitem import TaurusPlotDataItem
import taurus
from collections import OrderedDict


class TaurusModelChooserTool(QtGui.QAction):

    def __init__(self, parent=None):
        QtGui.QAction.__init__(self, parent)
        self.plot_item = None
        self.legend = None

    def attachToPlotItem(self,plot_item):
        self.plot_item = plot_item
        if self.plot_item.legend is not None:
            self.legend = self.plot_item.legend

        menu = self.plot_item.getViewBox().menu
        model_chooser = QtGui.QAction('Model chooser', menu)
        model_chooser.triggered.connect(self.onTriggered)
        menu.addAction(model_chooser)

    def onTriggered(self):
        list_items = self.plot_item.listDataItems()
        listedTaurusPlotDataItems = dict()
        listedModelNames = []
        for item in list_items:
            if isinstance(item, TaurusPlotDataItem):
                listedModelNames.append(item.getFullModelName())
                listedTaurusPlotDataItems[item.getFullModelName()] = item

        res, ok = TaurusModelChooser.modelChooserDlg(
                    selectables=[TaurusElementType.Attribute],
                    listedModels=listedModelNames)
        if ok:
            models = OrderedDict()
            for r in res:
                m = taurus.Attribute(r)
                models[m.getFullName()] = m

            for k, v in listedTaurusPlotDataItems.items():
                self.plot_item.removeItem(v)
                self.legend.removeItem(v.name())

            for modelName, model in models.items():
                if modelName in listedModelNames:
                    self.plot_item.addItem(listedTaurusPlotDataItems[modelName])
                elif modelName not in listedModelNames:
                    # TODO use simplename for the legend label
                    # TODO support labels
                    taurusplotDataItem = TaurusPlotDataItem(name=model.getSimpleName())
                    taurusplotDataItem.setModel(modelName)
                    self.plot_item.addItem(taurusplotDataItem)


if __name__ == '__main__':
    import sys
    import numpy
    import pyqtgraph as pg
    from taurus.qt.qtgui.extra_pyqtgraph.taurusmodelchoosertool import TaurusModelChooserTool
    from taurus.qt.qtgui.application import TaurusApplication
    from taurus.qt.qtgui.extra_pyqtgraph.taurusplotdataitem import TaurusPlotDataItem

    app = TaurusApplication()

    # a standard pyqtgraph widget
    w = pg.PlotWidget()

    #add legend to the plot, for that we have to give a name to plot items
    w.addLegend()

    # adding a regular data item (non-taurus)
    c1 = pg.PlotDataItem(name='st plot',pen='b', fillLevel=0, brush='c')
    c1.setData(numpy.arange(300) / 300.)
    w.addItem(c1)

    # adding a taurus data item
    c2 = TaurusPlotDataItem(name='st2 plot',pen='r', symbol='o')
    c2.setModel('sys/tg_test/1/wave')

    w.addItem(c2)

    #attach plot item contained in the PlotWidget to a new TaurusModelChooserTool
    tmCt = TaurusModelChooserTool()
    tmCt.attachToPlotItem(w.getPlotItem());

    w.show()

    sys.exit(app.exec_())