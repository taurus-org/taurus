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
__all__ = ["TaurusModelChooserToolImage"]

from taurus.external.qt import QtGui
from taurus.core import TaurusElementType
from taurus.qt.qtgui.panel.taurusmodelchooser import TaurusModelChooser
from taurus.qt.qtgui.tpg.taurusimageitem import TaurusImageItem


class TaurusModelChooserToolImage(QtGui.QAction):

    def __init__(self, parent=None):
        QtGui.QAction.__init__(self, parent)
        self._plot_item = None

    def attachToPlotItem(self, plot_item):
        self._plot_item = plot_item
        view = plot_item.getViewBox()
        menu = view.menu
        model_chooser = QtGui.QAction('Model chooser', menu)
        model_chooser.triggered.connect(self.onTriggered)
        menu.addAction(model_chooser)

    def onTriggered(self):

        imageItem = None

        for item in self._plot_item.items:
            if isinstance(item, TaurusImageItem):
                imageItem = item
                break

        if imageItem is None:
            imageItem = TaurusImageItem()
        modelName = imageItem.getFullModelName()
        if modelName is None:
            listedModels = []
        else:
            listedModels = [modelName]

        res, ok = TaurusModelChooser.modelChooserDlg(
                    selectables=[TaurusElementType.Attribute],
                    singleModel=True, listedModels=listedModels)
        print(ok)
        if ok:
            if res:
                model = res[0]
            else:
                model = None
            imageItem.setModel(model)



if __name__ == '__main__':
    import sys
    from taurus.qt.qtgui.tpg.taurusmodelchooserToolImage import TaurusModelChooserToolImage
    from taurus.qt.qtgui.application import TaurusApplication
    from taurus.qt.qtgui.tpg.taurusimageitem import TaurusImageItem
    import pyqtgraph as pg

    app = TaurusApplication()

    plot_widget = pg.PlotWidget()
    plot_item = plot_widget.getPlotItem()

    image_item = TaurusImageItem()

    # Add taurus 2D image data
    image_item.setModel('eval:rand(256,256)')

    plot_item.addItem(image_item)

    plot_item.showAxis('left', show=False)
    plot_item.showAxis('bottom', show=False)

    tmCt = TaurusModelChooserToolImage()
    tmCt.attachToPlotItem(plot_item)

    plot_widget.show()
    sys.exit(app.exec_())