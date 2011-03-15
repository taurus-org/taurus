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

import sys
import copy
import PyTango
import numpy

from PyQt4 import QtCore, QtGui, Qt

import taurus
import taurus.qt.qtcore.mimetypes
from taurus.qt.qtgui.base import TaurusBaseWidget
from taurus.qt.qtgui.container import TaurusWidget
from taurus.qt.qtgui.display import TaurusConfigLabel
from taurus.qt.qtgui.panel import DefaultLabelWidget
from taurus.qt.qtgui.panel import TaurusValue, TaurusAttrForm
from ui_poolmotorslim import Ui_PoolMotorSlim


class LimitsListener(QtCore.QObject):
    """
    A class that listens to changes on motor limits.
    If that is the case it emits a signal so the application
    can do whatever with it.
    """
    def __init__(self):
        QtCore.QObject.__init__(self)
        
    def eventReceived(self, evt_src, evt_type, evt_value):
        if evt_type not in [taurus.core.TaurusEventType.Change, taurus.core.TaurusEventType.Periodic]:
            return
        limits = evt_value.value
        self.emit(Qt.SIGNAL('updateLimits(PyQt_PyObject)'), limits.tolist())

class PoolMotorClient():

    maxint_in_32_bits = 2147483647
    def __init__(self):
        self.motor_dev = None
        self.has_limits = False
        self.has_encoder = False

    def setMotor(self, pool_motor_dev_name):
        # AT SOME POINT THIS WILL BE USING THE 'POOL' TAURUS EXTENSION
        # TO OPERATE THE MOTOR INSTEAD OF A 'TANGO' TAURUSDEVICE
        try:
            self.motor_dev = taurus.Device(pool_motor_dev_name)
            # IT IS IMPORTANT TO KNOW IF IT IS AN ICEPAP MOTOR, SO EXTRA FEATURES CAN BE PROVIDED
            # PENDING.
            self.has_limits = hasattr(self.motor_dev, 'Limit_Switches')
            self.has_encoder = hasattr(self.motor_dev, 'Encoder')
        except Exception,e:
            print 'EXCEPTION CREATING MOTOR DEVICE...\n'+str(e)
        
    def moveMotor(self, pos):
        #self.motor_dev['position'] = pos
        # Make use of Taurus operations (being logged)
        self.motor_dev.getAttribute('Position').write(pos)
        
    def moveInc(self, inc):
        self.moveMotor(self.motor_dev['position'].value + inc)
        
    def jogNeg(self):
        neg_limit = - ( (self.maxint_in_32_bits / 2) - 1)
        # THERE IS A BUG IN THE ICEPAP THAT DOES NOT ALLOW MOVE ABSOLUTE FURTHER THAN 32 BIT
        # SO IF THERE ARE STEPS PER UNIT, max_int HAS TO BE REDUCED
        if hasattr(self.motor_dev, 'step_per_unit'):
            neg_limit = neg_limit / self.motor_dev['step_per_unit'].value
        try:
            min_value = self.motor_dev.getAttribute('Position').getConfig().getValueObj().min_value
            neg_limit = float(min_value)
        except Exception,e:
            pass
        self.moveMotor(neg_limit)
        
    def jogPos(self):
        pos_limit = (self.maxint_in_32_bits / 2) - 1
        # THERE IS A BUG IN THE ICEPAP THAT DOES NOT ALLOW MOVE ABSOLUTE FURTHER THAN 32 BIT
        # SO IF THERE ARE STEPS PER UNIT, max_int HAS TO BE REDUCED
        if hasattr(self.motor_dev, 'step_per_unit'):
            pos_limit = pos_limit / self.motor_dev['step_per_unit'].value
        try:
            max_value = self.motor_dev.getAttribute('Position').getConfig().getValueObj().max_value
            pos_limit = float(max_value)
        except Exception,e:
            pass
        self.moveMotor(pos_limit)

    def goHome(self):
        pass

    def abort(self):
        self.motor_dev.abort()

