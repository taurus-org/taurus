import sys
from taurus.external.qt import Qt
from taurus.qt.qtgui.display import TaurusLabel
from taurus.qt.qtgui.application import TaurusApplication

app = TaurusApplication(sys.argv, cmd_line_parser=None)
panel = Qt.QWidget()
w = TaurusLabel(panel)
w.setModel('sys/taurustest/1/state')
panel.show()

sys.exit(app.exec_())
