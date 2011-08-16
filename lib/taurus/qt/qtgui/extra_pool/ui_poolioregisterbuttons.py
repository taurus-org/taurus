# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/poolioregisterbuttons.ui'
#
# Created: Tue Aug 16 10:17:34 2011
#      by: PyQt4 UI code generator 4.4.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_PoolIORegisterButtons(object):
    def setupUi(self, PoolIORegisterButtons):
        PoolIORegisterButtons.setObjectName("PoolIORegisterButtons")
        PoolIORegisterButtons.resize(172, 52)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(PoolIORegisterButtons.sizePolicy().hasHeightForWidth())
        PoolIORegisterButtons.setSizePolicy(sizePolicy)
        self.gridLayout = QtGui.QGridLayout(PoolIORegisterButtons)
        self.gridLayout.setMargin(0)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName("gridLayout")
        self.lo_state_read = QtGui.QHBoxLayout()
        self.lo_state_read.setSpacing(0)
        self.lo_state_read.setSizeConstraint(QtGui.QLayout.SetMinimumSize)
        self.lo_state_read.setObjectName("lo_state_read")
        self.gridLayout.addLayout(self.lo_state_read, 0, 0, 1, 1)
        self.lo_buttons_write = QtGui.QHBoxLayout()
        self.lo_buttons_write.setSpacing(0)
        self.lo_buttons_write.setObjectName("lo_buttons_write")
        self.gridLayout.addLayout(self.lo_buttons_write, 1, 0, 1, 1)

        self.retranslateUi(PoolIORegisterButtons)
        QtCore.QMetaObject.connectSlotsByName(PoolIORegisterButtons)

    def retranslateUi(self, PoolIORegisterButtons):
        PoolIORegisterButtons.setWindowTitle(QtGui.QApplication.translate("PoolIORegisterButtons", "Form", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    PoolIORegisterButtons = QtGui.QWidget()
    ui = Ui_PoolIORegisterButtons()
    ui.setupUi(PoolIORegisterButtons)
    PoolIORegisterButtons.show()
    sys.exit(app.exec_())

