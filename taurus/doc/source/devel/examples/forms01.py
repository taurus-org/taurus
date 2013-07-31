import sys
from taurus.qt import Qt
from taurus.qt.qtgui.panel import TaurusForm

app = Qt.QApplication(sys.argv)

panel = TaurusForm()
props = [ 'state', 'status', 'position', 'velocity', 'acceleration' ]
model = [ 'sys/taurustest/1/%s' % p for p in props ]
panel.setModel(model)
panel.show()
sys.exit(app.exec_())
