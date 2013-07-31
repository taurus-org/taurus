import sys
from taurus.qt import Qt
from taurus.qt.qtgui.application import TaurusApplication
from taurus.qt.qtgui.panel import TaurusValue

app = TaurusApplication(sys.argv)
panel = Qt.QWidget()
layout = Qt.QGridLayout()
panel.setLayout(layout)

w = TaurusValue(panel)
layout.addWidget(w)
w.model = 'sys/tg_test/1/double_scalar'

panel.show()
sys.exit(app.exec_())
