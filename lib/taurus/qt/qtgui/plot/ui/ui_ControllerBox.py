# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/cpascual/src/svn/taurus/widget/qwt/ui/ControllerBox.ui'
#
# Created: Mon Jan 25 12:21:47 2010
#      by: PyQt4 UI code generator 4.3.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_ControllerBox(object):
    def setupUi(self, ControllerBox):
        ControllerBox.setObjectName("ControllerBox")
        ControllerBox.resize(QtCore.QSize(QtCore.QRect(0,0,118,130).size()).expandedTo(ControllerBox.minimumSizeHint()))

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed,QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(ControllerBox.sizePolicy().hasHeightForWidth())
        ControllerBox.setSizePolicy(sizePolicy)

        self.vboxlayout = QtGui.QVBoxLayout(ControllerBox)
        self.vboxlayout.setObjectName("vboxlayout")

        self.box = QtGui.QGroupBox(ControllerBox)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum,QtGui.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.box.sizePolicy().hasHeightForWidth())
        self.box.setSizePolicy(sizePolicy)
        self.box.setMinimumSize(QtCore.QSize(100,0))
        self.box.setFlat(False)
        self.box.setCheckable(False)
        self.box.setObjectName("box")

        self.vboxlayout1 = QtGui.QVBoxLayout(self.box)
        self.vboxlayout1.setMargin(2)
        self.vboxlayout1.setObjectName("vboxlayout1")

        self.corrSB = QtGui.QDoubleSpinBox(self.box)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum,QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(252)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.corrSB.sizePolicy().hasHeightForWidth())
        self.corrSB.setSizePolicy(sizePolicy)
        self.corrSB.setAccelerated(True)
        self.corrSB.setMinimum(-1e+99)
        self.corrSB.setMaximum(1e+99)
        self.corrSB.setProperty("value",QtCore.QVariant(0.0))
        self.corrSB.setObjectName("corrSB")
        self.vboxlayout1.addWidget(self.corrSB)

        self.splitter_2 = QtGui.QSplitter(self.box)
        self.splitter_2.setOrientation(QtCore.Qt.Horizontal)
        self.splitter_2.setObjectName("splitter_2")

        self.lCopyBT = QtGui.QToolButton(self.splitter_2)
        self.lCopyBT.setObjectName("lCopyBT")

        self.rCopyBT = QtGui.QToolButton(self.splitter_2)
        self.rCopyBT.setObjectName("rCopyBT")
        self.vboxlayout1.addWidget(self.splitter_2)

        self.splitter = QtGui.QSplitter(self.box)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")

        self.lScaleBT = QtGui.QToolButton(self.splitter)
        self.lScaleBT.setObjectName("lScaleBT")

        self.rScaleBT = QtGui.QToolButton(self.splitter)
        self.rScaleBT.setObjectName("rScaleBT")
        self.vboxlayout1.addWidget(self.splitter)
        self.vboxlayout.addWidget(self.box)

        self.retranslateUi(ControllerBox)
        QtCore.QMetaObject.connectSlotsByName(ControllerBox)

    def retranslateUi(self, ControllerBox):
        ControllerBox.setWindowTitle(QtGui.QApplication.translate("ControllerBox", "ControlBox", None, QtGui.QApplication.UnicodeUTF8))
        self.box.setTitle(QtGui.QApplication.translate("ControllerBox", "x=", None, QtGui.QApplication.UnicodeUTF8))
        self.lCopyBT.setToolTip(QtGui.QApplication.translate("ControllerBox", "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
        "p, li { white-space: pre-wrap; }\n"
        "</style></head><body style=\" font-family:\'Sans Serif\'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
        "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Propagate value to the left</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.lCopyBT.setText(QtGui.QApplication.translate("ControllerBox", "<", None, QtGui.QApplication.UnicodeUTF8))
        self.rCopyBT.setToolTip(QtGui.QApplication.translate("ControllerBox", "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
        "p, li { white-space: pre-wrap; }\n"
        "</style></head><body style=\" font-family:\'Sans Serif\'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
        "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Propagate value to the right</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.rCopyBT.setText(QtGui.QApplication.translate("ControllerBox", ">", None, QtGui.QApplication.UnicodeUTF8))
        self.lScaleBT.setToolTip(QtGui.QApplication.translate("ControllerBox", "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
        "p, li { white-space: pre-wrap; }\n"
        "</style></head><body style=\" font-family:\'Sans Serif\'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
        "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Propagate value proportionally to the left</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.lScaleBT.setText(QtGui.QApplication.translate("ControllerBox", "<%", None, QtGui.QApplication.UnicodeUTF8))
        self.rScaleBT.setToolTip(QtGui.QApplication.translate("ControllerBox", "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
        "p, li { white-space: pre-wrap; }\n"
        "</style></head><body style=\" font-family:\'Sans Serif\'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
        "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Propagate value proportionally to the right</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.rScaleBT.setText(QtGui.QApplication.translate("ControllerBox", "%>", None, QtGui.QApplication.UnicodeUTF8))

