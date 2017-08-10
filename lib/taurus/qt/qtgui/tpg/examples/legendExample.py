# -*- coding: utf-8 -*-
"""
Demonstrates basic use of LegendItem

"""
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui




## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys

    app = QtGui.QApplication([])

    plt = pg.PlotWidget()
    # plt = pg.plot()
    plt.setWindowTitle('pyqtgraph example: PLOT')

    plt2 = QtGui.QGraphicsView(QtGui.QGraphicsScene())
    plt2.setWindowTitle('pyqtgraph example: Legend')
    plt2.setBackgroundBrush(QtGui.QBrush(QtGui.QColor('black')))

    l = pg.LegendItem((100,60), offset=(70,30))  # args are (size, offset)

    c1 = plt.plot([1, 3, 2, 4], pen='r', symbol='o', symbolPen='r',
                  symbolBrush=0.5, name='red plot')
    c2 = plt.plot([2, 1, 4, 3], pen='g', fillLevel=0,
                  fillBrush=(255, 255, 255, 30), name='green plot')
    c3 = plt.plot(range(7), pen='c', fillLevel=0)

    for dataitem in plt.getPlotItem().listDataItems():
        if dataitem.name():
            l.addItem(dataitem, dataitem.name())

    plt2.scene().addItem(l)
    plt.show()
    plt2.show()
    sys.exit(app.exec_())
