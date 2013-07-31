#!/usr/bin/env python

#############################################################################
##
## This file is part of Taurus, a Tango User Interface Library
## 
## http://www.tango-controls.org/static/taurus/latest/doc/html/index.html
##
## Copyright 2011 CELLS / ALBA Synchrotron, Bellaterra, Spain
## 
## Taurus is free software: you can redistribute it and/or modify
## it under the terms of the GNU Lesser General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
## 
## Taurus is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU Lesser General Public License for more details.
## 
## You should have received a copy of the GNU Lesser General Public License
## along with Taurus.  If not, see <http://www.gnu.org/licenses/>.
##
#############################################################################

"""
motor.py: 
"""


from taurus.qt import Qt
from taurus.qt.qtgui.base import TaurusBaseWidget
from ui_taurusmotorh import Ui_TaurusMotorH
from ui_taurusmotorh2 import Ui_TaurusMotorH2
from ui_taurusmotorv import Ui_TaurusMotorV
from ui_taurusmotorv2 import Ui_TaurusMotorV2


def showDialogConfigureMotor(parent):
    Dialog = Qt.QDialog(parent)
    Dialog.resize((Qt.QSize(Qt.QRect(0,0,310,309).size()).expandedTo(Dialog.minimumSizeHint())))
    motorV2 = TaurusMotorV2(Dialog)
    motorV2.setModel(parent.model)
    motorV2.setGeometry(Qt.QRect(10,10,291,291))
    Dialog.show()


class TaurusMotorH(Qt.QWidget, TaurusBaseWidget):

    __pyqtSignals__ = ("modelChanged(const QString &)",)

    def __init__(self, parent = None, designMode = False):
        self.call__init__wo_kw(Qt.QWidget, parent)
        self.call__init__(TaurusBaseWidget, str(self.objectName()), designMode=designMode)
        self.ui = Ui_TaurusMotorH()
        self.ui.setupUi(self)
        Qt.QObject.connect(self.ui.config, Qt.SIGNAL("clicked()"), self.configureMotor)

    def sizeHint(self):
        return Qt.QSize(330,50)

    def configureMotor(self):
        showDialogConfigureMotor(self.ui.TaurusGroupBox)

    @classmethod
    def getQtDesignerPluginInfo(cls):
        return None
#        ret = TaurusBaseWidget.getQtDesignerPluginInfo()
#        ret['module'] = 'taurus.qt.qtgui.extra_pool'
#        ret['group'] = 'Taurus Sardana'
#        ret['icon'] = ':/designer/extra_pool.png'
#        return ret
        
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # QT properties 
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    @Qt.pyqtSignature("getModel()")
    def getModel(self):
        return self.ui.TaurusGroupBox.getModel()

    @Qt.pyqtSignature("setModel(QString)")
    def setModel(self, model):
        self.ui.TaurusGroupBox.setModel(model)

    @Qt.pyqtSignature("resetModel()")
    def resetModel(self):
        self.ui.TaurusGroupBox.resetModel()


    @Qt.pyqtSignature("getShowText()")
    def getShowText(self):
        return self.ui.TaurusGroupBox.getShowText()

    @Qt.pyqtSignature("setShowText(bool)")
    def setShowText(self, showText):
        self.ui.TaurusGroupBox.setShowText(showText)

    @Qt.pyqtSignature("resetShowText()")
    def resetShowText(self):
        self.ui.TaurusGroupBox.resetShowText()

    model = Qt.pyqtProperty("QString", getModel,setModel,resetModel)
    showText = Qt.pyqtProperty("bool", getShowText,setShowText,resetShowText)

   

class TaurusMotorH2(Qt.QWidget, TaurusBaseWidget):
    
    __pyqtSignals__ = ("modelChanged(const QString &)",)

    def __init__(self, parent = None, designMode = False):
        self.call__init__wo_kw(Qt.QWidget, parent)
        self.call__init__(TaurusBaseWidget, str(self.objectName()), designMode=designMode)
        self.ui = Ui_TaurusMotorH2()
        self.ui.setupUi(self)
        Qt.QObject.connect(self.ui.config, Qt.SIGNAL("clicked()"), self.configureMotor)

    def sizeHint(self):
        return Qt.QSize(215,85)

    def configureMotor(self):
        showDialogConfigureMotor(self.ui.TaurusGroupBox)

    @classmethod
    def getQtDesignerPluginInfo(cls):
        return None
#        ret = TaurusBaseWidget.getQtDesignerPluginInfo()
#        ret['module'] = 'taurus.qt.qtgui.extra_pool'
#        ret['group'] = 'Taurus Sardana'
#        ret['icon'] = ':/designer/extra_pool.png'
#        return ret
        
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # QT properties 
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    @Qt.pyqtSignature("getModel()")
    def getModel(self):
        return self.ui.TaurusGroupBox.getModel()

    @Qt.pyqtSignature("setModel(QString)")
    def setModel(self, model):
        self.ui.TaurusGroupBox.setModel(model)

    @Qt.pyqtSignature("resetModel()")
    def resetModel(self):
        self.ui.TaurusGroupBox.resetModel()


    @Qt.pyqtSignature("getShowText()")
    def getShowText(self):
        return self.ui.TaurusGroupBox.getShowText()

    @Qt.pyqtSignature("setShowText(bool)")
    def setShowText(self, showText):
        self.ui.TaurusGroupBox.setShowText(showText)

    @Qt.pyqtSignature("resetShowText()")
    def resetShowText(self):
        self.ui.TaurusGroupBox.resetShowText()


    model = Qt.pyqtProperty("QString", getModel,setModel,resetModel)
    showText = Qt.pyqtProperty("bool", getShowText,setShowText,resetShowText)


class TaurusMotorV(Qt.QWidget, TaurusBaseWidget):
    
    __pyqtSignals__ = ("modelChanged(const QString &)",)

    def __init__(self, parent = None, designMode = False):
        self.call__init__wo_kw(Qt.QWidget, parent)
        self.call__init__(TaurusBaseWidget, str(self.objectName()), designMode=designMode)
        self.ui = Ui_TaurusMotorV()
        self.ui.setupUi(self)
        Qt.QObject.connect(self.ui.config, Qt.SIGNAL("clicked()"), self.configureMotor)

    def sizeHint(self):
        return Qt.QSize(120,145)

    def configureMotor(self):
        showDialogConfigureMotor(self.ui.TaurusGroupBox)

    @classmethod
    def getQtDesignerPluginInfo(cls):
        return None
#        ret = TaurusBaseWidget.getQtDesignerPluginInfo()
#        ret['module'] = 'taurus.qt.qtgui.extra_pool'
#        ret['group'] = 'Taurus Sardana'
#        ret['icon'] = ':/designer/extra_pool.png'
#        return ret
        
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # QT properties 
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    @Qt.pyqtSignature("getModel()")
    def getModel(self):
        return self.ui.TaurusGroupBox.getModel()

    @Qt.pyqtSignature("setModel(QString)")
    def setModel(self, model):
        self.ui.TaurusGroupBox.setModel(model)

    @Qt.pyqtSignature("resetModel()")
    def resetModel(self):
        self.ui.TaurusGroupBox.resetModel()


    @Qt.pyqtSignature("getShowText()")
    def getShowText(self):
        return self.ui.TaurusGroupBox.getShowText()

    @Qt.pyqtSignature("setShowText(bool)")
    def setShowText(self, showText):
        self.ui.TaurusGroupBox.setShowText(showText)

    @Qt.pyqtSignature("resetShowText()")
    def resetShowText(self):
        self.ui.TaurusGroupBox.resetShowText()


    model = Qt.pyqtProperty("QString", getModel,setModel,resetModel)
    showText = Qt.pyqtProperty("bool", getShowText,setShowText,resetShowText)


