# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/cpascual/src/taurus/widget/qwt/ui/EditCPointsDialog.ui'
#
# Created: Thu Aug 20 10:57:57 2009
#      by: PyQt4 UI code generator 4.3.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_EditCPointsDialog(object):
    def setupUi(self, EditCPointsDialog):
        EditCPointsDialog.setObjectName("EditCPointsDialog")
        EditCPointsDialog.resize(QtCore.QSize(QtCore.QRect(0,0,257,300).size()).expandedTo(EditCPointsDialog.minimumSizeHint()))

        self.vboxlayout = QtGui.QVBoxLayout(EditCPointsDialog)
        self.vboxlayout.setObjectName("vboxlayout")

        self.hboxlayout = QtGui.QHBoxLayout()
        self.hboxlayout.setObjectName("hboxlayout")

        self.tableTW = QtGui.QTableWidget(EditCPointsDialog)
        self.tableTW.setObjectName("tableTW")
        self.hboxlayout.addWidget(self.tableTW)

        self.vboxlayout1 = QtGui.QVBoxLayout()
        self.vboxlayout1.setObjectName("vboxlayout1")

        spacerItem = QtGui.QSpacerItem(20,40,QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Expanding)
        self.vboxlayout1.addItem(spacerItem)

        self.delBT = QtGui.QToolButton(EditCPointsDialog)
        self.delBT.setObjectName("delBT")
        self.vboxlayout1.addWidget(self.delBT)
        self.hboxlayout.addLayout(self.vboxlayout1)
        self.vboxlayout.addLayout(self.hboxlayout)

        self.buttonBox = QtGui.QDialogButtonBox(EditCPointsDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.NoButton|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.vboxlayout.addWidget(self.buttonBox)

        self.retranslateUi(EditCPointsDialog)
        QtCore.QObject.connect(self.buttonBox,QtCore.SIGNAL("accepted()"),EditCPointsDialog.accept)
        QtCore.QObject.connect(self.buttonBox,QtCore.SIGNAL("rejected()"),EditCPointsDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(EditCPointsDialog)

    def retranslateUi(self, EditCPointsDialog):
        EditCPointsDialog.setWindowTitle(QtGui.QApplication.translate("EditCPointsDialog", "Edit Control Points", None, QtGui.QApplication.UnicodeUTF8))
        self.tableTW.clear()
        self.tableTW.setColumnCount(2)
        self.tableTW.setRowCount(0)

        headerItem = QtGui.QTableWidgetItem()
        headerItem.setText(QtGui.QApplication.translate("EditCPointsDialog", "Position", None, QtGui.QApplication.UnicodeUTF8))
        self.tableTW.setHorizontalHeaderItem(0,headerItem)

        headerItem1 = QtGui.QTableWidgetItem()
        headerItem1.setText(QtGui.QApplication.translate("EditCPointsDialog", "Correction", None, QtGui.QApplication.UnicodeUTF8))
        self.tableTW.setHorizontalHeaderItem(1,headerItem1)
        self.delBT.setToolTip(QtGui.QApplication.translate("EditCPointsDialog", "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
        "p, li { white-space: pre-wrap; }\n"
        "</style></head><body style=\" font-family:\'Sans Serif\'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
        "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Delete selected</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.delBT.setText(QtGui.QApplication.translate("EditCPointsDialog", "D", None, QtGui.QApplication.UnicodeUTF8))

