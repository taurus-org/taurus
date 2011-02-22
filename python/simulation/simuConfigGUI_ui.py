# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'simuConfigGUI.ui'
#
# Created: Thu Mar 20 15:24:09 2008
#      by: PyQt4 UI code generator 4.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_simuConfigDialog(object):
    def setupUi(self, simuConfigDialog):
        simuConfigDialog.setObjectName("simuConfigDialog")
        simuConfigDialog.resize(QtCore.QSize(QtCore.QRect(0,0,496,608).size()).expandedTo(simuConfigDialog.minimumSizeHint()))

        self.gridlayout = QtGui.QGridLayout(simuConfigDialog)
        self.gridlayout.setObjectName("gridlayout")

        self.buttonBox = QtGui.QDialogButtonBox(simuConfigDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Apply|QtGui.QDialogButtonBox.Close)
        self.buttonBox.setCenterButtons(False)
        self.buttonBox.setObjectName("buttonBox")
        self.gridlayout.addWidget(self.buttonBox,2,2,1,1)

        self.simuTabWidget = QtGui.QTabWidget(simuConfigDialog)
        self.simuTabWidget.setObjectName("simuTabWidget")

        self.simulators = QtGui.QWidget()
        self.simulators.setObjectName("simulators")

        self.vboxlayout = QtGui.QVBoxLayout(self.simulators)
        self.vboxlayout.setObjectName("vboxlayout")

        self.motorGroupBox = QtGui.QGroupBox(self.simulators)
        self.motorGroupBox.setObjectName("motorGroupBox")

        self.gridlayout1 = QtGui.QGridLayout(self.motorGroupBox)
        self.gridlayout1.setObjectName("gridlayout1")

        self.motorServerNamelabel = QtGui.QLabel(self.motorGroupBox)
        self.motorServerNamelabel.setObjectName("motorServerNamelabel")
        self.gridlayout1.addWidget(self.motorServerNamelabel,0,0,1,1)

        self.motorServerNameLineEdit = QtGui.QLineEdit(self.motorGroupBox)
        self.motorServerNameLineEdit.setEnabled(False)
        self.motorServerNameLineEdit.setObjectName("motorServerNameLineEdit")
        self.gridlayout1.addWidget(self.motorServerNameLineEdit,0,1,1,1)

        self.motorControllerNameLabel = QtGui.QLabel(self.motorGroupBox)
        self.motorControllerNameLabel.setObjectName("motorControllerNameLabel")
        self.gridlayout1.addWidget(self.motorControllerNameLabel,1,0,1,1)

        self.motorControllerNameLineEdit = QtGui.QLineEdit(self.motorGroupBox)
        self.motorControllerNameLineEdit.setObjectName("motorControllerNameLineEdit")
        self.gridlayout1.addWidget(self.motorControllerNameLineEdit,1,1,1,1)

        self.motorNumberLabel = QtGui.QLabel(self.motorGroupBox)
        self.motorNumberLabel.setObjectName("motorNumberLabel")
        self.gridlayout1.addWidget(self.motorNumberLabel,2,0,1,1)

        self.motorNumberSpinBox = QtGui.QSpinBox(self.motorGroupBox)
        self.motorNumberSpinBox.setProperty("value",QtCore.QVariant(4))
        self.motorNumberSpinBox.setObjectName("motorNumberSpinBox")
        self.gridlayout1.addWidget(self.motorNumberSpinBox,2,1,1,1)

        spacerItem = QtGui.QSpacerItem(20,40,QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Expanding)
        self.gridlayout1.addItem(spacerItem,3,1,1,1)
        self.vboxlayout.addWidget(self.motorGroupBox)

        self.counterGroupBox = QtGui.QGroupBox(self.simulators)
        self.counterGroupBox.setObjectName("counterGroupBox")

        self.gridlayout2 = QtGui.QGridLayout(self.counterGroupBox)
        self.gridlayout2.setObjectName("gridlayout2")

        self.counterServerNamelabel = QtGui.QLabel(self.counterGroupBox)
        self.counterServerNamelabel.setObjectName("counterServerNamelabel")
        self.gridlayout2.addWidget(self.counterServerNamelabel,0,0,1,2)

        self.counterServerNameLineEdit = QtGui.QLineEdit(self.counterGroupBox)
        self.counterServerNameLineEdit.setEnabled(False)
        self.counterServerNameLineEdit.setObjectName("counterServerNameLineEdit")
        self.gridlayout2.addWidget(self.counterServerNameLineEdit,0,2,1,1)

        self.counterControllerNameLabel = QtGui.QLabel(self.counterGroupBox)
        self.counterControllerNameLabel.setObjectName("counterControllerNameLabel")
        self.gridlayout2.addWidget(self.counterControllerNameLabel,1,0,1,1)

        self.counterControllerNameLineEdit = QtGui.QLineEdit(self.counterGroupBox)
        self.counterControllerNameLineEdit.setObjectName("counterControllerNameLineEdit")
        self.gridlayout2.addWidget(self.counterControllerNameLineEdit,1,2,1,1)

        self.counterNumberLabel = QtGui.QLabel(self.counterGroupBox)
        self.counterNumberLabel.setObjectName("counterNumberLabel")
        self.gridlayout2.addWidget(self.counterNumberLabel,2,0,1,1)

        self.counterNumberSpinBox = QtGui.QSpinBox(self.counterGroupBox)
        self.counterNumberSpinBox.setProperty("value",QtCore.QVariant(4))
        self.counterNumberSpinBox.setObjectName("counterNumberSpinBox")
        self.gridlayout2.addWidget(self.counterNumberSpinBox,2,2,1,1)

        spacerItem1 = QtGui.QSpacerItem(20,40,QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Expanding)
        self.gridlayout2.addItem(spacerItem1,3,2,1,1)
        self.vboxlayout.addWidget(self.counterGroupBox)

        self.groupBox_3 = QtGui.QGroupBox(self.simulators)
        self.groupBox_3.setObjectName("groupBox_3")

        self.gridlayout3 = QtGui.QGridLayout(self.groupBox_3)
        self.gridlayout3.setObjectName("gridlayout3")

        self.zeroDNumberLabel = QtGui.QLabel(self.groupBox_3)
        self.zeroDNumberLabel.setObjectName("zeroDNumberLabel")
        self.gridlayout3.addWidget(self.zeroDNumberLabel,0,0,1,1)

        self.zeroDNumberSpinBox = QtGui.QSpinBox(self.groupBox_3)
        self.zeroDNumberSpinBox.setProperty("value",QtCore.QVariant(2))
        self.zeroDNumberSpinBox.setObjectName("zeroDNumberSpinBox")
        self.gridlayout3.addWidget(self.zeroDNumberSpinBox,0,1,1,1)

        self.label = QtGui.QLabel(self.groupBox_3)
        self.label.setWordWrap(True)
        self.label.setObjectName("label")
        self.gridlayout3.addWidget(self.label,1,0,1,1)

        spacerItem2 = QtGui.QSpacerItem(20,40,QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Expanding)
        self.gridlayout3.addItem(spacerItem2,1,1,1,1)
        self.vboxlayout.addWidget(self.groupBox_3)
        self.simuTabWidget.addTab(self.simulators,"")

        self.pool = QtGui.QWidget()
        self.pool.setObjectName("pool")

        self.gridlayout4 = QtGui.QGridLayout(self.pool)
        self.gridlayout4.setObjectName("gridlayout4")

        self.poolServerNameLabel = QtGui.QLabel(self.pool)
        self.poolServerNameLabel.setObjectName("poolServerNameLabel")
        self.gridlayout4.addWidget(self.poolServerNameLabel,0,0,1,1)

        self.poolServerNameLineEdit = QtGui.QLineEdit(self.pool)
        self.poolServerNameLineEdit.setEnabled(False)
        self.poolServerNameLineEdit.setObjectName("poolServerNameLineEdit")
        self.gridlayout4.addWidget(self.poolServerNameLineEdit,0,1,1,1)

        self.poolNamelabel = QtGui.QLabel(self.pool)
        self.poolNamelabel.setObjectName("poolNamelabel")
        self.gridlayout4.addWidget(self.poolNamelabel,1,0,1,1)

        self.poolNameLineEdit = QtGui.QLineEdit(self.pool)
        self.poolNameLineEdit.setObjectName("poolNameLineEdit")
        self.gridlayout4.addWidget(self.poolNameLineEdit,1,1,1,1)

        self.poolPathLabel = QtGui.QLabel(self.pool)
        self.poolPathLabel.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.poolPathLabel.setObjectName("poolPathLabel")
        self.gridlayout4.addWidget(self.poolPathLabel,2,0,1,1)

        spacerItem3 = QtGui.QSpacerItem(20,141,QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Expanding)
        self.gridlayout4.addItem(spacerItem3,3,1,1,1)

        self.poolPathTextEdit = QtGui.QTextEdit(self.pool)
        self.poolPathTextEdit.setObjectName("poolPathTextEdit")
        self.gridlayout4.addWidget(self.poolPathTextEdit,2,1,1,1)
        self.simuTabWidget.addTab(self.pool,"")

        self.macroServer = QtGui.QWidget()
        self.macroServer.setObjectName("macroServer")

        self.vboxlayout1 = QtGui.QVBoxLayout(self.macroServer)
        self.vboxlayout1.setObjectName("vboxlayout1")

        self.groupBox = QtGui.QGroupBox(self.macroServer)
        self.groupBox.setObjectName("groupBox")

        self.gridlayout5 = QtGui.QGridLayout(self.groupBox)
        self.gridlayout5.setObjectName("gridlayout5")

        self.msServerNameLabel = QtGui.QLabel(self.groupBox)
        self.msServerNameLabel.setObjectName("msServerNameLabel")
        self.gridlayout5.addWidget(self.msServerNameLabel,0,0,1,1)

        self.msServerNameLineEdit = QtGui.QLineEdit(self.groupBox)
        self.msServerNameLineEdit.setEnabled(False)
        self.msServerNameLineEdit.setObjectName("msServerNameLineEdit")
        self.gridlayout5.addWidget(self.msServerNameLineEdit,0,1,1,1)

        self.msNameLabel = QtGui.QLabel(self.groupBox)
        self.msNameLabel.setObjectName("msNameLabel")
        self.gridlayout5.addWidget(self.msNameLabel,1,0,1,1)

        self.msNameLineEdit = QtGui.QLineEdit(self.groupBox)
        self.msNameLineEdit.setObjectName("msNameLineEdit")
        self.gridlayout5.addWidget(self.msNameLineEdit,1,1,1,1)

        self.macroPathLabel = QtGui.QLabel(self.groupBox)
        self.macroPathLabel.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.macroPathLabel.setObjectName("macroPathLabel")
        self.gridlayout5.addWidget(self.macroPathLabel,2,0,1,1)

        self.macroPathTextEdit = QtGui.QTextEdit(self.groupBox)
        self.macroPathTextEdit.setObjectName("macroPathTextEdit")
        self.gridlayout5.addWidget(self.macroPathTextEdit,2,1,1,1)
        self.vboxlayout1.addWidget(self.groupBox)

        self.groupBox_2 = QtGui.QGroupBox(self.macroServer)
        self.groupBox_2.setObjectName("groupBox_2")

        self.gridlayout6 = QtGui.QGridLayout(self.groupBox_2)
        self.gridlayout6.setObjectName("gridlayout6")

        self.doorNameLabel = QtGui.QLabel(self.groupBox_2)
        self.doorNameLabel.setObjectName("doorNameLabel")
        self.gridlayout6.addWidget(self.doorNameLabel,0,0,1,1)

        self.doorNameLineEdit = QtGui.QLineEdit(self.groupBox_2)
        self.doorNameLineEdit.setObjectName("doorNameLineEdit")
        self.gridlayout6.addWidget(self.doorNameLineEdit,0,1,1,1)
        self.vboxlayout1.addWidget(self.groupBox_2)
        self.simuTabWidget.addTab(self.macroServer,"")
        self.gridlayout.addWidget(self.simuTabWidget,1,0,1,3)

        self.actionCreate = QtGui.QAction(simuConfigDialog)
        self.actionCreate.setObjectName("actionCreate")
        self.motorServerNamelabel.setBuddy(self.motorServerNameLineEdit)
        self.motorControllerNameLabel.setBuddy(self.motorControllerNameLineEdit)
        self.motorNumberLabel.setBuddy(self.motorNumberSpinBox)
        self.counterServerNamelabel.setBuddy(self.motorServerNameLineEdit)
        self.counterControllerNameLabel.setBuddy(self.motorControllerNameLineEdit)
        self.counterNumberLabel.setBuddy(self.motorNumberSpinBox)
        self.zeroDNumberLabel.setBuddy(self.motorNumberSpinBox)
        self.poolServerNameLabel.setBuddy(self.poolServerNameLineEdit)
        self.poolNamelabel.setBuddy(self.motorControllerNameLineEdit)
        self.poolPathLabel.setBuddy(self.poolPathTextEdit)
        self.msServerNameLabel.setBuddy(self.msServerNameLineEdit)
        self.msNameLabel.setBuddy(self.motorControllerNameLineEdit)
        self.macroPathLabel.setBuddy(self.macroPathTextEdit)
        self.doorNameLabel.setBuddy(self.motorControllerNameLineEdit)

        self.retranslateUi(simuConfigDialog)
        self.simuTabWidget.setCurrentIndex(0)
        QtCore.QObject.connect(self.buttonBox,QtCore.SIGNAL("accepted()"),self.actionCreate.trigger)
        QtCore.QObject.connect(self.buttonBox,QtCore.SIGNAL("rejected()"),simuConfigDialog.close)
        QtCore.QMetaObject.connectSlotsByName(simuConfigDialog)

    def retranslateUi(self, simuConfigDialog):
        simuConfigDialog.setWindowTitle(QtGui.QApplication.translate("simuConfigDialog", "Sardana simulation Configurator", None, QtGui.QApplication.UnicodeUTF8))
        self.motorGroupBox.setTitle(QtGui.QApplication.translate("simuConfigDialog", "Motor simulator", None, QtGui.QApplication.UnicodeUTF8))
        self.motorServerNamelabel.setText(QtGui.QApplication.translate("simuConfigDialog", "Server name:", None, QtGui.QApplication.UnicodeUTF8))
        self.motorControllerNameLabel.setText(QtGui.QApplication.translate("simuConfigDialog", "Motor controller name:", None, QtGui.QApplication.UnicodeUTF8))
        self.motorNumberLabel.setText(QtGui.QApplication.translate("simuConfigDialog", "Number motors:", None, QtGui.QApplication.UnicodeUTF8))
        self.counterGroupBox.setTitle(QtGui.QApplication.translate("simuConfigDialog", "Counter simulator", None, QtGui.QApplication.UnicodeUTF8))
        self.counterServerNamelabel.setText(QtGui.QApplication.translate("simuConfigDialog", "Server name:", None, QtGui.QApplication.UnicodeUTF8))
        self.counterControllerNameLabel.setText(QtGui.QApplication.translate("simuConfigDialog", "Counter controller name:", None, QtGui.QApplication.UnicodeUTF8))
        self.counterNumberLabel.setText(QtGui.QApplication.translate("simuConfigDialog", "Number counters:", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_3.setTitle(QtGui.QApplication.translate("simuConfigDialog", "0D Simulator", None, QtGui.QApplication.UnicodeUTF8))
        self.zeroDNumberLabel.setText(QtGui.QApplication.translate("simuConfigDialog", "Number 0D Channels:", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("simuConfigDialog", "(Actually there is no 0D simulator. The 0D controller in the device pool will act as the simulator itself)", None, QtGui.QApplication.UnicodeUTF8))
        self.simuTabWidget.setTabText(self.simuTabWidget.indexOf(self.simulators), QtGui.QApplication.translate("simuConfigDialog", "Simulators", None, QtGui.QApplication.UnicodeUTF8))
        self.poolServerNameLabel.setText(QtGui.QApplication.translate("simuConfigDialog", "Server name:", None, QtGui.QApplication.UnicodeUTF8))
        self.poolNamelabel.setText(QtGui.QApplication.translate("simuConfigDialog", "Pool name:", None, QtGui.QApplication.UnicodeUTF8))
        self.poolPathLabel.setText(QtGui.QApplication.translate("simuConfigDialog", "PoolPath:", None, QtGui.QApplication.UnicodeUTF8))
        self.simuTabWidget.setTabText(self.simuTabWidget.indexOf(self.pool), QtGui.QApplication.translate("simuConfigDialog", "Device Pool", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("simuConfigDialog", "Macro Server", None, QtGui.QApplication.UnicodeUTF8))
        self.msServerNameLabel.setText(QtGui.QApplication.translate("simuConfigDialog", "Server name:", None, QtGui.QApplication.UnicodeUTF8))
        self.msNameLabel.setText(QtGui.QApplication.translate("simuConfigDialog", "Macro server name:", None, QtGui.QApplication.UnicodeUTF8))
        self.macroPathLabel.setText(QtGui.QApplication.translate("simuConfigDialog", "MacroPath:", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_2.setTitle(QtGui.QApplication.translate("simuConfigDialog", "Door", None, QtGui.QApplication.UnicodeUTF8))
        self.doorNameLabel.setText(QtGui.QApplication.translate("simuConfigDialog", "Door name:", None, QtGui.QApplication.UnicodeUTF8))
        self.simuTabWidget.setTabText(self.simuTabWidget.indexOf(self.macroServer), QtGui.QApplication.translate("simuConfigDialog", "Macro Server", None, QtGui.QApplication.UnicodeUTF8))
        self.actionCreate.setText(QtGui.QApplication.translate("simuConfigDialog", "create", None, QtGui.QApplication.UnicodeUTF8))

