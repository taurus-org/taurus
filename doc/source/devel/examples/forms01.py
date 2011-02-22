import sys
from PyQt4 import Qt
from taurus.qt.qtgui.panel import TaurusForm

app = Qt.QApplication(sys.argv)

panel = TaurusForm()
props = [ 'state', 'status', 'position', 'velocity', 'acceleration' ]
model = [ 'sys/taurustest/1/%s' % p for p in props ]
panel.setModel(model)
panel.setVisible(True)
sys.exit(app.exec_())
