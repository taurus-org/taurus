# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/TaurusMotorH2.ui'
#
# Created: Thu Nov 11 19:30:22 2010
#      by: PyQt4 UI code generator 4.4.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_TaurusMotorH2(object):
    def setupUi(self, TaurusMotorH2):
        TaurusMotorH2.setObjectName("TaurusMotorH2")
        TaurusMotorH2.resize(212, 82)
        self.gridlayout = QtGui.QGridLayout(TaurusMotorH2)
        self.gridlayout.setMargin(0)
        self.gridlayout.setSpacing(0)
        self.gridlayout.setObjectName("gridlayout")
        self.TaurusGroupBox = TaurusGroupBox(TaurusMotorH2)
        self.TaurusGroupBox.setShowText(False)
        self.TaurusGroupBox.setObjectName("TaurusGroupBox")
        self.gridlayout1 = QtGui.QGridLayout(self.TaurusGroupBox)
        self.gridlayout1.setObjectName("gridlayout1")
        self.vboxlayout = QtGui.QVBoxLayout()
        self.vboxlayout.setObjectName("vboxlayout")
        self.hboxlayout = QtGui.QHBoxLayout()
        self.hboxlayout.setObjectName("hboxlayout")
        self.labelState = TaurusValueLabel(self.TaurusGroupBox)
        self.labelState.setMinimumSize(QtCore.QSize(50, 22))
        self.labelState.setFrameShape(QtGui.QFrame.NoFrame)
        self.labelState.setFrameShadow(QtGui.QFrame.Plain)
        self.labelState.setShowQuality(False)
        self.labelState.setUseParentModel(True)
        self.labelState.setObjectName("labelState")
        self.hboxlayout.addWidget(self.labelState)
        self.ledState = TaurusStateLed(self.TaurusGroupBox)
        self.ledState.setUseParentModel(True)
        self.ledState.setObjectName("ledState")
        self.hboxlayout.addWidget(self.ledState)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.hboxlayout.addItem(spacerItem)
        self.limitN = TaurusBoolLed(self.TaurusGroupBox)
        self.limitN.setUseParentModel(True)
        self.limitN.setBoolIndex(2)
        self.limitN.setObjectName("limitN")
        self.hboxlayout.addWidget(self.limitN)
        self.limitLabel = QtGui.QLabel(self.TaurusGroupBox)
        self.limitLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.limitLabel.setObjectName("limitLabel")
        self.hboxlayout.addWidget(self.limitLabel)
        self.limitP = TaurusBoolLed(self.TaurusGroupBox)
        self.limitP.setUseParentModel(True)
        self.limitP.setBoolIndex(1)
        self.limitP.setObjectName("limitP")
        self.hboxlayout.addWidget(self.limitP)
        self.vboxlayout.addLayout(self.hboxlayout)
        self.hboxlayout1 = QtGui.QHBoxLayout()
        self.hboxlayout1.setObjectName("hboxlayout1")
        self.positionWrite = TaurusValueLineEdit(self.TaurusGroupBox)
        self.positionWrite.setUseParentModel(True)
        self.positionWrite.setObjectName("positionWrite")
        self.hboxlayout1.addWidget(self.positionWrite)
        self.positionRead = TaurusValueLabel(self.TaurusGroupBox)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.positionRead.sizePolicy().hasHeightForWidth())
        self.positionRead.setSizePolicy(sizePolicy)
        self.positionRead.setUseParentModel(True)
        self.positionRead.setObjectName("positionRead")
        self.hboxlayout1.addWidget(self.positionRead)
        self.positionUnits = TaurusConfigLabel(self.TaurusGroupBox)
        self.positionUnits.setMinimumSize(QtCore.QSize(35, 24))
        self.positionUnits.setMaximumSize(QtCore.QSize(35, 24))
        self.positionUnits.setUseParentModel(True)
        self.positionUnits.setObjectName("positionUnits")
        self.hboxlayout1.addWidget(self.positionUnits)
        self.config = QtGui.QToolButton(self.TaurusGroupBox)
        self.config.setObjectName("config")
        self.hboxlayout1.addWidget(self.config)
        self.vboxlayout.addLayout(self.hboxlayout1)
        self.gridlayout1.addLayout(self.vboxlayout, 0, 0, 1, 1)
        self.gridlayout.addWidget(self.TaurusGroupBox, 0, 0, 1, 1)

        self.retranslateUi(TaurusMotorH2)
        QtCore.QMetaObject.connectSlotsByName(TaurusMotorH2)

    def retranslateUi(self, TaurusMotorH2):
        TaurusMotorH2.setWindowTitle(QtGui.QApplication.translate("TaurusMotorH2", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.labelState.setModel(QtGui.QApplication.translate("TaurusMotorH2", "/State", None, QtGui.QApplication.UnicodeUTF8))
        self.ledState.setModel(QtGui.QApplication.translate("TaurusMotorH2", "/State", None, QtGui.QApplication.UnicodeUTF8))
        self.limitN.setModel(QtGui.QApplication.translate("TaurusMotorH2", "/Limit_switches", None, QtGui.QApplication.UnicodeUTF8))
        self.limitLabel.setText(QtGui.QApplication.translate("TaurusMotorH2", "- lim +", None, QtGui.QApplication.UnicodeUTF8))
        self.limitP.setModel(QtGui.QApplication.translate("TaurusMotorH2", "/Limit_switches", None, QtGui.QApplication.UnicodeUTF8))
        self.positionWrite.setModel(QtGui.QApplication.translate("TaurusMotorH2", "/Position", None, QtGui.QApplication.UnicodeUTF8))
        self.positionRead.setModel(QtGui.QApplication.translate("TaurusMotorH2", "/Position", None, QtGui.QApplication.UnicodeUTF8))
        self.positionUnits.setModel(QtGui.QApplication.translate("TaurusMotorH2", "/Position?configuration=unit", None, QtGui.QApplication.UnicodeUTF8))
        self.config.setText(QtGui.QApplication.translate("TaurusMotorH2", "cfg", None, QtGui.QApplication.UnicodeUTF8))

from taurus.qt.qtgui.display import TaurusBoolLed, TaurusConfigLabel, TaurusStateLed, TaurusValueLabel
from taurus.qt.qtgui.container import TaurusGroupBox
from taurus.qt.qtgui.input import TaurusValueLineEdit

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    TaurusMotorH2 = QtGui.QWidget()
    ui = Ui_TaurusMotorH2()
    ui.setupUi(TaurusMotorH2)
    TaurusMotorH2.show()
    sys.exit(app.exec_())