class LabelWidgetDragsDeviceAndAttribute(DefaultLabelWidget):
    """ Offer richer mime data with taurus-device, taurus-attribute, and plain-text. """
    def mouseMoveEvent(self, event):
        model = self.taurusValueBuddy.getModelName()
        mimeData = Qt.QMimeData()
        mimeData.setText(self.text())
        attr_name = model
        dev_name = model.rpartition('/')[0]
        mimeData.setData(taurus.qt.qtcore.mimetypes.TAURUS_DEV_MIME_TYPE, dev_name)
        mimeData.setData(taurus.qt.qtcore.mimetypes.TAURUS_ATTR_MIME_TYPE, attr_name)

        drag = Qt.QDrag(self)
        drag.setMimeData(mimeData)
        drag.setHotSpot(event.pos() - self.rect().topLeft())
        dropAction = drag.start(Qt.Qt.CopyAction)
        
class PoolMotorConfigurationForm(TaurusAttrForm):
    
    def __init__(self, parent=None, designMode=False):
        TaurusAttrForm.__init__(self, parent, designMode)
        self._form.setWithButtons(False)
        
    def getMotorControllerType(self):
        modelObj = self.getModelObj()
        modelNormalName = modelObj.getNormalName()
        poolDsId = modelObj.getHWObj().info().server_id
        db = taurus.Database()
        pool_devices = tuple(db.get_device_class_list(poolDsId).value_string)
        pool_dev_name = pool_devices[pool_devices.index('Pool') - 1]
        pool = taurus.Device(pool_dev_name)
        poolMotorInfos = pool["MotorList"].value
        for motorInfo in poolMotorInfos:
            # BE CAREFUL, THIS ONLY WORKS IF NOBODY CHANGES THE DEVICE NAME OF A MOTOR!!!
            # ALSO THERE COULD BE A CASE PROBLEM, BETTER DO COMPARISONS WITH .lower()
            #to better understand following actions
            #this is an example of one motor info record
            #'dummymotor10 (motor/dummymotorctrl/10) (dummymotorctrl/10) Motor',
            motorInfos = motorInfo.split()
            if modelNormalName.lower() == motorInfos[1][1:-1].lower():
                controllerName = motorInfos[2][1:-1].split("/")[0]
        
        poolControllerInfos = pool["ControllerList"].value
        for controllerInfo in poolControllerInfos:
            #to better understand following actions
            #this is an example of one controller info record
            #'dummymotorctrl (DummyMotorController.DummyMotorController/dummymotorctrl) - Motor Python ctrl (DummyMotorController.py)'
            controllerInfos = controllerInfo.split()
            if controllerName.lower() == controllerInfos[0].lower():
                controllerType = controllerInfos[1][1:-1].split("/")[0]
        return controllerType
    
    def getDisplayAttributes(self, controllerType):
        attributes = ['position',
                      'state', 
                      'status', 
                      'velocity', 
                      'acceleration', 
                      'base_rate', 
                      'step_per_unit',
                      'dialposition',
                      'sign', 
                      'offset',  
                      'backlash'] 
        
        if controllerType == "IcePAPCtrl.IcepapController":
            attributes.insert(1,"encoder")
            attributes.extend(['frequency', 
                               'poweron', 
                               'closedloop', 
                               'useencodersource', 
                               'encodersource', 
                               'encodersourceformula', 
                               'statusstopcode', 
                               'statusdisable', 
                               'statusready', 
                               'statuslim-', 
                               'statuslim+', 
                               'statushome'])
            
        elif controllerType == "PmacCtrl.PmacController":
            attributes.extend(["motoractivated", 
                               "negativeendlimitset", 
                               "positiveendlimitset", 
                               "handwheelenabled",
                               "phasedmotor", 
                               "openloopmode", 
                               "runningdefine-timemove", 
                               "integrationmode",
                               "dwellinprogress", 
                               "datablockerror", 
                               "desiredvelocityzero", 
                               "abortdeceleration", 
                               "blockrequest", 
                               "homesearchinprogress", 
                               "assignedtocoordinatesystem",
                               "coordinatesystem", 
                               "amplifierenabled",
                               "stoppedonpositionlimit", 
                               "homecomplete", 
                               "phasingsearcherror", 
                               "triggermove",
                               "integratedfatalfollowingerror", 
                               "i2t_amplifierfaulterror", 
                               "backlashdirectionflag",
                               "amplifierfaulterror", 
                               "fatalfollowingerror", 
                               "warningfollowingerror", 
                               "inposition",
                               "motionprogramrunning"])

        elif controllerType == "TurboPmacCtrl.TurboPmacController":
            attributes.extend(["motoractivated", 
                               "negativeendlimitset", 
                               "positiveendlimitset", 
			       "extendedservoalgorithmenabled"
                               "amplifierenabled",
                               "openloopmode", 
                               "movetimeractive", 
                               "integrationmode",
                               "dwellinprogress", 
                               "datablockerror", 
                               "desiredvelocityzero", 
                               "abortdeceleration", 
                               "blockrequest", 
                               "homesearchinprogress", 
                               "user-writtenphaseenable",
                               "user-writtenservoenable", 
                               "alternatesource/destination",
                               "phasedmotor",
                               "followingoffsetmode",
                               "followingenabled",
                               "errortriger",
                               "softwarepositioncapture",
                               "integratorinvelocityloop",
                               "alternatecommand-outputmode",
                               "coordinatesystem",
                               "coordinatedefinition",
                               "assignedtocoordinatesystem",
                               "foregroundinposition",
                               "stoppedondesiredpositionlimit",
                               "stoppedonpositionlimit", 
                               "homecomplete", 
                               "phasing_search/read_active", 
                               "triggermove",
                               "integratedfatalfollowingerror", 
                               "i2t_amplifierfaulterror", 
                               "backlashdirectionflag",
                               "amplifierfaulterror", 
                               "fatalfollowingerror", 
                               "warningfollowingerror", 
                               "inposition"])            
        return attributes
            
    def setModel(self, modelName):
        TaurusAttrForm.setModel(self, modelName)
        controllerType = self.getMotorControllerType()
        attributes = self.getDisplayAttributes(controllerType)
        self.setViewFilters([lambda a: a.name.lower() in attributes])
        self.setSortKey(lambda att: attributes.index(att.name.lower()) if att.name.lower() in attributes else 1)
        
