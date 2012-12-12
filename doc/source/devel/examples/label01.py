import sys
from taurus.qt import Qt
from taurus.qt.qtgui.application import TaurusApplication

app = TaurusApplication(sys.argv)
panel = Qt.QWidget()
layout = Qt.QHBoxLayout()
panel.setLayout(layout)

from taurus.qt.qtgui.display import TaurusLabel
w = TaurusLabel()
layout.addWidget(w)
w.model = 'sys/tg_test/1/double_scalar'

panel.show()
sys.exit(app.exec_())
