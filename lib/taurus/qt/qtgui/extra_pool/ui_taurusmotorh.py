# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/TaurusMotorH.ui'
#
# Created: Thu Nov 11 19:30:21 2010
#      by: PyQt4 UI code generator 4.4.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_TaurusMotorH(object):
    def setupUi(self, TaurusMotorH):
        TaurusMotorH.setObjectName("TaurusMotorH")
        TaurusMotorH.resize(392, 48)
        self.gridlayout = QtGui.QGridLayout(TaurusMotorH)
        self.gridlayout.setMargin(0)
        self.gridlayout.setSpacing(0)
        self.gridlayout.setObjectName("gridlayout")
        self.TaurusGroupBox = TaurusGroupBox(TaurusMotorH)
        self.TaurusGroupBox.setShowText(False)
        self.TaurusGroupBox.setObjectName("TaurusGroupBox")
        self.gridlayout1 = QtGui.QGridLayout(self.TaurusGroupBox)
        self.gridlayout1.setObjectName("gridlayout1")
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
        self.positionWrite = TaurusValueLineEdit(self.TaurusGroupBox)
        self.positionWrite.setMinimumSize(QtCore.QSize(50, 22))
        self.positionWrite.setUseParentModel(True)
        self.positionWrite.setObjectName("positionWrite")
        self.hboxlayout.addWidget(self.positionWrite)
        self.positionRead = TaurusValueLabel(self.TaurusGroupBox)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.positionRead.sizePolicy().hasHeightForWidth())
        self.positionRead.setSizePolicy(sizePolicy)
        self.positionRead.setMinimumSize(QtCore.QSize(50, 22))
        self.positionRead.setUseParentModel(True)
        self.positionRead.setObjectName("positionRead")
        self.hboxlayout.addWidget(self.positionRead)
        self.positionUnits = TaurusConfigLabel(self.TaurusGroupBox)
        self.positionUnits.setMinimumSize(QtCore.QSize(35, 22))
        self.positionUnits.setMaximumSize(QtCore.QSize(35, 16777215))
        self.positionUnits.setUseParentModel(True)
        self.positionUnits.setObjectName("positionUnits")
        self.hboxlayout.addWidget(self.positionUnits)
        self.config = QtGui.QToolButton(self.TaurusGroupBox)
        self.config.setObjectName("config")
        self.hboxlayout.addWidget(self.config)
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
        self.gridlayout1.addLayout(self.hboxlayout, 0, 0, 1, 1)
        self.gridlayout.addWidget(self.TaurusGroupBox, 0, 0, 1, 1)

        self.retranslateUi(TaurusMotorH)
        QtCore.QMetaObject.connectSlotsByName(TaurusMotorH)

    def retranslateUi(self, TaurusMotorH):
        TaurusMotorH.setWindowTitle(QtGui.QApplication.translate("TaurusMotorH", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.labelState.setModel(QtGui.QApplication.translate("TaurusMotorH", "/State", None, QtGui.QApplication.UnicodeUTF8))
        self.ledState.setModel(QtGui.QApplication.translate("TaurusMotorH", "/State", None, QtGui.QApplication.UnicodeUTF8))
        self.positionWrite.setModel(QtGui.QApplication.translate("TaurusMotorH", "/Position", None, QtGui.QApplication.UnicodeUTF8))
        self.positionRead.setModel(QtGui.QApplication.translate("TaurusMotorH", "/Position", None, QtGui.QApplication.UnicodeUTF8))
        self.positionUnits.setModel(QtGui.QApplication.translate("TaurusMotorH", "/Position?configuration=unit", None, QtGui.QApplication.UnicodeUTF8))
        self.config.setText(QtGui.QApplication.translate("TaurusMotorH", "cfg", None, QtGui.QApplication.UnicodeUTF8))
        self.limitN.setModel(QtGui.QApplication.translate("TaurusMotorH", "/Limit_switches", None, QtGui.QApplication.UnicodeUTF8))
        self.limitLabel.setText(QtGui.QApplication.translate("TaurusMotorH", "- lim +", None, QtGui.QApplication.UnicodeUTF8))
        self.limitP.setModel(QtGui.QApplication.translate("TaurusMotorH", "/Limit_switches", None, QtGui.QApplication.UnicodeUTF8))

from taurus.qt.qtgui.display import TaurusBoolLed, TaurusConfigLabel, TaurusStateLed, TaurusValueLabel
from taurus.qt.qtgui.container import TaurusGroupBox
from taurus.qt.qtgui.input import TaurusValueLineEdit

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    TaurusMotorH = QtGui.QWidget()
    ui = Ui_TaurusMotorH()
    ui.setupUi(TaurusMotorH)
    TaurusMotorH.show()
    sys.exit(app.exec_())

