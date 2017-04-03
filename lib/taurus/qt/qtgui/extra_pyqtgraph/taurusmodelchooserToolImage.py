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
from taurus.core import TaurusElementType
from taurus.qt.qtgui.panel.taurusmodelchooser import TaurusModelChooser
import taurus


class TaurusModelChooserToolImage(QtGui.QAction):

    def __init__(self, parent=None):
        QtGui.QAction.__init__(self, parent)
        self.image_item = None

    def attachToImageItem(self, plot_item):
        self.image_item = plot_item.items[0]
        view_from_image = plot_item.getViewBox()
        menu = view_from_image.menu
        model_chooser = QtGui.QAction('Model chooser', menu)
        model_chooser.triggered.connect(self.onTriggered)
        menu.addAction(model_chooser)

    def onTriggered(self):
        item = self.image_item
        listModelName = []
        print(item.getFullModelName())
        if item.getFullModelName() is None:
            listModelName = None
        else:
            listModelName.append(item.getFullModelName())

        res, ok = TaurusModelChooser.modelChooserDlg(
                    selectables=[TaurusElementType.Attribute],
                    singleModel=True, listedModels=listModelName)
        if ok:
            if len(res) != 0:
                model = taurus.Attribute(res[0])
                item.setModel(model.getFullName())


if __name__ == '__main__':
    import sys
    from taurus.qt.qtgui.extra_pyqtgraph.taurusmodelchooserToolImage import TaurusModelChooserToolImage
    from taurus.qt.qtgui.application import TaurusApplication
    from taurus.qt.qtgui.extra_pyqtgraph.taurusimageitem import TaurusImageItem
    import pyqtgraph as pg

    app = TaurusApplication()

    plot_widget = pg.PlotWidget()
    plot_item = plot_widget.getPlotItem()

    image_item = TaurusImageItem()

    # Add taurus 2D image data
    image_item.setModel('eval:rand(256,256)')
    plot_item.addItem(image_item)

    plot_item.showAxis('left', show=False)
    plot_item.showAxis('bottom', show=True)

    tmCt = TaurusModelChooserToolImage()
    tmCt.attachToImageItem(plot_item)

    plot_widget.show()
    sys.exit(app.exec_())