# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'SendMailForm.ui'
#
# Created: Tue May 22 17:06:40 2012
#      by: PyQt4 UI code generator 4.4.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_SendMailForm(object):
    def setupUi(self, SendMailForm):
        SendMailForm.setObjectName("SendMailForm")
        SendMailForm.resize(400, 300)
        self.mainLayout = QtGui.QGridLayout(SendMailForm)
        self.mainLayout.setObjectName("mainLayout")
        self.labelFrom = QtGui.QLabel(SendMailForm)
        self.labelFrom.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.labelFrom.setObjectName("labelFrom")
        self.mainLayout.addWidget(self.labelFrom, 0, 0, 1, 1)
        self.lineEditFrom = QtGui.QLineEdit(SendMailForm)
        self.lineEditFrom.setObjectName("lineEditFrom")
        self.mainLayout.addWidget(self.lineEditFrom, 0, 1, 1, 1)
        self.labelTo = QtGui.QLabel(SendMailForm)
        self.labelTo.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.labelTo.setObjectName("labelTo")
        self.mainLayout.addWidget(self.labelTo, 1, 0, 1, 1)
        self.lineEditTo = QtGui.QLineEdit(SendMailForm)
        self.lineEditTo.setObjectName("lineEditTo")
        self.mainLayout.addWidget(self.lineEditTo, 1, 1, 1, 1)
        self.labelSubject = QtGui.QLabel(SendMailForm)
        self.labelSubject.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.labelSubject.setObjectName("labelSubject")
        self.mainLayout.addWidget(self.labelSubject, 2, 0, 1, 1)
        self.lineEditSubject = QtGui.QLineEdit(SendMailForm)
        self.lineEditSubject.setObjectName("lineEditSubject")
        self.mainLayout.addWidget(self.lineEditSubject, 2, 1, 1, 1)
        self.plainTextEditText = QtGui.QPlainTextEdit(SendMailForm)
        self.plainTextEditText.setObjectName("plainTextEditText")
        self.mainLayout.addWidget(self.plainTextEditText, 3, 0, 1, 2)
        self.buttonBox = QtGui.QDialogButtonBox(SendMailForm)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.mainLayout.addWidget(self.buttonBox, 4, 0, 1, 2)

        self.retranslateUi(SendMailForm)
        QtCore.QMetaObject.connectSlotsByName(SendMailForm)

    def retranslateUi(self, SendMailForm):
        SendMailForm.setWindowTitle(QtGui.QApplication.translate("SendMailForm", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.labelFrom.setText(QtGui.QApplication.translate("SendMailForm", "From:", None, QtGui.QApplication.UnicodeUTF8))
        self.labelTo.setText(QtGui.QApplication.translate("SendMailForm", "To:", None, QtGui.QApplication.UnicodeUTF8))
        self.labelSubject.setText(QtGui.QApplication.translate("SendMailForm", "Subject:", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    SendMailForm = QtGui.QWidget()
    ui = Ui_SendMailForm()
    ui.setupUi(SendMailForm)
    SendMailForm.show()
    sys.exit(app.exec_())

