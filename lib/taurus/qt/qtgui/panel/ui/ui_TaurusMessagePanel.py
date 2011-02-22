# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'TaurusMessagePanel.ui'
#
# Created: Mon Jan 24 11:40:48 2011
#      by: PyQt4 UI code generator 4.7.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_TaurusMessagePanel(object):
    def setupUi(self, TaurusMessagePanel):
        TaurusMessagePanel.setObjectName("TaurusMessagePanel")
        TaurusMessagePanel.resize(548, 586)
        self.gridLayout = QtGui.QGridLayout(TaurusMessagePanel)
        self.gridLayout.setObjectName("gridLayout")
        self.iconLabel = QtGui.QLabel(TaurusMessagePanel)
        self.iconLabel.setObjectName("iconLabel")
        self.gridLayout.addWidget(self.iconLabel, 0, 0, 1, 1)
        self.textLabel = QtGui.QLabel(TaurusMessagePanel)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.textLabel.sizePolicy().hasHeightForWidth())
        self.textLabel.setSizePolicy(sizePolicy)
        self.textLabel.setObjectName("textLabel")
        self.gridLayout.addWidget(self.textLabel, 0, 1, 1, 2)
        self.detailsWidget = QtGui.QWidget(TaurusMessagePanel)
        self.detailsWidget.setObjectName("detailsWidget")
        self.verticalLayout = QtGui.QVBoxLayout(self.detailsWidget)
        self.verticalLayout.setSpacing(2)
        self.verticalLayout.setMargin(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.detailsTabWidget = QtGui.QTabWidget(self.detailsWidget)
        self.detailsTabWidget.setMinimumSize(QtCore.QSize(512, 512))
        self.detailsTabWidget.setObjectName("detailsTabWidget")
        self.tabDetails = QtGui.QWidget()
        self.tabDetails.setObjectName("tabDetails")
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.tabDetails)
        self.verticalLayout_2.setMargin(2)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.detailsTextEdit = QtGui.QTextEdit(self.tabDetails)
        self.detailsTextEdit.setMinimumSize(QtCore.QSize(512, 512))
        self.detailsTextEdit.setReadOnly(True)
        self.detailsTextEdit.setObjectName("detailsTextEdit")
        self.verticalLayout_2.addWidget(self.detailsTextEdit)
        self.detailsTabWidget.addTab(self.tabDetails, "")
        self.tabOrigin = QtGui.QWidget()
        self.tabOrigin.setObjectName("tabOrigin")
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.tabOrigin)
        self.verticalLayout_3.setMargin(2)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.originTextEdit = QtGui.QTextEdit(self.tabOrigin)
        self.originTextEdit.setMinimumSize(QtCore.QSize(512, 256))
        self.originTextEdit.setReadOnly(True)
        self.originTextEdit.setObjectName("originTextEdit")
        self.verticalLayout_3.addWidget(self.originTextEdit)
        self.detailsTabWidget.addTab(self.tabOrigin, "")
        self.verticalLayout.addWidget(self.detailsTabWidget)
        self.gridLayout.addWidget(self.detailsWidget, 2, 0, 1, 3)
        self.buttonPanelWidget = QtGui.QWidget(TaurusMessagePanel)
        self.buttonPanelWidget.setObjectName("buttonPanelWidget")
        self.horizontalLayout = QtGui.QHBoxLayout(self.buttonPanelWidget)
        self.horizontalLayout.setMargin(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.showDetailsButton = QtGui.QPushButton(self.buttonPanelWidget)
        self.showDetailsButton.setCheckable(True)
        self.showDetailsButton.setObjectName("showDetailsButton")
        self.horizontalLayout.addWidget(self.showDetailsButton)
        self.copyClipboardButton = QtGui.QPushButton(self.buttonPanelWidget)
        self.copyClipboardButton.setObjectName("copyClipboardButton")
        self.horizontalLayout.addWidget(self.copyClipboardButton)
        self.buttonBox = QtGui.QDialogButtonBox(self.buttonPanelWidget)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.horizontalLayout.addWidget(self.buttonBox)
        self.gridLayout.addWidget(self.buttonPanelWidget, 1, 0, 1, 3)

        self.retranslateUi(TaurusMessagePanel)
        self.detailsTabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(TaurusMessagePanel)

    def retranslateUi(self, TaurusMessagePanel):
        TaurusMessagePanel.setWindowTitle(QtGui.QApplication.translate("TaurusMessagePanel", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.iconLabel.setText(QtGui.QApplication.translate("TaurusMessagePanel", "iconLabel", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel.setText(QtGui.QApplication.translate("TaurusMessagePanel", "textLabel", None, QtGui.QApplication.UnicodeUTF8))
        self.detailsTabWidget.setTabText(self.detailsTabWidget.indexOf(self.tabDetails), QtGui.QApplication.translate("TaurusMessagePanel", "Details", None, QtGui.QApplication.UnicodeUTF8))
        self.detailsTabWidget.setTabText(self.detailsTabWidget.indexOf(self.tabOrigin), QtGui.QApplication.translate("TaurusMessagePanel", "Origin", None, QtGui.QApplication.UnicodeUTF8))
        self.showDetailsButton.setText(QtGui.QApplication.translate("TaurusMessagePanel", "Show Details...", None, QtGui.QApplication.UnicodeUTF8))
        self.copyClipboardButton.setText(QtGui.QApplication.translate("TaurusMessagePanel", "Copy to Clipboard", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    TaurusMessagePanel = QtGui.QWidget()
    ui = Ui_TaurusMessagePanel()
    ui.setupUi(TaurusMessagePanel)
    TaurusMessagePanel.show()
    sys.exit(app.exec_())

