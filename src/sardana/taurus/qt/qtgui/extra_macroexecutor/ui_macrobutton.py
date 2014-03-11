# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'macrobutton.ui'
#
# Created: Tue Aug 16 15:59:17 2011
#      by: PyQt4 UI code generator 4.4.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_MacroButton(object):
    def setupUi(self, MacroButton):
        MacroButton.setObjectName("MacroButton")
        MacroButton.resize(106, 79)
        self.gridLayout_2 = QtGui.QGridLayout(MacroButton)
        self.gridLayout_2.setMargin(0)
        self.gridLayout_2.setSpacing(0)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.frame = QtGui.QFrame(MacroButton)
        self.frame.setFrameShape(QtGui.QFrame.Box)
        self.frame.setFrameShadow(QtGui.QFrame.Plain)
        self.frame.setLineWidth(3)
        self.frame.setMidLineWidth(3)
        self.frame.setObjectName("frame")
        self.gridLayout = QtGui.QGridLayout(self.frame)
        self.gridLayout.setMargin(0)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName("gridLayout")
        self.button = QtGui.QPushButton(self.frame)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.button.sizePolicy().hasHeightForWidth())
        self.button.setSizePolicy(sizePolicy)
        self.button.setCheckable(True)
        self.button.setAutoDefault(False)
        self.button.setObjectName("button")
        self.gridLayout.addWidget(self.button, 0, 0, 1, 1)
        self.progress = QtGui.QProgressBar(self.frame)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.progress.sizePolicy().hasHeightForWidth())
        self.progress.setSizePolicy(sizePolicy)
        self.progress.setMaximumSize(QtCore.QSize(16777215, 10))
        font = QtGui.QFont()
        font.setPointSize(6)
        self.progress.setFont(font)
        self.progress.setProperty("value", QtCore.QVariant(24))
        self.progress.setObjectName("progress")
        self.gridLayout.addWidget(self.progress, 1, 0, 1, 1)
        self.gridLayout_2.addWidget(self.frame, 0, 0, 1, 1)

        self.retranslateUi(MacroButton)
        QtCore.QMetaObject.connectSlotsByName(MacroButton)

    def retranslateUi(self, MacroButton):
        MacroButton.setWindowTitle(QtGui.QApplication.translate("MacroButton", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.button.setText(QtGui.QApplication.translate("MacroButton", "PushButton", None, QtGui.QApplication.UnicodeUTF8))

