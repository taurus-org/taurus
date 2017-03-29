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

import sys
from taurus.qt.qtgui.application import TaurusApplication
from taurus.qt.qtgui.base import TaurusBaseComponent
from pyqtgraph import ImageItem
import numpy as np


class TaurusImageItem(ImageItem, TaurusBaseComponent):
    """
    Displays 2D and 3D image data
    """
    def __init__(self, *args, **kwargs):
        ImageItem.__init__(self, *args, **kwargs)
        TaurusBaseComponent.__init__(self, 'TaurusImageView')

    def handleEvent(self, evt_src, evt_type, evt_val):
        try:
            data = evt_val.rvalue
            self.setImage(data)
        except Exception, e:
            self.warning('Exception in handleEvent: %s', e)


if __name__ == "__main__":
    import pyqtgraph as pg

    app = TaurusApplication()

    axis_view = pg.PlotItem()

    #set param AxisView for display the axis from the plot view

    image_item = TaurusImageItem()
    imv = pg.ImageView(view=axis_view, imageItem=image_item)

    #set a custom color map
    colors = [
        (0, 0, 0),
        (45, 5, 61),
        (84, 42, 55),
        (150, 87, 60),
        (208, 171, 141),
        (230, 230, 230)
    ]
    cmap = pg.ColorMap(pos=np.linspace(0.0, 1.0, 6), color=colors)
    imv.setColorMap(cmap)

    # Add random 3D image data
    # imv.setImage(np.random.normal(size=(100,200,200)))

    #Add taurus 2D image data
    image_item.setModel('eval:rand(256,256)')

    imv.show()
    sys.exit(app.exec_())