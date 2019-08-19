import sys
from taurus.external.qt import Qt
from taurus.qt.qtgui.application import TaurusApplication

app = TaurusApplication(sys.argv, cmd_line_parser=None)
panel = Qt.QWidget()
layout = Qt.QHBoxLayout()
panel.setLayout(layout)

from taurus.qt.qtgui.display import TaurusLabel
w1 = TaurusLabel()
w2 = TaurusLabel()
layout.addWidget(w1)
layout.addWidget(w2)
w1.model = 'sys/tg_test/1/double_scalar#label'
w1.bgRole = ''
w2.model = 'sys/tg_test/1/double_scalar#rvalue.magnitude'

panel.show()
sys.exit(app.exec_())
