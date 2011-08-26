# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/tmp/tmpf8jNJv.ui'
#
# Created: Tue Aug 23 12:54:43 2011
#      by: PyQt4 UI code generator 4.4.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_ExpDescriptionEditor(object):
    def setupUi(self, ExpDescriptionEditor):
        ExpDescriptionEditor.setObjectName("ExpDescriptionEditor")
        ExpDescriptionEditor.resize(707, 646)
        self.verticalLayout_2 = QtGui.QVBoxLayout(ExpDescriptionEditor)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.taurusGroupBox = TaurusGroupBox(ExpDescriptionEditor)
        self.taurusGroupBox.setObjectName("taurusGroupBox")
        self.verticalLayout = QtGui.QVBoxLayout(self.taurusGroupBox)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtGui.QLabel(self.taurusGroupBox)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.activeMntGrpCB = QtGui.QComboBox(self.taurusGroupBox)
        self.activeMntGrpCB.setObjectName("activeMntGrpCB")
        self.horizontalLayout.addWidget(self.activeMntGrpCB)
        self.mntGrpOptionBT = QtGui.QToolButton(self.taurusGroupBox)
        self.mntGrpOptionBT.setObjectName("mntGrpOptionBT")
        self.horizontalLayout.addWidget(self.mntGrpOptionBT)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.channelEditor = MntGrpChannelEditor(self.taurusGroupBox)
        self.channelEditor.setObjectName("channelEditor")
        self.verticalLayout.addWidget(self.channelEditor)
        self.verticalLayout_2.addWidget(self.taurusGroupBox)
        self.groupBox = QtGui.QGroupBox(ExpDescriptionEditor)
        self.groupBox.setObjectName("groupBox")
        self.formLayout = QtGui.QFormLayout(self.groupBox)
        self.formLayout.setObjectName("formLayout")
        self.label_3 = QtGui.QLabel(self.groupBox)
        self.label_3.setObjectName("label_3")
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.label_3)
        self.filenameLE = QtGui.QLineEdit(self.groupBox)
        self.filenameLE.setObjectName("filenameLE")
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.filenameLE)
        self.label_2 = QtGui.QLabel(self.groupBox)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.label_2)
        self.pathLE = QtGui.QLineEdit(self.groupBox)
        self.pathLE.setObjectName("pathLE")
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.pathLE)
        self.label_4 = QtGui.QLabel(self.groupBox)
        self.label_4.setObjectName("label_4")
        self.formLayout.setWidget(2, QtGui.QFormLayout.LabelRole, self.label_4)
        self.compressionCB = QtGui.QComboBox(self.groupBox)
        self.compressionCB.setObjectName("compressionCB")
        self.compressionCB.addItem(QtCore.QString())
        self.compressionCB.addItem(QtCore.QString())
        self.compressionCB.addItem(QtCore.QString())
        self.compressionCB.addItem(QtCore.QString())
        self.compressionCB.addItem(QtCore.QString())
        self.formLayout.setWidget(2, QtGui.QFormLayout.FieldRole, self.compressionCB)
        self.verticalLayout_2.addWidget(self.groupBox)
        self.buttonBox = QtGui.QDialogButtonBox(ExpDescriptionEditor)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.NoButton)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout_2.addWidget(self.buttonBox)

        self.retranslateUi(ExpDescriptionEditor)
        QtCore.QMetaObject.connectSlotsByName(ExpDescriptionEditor)

    def retranslateUi(self, ExpDescriptionEditor):
        ExpDescriptionEditor.setWindowTitle(QtGui.QApplication.translate("ExpDescriptionEditor", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.taurusGroupBox.setTitle(QtGui.QApplication.translate("ExpDescriptionEditor", "Measurement group", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("ExpDescriptionEditor", "Active Measurement Group", None, QtGui.QApplication.UnicodeUTF8))
        self.mntGrpOptionBT.setText(QtGui.QApplication.translate("ExpDescriptionEditor", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("ExpDescriptionEditor", "Storage", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("ExpDescriptionEditor", "File Name", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("ExpDescriptionEditor", "Path", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("ExpDescriptionEditor", "Data compression", None, QtGui.QApplication.UnicodeUTF8))
        self.compressionCB.setItemText(0, QtGui.QApplication.translate("ExpDescriptionEditor", "nowhere", None, QtGui.QApplication.UnicodeUTF8))
        self.compressionCB.setItemText(1, QtGui.QApplication.translate("ExpDescriptionEditor", "for all datasets", None, QtGui.QApplication.UnicodeUTF8))
        self.compressionCB.setItemText(2, QtGui.QApplication.translate("ExpDescriptionEditor", "for datasets of rank 1 or more", None, QtGui.QApplication.UnicodeUTF8))
        self.compressionCB.setItemText(3, QtGui.QApplication.translate("ExpDescriptionEditor", "for datasets of rank 2 or more", None, QtGui.QApplication.UnicodeUTF8))
        self.compressionCB.setItemText(4, QtGui.QApplication.translate("ExpDescriptionEditor", "for datasets of rank 3 or more", None, QtGui.QApplication.UnicodeUTF8))

from taurus.qt.qtgui.container import TaurusGroupBox
from taurus.qt.qtgui.extra_sardana import MntGrpChannelEditor

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    ExpDescriptionEditor = QtGui.QWidget()
    ui = Ui_ExpDescriptionEditor()
    ui.setupUi(ExpDescriptionEditor)
    ExpDescriptionEditor.show()
    sys.exit(app.exec_())

