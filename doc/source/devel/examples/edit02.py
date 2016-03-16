import sys
from taurus.external.qt import Qt
from taurus.qt.qtgui.container import TaurusWidget
from taurus.qt.qtgui.display import TaurusLabel
from taurus.qt.qtgui.input import TaurusValueSpinBox

app = Qt.QApplication(sys.argv)

panel = TaurusWidget()
layout = Qt.QHBoxLayout()
panel.setLayout(layout)

w1 = TaurusLabel()
w2 = TaurusLabel()
w3 = TaurusValueSpinBox()
w4 = TaurusLabel()
layout.addWidget(w1)
layout.addWidget(w2)
layout.addWidget(w3)
layout.addWidget(w4)
w1.setUseParentModel(True)
w2.setUseParentModel(True)
w3.setUseParentModel(True)
w4.setUseParentModel(True)
panel.setModel('sys/taurustest/1')
w1.setModel('/position#label')
w2.setModel('/position')
w3.setModel('/position')
w4.setModel('/position#unit')

panel.show()
sys.exit(app.exec_())
