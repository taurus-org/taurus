#!/usr/bin/env python

import sys
from taurus.qt import Qt
from taurus.qt.qtgui.plot import TaurusTrend

app = Qt.QApplication(sys.argv)
##########################
#BEGIN EXAMPLE CODE
##########################

panel = TaurusTrend()
model = ['sys/taurustest/1/position']
panel.setXIsTime(True) #to show the x values as time
panel.setModel(model)

########################
#END EXAMPLE CODE
########################
panel.show()
sys.exit(app.exec_())
