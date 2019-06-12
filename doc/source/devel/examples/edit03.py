import sys
from taurus.external.qt import Qt
from taurus.qt.qtgui.container import TaurusWidget
from taurus.qt.qtgui.display import TaurusLabel
from taurus.qt.qtgui.input import TaurusWheelEdit
from taurus.qt.qtgui.application import TaurusApplication

app = TaurusApplication(sys.argv, cmd_line_parser=None)

panel = TaurusWidget()
layout = Qt.QHBoxLayout()
panel.setLayout(layout)

w1 = TaurusLabel()
w2 = TaurusLabel()
w3 = TaurusWheelEdit()
w4 = TaurusLabel()
layout.addWidget(w1)
layout.addWidget(w2)
layout.addWidget(w3)
layout.addWidget(w4)
panel.setModel('sys/taurustest/1')
w1.setModel('sys/taurustest/1/position#label')
w2.setModel('sys/taurustest/1/position#rvalue.magnitude')
w3.setModel('sys/taurustest/1/position#rvalue.magnitude')
w4.setModel('sys/taurustest/1/position#unit')

panel.show()
sys.exit(app.exec_())
