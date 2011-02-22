# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/TauPopupMenuEditorDialog.ui'
#
# Created: Thu May 15 17:36:11 2008
#      by: PyQt4 UI code generator 4.3.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_TauPopupMenuEditorDialog(object):
    def setupUi(self, TauPopupMenuEditorDialog):
        TauPopupMenuEditorDialog.setObjectName("TauPopupMenuEditorDialog")
        TauPopupMenuEditorDialog.resize(QtCore.QSize(QtCore.QRect(0,0,693,321).size()).expandedTo(TauPopupMenuEditorDialog.minimumSizeHint()))

        self.gridlayout = QtGui.QGridLayout(TauPopupMenuEditorDialog)
        self.gridlayout.setObjectName("gridlayout")

        self.itemsBox = QtGui.QGroupBox(TauPopupMenuEditorDialog)
        self.itemsBox.setObjectName("itemsBox")

        self.gridlayout1 = QtGui.QGridLayout(self.itemsBox)
        self.gridlayout1.setObjectName("gridlayout1")

        self.treeWidget = QtGui.QTreeWidget(self.itemsBox)
        self.treeWidget.setFocusPolicy(QtCore.Qt.TabFocus)
        self.treeWidget.setObjectName("treeWidget")
        self.gridlayout1.addWidget(self.treeWidget,0,0,1,1)

        self.hboxlayout = QtGui.QHBoxLayout()
        self.hboxlayout.setObjectName("hboxlayout")

        self.newItemButton = QtGui.QToolButton(self.itemsBox)
        self.newItemButton.setObjectName("newItemButton")
        self.hboxlayout.addWidget(self.newItemButton)

        self.newSubItemButton = QtGui.QToolButton(self.itemsBox)
        self.newSubItemButton.setObjectName("newSubItemButton")
        self.hboxlayout.addWidget(self.newSubItemButton)

        self.deleteItemButton = QtGui.QToolButton(self.itemsBox)
        self.deleteItemButton.setObjectName("deleteItemButton")
        self.hboxlayout.addWidget(self.deleteItemButton)

        spacerItem = QtGui.QSpacerItem(28,23,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout.addItem(spacerItem)

        self.moveItemLeftButton = QtGui.QToolButton(self.itemsBox)
        self.moveItemLeftButton.setObjectName("moveItemLeftButton")
        self.hboxlayout.addWidget(self.moveItemLeftButton)

        self.moveItemRightButton = QtGui.QToolButton(self.itemsBox)
        self.moveItemRightButton.setObjectName("moveItemRightButton")
        self.hboxlayout.addWidget(self.moveItemRightButton)

        self.moveItemUpButton = QtGui.QToolButton(self.itemsBox)
        self.moveItemUpButton.setObjectName("moveItemUpButton")
        self.hboxlayout.addWidget(self.moveItemUpButton)

        self.moveItemDownButton = QtGui.QToolButton(self.itemsBox)
        self.moveItemDownButton.setObjectName("moveItemDownButton")
        self.hboxlayout.addWidget(self.moveItemDownButton)
        self.gridlayout1.addLayout(self.hboxlayout,1,0,1,1)
        self.gridlayout.addWidget(self.itemsBox,0,0,1,1)

        self.buttonBox = QtGui.QDialogButtonBox(TauPopupMenuEditorDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.NoButton|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridlayout.addWidget(self.buttonBox,1,0,1,2)

        self.groupBox = QtGui.QGroupBox(TauPopupMenuEditorDialog)
        self.groupBox.setObjectName("groupBox")
        self.gridlayout.addWidget(self.groupBox,0,1,1,1)

        self.retranslateUi(TauPopupMenuEditorDialog)
        QtCore.QObject.connect(self.buttonBox,QtCore.SIGNAL("accepted()"),TauPopupMenuEditorDialog.accept)
        QtCore.QObject.connect(self.buttonBox,QtCore.SIGNAL("rejected()"),TauPopupMenuEditorDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(TauPopupMenuEditorDialog)
        TauPopupMenuEditorDialog.setTabOrder(self.treeWidget,self.newItemButton)
        TauPopupMenuEditorDialog.setTabOrder(self.newItemButton,self.newSubItemButton)
        TauPopupMenuEditorDialog.setTabOrder(self.newSubItemButton,self.deleteItemButton)
        TauPopupMenuEditorDialog.setTabOrder(self.deleteItemButton,self.moveItemLeftButton)
        TauPopupMenuEditorDialog.setTabOrder(self.moveItemLeftButton,self.moveItemRightButton)
        TauPopupMenuEditorDialog.setTabOrder(self.moveItemRightButton,self.moveItemUpButton)
        TauPopupMenuEditorDialog.setTabOrder(self.moveItemUpButton,self.moveItemDownButton)

    def retranslateUi(self, TauPopupMenuEditorDialog):
        TauPopupMenuEditorDialog.setWindowTitle(QtGui.QApplication.translate("TauPopupMenuEditorDialog", "Tau Popup Menu Editor", None, QtGui.QApplication.UnicodeUTF8))
        self.itemsBox.setTitle(QtGui.QApplication.translate("TauPopupMenuEditorDialog", "Popup menu editor", None, QtGui.QApplication.UnicodeUTF8))
        self.treeWidget.setToolTip(QtGui.QApplication.translate("TauPopupMenuEditorDialog", "Tree Items", None, QtGui.QApplication.UnicodeUTF8))
        self.treeWidget.headerItem().setText(0,QtGui.QApplication.translate("TauPopupMenuEditorDialog", "1", None, QtGui.QApplication.UnicodeUTF8))
        self.newItemButton.setToolTip(QtGui.QApplication.translate("TauPopupMenuEditorDialog", "New Item", None, QtGui.QApplication.UnicodeUTF8))
        self.newItemButton.setText(QtGui.QApplication.translate("TauPopupMenuEditorDialog", "&New", None, QtGui.QApplication.UnicodeUTF8))
        self.newSubItemButton.setToolTip(QtGui.QApplication.translate("TauPopupMenuEditorDialog", "New Subitem", None, QtGui.QApplication.UnicodeUTF8))
        self.newSubItemButton.setText(QtGui.QApplication.translate("TauPopupMenuEditorDialog", "New &Subitem", None, QtGui.QApplication.UnicodeUTF8))
        self.deleteItemButton.setToolTip(QtGui.QApplication.translate("TauPopupMenuEditorDialog", "Delete Item", None, QtGui.QApplication.UnicodeUTF8))
        self.deleteItemButton.setText(QtGui.QApplication.translate("TauPopupMenuEditorDialog", "&Delete", None, QtGui.QApplication.UnicodeUTF8))
        self.moveItemLeftButton.setToolTip(QtGui.QApplication.translate("TauPopupMenuEditorDialog", "Move Item Left (before Parent Item)", None, QtGui.QApplication.UnicodeUTF8))
        self.moveItemLeftButton.setText(QtGui.QApplication.translate("TauPopupMenuEditorDialog", "L", None, QtGui.QApplication.UnicodeUTF8))
        self.moveItemRightButton.setToolTip(QtGui.QApplication.translate("TauPopupMenuEditorDialog", "Move Item Right (as a First Subitem of the Next Sibling Item)", None, QtGui.QApplication.UnicodeUTF8))
        self.moveItemRightButton.setText(QtGui.QApplication.translate("TauPopupMenuEditorDialog", "R", None, QtGui.QApplication.UnicodeUTF8))
        self.moveItemUpButton.setToolTip(QtGui.QApplication.translate("TauPopupMenuEditorDialog", "Move Item Up", None, QtGui.QApplication.UnicodeUTF8))
        self.moveItemUpButton.setText(QtGui.QApplication.translate("TauPopupMenuEditorDialog", "U", None, QtGui.QApplication.UnicodeUTF8))
        self.moveItemDownButton.setToolTip(QtGui.QApplication.translate("TauPopupMenuEditorDialog", "Move Item Down", None, QtGui.QApplication.UnicodeUTF8))
        self.moveItemDownButton.setText(QtGui.QApplication.translate("TauPopupMenuEditorDialog", "D", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("TauPopupMenuEditorDialog", "Preview Area", None, QtGui.QApplication.UnicodeUTF8))



if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    TauPopupMenuEditorDialog = QtGui.QDialog()
    ui = Ui_TauPopupMenuEditorDialog()
    ui.setupUi(TauPopupMenuEditorDialog)
    TauPopupMenuEditorDialog.show()
    sys.exit(app.exec_())
