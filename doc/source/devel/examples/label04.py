import sys
from taurus.external.qt import Qt
from taurus.qt.qtgui.container import TaurusWidget
from taurus.qt.qtgui.display import TaurusLabel
from taurus.qt.qtgui.application import TaurusApplication

app = TaurusApplication(sys.argv, cmd_line_parser=None)
panel = TaurusWidget()
layout = Qt.QVBoxLayout()
panel.setLayout(layout)
panel.setModel('sys/taurustest/1')
w1 = TaurusLabel()
w2 = TaurusLabel()
w3 = TaurusLabel()
w1.setModel('sys/taurustest/1/state')
w2.setModel('sys/taurustest/1/position')
w3.setModel('sys/taurustest/1/simulationmode')
w1.setShowQuality(False)

layout.addWidget(w1)
layout.addWidget(w2)
layout.addWidget(w3)
panel.show()

sys.exit(app.exec_())
