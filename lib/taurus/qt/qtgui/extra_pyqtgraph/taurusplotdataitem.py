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


from taurus.qt.qtgui.base import TaurusBaseComponent
from pyqtgraph import PlotDataItem


class TaurusPlotDataItem(PlotDataItem, TaurusBaseComponent):
    """A taurus-ified PlotDataItem"""

    def __init__(self, *args, **kwargs):
        PlotDataItem.__init__(self, *args, **kwargs)
        TaurusBaseComponent.__init__(self, 'TaurusBaseComponent')

    def handleEvent(self, evt_src, evt_type, evt_value):
        try:
            y = evt_value.rvalue
            self.setData(y)
        except Exception, e:
            self.warning('Exception in handleEvent: %s', e)



if __name__ == '__main__':
    import sys
    import numpy
    import pyqtgraph as pg
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
    c2.setModel('eval:Quantity(rand(256),"m")')

    w.addItem(c2)

    w.show()

    sys.exit(app.exec_())