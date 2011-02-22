# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'DataExportDlg.ui'
#
# Created: Wed Feb  3 12:31:44 2010
#      by: PyQt4 UI code generator 4.4.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_DataExportDlg(object):
    def setupUi(self, DataExportDlg):
        DataExportDlg.setObjectName("DataExportDlg")
        DataExportDlg.resize(394, 371)
        self.vboxlayout = QtGui.QVBoxLayout(DataExportDlg)
        self.vboxlayout.setObjectName("vboxlayout")
        self.groupBox_2 = QtGui.QGroupBox(DataExportDlg)
        self.groupBox_2.setObjectName("groupBox_2")
        self.vboxlayout1 = QtGui.QVBoxLayout(self.groupBox_2)
        self.vboxlayout1.setObjectName("vboxlayout1")
        self.hboxlayout = QtGui.QHBoxLayout()
        self.hboxlayout.setObjectName("hboxlayout")
        self.label = QtGui.QLabel(self.groupBox_2)
        self.label.setObjectName("label")
        self.hboxlayout.addWidget(self.label)
        self.dataSetCB = QtGui.QComboBox(self.groupBox_2)
        self.dataSetCB.setObjectName("dataSetCB")
        self.hboxlayout.addWidget(self.dataSetCB)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.hboxlayout.addItem(spacerItem)
        self.vboxlayout1.addLayout(self.hboxlayout)
        self.dataTE = QtGui.QTextEdit(self.groupBox_2)
        self.dataTE.setObjectName("dataTE")
        self.vboxlayout1.addWidget(self.dataTE)
        self.vboxlayout.addWidget(self.groupBox_2)
        self.groupBox = QtGui.QGroupBox(DataExportDlg)
        self.groupBox.setObjectName("groupBox")
        self.hboxlayout1 = QtGui.QHBoxLayout(self.groupBox)
        self.hboxlayout1.setObjectName("hboxlayout1")
        self.exportBT = QtGui.QPushButton(self.groupBox)
        self.exportBT.setObjectName("exportBT")
        self.hboxlayout1.addWidget(self.exportBT)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.hboxlayout1.addItem(spacerItem1)
        self.closeAfterCB = QtGui.QCheckBox(self.groupBox)
        self.closeAfterCB.setChecked(True)
        self.closeAfterCB.setObjectName("closeAfterCB")
        self.hboxlayout1.addWidget(self.closeAfterCB)
        self.vboxlayout.addWidget(self.groupBox)
        self.label.setBuddy(self.dataSetCB)

        self.retranslateUi(DataExportDlg)
        QtCore.QMetaObject.connectSlotsByName(DataExportDlg)

    def retranslateUi(self, DataExportDlg):
        DataExportDlg.setWindowTitle(QtGui.QApplication.translate("DataExportDlg", "Export to ASCII", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_2.setTitle(QtGui.QApplication.translate("DataExportDlg", "View data", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("DataExportDlg", "&Data set", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("DataExportDlg", "Save to File(s)", None, QtGui.QApplication.UnicodeUTF8))
        self.exportBT.setText(QtGui.QApplication.translate("DataExportDlg", "&Save", None, QtGui.QApplication.UnicodeUTF8))
        self.closeAfterCB.setText(QtGui.QApplication.translate("DataExportDlg", "&Close after exporting", None, QtGui.QApplication.UnicodeUTF8))

