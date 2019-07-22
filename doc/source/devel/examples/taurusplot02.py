#!/usr/bin/env python

import sys
from taurus.qt.qtgui.plot import TaurusPlot
from taurus.qt.qtgui.application import TaurusApplication

app = TaurusApplication(sys.argv, cmd_line_parser=None)
##########################
# BEGUIN EXAMPLE CODE
##########################

panel = TaurusPlot()
model = ['sys/taurustest/1/abscissas|sys/taurustest/1/curve']
panel.setModel(model)

########################
# END EXAMPLE CODE
########################
panel.show()
sys.exit(app.exec_())
