import sys
from taurus.qt import Qt
from taurus.qt.qtgui.container import TaurusWidget
from taurus.qt.qtgui.display import TaurusValueLabel, TaurusConfigLabel
from taurus.qt.qtgui.input import TaurusWheelEdit

app = Qt.QApplication(sys.argv)

panel = TaurusWidget()
layout = Qt.QHBoxLayout()
panel.setLayout(layout)

w1 = TaurusConfigLabel()
w2 = TaurusValueLabel()
w3 = TaurusWheelEdit()
w4 = TaurusConfigLabel()
layout.addWidget(w1)
layout.addWidget(w2)
layout.addWidget(w3)
layout.addWidget(w4)
w1.setUseParentModel(True)
w2.setUseParentModel(True)
w3.setUseParentModel(True)
w4.setUseParentModel(True)
panel.setModel('sys/taurustest/1')
w1.setModel('/position?configuration=label')
w2.setModel('/position')
w3.setModel('/position')
w4.setModel('/position?configuration=unit')

panel.show()
sys.exit(app.exec_())