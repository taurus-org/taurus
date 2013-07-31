# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/cpascual/src/svn/taurus/widget/dialog/ui/RawDataChooser.ui'
#
# Created: Fri Jan 29 11:48:43 2010
#      by: PyQt4 UI code generator 4.3.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_RawDataChooser(object):
    def setupUi(self, RawDataChooser):
        RawDataChooser.setObjectName("RawDataChooser")
        RawDataChooser.resize(QtCore.QSize(QtCore.QRect(0,0,373,468).size()).expandedTo(RawDataChooser.minimumSizeHint()))

        self.vboxlayout = QtGui.QVBoxLayout(RawDataChooser)
        self.vboxlayout.setObjectName("vboxlayout")

        self.groupBox = QtGui.QGroupBox(RawDataChooser)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred,QtGui.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy)
        self.groupBox.setObjectName("groupBox")

        self.vboxlayout1 = QtGui.QVBoxLayout(self.groupBox)
        self.vboxlayout1.setObjectName("vboxlayout1")

        self.hboxlayout = QtGui.QHBoxLayout()
        self.hboxlayout.setObjectName("hboxlayout")

        self.label_8 = QtGui.QLabel(self.groupBox)
        self.label_8.setObjectName("label_8")
        self.hboxlayout.addWidget(self.label_8)

        self.headerSB = QtGui.QSpinBox(self.groupBox)
        self.headerSB.setObjectName("headerSB")
        self.hboxlayout.addWidget(self.headerSB)
        self.vboxlayout1.addLayout(self.hboxlayout)

        self.hboxlayout1 = QtGui.QHBoxLayout()
        self.hboxlayout1.setObjectName("hboxlayout1")

        self.label_9 = QtGui.QLabel(self.groupBox)
        self.label_9.setObjectName("label_9")
        self.hboxlayout1.addWidget(self.label_9)

        self.xcolSB = QtGui.QSpinBox(self.groupBox)
        self.xcolSB.setMinimum(-1)
        self.xcolSB.setProperty("value",QtCore.QVariant(-1))
        self.xcolSB.setObjectName("xcolSB")
        self.hboxlayout1.addWidget(self.xcolSB)
        self.vboxlayout1.addLayout(self.hboxlayout1)

        self.hboxlayout2 = QtGui.QHBoxLayout()
        self.hboxlayout2.setObjectName("hboxlayout2")

        self.openFilesBT = QtGui.QPushButton(self.groupBox)
        self.openFilesBT.setObjectName("openFilesBT")
        self.hboxlayout2.addWidget(self.openFilesBT)

        spacerItem = QtGui.QSpacerItem(40,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout2.addItem(spacerItem)
        self.vboxlayout1.addLayout(self.hboxlayout2)
        self.vboxlayout.addWidget(self.groupBox)

        self.groupBox_2 = QtGui.QGroupBox(RawDataChooser)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred,QtGui.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox_2.sizePolicy().hasHeightForWidth())
        self.groupBox_2.setSizePolicy(sizePolicy)
        self.groupBox_2.setObjectName("groupBox_2")

        self.vboxlayout2 = QtGui.QVBoxLayout(self.groupBox_2)
        self.vboxlayout2.setObjectName("vboxlayout2")

        self.groupBox_3 = QtGui.QGroupBox(self.groupBox_2)
        self.groupBox_3.setObjectName("groupBox_3")

        self.vboxlayout3 = QtGui.QVBoxLayout(self.groupBox_3)
        self.vboxlayout3.setObjectName("vboxlayout3")

        self.hboxlayout3 = QtGui.QHBoxLayout()
        self.hboxlayout3.setObjectName("hboxlayout3")

        self.xRangeRB = QtGui.QRadioButton(self.groupBox_3)
        self.xRangeRB.setChecked(True)
        self.xRangeRB.setObjectName("xRangeRB")
        self.hboxlayout3.addWidget(self.xRangeRB)

        self.hboxlayout4 = QtGui.QHBoxLayout()
        self.hboxlayout4.setObjectName("hboxlayout4")

        self.label_5 = QtGui.QLabel(self.groupBox_3)
        self.label_5.setObjectName("label_5")
        self.hboxlayout4.addWidget(self.label_5)

        self.xFromLE = QtGui.QLineEdit(self.groupBox_3)
        self.xFromLE.setObjectName("xFromLE")
        self.hboxlayout4.addWidget(self.xFromLE)

        self.label_6 = QtGui.QLabel(self.groupBox_3)
        self.label_6.setObjectName("label_6")
        self.hboxlayout4.addWidget(self.label_6)

        self.xToLE = QtGui.QLineEdit(self.groupBox_3)
        self.xToLE.setObjectName("xToLE")
        self.hboxlayout4.addWidget(self.xToLE)

        self.label_7 = QtGui.QLabel(self.groupBox_3)
        self.label_7.setObjectName("label_7")
        self.hboxlayout4.addWidget(self.label_7)

        self.xStepLE = QtGui.QLineEdit(self.groupBox_3)
        self.xStepLE.setObjectName("xStepLE")
        self.hboxlayout4.addWidget(self.xStepLE)
        self.hboxlayout3.addLayout(self.hboxlayout4)
        self.vboxlayout3.addLayout(self.hboxlayout3)

        self.hboxlayout5 = QtGui.QHBoxLayout()
        self.hboxlayout5.setObjectName("hboxlayout5")

        self.xValuesRB = QtGui.QRadioButton(self.groupBox_3)
        self.xValuesRB.setObjectName("xValuesRB")
        self.hboxlayout5.addWidget(self.xValuesRB)

        self.xValuesLE = QtGui.QLineEdit(self.groupBox_3)
        self.xValuesLE.setObjectName("xValuesLE")
        self.hboxlayout5.addWidget(self.xValuesLE)
        self.vboxlayout3.addLayout(self.hboxlayout5)
        self.vboxlayout2.addWidget(self.groupBox_3)

        self.groupBox_4 = QtGui.QGroupBox(self.groupBox_2)
        self.groupBox_4.setObjectName("groupBox_4")

        self.vboxlayout4 = QtGui.QVBoxLayout(self.groupBox_4)
        self.vboxlayout4.setObjectName("vboxlayout4")

        self.hboxlayout6 = QtGui.QHBoxLayout()
        self.hboxlayout6.setObjectName("hboxlayout6")

        self.label = QtGui.QLabel(self.groupBox_4)
        self.label.setObjectName("label")
        self.hboxlayout6.addWidget(self.label)

        self.f_xLE = QtGui.QLineEdit(self.groupBox_4)
        self.f_xLE.setObjectName("f_xLE")
        self.hboxlayout6.addWidget(self.f_xLE)
        self.vboxlayout4.addLayout(self.hboxlayout6)
        self.vboxlayout2.addWidget(self.groupBox_4)

        self.hboxlayout7 = QtGui.QHBoxLayout()
        self.hboxlayout7.setObjectName("hboxlayout7")

        spacerItem1 = QtGui.QSpacerItem(40,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout7.addItem(spacerItem1)

        self.addCurveBT = QtGui.QPushButton(self.groupBox_2)
        self.addCurveBT.setObjectName("addCurveBT")
        self.hboxlayout7.addWidget(self.addCurveBT)
        self.vboxlayout2.addLayout(self.hboxlayout7)
        self.vboxlayout.addWidget(self.groupBox_2)

        self.retranslateUi(RawDataChooser)
        QtCore.QMetaObject.connectSlotsByName(RawDataChooser)

    def retranslateUi(self, RawDataChooser):
        RawDataChooser.setWindowTitle(QtGui.QApplication.translate("RawDataChooser", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("RawDataChooser", "Load data from ASCII File", None, QtGui.QApplication.UnicodeUTF8))
        self.label_8.setText(QtGui.QApplication.translate("RawDataChooser", "Number of header lines", None, QtGui.QApplication.UnicodeUTF8))
        self.headerSB.setToolTip(QtGui.QApplication.translate("RawDataChooser", "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
        "p, li { white-space: pre-wrap; }\n"
        "</style></head><body style=\" font-family:\'Sans Serif\'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
        "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">This many lines at the beginning of the file will be ignored</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.label_9.setText(QtGui.QApplication.translate("RawDataChooser", "x values in colum:", None, QtGui.QApplication.UnicodeUTF8))
        self.xcolSB.setToolTip(QtGui.QApplication.translate("RawDataChooser", "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
        "p, li { white-space: pre-wrap; }\n"
        "</style></head><body style=\" font-family:\'Sans Serif\'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
        "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">In multi column files, the values of this column will be used for the abcissas. Set to \"no x\" if the abcissas should be automatically generated as the row number.</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.xcolSB.setSpecialValueText(QtGui.QApplication.translate("RawDataChooser", "--", None, QtGui.QApplication.UnicodeUTF8))
        self.openFilesBT.setText(QtGui.QApplication.translate("RawDataChooser", "Open File(s)...", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_2.setTitle(QtGui.QApplication.translate("RawDataChooser", "Generate curve from function", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_3.setTitle(QtGui.QApplication.translate("RawDataChooser", "x", None, QtGui.QApplication.UnicodeUTF8))
        self.xRangeRB.setText(QtGui.QApplication.translate("RawDataChooser", "Range", None, QtGui.QApplication.UnicodeUTF8))
        self.label_5.setText(QtGui.QApplication.translate("RawDataChooser", "from", None, QtGui.QApplication.UnicodeUTF8))
        self.xFromLE.setText(QtGui.QApplication.translate("RawDataChooser", "0", None, QtGui.QApplication.UnicodeUTF8))
        self.label_6.setText(QtGui.QApplication.translate("RawDataChooser", "to", None, QtGui.QApplication.UnicodeUTF8))
        self.xToLE.setText(QtGui.QApplication.translate("RawDataChooser", "100", None, QtGui.QApplication.UnicodeUTF8))
        self.label_7.setText(QtGui.QApplication.translate("RawDataChooser", "step", None, QtGui.QApplication.UnicodeUTF8))
        self.xStepLE.setText(QtGui.QApplication.translate("RawDataChooser", "1", None, QtGui.QApplication.UnicodeUTF8))
        self.xValuesRB.setText(QtGui.QApplication.translate("RawDataChooser", "Values", None, QtGui.QApplication.UnicodeUTF8))
        self.xValuesLE.setToolTip(QtGui.QApplication.translate("RawDataChooser", "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
        "p, li { white-space: pre-wrap; }\n"
        "</style></head><body style=\" font-family:\'Sans Serif\'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
        "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">comma separated list of values</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_4.setTitle(QtGui.QApplication.translate("RawDataChooser", "y", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("RawDataChooser", "f(x)=", None, QtGui.QApplication.UnicodeUTF8))
        self.addCurveBT.setToolTip(QtGui.QApplication.translate("RawDataChooser", "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
        "p, li { white-space: pre-wrap; }\n"
        "</style></head><body style=\" font-family:\'Sans Serif\'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
        "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Generate new curve and add it</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.addCurveBT.setText(QtGui.QApplication.translate("RawDataChooser", "Add", None, QtGui.QApplication.UnicodeUTF8))

