#!/usr/bin/env python

import sys
from taurus.external.qt import Qt
from taurus.qt.qtgui.plot import TaurusPlot, CurveAppearanceProperties
from taurus.qt.qtgui.application import TaurusApplication
app = TaurusApplication(sys.argv, cmd_line_parser=None)
##########################
# BEGIN EXAMPLE CODE
##########################

import numpy
from taurus.external.qt import Qwt5

panel = TaurusPlot()

rawdata1 = {"y": 5 * numpy.random.random(10), "name": "Random"}
rawdata2 = {"x": [1, 2, 5, 7], "y": [2, 3, 1, 4], "name": "Hand-written"}
rawdata3 = {"x": numpy.arange(0, 10, 0.1), "f(x)": "sqrt(x)"}

p1 = CurveAppearanceProperties(sStyle=Qwt5.QwtSymbol.Rect,
                               sSize=5,
                               sColor="green",
                               sFill=False,
                               lStyle=Qt.Qt.NoPen)

p2 = CurveAppearanceProperties(sStyle=Qwt5.QwtSymbol.Triangle,
                               sSize=8,
                               sColor="red",
                               sFill=True,
                               lColor="red",
                               lStyle=Qt.Qt.DashLine)

panel.attachRawData(rawdata1, properties=p1)
panel.attachRawData(rawdata2, properties=p2)
panel.attachRawData(rawdata3)


########################
# END EXAMPLE CODE
########################
panel.show()
sys.exit(app.exec_())
