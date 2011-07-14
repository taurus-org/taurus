# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/tmp/tmpjOVn8C.ui'
#
# Created: Thu Jul 14 17:28:55 2011
#      by: PyQt4 UI code generator 4.4.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_CurveItemConfDlg(object):
    def setupUi(self, CurveItemConfDlg):
        CurveItemConfDlg.setObjectName("CurveItemConfDlg")
        CurveItemConfDlg.resize(812, 495)
        self.gridLayout = QtGui.QGridLayout(CurveItemConfDlg)
        self.gridLayout.setObjectName("gridLayout")
        self.splitter = QtGui.QSplitter(CurveItemConfDlg)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        self.groupBox_2 = QtGui.QGroupBox(self.splitter)
        self.groupBox_2.setObjectName("groupBox_2")
        self.verticalLayout_5 = QtGui.QVBoxLayout(self.groupBox_2)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.tabWidget = QtGui.QTabWidget(self.groupBox_2)
        self.tabWidget.setObjectName("tabWidget")
        self.tangoTab = QtGui.QWidget()
        self.tangoTab.setObjectName("tangoTab")
        self.horizontalLayout_4 = QtGui.QHBoxLayout(self.tangoTab)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.tangoTree = TaurusModelSelectorTree(self.tangoTab)
        self.tangoTree.setObjectName("tangoTree")
        self.horizontalLayout_4.addWidget(self.tangoTree)
        self.tabWidget.addTab(self.tangoTab, "")
        self.verticalLayout_5.addWidget(self.tabWidget)
        self.groupBox_3 = QtGui.QGroupBox(self.splitter)
        self.groupBox_3.setObjectName("groupBox_3")
        self.verticalLayout_7 = QtGui.QVBoxLayout(self.groupBox_3)
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.verticalLayout_4 = QtGui.QVBoxLayout()
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.curvesTable = QtGui.QTableView(self.groupBox_3)
        self.curvesTable.setMinimumSize(QtCore.QSize(400, 0))
        self.curvesTable.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.curvesTable.setDragDropMode(QtGui.QAbstractItemView.DragDrop)
        self.curvesTable.setObjectName("curvesTable")
        self.verticalLayout_4.addWidget(self.curvesTable)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.removeCurvesBT = QtGui.QToolButton(self.groupBox_3)
        self.removeCurvesBT.setContextMenuPolicy(QtCore.Qt.NoContextMenu)
        self.removeCurvesBT.setPopupMode(QtGui.QToolButton.MenuButtonPopup)
        self.removeCurvesBT.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.removeCurvesBT.setObjectName("removeCurvesBT")
        self.horizontalLayout_2.addWidget(self.removeCurvesBT)
        self.verticalLayout_4.addLayout(self.horizontalLayout_2)
        self.verticalLayout_7.addLayout(self.verticalLayout_4)
        self.gridLayout.addWidget(self.splitter, 0, 0, 1, 1)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem1)
        self.reloadBT = QtGui.QPushButton(CurveItemConfDlg)
        self.reloadBT.setObjectName("reloadBT")
        self.horizontalLayout_3.addWidget(self.reloadBT)
        self.cancelBT = QtGui.QPushButton(CurveItemConfDlg)
        self.cancelBT.setObjectName("cancelBT")
        self.horizontalLayout_3.addWidget(self.cancelBT)
        self.applyBT = QtGui.QPushButton(CurveItemConfDlg)
        self.applyBT.setObjectName("applyBT")
        self.horizontalLayout_3.addWidget(self.applyBT)
        self.gridLayout.addLayout(self.horizontalLayout_3, 1, 0, 1, 1)

        self.retranslateUi(CurveItemConfDlg)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(CurveItemConfDlg)

    def retranslateUi(self, CurveItemConfDlg):
        CurveItemConfDlg.setWindowTitle(QtGui.QApplication.translate("CurveItemConfDlg", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_2.setTitle(QtGui.QApplication.translate("CurveItemConfDlg", "Sources of data", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tangoTab), QtGui.QApplication.translate("CurveItemConfDlg", "Tango", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_3.setTitle(QtGui.QApplication.translate("CurveItemConfDlg", "Contents & appearance", None, QtGui.QApplication.UnicodeUTF8))
        self.removeCurvesBT.setText(QtGui.QApplication.translate("CurveItemConfDlg", " Remove", None, QtGui.QApplication.UnicodeUTF8))
        self.reloadBT.setText(QtGui.QApplication.translate("CurveItemConfDlg", "Reload", None, QtGui.QApplication.UnicodeUTF8))
        self.cancelBT.setText(QtGui.QApplication.translate("CurveItemConfDlg", "Cancel", None, QtGui.QApplication.UnicodeUTF8))
        self.applyBT.setText(QtGui.QApplication.translate("CurveItemConfDlg", "Apply", None, QtGui.QApplication.UnicodeUTF8))

from taurus.qt.qtgui.panel import TaurusModelSelectorTree

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    CurveItemConfDlg = QtGui.QWidget()
    ui = Ui_CurveItemConfDlg()
    ui.setupUi(CurveItemConfDlg)
    CurveItemConfDlg.show()
    sys.exit(app.exec_())

