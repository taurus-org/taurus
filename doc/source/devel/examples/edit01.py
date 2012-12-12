import sys
from taurus.qt import Qt
from taurus.qt.qtgui.application import TaurusApplication

app = TaurusApplication(sys.argv)
panel = Qt.QWidget()
layout = Qt.QHBoxLayout()
panel.setLayout(layout)

from taurus.qt.qtgui.display import TaurusLabel
from taurus.qt.qtgui.input import TaurusValueLineEdit, TaurusValueSpinBox, TaurusWheelEdit

w1 = TaurusLabel()
w2 = TaurusLabel()
w3 = TaurusValueLineEdit() # or TaurusValueSpinBox or TaurusWheelEdit
w4 = TaurusLabel()
layout.addWidget(w1)
layout.addWidget(w2)
layout.addWidget(w3)
layout.addWidget(w4)
w1.model, w1.bgRole = 'sys/tg_test/1/double_scalar?configuration=label', ''
w2.model = 'sys/tg_test/1/double_scalar'
w3.model = 'sys/tg_test/1/double_scalar'
w4.model, w4.bgRole = 'sys/tg_test/1/double_scalar?configuration=unit', ''

panel.show()
sys.exit(app.exec_())