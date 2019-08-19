#!/usr/bin/env python

import sys
from taurus.qt.qtgui.plot import TaurusTrend
from taurus.qt.qtgui.application import TaurusApplication

app = TaurusApplication(sys.argv, cmd_line_parser=None)
##########################
# BEGIN EXAMPLE CODE
##########################

panel = TaurusTrend()
model = ['sys/taurustest/1/position']
panel.setXIsTime(True)  # to show the x values as time
panel.setModel(model)

########################
# END EXAMPLE CODE
########################
panel.show()
sys.exit(app.exec_())
