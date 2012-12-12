import sys
from taurus.qt import Qt
from taurus.qt.qtgui.display import TaurusStateLabel

app = Qt.QApplication(sys.argv)
panel = Qt.QWidget()
w = TaurusStateLabel(panel)
w.setModel('sys/taurustest/1/state')
panel.show()

sys.exit(app.exec_())
