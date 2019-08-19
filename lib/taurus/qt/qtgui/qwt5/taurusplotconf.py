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
TaurusPlotConf: widget for configurating the contents and appearance of a TaurusPlot
"""
from __future__ import print_function
from __future__ import absolute_import

raise NotImplementedError('Under Construction!')

import taurus.core
from taurus.external.qt import Qt, Qwt5
from taurus.qt.qtgui.util.ui import UILoadable

from . import curveprops
try:
    import taurus.qt.qtgui.extra_nexus as extra_nexus
except:
    extra_nexus = None


__all__ = ['TaurusPlotConfDlg']


@UILoadable(with_ui='ui')
class TaurusPlotConfDlg(Qt.QWidget):
    ''' A configuration dialog for TaurusPlot.

    The dialog uses a Model/View design:
      - it uses a :class:`CurvesTableModel` for describing the curves
        configuration
      - it has two views on that model: a :class:`QTableView` and a
        :class:`CurvePropertiesView`.
      - The selection is managed via a :class:`ExtendedSelectionModel` which is
        shared by both views.

    It also has a data sources browser which is used to select the sources of
    the data to be used by the curves. Currently supported sources are: Tango
    attributes, Nexus/HDF5 datasets, and column organized ASCII data. Apart from
    this, the dialog allows to use mathematical expression and the given sources
    to assign values to the curves


    When the changes are applied (eg, when the Apply button is pressed), the
    model is used to (re)configure the plot.
    '''

    def __init__(self, parent=None, curves=None):
        super(TaurusPlotConfDlg, self).__init__(parent)
        self.loadUi()

        ###################################
        #@todo: this block should disappear once we can use taurusuic4 to include taurus widgets
        self.ui.propView = self.__replaceWidget(
            curveprops.CurvePropertiesView(), self.ui.propView)
        from taurus.qt.qtgui.panel import TaurusModelSelectorTree
        tangoTree = TaurusModelSelectorTree(parent=None,
                                            selectables=[
                                                taurus.core.taurusbasetypes.TaurusElementType.Attribute],
                                            buttonsPos=Qt.Qt.RightToolBarArea)
        self.ui.tangoTree = self.__replaceWidget(tangoTree, self.ui.tangoTree)
#        l=self.ui.propView.parent().layout()
#        self.ui.propView = curveprops.CurvePropertiesView()
#        l.insertWidget(0, self.ui.propView)
#        l=self.ui.tangoTree.parent().layout()
#        from taurus.qt.qtgui.panel import TaurusModelSelectorTree
#        self.ui.tangoTree = TaurusModelSelectorTree(parent = None,
#                                                     selectables=[taurus.core.taurusbasetypes.TaurusElementType.Attribute],
#                                                     buttonsPos=Qt.Qt.RightToolBarArea)
#        l.insertWidget(0, self.ui.tangoTree)
        ####################################

        if extra_nexus is not None:
            self.ui.nexusBrowser = self.__replaceWidget(
                extra_nexus.TaurusNeXusBrowser(), self.ui.nexusBrowser)

        self.model = curveprops.CurvesTableModel(curves)
        self.selectionModel = curveprops.ExtendedSelectionModel(self.model)
        self.ui.curvesTable.setModel(self.model)
        self.ui.propView.setModel(self.model)
        self.ui.curvesTable.setSelectionModel(self.selectionModel)
        self.ui.propView.setSelectionModel(self.selectionModel)

        # host
        host = taurus.Authority().getNormalName()
        self.ui.tangoTree.setModel(host)

        # Connections
        self.ui.applyBT.clicked.connect(self.onApply)
        self.ui.reloadBT.clicked.connect(self.onReload)
        self.ui.cancelBT.clicked.connect(self.close)
        self.ui.tangoTree.addModels.connect(self.onModelsAdded)

    def __replaceWidget(self, new, old, layout=None):
        if layout is None:
            layout = old.parent().layout()
        index = layout.indexOf(old)
        layout.removeWidget(old)
        old.setParent(None)
        layout.insertWidget(index, new)
        return new

    def onModelsAdded(self, models):
        print(models)
        nmodels = len(models)
        rowcount = self.model.rowCount()
        self.model.insertRows(rowcount, nmodels)
        for i, m in enumerate(models):
            self.model.setData(self.model.index(rowcount + i, curveprops.Y),
                               value=m)

    def onApply(self):
        print("APPLY!!! (todo)")
        curveConfs = self.model.dumpData()

        for c in curveConfs:
            print(repr(c))

    def onReload(self):
        print("RELOAD!!! (todo)")


class demo(Qt.QDialog):

    def __init__(self, parent=None, curves=None):
        super(demo, self).__init__(parent)

        if curves is None:
            curves = [curveprops.CurveConf(xsrc='', ysrc='a/b/c/d', properties=None, title="tangocurve", vis=Qwt5.QwtPlot.yLeft),
                      curveprops.CurveConf(
                xsrc='[1,2,3]', ysrc='=#2.x**2', properties=None, title="parab", vis=Qwt5.QwtPlot.yLeft)
            ]

        # create table
        self.model = curveprops.CurvesTableModel(curves)
#        self.selection = Qt.QItemSelectionModel(self.model)

        self.table = Qt.QTableView(self)
        self.table.setModel(self.model)

#        print "!!!!!!!!",self.table.selectionModel()
#        self.table.setItemDelegate(commandDelegate(self))

        # create buttons
        self.posSB = Qt.QSpinBox()
        self.newSB = Qt.QSpinBox()
        self.addBT = Qt.QPushButton(u"Add")
        self.remBT = Qt.QPushButton(u"Rem")
        self.dataBT = Qt.QPushButton(u"Data")

        # put widgets in the layout
        mainLayout = Qt.QGridLayout()
        mainLayout.addWidget(self.table, 0, 0, 1, 2)
        mainLayout.addWidget(self.posSB, 1, 0)
        mainLayout.addWidget(self.newSB, 1, 1)
        mainLayout.addWidget(self.addBT, 2, 0)
        mainLayout.addWidget(self.remBT, 2, 1)
        mainLayout.addWidget(self.dataBT, 3, 0)
        self.setLayout(mainLayout)

        # connections
        self.addBT.clicked.connect(self.onAdd)
        self.remBT.clicked.connect(self.onRem)
        self.dataBT.clicked.connect(self.onData)

        # misc
        self.table.resizeColumnsToContents()
#        self.table.setShowGrid(False)
#        self.table.setSelectionMode(self.table.ExtendedSelection)
#        self.table.setSelectionBehavior(Qt.QAbstractItemView.SelectItems)
        self.model.mimeTypes()

    def onAdd(self):
        self.model.insertRows(position=self.posSB.value(),
                              rows=self.newSB.value())

    def onRem(self):
        self.model.removeRows(position=self.posSB.value(),
                              rows=self.newSB.value())

    def onData(self):
        cmds = self.model.dumpData()
        print(self.model.curves)


def main1():
    from taurus.qt.qtgui.application import TaurusApplication

    app = TaurusApplication(sys.argv, cmd_line_parser=None)
    form = demo()
    form.show()
    sys.exit(app.exec_())


def main2():
    from taurus.qt.qtgui.application import TaurusApplication

    app = TaurusApplication(sys.argv, cmd_line_parser=None)

    curves = [curveprops.CurveConf(xsrc='', ysrc='tango://host:1000/a/b/c/d', properties=None, title="tangocurve", vis=Qwt5.QwtPlot.yLeft),
              curveprops.CurveConf(
                  xsrc='=[1,2,3]', ysrc='=#2.x**2', properties=None, title="parab", vis=Qwt5.QwtPlot.yLeft)
              ]
    form = TaurusPlotConfDlg(curves=curves)
    form.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    import sys
    main2()
