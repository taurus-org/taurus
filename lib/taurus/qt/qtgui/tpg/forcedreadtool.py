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
    This tool adds the "force read" feature to the PlotItem to which it is
    attached, and it inserts a spinbox in at the menu to set the period
    (or disable).

    When enabled it emits a timeout() signal with the given period

    The force-read feature consists on forcing periodic attribute reads for
    those attributes being plotted with a :class:`TaurusTrendSet` object.
    This allows to force plotting periodical updates even for attributes
    for which the taurus polling is not enabled.
    Note that this is done at the widget level and therefore does not affect
    the rate of arrival of events for other widgets connected to the same
    attributes

    It is implemented as an Action, and provides a method to attach it to
     a :class:`pyqtgraph.PlotItem`
    """
    timeout = QtCore.pyqtSignal()

    def __init__(self, parent=None, period=0, text='Forced read'):
        BaseConfigurableClass.__init__(self)
        QtGui.QWidgetAction.__init__(self, parent)

        self._timer = QtCore.QTimer()

        # defining the widget
        self._w = QtGui.QWidget()
        self._w.setLayout(QtGui.QHBoxLayout())
        tt = 'Period between forced readings.\nSet to 0 to disable'
        self._w.setToolTip(tt)
        self._label = QtGui.QLabel(text)
        self._w.layout().addWidget(self._label)
        self._sb = QtGui.QSpinBox()
        self._w.layout().addWidget(self._sb)
        self._sb.setValue(period)
        self._sb.setRange(0, 604800000)
        self._sb.setSingleStep(100)
        self._sb.setSuffix(' ms')
        self._sb.setSpecialValueText('disabled')

        self.setDefaultWidget(self._w)

        self.registerConfigProperty(self,period, self.setPeriod, 'period')

        # self._sb.valueChanged[int].connect(self._onValueChanged)
        self._sb.editingFinished.connect(self._onValueChanged)
        self._timer.timeout.connect(self.timeout)

    @property
    def period(self):
        return self._sb.value()

    @period.setter
    def setPeriod(self, value):
        self._sb.setValue(value)

    def attachToPlotItem(self, plot_item):
        """Use this method to add this tool to a plot

        :param plot_item: (PlotItem)
        """
        menu = plot_item.getViewBox().menu
        menu.addAction(self)

    def _onValueChanged(self, period=None):
        if period is None:
            period = self._sb.value()
        if period > 0:
            self._timer.start(period)
        else:
            self._timer.stop()


if __name__ == '__main__':
    import sys
    from taurus.qt.qtgui.application import TaurusApplication
    from taurus.qt.qtgui.tpg import TaurusTrendSet
    import pyqtgraph as pg

    app = TaurusApplication()

    w = pg.PlotWidget()

    fr = ForcedReadTool()
    fr.attachToPlotItem(w.getPlotItem())

    # ts = TaurusTrendSet(name='foo')
    # ts.setModel('eval:rand(5)')
    # w.addItem(ts)
    # fr.timeout.connect(ts.onForcedRead)  # TODO: this should be done by the ts

    def onForcedRead():
        print 'REFRESH'

    fr.timeout.connect(onForcedRead)  # TODO: this should be done by the ts

    w.show()

    sys.exit(app.exec_())