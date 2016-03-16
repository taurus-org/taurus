import sys
from taurus.external.qt import Qt
from taurus.qt.qtgui.display import TaurusLabel

app = Qt.QApplication(sys.argv)
panel = Qt.QWidget()
w = TaurusLabel(panel)
w.setModel('sys/taurustest/1/state')
panel.show()

sys.exit(app.exec_())
