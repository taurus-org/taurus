import sys
from taurus.qt import Qt
from taurus.qt.qtgui.container import TaurusWidget
from taurus.qt.qtgui.display import TaurusValueLabel, TaurusConfigLabel

app = Qt.QApplication(sys.argv)
panel = TaurusWidget()
layout = Qt.QVBoxLayout()
panel.setLayout(layout)
panel.setModel('sys/taurustest/1')
w1 = TaurusValueLabel()
w2 = TaurusValueLabel()
w3 = TaurusValueLabel()
w1.setUseParentModel(True)
w2.setUseParentModel(True)
w3.setUseParentModel(True)
w1.setModel('/state')
w2.setModel('/position')
w3.setModel('/simulationmode')
w1.setShowQuality(False)

layout.addWidget(w1)
layout.addWidget(w2)
layout.addWidget(w3)
panel.show()

sys.exit(app.exec_())