class TaurusMotorV2(Qt.QWidget, TaurusBaseWidget):
    
    __pyqtSignals__ = ("modelChanged(const QString &)",)

    def __init__(self, parent = None, designMode = False):
        self.call__init__wo_kw(Qt.QWidget, parent)
        self.call__init__(TaurusBaseWidget, str(self.objectName()), designMode=designMode)
        self.ui = Ui_TaurusMotorV2()
        self.ui.setupUi(self)

    def sizeHint(self):
        return Qt.QSize(300,275)

    @classmethod
    def getQtDesignerPluginInfo(cls):
        return None
#        ret = TaurusBaseWidget.getQtDesignerPluginInfo()
#        ret['module'] = 'taurus.qt.qtgui.extra_pool'
#        ret['group'] = 'Taurus Sardana'
#        ret['icon'] = ':/designer/extra_pool.png'
#        return ret
        
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # QT properties 
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    @Qt.pyqtSignature("getModel()")
    def getModel(self):
        return self.ui.TaurusGroupBox.getModel()

    @Qt.pyqtSignature("setModel(QString)")
    def setModel(self, model):
        self.ui.TaurusGroupBox.setModel(model)

    @Qt.pyqtSignature("resetModel()")
    def resetModel(self):
        self.ui.TaurusGroupBox.resetModel()


    @Qt.pyqtSignature("getShowText()")
    def getShowText(self):
        return self.ui.TaurusGroupBox.getShowText()

    @Qt.pyqtSignature("setShowText(bool)")
    def setShowText(self, showText):
        self.ui.TaurusGroupBox.setShowText(showText)

    @Qt.pyqtSignature("resetShowText()")
    def resetShowText(self):
        self.ui.TaurusGroupBox.resetShowText()


    model = Qt.pyqtProperty("QString", getModel,setModel,resetModel)
    showText = Qt.pyqtProperty("bool", getShowText,setShowText,resetShowText)
   

