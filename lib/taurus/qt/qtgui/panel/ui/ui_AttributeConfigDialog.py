# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/cpascual/src/svn/taurus/widget/dialog/ui/AttributeConfigDialog.ui'
#
# Created: Fri Jan 29 11:48:44 2010
#      by: PyQt4 UI code generator 4.3.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_AttributeConfigDialog(object):
    def setupUi(self, AttributeConfigDialog):
        AttributeConfigDialog.setObjectName("AttributeConfigDialog")
        AttributeConfigDialog.resize(QtCore.QSize(QtCore.QRect(0,0,453,494).size()).expandedTo(AttributeConfigDialog.minimumSizeHint()))

        self.vboxlayout = QtGui.QVBoxLayout(AttributeConfigDialog)
        self.vboxlayout.setObjectName("vboxlayout")

        self.globalAttributeFrame = TaurusFrame(AttributeConfigDialog)
        self.globalAttributeFrame.setObjectName("globalAttributeFrame")

        self.gridlayout = QtGui.QGridLayout(self.globalAttributeFrame)
        self.gridlayout.setObjectName("gridlayout")

        self.hboxlayout = QtGui.QHBoxLayout()
        self.hboxlayout.setObjectName("hboxlayout")

        self.labelLabel = QtGui.QLabel(self.globalAttributeFrame)
        self.labelLabel.setObjectName("labelLabel")
        self.hboxlayout.addWidget(self.labelLabel)

        self.labelEdit = TaurusConfigLineEdit(self.globalAttributeFrame)
        self.labelEdit.setProperty("useParentModel",QtCore.QVariant(True))
        self.labelEdit.setProperty("model",QtCore.QVariant(QtGui.QApplication.translate("AttributeConfigDialog", "?configuration=label", None, QtGui.QApplication.UnicodeUTF8)))
        self.labelEdit.setObjectName("labelEdit")
        self.hboxlayout.addWidget(self.labelEdit)
        self.gridlayout.addLayout(self.hboxlayout,0,0,1,2)

        self.hboxlayout1 = QtGui.QHBoxLayout()
        self.hboxlayout1.setObjectName("hboxlayout1")

        self.hboxlayout2 = QtGui.QHBoxLayout()
        self.hboxlayout2.setObjectName("hboxlayout2")

        self.unitLabel = QtGui.QLabel(self.globalAttributeFrame)
        self.unitLabel.setObjectName("unitLabel")
        self.hboxlayout2.addWidget(self.unitLabel)

        self.unitEdit = TaurusConfigLineEdit(self.globalAttributeFrame)
        self.unitEdit.setProperty("useParentModel",QtCore.QVariant(True))
        self.unitEdit.setProperty("model",QtCore.QVariant(QtGui.QApplication.translate("AttributeConfigDialog", "?configuration=unit", None, QtGui.QApplication.UnicodeUTF8)))
        self.unitEdit.setObjectName("unitEdit")
        self.hboxlayout2.addWidget(self.unitEdit)
        self.hboxlayout1.addLayout(self.hboxlayout2)

        self.hboxlayout3 = QtGui.QHBoxLayout()
        self.hboxlayout3.setObjectName("hboxlayout3")

        self.formatLabel = QtGui.QLabel(self.globalAttributeFrame)
        self.formatLabel.setObjectName("formatLabel")
        self.hboxlayout3.addWidget(self.formatLabel)

        self.formatEdit = TaurusConfigLineEdit(self.globalAttributeFrame)
        self.formatEdit.setProperty("useParentModel",QtCore.QVariant(True))
        self.formatEdit.setProperty("model",QtCore.QVariant(QtGui.QApplication.translate("AttributeConfigDialog", "?configuration=format", None, QtGui.QApplication.UnicodeUTF8)))
        self.formatEdit.setObjectName("formatEdit")
        self.hboxlayout3.addWidget(self.formatEdit)
        self.hboxlayout1.addLayout(self.hboxlayout3)
        self.gridlayout.addLayout(self.hboxlayout1,1,0,1,2)

        self.descriptionLabel = QtGui.QLabel(self.globalAttributeFrame)
        self.descriptionLabel.setObjectName("descriptionLabel")
        self.gridlayout.addWidget(self.descriptionLabel,2,0,1,1)

        self.descriptionEdit = TaurusConfigLineEdit(self.globalAttributeFrame)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.descriptionEdit.sizePolicy().hasHeightForWidth())
        self.descriptionEdit.setSizePolicy(sizePolicy)
        self.descriptionEdit.setProperty("useParentModel",QtCore.QVariant(True))
        self.descriptionEdit.setProperty("model",QtCore.QVariant(QtGui.QApplication.translate("AttributeConfigDialog", "?configuration=description", None, QtGui.QApplication.UnicodeUTF8)))
        self.descriptionEdit.setObjectName("descriptionEdit")
        self.gridlayout.addWidget(self.descriptionEdit,2,1,1,1)

        self.gridlayout1 = QtGui.QGridLayout()
        self.gridlayout1.setObjectName("gridlayout1")

        self.rangeGB = QtGui.QGroupBox(self.globalAttributeFrame)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred,QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.rangeGB.sizePolicy().hasHeightForWidth())
        self.rangeGB.setSizePolicy(sizePolicy)
        self.rangeGB.setObjectName("rangeGB")

        self.gridlayout2 = QtGui.QGridLayout(self.rangeGB)
        self.gridlayout2.setObjectName("gridlayout2")

        self.minValueLabel = QtGui.QLabel(self.rangeGB)
        self.minValueLabel.setObjectName("minValueLabel")
        self.gridlayout2.addWidget(self.minValueLabel,0,0,1,1)

        self.minValueEdit = TaurusConfigLineEdit(self.rangeGB)
        self.minValueEdit.setProperty("useParentModel",QtCore.QVariant(True))
        self.minValueEdit.setProperty("model",QtCore.QVariant(QtGui.QApplication.translate("AttributeConfigDialog", "?configuration=min_value", None, QtGui.QApplication.UnicodeUTF8)))
        self.minValueEdit.setObjectName("minValueEdit")
        self.gridlayout2.addWidget(self.minValueEdit,0,1,1,1)

        self.maxValueLabel = QtGui.QLabel(self.rangeGB)
        self.maxValueLabel.setObjectName("maxValueLabel")
        self.gridlayout2.addWidget(self.maxValueLabel,1,0,1,1)

        self.maxValueEdit = TaurusConfigLineEdit(self.rangeGB)
        self.maxValueEdit.setProperty("useParentModel",QtCore.QVariant(True))
        self.maxValueEdit.setProperty("model",QtCore.QVariant(QtGui.QApplication.translate("AttributeConfigDialog", "?configuration=max_value", None, QtGui.QApplication.UnicodeUTF8)))
        self.maxValueEdit.setObjectName("maxValueEdit")
        self.gridlayout2.addWidget(self.maxValueEdit,1,1,1,1)
        self.gridlayout1.addWidget(self.rangeGB,0,0,1,1)

        self.alarmGB = QtGui.QGroupBox(self.globalAttributeFrame)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred,QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.alarmGB.sizePolicy().hasHeightForWidth())
        self.alarmGB.setSizePolicy(sizePolicy)
        self.alarmGB.setObjectName("alarmGB")

        self.gridlayout3 = QtGui.QGridLayout(self.alarmGB)
        self.gridlayout3.setObjectName("gridlayout3")

        self.minAlarmLabel = QtGui.QLabel(self.alarmGB)
        self.minAlarmLabel.setObjectName("minAlarmLabel")
        self.gridlayout3.addWidget(self.minAlarmLabel,0,0,1,1)

        self.minAlarmEdit = TaurusConfigLineEdit(self.alarmGB)
        self.minAlarmEdit.setProperty("useParentModel",QtCore.QVariant(True))
        self.minAlarmEdit.setProperty("model",QtCore.QVariant(QtGui.QApplication.translate("AttributeConfigDialog", "?configuration=min_alarm", None, QtGui.QApplication.UnicodeUTF8)))
        self.minAlarmEdit.setObjectName("minAlarmEdit")
        self.gridlayout3.addWidget(self.minAlarmEdit,0,1,1,1)

        self.maxAlarmLabel = QtGui.QLabel(self.alarmGB)
        self.maxAlarmLabel.setObjectName("maxAlarmLabel")
        self.gridlayout3.addWidget(self.maxAlarmLabel,1,0,1,1)

        self.maxAlarmEdit = TaurusConfigLineEdit(self.alarmGB)
        self.maxAlarmEdit.setProperty("useParentModel",QtCore.QVariant(True))
        self.maxAlarmEdit.setProperty("model",QtCore.QVariant(QtGui.QApplication.translate("AttributeConfigDialog", "?configuration=max_alarm", None, QtGui.QApplication.UnicodeUTF8)))
        self.maxAlarmEdit.setObjectName("maxAlarmEdit")
        self.gridlayout3.addWidget(self.maxAlarmEdit,1,1,1,1)
        self.gridlayout1.addWidget(self.alarmGB,0,1,1,1)

        self.warningGB = QtGui.QGroupBox(self.globalAttributeFrame)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred,QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.warningGB.sizePolicy().hasHeightForWidth())
        self.warningGB.setSizePolicy(sizePolicy)
        self.warningGB.setObjectName("warningGB")

        self.gridlayout4 = QtGui.QGridLayout(self.warningGB)
        self.gridlayout4.setObjectName("gridlayout4")

        self.minWarningLabel = QtGui.QLabel(self.warningGB)
        self.minWarningLabel.setObjectName("minWarningLabel")
        self.gridlayout4.addWidget(self.minWarningLabel,0,0,1,1)

        self.minWarningEdit = TaurusConfigLineEdit(self.warningGB)
        self.minWarningEdit.setProperty("useParentModel",QtCore.QVariant(True))
        self.minWarningEdit.setProperty("model",QtCore.QVariant(QtGui.QApplication.translate("AttributeConfigDialog", "?configuration=min_warning", None, QtGui.QApplication.UnicodeUTF8)))
        self.minWarningEdit.setObjectName("minWarningEdit")
        self.gridlayout4.addWidget(self.minWarningEdit,0,1,1,1)

        self.maxWarningLabel = QtGui.QLabel(self.warningGB)
        self.maxWarningLabel.setObjectName("maxWarningLabel")
        self.gridlayout4.addWidget(self.maxWarningLabel,1,0,1,1)

        self.maxWarningEdit = TaurusConfigLineEdit(self.warningGB)
        self.maxWarningEdit.setProperty("useParentModel",QtCore.QVariant(True))
        self.maxWarningEdit.setProperty("model",QtCore.QVariant(QtGui.QApplication.translate("AttributeConfigDialog", "?configuration=max_warning", None, QtGui.QApplication.UnicodeUTF8)))
        self.maxWarningEdit.setObjectName("maxWarningEdit")
        self.gridlayout4.addWidget(self.maxWarningEdit,1,1,1,1)
        self.gridlayout1.addWidget(self.warningGB,1,0,1,1)

        self.deltasGB = QtGui.QGroupBox(self.globalAttributeFrame)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred,QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.deltasGB.sizePolicy().hasHeightForWidth())
        self.deltasGB.setSizePolicy(sizePolicy)
        self.deltasGB.setObjectName("deltasGB")

        self.gridlayout5 = QtGui.QGridLayout(self.deltasGB)
        self.gridlayout5.setObjectName("gridlayout5")

        self.deltaTLabel = QtGui.QLabel(self.deltasGB)
        self.deltaTLabel.setObjectName("deltaTLabel")
        self.gridlayout5.addWidget(self.deltaTLabel,0,0,1,1)

        self.deltaTEdit = TaurusConfigLineEdit(self.deltasGB)
        self.deltaTEdit.setProperty("useParentModel",QtCore.QVariant(True))
        self.deltaTEdit.setProperty("model",QtCore.QVariant(QtGui.QApplication.translate("AttributeConfigDialog", "?configuration=delta_t", None, QtGui.QApplication.UnicodeUTF8)))
        self.deltaTEdit.setObjectName("deltaTEdit")
        self.gridlayout5.addWidget(self.deltaTEdit,0,1,1,1)

        self.deltaValLabel = QtGui.QLabel(self.deltasGB)
        self.deltaValLabel.setObjectName("deltaValLabel")
        self.gridlayout5.addWidget(self.deltaValLabel,1,0,1,1)

        self.deltaValEdit = TaurusConfigLineEdit(self.deltasGB)
        self.deltaValEdit.setProperty("useParentModel",QtCore.QVariant(True))
        self.deltaValEdit.setProperty("model",QtCore.QVariant(QtGui.QApplication.translate("AttributeConfigDialog", "?configuration=delta_val", None, QtGui.QApplication.UnicodeUTF8)))
        self.deltaValEdit.setObjectName("deltaValEdit")
        self.gridlayout5.addWidget(self.deltaValEdit,1,1,1,1)
        self.gridlayout1.addWidget(self.deltasGB,1,1,1,1)
        self.gridlayout.addLayout(self.gridlayout1,3,0,1,2)
        self.vboxlayout.addWidget(self.globalAttributeFrame)

        self.buttonBox = QtGui.QDialogButtonBox(AttributeConfigDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Apply|QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.NoButton|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.vboxlayout.addWidget(self.buttonBox)
        self.labelLabel.setBuddy(self.labelEdit)
        self.unitLabel.setBuddy(self.unitEdit)
        self.formatLabel.setBuddy(self.formatEdit)
        self.descriptionLabel.setBuddy(self.descriptionEdit)
        self.minValueLabel.setBuddy(self.minValueEdit)
        self.maxValueLabel.setBuddy(self.maxValueEdit)
        self.minAlarmLabel.setBuddy(self.minAlarmEdit)
        self.maxAlarmLabel.setBuddy(self.maxAlarmEdit)
        self.minWarningLabel.setBuddy(self.minWarningEdit)
        self.maxWarningLabel.setBuddy(self.maxWarningEdit)
        self.deltaTLabel.setBuddy(self.deltaTEdit)
        self.deltaValLabel.setBuddy(self.deltaValEdit)

        self.retranslateUi(AttributeConfigDialog)
        QtCore.QObject.connect(self.buttonBox,QtCore.SIGNAL("accepted()"),AttributeConfigDialog.accept)
        QtCore.QObject.connect(self.buttonBox,QtCore.SIGNAL("rejected()"),AttributeConfigDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(AttributeConfigDialog)

    def retranslateUi(self, AttributeConfigDialog):
        AttributeConfigDialog.setWindowTitle(QtGui.QApplication.translate("AttributeConfigDialog", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.labelLabel.setText(QtGui.QApplication.translate("AttributeConfigDialog", "Label:", None, QtGui.QApplication.UnicodeUTF8))
        self.unitLabel.setText(QtGui.QApplication.translate("AttributeConfigDialog", "Units:", None, QtGui.QApplication.UnicodeUTF8))
        self.formatLabel.setText(QtGui.QApplication.translate("AttributeConfigDialog", "Format:", None, QtGui.QApplication.UnicodeUTF8))
        self.descriptionLabel.setText(QtGui.QApplication.translate("AttributeConfigDialog", "Description:", None, QtGui.QApplication.UnicodeUTF8))
        self.rangeGB.setTitle(QtGui.QApplication.translate("AttributeConfigDialog", "Ranges:", None, QtGui.QApplication.UnicodeUTF8))
        self.minValueLabel.setText(QtGui.QApplication.translate("AttributeConfigDialog", "Min.:", None, QtGui.QApplication.UnicodeUTF8))
        self.maxValueLabel.setText(QtGui.QApplication.translate("AttributeConfigDialog", "Max.:", None, QtGui.QApplication.UnicodeUTF8))
        self.alarmGB.setTitle(QtGui.QApplication.translate("AttributeConfigDialog", "Alarms:", None, QtGui.QApplication.UnicodeUTF8))
        self.minAlarmLabel.setText(QtGui.QApplication.translate("AttributeConfigDialog", "Min.:", None, QtGui.QApplication.UnicodeUTF8))
        self.maxAlarmLabel.setText(QtGui.QApplication.translate("AttributeConfigDialog", "Max.:", None, QtGui.QApplication.UnicodeUTF8))
        self.warningGB.setTitle(QtGui.QApplication.translate("AttributeConfigDialog", "Warnings:", None, QtGui.QApplication.UnicodeUTF8))
        self.minWarningLabel.setText(QtGui.QApplication.translate("AttributeConfigDialog", "Min.:", None, QtGui.QApplication.UnicodeUTF8))
        self.maxWarningLabel.setText(QtGui.QApplication.translate("AttributeConfigDialog", "Max.:", None, QtGui.QApplication.UnicodeUTF8))
        self.deltasGB.setTitle(QtGui.QApplication.translate("AttributeConfigDialog", "Deltas:", None, QtGui.QApplication.UnicodeUTF8))
        self.deltaTLabel.setText(QtGui.QApplication.translate("AttributeConfigDialog", "T (ms):", None, QtGui.QApplication.UnicodeUTF8))
        self.deltaValLabel.setText(QtGui.QApplication.translate("AttributeConfigDialog", "Value:", None, QtGui.QApplication.UnicodeUTF8))

from taurus.widget import TaurusConfigLineEdit, TaurusFrame
