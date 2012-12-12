import sys
from taurus.qt import Qt
from taurus.qt.qtgui.display import TaurusStateLabel

app = Qt.QApplication(sys.argv)
panel = Qt.QWidget()
layout = Qt.QGridLayout()
panel.setLayout(layout)
for y in range(4):
    for x in range(2):
        w = TaurusStateLabel()
        w.setModel('sys/taurustest/%d/state' % ((y+1)+4*x))
        w.setShowText(False)
        #w.setShowQualityForeground(False)
        layout.addWidget(w,x,y)
panel.show()

sys.exit(app.exec_())
