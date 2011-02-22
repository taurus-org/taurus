#!/usr/bin/env python

import sys
from PyQt4 import Qt
from taurus.qt.qtgui.plot import TaurusPlot

app = Qt.QApplication(sys.argv)
##########################
#BEGUIN EXAMPLE CODE
##########################

panel = TaurusPlot()
model = ['sys/taurustest/1/abscissas|sys/taurustest/1/curve']
panel.setModel(model)

########################
#END EXAMPLE CODE
########################
panel.setVisible(True)
sys.exit(app.exec_())
