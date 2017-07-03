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
import pyqtgraph as pg
import numpy as np


if __name__ == '__main__':

    """
    This is an example of how to assign specific labels to a given axis.
    First we have to define this labels names, and extract the axis from
    plotItem or Widget and call the method AxisItem.setTicks().
    """

    app = TaurusApplication()

    w = pg.PlotWidget()

    ticks = [list(zip(range(5), ('a', 'b', 'c', 'd', 'e')))]
    xax = w.getAxis('bottom')
    xax.setTicks(ticks)
    w.plot(np.arange(5))


    w.show()

    sys.exit(app.exec_())