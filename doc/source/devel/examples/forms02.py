import sys
from PyQt4 import Qt
from taurus.qt.qtgui.panel import TaurusForm
from taurus.qt.qtgui.display import TaurusValueLabel
from taurus.qt.qtgui.input import TaurusWheelEdit

app = Qt.QApplication(sys.argv)

panel = TaurusForm()
props = [ 'state', 'status', 'position', 'velocity', 'acceleration' ]
model = [ 'sys/taurustest/1/%s' % p for p in props ]
panel.setModel(model)
panel.getItemByIndex(0).setReadWidgetClass(TaurusValueLabel)
panel.getItemByIndex(2).setWriteWidgetClass(TaurusWheelEdit)

panel.setVisible(True)
sys.exit(app.exec_())
