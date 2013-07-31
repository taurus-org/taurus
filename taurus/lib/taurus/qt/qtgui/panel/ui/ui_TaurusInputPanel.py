# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'TaurusInputPanel.ui'
#
# Created: Mon Jul  9 14:25:29 2012
#      by: PyQt4 UI code generator 4.8.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_TaurusInputPanel(object):
    def setupUi(self, TaurusInputPanel):
        TaurusInputPanel.setObjectName(_fromUtf8("TaurusInputPanel"))
        TaurusInputPanel.resize(549, 174)
        self.gridLayout = QtGui.QGridLayout(TaurusInputPanel)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.buttonPanelWidget = QtGui.QWidget(TaurusInputPanel)
        self.buttonPanelWidget.setObjectName(_fromUtf8("buttonPanelWidget"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.buttonPanelWidget)
        self.horizontalLayout.setMargin(0)
        self.horizontalLayout.setMargin(0)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.buttonBox = QtGui.QDialogButtonBox(self.buttonPanelWidget)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.horizontalLayout.addWidget(self.buttonBox)
        self.horizontalLayout.setStretch(0, 1)
        self.gridLayout.addWidget(self.buttonPanelWidget, 4, 0, 1, 2)
        self.iconTextLayout = QtGui.QHBoxLayout()
        self.iconTextLayout.setObjectName(_fromUtf8("iconTextLayout"))
        self.iconLabel = QtGui.QLabel(TaurusInputPanel)
        self.iconLabel.setObjectName(_fromUtf8("iconLabel"))
        self.iconTextLayout.addWidget(self.iconLabel)
        self.textLabel = QtGui.QLabel(TaurusInputPanel)
        self.textLabel.setObjectName(_fromUtf8("textLabel"))
        self.iconTextLayout.addWidget(self.textLabel)
        self.iconTextLayout.setStretch(1, 1)
        self.gridLayout.addLayout(self.iconTextLayout, 1, 0, 2, 2)
        self.inputPanel = QtGui.QWidget(TaurusInputPanel)
        self.inputPanel.setObjectName(_fromUtf8("inputPanel"))
        self.gridLayout.addWidget(self.inputPanel, 3, 0, 1, 2)
        self.gridLayout.setRowStretch(3, 1)

        self.retranslateUi(TaurusInputPanel)
        QtCore.QMetaObject.connectSlotsByName(TaurusInputPanel)

    def retranslateUi(self, TaurusInputPanel):
        TaurusInputPanel.setWindowTitle(QtGui.QApplication.translate("TaurusInputPanel", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.iconLabel.setText(QtGui.QApplication.translate("TaurusInputPanel", "iconLabel", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel.setText(QtGui.QApplication.translate("TaurusInputPanel", "textLabel", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    TaurusInputPanel = QtGui.QWidget()
    ui = Ui_TaurusInputPanel()
    ui.setupUi(TaurusInputPanel)
    TaurusInputPanel.show()
    sys.exit(app.exec_())

