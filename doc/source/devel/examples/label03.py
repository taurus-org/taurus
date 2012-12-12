import sys
from taurus.qt import Qt
from taurus.qt.qtgui.application import TaurusApplication

app = TaurusApplication(sys.argv)
panel = Qt.QWidget()
layout = Qt.QHBoxLayout()
panel.setLayout(layout)

from taurus.qt.qtgui.container import TaurusWidget
from taurus.qt.qtgui.display import TaurusLabel
w1, w2, w3 = TaurusLabel(), TaurusLabel(), TaurusLabel()
layout.addWidget(w1)
layout.addWidget(w2)
layout.addWidget(w3)
w1.model, w1.bgRole = 'sys/tg_test/1/double_scalar?configuration=label', ''
w2.model = 'sys/tg_test/1/double_scalar'
w3.model, w3.bgRole = 'sys/tg_test/1/double_scalar?configuration=unit', ''

panel.show()
sys.exit(app.exec_())