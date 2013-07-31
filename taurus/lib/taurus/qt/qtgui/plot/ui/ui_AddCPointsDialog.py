# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/cpascual/src/taurus/widget/qwt/ui/AddCPointsDialog.ui'
#
# Created: Fri Aug 21 16:24:23 2009
#      by: PyQt4 UI code generator 4.3.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_AddCPointsDialog(object):
    def setupUi(self, AddCPointsDialog):
        AddCPointsDialog.setObjectName("AddCPointsDialog")
        AddCPointsDialog.resize(QtCore.QSize(QtCore.QRect(0,0,367,127).size()).expandedTo(AddCPointsDialog.minimumSizeHint()))

        self.vboxlayout = QtGui.QVBoxLayout(AddCPointsDialog)
        self.vboxlayout.setObjectName("vboxlayout")

        self.gridlayout = QtGui.QGridLayout()
        self.gridlayout.setObjectName("gridlayout")

        self.label = QtGui.QLabel(AddCPointsDialog)
        self.label.setObjectName("label")
        self.gridlayout.addWidget(self.label,0,0,1,2)

        self.singleCPointXSB = QtGui.QDoubleSpinBox(AddCPointsDialog)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred,QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.singleCPointXSB.sizePolicy().hasHeightForWidth())
        self.singleCPointXSB.setSizePolicy(sizePolicy)
        self.singleCPointXSB.setMinimumSize(QtCore.QSize(50,0))
        self.singleCPointXSB.setMinimum(-1e+300)
        self.singleCPointXSB.setMaximum(1e+300)
        self.singleCPointXSB.setObjectName("singleCPointXSB")
        self.gridlayout.addWidget(self.singleCPointXSB,0,2,1,1)

        self.addSingleCPointBT = QtGui.QPushButton(AddCPointsDialog)
        self.addSingleCPointBT.setObjectName("addSingleCPointBT")
        self.gridlayout.addWidget(self.addSingleCPointBT,0,3,1,1)

        self.regEspCPointsSB = QtGui.QSpinBox(AddCPointsDialog)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred,QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.regEspCPointsSB.sizePolicy().hasHeightForWidth())
        self.regEspCPointsSB.setSizePolicy(sizePolicy)
        self.regEspCPointsSB.setMinimum(1)
        self.regEspCPointsSB.setObjectName("regEspCPointsSB")
        self.gridlayout.addWidget(self.regEspCPointsSB,1,0,1,1)

        self.label_2 = QtGui.QLabel(AddCPointsDialog)
        self.label_2.setObjectName("label_2")
        self.gridlayout.addWidget(self.label_2,1,1,1,2)

        self.addRegEspCPointsBT = QtGui.QPushButton(AddCPointsDialog)
        self.addRegEspCPointsBT.setObjectName("addRegEspCPointsBT")
        self.gridlayout.addWidget(self.addRegEspCPointsBT,1,3,1,1)
        self.vboxlayout.addLayout(self.gridlayout)

        self.hboxlayout = QtGui.QHBoxLayout()
        self.hboxlayout.setObjectName("hboxlayout")

        self.cleanBT = QtGui.QPushButton(AddCPointsDialog)
        self.cleanBT.setObjectName("cleanBT")
        self.hboxlayout.addWidget(self.cleanBT)

        self.editBT = QtGui.QPushButton(AddCPointsDialog)
        self.editBT.setObjectName("editBT")
        self.hboxlayout.addWidget(self.editBT)

        spacerItem = QtGui.QSpacerItem(40,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout.addItem(spacerItem)

        self.buttonBox = QtGui.QDialogButtonBox(AddCPointsDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Close)
        self.buttonBox.setObjectName("buttonBox")
        self.hboxlayout.addWidget(self.buttonBox)
        self.vboxlayout.addLayout(self.hboxlayout)

        self.retranslateUi(AddCPointsDialog)
        QtCore.QObject.connect(self.buttonBox,QtCore.SIGNAL("accepted()"),AddCPointsDialog.accept)
        QtCore.QObject.connect(self.buttonBox,QtCore.SIGNAL("rejected()"),AddCPointsDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(AddCPointsDialog)

    def retranslateUi(self, AddCPointsDialog):
        AddCPointsDialog.setWindowTitle(QtGui.QApplication.translate("AddCPointsDialog", "Add Control Points", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("AddCPointsDialog", "Single Control Point at x=", None, QtGui.QApplication.UnicodeUTF8))
        self.addSingleCPointBT.setText(QtGui.QApplication.translate("AddCPointsDialog", "Add", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("AddCPointsDialog", "Regularly spaced Control Points", None, QtGui.QApplication.UnicodeUTF8))
        self.addRegEspCPointsBT.setText(QtGui.QApplication.translate("AddCPointsDialog", "Add", None, QtGui.QApplication.UnicodeUTF8))
        self.cleanBT.setText(QtGui.QApplication.translate("AddCPointsDialog", "Clean", None, QtGui.QApplication.UnicodeUTF8))
        self.editBT.setText(QtGui.QApplication.translate("AddCPointsDialog", "Edit", None, QtGui.QApplication.UnicodeUTF8))

