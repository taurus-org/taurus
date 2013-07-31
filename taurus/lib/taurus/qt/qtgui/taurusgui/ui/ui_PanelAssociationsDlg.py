# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/tmp/tmpfQKVhW.ui'
#
# Created: Fri Nov  4 17:03:41 2011
#      by: PyQt4 UI code generator 4.4.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_PanelAssociationsDlg(object):
    def setupUi(self, PanelAssociationsDlg):
        PanelAssociationsDlg.setObjectName("PanelAssociationsDlg")
        PanelAssociationsDlg.resize(402, 122)
        self.verticalLayout = QtGui.QVBoxLayout(PanelAssociationsDlg)
        self.verticalLayout.setObjectName("verticalLayout")
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 0, 0, 1, 1)
        self.label = QtGui.QLabel(PanelAssociationsDlg)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 1, 0, 1, 1)
        self.label_2 = QtGui.QLabel(PanelAssociationsDlg)
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 1, 2, 1, 1)
        self.instrumentCB = QtGui.QComboBox(PanelAssociationsDlg)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.instrumentCB.sizePolicy().hasHeightForWidth())
        self.instrumentCB.setSizePolicy(sizePolicy)
        self.instrumentCB.setEditable(False)
        self.instrumentCB.setObjectName("instrumentCB")
        self.gridLayout.addWidget(self.instrumentCB, 2, 0, 1, 1)
        self.label_3 = QtGui.QLabel(PanelAssociationsDlg)
        self.label_3.setAlignment(QtCore.Qt.AlignCenter)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 2, 1, 1, 1)
        self.panelCB = QtGui.QComboBox(PanelAssociationsDlg)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.panelCB.sizePolicy().hasHeightForWidth())
        self.panelCB.setSizePolicy(sizePolicy)
        self.panelCB.setEditable(False)
        self.panelCB.setObjectName("panelCB")
        self.gridLayout.addWidget(self.panelCB, 2, 2, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem1, 3, 0, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.refreshBT = QtGui.QPushButton(PanelAssociationsDlg)
        self.refreshBT.setObjectName("refreshBT")
        self.horizontalLayout.addWidget(self.refreshBT)
        spacerItem2 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem2)
        self.buttonBox = QtGui.QDialogButtonBox(PanelAssociationsDlg)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Apply|QtGui.QDialogButtonBox.Close|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.horizontalLayout.addWidget(self.buttonBox)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(PanelAssociationsDlg)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), PanelAssociationsDlg.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), PanelAssociationsDlg.reject)
        QtCore.QMetaObject.connectSlotsByName(PanelAssociationsDlg)

    def retranslateUi(self, PanelAssociationsDlg):
        PanelAssociationsDlg.setWindowTitle(QtGui.QApplication.translate("PanelAssociationsDlg", "Panel-Instrument associations", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("PanelAssociationsDlg", "Instrument", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("PanelAssociationsDlg", "Panel", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("PanelAssociationsDlg", "<->", None, QtGui.QApplication.UnicodeUTF8))
        self.refreshBT.setText(QtGui.QApplication.translate("PanelAssociationsDlg", "Refresh", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    PanelAssociationsDlg = QtGui.QDialog()
    ui = Ui_PanelAssociationsDlg()
    ui.setupUi(PanelAssociationsDlg)
    PanelAssociationsDlg.show()
    sys.exit(app.exec_())

