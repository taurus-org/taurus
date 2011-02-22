# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'taurusserverswidget.ui'
#
# Created: Tue Aug 11 15:51:37 2009
#      by: PyQt4 UI code generator 4.3.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_TaurusServersWidget(object):
    def setupUi(self, TaurusServersWidget):
        TaurusServersWidget.setObjectName("TaurusServersWidget")
        TaurusServersWidget.resize(QtCore.QSize(QtCore.QRect(0,0,508,312).size()).expandedTo(TaurusServersWidget.minimumSizeHint()))

        self.gridlayout = QtGui.QGridLayout(TaurusServersWidget)
        self.gridlayout.setObjectName("gridlayout")

        self.hboxlayout = QtGui.QHBoxLayout()
        self.hboxlayout.setObjectName("hboxlayout")

        self.vboxlayout = QtGui.QVBoxLayout()
        self.vboxlayout.setObjectName("vboxlayout")

        self.frDSStates = QtGui.QFrame(TaurusServersWidget)
        self.frDSStates.setObjectName("frDSStates")
        self.vboxlayout.addWidget(self.frDSStates)

        spacerItem = QtGui.QSpacerItem(20,40,QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Expanding)
        self.vboxlayout.addItem(spacerItem)
        self.hboxlayout.addLayout(self.vboxlayout)

        self.frButtons = QtGui.QFrame(TaurusServersWidget)
        self.frButtons.setMaximumSize(QtCore.QSize(100,16777215))
        self.frButtons.setFrameShape(QtGui.QFrame.NoFrame)
        self.frButtons.setFrameShadow(QtGui.QFrame.Plain)
        self.frButtons.setObjectName("frButtons")

        self.gridlayout1 = QtGui.QGridLayout(self.frButtons)
        self.gridlayout1.setMargin(1)
        self.gridlayout1.setSpacing(1)
        self.gridlayout1.setObjectName("gridlayout1")

        spacerItem1 = QtGui.QSpacerItem(20,40,QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Expanding)
        self.gridlayout1.addItem(spacerItem1,0,0,1,1)

        self.btnStartAll = QtGui.QPushButton(self.frButtons)
        self.btnStartAll.setMaximumSize(QtCore.QSize(80,16777215))
        self.btnStartAll.setObjectName("btnStartAll")
        self.gridlayout1.addWidget(self.btnStartAll,1,0,1,1)

        self.btnStopAll = QtGui.QPushButton(self.frButtons)
        self.btnStopAll.setMaximumSize(QtCore.QSize(80,16777215))
        self.btnStopAll.setObjectName("btnStopAll")
        self.gridlayout1.addWidget(self.btnStopAll,2,0,1,1)

        self.btnRestartAll = QtGui.QPushButton(self.frButtons)
        self.btnRestartAll.setMaximumSize(QtCore.QSize(80,16777215))
        self.btnRestartAll.setObjectName("btnRestartAll")
        self.gridlayout1.addWidget(self.btnRestartAll,3,0,1,1)
        self.hboxlayout.addWidget(self.frButtons)
        self.gridlayout.addLayout(self.hboxlayout,0,0,1,1)

        self.retranslateUi(TaurusServersWidget)
        QtCore.QMetaObject.connectSlotsByName(TaurusServersWidget)

    def retranslateUi(self, TaurusServersWidget):
        TaurusServersWidget.setWindowTitle(QtGui.QApplication.translate("TaurusServersWidget", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.btnStartAll.setText(QtGui.QApplication.translate("TaurusServersWidget", "Start All", None, QtGui.QApplication.UnicodeUTF8))
        self.btnStopAll.setText(QtGui.QApplication.translate("TaurusServersWidget", "Stop All", None, QtGui.QApplication.UnicodeUTF8))
        self.btnRestartAll.setText(QtGui.QApplication.translate("TaurusServersWidget", "Restart All", None, QtGui.QApplication.UnicodeUTF8))

