import sys
from PyQt4 import Qt
from taurus.qt.qtgui.display import TaurusStateLabel

app = Qt.QApplication(sys.argv)
panel = Qt.QWidget()
w = TaurusStateLabel(panel)
w.setModel('sys/taurustest/1/state')
panel.setVisible(True)

sys.exit(app.exec_())
