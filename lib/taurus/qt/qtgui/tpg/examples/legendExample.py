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


"""
Example on how to use a separate widget (LegendItem) for the legend of a plot.
(Pure Qt)
"""

import pyqtgraph as pg
from pyqtgraph.Qt import QtGui
import sys


if __name__ == '__main__':

    app = QtGui.QApplication([])

    # instantiate the main plot
    plt = pg.PlotWidget()
    plt.setWindowTitle('pyqtgraph example: PLOT')

    # instantiate a graphics view to contain the legend
    gv = QtGui.QGraphicsView(QtGui.QGraphicsScene())
    gv.setWindowTitle('pyqtgraph example: Legend')
    gv.setBackgroundBrush(QtGui.QBrush(QtGui.QColor('black')))

    l = pg.LegendItem((100,60), offset=(70,30))  # args are (size, offset)
    gv.scene().addItem(l)

    # create 3 curves
    c1 = plt.plot([1, 3, 2, 4], pen='r', symbol='o', symbolPen='r',
                  symbolBrush=0.5, name='red plot')
    c2 = plt.plot([2, 1, 4, 3], pen='g', fillLevel=0,
                  fillBrush=(255, 255, 255, 30), name='green plot')
    c3 = plt.plot(range(7), pen='c', fillLevel=0)

    # add the **named** curves to the legend
    for dataitem in plt.getPlotItem().listDataItems():
        if dataitem.name():
            l.addItem(dataitem, dataitem.name())

    plt.show()
    gv.show()

    sys.exit(app.exec_())
