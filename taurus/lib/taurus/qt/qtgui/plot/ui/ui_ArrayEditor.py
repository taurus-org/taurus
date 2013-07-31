# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ArrayEditor.ui'
#
# Created: Thu Sep 30 15:22:10 2010
#      by: PyQt4 UI code generator 4.7.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_ArrayEditor(object):
    def setupUi(self, ArrayEditor):
        ArrayEditor.setObjectName("ArrayEditor")
        ArrayEditor.resize(879, 654)
        self.vboxlayout = QtGui.QVBoxLayout(ArrayEditor)
        self.vboxlayout.setObjectName("vboxlayout")
        self.plot1 = TaurusPlot(ArrayEditor)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(2)
        sizePolicy.setHeightForWidth(self.plot1.sizePolicy().hasHeightForWidth())
        self.plot1.setSizePolicy(sizePolicy)
        self.plot1.setMinimumSize(QtCore.QSize(400, 150))
        self.plot1.setAllowZoomers(False)
        self.plot1.setObjectName("plot1")
        self.vboxlayout.addWidget(self.plot1)
        self.plot2 = TaurusPlot(ArrayEditor)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.plot2.sizePolicy().hasHeightForWidth())
        self.plot2.setSizePolicy(sizePolicy)
        self.plot2.setMinimumSize(QtCore.QSize(400, 150))
        self.plot2.setAllowZoomers(False)
        self.plot2.setObjectName("plot2")
        self.vboxlayout.addWidget(self.plot2)
        self.cpointsGroupBox = QtGui.QGroupBox(ArrayEditor)
        self.cpointsGroupBox.setMinimumSize(QtCore.QSize(0, 180))
        self.cpointsGroupBox.setObjectName("cpointsGroupBox")
        self.hboxlayout = QtGui.QHBoxLayout(self.cpointsGroupBox)
        self.hboxlayout.setContentsMargins(0, 0, 1, 1)
        self.hboxlayout.setObjectName("hboxlayout")
        self.controllersContainer = QtGui.QWidget(self.cpointsGroupBox)
        self.controllersContainer.setObjectName("controllersContainer")
        self.hboxlayout.addWidget(self.controllersContainer)
        self.vboxlayout1 = QtGui.QVBoxLayout()
        self.vboxlayout1.setObjectName("vboxlayout1")
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.vboxlayout1.addItem(spacerItem)
        self.addCPointsBT = QtGui.QPushButton(self.cpointsGroupBox)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.addCPointsBT.sizePolicy().hasHeightForWidth())
        self.addCPointsBT.setSizePolicy(sizePolicy)
        self.addCPointsBT.setObjectName("addCPointsBT")
        self.vboxlayout1.addWidget(self.addCPointsBT)
        self.hboxlayout.addLayout(self.vboxlayout1)
        self.vboxlayout.addWidget(self.cpointsGroupBox)

        self.retranslateUi(ArrayEditor)
        QtCore.QMetaObject.connectSlotsByName(ArrayEditor)

    def retranslateUi(self, ArrayEditor):
        ArrayEditor.setWindowTitle(QtGui.QApplication.translate("ArrayEditor", "ArrayEditor", None, QtGui.QApplication.UnicodeUTF8))
        self.cpointsGroupBox.setTitle(QtGui.QApplication.translate("ArrayEditor", "Control Points", None, QtGui.QApplication.UnicodeUTF8))
        self.addCPointsBT.setText(QtGui.QApplication.translate("ArrayEditor", "Add...", None, QtGui.QApplication.UnicodeUTF8))

from taurus.qt.qtgui.plot import TaurusPlot
