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

from taurus import Attribute
from taurus.core import TaurusEventType
from taurus.qt.qtgui.base import TaurusBaseComponent
from pyqtgraph import PlotDataItem


class TaurusPlotDataItem(PlotDataItem, TaurusBaseComponent):
    """A taurus-ified PlotDataItem"""

    def __init__(self, *args, **kwargs):
        """
        Accepts same args and kwargs as PlotDataItem, plus:
        :param xModel: (str) Taurus model name for abscissas values.
                       Default=None
        :param yModel: (str) Taurus model name for ordinate values.
                       Default=None
        """
        xModel = kwargs.pop('xModel', None)
        yModel = kwargs.pop('yModel', None)
        PlotDataItem.__init__(self, *args, **kwargs)
        TaurusBaseComponent.__init__(self, 'TaurusBaseComponent')
        self._x = None
        self._y = None
        self.xModel = None
        if xModel is not None:
            self.setXmodel(xModel)
        if yModel is not None:
            self.setModel(yModel)

    def setXmodel(self, xModel):
        if xModel is None:
            if self.xModel is not None:
                self.xModel.removeListener(self)
            self.xModel = None
            return
        self.xModel = Attribute(xModel)
        self._x = self.xModel.read().rvalue
        self.xModel.addListener(self)

    def handleEvent(self, evt_src, evt_type, evt_value):
        if evt_type not in (TaurusEventType.Change, TaurusEventType.Periodic):
            return
        yModel = self.getModelObj()
        if yModel == evt_src and yModel is not None:
            self._y = evt_value.rvalue
        if self.xModel == evt_src and self.xModel is not None:
            self._x = evt_value.rvalue
        self.setData(x=self._x, y=self._y)


if __name__ == '__main__':
    import sys
    import numpy
    import pyqtgraph as pg
    from taurus.qt.qtgui.application import TaurusApplication
    from taurus.qt.qtgui.extra_pyqtgraph.taurusplotdataitem import TaurusPlotDataItem

    app = TaurusApplication()

    # a standard pyqtgraph plot_item
    w = pg.PlotWidget()

    #add legend to the plot, for that we have to give a name to plot items
    w.addLegend()

    # adding a regular data item (non-taurus)
    c1 = pg.PlotDataItem(name='st plot', pen='b', fillLevel=0, brush='c')
    c1.setData(numpy.arange(300) / 300.)
    w.addItem(c1)

    # adding a taurus data item
    c2 = TaurusPlotDataItem(name='st2 plot', pen='r', symbol='o')
    c2.setModel('eval:Quantity(rand(256),"m")')

    # c2.setXmodel('eval:Quantity(rand(256),"m")')

    w.addItem(c2)

    w.show()
    sys.exit(app.exec_())
