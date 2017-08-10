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
__all__ = ["TaurusImageItem"]

import sys
import taurus
from taurus.qt.qtgui.application import TaurusApplication
from taurus.qt.qtgui.base import TaurusBaseComponent
from pyqtgraph import ImageItem


class TaurusImageItem(ImageItem, TaurusBaseComponent):
    """
    Displays 2D and 3D image data
    """
    # TODO: clear image if .setModel(None)
    def __init__(self, *args, **kwargs):
        ImageItem.__init__(self, *args, **kwargs)
        TaurusBaseComponent.__init__(self, 'TaurusImageItem')

    def handleEvent(self, evt_src, evt_type, evt_val):
        try:
            data = evt_val.rvalue
            self.setImage(data)
        except Exception, e:
            self.warning('Exception in handleEvent: %s', e)



if __name__ == "__main__":
    import pyqtgraph as pg

    app = TaurusApplication()

    plot_widget = pg.PlotWidget()
    plot_item = plot_widget.getPlotItem()

    image_item = TaurusImageItem()

    #Add taurus 2D image data
    image_item.setModel('eval:randint(0,256,(16,16))')

    #add TarusImageItem to a PlotItem
    plot_item.addItem(image_item)

    #show or hide axis from the plot
    plot_item.showAxis('left', show=True)
    plot_item.showAxis('bottom', show=True)

    plot_widget.show()

    sys.exit(app.exec_())