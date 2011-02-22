# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'CurvePropertiesView.ui'
#
# Created: Fri Jul 30 12:08:19 2010
#      by: PyQt4 UI code generator 4.4.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_CurvePropertiesView(object):
    def setupUi(self, CurvePropertiesView):
        CurvePropertiesView.setObjectName("CurvePropertiesView")
        CurvePropertiesView.resize(274, 198)
        CurvePropertiesView.setMinimumSize(QtCore.QSize(250, 180))
        self.horizontalLayout = QtGui.QHBoxLayout(CurvePropertiesView)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.lineGB = QtGui.QGroupBox(CurvePropertiesView)
        self.lineGB.setObjectName("lineGB")
        self._2 = QtGui.QGridLayout(self.lineGB)
        self._2.setObjectName("_2")
        self.label_4 = QtGui.QLabel(self.lineGB)
        self.label_4.setObjectName("label_4")
        self._2.addWidget(self.label_4, 0, 0, 1, 1)
        self.lStyleCB = QtGui.QComboBox(self.lineGB)
        self.lStyleCB.setObjectName("lStyleCB")
        self._2.addWidget(self.lStyleCB, 0, 1, 1, 1)
        self.label_5 = QtGui.QLabel(self.lineGB)
        self.label_5.setObjectName("label_5")
        self._2.addWidget(self.label_5, 1, 0, 1, 1)
        self.lWidthSB = QtGui.QSpinBox(self.lineGB)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lWidthSB.sizePolicy().hasHeightForWidth())
        self.lWidthSB.setSizePolicy(sizePolicy)
        self.lWidthSB.setMinimum(-1)
        self.lWidthSB.setMaximum(10)
        self.lWidthSB.setProperty("value", QtCore.QVariant(1))
        self.lWidthSB.setObjectName("lWidthSB")
        self._2.addWidget(self.lWidthSB, 1, 1, 1, 1)
        self.label_6 = QtGui.QLabel(self.lineGB)
        self.label_6.setObjectName("label_6")
        self._2.addWidget(self.label_6, 2, 0, 1, 1)
        self.lColorCB = QtGui.QComboBox(self.lineGB)
        self.lColorCB.setObjectName("lColorCB")
        self._2.addWidget(self.lColorCB, 2, 1, 1, 1)
        self.labelCurveStyle = QtGui.QLabel(self.lineGB)
        self.labelCurveStyle.setObjectName("labelCurveStyle")
        self._2.addWidget(self.labelCurveStyle, 3, 0, 1, 1)
        self.cStyleCB = QtGui.QComboBox(self.lineGB)
        self.cStyleCB.setObjectName("cStyleCB")
        self._2.addWidget(self.cStyleCB, 3, 1, 1, 1)
        self.cFillCB = QtGui.QCheckBox(self.lineGB)
        self.cFillCB.setTristate(True)
        self.cFillCB.setObjectName("cFillCB")
        self._2.addWidget(self.cFillCB, 4, 0, 1, 2)
        self.horizontalLayout.addWidget(self.lineGB)
        self.symbolGB = QtGui.QGroupBox(CurvePropertiesView)
        self.symbolGB.setObjectName("symbolGB")
        self._3 = QtGui.QGridLayout(self.symbolGB)
        self._3.setObjectName("_3")
        self.label = QtGui.QLabel(self.symbolGB)
        self.label.setObjectName("label")
        self._3.addWidget(self.label, 0, 0, 1, 1)
        self.sStyleCB = QtGui.QComboBox(self.symbolGB)
        self.sStyleCB.setObjectName("sStyleCB")
        self._3.addWidget(self.sStyleCB, 0, 1, 1, 1)
        self.label_2 = QtGui.QLabel(self.symbolGB)
        self.label_2.setObjectName("label_2")
        self._3.addWidget(self.label_2, 1, 0, 1, 1)
        self.sSizeSB = QtGui.QSpinBox(self.symbolGB)
        self.sSizeSB.setMinimum(-1)
        self.sSizeSB.setMaximum(10)
        self.sSizeSB.setSingleStep(1)
        self.sSizeSB.setProperty("value", QtCore.QVariant(3))
        self.sSizeSB.setObjectName("sSizeSB")
        self._3.addWidget(self.sSizeSB, 1, 1, 1, 1)
        self.label_3 = QtGui.QLabel(self.symbolGB)
        self.label_3.setObjectName("label_3")
        self._3.addWidget(self.label_3, 2, 0, 1, 1)
        self.sColorCB = QtGui.QComboBox(self.symbolGB)
        self.sColorCB.setObjectName("sColorCB")
        self._3.addWidget(self.sColorCB, 2, 1, 1, 1)
        self.sFillCB = QtGui.QCheckBox(self.symbolGB)
        self.sFillCB.setTristate(True)
        self.sFillCB.setObjectName("sFillCB")
        self._3.addWidget(self.sFillCB, 3, 0, 1, 2)
        spacerItem = QtGui.QSpacerItem(111, 16, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self._3.addItem(spacerItem, 4, 0, 1, 2)
        self.horizontalLayout.addWidget(self.symbolGB)
        self.label_4.setBuddy(self.lStyleCB)
        self.label_5.setBuddy(self.lWidthSB)
        self.label_6.setBuddy(self.lColorCB)
        self.label.setBuddy(self.sStyleCB)
        self.label_2.setBuddy(self.sSizeSB)
        self.label_3.setBuddy(self.sColorCB)

        self.retranslateUi(CurvePropertiesView)
        QtCore.QMetaObject.connectSlotsByName(CurvePropertiesView)

    def retranslateUi(self, CurvePropertiesView):
        CurvePropertiesView.setWindowTitle(QtGui.QApplication.translate("CurvePropertiesView", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.lineGB.setTitle(QtGui.QApplication.translate("CurvePropertiesView", "Line", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("CurvePropertiesView", "S&tyle", None, QtGui.QApplication.UnicodeUTF8))
        self.lStyleCB.setToolTip(QtGui.QApplication.translate("CurvePropertiesView", "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Sans Serif\'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Style of the pen used to connect the points.</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.label_5.setText(QtGui.QApplication.translate("CurvePropertiesView", "&Width", None, QtGui.QApplication.UnicodeUTF8))
        self.lWidthSB.setSpecialValueText(QtGui.QApplication.translate("CurvePropertiesView", "--", None, QtGui.QApplication.UnicodeUTF8))
        self.label_6.setText(QtGui.QApplication.translate("CurvePropertiesView", "C&olor", None, QtGui.QApplication.UnicodeUTF8))
        self.labelCurveStyle.setText(QtGui.QApplication.translate("CurvePropertiesView", "Mode", None, QtGui.QApplication.UnicodeUTF8))
        self.cStyleCB.setToolTip(QtGui.QApplication.translate("CurvePropertiesView", "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Sans Serif\'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Connector mode: how the data points are connected (steps, straight lines,...)</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.cFillCB.setText(QtGui.QApplication.translate("CurvePropertiesView", "&Area Fill", None, QtGui.QApplication.UnicodeUTF8))
        self.symbolGB.setTitle(QtGui.QApplication.translate("CurvePropertiesView", "Symbols", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("CurvePropertiesView", "&Style", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("CurvePropertiesView", "Si&ze", None, QtGui.QApplication.UnicodeUTF8))
        self.sSizeSB.setSpecialValueText(QtGui.QApplication.translate("CurvePropertiesView", "--", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("CurvePropertiesView", "&Color", None, QtGui.QApplication.UnicodeUTF8))
        self.sFillCB.setText(QtGui.QApplication.translate("CurvePropertiesView", "&Fill", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    CurvePropertiesView = QtGui.QWidget()
    ui = Ui_CurvePropertiesView()
    ui.setupUi(CurvePropertiesView)
    CurvePropertiesView.show()
    sys.exit(app.exec_())

