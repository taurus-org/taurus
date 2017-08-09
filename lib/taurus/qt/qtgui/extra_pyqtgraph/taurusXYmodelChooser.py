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

import taurus
from taurus.qt.qtgui.extra_pyqtgraph.curvesmodel import (
    TaurusItemConfDlg, TaurusItemConf)
from taurus.external.qt import QtGui
from taurus.qt.qtgui.extra_pyqtgraph.taurusplotdataitem import (
    TaurusPlotDataItem)
from collections import OrderedDict


class TaurusXYModelChooserTool(QtGui.QAction):

    def __init__(self, parent=None):
        QtGui.QAction.__init__(self, 'Model XY chooser', parent)
        self.triggered.connect(self.onTriggered)
        self.plot_item = None
        self.legend = None
        self._curveColors = None

    def attachToPlotItem(self, plot_item,
                         parentWidget=None, curve_colors=None):
        self.plot_item = plot_item
        self._curveColors = curve_colors
        if self.plot_item.legend is not None:
            self.legend = self.plot_item.legend

        menu = self.plot_item.getViewBox().menu
        menu.addAction(self)
        self.setParent(parentWidget or menu)

    def onTriggered(self):

        currentModelItems = dict()
        currentModelNames = []
        taurusItems = []

        for curve in self.plot_item.listDataItems():
            if isinstance(curve, TaurusPlotDataItem):
                currentModelNames.append(curve.getFullModelNames())
                currentModelItems[
                    curve.getFullModelNames()] = (curve, curve.getViewBox())
                item = TaurusItemConf(YModel=curve.getFullModelName(),
                                      XModel=curve.getXModelName(),
                                      name=curve.name())
                taurusItems.append(item)

        conf, ok = TaurusItemConfDlg.showDlg(
            parent=self.parent(), taurusItemConf=taurusItems)

        # print conf, ok

        if ok:
            yModels = OrderedDict()
            xModels = OrderedDict()
            curve_name = OrderedDict()
            for c in conf:
                try:
                    # print c.yModel, type(c.yModel)
                    m = taurus.Attribute(c.yModel)
                    n = c.xModel
                    name = c.curveLabel
                    yModels[n, m.getFullName()] = m
                    xModels[n, m.getFullName()] = n
                    curve_name[n, m.getFullName()] = name
                except Exception as e:
                    from taurus import warning
                    warning(e)

            for k, v in currentModelItems.items():
                curve, parent = v
                self.plot_item.removeItem(curve)
                parent.removeItem(curve)
                if self.legend is not None:
                    self.legend.removeItem(curve.name())

            for modelName, model in yModels.items():
                # print modelName, model
                if modelName in currentModelNames:
                    item, parent = currentModelItems[modelName]
                    X = xModels[modelName]
                    c_name = curve_name[modelName]
                    item.opts['name'] = c_name
                    item.setXModel(X)
                    self.plot_item.addItem(item)

                    # checks if the viewBox associated to
                    # TaurusPlotDataItem(curve), it is the main view or not.
                    # If is the same, we dont have to addItem again in the
                    # parent (viewBox). This avoid duplicate objects in the
                    # ViewBox.scene() contained in PlotItem.
                    if parent is not self.plot_item.getViewBox():
                        parent.addItem(item)

                elif modelName not in currentModelNames:
                    x_model = xModels[modelName]
                    y_model = yModels[modelName]
                    c_name = curve_name[modelName]
                    item = TaurusPlotDataItem(
                        xModel=x_model, yModel=y_model, name=c_name)

                    if self._curveColors is not None:
                        item.setPen(self._curveColors.next().color())
                    self.plot_item.addItem(item)

