# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'TaurusDevPanel.ui'
#
# Created: Fri Aug 20 17:59:11 2010
#      by: PyQt4 UI code generator 4.7.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_TaurusDevPanel(object):
    def setupUi(self, TaurusDevPanel):
        TaurusDevPanel.setObjectName("TaurusDevPanel")
        TaurusDevPanel.resize(484, 615)
        self.centralwidget = QtGui.QWidget(TaurusDevPanel)
        self.centralwidget.setObjectName("centralwidget")
        self.hboxlayout = QtGui.QHBoxLayout(self.centralwidget)
        self.hboxlayout.setObjectName("hboxlayout")
        TaurusDevPanel.setCentralWidget(self.centralwidget)
        self.statusbar = QtGui.QStatusBar(TaurusDevPanel)
        self.statusbar.setObjectName("statusbar")
        TaurusDevPanel.setStatusBar(self.statusbar)
        self.attrDW = QtGui.QDockWidget(TaurusDevPanel)
        self.attrDW.setAllowedAreas(QtCore.Qt.AllDockWidgetAreas)
        self.attrDW.setObjectName("attrDW")
        self.dockWidgetContents = QtGui.QWidget()
        self.dockWidgetContents.setObjectName("dockWidgetContents")
        self.vboxlayout = QtGui.QVBoxLayout(self.dockWidgetContents)
        self.vboxlayout.setObjectName("vboxlayout")
        self.taurusAttrForm = TaurusAttrForm(self.dockWidgetContents)
        self.taurusAttrForm.setUseParentModel(True)
        self.taurusAttrForm.setObjectName("taurusAttrForm")
        self.vboxlayout.addWidget(self.taurusAttrForm)
        self.attrDW.setWidget(self.dockWidgetContents)
        TaurusDevPanel.addDockWidget(QtCore.Qt.DockWidgetArea(2), self.attrDW)
        self.commandsDW = QtGui.QDockWidget(TaurusDevPanel)
        self.commandsDW.setAllowedAreas(QtCore.Qt.AllDockWidgetAreas)
        self.commandsDW.setObjectName("commandsDW")
        self.dockWidgetContents_2 = QtGui.QWidget()
        self.dockWidgetContents_2.setObjectName("dockWidgetContents_2")
        self.vboxlayout1 = QtGui.QVBoxLayout(self.dockWidgetContents_2)
        self.vboxlayout1.setObjectName("vboxlayout1")
        self.taurusCommandsForm = TaurusCommandsForm(self.dockWidgetContents_2)
        self.taurusCommandsForm.setUseParentModel(True)
        self.taurusCommandsForm.setObjectName("taurusCommandsForm")
        self.vboxlayout1.addWidget(self.taurusCommandsForm)
        self.commandsDW.setWidget(self.dockWidgetContents_2)
        TaurusDevPanel.addDockWidget(QtCore.Qt.DockWidgetArea(2), self.commandsDW)
        self.trendDW = QtGui.QDockWidget(TaurusDevPanel)
        self.trendDW.setObjectName("trendDW")
        self.dockWidgetContents_3 = QtGui.QWidget()
        self.dockWidgetContents_3.setObjectName("dockWidgetContents_3")
        self.vboxlayout2 = QtGui.QVBoxLayout(self.dockWidgetContents_3)
        self.vboxlayout2.setObjectName("vboxlayout2")
        self.taurusTrend = TaurusTrend(self.dockWidgetContents_3)
        self.taurusTrend.setObjectName("taurusTrend")
        self.vboxlayout2.addWidget(self.taurusTrend)
        self.trendDW.setWidget(self.dockWidgetContents_3)
        TaurusDevPanel.addDockWidget(QtCore.Qt.DockWidgetArea(8), self.trendDW)

        self.retranslateUi(TaurusDevPanel)
        QtCore.QMetaObject.connectSlotsByName(TaurusDevPanel)

    def retranslateUi(self, TaurusDevPanel):
        TaurusDevPanel.setWindowTitle(QtGui.QApplication.translate("TaurusDevPanel", "MainWindow", None, QtGui.QApplication.UnicodeUTF8))
        self.attrDW.setWindowTitle(QtGui.QApplication.translate("TaurusDevPanel", "Attributes", None, QtGui.QApplication.UnicodeUTF8))
        self.commandsDW.setWindowTitle(QtGui.QApplication.translate("TaurusDevPanel", "Commands", None, QtGui.QApplication.UnicodeUTF8))
        self.trendDW.setWindowTitle(QtGui.QApplication.translate("TaurusDevPanel", "Trends", None, QtGui.QApplication.UnicodeUTF8))

from taurus.qt.qtgui.plot import TaurusTrend
from taurus.qt.qtgui.panel import TaurusCommandsForm, TaurusAttrForm

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    TaurusDevPanel = QtGui.QMainWindow()
    ui = Ui_TaurusDevPanel()
    ui.setupUi(TaurusDevPanel)
    TaurusDevPanel.show()
    sys.exit(app.exec_())

