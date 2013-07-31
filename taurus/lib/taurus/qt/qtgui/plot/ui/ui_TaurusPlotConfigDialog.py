# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/cpascual/src/svn/taurus/widget/qwt/ui/TaurusPlotConfigDialog.ui'
#
# Created: Fri Jan 29 11:47:12 2010
#      by: PyQt4 UI code generator 4.3.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_TaurusPlotConfigDialog(object):
    def setupUi(self, TaurusPlotConfigDialog):
        TaurusPlotConfigDialog.setObjectName("TaurusPlotConfigDialog")
        TaurusPlotConfigDialog.resize(QtCore.QSize(QtCore.QRect(0,0,573,486).size()).expandedTo(TaurusPlotConfigDialog.minimumSizeHint()))
        TaurusPlotConfigDialog.setModal(True)

        self.gridlayout = QtGui.QGridLayout(TaurusPlotConfigDialog)
        self.gridlayout.setObjectName("gridlayout")

        self.curveAppearanceGB = QtGui.QGroupBox(TaurusPlotConfigDialog)
        self.curveAppearanceGB.setObjectName("curveAppearanceGB")
        self.gridlayout.addWidget(self.curveAppearanceGB,0,0,1,3)

        self.xGroupBox = QtGui.QGroupBox(TaurusPlotConfigDialog)
        self.xGroupBox.setObjectName("xGroupBox")

        self.gridlayout1 = QtGui.QGridLayout(self.xGroupBox)
        self.gridlayout1.setObjectName("gridlayout1")

        self.xAutoGroupBox = QtGui.QGroupBox(self.xGroupBox)
        self.xAutoGroupBox.setCheckable(True)
        self.xAutoGroupBox.setChecked(False)
        self.xAutoGroupBox.setObjectName("xAutoGroupBox")

        self.gridlayout2 = QtGui.QGridLayout(self.xAutoGroupBox)
        self.gridlayout2.setObjectName("gridlayout2")

        self.xLabelMin = QtGui.QLabel(self.xAutoGroupBox)
        self.xLabelMin.setObjectName("xLabelMin")
        self.gridlayout2.addWidget(self.xLabelMin,0,0,1,1)

        self.xEditMin = QtGui.QLineEdit(self.xAutoGroupBox)
        self.xEditMin.setMinimumSize(QtCore.QSize(150,0))
        self.xEditMin.setObjectName("xEditMin")
        self.gridlayout2.addWidget(self.xEditMin,0,1,1,1)

        self.xLabelMax = QtGui.QLabel(self.xAutoGroupBox)
        self.xLabelMax.setObjectName("xLabelMax")
        self.gridlayout2.addWidget(self.xLabelMax,1,0,1,1)

        self.xEditMax = QtGui.QLineEdit(self.xAutoGroupBox)
        self.xEditMax.setMinimumSize(QtCore.QSize(150,0))
        self.xEditMax.setObjectName("xEditMax")
        self.gridlayout2.addWidget(self.xEditMax,1,1,1,1)
        self.gridlayout1.addWidget(self.xAutoGroupBox,0,0,1,2)

        self.xLabelRange = QtGui.QLabel(self.xGroupBox)
        self.xLabelRange.setObjectName("xLabelRange")
        self.gridlayout1.addWidget(self.xLabelRange,1,0,1,1)

        self.xRangeCB = QtGui.QComboBox(self.xGroupBox)
        self.xRangeCB.setEditable(True)
        self.xRangeCB.setObjectName("xRangeCB")
        self.gridlayout1.addWidget(self.xRangeCB,1,1,1,1)

        self.xModeLabel = QtGui.QLabel(self.xGroupBox)
        self.xModeLabel.setObjectName("xModeLabel")
        self.gridlayout1.addWidget(self.xModeLabel,2,0,1,1)

        self.xModeComboBox = QtGui.QComboBox(self.xGroupBox)
        self.xModeComboBox.setObjectName("xModeComboBox")
        self.gridlayout1.addWidget(self.xModeComboBox,2,1,1,1)

        self.xDynScaleCheckBox = QtGui.QCheckBox(self.xGroupBox)
        self.xDynScaleCheckBox.setObjectName("xDynScaleCheckBox")
        self.gridlayout1.addWidget(self.xDynScaleCheckBox,3,0,1,2)
        self.gridlayout.addWidget(self.xGroupBox,1,0,2,1)

        self.tabWidget = QtGui.QTabWidget(TaurusPlotConfigDialog)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred,QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tabWidget.sizePolicy().hasHeightForWidth())
        self.tabWidget.setSizePolicy(sizePolicy)
        self.tabWidget.setObjectName("tabWidget")

        self.y1Tab = QtGui.QWidget()
        self.y1Tab.setObjectName("y1Tab")

        self.gridlayout3 = QtGui.QGridLayout(self.y1Tab)
        self.gridlayout3.setObjectName("gridlayout3")

        self.y1AutoGroupBox = QtGui.QGroupBox(self.y1Tab)
        self.y1AutoGroupBox.setCheckable(True)
        self.y1AutoGroupBox.setChecked(False)
        self.y1AutoGroupBox.setObjectName("y1AutoGroupBox")

        self.gridlayout4 = QtGui.QGridLayout(self.y1AutoGroupBox)
        self.gridlayout4.setObjectName("gridlayout4")

        self.y1LabelMin = QtGui.QLabel(self.y1AutoGroupBox)
        self.y1LabelMin.setObjectName("y1LabelMin")
        self.gridlayout4.addWidget(self.y1LabelMin,0,0,1,1)

        self.y1EditMin = QtGui.QLineEdit(self.y1AutoGroupBox)
        self.y1EditMin.setObjectName("y1EditMin")
        self.gridlayout4.addWidget(self.y1EditMin,0,1,1,1)

        self.y1LabelMax = QtGui.QLabel(self.y1AutoGroupBox)
        self.y1LabelMax.setObjectName("y1LabelMax")
        self.gridlayout4.addWidget(self.y1LabelMax,1,0,1,1)

        self.y1EditMax = QtGui.QLineEdit(self.y1AutoGroupBox)
        self.y1EditMax.setObjectName("y1EditMax")
        self.gridlayout4.addWidget(self.y1EditMax,1,1,1,1)
        self.gridlayout3.addWidget(self.y1AutoGroupBox,0,0,1,2)

        self.y1ModeLabel = QtGui.QLabel(self.y1Tab)
        self.y1ModeLabel.setObjectName("y1ModeLabel")
        self.gridlayout3.addWidget(self.y1ModeLabel,1,0,1,1)

        self.y1ModeComboBox = QtGui.QComboBox(self.y1Tab)
        self.y1ModeComboBox.setObjectName("y1ModeComboBox")
        self.gridlayout3.addWidget(self.y1ModeComboBox,1,1,1,1)
        self.tabWidget.addTab(self.y1Tab,"")

        self.y2Tab = QtGui.QWidget()
        self.y2Tab.setObjectName("y2Tab")

        self.gridlayout5 = QtGui.QGridLayout(self.y2Tab)
        self.gridlayout5.setObjectName("gridlayout5")

        self.y2AutoGroupBox = QtGui.QGroupBox(self.y2Tab)
        self.y2AutoGroupBox.setCheckable(True)
        self.y2AutoGroupBox.setChecked(False)
        self.y2AutoGroupBox.setObjectName("y2AutoGroupBox")

        self.gridlayout6 = QtGui.QGridLayout(self.y2AutoGroupBox)
        self.gridlayout6.setObjectName("gridlayout6")

        self.y2LabelMin = QtGui.QLabel(self.y2AutoGroupBox)
        self.y2LabelMin.setObjectName("y2LabelMin")
        self.gridlayout6.addWidget(self.y2LabelMin,0,0,1,1)

        self.y2EditMin = QtGui.QLineEdit(self.y2AutoGroupBox)
        self.y2EditMin.setObjectName("y2EditMin")
        self.gridlayout6.addWidget(self.y2EditMin,0,1,1,1)

        self.y2LabelMax = QtGui.QLabel(self.y2AutoGroupBox)
        self.y2LabelMax.setObjectName("y2LabelMax")
        self.gridlayout6.addWidget(self.y2LabelMax,1,0,1,1)

        self.y2EditMax = QtGui.QLineEdit(self.y2AutoGroupBox)
        self.y2EditMax.setObjectName("y2EditMax")
        self.gridlayout6.addWidget(self.y2EditMax,1,1,1,1)
        self.gridlayout5.addWidget(self.y2AutoGroupBox,0,0,1,2)

        self.y2ModeLabel = QtGui.QLabel(self.y2Tab)
        self.y2ModeLabel.setObjectName("y2ModeLabel")
        self.gridlayout5.addWidget(self.y2ModeLabel,1,0,1,1)

        self.y2ModeComboBox = QtGui.QComboBox(self.y2Tab)
        self.y2ModeComboBox.setObjectName("y2ModeComboBox")
        self.gridlayout5.addWidget(self.y2ModeComboBox,1,1,1,1)
        self.tabWidget.addTab(self.y2Tab,"")
        self.gridlayout.addWidget(self.tabWidget,1,1,2,1)

        self.hboxlayout = QtGui.QHBoxLayout()
        self.hboxlayout.setObjectName("hboxlayout")

        self.y1PeaksLabel = QtGui.QLabel(TaurusPlotConfigDialog)
        self.y1PeaksLabel.setObjectName("y1PeaksLabel")
        self.hboxlayout.addWidget(self.y1PeaksLabel)

        self.peaksComboBox = QtGui.QComboBox(TaurusPlotConfigDialog)
        self.peaksComboBox.setObjectName("peaksComboBox")
        self.hboxlayout.addWidget(self.peaksComboBox)
        self.gridlayout.addLayout(self.hboxlayout,1,2,1,1)

        self.buttonBox = QtGui.QDialogButtonBox(TaurusPlotConfigDialog)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred,QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.buttonBox.sizePolicy().hasHeightForWidth())
        self.buttonBox.setSizePolicy(sizePolicy)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Apply|QtGui.QDialogButtonBox.Close|QtGui.QDialogButtonBox.NoButton)
        self.buttonBox.setObjectName("buttonBox")
        self.gridlayout.addWidget(self.buttonBox,2,2,1,1)

        self.retranslateUi(TaurusPlotConfigDialog)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QObject.connect(self.xDynScaleCheckBox,QtCore.SIGNAL("toggled(bool)"),self.xLabelRange.setVisible)
        QtCore.QObject.connect(self.xDynScaleCheckBox,QtCore.SIGNAL("toggled(bool)"),self.xRangeCB.setVisible)
        QtCore.QObject.connect(self.xDynScaleCheckBox,QtCore.SIGNAL("toggled(bool)"),self.xAutoGroupBox.setHidden)
        QtCore.QMetaObject.connectSlotsByName(TaurusPlotConfigDialog)

    def retranslateUi(self, TaurusPlotConfigDialog):
        TaurusPlotConfigDialog.setWindowTitle(QtGui.QApplication.translate("TaurusPlotConfigDialog", "Configure plot", None, QtGui.QApplication.UnicodeUTF8))
        self.curveAppearanceGB.setTitle(QtGui.QApplication.translate("TaurusPlotConfigDialog", "Curves Appearance", None, QtGui.QApplication.UnicodeUTF8))
        self.xGroupBox.setTitle(QtGui.QApplication.translate("TaurusPlotConfigDialog", "X Axis", None, QtGui.QApplication.UnicodeUTF8))
        self.xAutoGroupBox.setToolTip(QtGui.QApplication.translate("TaurusPlotConfigDialog", "Customize scale range (this disables autoscaling)", None, QtGui.QApplication.UnicodeUTF8))
        self.xAutoGroupBox.setTitle(QtGui.QApplication.translate("TaurusPlotConfigDialog", "Custom scale", None, QtGui.QApplication.UnicodeUTF8))
        self.xLabelMin.setText(QtGui.QApplication.translate("TaurusPlotConfigDialog", "Min.:", None, QtGui.QApplication.UnicodeUTF8))
        self.xLabelMax.setText(QtGui.QApplication.translate("TaurusPlotConfigDialog", "Max:", None, QtGui.QApplication.UnicodeUTF8))
        self.xLabelRange.setText(QtGui.QApplication.translate("TaurusPlotConfigDialog", "Range", None, QtGui.QApplication.UnicodeUTF8))
        self.xModeLabel.setText(QtGui.QApplication.translate("TaurusPlotConfigDialog", "Mode", None, QtGui.QApplication.UnicodeUTF8))
        self.xDynScaleCheckBox.setToolTip(QtGui.QApplication.translate("TaurusPlotConfigDialog", "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
        "p, li { white-space: pre-wrap; }\n"
        "</style></head><body style=\" font-family:\'Sans Serif\'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
        "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:9pt; font-style:italic;\">AKA</span><span style=\" font-size:9pt;\">, \"Trend Mode\":</span></p>\n"
        "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:9pt;\">(If checked, the X scale range will be kept constant but its offset will move to guarantee that the newest point is shown.)</p>\n"
        "<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:9pt;\"></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.xDynScaleCheckBox.setText(QtGui.QApplication.translate("TaurusPlotConfigDialog", "Fixed-range scale", None, QtGui.QApplication.UnicodeUTF8))
        self.y1AutoGroupBox.setToolTip(QtGui.QApplication.translate("TaurusPlotConfigDialog", "Customize scale range (this disables autoscaling)", None, QtGui.QApplication.UnicodeUTF8))
        self.y1AutoGroupBox.setTitle(QtGui.QApplication.translate("TaurusPlotConfigDialog", "Custom scale", None, QtGui.QApplication.UnicodeUTF8))
        self.y1LabelMin.setText(QtGui.QApplication.translate("TaurusPlotConfigDialog", "Min.:", None, QtGui.QApplication.UnicodeUTF8))
        self.y1LabelMax.setText(QtGui.QApplication.translate("TaurusPlotConfigDialog", "Max:", None, QtGui.QApplication.UnicodeUTF8))
        self.y1ModeLabel.setText(QtGui.QApplication.translate("TaurusPlotConfigDialog", "Mode", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.y1Tab), QtGui.QApplication.translate("TaurusPlotConfigDialog", "Y1 Axis", None, QtGui.QApplication.UnicodeUTF8))
        self.y2AutoGroupBox.setToolTip(QtGui.QApplication.translate("TaurusPlotConfigDialog", "Customize scale range (this disables autoscaling)", None, QtGui.QApplication.UnicodeUTF8))
        self.y2AutoGroupBox.setTitle(QtGui.QApplication.translate("TaurusPlotConfigDialog", "Custom scale", None, QtGui.QApplication.UnicodeUTF8))
        self.y2LabelMin.setText(QtGui.QApplication.translate("TaurusPlotConfigDialog", "Min.:", None, QtGui.QApplication.UnicodeUTF8))
        self.y2LabelMax.setText(QtGui.QApplication.translate("TaurusPlotConfigDialog", "Max:", None, QtGui.QApplication.UnicodeUTF8))
        self.y2ModeLabel.setText(QtGui.QApplication.translate("TaurusPlotConfigDialog", "Mode", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.y2Tab), QtGui.QApplication.translate("TaurusPlotConfigDialog", "Y2 Axis", None, QtGui.QApplication.UnicodeUTF8))
        self.y1PeaksLabel.setText(QtGui.QApplication.translate("TaurusPlotConfigDialog", "Peak Markers", None, QtGui.QApplication.UnicodeUTF8))

