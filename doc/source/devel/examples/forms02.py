import sys
from taurus.qt import Qt
from taurus.qt.qtgui.panel import TaurusForm
from taurus.qt.qtgui.display import TaurusValueLabel
from taurus.qt.qtgui.input import TaurusWheelEdit

app = Qt.QApplication(sys.argv)

panel = TaurusForm()
props = [ 'state', 'status', 'position', 'velocity', 'acceleration' ]
model = [ 'sys/taurustest/1/%s' % p for p in props ]
panel.setModel(model)
panel[0].readWidgetClass = TaurusValueLabel
panel[2].writeWidgetClass='TaurusWheelEdit'

panel.show()
sys.exit(app.exec_())