###class TaurusMotorH2(Qt.QGroupBox, TaurusBaseWidget):
###    
###    def __init__(self, parent = None, designMode = False):
###        name = "TaurusMotorH2"
###        self._prefix = ''
###        self._suffix = ''
###        
###        self.call__init__wo_kw(Qt.QGroupBox, parent)
###        self.call__init__(TaurusBaseWidget, name, designMode = designMode)
###        
###        self.setObjectName(name)
###        self.defineStyle()
###        
###
###        ## I CAN NOT INHERIT FROM TAUGROUPBOX !
###        ## SO ALL THE STUFFABOVE IS NECESSARY
###        ##
###        ## ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
###        ##############################################################################
###        ##
###        #class TaurusMotorH2(TaurusGroupBox):
###        #def __init__(self, parent = None):
###        #self.call__init__wo_kw(TaurusGroupBox,parent)
###        #self.call__init__(TaurusGroupBox,str(self.objectName()))
###        self.setupUi()
###        self.retranslateUi()
###        self.connect(self.config,Qt.SIGNAL('clicked()'),self.configureMotor)
###
###
###    def configureMotor(self):
###        Dialog = Qt.QDialog(self)
###        Dialog.resize((Qt.QSize(Qt.QRect(0,0,310,309).size()).expandedTo(Dialog.minimumSizeHint())))
###        motorV2 = TaurusMotorV2(Dialog)
###        motorV2.setModel(self.model)
###        motorV2.setGeometry(Qt.QRect(10,10,291,291))
###        Dialog.show()
###
###
###
###    def minimumSizeHint(self):
###        return Qt.QSize(211,80)
###    
###    def sizeHint(self):
###        return Qt.QSize(211,80)
###    
###
###    def setupUi(self):
###
###        self.gridlayout = Qt.QGridLayout(self)
###        self.gridlayout.setObjectName("gridlayout")
###
###        self.vboxlayout = Qt.QVBoxLayout()
###        self.vboxlayout.setObjectName("vboxlayout")
###
###        self.hboxlayout = Qt.QHBoxLayout()
###        self.hboxlayout.setObjectName("hboxlayout")
###
###        self.taurusValueLabel_2 = TaurusValueLabel(self)
###        self.taurusValueLabel_2.setFrameShape(Qt.QFrame.NoFrame)
###        self.taurusValueLabel_2.setFrameShadow(Qt.QFrame.Plain)
###        self.taurusValueLabel_2.setShowQuality(False)
###        self.taurusValueLabel_2.setUseParentModel(True)
###        self.taurusValueLabel_2.setObjectName("taurusValueLabel_2")
###        self.hboxlayout.addWidget(self.taurusValueLabel_2)
###
###        self.TaurusStateLed_17 = TaurusStateLed(self)
###        self.TaurusStateLed_17.setUseParentModel(True)
###        self.TaurusStateLed_17.setObjectName("TaurusStateLed_17")
###        self.hboxlayout.addWidget(self.TaurusStateLed_17)
###
###        spacerItem = Qt.QSpacerItem(40,20,Qt.QSizePolicy.Expanding,Qt.QSizePolicy.Minimum)
###        self.hboxlayout.addItem(spacerItem)
###
###        self.TaurusLimitSwitch = TaurusLimitSwitch(self)
###        self.TaurusLimitSwitch.setUseParentModel(True)
###        self.TaurusLimitSwitch.setBoolIndex(2)
###        self.TaurusLimitSwitch.setObjectName("TaurusLimitSwitch")
###        self.hboxlayout.addWidget(self.TaurusLimitSwitch)
###
###        self.label_3 = Qt.QLabel(self)
###        self.label_3.setAlignment(Qt.Qt.AlignCenter)
###        self.label_3.setObjectName("label_3")
###        self.hboxlayout.addWidget(self.label_3)
###
###        self.TaurusLimitSwitch_2 = TaurusLimitSwitch(self)
###        self.TaurusLimitSwitch_2.setUseParentModel(True)
###        self.TaurusLimitSwitch_2.setBoolIndex(1)
###        self.TaurusLimitSwitch_2.setObjectName("TaurusLimitSwitch_2")
###        self.hboxlayout.addWidget(self.TaurusLimitSwitch_2)
###        self.vboxlayout.addLayout(self.hboxlayout)
###
###        self.hboxlayout1 = Qt.QHBoxLayout()
###        self.hboxlayout1.setObjectName("hboxlayout1")
###
###        self.TaurusValueLineEdit_21 = TaurusValueLineEdit(self)
###        self.TaurusValueLineEdit_21.setUseParentModel(True)
###        self.TaurusValueLineEdit_21.setObjectName("TaurusValueLineEdit_21")
###        self.hboxlayout1.addWidget(self.TaurusValueLineEdit_21)
###
###        self.taurusValueLabel_21 = TaurusValueLabel(self)
###
###        sizePolicy = Qt.QSizePolicy(Qt.QSizePolicy.Expanding,Qt.QSizePolicy.Preferred)
###        sizePolicy.setHorizontalStretch(0)
###        sizePolicy.setVerticalStretch(0)
###        sizePolicy.setHeightForWidth(self.taurusValueLabel_21.sizePolicy().hasHeightForWidth())
###        self.taurusValueLabel_21.setSizePolicy(sizePolicy)
###        self.taurusValueLabel_21.setUseParentModel(True)
###        self.taurusValueLabel_21.setObjectName("taurusValueLabel_21")
###        self.hboxlayout1.addWidget(self.taurusValueLabel_21)
###
###        self.taurusConfigLabel_18 = TaurusConfigLabel(self)
###        self.taurusConfigLabel_18.setMaximumSize(Qt.QSize(27,22))
###        self.taurusConfigLabel_18.setUseParentModel(True)
###        self.taurusConfigLabel_18.setObjectName("taurusConfigLabel_18")
###        self.hboxlayout1.addWidget(self.taurusConfigLabel_18)
###
###        self.config = Qt.QToolButton(self)
###        self.config.setObjectName("config")
###        self.hboxlayout1.addWidget(self.config)
###        self.vboxlayout.addLayout(self.hboxlayout1)
###        self.gridlayout.addLayout(self.vboxlayout,0,0,1,1)
###
###
###    def retranslateUi(self):
###        self.taurusValueLabel_2.setModel(Qt.QApplication.translate("Form", "/State", None, Qt.QApplication.UnicodeUTF8))
###        self.TaurusStateLed_17.setModel(Qt.QApplication.translate("Form", "/State", None, Qt.QApplication.UnicodeUTF8))
###        self.TaurusLimitSwitch.setModel(Qt.QApplication.translate("Form", "/Limit_switches", None, Qt.QApplication.UnicodeUTF8))
###        self.label_3.setText(Qt.QApplication.translate("Form", "- lim +", None, Qt.QApplication.UnicodeUTF8))
###        self.TaurusLimitSwitch_2.setModel(Qt.QApplication.translate("Form", "/Limit_switches", None, Qt.QApplication.UnicodeUTF8))
###        self.TaurusValueLineEdit_21.setModel(Qt.QApplication.translate("Form", "/Position", None, Qt.QApplication.UnicodeUTF8))
###        self.taurusValueLabel_21.setModel(Qt.QApplication.translate("Form", "/Position", None, Qt.QApplication.UnicodeUTF8))
###        self.taurusConfigLabel_18.setModel(Qt.QApplication.translate("Form", "/Position?configuration=unit", None, Qt.QApplication.UnicodeUTF8))
###        self.config.setText(Qt.QApplication.translate("Form", "cfg", None, Qt.QApplication.UnicodeUTF8))
###
###
###    ##############################################################################
###    ## VVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV
###    ##
###    ## I CAN NOT INHERIT FROM TAUGROUPBOX !
###    ## SO ALL THE STUFF BELOW IS NECESSARY
###
###
###        
###    def defineStyle(self):
###        palette = Qt.QPalette()
###        self.setPalette(palette)
###        self.updateStyle()
###        
###    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
###    # TaurusBaseWidget over writing
###    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
###                    
###    def getDisplayValue(self):
###        return (self._prefix or '') + TaurusBaseWidget.getDisplayValue(self) + (self._suffix or '')
###    
###    def isReadOnly(self):
###        return True
###    
###    def updateStyle(self):
###        if self.getShowQuality():
###            self.setAutoFillBackground(True)
###            #TODO: get quality/state from model and update accordingly
###        else:
###            self.setAutoFillBackground(False)
###            #TODO: restore colors
###        self.update()
###        
###    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
###    # QT properties 
###    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
###   
###    def getPrefixText(self):
###        return self._prefix
###    
###    @Qt.pyqtSignature("setPrefixText(QString)")
###    def setPrefixText(self,prefix):
###        self._prefix = prefix
###        self.fireValueChanged()
###
###    def getSuffixText(self):
###        return self._suffix
###    
###    @Qt.pyqtSignature("setSuffixText(QString)")
###    def setSuffixText(self,suffix):
###        self._suffix = suffix
###        self.fireValueChanged()
###
###    model = Qt.pyqtProperty("QString", TaurusBaseWidget.getModel, 
###                                TaurusBaseWidget.setModel, TaurusBaseWidget.resetModel)
###    useParentModel = Qt.pyqtProperty("bool", TaurusBaseWidget.getUseParentModel, 
###                                         TaurusBaseWidget.setUseParentModel, 
###                                         TaurusBaseWidget.resetUseParentModel)
###    showQuality = Qt.pyqtProperty("bool", TaurusBaseWidget.getShowQuality, 
###                                      TaurusBaseWidget.setShowQuality, 
###                                      TaurusBaseWidget.resetShowQuality)
###    showText = Qt.pyqtProperty("bool", TaurusBaseWidget.getShowText, 
###                                   TaurusBaseWidget.setShowText, 
###                                   TaurusBaseWidget.resetShowText)
###    prefixText = Qt.pyqtProperty("QString", getPrefixText, setPrefixText, 
###                                     doc="prefix text (optional)")
###    suffixText = Qt.pyqtProperty("QString", getSuffixText, setSuffixText, 
###                                    doc="suffix text (optional)")
###
###        
###
###
###class TaurusMotorV(Qt.QGroupBox, TaurusBaseWidget):
###    
###    def __init__(self, parent = None):
###        name = "TaurusMotorV"
###        self._prefix = ''
###        self._suffix = ''
###        
###        self.call__init__wo_kw(Qt.QGroupBox, parent)
###        self.call__init__(TaurusBaseWidget, name)
###        
###        self.setObjectName(name)
###        self.defineStyle()
###        
###
###        ## I CAN NOT INHERIT FROM TAUGROUPBOX !
###        ## SO ALL THE STUFFABOVE IS NECESSARY
###        ##
###        ## ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
###        ##############################################################################
###        ##
###        #class TaurusMotorV(TaurusGroupBox):
###        #def __init__(self, parent = None):
###        #self.call__init__wo_kw(TaurusGroupBox,parent)
###        #self.call__init__(TaurusGroupBox,str(self.objectName()))
###        self.setupUi()
###        self.retranslateUi()
###        self.connect(self.config,Qt.SIGNAL('clicked()'),self.configureMotor)
###
###
###    def configureMotor(self):
###        Dialog = Qt.QDialog(self)
###        Dialog.resize((Qt.QSize(Qt.QRect(0,0,310,309).size()).expandedTo(Dialog.minimumSizeHint())))
###        motorV2 = TaurusMotorV2(Dialog)
###        motorV2.setModel(self.model)
###        motorV2.setGeometry(Qt.QRect(10,10,291,291))
###        Dialog.show()
###
###
###
###
###    def minimumSizeHint(self):
###        return Qt.QSize(150,128)
###    
###    def sizeHint(self):
###        return Qt.QSize(150,128)
###    
###    def setupUi(self):
###
###        self.gridlayout = Qt.QGridLayout(self)
###        self.gridlayout.setObjectName("gridlayout")
###
###        self.vboxlayout = Qt.QVBoxLayout()
###        self.vboxlayout.setObjectName("vboxlayout")
###
###        self.hboxlayout = Qt.QHBoxLayout()
###        self.hboxlayout.setObjectName("hboxlayout")
###
###        self.taurusValueLabel_2 = TaurusValueLabel(self)
###        self.taurusValueLabel_2.setFrameShape(Qt.QFrame.NoFrame)
###        self.taurusValueLabel_2.setFrameShadow(Qt.QFrame.Plain)
###        self.taurusValueLabel_2.setShowQuality(False)
###        self.taurusValueLabel_2.setUseParentModel(True)
###        self.taurusValueLabel_2.setObjectName("taurusValueLabel_2")
###        self.hboxlayout.addWidget(self.taurusValueLabel_2)
###
###        self.TaurusStateLed_17 = TaurusStateLed(self)
###        self.TaurusStateLed_17.setUseParentModel(True)
###        self.TaurusStateLed_17.setObjectName("TaurusStateLed_17")
###        self.hboxlayout.addWidget(self.TaurusStateLed_17)
###        self.vboxlayout.addLayout(self.hboxlayout)
###
###        self.hboxlayout1 = Qt.QHBoxLayout()
###        self.hboxlayout1.setObjectName("hboxlayout1")
###
###        self.TaurusValueLineEdit_21 = TaurusValueLineEdit(self)
###        self.TaurusValueLineEdit_21.setUseParentModel(True)
###        self.TaurusValueLineEdit_21.setObjectName("TaurusValueLineEdit_21")
###        self.hboxlayout1.addWidget(self.TaurusValueLineEdit_21)
###
###        self.config = Qt.QToolButton(self)
###        self.config.setObjectName("config")
###        self.hboxlayout1.addWidget(self.config)
###        self.vboxlayout.addLayout(self.hboxlayout1)
###
###        self.hboxlayout2 = Qt.QHBoxLayout()
###        self.hboxlayout2.setObjectName("hboxlayout2")
###
###        self.taurusValueLabel_21 = TaurusValueLabel(self)
###        self.taurusValueLabel_21.setUseParentModel(True)
###        self.taurusValueLabel_21.setObjectName("taurusValueLabel_21")
###        self.hboxlayout2.addWidget(self.taurusValueLabel_21)
###
###        self.taurusConfigLabel_18 = TaurusConfigLabel(self)
###        self.taurusConfigLabel_18.setMaximumSize(Qt.QSize(27,22))
###        self.taurusConfigLabel_18.setUseParentModel(True)
###        self.taurusConfigLabel_18.setObjectName("taurusConfigLabel_18")
###        self.hboxlayout2.addWidget(self.taurusConfigLabel_18)
###        self.vboxlayout.addLayout(self.hboxlayout2)
###
###        self.hboxlayout3 = Qt.QHBoxLayout()
###        self.hboxlayout3.setObjectName("hboxlayout3")
###
###        self.TaurusLimitSwitch = TaurusLimitSwitch(self)
###        self.TaurusLimitSwitch.setUseParentModel(True)
###        self.TaurusLimitSwitch.setBoolIndex(2)
###        self.TaurusLimitSwitch.setObjectName("TaurusLimitSwitch")
###        self.hboxlayout3.addWidget(self.TaurusLimitSwitch)
###
###        self.label_3 = Qt.QLabel(self)
###        self.label_3.setAlignment(Qt.Qt.AlignCenter)
###        self.label_3.setObjectName("label_3")
###        self.hboxlayout3.addWidget(self.label_3)
###
###        self.TaurusLimitSwitch_2 = TaurusLimitSwitch(self)
###        self.TaurusLimitSwitch_2.setUseParentModel(True)
###        self.TaurusLimitSwitch_2.setBoolIndex(1)
###        self.TaurusLimitSwitch_2.setObjectName("TaurusLimitSwitch_2")
###        self.hboxlayout3.addWidget(self.TaurusLimitSwitch_2)
###        self.vboxlayout.addLayout(self.hboxlayout3)
###        self.gridlayout.addLayout(self.vboxlayout,0,0,1,1)
###
###
###    def retranslateUi(self):
###        self.taurusValueLabel_2.setModel(Qt.QApplication.translate("Form", "/State", None, Qt.QApplication.UnicodeUTF8))
###        self.TaurusStateLed_17.setModel(Qt.QApplication.translate("Form", "/State", None, Qt.QApplication.UnicodeUTF8))
###        self.TaurusValueLineEdit_21.setModel(Qt.QApplication.translate("Form", "/Position", None, Qt.QApplication.UnicodeUTF8))
###        self.config.setText(Qt.QApplication.translate("Form", "cfg", None, Qt.QApplication.UnicodeUTF8))
###        self.taurusValueLabel_21.setModel(Qt.QApplication.translate("Form", "/Position", None, Qt.QApplication.UnicodeUTF8))
###        self.taurusConfigLabel_18.setModel(Qt.QApplication.translate("Form", "/Position?configuration=unit", None, Qt.QApplication.UnicodeUTF8))
###        self.TaurusLimitSwitch.setModel(Qt.QApplication.translate("Form", "/Limit_switches", None, Qt.QApplication.UnicodeUTF8))
###        self.label_3.setText(Qt.QApplication.translate("Form", "- lim +", None, Qt.QApplication.UnicodeUTF8))
###        self.TaurusLimitSwitch_2.setModel(Qt.QApplication.translate("Form", "/Limit_switches", None, Qt.QApplication.UnicodeUTF8))
###
###    ##############################################################################
###    ## VVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV
###    ##
###    ## I CAN NOT INHERIT FROM TAUGROUPBOX !
###    ## SO ALL THE STUFF BELOW IS NECESSARY
###
###
###        
###    def defineStyle(self):
###        palette = Qt.QPalette()
###        self.setPalette(palette)
###        self.updateStyle()
###        
###    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
###    # TaurusBaseWidget over writing
###    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
###                    
###    def getDisplayValue(self):
###        return (self._prefix or '') + TaurusBaseWidget.getDisplayValue(self) + (self._suffix or '')
###    
###    def isReadOnly(self):
###        return True
###    
###    def updateStyle(self):
###        if self.getShowQuality():
###            self.setAutoFillBackground(True)
###            #TODO: get quality/state from model and update accordingly
###        else:
###            self.setAutoFillBackground(False)
###            #TODO: restore colors
###        self.update()
###        
###    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
###    # QT properties 
###    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
###   
###    def getPrefixText(self):
###        return self._prefix
###    
###    @Qt.pyqtSignature("setPrefixText(QString)")
###    def setPrefixText(self,prefix):
###        self._prefix = prefix
###        self.fireValueChanged()
###
###    def getSuffixText(self):
###        return self._suffix
###    
###    @Qt.pyqtSignature("setSuffixText(QString)")
###    def setSuffixText(self,suffix):
###        self._suffix = suffix
###        self.fireValueChanged()
###
###    model = Qt.pyqtProperty("QString", TaurusBaseWidget.getModel, 
###                                TaurusBaseWidget.setModel, TaurusBaseWidget.resetModel)
###    useParentModel = Qt.pyqtProperty("bool", TaurusBaseWidget.getUseParentModel, 
###                                         TaurusBaseWidget.setUseParentModel, 
###                                         TaurusBaseWidget.resetUseParentModel)
###    showQuality = Qt.pyqtProperty("bool", TaurusBaseWidget.getShowQuality, 
###                                      TaurusBaseWidget.setShowQuality, 
###                                      TaurusBaseWidget.resetShowQuality)
###    showText = Qt.pyqtProperty("bool", TaurusBaseWidget.getShowText, 
###                                   TaurusBaseWidget.setShowText, 
###                                   TaurusBaseWidget.resetShowText)
###    prefixText = Qt.pyqtProperty("QString", getPrefixText, setPrefixText, 
###                                     doc="prefix text (optional)")
###    suffixText = Qt.pyqtProperty("QString", getSuffixText, setSuffixText, 
###                                    doc="suffix text (optional)")
###
###        
###
###class TaurusMotorV2(Qt.QGroupBox, TaurusBaseWidget):
###    
###    def __init__(self, parent = None):
###        name = "TaurusMotorV2"
###        self._prefix = ''
###        self._suffix = ''
###        
###        self.call__init__wo_kw(Qt.QGroupBox, parent)
###        self.call__init__(TaurusBaseWidget, name)
###        
###        self.setObjectName(name)
###        self.defineStyle()
###        
###
###        ## I CAN NOT INHERIT FROM TAUGROUPBOX !
###        ## SO ALL THE STUFFABOVE IS NECESSARY
###        ##
###        ## ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
###        ##############################################################################
###        ##
###        #class TaurusMotorV2(TaurusGroupBox):
###        #def __init__(self, parent = None):
###        #self.call__init__wo_kw(TaurusGroupBox,parent)
###        #self.call__init__(TaurusGroupBox,str(self.objectName()))
###        self.setupUi()
###        self.retranslateUi()
###
###
###    def minimumSizeHint(self):
###        return Qt.QSize(260,270)
###    
###    def sizeHint(self):
###        return Qt.QSize(260,270)
###    
###
###    def setupUi(self):
###
###        self.gridlayout = Qt.QGridLayout(self)
###        self.gridlayout.setObjectName("gridlayout")
###
###        self.m1StateLed_2 = TaurusStateLed(self)
###        self.m1StateLed_2.setLedSize(24)
###        self.m1StateLed_2.setUseParentModel(True)
###        self.m1StateLed_2.setObjectName("m1StateLed_2")
###        self.gridlayout.addWidget(self.m1StateLed_2,0,0,1,1)
###
###        self.taurusValueLabel = TaurusValueLabel(self)
###        self.taurusValueLabel.setFrameShape(Qt.QFrame.NoFrame)
###        self.taurusValueLabel.setFrameShadow(Qt.QFrame.Plain)
###        self.taurusValueLabel.setShowQuality(False)
###        self.taurusValueLabel.setUseParentModel(True)
###        self.taurusValueLabel.setObjectName("taurusValueLabel")
###        self.gridlayout.addWidget(self.taurusValueLabel,0,1,1,1)
###
###        self.TaurusLimitSwitch = TaurusLimitSwitch(self)
###        self.TaurusLimitSwitch.setUseParentModel(True)
###        self.TaurusLimitSwitch.setBoolIndex(2)
###        self.TaurusLimitSwitch.setObjectName("TaurusLimitSwitch")
###        self.gridlayout.addWidget(self.TaurusLimitSwitch,0,3,1,1)
###
###        self.TaurusLimitSwitch_2 = TaurusLimitSwitch(self)
###        self.TaurusLimitSwitch_2.setUseParentModel(True)
###        self.TaurusLimitSwitch_2.setBoolIndex(1)
###        self.TaurusLimitSwitch_2.setObjectName("TaurusLimitSwitch_2")
###        self.gridlayout.addWidget(self.TaurusLimitSwitch_2,0,4,1,1)
###
###        self.m1PositionLabel_2 = TaurusConfigLabel(self)
###        self.m1PositionLabel_2.setUseParentModel(True)
###        self.m1PositionLabel_2.setObjectName("m1PositionLabel_2")
###        self.gridlayout.addWidget(self.m1PositionLabel_2,1,0,1,2)
###
###        self.m1PositionEdit_2 = TaurusValueLineEdit(self)
###
###        sizePolicy = Qt.QSizePolicy(Qt.QSizePolicy.Fixed,Qt.QSizePolicy.Fixed)
###        sizePolicy.setHorizontalStretch(0)
###        sizePolicy.setVerticalStretch(0)
###        sizePolicy.setHeightForWidth(self.m1PositionEdit_2.sizePolicy().hasHeightForWidth())
###        self.m1PositionEdit_2.setSizePolicy(sizePolicy)
###        self.m1PositionEdit_2.setUseParentModel(True)
###        self.m1PositionEdit_2.setObjectName("m1PositionEdit_2")
###        self.gridlayout.addWidget(self.m1PositionEdit_2,1,2,1,1)
###
###        self.m1Position_2 = TaurusValueLabel(self)
###        self.m1Position_2.setUseParentModel(True)
###        self.m1Position_2.setObjectName("m1Position_2")
###        self.gridlayout.addWidget(self.m1Position_2,1,3,1,2)
###
###        self.m1PositionUnitLabel_2 = TaurusConfigLabel(self)
###
###        sizePolicy = Qt.QSizePolicy(Qt.QSizePolicy.Expanding,Qt.QSizePolicy.Preferred)
###        sizePolicy.setHorizontalStretch(0)
###        sizePolicy.setVerticalStretch(0)
###        sizePolicy.setHeightForWidth(self.m1PositionUnitLabel_2.sizePolicy().hasHeightForWidth())
###        self.m1PositionUnitLabel_2.setSizePolicy(sizePolicy)
###        self.m1PositionUnitLabel_2.setUseParentModel(True)
###        self.m1PositionUnitLabel_2.setObjectName("m1PositionUnitLabel_2")
###        self.gridlayout.addWidget(self.m1PositionUnitLabel_2,1,5,1,1)
###
###        self.m1VelocityLabel_2 = TaurusConfigLabel(self)
###        self.m1VelocityLabel_2.setUseParentModel(True)
###        self.m1VelocityLabel_2.setObjectName("m1VelocityLabel_2")
###        self.gridlayout.addWidget(self.m1VelocityLabel_2,2,0,1,2)
###
###        self.m1VelocityEdit_2 = TaurusValueLineEdit(self)
###
###        sizePolicy = Qt.QSizePolicy(Qt.QSizePolicy.Fixed,Qt.QSizePolicy.Fixed)
###        sizePolicy.setHorizontalStretch(0)
###        sizePolicy.setVerticalStretch(0)
###        sizePolicy.setHeightForWidth(self.m1VelocityEdit_2.sizePolicy().hasHeightForWidth())
###        self.m1VelocityEdit_2.setSizePolicy(sizePolicy)
###        self.m1VelocityEdit_2.setUseParentModel(True)
###        self.m1VelocityEdit_2.setObjectName("m1VelocityEdit_2")
###        self.gridlayout.addWidget(self.m1VelocityEdit_2,2,2,1,1)
###
###        self.m1Velocity_2 = TaurusValueLabel(self)
###        self.m1Velocity_2.setUseParentModel(True)
###        self.m1Velocity_2.setObjectName("m1Velocity_2")
###        self.gridlayout.addWidget(self.m1Velocity_2,2,3,1,2)
###
###        self.m1VelocityUnitLabel_2 = TaurusConfigLabel(self)
###
###        sizePolicy = Qt.QSizePolicy(Qt.QSizePolicy.Expanding,Qt.QSizePolicy.Preferred)
###        sizePolicy.setHorizontalStretch(0)
###        sizePolicy.setVerticalStretch(0)
###        sizePolicy.setHeightForWidth(self.m1VelocityUnitLabel_2.sizePolicy().hasHeightForWidth())
###        self.m1VelocityUnitLabel_2.setSizePolicy(sizePolicy)
###        self.m1VelocityUnitLabel_2.setUseParentModel(True)
###        self.m1VelocityUnitLabel_2.setObjectName("m1VelocityUnitLabel_2")
###        self.gridlayout.addWidget(self.m1VelocityUnitLabel_2,2,5,1,1)
###
###        self.m1PositionLabel_4 = TaurusConfigLabel(self)
###        self.m1PositionLabel_4.setUseParentModel(True)
###        self.m1PositionLabel_4.setObjectName("m1PositionLabel_4")
###        self.gridlayout.addWidget(self.m1PositionLabel_4,3,0,1,2)
###
###        self.m1PositionEdit_4 = TaurusValueLineEdit(self)
###
###        sizePolicy = Qt.QSizePolicy(Qt.QSizePolicy.Fixed,Qt.QSizePolicy.Fixed)
###        sizePolicy.setHorizontalStretch(0)
###        sizePolicy.setVerticalStretch(0)
###        sizePolicy.setHeightForWidth(self.m1PositionEdit_4.sizePolicy().hasHeightForWidth())
###        self.m1PositionEdit_4.setSizePolicy(sizePolicy)
###        self.m1PositionEdit_4.setUseParentModel(True)
###        self.m1PositionEdit_4.setObjectName("m1PositionEdit_4")
###        self.gridlayout.addWidget(self.m1PositionEdit_4,3,2,1,1)
###
###        self.m1Position_4 = TaurusValueLabel(self)
###        self.m1Position_4.setUseParentModel(True)
###        self.m1Position_4.setObjectName("m1Position_4")
###        self.gridlayout.addWidget(self.m1Position_4,3,3,1,2)
###
###        self.m1PositionUnitLabel_4 = TaurusConfigLabel(self)
###
###        sizePolicy = Qt.QSizePolicy(Qt.QSizePolicy.Expanding,Qt.QSizePolicy.Preferred)
###        sizePolicy.setHorizontalStretch(0)
###        sizePolicy.setVerticalStretch(0)
###        sizePolicy.setHeightForWidth(self.m1PositionUnitLabel_4.sizePolicy().hasHeightForWidth())
###        self.m1PositionUnitLabel_4.setSizePolicy(sizePolicy)
###        self.m1PositionUnitLabel_4.setUseParentModel(True)
###        self.m1PositionUnitLabel_4.setObjectName("m1PositionUnitLabel_4")
###        self.gridlayout.addWidget(self.m1PositionUnitLabel_4,3,5,1,1)
###
###        self.m1AccelerationLabel_2 = TaurusConfigLabel(self)
###        self.m1AccelerationLabel_2.setUseParentModel(True)
###        self.m1AccelerationLabel_2.setObjectName("m1AccelerationLabel_2")
###        self.gridlayout.addWidget(self.m1AccelerationLabel_2,4,0,1,2)
###
###        self.m1AccelerationEdit_2 = TaurusValueLineEdit(self)
###
###        sizePolicy = Qt.QSizePolicy(Qt.QSizePolicy.Fixed,Qt.QSizePolicy.Fixed)
###        sizePolicy.setHorizontalStretch(0)
###        sizePolicy.setVerticalStretch(0)
###        sizePolicy.setHeightForWidth(self.m1AccelerationEdit_2.sizePolicy().hasHeightForWidth())
###        self.m1AccelerationEdit_2.setSizePolicy(sizePolicy)
###        self.m1AccelerationEdit_2.setUseParentModel(True)
###        self.m1AccelerationEdit_2.setObjectName("m1AccelerationEdit_2")
###        self.gridlayout.addWidget(self.m1AccelerationEdit_2,4,2,1,1)
###
###        self.m1Acceleration_2 = TaurusValueLabel(self)
###        self.m1Acceleration_2.setUseParentModel(True)
###        self.m1Acceleration_2.setObjectName("m1Acceleration_2")
###        self.gridlayout.addWidget(self.m1Acceleration_2,4,3,1,2)
###
###        self.m1AccelerationUnitLabel_2 = TaurusConfigLabel(self)
###
###        sizePolicy = Qt.QSizePolicy(Qt.QSizePolicy.Expanding,Qt.QSizePolicy.Preferred)
###        sizePolicy.setHorizontalStretch(0)
###        sizePolicy.setVerticalStretch(0)
###        sizePolicy.setHeightForWidth(self.m1AccelerationUnitLabel_2.sizePolicy().hasHeightForWidth())
###        self.m1AccelerationUnitLabel_2.setSizePolicy(sizePolicy)
###        self.m1AccelerationUnitLabel_2.setUseParentModel(True)
###        self.m1AccelerationUnitLabel_2.setObjectName("m1AccelerationUnitLabel_2")
###        self.gridlayout.addWidget(self.m1AccelerationUnitLabel_2,4,5,1,1)
###
###        self.m1PositionLabel_5 = TaurusConfigLabel(self)
###        self.m1PositionLabel_5.setUseParentModel(True)
###        self.m1PositionLabel_5.setObjectName("m1PositionLabel_5")
###        self.gridlayout.addWidget(self.m1PositionLabel_5,5,0,1,2)
###
###        self.m1PositionEdit_5 = TaurusValueLineEdit(self)
###
###        sizePolicy = Qt.QSizePolicy(Qt.QSizePolicy.Fixed,Qt.QSizePolicy.Fixed)
###        sizePolicy.setHorizontalStretch(0)
###        sizePolicy.setVerticalStretch(0)
###        sizePolicy.setHeightForWidth(self.m1PositionEdit_5.sizePolicy().hasHeightForWidth())
###        self.m1PositionEdit_5.setSizePolicy(sizePolicy)
###        self.m1PositionEdit_5.setUseParentModel(True)
###        self.m1PositionEdit_5.setObjectName("m1PositionEdit_5")
###        self.gridlayout.addWidget(self.m1PositionEdit_5,5,2,1,1)
###
###        self.m1Position_5 = TaurusValueLabel(self)
###        self.m1Position_5.setUseParentModel(True)
###        self.m1Position_5.setObjectName("m1Position_5")
###        self.gridlayout.addWidget(self.m1Position_5,5,3,1,2)
###
###        self.m1PositionUnitLabel_5 = TaurusConfigLabel(self)
###
###        sizePolicy = Qt.QSizePolicy(Qt.QSizePolicy.Expanding,Qt.QSizePolicy.Preferred)
###        sizePolicy.setHorizontalStretch(0)
###        sizePolicy.setVerticalStretch(0)
###        sizePolicy.setHeightForWidth(self.m1PositionUnitLabel_5.sizePolicy().hasHeightForWidth())
###        self.m1PositionUnitLabel_5.setSizePolicy(sizePolicy)
###        self.m1PositionUnitLabel_5.setUseParentModel(True)
###        self.m1PositionUnitLabel_5.setObjectName("m1PositionUnitLabel_5")
###        self.gridlayout.addWidget(self.m1PositionUnitLabel_5,5,5,1,1)
###
###        self.m1DecelerationLabel_2 = TaurusConfigLabel(self)
###        self.m1DecelerationLabel_2.setUseParentModel(True)
###        self.m1DecelerationLabel_2.setObjectName("m1DecelerationLabel_2")
###        self.gridlayout.addWidget(self.m1DecelerationLabel_2,6,0,1,2)
###
###        self.m1DecelerationEdit_2 = TaurusValueLineEdit(self)
###
###        sizePolicy = Qt.QSizePolicy(Qt.QSizePolicy.Fixed,Qt.QSizePolicy.Fixed)
###        sizePolicy.setHorizontalStretch(0)
###        sizePolicy.setVerticalStretch(0)
###        sizePolicy.setHeightForWidth(self.m1DecelerationEdit_2.sizePolicy().hasHeightForWidth())
###        self.m1DecelerationEdit_2.setSizePolicy(sizePolicy)
###        self.m1DecelerationEdit_2.setUseParentModel(True)
###        self.m1DecelerationEdit_2.setObjectName("m1DecelerationEdit_2")
###        self.gridlayout.addWidget(self.m1DecelerationEdit_2,6,2,1,1)
###
###        self.m1Deceleration_2 = TaurusValueLabel(self)
###        self.m1Deceleration_2.setUseParentModel(True)
###        self.m1Deceleration_2.setObjectName("m1Deceleration_2")
###        self.gridlayout.addWidget(self.m1Deceleration_2,6,3,1,2)
###
###        self.m1DecelerationUnitLabel_2 = TaurusConfigLabel(self)
###
###        sizePolicy = Qt.QSizePolicy(Qt.QSizePolicy.Expanding,Qt.QSizePolicy.Preferred)
###        sizePolicy.setHorizontalStretch(0)
###        sizePolicy.setVerticalStretch(0)
###        sizePolicy.setHeightForWidth(self.m1DecelerationUnitLabel_2.sizePolicy().hasHeightForWidth())
###        self.m1DecelerationUnitLabel_2.setSizePolicy(sizePolicy)
###        self.m1DecelerationUnitLabel_2.setUseParentModel(True)
###        self.m1DecelerationUnitLabel_2.setObjectName("m1DecelerationUnitLabel_2")
###        self.gridlayout.addWidget(self.m1DecelerationUnitLabel_2,6,5,1,1)
###
###        self.m1PositionLabel_6 = TaurusConfigLabel(self)
###        self.m1PositionLabel_6.setUseParentModel(True)
###        self.m1PositionLabel_6.setObjectName("m1PositionLabel_6")
###        self.gridlayout.addWidget(self.m1PositionLabel_6,7,0,1,2)
###
###        self.m1PositionEdit_6 = TaurusValueLineEdit(self)
###
###        sizePolicy = Qt.QSizePolicy(Qt.QSizePolicy.Fixed,Qt.QSizePolicy.Fixed)
###        sizePolicy.setHorizontalStretch(0)
###        sizePolicy.setVerticalStretch(0)
###        sizePolicy.setHeightForWidth(self.m1PositionEdit_6.sizePolicy().hasHeightForWidth())
###        self.m1PositionEdit_6.setSizePolicy(sizePolicy)
###        self.m1PositionEdit_6.setUseParentModel(True)
###        self.m1PositionEdit_6.setObjectName("m1PositionEdit_6")
###        self.gridlayout.addWidget(self.m1PositionEdit_6,7,2,1,1)
###
###        self.m1Position_6 = TaurusValueLabel(self)
###        self.m1Position_6.setUseParentModel(True)
###        self.m1Position_6.setObjectName("m1Position_6")
###        self.gridlayout.addWidget(self.m1Position_6,7,3,1,2)
###
###        self.m1PositionUnitLabel_6 = TaurusConfigLabel(self)
###
###        sizePolicy = Qt.QSizePolicy(Qt.QSizePolicy.Expanding,Qt.QSizePolicy.Preferred)
###        sizePolicy.setHorizontalStretch(0)
###        sizePolicy.setVerticalStretch(0)
###        sizePolicy.setHeightForWidth(self.m1PositionUnitLabel_6.sizePolicy().hasHeightForWidth())
###        self.m1PositionUnitLabel_6.setSizePolicy(sizePolicy)
###        self.m1PositionUnitLabel_6.setUseParentModel(True)
###        self.m1PositionUnitLabel_6.setObjectName("m1PositionUnitLabel_6")
###        self.gridlayout.addWidget(self.m1PositionUnitLabel_6,7,5,1,1)
###
###        self.m1StepPerUnitLabel_2 = TaurusConfigLabel(self)
###        self.m1StepPerUnitLabel_2.setUseParentModel(True)
###        self.m1StepPerUnitLabel_2.setObjectName("m1StepPerUnitLabel_2")
###        self.gridlayout.addWidget(self.m1StepPerUnitLabel_2,8,0,1,2)
###
###        self.m1StepPerUnitEdit_2 = TaurusValueLineEdit(self)
###
###        sizePolicy = Qt.QSizePolicy(Qt.QSizePolicy.Fixed,Qt.QSizePolicy.Fixed)
###        sizePolicy.setHorizontalStretch(0)
###        sizePolicy.setVerticalStretch(0)
###        sizePolicy.setHeightForWidth(self.m1StepPerUnitEdit_2.sizePolicy().hasHeightForWidth())
###        self.m1StepPerUnitEdit_2.setSizePolicy(sizePolicy)
###        self.m1StepPerUnitEdit_2.setUseParentModel(True)
###        self.m1StepPerUnitEdit_2.setObjectName("m1StepPerUnitEdit_2")
###        self.gridlayout.addWidget(self.m1StepPerUnitEdit_2,8,2,1,1)
###
###        self.m1StepPerUnit_2 = TaurusValueLabel(self)
###        self.m1StepPerUnit_2.setUseParentModel(True)
###        self.m1StepPerUnit_2.setObjectName("m1StepPerUnit_2")
###        self.gridlayout.addWidget(self.m1StepPerUnit_2,8,3,1,2)
###
###        self.m1StepPerUnitUnitLabel_2 = TaurusConfigLabel(self)
###
###        sizePolicy = Qt.QSizePolicy(Qt.QSizePolicy.Expanding,Qt.QSizePolicy.Preferred)
###        sizePolicy.setHorizontalStretch(0)
###        sizePolicy.setVerticalStretch(0)
###        sizePolicy.setHeightForWidth(self.m1StepPerUnitUnitLabel_2.sizePolicy().hasHeightForWidth())
###        self.m1StepPerUnitUnitLabel_2.setSizePolicy(sizePolicy)
###        self.m1StepPerUnitUnitLabel_2.setUseParentModel(True)
###        self.m1StepPerUnitUnitLabel_2.setObjectName("m1StepPerUnitUnitLabel_2")
###        self.gridlayout.addWidget(self.m1StepPerUnitUnitLabel_2,8,5,1,1)
###
###
###    def retranslateUi(self):
###        self.m1StateLed_2.setModel(Qt.QApplication.translate("Dialog", "/State", None, Qt.QApplication.UnicodeUTF8))
###        self.taurusValueLabel.setModel(Qt.QApplication.translate("Dialog", "/State", None, Qt.QApplication.UnicodeUTF8))
###        self.TaurusLimitSwitch.setLedColor(Qt.QApplication.translate("Dialog", "ORANGE", None, Qt.QApplication.UnicodeUTF8))
###        self.TaurusLimitSwitch.setModel(Qt.QApplication.translate("Dialog", "/Limit_switches", None, Qt.QApplication.UnicodeUTF8))
###        self.TaurusLimitSwitch_2.setLedColor(Qt.QApplication.translate("Dialog", "ORANGE", None, Qt.QApplication.UnicodeUTF8))
###        self.TaurusLimitSwitch_2.setModel(Qt.QApplication.translate("Dialog", "/Limit_switches", None, Qt.QApplication.UnicodeUTF8))
###        self.m1PositionLabel_2.setSuffixText(Qt.QApplication.translate("Dialog", ":", None, Qt.QApplication.UnicodeUTF8))
###        self.m1PositionLabel_2.setModel(Qt.QApplication.translate("Dialog", "/Position?configuration=label", None, Qt.QApplication.UnicodeUTF8))
###        self.m1PositionEdit_2.setModel(Qt.QApplication.translate("Dialog", "/Position", None, Qt.QApplication.UnicodeUTF8))
###        self.m1Position_2.setModel(Qt.QApplication.translate("Dialog", "/Position", None, Qt.QApplication.UnicodeUTF8))
###        self.m1PositionUnitLabel_2.setModel(Qt.QApplication.translate("Dialog", "/Position?configuration=unit", None, Qt.QApplication.UnicodeUTF8))
###        self.m1VelocityLabel_2.setSuffixText(Qt.QApplication.translate("Dialog", ":", None, Qt.QApplication.UnicodeUTF8))
###        self.m1VelocityLabel_2.setModel(Qt.QApplication.translate("Dialog", "/Velocity?configuration=label", None, Qt.QApplication.UnicodeUTF8))
###        self.m1VelocityEdit_2.setModel(Qt.QApplication.translate("Dialog", "/Velocity", None, Qt.QApplication.UnicodeUTF8))
###        self.m1Velocity_2.setModel(Qt.QApplication.translate("Dialog", "/Velocity", None, Qt.QApplication.UnicodeUTF8))
###        self.m1VelocityUnitLabel_2.setModel(Qt.QApplication.translate("Dialog", "/Velocity?configuration=unit", None, Qt.QApplication.UnicodeUTF8))
###        self.m1PositionLabel_4.setSuffixText(Qt.QApplication.translate("Dialog", ":", None, Qt.QApplication.UnicodeUTF8))
###        self.m1PositionLabel_4.setModel(Qt.QApplication.translate("Dialog", "/Acceleration?configuration=label", None, Qt.QApplication.UnicodeUTF8))
###        self.m1PositionEdit_4.setModel(Qt.QApplication.translate("Dialog", "/Acceleration", None, Qt.QApplication.UnicodeUTF8))
###        self.m1Position_4.setModel(Qt.QApplication.translate("Dialog", "/Acceleration", None, Qt.QApplication.UnicodeUTF8))
###        self.m1PositionUnitLabel_4.setModel(Qt.QApplication.translate("Dialog", "/Acceleration?configuration=unit", None, Qt.QApplication.UnicodeUTF8))
###        self.m1AccelerationLabel_2.setSuffixText(Qt.QApplication.translate("Dialog", ":", None, Qt.QApplication.UnicodeUTF8))
###        self.m1AccelerationLabel_2.setModel(Qt.QApplication.translate("Dialog", "/Deceleration?configuration=label", None, Qt.QApplication.UnicodeUTF8))
###        self.m1AccelerationEdit_2.setModel(Qt.QApplication.translate("Dialog", "/Deceleration", None, Qt.QApplication.UnicodeUTF8))
###        self.m1Acceleration_2.setModel(Qt.QApplication.translate("Dialog", "/Deceleration", None, Qt.QApplication.UnicodeUTF8))
###        self.m1AccelerationUnitLabel_2.setModel(Qt.QApplication.translate("Dialog", "/Deceleration?configuration=unit", None, Qt.QApplication.UnicodeUTF8))
###        self.m1PositionLabel_5.setSuffixText(Qt.QApplication.translate("Dialog", ":", None, Qt.QApplication.UnicodeUTF8))
###        self.m1PositionLabel_5.setModel(Qt.QApplication.translate("Dialog", "/Offset?configuration=label", None, Qt.QApplication.UnicodeUTF8))
###        self.m1PositionEdit_5.setModel(Qt.QApplication.translate("Dialog", "/Offset", None, Qt.QApplication.UnicodeUTF8))
###        self.m1Position_5.setModel(Qt.QApplication.translate("Dialog", "/Offset", None, Qt.QApplication.UnicodeUTF8))
###        self.m1PositionUnitLabel_5.setModel(Qt.QApplication.translate("Dialog", "/Offset?configuration=unit", None, Qt.QApplication.UnicodeUTF8))
###        self.m1DecelerationLabel_2.setSuffixText(Qt.QApplication.translate("Dialog", ":", None, Qt.QApplication.UnicodeUTF8))
###        self.m1DecelerationLabel_2.setModel(Qt.QApplication.translate("Dialog", "/Base_rate?configuration=label", None, Qt.QApplication.UnicodeUTF8))
###        self.m1DecelerationEdit_2.setModel(Qt.QApplication.translate("Dialog", "/Base_rate", None, Qt.QApplication.UnicodeUTF8))
###        self.m1Deceleration_2.setModel(Qt.QApplication.translate("Dialog", "/Base_rate", None, Qt.QApplication.UnicodeUTF8))
###        self.m1DecelerationUnitLabel_2.setModel(Qt.QApplication.translate("Dialog", "/Base_rate?configuration=unit", None, Qt.QApplication.UnicodeUTF8))
###        self.m1PositionLabel_6.setSuffixText(Qt.QApplication.translate("Dialog", ":", None, Qt.QApplication.UnicodeUTF8))
###        self.m1PositionLabel_6.setModel(Qt.QApplication.translate("Dialog", "/Step_per_unit?configuration=label", None, Qt.QApplication.UnicodeUTF8))
###        self.m1PositionEdit_6.setModel(Qt.QApplication.translate("Dialog", "/Step_per_unit", None, Qt.QApplication.UnicodeUTF8))
###        self.m1Position_6.setModel(Qt.QApplication.translate("Dialog", "/Step_per_unit", None, Qt.QApplication.UnicodeUTF8))
###        self.m1PositionUnitLabel_6.setModel(Qt.QApplication.translate("Dialog", "/Step_per_unit?configuration=unit", None, Qt.QApplication.UnicodeUTF8))
###        self.m1StepPerUnitLabel_2.setSuffixText(Qt.QApplication.translate("Dialog", ":", None, Qt.QApplication.UnicodeUTF8))
###        self.m1StepPerUnitLabel_2.setModel(Qt.QApplication.translate("Dialog", "/Backlash?configuration=label", None, Qt.QApplication.UnicodeUTF8))
###        self.m1StepPerUnitEdit_2.setModel(Qt.QApplication.translate("Dialog", "/Backlash", None, Qt.QApplication.UnicodeUTF8))
###        self.m1StepPerUnit_2.setModel(Qt.QApplication.translate("Dialog", "/Backlash", None, Qt.QApplication.UnicodeUTF8))
###        self.m1StepPerUnitUnitLabel_2.setModel(Qt.QApplication.translate("Dialog", "/Backlash?configuration=unit", None, Qt.QApplication.UnicodeUTF8))
###
###    ##############################################################################
###    ## VVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV
###    ##
###    ## I CAN NOT INHERIT FROM TAUGROUPBOX !
###    ## SO ALL THE STUFF BELOW IS NECESSARY
###
###
###        
###    def defineStyle(self):
###        palette = Qt.QPalette()
###        self.setPalette(palette)
###        self.updateStyle()
###        
###    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
###    # TaurusBaseWidget over writing
###    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
###                    
###    def getDisplayValue(self):
###        return (self._prefix or '') + TaurusBaseWidget.getDisplayValue(self) + (self._suffix or '')
###    
###    def isReadOnly(self):
###        return True
###    
###    def updateStyle(self):
###        if self.getShowQuality():
###            self.setAutoFillBackground(True)
###            #TODO: get quality/state from model and update accordingly
###        else:
###            self.setAutoFillBackground(False)
###            #TODO: restore colors
###        self.update()
###        
###    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
###    # QT properties 
###    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
###   
###    def getPrefixText(self):
###        return self._prefix
###    
###    @Qt.pyqtSignature("setPrefixText(QString)")
###    def setPrefixText(self,prefix):
###        self._prefix = prefix
###        self.fireValueChanged()
###
###    def getSuffixText(self):
###        return self._suffix
###    
###    @Qt.pyqtSignature("setSuffixText(QString)")
###    def setSuffixText(self,suffix):
###        self._suffix = suffix
###        self.fireValueChanged()
###
###    model = Qt.pyqtProperty("QString", TaurusBaseWidget.getModel, 
###                                TaurusBaseWidget.setModel, TaurusBaseWidget.resetModel)
###    useParentModel = Qt.pyqtProperty("bool", TaurusBaseWidget.getUseParentModel, 
###                                         TaurusBaseWidget.setUseParentModel, 
###                                         TaurusBaseWidget.resetUseParentModel)
###    showQuality = Qt.pyqtProperty("bool", TaurusBaseWidget.getShowQuality, 
###                                      TaurusBaseWidget.setShowQuality, 
###                                      TaurusBaseWidget.resetShowQuality)
###    showText = Qt.pyqtProperty("bool", TaurusBaseWidget.getShowText, 
###                                   TaurusBaseWidget.setShowText, 
###                                   TaurusBaseWidget.resetShowText)
###    prefixText = Qt.pyqtProperty("QString", getPrefixText, setPrefixText, 
###                                     doc="prefix text (optional)")
###    suffixText = Qt.pyqtProperty("QString", getSuffixText, setSuffixText, 
###                                    doc="suffix text (optional)")
###
###        
###

if __name__ == "__main__":
    
    import sys
    app = Qt.QApplication(sys.argv)
    
    form = TaurusMotorH()
    form.setModel(sys.argv[1])
        
    form.show()
    sys.exit(app.exec_())