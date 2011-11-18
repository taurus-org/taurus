# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'TaurusMessagePanel.ui'
#
# Created: Fri Nov 18 09:36:31 2011
#      by: PyQt4 UI code generator 4.8.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_TaurusMessagePanel(object):
    def setupUi(self, TaurusMessagePanel):
        TaurusMessagePanel.setObjectName(_fromUtf8("TaurusMessagePanel"))
        TaurusMessagePanel.resize(548, 614)
        self.gridLayout = QtGui.QGridLayout(TaurusMessagePanel)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.detailsWidget = QtGui.QWidget(TaurusMessagePanel)
        self.detailsWidget.setObjectName(_fromUtf8("detailsWidget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.detailsWidget)
        self.verticalLayout.setSpacing(2)
        self.verticalLayout.setMargin(0)
        self.verticalLayout.setMargin(0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.detailsTabWidget = QtGui.QTabWidget(self.detailsWidget)
        self.detailsTabWidget.setMinimumSize(QtCore.QSize(512, 512))
        self.detailsTabWidget.setObjectName(_fromUtf8("detailsTabWidget"))
        self.tabDetails = QtGui.QWidget()
        self.tabDetails.setObjectName(_fromUtf8("tabDetails"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.tabDetails)
        self.verticalLayout_2.setMargin(2)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.detailsTextEdit = QtGui.QTextEdit(self.tabDetails)
        self.detailsTextEdit.setMinimumSize(QtCore.QSize(512, 512))
        self.detailsTextEdit.setReadOnly(True)
        self.detailsTextEdit.setObjectName(_fromUtf8("detailsTextEdit"))
        self.verticalLayout_2.addWidget(self.detailsTextEdit)
        self.detailsTabWidget.addTab(self.tabDetails, _fromUtf8(""))
        self.tabOrigin = QtGui.QWidget()
        self.tabOrigin.setObjectName(_fromUtf8("tabOrigin"))
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.tabOrigin)
        self.verticalLayout_3.setMargin(2)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.originTextEdit = QtGui.QTextEdit(self.tabOrigin)
        self.originTextEdit.setMinimumSize(QtCore.QSize(512, 256))
        self.originTextEdit.setReadOnly(True)
        self.originTextEdit.setObjectName(_fromUtf8("originTextEdit"))
        self.verticalLayout_3.addWidget(self.originTextEdit)
        self.detailsTabWidget.addTab(self.tabOrigin, _fromUtf8(""))
        self.verticalLayout.addWidget(self.detailsTabWidget)
        self.gridLayout.addWidget(self.detailsWidget, 4, 0, 1, 3)
        self.buttonPanelWidget = QtGui.QWidget(TaurusMessagePanel)
        self.buttonPanelWidget.setObjectName(_fromUtf8("buttonPanelWidget"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.buttonPanelWidget)
        self.horizontalLayout.setMargin(0)
        self.horizontalLayout.setMargin(0)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.showDetailsButton = QtGui.QPushButton(self.buttonPanelWidget)
        self.showDetailsButton.setCheckable(True)
        self.showDetailsButton.setObjectName(_fromUtf8("showDetailsButton"))
        self.horizontalLayout.addWidget(self.showDetailsButton)
        self.copyClipboardButton = QtGui.QPushButton(self.buttonPanelWidget)
        self.copyClipboardButton.setObjectName(_fromUtf8("copyClipboardButton"))
        self.horizontalLayout.addWidget(self.copyClipboardButton)
        self.buttonBox = QtGui.QDialogButtonBox(self.buttonPanelWidget)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.horizontalLayout.addWidget(self.buttonBox)
        self.gridLayout.addWidget(self.buttonPanelWidget, 3, 0, 1, 3)
        self.checkBox = QtGui.QCheckBox(TaurusMessagePanel)
        self.checkBox.setObjectName(_fromUtf8("checkBox"))
        self.gridLayout.addWidget(self.checkBox, 5, 0, 1, 1)
        self.iconTextLayout = QtGui.QHBoxLayout()
        self.iconTextLayout.setObjectName(_fromUtf8("iconTextLayout"))
        self.iconLabel = QtGui.QLabel(TaurusMessagePanel)
        self.iconLabel.setObjectName(_fromUtf8("iconLabel"))
        self.iconTextLayout.addWidget(self.iconLabel)
        self.textLabel = QtGui.QLabel(TaurusMessagePanel)
        self.textLabel.setObjectName(_fromUtf8("textLabel"))
        self.iconTextLayout.addWidget(self.textLabel)
        self.iconTextLayout.setStretch(1, 1)
        self.gridLayout.addLayout(self.iconTextLayout, 1, 0, 2, 3)

        self.retranslateUi(TaurusMessagePanel)
        self.detailsTabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(TaurusMessagePanel)

    def retranslateUi(self, TaurusMessagePanel):
        TaurusMessagePanel.setWindowTitle(QtGui.QApplication.translate("TaurusMessagePanel", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.detailsTabWidget.setTabText(self.detailsTabWidget.indexOf(self.tabDetails), QtGui.QApplication.translate("TaurusMessagePanel", "Details", None, QtGui.QApplication.UnicodeUTF8))
        self.detailsTabWidget.setTabText(self.detailsTabWidget.indexOf(self.tabOrigin), QtGui.QApplication.translate("TaurusMessagePanel", "Origin", None, QtGui.QApplication.UnicodeUTF8))
        self.showDetailsButton.setText(QtGui.QApplication.translate("TaurusMessagePanel", "Show Details...", None, QtGui.QApplication.UnicodeUTF8))
        self.copyClipboardButton.setText(QtGui.QApplication.translate("TaurusMessagePanel", "Copy to Clipboard", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox.setText(QtGui.QApplication.translate("TaurusMessagePanel", "Don\'t show this message again", None, QtGui.QApplication.UnicodeUTF8))
        self.iconLabel.setText(QtGui.QApplication.translate("TaurusMessagePanel", "iconLabel", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel.setText(QtGui.QApplication.translate("TaurusMessagePanel", "textLabel", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    TaurusMessagePanel = QtGui.QWidget()
    ui = Ui_TaurusMessagePanel()
    ui.setupUi(TaurusMessagePanel)
    TaurusMessagePanel.show()
    sys.exit(app.exec_())

