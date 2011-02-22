# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/cpascual/src/svn/taurus/widget/dialog/ui/AttributeChooser.ui'
#
# Created: Tue Feb  2 11:34:16 2010
#      by: PyQt4 UI code generator 4.3.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_AttrCh(object):
    def setupUi(self, AttrCh):
        AttrCh.setObjectName("AttrCh")
        AttrCh.resize(QtCore.QSize(QtCore.QRect(0,0,371,469).size()).expandedTo(AttrCh.minimumSizeHint()))
        AttrCh.setMinimumSize(QtCore.QSize(0,0))

        self.vboxlayout = QtGui.QVBoxLayout(AttrCh)
        self.vboxlayout.setObjectName("vboxlayout")

        self.hboxlayout = QtGui.QHBoxLayout()
        self.hboxlayout.setObjectName("hboxlayout")

        self.label_1 = QtGui.QLabel(AttrCh)
        self.label_1.setMinimumSize(QtCore.QSize(54,20))
        self.label_1.setObjectName("label_1")
        self.hboxlayout.addWidget(self.label_1)

        self.lineEdit = QtGui.QLineEdit(AttrCh)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lineEdit.sizePolicy().hasHeightForWidth())
        self.lineEdit.setSizePolicy(sizePolicy)
        self.lineEdit.setMinimumSize(QtCore.QSize(0,0))
        self.lineEdit.setObjectName("lineEdit")
        self.hboxlayout.addWidget(self.lineEdit)
        self.vboxlayout.addLayout(self.hboxlayout)

        self.hboxlayout1 = QtGui.QHBoxLayout()
        self.hboxlayout1.setObjectName("hboxlayout1")

        self.vboxlayout1 = QtGui.QVBoxLayout()
        self.vboxlayout1.setObjectName("vboxlayout1")

        self.label_2 = QtGui.QLabel(AttrCh)
        self.label_2.setObjectName("label_2")
        self.vboxlayout1.addWidget(self.label_2)

        self.devList = QtGui.QListWidget(AttrCh)
        self.devList.setMinimumSize(QtCore.QSize(0,0))
        self.devList.setObjectName("devList")
        self.vboxlayout1.addWidget(self.devList)
        self.hboxlayout1.addLayout(self.vboxlayout1)

        self.vboxlayout2 = QtGui.QVBoxLayout()
        self.vboxlayout2.setObjectName("vboxlayout2")

        self.label_3 = QtGui.QLabel(AttrCh)
        self.label_3.setObjectName("label_3")
        self.vboxlayout2.addWidget(self.label_3)

        self.attrList = QtGui.QListWidget(AttrCh)
        self.attrList.setMinimumSize(QtCore.QSize(0,0))
        self.attrList.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.attrList.setObjectName("attrList")
        self.vboxlayout2.addWidget(self.attrList)
        self.hboxlayout1.addLayout(self.vboxlayout2)
        self.vboxlayout.addLayout(self.hboxlayout1)

        self.hboxlayout2 = QtGui.QHBoxLayout()
        self.hboxlayout2.setObjectName("hboxlayout2")

        spacerItem = QtGui.QSpacerItem(51,23,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout2.addItem(spacerItem)

        self.addButton = QtGui.QToolButton(AttrCh)
        self.addButton.setObjectName("addButton")
        self.hboxlayout2.addWidget(self.addButton)

        self.removeButton = QtGui.QToolButton(AttrCh)
        self.removeButton.setObjectName("removeButton")
        self.hboxlayout2.addWidget(self.removeButton)

        self.cancelButton = QtGui.QToolButton(AttrCh)
        self.cancelButton.setObjectName("cancelButton")
        self.hboxlayout2.addWidget(self.cancelButton)
        self.vboxlayout.addLayout(self.hboxlayout2)

        self.vboxlayout3 = QtGui.QVBoxLayout()
        self.vboxlayout3.setObjectName("vboxlayout3")

        self.label_4 = QtGui.QLabel(AttrCh)
        self.label_4.setMinimumSize(QtCore.QSize(0,0))
        self.label_4.setObjectName("label_4")
        self.vboxlayout3.addWidget(self.label_4)

        self.final_List = QtGui.QListWidget(AttrCh)
        self.final_List.setMinimumSize(QtCore.QSize(0,0))
        self.final_List.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.final_List.setObjectName("final_List")
        self.vboxlayout3.addWidget(self.final_List)

        self.updateButton = QtGui.QPushButton(AttrCh)
        self.updateButton.setMinimumSize(QtCore.QSize(75,41))
        self.updateButton.setObjectName("updateButton")
        self.vboxlayout3.addWidget(self.updateButton)
        self.vboxlayout.addLayout(self.vboxlayout3)

        self.retranslateUi(AttrCh)
        QtCore.QMetaObject.connectSlotsByName(AttrCh)

    def retranslateUi(self, AttrCh):
        AttrCh.setWindowTitle(QtGui.QApplication.translate("AttrCh", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.label_1.setWhatsThis(QtGui.QApplication.translate("AttrCh", "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
        "p, li { white-space: pre-wrap; }\n"
        "</style></head><body style=\" font-family:\'Sans Serif\'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
        "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Enter here the path for search a device.</p>\n"
        "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Format:</p>\n"
        "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Domain/Family/Member</p>\n"
        "<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.label_1.setText(QtGui.QApplication.translate("AttrCh", "Enter a path:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setWhatsThis(QtGui.QApplication.translate("AttrCh", "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
        "p, li { white-space: pre-wrap; }\n"
        "</style></head><body style=\" font-family:\'Sans Serif\'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
        "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">List of Devices.</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("AttrCh", "Devices:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setWhatsThis(QtGui.QApplication.translate("AttrCh", "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
        "p, li { white-space: pre-wrap; }\n"
        "</style></head><body style=\" font-family:\'Sans Serif\'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
        "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">List of the device attributes.</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("AttrCh", "Attributes:", None, QtGui.QApplication.UnicodeUTF8))
        self.addButton.setToolTip(QtGui.QApplication.translate("AttrCh", "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
        "p, li { white-space: pre-wrap; }\n"
        "</style></head><body style=\" font-family:\'Sans Serif\'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
        "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Add selected attribute(s) from the <span style=\" font-style:italic;\">Attribute List</span> to the <span style=\" font-style:italic;\">Chosen Attributes</span></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.addButton.setText(QtGui.QApplication.translate("AttrCh", "Add", None, QtGui.QApplication.UnicodeUTF8))
        self.removeButton.setToolTip(QtGui.QApplication.translate("AttrCh", "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
        "p, li { white-space: pre-wrap; }\n"
        "</style></head><body style=\" font-family:\'Sans Serif\'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
        "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Remove selected attribute(s) from the <span style=\" font-style:italic;\">Chosen Attributes</span></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.removeButton.setText(QtGui.QApplication.translate("AttrCh", "Remove", None, QtGui.QApplication.UnicodeUTF8))
        self.cancelButton.setToolTip(QtGui.QApplication.translate("AttrCh", "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
        "p, li { white-space: pre-wrap; }\n"
        "</style></head><body style=\" font-family:\'Sans Serif\'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
        "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Clear the <span style=\" font-style:italic;\">Chosen Attributes</span> list</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.cancelButton.setText(QtGui.QApplication.translate("AttrCh", "Clear", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setWhatsThis(QtGui.QApplication.translate("AttrCh", "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
        "p, li { white-space: pre-wrap; }\n"
        "</style></head><body style=\" font-family:\'Sans Serif\'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
        "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">List of all the attributes selected.</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("AttrCh", "Chosen attributes:", None, QtGui.QApplication.UnicodeUTF8))
        self.updateButton.setToolTip(QtGui.QApplication.translate("AttrCh", "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
        "p, li { white-space: pre-wrap; }\n"
        "</style></head><body style=\" font-family:\'Sans Serif\'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
        "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Update the attribute(s)</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.updateButton.setWhatsThis(QtGui.QApplication.translate("AttrCh", "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
        "p, li { white-space: pre-wrap; }\n"
        "</style></head><body style=\" font-family:\'Sans Serif\'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
        "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Update with the choosen attributes.</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.updateButton.setText(QtGui.QApplication.translate("AttrCh", "Apply", None, QtGui.QApplication.UnicodeUTF8))

