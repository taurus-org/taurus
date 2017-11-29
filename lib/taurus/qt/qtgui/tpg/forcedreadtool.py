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
__all__ = ["ForcedReadTool"]

from taurus.external.qt import QtGui, QtCore
from taurus.qt.qtcore.configuration.configuration import BaseConfigurableClass


class ForcedReadTool(QtGui.QWidgetAction, BaseConfigurableClass):
    """
    This tool provides a menu option to control the "Forced Read" period of
    Plot data items that implement a `setForcedReadPeriod` method
    (see, e.g. :meth:`TaurusTrendSet.setForcedReadPeriod`).

    The force-read feature consists on forcing periodic attribute reads for
    those attributes being plotted with a :class:`TaurusTrendSet` object.
    This allows to force plotting periodical updates even for attributes
    for which the taurus polling is not enabled.
    Note that this is done at the widget level and therefore does not affect
    the rate of arrival of events for other widgets connected to the same
    attributes

    This tool inserts an action with a spinbox and emits a `valueChanged`
    signal whenever the value is changed.

    The connection between the data items and this tool can be done manually
    (by connecting to the `valueChanged` signal or automatically, if
    :meth:`autoconnect()` is `True` (default). The autoconnection feature works
    by discovering the compliant data items that share associated to the
    plot_item.

    This tool is implemented as an Action, and provides a method to attach it
    to a :class:`pyqtgraph.PlotItem`
    """
    valueChanged = QtCore.pyqtSignal(int)

    def __init__(self, parent=None, period=0, text='Forced read',
                 autoconnect=True):
        BaseConfigurableClass.__init__(self)
        QtGui.QWidgetAction.__init__(self, parent)

        # defining the widget
        self._w = QtGui.QWidget()
        self._w.setLayout(QtGui.QHBoxLayout())
        tt = 'Period between forced readings.\nSet to 0 to disable'
        self._w.setToolTip(tt)
        self._label = QtGui.QLabel(text)
        self._w.layout().addWidget(self._label)
        self._sb = QtGui.QSpinBox()
        self._w.layout().addWidget(self._sb)
        self._sb.setRange(0, 604800000)
        self._sb.setValue(period)
        self._sb.setSingleStep(500)
        self._sb.setSuffix(' ms')
        self._sb.setSpecialValueText('disabled')
        self._autoconnect = autoconnect

        self.setDefaultWidget(self._w)

        # register config properties
        self.registerConfigProperty(self.period, self.setPeriod, 'period')
        self.registerConfigProperty(self.autoconnect, self.setAutoconnect,
                                    'autoconnect')

        # internal conections
        self._sb.valueChanged[int].connect(self._onValueChanged)

    def _onValueChanged(self, period):
        """emit valueChanged and update all associated trendsets (if
        self.autoconnect=True
        """
        self.valueChanged.emit(period)
        if self.autoconnect() and self.plot_item is not None:
            for item in self.plot_item.listDataItems():
                if hasattr(item, 'setForcedReadPeriod'):
                    item.setForcedReadPeriod(period)

    def attachToPlotItem(self, plot_item):
        """Use this method to add this tool to a plot

        :param plot_item: (PlotItem)
        """
        menu = plot_item.getViewBox().menu
        menu.addAction(self)
        self.plot_item = plot_item
        # force an update of period for connected trendsets
        self._onValueChanged(self.period())

    def autoconnect(self):
        """Returns autoconnect state

        :return: (bool)
        """
        return self._autoconnect

    def setAutoconnect(self, autoconnect):
        """Set autoconnect state. If True, the tool will autodetect trendsets
        associated to the plot item and will call setForcedReadPeriod
        on each of them for each change. If False, it will only emit a
        valueChanged signal and only those connected to it will be notified
        of changes

        :param autoconnect: (bool)
        """
        self._autoconnect = autoconnect

    def period(self):
        """Returns the current period value (in ms)

        :return: (int)
        """
        return self._sb.value()

    def setPeriod(self, value):
        """Change the period value. Use 0 for disabling

        :param period: (int) period in ms
        """
        self._sb.setValue(value)


if __name__ == '__main__':
    import taurus
    taurus.setLogLevel(taurus.Debug)
    import sys
    from taurus.qt.qtgui.application import TaurusApplication
    from taurus.qt.qtgui.tpg import TaurusTrendSet, DateAxisItem
    import pyqtgraph as pg
    from taurus.qt.qtgui.tpg import ForcedReadTool

    app = TaurusApplication()

    w = pg.PlotWidget()

    axis = DateAxisItem(orientation='bottom')
    w = pg.PlotWidget()
    axis.attachToPlotItem(w.getPlotItem())

    # test adding the curve before the tool
    ts1 = TaurusTrendSet(name='before', symbol='o')
    ts1.setModel('eval:rand()+1')

    w.addItem(ts1)

    fr = ForcedReadTool(w, period=1000)
    fr.attachToPlotItem(w.getPlotItem())

    # test adding the curve after the tool
    ts2 = TaurusTrendSet(name='after', symbol='+')
    ts2.setModel('eval:rand()')

    w.addItem(ts2)

    w.show()

    ret = app.exec_()

    import pprint
    pprint.pprint(fr.createConfig())

    sys.exit(ret)