class PoolMotorSlim(TaurusWidget, PoolMotorClient):

    __pyqtSignals__ = ("modelChanged(const QString &)",)

    def __init__(self, parent = None, designMode = False):
        TaurusWidget.__init__(self, parent)
        
        #self.call__init__wo_kw(QtGui.QWidget, parent)
        #self.call__init__(TaurusBaseWidget, str(self.objectName()), designMode=designMode)
        PoolMotorClient.__init__(self)
        self.show_context_menu = True
        
        self.setAcceptDrops(True)

        self.ui = Ui_PoolMotorSlim()
        self.ui.setupUi(self)

        # CREATE THE TaurusValue that can not be configured in the Designer
        self.taurus_value = TaurusValue(self.ui.taurusValueContainer)

        # Use a DragDevAndAttributeLabelWidget to provide a richer QMimeData content
        self.taurus_value.setLabelWidgetClass(LabelWidgetDragsDeviceAndAttribute)

        # Make the label to be the device alias
        self.taurus_value.setLabelConfig('dev_alias')

        self.taurus_value_enc = TaurusValue(self.ui.taurusValueContainer)
        self.taurus_value_enc.readWidget().setShowQuality(False)

        # THIS WILL BE DONE IN THE DESIGNER
        # Config Button will launch a PoolMotorConfigurationForm
        taurus_attr_form = PoolMotorConfigurationForm()
        
        taurus_attr_form.setMinimumSize(Qt.QSize(470,800))
        self.ui.btnCfg.setWidget(taurus_attr_form)
        self.ui.btnCfg.setUseParentModel(True)

        # ADD AN EVENT FILTER FOR THE STATUS LABEL IN ORDER TO PROVIDE JUST THE STRING FROM THE CONTROLLER (LAST LINE)
        def just_ctrl_status_line(evt_src, evt_type, evt_value):
            if evt_type not in [taurus.core.TaurusEventType.Change, taurus.core.TaurusEventType.Periodic]:
                return evt_src, evt_type, evt_value
            try:
                status = evt_value.value
                last_line = status.split('\n')[-1]
                new_evt_value = PyTango.DeviceAttribute(evt_value)
                new_evt_value.value = last_line
                return evt_src, evt_type, new_evt_value
            except:
                return evt_src, evt_type, evt_value
        self.ui.lblStatus.insertEventFilter(just_ctrl_status_line)

        # These buttons are just for showing if the limit is active or not
        self.ui.btnMin.setEnabled(False)
        self.ui.btnMax.setEnabled(False)

        # HOMING NOT IMPLMENTED YET
        self.ui.btnHome.setEnabled(False)

        # DEFAULT VISIBLE COMPONENTS
        self.toggleHideAll()
        self.toggleMoveAbsolute(True)
        self.toggleStopMove(True)

        #################################################################################################################
        ################
        # SET TAURUS ICONS 
        ################
        self.ui.btnMin.setText('')
        self.ui.btnMin.setIcon(taurus.qt.qtgui.resource.getIcon(':/actions/list-remove.svg'))
        self.ui.btnMax.setText('')
        self.ui.btnMax.setIcon(taurus.qt.qtgui.resource.getIcon(':/actions/list-add.svg'))
        
        self.ui.btnGoToNeg.setText('')
        self.ui.btnGoToNeg.setIcon(taurus.qt.qtgui.resource.getIcon(':/actions/media_skip_backward.svg'))
        self.ui.btnGoToNegPress.setText('')
        self.ui.btnGoToNegPress.setIcon(taurus.qt.qtgui.resource.getIcon(':/actions/media_seek_backward.svg'))
        self.ui.btnGoToNegInc.setText('')
        self.ui.btnGoToNegInc.setIcon(taurus.qt.qtgui.resource.getIcon(':/actions/media_playback_backward.svg'))
        self.ui.btnGoToPos.setText('')
        self.ui.btnGoToPos.setIcon(taurus.qt.qtgui.resource.getIcon(':/actions/media_skip_forward.svg'))
        self.ui.btnGoToPosPress.setText('')
        self.ui.btnGoToPosPress.setIcon(taurus.qt.qtgui.resource.getIcon(':/actions/media_seek_forward.svg'))
        self.ui.btnGoToPosInc.setText('')
        self.ui.btnGoToPosInc.setIcon(taurus.qt.qtgui.resource.getIcon(':/actions/media_playback_start.svg'))
        self.ui.btnStop.setText('')
        self.ui.btnStop.setIcon(taurus.qt.qtgui.resource.getIcon(':/actions/media_playback_stop.svg'))
        self.ui.btnHome.setText('')
        self.ui.btnHome.setIcon(taurus.qt.qtgui.resource.getIcon(':/actions/go-home.svg'))
        self.ui.btnCfg.setText('')
        self.ui.btnCfg.setIcon(taurus.qt.qtgui.resource.getIcon(':/categories/preferences-system.svg'))
        #################################################################################################################
        

        self.ui.motorGroupBox.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.connect(self.ui.motorGroupBox, QtCore.SIGNAL('customContextMenuRequested(QPoint)'), self.buildContextMenu)
        
        self.connect(self.ui.btnGoToNeg, QtCore.SIGNAL('clicked()'), self.jogNeg)
        self.connect(self.ui.btnGoToNegPress, QtCore.SIGNAL('pressed()'), self.jogNeg)
        self.connect(self.ui.btnGoToNegPress, QtCore.SIGNAL('released()'), self.abort)
        self.connect(self.ui.btnGoToNegInc, QtCore.SIGNAL('clicked()'), self.goToNegInc)
        self.connect(self.ui.btnGoToPos, QtCore.SIGNAL('clicked()'), self.jogPos)
        self.connect(self.ui.btnGoToPosPress, QtCore.SIGNAL('pressed()'), self.jogPos)
        self.connect(self.ui.btnGoToPosPress, QtCore.SIGNAL('released()'), self.abort)
        self.connect(self.ui.btnGoToPosInc, QtCore.SIGNAL('clicked()'), self.goToPosInc)

        self.connect(self.ui.btnHome, QtCore.SIGNAL('clicked()'), self.goHome)
        self.connect(self.ui.btnStop, QtCore.SIGNAL('clicked()'), self.abort)

        # ALSO UPDATE THE WIDGETS EVERYTIME THE FORM HAS TO BE SHOWN
        self.connect(self.ui.btnCfg, QtCore.SIGNAL('clicked()'), taurus_attr_form._updateAttrWidgets)
        self.connect(self.ui.btnCfg, QtCore.SIGNAL('clicked()'), self.buildBetterCfgDialogTitle)

        #################################################################################################################
        ########################################
        # LET TAURUS CONFIGURATION MECANISM SHINE!
        ########################################
        self.registerConfigProperty(self.ui.inc.isVisible, self.toggleMoveRelative, 'MoveRelative')
        self.registerConfigProperty(self.ui.btnGoToNegPress.isVisible, self.toggleMoveContinuous, 'MoveContinuous')
        self.registerConfigProperty(self.ui.btnGoToNeg.isVisible, self.toggleMoveToLimits, 'MoveToLimits')
        self.registerConfigProperty(self.ui.btnStop.isVisible, self.toggleStopMove, 'StopMove')
        self.registerConfigProperty(self.ui.btnHome.isVisible, self.toggleHoming, 'Homing')
        self.registerConfigProperty(self.ui.btnCfg.isVisible, self.toggleConfig, 'Config')
        self.registerConfigProperty(self.ui.lblStatus.isVisible, self.toggleStatus, 'Status')
        #################################################################################################################

    #@Qt.pyqtSlot(list)
    def updateLimits(self, limits):
        if isinstance(limits, dict): limits = limits["limits"]
        pos_lim = limits[1]
        pos_btnstylesheet = ''
        enabled = True
        if pos_lim:
            pos_btnstylesheet = 'QPushButton{%s}'%taurus.core.util.DEVICE_STATE_PALETTE.qtStyleSheet(PyTango.DevState.ALARM)
            enabled = False
        self.ui.btnMax.setStyleSheet(pos_btnstylesheet)
        self.ui.btnGoToPos.setEnabled(enabled)
        self.ui.btnGoToPosPress.setEnabled(enabled)
        self.ui.btnGoToPosInc.setEnabled(enabled)
        
        
        neg_lim = limits[2]
        neg_btnstylesheet = ''
        enabled = True
        if neg_lim:
            neg_btnstylesheet = 'QPushButton{%s}'%taurus.core.util.DEVICE_STATE_PALETTE.qtStyleSheet(PyTango.DevState.ALARM)
            enabled = False
        self.ui.btnMin.setStyleSheet(neg_btnstylesheet)
        self.ui.btnGoToNeg.setEnabled(enabled)
        self.ui.btnGoToNegPress.setEnabled(enabled)
        self.ui.btnGoToNegInc.setEnabled(enabled)

    #def sizeHint(self):
    #    return QtCore.QSize(300,30)

    def goToNegInc(self):
        self.moveInc(-1 * self.ui.inc.value())
        
    def goToPosInc(self):
        self.moveInc(self.ui.inc.value())
        
    def buildContextMenu(self, point):
        if not self.show_context_menu:
            return
        menu = Qt.QMenu(self)

        action_hide_all = Qt.QAction(self)
        action_hide_all.setText('Hide All')
        menu.addAction(action_hide_all)

        action_show_all = Qt.QAction(self)
        action_show_all.setText('Show All')
        menu.addAction(action_show_all)

        action_move_absolute = Qt.QAction(self)
        action_move_absolute.setText('Move Absolute')
        action_move_absolute.setCheckable(True)
        action_move_absolute.setChecked(self.taurus_value.writeWidget().isVisible())
        menu.addAction(action_move_absolute)

        action_move_relative = Qt.QAction(self)
        action_move_relative.setText('Move Relative')
        action_move_relative.setCheckable(True)
        action_move_relative.setChecked(self.ui.inc.isVisible())
        menu.addAction(action_move_relative)

        action_move_continuous = Qt.QAction(self)
        action_move_continuous.setText('Move Continuous')
        action_move_continuous.setCheckable(True)
        action_move_continuous.setChecked(self.ui.btnGoToNegPress.isVisible())
        menu.addAction(action_move_continuous)

        action_move_to_limits = Qt.QAction(self)
        action_move_to_limits.setText('Move to Limits')
        action_move_to_limits.setCheckable(True)
        action_move_to_limits.setChecked(self.ui.btnGoToNeg.isVisible())
        menu.addAction(action_move_to_limits)

        action_encoder = Qt.QAction(self)
        action_encoder.setText('Encoder Read')
        action_encoder.setCheckable(True)
        action_encoder.setChecked(self.taurus_value_enc.labelWidget().isVisible())
        if self.has_encoder:
            menu.addAction(action_encoder)

        action_stop_move = Qt.QAction(self)
        action_stop_move.setText('Stop Movement')
        action_stop_move.setCheckable(True)
        action_stop_move.setChecked(self.ui.btnStop.isVisible())
        menu.addAction(action_stop_move)

        action_homing = Qt.QAction(self)
        action_homing.setText('Homing')
        action_homing.setCheckable(True)
        action_homing.setChecked(self.ui.btnHome.isVisible())
        menu.addAction(action_homing)
        
        action_config = Qt.QAction(self)
        action_config.setText('Config')
        action_config.setCheckable(True)
        action_config.setChecked(self.ui.btnCfg.isVisible())
        menu.addAction(action_config)
        
        action_status = Qt.QAction(self)
        action_status.setText('Status')
        action_status.setCheckable(True)
        action_status.setChecked(self.ui.lblStatus.isVisible())
        menu.addAction(action_status)
        
        self.connect(action_hide_all, QtCore.SIGNAL('triggered()'), self.toggleHideAll)
        self.connect(action_show_all, QtCore.SIGNAL('triggered()'), self.toggleShowAll)
        self.connect(action_move_absolute, QtCore.SIGNAL('toggled(bool)'), self.toggleMoveAbsolute)
        self.connect(action_move_relative, QtCore.SIGNAL('toggled(bool)'), self.toggleMoveRelative)
        self.connect(action_move_continuous, QtCore.SIGNAL('toggled(bool)'), self.toggleMoveContinuous)
        self.connect(action_move_to_limits, QtCore.SIGNAL('toggled(bool)'), self.toggleMoveToLimits)
        self.connect(action_encoder, QtCore.SIGNAL('toggled(bool)'), self.toggleEncoder)
        self.connect(action_stop_move, QtCore.SIGNAL('toggled(bool)'), self.toggleStopMove)
        self.connect(action_homing, QtCore.SIGNAL('toggled(bool)'), self.toggleHoming)
        self.connect(action_config, QtCore.SIGNAL('toggled(bool)'), self.toggleConfig)
        self.connect(action_status, QtCore.SIGNAL('toggled(bool)'), self.toggleStatus)
        
        menu.popup(self.cursor().pos())

    def toggleHideAll(self):
        self.toggleAll(False)

    def toggleShowAll(self):
        self.toggleAll(True)

    def toggleAll(self, visible):
        self.toggleMoveAbsolute(visible)
        self.toggleMoveRelative(visible)
        self.toggleMoveContinuous(visible)
        self.toggleMoveToLimits(visible)
        self.toggleEncoder(visible)
        self.toggleStopMove(visible)
        self.toggleHoming(visible)
        self.toggleConfig(visible)
        self.toggleStatus(visible)

    def toggleMoveAbsolute(self, visible):
        if self.taurus_value.writeWidget() is not None:
            self.taurus_value.writeWidget().setVisible(visible)

    def toggleMoveRelative(self, visible):
        self.ui.btnGoToNegInc.setVisible(visible)
        self.ui.inc.setVisible(visible)
        self.ui.btnGoToPosInc.setVisible(visible)

    def toggleMoveContinuous(self, visible):
        self.ui.btnGoToNegPress.setVisible(visible)
        self.ui.btnGoToPosPress.setVisible(visible)

    def toggleMoveToLimits(self, visible):
        self.ui.btnGoToNeg.setVisible(visible)
        self.ui.btnGoToPos.setVisible(visible)

    def toggleEncoder(self, visible):
        if self.has_encoder and visible:
            self.taurus_value_enc.setModel(self.motor_dev.getSimpleName()+'/Encoder')
        else:
            # NOT SURE ENOUGH THAT THIS IS SAFE
            self.taurus_value_enc.destroy()

    def toggleStopMove(self, visible):
        self.ui.btnStop.setVisible(visible)

    def toggleHoming(self, visible):
        self.ui.btnHome.setVisible(visible)

    def toggleConfig(self, visible):
        self.ui.btnCfg.setVisible(visible)

    def toggleStatus(self, visible):
        self.ui.lblStatus.setVisible(visible)

    def dragEnterEvent(self, event):
        event.accept()
        
    def dropEvent(self, event):
        mimeData = event.mimeData()
        if mimeData.hasFormat(taurus.qt.qtcore.mimetypes.TAURUS_DEV_MIME_TYPE):
            model = str(mimeData.data(taurus.qt.qtcore.mimetypes.TAURUS_DEV_MIME_TYPE))
        elif mimeData.hasFormat(taurus.qt.qtcore.mimetypes.TAURUS_ATTR_MIME_TYPE):
            model = str(mimeData.data(taurus.qt.qtcore.mimetypes.TAURUS_ATTR_MIME_TYPE))
        else:
            model = str(mimeData.text())
        self.setModel(model)

    def keyPressEvent(self, key_event):
        if key_event.key() == Qt.Qt.Key_Escape:
            self.abort()
            key_event.accept()
        TaurusWidget.keyPressEvent(self, key_event)

    def buildBetterCfgDialogTitle(self):
        while self.ui.btnCfg._dialog is None:
            pass
        model = self.getModel()
        self.ui.btnCfg._dialog.setWindowTitle('%s config'%taurus.Factory().getDevice(model).getSimpleName())

    @classmethod
    def getQtDesignerPluginInfo(cls):
        ret = TaurusBaseWidget.getQtDesignerPluginInfo()
        ret['module'] = 'taurus.qt.qtgui.extra_pool'
        ret['group'] = 'Taurus Extra Sardana'
        ret['icon'] = ':/designer/extra_pool.png'
        ret['container'] = False
        return ret
    
    def showEvent(self, event):
        TaurusWidget.showEvent(self, event)
        self.motor_dev.getAttribute('Position').enablePolling(force=True)

    def hideEvent(self, event):
        TaurusWidget.hideEvent(self, event)
        self.motor_dev.getAttribute('Position').disablePolling()

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # QT properties 
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    @QtCore.pyqtSignature("getModel()")
    def getModel(self):
        return self.ui.motorGroupBox.getModel()

    @QtCore.pyqtSignature("setModel(QString)")
    def setModel(self, model):
        # DUE TO A BUG IN TAUGROUPBOX, WE NEED THE FULL MODEL NAME
        try:
            # In case the model is an attribute of a motor, get the device name
            if not taurus.core.DeviceNameValidator().isValid(model):
                model = model.rpartition('/')[0]
            model = taurus.Factory().getDevice(model).getFullName()
            self.setMotor(model)
            self.ui.motorGroupBox.setModel(model)
            self.ui.motorGroupBox.setEnabled(True)
            
            self.taurus_value.setModel(model+'/Position')

            # DUE TO A BUG IN TAURUSVALUE, THAT DO NOT USE PARENT MODEL WE NEED TO ALWAYS SET THE MODEL
            self.taurus_value.setUseParentModel(False)

            # THE FORCED APPLY HAS TO BE DONE AFTER THE MODEL IS SET, SO THE WRITEWIDGET IS AVAILABLE
            if self.taurus_value.writeWidget() is not None:
                self.taurus_value.writeWidget().setForcedApply(True)
            
            show_enc = self.taurus_value_enc.isVisible()
            if self.has_encoder:
                self.taurus_value_enc.setModel(model+'/Encoder')
                self.taurus_value_enc.setUseParentModel(False)
            else:
                self.taurus_value_enc.setModel(None)
                show_enc = False
            if not show_enc:
                self.toggleEncoder(False)

            try:
                self.unregisterConfigurableItem('MoveAbsolute')
                self.unregisterConfigurableItem('Encoder')
            except:
                pass
            self.registerConfigProperty(self.taurus_value.writeWidget().isVisible, self.toggleMoveAbsolute, 'MoveAbsolute')
            self.registerConfigProperty(self.taurus_value_enc.labelWidget().isVisible, self.toggleEncoder, 'Encoder')

            
            # SINCE TAURUSLAUNCHERBUTTON HAS NOT THIS PROPERTY IN THE
            # DESIGNER, WE MUST SET IT HERE
            self.ui.btnCfg.setUseParentModel(True)
            
            # CONFIGURE A LISTENER IN ORDER TO UPDATE LIMIT SWITCHES STATES
            self.limits_listener = LimitsListener()
            self.connect(self.limits_listener, QtCore.SIGNAL('updateLimits(PyQt_PyObject)'), self.updateLimits)
            limits_visible = False
            if self.has_limits:
                limits_attribute = self.motor_dev.getAttribute('Limit_switches')
                limits_attribute.addListener(self.limits_listener)
                #self.updateLimits(limits_attribute.read().value)
                limits_visible = True
            self.ui.btnMin.setVisible(limits_visible)
            self.ui.btnMax.setVisible(limits_visible)
        except Exception,e:
            self.ui.motorGroupBox.setEnabled(False)
            print 'Some exception while setting model',model
            print 'Exception was:',e
        
    @QtCore.pyqtSignature("resetModel()")
    def resetModel(self):
        self.ui.motorGroupBox.resetModel()

    @QtCore.pyqtSignature("getShowContextMenu()")
    def getShowContextMenu(self):
        return self.show_context_menu

    @QtCore.pyqtSignature("setShowContextMenu(bool)")
    def setShowContextMenu(self, showContextMenu):
        self.show_context_menu = showContextMenu

    @QtCore.pyqtSignature("resetShowContextMenu()")
    def resetShowContextMenu(self):
        self.show_context_menu = True

    @QtCore.pyqtSignature("getStepSize()")
    def getStepSize(self):
        return self.ui.inc.value()

    @QtCore.pyqtSignature("setStepSize(double)")
    def setStepSize(self, stepSize):
        self.ui.inc.setValue(stepSize)

    @QtCore.pyqtSignature("resetStepSize()")
    def resetStepSize(self):
        self.setStepSize(1)

    @QtCore.pyqtSignature("getStepSizeIncrement()")
    def getStepSizeIncrement(self):
        return self.ui.inc.singleStep()

    @QtCore.pyqtSignature("setStepSizeIncrement(double)")
    def setStepSizeIncrement(self, stepSizeIncrement):
        self.ui.inc.setSingleStep(stepSizeIncrement)

    @QtCore.pyqtSignature("resetStepSizeIncrement()")
    def resetStepSizeIncrement(self):
        self.setStepSizeIncrement(1)

    model = QtCore.pyqtProperty("QString", getModel,setModel,resetModel)
    stepSize = QtCore.pyqtProperty("double", getStepSize,setStepSize,resetStepSize)
    stepSizeIncrement = QtCore.pyqtProperty("double", getStepSizeIncrement,setStepSizeIncrement,resetStepSizeIncrement)


def main():
    
    import sys
    import taurus.qt.qtgui.application
    import taurus.core.util.argparse
    
    parser = taurus.core.util.argparse.get_taurus_parser()
    parser.usage = "%prog [options] [<motor1> [<motor2>] ...]"
       
    app = taurus.qt.qtgui.application.TaurusApplication(cmd_line_parser=parser)
    args = app.get_command_line_args()
    
    qw = QtGui.QWidget()
    qw.setLayout(QtGui.QVBoxLayout())

    motors = ['tango://controls02:10000/motor/gc_ipap_ctrl/8']
    if len(args)>0:
        motors = args
    
    for motor in motors:
        pms = PoolMotorSlim()
        pms.setStepSize(1)
        pms.setStepSizeIncrement(1)
        pms.setModel(motor)
        qw.layout().addWidget(pms)
     
    qw.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
