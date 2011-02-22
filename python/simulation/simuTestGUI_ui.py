# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'simuTestGUI.ui'
#
# Created: Wed Mar 19 15:45:59 2008
#      by: PyQt4 UI code generator 4.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_testDialog(object):
    def setupUi(self, testDialog):
        testDialog.setObjectName("testDialog")
        testDialog.resize(QtCore.QSize(QtCore.QRect(0,0,413,586).size()).expandedTo(testDialog.minimumSizeHint()))

        self.tabWidget = QtGui.QTabWidget(testDialog)
        self.tabWidget.setGeometry(QtCore.QRect(10,20,391,551))
        self.tabWidget.setObjectName("tabWidget")

        self.pool = QtGui.QWidget()
        self.pool.setObjectName("pool")

        self.gridlayout = QtGui.QGridLayout(self.pool)
        self.gridlayout.setObjectName("gridlayout")

        self.tabWidget_2 = QtGui.QTabWidget(self.pool)
        self.tabWidget_2.setObjectName("tabWidget_2")

        self.motors = QtGui.QWidget()
        self.motors.setObjectName("motors")

        self.label = QtGui.QLabel(self.motors)
        self.label.setGeometry(QtCore.QRect(10,10,208,18))
        self.label.setObjectName("label")

        self.m1GB = TauGroupBox(self.motors)
        self.m1GB.setGeometry(QtCore.QRect(10,40,341,211))
        self.m1GB.setShowQuality(False)
        self.m1GB.setObjectName("m1GB")

        self.gridlayout1 = QtGui.QGridLayout(self.m1GB)
        self.gridlayout1.setObjectName("gridlayout1")

        self.m1StateLed = TauStateLed(self.m1GB)
        self.m1StateLed.setLedSize(24)
        self.m1StateLed.setUseParentModel(True)
        self.m1StateLed.setObjectName("m1StateLed")
        self.gridlayout1.addWidget(self.m1StateLed,0,0,1,1)

        self.m1statusLabel = TauValueLabel(self.m1GB)
        self.m1statusLabel.setShowQuality(False)
        self.m1statusLabel.setUseParentModel(True)
        self.m1statusLabel.setObjectName("m1statusLabel")
        self.gridlayout1.addWidget(self.m1statusLabel,0,1,1,4)

        self.m1PositionLabel = TauConfigLabel(self.m1GB)
        self.m1PositionLabel.setUseParentModel(True)
        self.m1PositionLabel.setObjectName("m1PositionLabel")
        self.gridlayout1.addWidget(self.m1PositionLabel,1,0,1,2)

        self.m1PositionEdit = TauValueLineEdit(self.m1GB)
        self.m1PositionEdit.setUseParentModel(True)
        self.m1PositionEdit.setObjectName("m1PositionEdit")
        self.gridlayout1.addWidget(self.m1PositionEdit,1,2,1,1)

        self.m1Position = TauValueLabel(self.m1GB)
        self.m1Position.setUseParentModel(True)
        self.m1Position.setObjectName("m1Position")
        self.gridlayout1.addWidget(self.m1Position,1,3,1,1)

        self.m1PositionUnitLabel = TauConfigLabel(self.m1GB)
        self.m1PositionUnitLabel.setUseParentModel(True)
        self.m1PositionUnitLabel.setObjectName("m1PositionUnitLabel")
        self.gridlayout1.addWidget(self.m1PositionUnitLabel,1,4,1,1)

        self.m1VelocityLabel = TauConfigLabel(self.m1GB)
        self.m1VelocityLabel.setUseParentModel(True)
        self.m1VelocityLabel.setObjectName("m1VelocityLabel")
        self.gridlayout1.addWidget(self.m1VelocityLabel,2,0,1,2)

        self.m1VelocityEdit = TauValueLineEdit(self.m1GB)
        self.m1VelocityEdit.setUseParentModel(True)
        self.m1VelocityEdit.setObjectName("m1VelocityEdit")
        self.gridlayout1.addWidget(self.m1VelocityEdit,2,2,1,1)

        self.m1Velocity = TauValueLabel(self.m1GB)
        self.m1Velocity.setUseParentModel(True)
        self.m1Velocity.setObjectName("m1Velocity")
        self.gridlayout1.addWidget(self.m1Velocity,2,3,1,1)

        self.m1VelocityUnitLabel = TauConfigLabel(self.m1GB)
        self.m1VelocityUnitLabel.setUseParentModel(True)
        self.m1VelocityUnitLabel.setObjectName("m1VelocityUnitLabel")
        self.gridlayout1.addWidget(self.m1VelocityUnitLabel,2,4,1,1)

        self.m1AccelerationLabel = TauConfigLabel(self.m1GB)
        self.m1AccelerationLabel.setUseParentModel(True)
        self.m1AccelerationLabel.setObjectName("m1AccelerationLabel")
        self.gridlayout1.addWidget(self.m1AccelerationLabel,3,0,1,2)

        self.m1AccelerationEdit = TauValueLineEdit(self.m1GB)
        self.m1AccelerationEdit.setUseParentModel(True)
        self.m1AccelerationEdit.setObjectName("m1AccelerationEdit")
        self.gridlayout1.addWidget(self.m1AccelerationEdit,3,2,1,1)

        self.m1Acceleration = TauValueLabel(self.m1GB)
        self.m1Acceleration.setUseParentModel(True)
        self.m1Acceleration.setObjectName("m1Acceleration")
        self.gridlayout1.addWidget(self.m1Acceleration,3,3,1,1)

        self.m1AccelerationUnitLabel = TauConfigLabel(self.m1GB)
        self.m1AccelerationUnitLabel.setUseParentModel(True)
        self.m1AccelerationUnitLabel.setObjectName("m1AccelerationUnitLabel")
        self.gridlayout1.addWidget(self.m1AccelerationUnitLabel,3,4,1,1)

        self.m1DecelerationLabel = TauConfigLabel(self.m1GB)
        self.m1DecelerationLabel.setUseParentModel(True)
        self.m1DecelerationLabel.setObjectName("m1DecelerationLabel")
        self.gridlayout1.addWidget(self.m1DecelerationLabel,4,0,1,2)

        self.m1DecelerationEdit = TauValueLineEdit(self.m1GB)
        self.m1DecelerationEdit.setUseParentModel(True)
        self.m1DecelerationEdit.setObjectName("m1DecelerationEdit")
        self.gridlayout1.addWidget(self.m1DecelerationEdit,4,2,1,1)

        self.m1Deceleration = TauValueLabel(self.m1GB)
        self.m1Deceleration.setUseParentModel(True)
        self.m1Deceleration.setObjectName("m1Deceleration")
        self.gridlayout1.addWidget(self.m1Deceleration,4,3,1,1)

        self.m1DecelerationUnitLabel = TauConfigLabel(self.m1GB)
        self.m1DecelerationUnitLabel.setUseParentModel(True)
        self.m1DecelerationUnitLabel.setObjectName("m1DecelerationUnitLabel")
        self.gridlayout1.addWidget(self.m1DecelerationUnitLabel,4,4,1,1)

        self.m1StepPerUnitLabel = TauConfigLabel(self.m1GB)
        self.m1StepPerUnitLabel.setUseParentModel(True)
        self.m1StepPerUnitLabel.setObjectName("m1StepPerUnitLabel")
        self.gridlayout1.addWidget(self.m1StepPerUnitLabel,5,0,1,2)

        self.m1StepPerUnitEdit = TauValueLineEdit(self.m1GB)
        self.m1StepPerUnitEdit.setUseParentModel(True)
        self.m1StepPerUnitEdit.setObjectName("m1StepPerUnitEdit")
        self.gridlayout1.addWidget(self.m1StepPerUnitEdit,5,2,1,1)

        self.m1StepPerUnit = TauValueLabel(self.m1GB)
        self.m1StepPerUnit.setUseParentModel(True)
        self.m1StepPerUnit.setObjectName("m1StepPerUnit")
        self.gridlayout1.addWidget(self.m1StepPerUnit,5,3,1,1)

        self.m1StepPerUnitUnitLabel = TauConfigLabel(self.m1GB)
        self.m1StepPerUnitUnitLabel.setUseParentModel(True)
        self.m1StepPerUnitUnitLabel.setObjectName("m1StepPerUnitUnitLabel")
        self.gridlayout1.addWidget(self.m1StepPerUnitUnitLabel,5,4,1,1)

        self.m2GB = TauGroupBox(self.motors)
        self.m2GB.setGeometry(QtCore.QRect(10,260,341,191))
        self.m2GB.setShowQuality(False)
        self.m2GB.setObjectName("m2GB")

        self.gridlayout2 = QtGui.QGridLayout(self.m2GB)
        self.gridlayout2.setObjectName("gridlayout2")

        self.m1StateLed_2 = TauStateLed(self.m2GB)
        self.m1StateLed_2.setLedSize(24)
        self.m1StateLed_2.setUseParentModel(True)
        self.m1StateLed_2.setObjectName("m1StateLed_2")
        self.gridlayout2.addWidget(self.m1StateLed_2,0,0,1,1)

        self.m2statusLabel = TauValueLabel(self.m2GB)
        self.m2statusLabel.setShowQuality(False)
        self.m2statusLabel.setUseParentModel(True)
        self.m2statusLabel.setObjectName("m2statusLabel")
        self.gridlayout2.addWidget(self.m2statusLabel,0,1,1,4)

        self.m2PositionLabel = TauConfigLabel(self.m2GB)
        self.m2PositionLabel.setUseParentModel(True)
        self.m2PositionLabel.setObjectName("m2PositionLabel")
        self.gridlayout2.addWidget(self.m2PositionLabel,1,0,1,2)

        self.m2PositionEdit = TauValueLineEdit(self.m2GB)
        self.m2PositionEdit.setUseParentModel(True)
        self.m2PositionEdit.setObjectName("m2PositionEdit")
        self.gridlayout2.addWidget(self.m2PositionEdit,1,2,1,1)

        self.m2Position = TauValueLabel(self.m2GB)
        self.m2Position.setUseParentModel(True)
        self.m2Position.setObjectName("m2Position")
        self.gridlayout2.addWidget(self.m2Position,1,3,1,1)

        self.m2PositionUnitLabel = TauConfigLabel(self.m2GB)
        self.m2PositionUnitLabel.setUseParentModel(True)
        self.m2PositionUnitLabel.setObjectName("m2PositionUnitLabel")
        self.gridlayout2.addWidget(self.m2PositionUnitLabel,1,4,1,1)

        self.m2VelocityLabel = TauConfigLabel(self.m2GB)
        self.m2VelocityLabel.setUseParentModel(True)
        self.m2VelocityLabel.setObjectName("m2VelocityLabel")
        self.gridlayout2.addWidget(self.m2VelocityLabel,2,0,1,2)

        self.m2VelocityEdit = TauValueLineEdit(self.m2GB)
        self.m2VelocityEdit.setUseParentModel(True)
        self.m2VelocityEdit.setObjectName("m2VelocityEdit")
        self.gridlayout2.addWidget(self.m2VelocityEdit,2,2,1,1)

        self.m2Velocity = TauValueLabel(self.m2GB)
        self.m2Velocity.setUseParentModel(True)
        self.m2Velocity.setObjectName("m2Velocity")
        self.gridlayout2.addWidget(self.m2Velocity,2,3,1,1)

        self.m2VelocityUnitLabel = TauConfigLabel(self.m2GB)
        self.m2VelocityUnitLabel.setUseParentModel(True)
        self.m2VelocityUnitLabel.setObjectName("m2VelocityUnitLabel")
        self.gridlayout2.addWidget(self.m2VelocityUnitLabel,2,4,1,1)

        self.m2AccelerationLabel = TauConfigLabel(self.m2GB)
        self.m2AccelerationLabel.setUseParentModel(True)
        self.m2AccelerationLabel.setObjectName("m2AccelerationLabel")
        self.gridlayout2.addWidget(self.m2AccelerationLabel,3,0,1,2)

        self.m2AccelerationEdit = TauValueLineEdit(self.m2GB)
        self.m2AccelerationEdit.setUseParentModel(True)
        self.m2AccelerationEdit.setObjectName("m2AccelerationEdit")
        self.gridlayout2.addWidget(self.m2AccelerationEdit,3,2,1,1)

        self.m2Acceleration = TauValueLabel(self.m2GB)
        self.m2Acceleration.setUseParentModel(True)
        self.m2Acceleration.setObjectName("m2Acceleration")
        self.gridlayout2.addWidget(self.m2Acceleration,3,3,1,1)

        self.m2AccelerationUnitLabel = TauConfigLabel(self.m2GB)
        self.m2AccelerationUnitLabel.setUseParentModel(True)
        self.m2AccelerationUnitLabel.setObjectName("m2AccelerationUnitLabel")
        self.gridlayout2.addWidget(self.m2AccelerationUnitLabel,3,4,1,1)

        self.m2DecelerationLabel = TauConfigLabel(self.m2GB)
        self.m2DecelerationLabel.setUseParentModel(True)
        self.m2DecelerationLabel.setObjectName("m2DecelerationLabel")
        self.gridlayout2.addWidget(self.m2DecelerationLabel,4,0,1,2)

        self.m2DecelerationEdit = TauValueLineEdit(self.m2GB)
        self.m2DecelerationEdit.setUseParentModel(True)
        self.m2DecelerationEdit.setObjectName("m2DecelerationEdit")
        self.gridlayout2.addWidget(self.m2DecelerationEdit,4,2,1,1)

        self.m2Deceleration = TauValueLabel(self.m2GB)
        self.m2Deceleration.setUseParentModel(True)
        self.m2Deceleration.setObjectName("m2Deceleration")
        self.gridlayout2.addWidget(self.m2Deceleration,4,3,1,1)

        self.m2DecelerationUnitLabel = TauConfigLabel(self.m2GB)
        self.m2DecelerationUnitLabel.setUseParentModel(True)
        self.m2DecelerationUnitLabel.setObjectName("m2DecelerationUnitLabel")
        self.gridlayout2.addWidget(self.m2DecelerationUnitLabel,4,4,1,1)

        self.m2StepPerUnitLabel = TauConfigLabel(self.m2GB)
        self.m2StepPerUnitLabel.setUseParentModel(True)
        self.m2StepPerUnitLabel.setObjectName("m2StepPerUnitLabel")
        self.gridlayout2.addWidget(self.m2StepPerUnitLabel,5,0,1,2)

        self.m2StepPerUnitEdit = TauValueLineEdit(self.m2GB)
        self.m2StepPerUnitEdit.setUseParentModel(True)
        self.m2StepPerUnitEdit.setObjectName("m2StepPerUnitEdit")
        self.gridlayout2.addWidget(self.m2StepPerUnitEdit,5,2,1,1)

        self.m2StepPerUnit = TauValueLabel(self.m2GB)
        self.m2StepPerUnit.setUseParentModel(True)
        self.m2StepPerUnit.setObjectName("m2StepPerUnit")
        self.gridlayout2.addWidget(self.m2StepPerUnit,5,3,1,1)

        self.m2StepPerUnitUnitLabel = TauConfigLabel(self.m2GB)
        self.m2StepPerUnitUnitLabel.setUseParentModel(True)
        self.m2StepPerUnitUnitLabel.setObjectName("m2StepPerUnitUnitLabel")
        self.gridlayout2.addWidget(self.m2StepPerUnitUnitLabel,5,4,1,1)
        self.tabWidget_2.addTab(self.motors,"")

        self.counters = QtGui.QWidget()
        self.counters.setObjectName("counters")

        self.label_2 = QtGui.QLabel(self.counters)
        self.label_2.setGeometry(QtCore.QRect(10,10,220,18))
        self.label_2.setObjectName("label_2")

        self.c1GB = TauGroupBox(self.counters)
        self.c1GB.setGeometry(QtCore.QRect(10,40,341,131))
        self.c1GB.setShowQuality(False)
        self.c1GB.setObjectName("c1GB")

        self.gridlayout3 = QtGui.QGridLayout(self.c1GB)
        self.gridlayout3.setObjectName("gridlayout3")

        self.c1StateLed = TauStateLed(self.c1GB)
        self.c1StateLed.setObjectName("c1StateLed")
        self.gridlayout3.addWidget(self.c1StateLed,0,0,1,1)

        self.c1StatusLabel = TauValueLabel(self.c1GB)
        self.c1StatusLabel.setShowQuality(False)
        self.c1StatusLabel.setUseParentModel(True)
        self.c1StatusLabel.setObjectName("c1StatusLabel")
        self.gridlayout3.addWidget(self.c1StatusLabel,0,1,1,4)

        self.c1ValueLabel = TauConfigLabel(self.c1GB)
        self.c1ValueLabel.setUseParentModel(True)
        self.c1ValueLabel.setObjectName("c1ValueLabel")
        self.gridlayout3.addWidget(self.c1ValueLabel,1,0,1,2)

        self.c1ValueEdit = TauValueLineEdit(self.c1GB)
        self.c1ValueEdit.setUseParentModel(True)
        self.c1ValueEdit.setObjectName("c1ValueEdit")
        self.gridlayout3.addWidget(self.c1ValueEdit,1,2,1,1)

        self.c1Value = TauValueLabel(self.c1GB)
        self.c1Value.setUseParentModel(True)
        self.c1Value.setObjectName("c1Value")
        self.gridlayout3.addWidget(self.c1Value,1,3,1,1)

        self.c1ValueUnitLabel = TauConfigLabel(self.c1GB)
        self.c1ValueUnitLabel.setUseParentModel(True)
        self.c1ValueUnitLabel.setObjectName("c1ValueUnitLabel")
        self.gridlayout3.addWidget(self.c1ValueUnitLabel,1,4,1,1)

        self.c1StartPushButton = QtGui.QPushButton(self.c1GB)
        self.c1StartPushButton.setObjectName("c1StartPushButton")
        self.gridlayout3.addWidget(self.c1StartPushButton,2,3,1,2)

        self.c2GB = TauGroupBox(self.counters)
        self.c2GB.setGeometry(QtCore.QRect(10,180,341,91))
        self.c2GB.setShowQuality(False)
        self.c2GB.setObjectName("c2GB")

        self.gridlayout4 = QtGui.QGridLayout(self.c2GB)
        self.gridlayout4.setObjectName("gridlayout4")

        self.c2StateLed = TauStateLed(self.c2GB)
        self.c2StateLed.setObjectName("c2StateLed")
        self.gridlayout4.addWidget(self.c2StateLed,0,0,1,1)

        self.c2StatusLabel = TauValueLabel(self.c2GB)
        self.c2StatusLabel.setShowQuality(False)
        self.c2StatusLabel.setUseParentModel(True)
        self.c2StatusLabel.setObjectName("c2StatusLabel")
        self.gridlayout4.addWidget(self.c2StatusLabel,0,1,1,4)

        self.c2ValueLabel = TauConfigLabel(self.c2GB)
        self.c2ValueLabel.setUseParentModel(True)
        self.c2ValueLabel.setObjectName("c2ValueLabel")
        self.gridlayout4.addWidget(self.c2ValueLabel,1,0,1,2)

        self.c2ValueEdit = TauValueLineEdit(self.c2GB)
        self.c2ValueEdit.setUseParentModel(True)
        self.c2ValueEdit.setObjectName("c2ValueEdit")
        self.gridlayout4.addWidget(self.c2ValueEdit,1,2,1,1)

        self.c2Value = TauValueLabel(self.c2GB)
        self.c2Value.setUseParentModel(True)
        self.c2Value.setObjectName("c2Value")
        self.gridlayout4.addWidget(self.c2Value,1,3,1,1)

        self.c2ValueUnitLabel = TauConfigLabel(self.c2GB)
        self.c2ValueUnitLabel.setUseParentModel(True)
        self.c2ValueUnitLabel.setObjectName("c2ValueUnitLabel")
        self.gridlayout4.addWidget(self.c2ValueUnitLabel,1,4,1,1)

        self.c3GB = TauGroupBox(self.counters)
        self.c3GB.setGeometry(QtCore.QRect(10,280,341,91))
        self.c3GB.setShowQuality(False)
        self.c3GB.setObjectName("c3GB")

        self.gridlayout5 = QtGui.QGridLayout(self.c3GB)
        self.gridlayout5.setObjectName("gridlayout5")

        self.c3StateLed = TauStateLed(self.c3GB)
        self.c3StateLed.setObjectName("c3StateLed")
        self.gridlayout5.addWidget(self.c3StateLed,0,0,1,1)

        self.c3StatusLabel = TauValueLabel(self.c3GB)
        self.c3StatusLabel.setShowQuality(False)
        self.c3StatusLabel.setUseParentModel(True)
        self.c3StatusLabel.setObjectName("c3StatusLabel")
        self.gridlayout5.addWidget(self.c3StatusLabel,0,1,1,4)

        self.c3ValueLabel = TauConfigLabel(self.c3GB)
        self.c3ValueLabel.setUseParentModel(True)
        self.c3ValueLabel.setObjectName("c3ValueLabel")
        self.gridlayout5.addWidget(self.c3ValueLabel,1,0,1,2)

        self.c3ValueEdit = TauValueLineEdit(self.c3GB)
        self.c3ValueEdit.setUseParentModel(True)
        self.c3ValueEdit.setObjectName("c3ValueEdit")
        self.gridlayout5.addWidget(self.c3ValueEdit,1,2,1,1)

        self.c3Value = TauValueLabel(self.c3GB)
        self.c3Value.setUseParentModel(True)
        self.c3Value.setObjectName("c3Value")
        self.gridlayout5.addWidget(self.c3Value,1,3,1,1)

        self.c3ValueUnitLabel = TauConfigLabel(self.c3GB)
        self.c3ValueUnitLabel.setUseParentModel(True)
        self.c3ValueUnitLabel.setObjectName("c3ValueUnitLabel")
        self.gridlayout5.addWidget(self.c3ValueUnitLabel,1,4,1,1)
        self.tabWidget_2.addTab(self.counters,"")
        self.gridlayout.addWidget(self.tabWidget_2,0,0,1,1)
        self.tabWidget.addTab(self.pool,"")

        self.actionC1Start = QtGui.QAction(testDialog)
        self.actionC1Start.setObjectName("actionC1Start")
        self.m2PositionLabel.setBuddy(self.m1PositionEdit)
        self.m2PositionUnitLabel.setBuddy(self.m1PositionEdit)

        self.retranslateUi(testDialog)
        self.tabWidget.setCurrentIndex(0)
        self.tabWidget_2.setCurrentIndex(0)
        QtCore.QObject.connect(self.c1StartPushButton,QtCore.SIGNAL("clicked()"),self.actionC1Start.trigger)
        QtCore.QMetaObject.connectSlotsByName(testDialog)

    def retranslateUi(self, testDialog):
        testDialog.setWindowTitle(QtGui.QApplication.translate("testDialog", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("testDialog", "Only the first 2 motors are shown", None, QtGui.QApplication.UnicodeUTF8))
        self.m1StateLed.setModel(QtGui.QApplication.translate("testDialog", "/State", None, QtGui.QApplication.UnicodeUTF8))
        self.m1statusLabel.setModel(QtGui.QApplication.translate("testDialog", "/Status", None, QtGui.QApplication.UnicodeUTF8))
        self.m1PositionLabel.setSuffixText(QtGui.QApplication.translate("testDialog", ":", None, QtGui.QApplication.UnicodeUTF8))
        self.m1PositionLabel.setModel(QtGui.QApplication.translate("testDialog", "/position?configuration=label", None, QtGui.QApplication.UnicodeUTF8))
        self.m1PositionEdit.setModel(QtGui.QApplication.translate("testDialog", "/Position", None, QtGui.QApplication.UnicodeUTF8))
        self.m1Position.setModel(QtGui.QApplication.translate("testDialog", "/Position", None, QtGui.QApplication.UnicodeUTF8))
        self.m1PositionUnitLabel.setModel(QtGui.QApplication.translate("testDialog", "/position?configuration=unit", None, QtGui.QApplication.UnicodeUTF8))
        self.m1VelocityLabel.setSuffixText(QtGui.QApplication.translate("testDialog", ":", None, QtGui.QApplication.UnicodeUTF8))
        self.m1VelocityLabel.setModel(QtGui.QApplication.translate("testDialog", "/velocity?configuration=label", None, QtGui.QApplication.UnicodeUTF8))
        self.m1VelocityEdit.setModel(QtGui.QApplication.translate("testDialog", "/Velocity", None, QtGui.QApplication.UnicodeUTF8))
        self.m1Velocity.setModel(QtGui.QApplication.translate("testDialog", "/velocity", None, QtGui.QApplication.UnicodeUTF8))
        self.m1VelocityUnitLabel.setModel(QtGui.QApplication.translate("testDialog", "/velocity?configuration=unit", None, QtGui.QApplication.UnicodeUTF8))
        self.m1AccelerationLabel.setSuffixText(QtGui.QApplication.translate("testDialog", ":", None, QtGui.QApplication.UnicodeUTF8))
        self.m1AccelerationLabel.setModel(QtGui.QApplication.translate("testDialog", "/acceleration?configuration=label", None, QtGui.QApplication.UnicodeUTF8))
        self.m1AccelerationEdit.setModel(QtGui.QApplication.translate("testDialog", "/Acceleration", None, QtGui.QApplication.UnicodeUTF8))
        self.m1Acceleration.setModel(QtGui.QApplication.translate("testDialog", "/Acceleration", None, QtGui.QApplication.UnicodeUTF8))
        self.m1AccelerationUnitLabel.setModel(QtGui.QApplication.translate("testDialog", "/acceleration?configuration=unit", None, QtGui.QApplication.UnicodeUTF8))
        self.m1DecelerationLabel.setSuffixText(QtGui.QApplication.translate("testDialog", ":", None, QtGui.QApplication.UnicodeUTF8))
        self.m1DecelerationLabel.setModel(QtGui.QApplication.translate("testDialog", "/deceleration?configuration=label", None, QtGui.QApplication.UnicodeUTF8))
        self.m1DecelerationEdit.setModel(QtGui.QApplication.translate("testDialog", "/Deceleration", None, QtGui.QApplication.UnicodeUTF8))
        self.m1Deceleration.setModel(QtGui.QApplication.translate("testDialog", "/Deceleration", None, QtGui.QApplication.UnicodeUTF8))
        self.m1DecelerationUnitLabel.setModel(QtGui.QApplication.translate("testDialog", "/deceleration?configuration=unit", None, QtGui.QApplication.UnicodeUTF8))
        self.m1StepPerUnitLabel.setSuffixText(QtGui.QApplication.translate("testDialog", ":", None, QtGui.QApplication.UnicodeUTF8))
        self.m1StepPerUnitLabel.setModel(QtGui.QApplication.translate("testDialog", "/step_per_unit?configuration=label", None, QtGui.QApplication.UnicodeUTF8))
        self.m1StepPerUnitEdit.setModel(QtGui.QApplication.translate("testDialog", "/step_per_unit", None, QtGui.QApplication.UnicodeUTF8))
        self.m1StepPerUnit.setModel(QtGui.QApplication.translate("testDialog", "/step_per_unit", None, QtGui.QApplication.UnicodeUTF8))
        self.m1StepPerUnitUnitLabel.setModel(QtGui.QApplication.translate("testDialog", "/step_per_unit?configuration=unit", None, QtGui.QApplication.UnicodeUTF8))
        self.m1StateLed_2.setModel(QtGui.QApplication.translate("testDialog", "/State", None, QtGui.QApplication.UnicodeUTF8))
        self.m2statusLabel.setModel(QtGui.QApplication.translate("testDialog", "/Status", None, QtGui.QApplication.UnicodeUTF8))
        self.m2PositionLabel.setSuffixText(QtGui.QApplication.translate("testDialog", ":", None, QtGui.QApplication.UnicodeUTF8))
        self.m2PositionLabel.setModel(QtGui.QApplication.translate("testDialog", "?configuration=label", None, QtGui.QApplication.UnicodeUTF8))
        self.m2PositionEdit.setModel(QtGui.QApplication.translate("testDialog", "/Position", None, QtGui.QApplication.UnicodeUTF8))
        self.m2Position.setModel(QtGui.QApplication.translate("testDialog", "/Position", None, QtGui.QApplication.UnicodeUTF8))
        self.m2PositionUnitLabel.setModel(QtGui.QApplication.translate("testDialog", "?configuration=unit", None, QtGui.QApplication.UnicodeUTF8))
        self.m2VelocityLabel.setSuffixText(QtGui.QApplication.translate("testDialog", ":", None, QtGui.QApplication.UnicodeUTF8))
        self.m2VelocityLabel.setModel(QtGui.QApplication.translate("testDialog", "/velocity?configuration=label", None, QtGui.QApplication.UnicodeUTF8))
        self.m2VelocityEdit.setModel(QtGui.QApplication.translate("testDialog", "/Velocity", None, QtGui.QApplication.UnicodeUTF8))
        self.m2Velocity.setModel(QtGui.QApplication.translate("testDialog", "/velocity", None, QtGui.QApplication.UnicodeUTF8))
        self.m2VelocityUnitLabel.setModel(QtGui.QApplication.translate("testDialog", "/velocity?configuration=unit", None, QtGui.QApplication.UnicodeUTF8))
        self.m2AccelerationLabel.setSuffixText(QtGui.QApplication.translate("testDialog", ":", None, QtGui.QApplication.UnicodeUTF8))
        self.m2AccelerationLabel.setModel(QtGui.QApplication.translate("testDialog", "/acceleration?configuration=label", None, QtGui.QApplication.UnicodeUTF8))
        self.m2AccelerationEdit.setModel(QtGui.QApplication.translate("testDialog", "/Acceleration", None, QtGui.QApplication.UnicodeUTF8))
        self.m2Acceleration.setModel(QtGui.QApplication.translate("testDialog", "/Acceleration", None, QtGui.QApplication.UnicodeUTF8))
        self.m2AccelerationUnitLabel.setModel(QtGui.QApplication.translate("testDialog", "/acceleration?configuration=unit", None, QtGui.QApplication.UnicodeUTF8))
        self.m2DecelerationLabel.setSuffixText(QtGui.QApplication.translate("testDialog", ":", None, QtGui.QApplication.UnicodeUTF8))
        self.m2DecelerationLabel.setModel(QtGui.QApplication.translate("testDialog", "/deceleration?configuration=label", None, QtGui.QApplication.UnicodeUTF8))
        self.m2DecelerationEdit.setModel(QtGui.QApplication.translate("testDialog", "/Deceleration", None, QtGui.QApplication.UnicodeUTF8))
        self.m2Deceleration.setModel(QtGui.QApplication.translate("testDialog", "/Deceleration", None, QtGui.QApplication.UnicodeUTF8))
        self.m2DecelerationUnitLabel.setModel(QtGui.QApplication.translate("testDialog", "/deceleration?configuration=unit", None, QtGui.QApplication.UnicodeUTF8))
        self.m2StepPerUnitLabel.setSuffixText(QtGui.QApplication.translate("testDialog", ":", None, QtGui.QApplication.UnicodeUTF8))
        self.m2StepPerUnitLabel.setModel(QtGui.QApplication.translate("testDialog", "/step_per_unit?configuration=label", None, QtGui.QApplication.UnicodeUTF8))
        self.m2StepPerUnitEdit.setModel(QtGui.QApplication.translate("testDialog", "/step_per_unit", None, QtGui.QApplication.UnicodeUTF8))
        self.m2StepPerUnit.setModel(QtGui.QApplication.translate("testDialog", "/step_per_unit", None, QtGui.QApplication.UnicodeUTF8))
        self.m2StepPerUnitUnitLabel.setModel(QtGui.QApplication.translate("testDialog", "/step_per_unit?configuration=unit", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.motors), QtGui.QApplication.translate("testDialog", "Motors", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("testDialog", "Only the first 3 counters are shown", None, QtGui.QApplication.UnicodeUTF8))
        self.c1StatusLabel.setModel(QtGui.QApplication.translate("testDialog", "/Status", None, QtGui.QApplication.UnicodeUTF8))
        self.c1ValueLabel.setSuffixText(QtGui.QApplication.translate("testDialog", ":", None, QtGui.QApplication.UnicodeUTF8))
        self.c1ValueLabel.setModel(QtGui.QApplication.translate("testDialog", "/value?configuration=label", None, QtGui.QApplication.UnicodeUTF8))
        self.c1ValueEdit.setModel(QtGui.QApplication.translate("testDialog", "/value", None, QtGui.QApplication.UnicodeUTF8))
        self.c1Value.setModel(QtGui.QApplication.translate("testDialog", "/value", None, QtGui.QApplication.UnicodeUTF8))
        self.c1ValueUnitLabel.setModel(QtGui.QApplication.translate("testDialog", "/value?configuration=unit", None, QtGui.QApplication.UnicodeUTF8))
        self.c1StartPushButton.setText(QtGui.QApplication.translate("testDialog", "Start", None, QtGui.QApplication.UnicodeUTF8))
        self.c2StatusLabel.setModel(QtGui.QApplication.translate("testDialog", "/Status", None, QtGui.QApplication.UnicodeUTF8))
        self.c2ValueLabel.setSuffixText(QtGui.QApplication.translate("testDialog", ":", None, QtGui.QApplication.UnicodeUTF8))
        self.c2ValueLabel.setModel(QtGui.QApplication.translate("testDialog", "/value?configuration=label", None, QtGui.QApplication.UnicodeUTF8))
        self.c2ValueEdit.setModel(QtGui.QApplication.translate("testDialog", "/value", None, QtGui.QApplication.UnicodeUTF8))
        self.c2Value.setModel(QtGui.QApplication.translate("testDialog", "/value", None, QtGui.QApplication.UnicodeUTF8))
        self.c2ValueUnitLabel.setModel(QtGui.QApplication.translate("testDialog", "/value?configuration=unit", None, QtGui.QApplication.UnicodeUTF8))
        self.c3StatusLabel.setModel(QtGui.QApplication.translate("testDialog", "/Status", None, QtGui.QApplication.UnicodeUTF8))
        self.c3ValueLabel.setSuffixText(QtGui.QApplication.translate("testDialog", ":", None, QtGui.QApplication.UnicodeUTF8))
        self.c3ValueLabel.setModel(QtGui.QApplication.translate("testDialog", "/value?configuration=label", None, QtGui.QApplication.UnicodeUTF8))
        self.c3ValueEdit.setModel(QtGui.QApplication.translate("testDialog", "/value", None, QtGui.QApplication.UnicodeUTF8))
        self.c3Value.setModel(QtGui.QApplication.translate("testDialog", "/value", None, QtGui.QApplication.UnicodeUTF8))
        self.c3ValueUnitLabel.setModel(QtGui.QApplication.translate("testDialog", "/value?configuration=unit", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.counters), QtGui.QApplication.translate("testDialog", "Counters", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.pool), QtGui.QApplication.translate("testDialog", "Device Pool", None, QtGui.QApplication.UnicodeUTF8))
        self.actionC1Start.setText(QtGui.QApplication.translate("testDialog", "c1Start", None, QtGui.QApplication.UnicodeUTF8))

from tau.widget import TauValueLabel, TauGroupBox, TauValueLineEdit, TauConfigLabel, TauStateLed
