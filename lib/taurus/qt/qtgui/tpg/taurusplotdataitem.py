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
__all__ = ["TaurusPlotDataItem"]

import copy
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
            self.setXModel(xModel)
        if yModel is not None:
            self.setModel(yModel)

        self.registerConfigProperty(self.getOpts, self.setOpts, 'opts')
        self.setModelInConfig(True)
        self.registerConfigProperty(self.getXModelName,
                                    self.setXModel, 'XModel')

    def setXModel(self, xModel):
        if not xModel:
            if self.xModel is not None:
                self.xModel.removeListener(self)
            self.xModel = None
            return
        self.xModel = Attribute(xModel)
        self._x = self.xModel.read().rvalue
        self.xModel.addListener(self)

    def getXModelName(self):
        if self.xModel is None:
            return None
        else:
            return self.xModel.getFullName()

    def handleEvent(self, evt_src, evt_type, evt_value):
        if evt_type not in (TaurusEventType.Change, TaurusEventType.Periodic):
            return
        yModel = self.getModelObj()
        if yModel == evt_src and yModel is not None:
            self._y = evt_value.rvalue
        if self.xModel == evt_src and self.xModel is not None:
            self._x = evt_value.rvalue
        self.setData(x=self._x, y=self._y)

    def getOpts(self):
        from taurus.qt.qtgui.tpg import serialize_opts
        return serialize_opts(copy.copy(self.opts))

    def setOpts(self, opts):
        # creates QPainters (QPen or QBrush) from a pickle loaded file
        # for adapt the serialized objects into PlotDataItem properties

        from taurus.qt.qtgui.tpg import deserialize_opts
        self.opts = deserialize_opts(opts)

        # This is a workaround for the following pyqtgraph's bug:
        # https://github.com/pyqtgraph/pyqtgraph/issues/531
        if opts['connect'] == 'all':
            self.opts['connect'] = 'all'
        elif opts['connect'] == 'pairs':
            self.opts['connect'] = 'pairs'
        elif opts['connect'] == 'finite':
            self.opts['connect'] = 'finite'

    def getFullModelNames(self):
        return (self.getXModelName(), self.getFullModelName())


if __name__ == '__main__':
    import sys
    import numpy
    import pyqtgraph as pg
    from taurus.qt.qtgui.application import TaurusApplication
    from taurus.qt.qtgui.tpg import TaurusPlotDataItem
    from taurus.external.qt import Qt
    from taurus.qt.qtgui.tpg import TaurusModelChooserTool

    app = TaurusApplication()

    # a standard pyqtgraph plot_item
    w = pg.PlotWidget()

    #add legend to the plot, for that we have to give a name to plot items
    w.addLegend()

    # adding a regular data item (non-taurus)
    c1 = pg.PlotDataItem(name='st plot', pen='b', fillLevel=0, brush='c')
    c1.setData(numpy.arange(300) / 300.)
    w.addItem(c1)

    pen = pg.mkPen(color='r', style=4)
    brush = pg.mkBrush(color='b')
    brush.setStyle(3)

    # adding a taurus data item
    # c2 = TaurusPlotDataItem(name='st2 plot', pen='r', symbol='o')
    c2 = TaurusPlotDataItem(pen=pen, name='foo')
    # c2 = TaurusPlotDataItem()

    # c2.loadConfigFile('tmp/conf.cfg')

    c2.setModel('eval:Quantity(rand(256),"m")')
    # c2.setModel('sys/tg_test/1/wave')
    # c2.setModel(None)
    # c2.setXModel(None)

    # c2.setXModel('eval:Quantity(rand(256),"m")')

    w.addItem(c2)


    # ...and remove it after a while
    def rem():
        w.removeItem(c2)
    Qt.QTimer.singleShot(2000, rem)

    modelchooser = TaurusModelChooserTool(itemClass=TaurusPlotDataItem)
    modelchooser.attachToPlotItem(w.getPlotItem())

    w.show()

    res = app.exec_()


    # config = c2.createConfig()
    # print config

    # c2.saveConfigFile('tmp/conf.cfg')

    sys.exit(res)
