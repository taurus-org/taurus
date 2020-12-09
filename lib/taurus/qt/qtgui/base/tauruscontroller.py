#!/usr/bin/env python
# -*- coding: utf-8 -*-

#############################################################################
##
# This file is part of Taurus
##
# http://taurus-scada.org
##
# Copyright 2011 CELLS / ALBA Synchrotron, Bellaterra, Spain
##
# Taurus is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
##
# Taurus is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
##
# You should have received a copy of the GNU Lesser General Public License
# along with Taurus.  If not, see <http://www.gnu.org/licenses/>.
##
#############################################################################

"""This module provides the set of base class taurus controllers."""

from builtins import str
from builtins import object

import weakref

from taurus.external.qt import Qt

from taurus.core.taurusbasetypes import DataFormat, TaurusEventType

from taurus.qt.qtgui.util import QT_ATTRIBUTE_QUALITY_PALETTE
from taurus.qt.qtgui.util import QT_DEVICE_STATE_PALETTE


__all__ = ["TaurusBaseController", "TaurusAttributeControllerHelper",
           "TaurusScalarAttributeControllerHelper",
           "TaurusConfigurationControllerHelper",
           "updateLabelBackground"]

__docformat__ = 'restructuredtext'


class TaurusBaseController(object):
    """Base class for all taurus controllers"""

    def __init__(self, widget, updateAsPalette=True):
        self._widget = weakref.ref(widget)
        self._updateAsPalette = updateAsPalette
        self._stateObj = None
        self._last_value = None
        self._last_config_value = None
        self._last_error_value = None
        self._setStyle()

    def _setStyle(self):
        pass

    def usePalette(self):
        return self._updateAsPalette

    def widget(self):
        return self._widget()

    def modelObj(self):
        return self.widget().getModelObj()

    attrObj = configObj = deviceObj = modelObj

    def valueObj(self):
        value = self._last_value
        if value is None:
            modelObj = self.modelObj()
            if modelObj is None:
                return None
            value = modelObj.getValueObj()
        return value

    def value(self):
        valueObj = self.valueObj()
        return getattr(valueObj, "value", None)

    def w_value(self):  # TODO: adapt to tep14
        valueObj = self.valueObj()
        return getattr(valueObj, "w_value", None)

    def quality(self):
        valueObj = self.valueObj()
        return getattr(valueObj, "quality", None)

    def state(self):
        return self._stateObj.state

    def getDisplayValue(self, write=False):
        return self.widget().getDisplayValue()

    def handleEvent(self, evt_src, evt_type, evt_value):
        # update the "_last" values only if the event source is the model
        # (it could be the background...)
        if evt_src == self.modelObj():
            if evt_type in (TaurusEventType.Change, TaurusEventType.Periodic):
                if self._last_value is None:
                    # reset the format so that it gets updated by displayValue
                    self.widget().resetFormat()
                self._last_value = evt_value
            elif evt_type == TaurusEventType.Config:  # TODO: adapt to tep14
                self._last_config_value = evt_value
                self.widget().resetFormat()
            else:
                self._last_error_value = evt_value
                # In case of error, modify the last_value as well
                try:
                    self._last_value = self.modelObj().getValueObj()
                except:
                    self._last_value = None
        self.update()

    def eventReceived(self, evt_src, evt_type, evt_value):
        # should handle the state event here. Because this is invoked by a random
        # thread, we pass it to the widget, which will forward to the proper
        # thread

        #@todo: sometimes we get this method called but self.widget() is None. Check why.
        #       For the moment I just protect it by substituting the following line by the ones after it
        #self.widget().eventReceived(evt_src, evt_type, evt_value)
        w = self.widget()
        if w is not None:
            w.eventReceived(evt_src, evt_type, evt_value)

    def update(self):
        widget = self.widget()
        self._updateConnections(widget)
        self._updateForeground(widget)
        self._updateBackground(widget)
        self._updateToolTip(widget)

    def _needsStateConnection(self):
        return False

    def _updateConnections(self, widget):
        stateObj, newStateObj = self._stateObj, None
        if self._needsStateConnection():
            newStateObj = self.deviceObj()
            if stateObj != newStateObj:
                if stateObj is not None:
                    stateObj.removeListener(self)
                if newStateObj is not None:
                    newStateObj.addListener(self)
        else:
            if stateObj is not None:
                stateObj.removeListener(self)
        self._stateObj = newStateObj

    def _updateForeground(self, widget):
        pass

    def _updateBackground(self, widget):
        pass

    def _updateToolTip(self, widget):
        if widget.getAutoTooltip():
            widget.setToolTip(widget.getFormatedToolTip())


class TaurusAttributeControllerHelper(object):

    def configObj(self):
        return self.attrObj()  # they are the same object since tep14
        # attrObj = self.attrObj()
        # if attrObj is None: return None
        # return attrObj.getConfig()

    def deviceObj(self):
        attrObj = self.attrObj()
        if attrObj is None:
            return None
        return attrObj.getParentObj()


class TaurusScalarAttributeControllerHelper(TaurusAttributeControllerHelper):

    def getDisplayValue(self, write=False):
        valueObj = self.valueObj()
        widget = self.widget()
        if valueObj is None or valueObj.rvalue is None:
            return widget.getDisplayValue()

        format = self.attrObj().data_format
        if format == DataFormat._0D:
            return self._getDisplayValue(widget, valueObj, None, write)

        idx = widget.getModelIndexValue()
        return self._getDisplayValue(widget, valueObj, idx, write)

    def _getDisplayValue(self, widget, valueObj, idx, write):
        try:
            if write:
                value = valueObj.wvalue
            else:
                value = valueObj.rvalue
            if idx is not None and len(idx):
                for i in idx:
                    value = value[i]
            return widget.displayValue(value)
        except Exception as e:
            return widget.getNoneValue()

    def displayValue(self, value):
        if value is None:
            return None
        ret = None
        try:
            if self.isScalar():
                format = self.getFormat()
                if self.isNumeric() and format is not None:
                    format = self.getFormat()
                    ret = self.getFormat() % value
                else:
                    ret = str(value)
            elif self.isSpectrum():
                ret = str(value)
            else:
                ret = str(value)
        except:
            # if cannot calculate value based on the format just return the
            # value
            raise
            ret = str(value)
        return ret


class TaurusConfigurationControllerHelper(object):
    #TODO: Check if this is  used. If so, rename to avoid "Configuration"

    def __init__(self):
        self._configParam = None

    def attrObj(self):
        return self.configObj()  # they are the same object since tep14

    def deviceObj(self):
        attrObj = self.attrObj()
        if attrObj is None:
            return None
        return attrObj.getParentObj()

    @property
    def configParam(self):
        if self._configParam is None:
            self._configParam = self.widget().modelFragmentName or ''
        return self._configParam

    def getDisplayValue(self, write=False):
        widget = self.widget()
        model = self.configObj()
        if model is None:
            return widget.getNoneValue()
        param = self.configParam
        try:
            val = widget.getModelFragmentObj()
            try:
                no_val = getattr(model, "no_" + param)  # TODO: Tango-centric
                if val.lower() == no_val.lower():
                    val = widget.getNoneValue()
            except:
                pass
        except AttributeError:
            if param:
                val = str(param)
                attr = self.attrObj()
                if attr is not None:
                    val = val.replace('<label>', attr.label or '---')
                    val = val.replace('<attr_name>', attr.name or '---')
                    val = val.replace('<attr_fullname>', attr.getFullName() or
                                      '---')
                dev = self.deviceObj()
                if dev is not None:
                    val = val.replace('<dev_fullname>', dev.getFullName() or
                                      '---')
                    val = val.replace('<dev_alias>', dev.getSimpleName() or
                                      '---')
                    val = val.replace('<dev_name>', dev.getNormalName() or
                                      '---')
            else:
                val = widget.getNoneValue()
        except:
            widget.debug("Invalid configuration parameter '%s'" % param)
            val = widget.getNoneValue()
        if val is None:
            val = widget.getNoneValue()
        return val


StyleSheetTemplate = """border-style: outset; border-width: 2px; border-color: {0}; {1}"""


def _updatePaletteColors(widget, bgBrush, fgBrush, frameBrush):
    qt_palette = widget.palette()
    qt_palette.setBrush(Qt.QPalette.Window, bgBrush)
    qt_palette.setBrush(Qt.QPalette.Base, bgBrush)
    qt_palette.setBrush(Qt.QPalette.WindowText, fgBrush)
    qt_palette.setBrush(Qt.QPalette.Light, frameBrush)
    qt_palette.setBrush(Qt.QPalette.Dark, frameBrush)
    widget.setPalette(qt_palette)


def updateLabelBackground(ctrl, widget):
    """Helper method to setup background of taurus labels and lcds"""
    bgRole = widget.bgRole

    if ctrl.usePalette():
        widget.setAutoFillBackground(True)
        if bgRole in ('', 'none', 'None'):
            transparentBrush = Qt.QBrush(Qt.Qt.transparent)
            frameBrush = transparentBrush
            bgBrush, fgBrush = transparentBrush, Qt.QBrush(Qt.Qt.black)
        else:
            frameBrush = Qt.QBrush(Qt.QColor(255, 255, 255, 128))
            bgItem, palette = None, QT_DEVICE_STATE_PALETTE
            if bgRole == 'quality':
                palette = QT_ATTRIBUTE_QUALITY_PALETTE
                bgItem = ctrl.quality()
            elif bgRole == 'state':
                try:
                    bgItem = ctrl.state()
                except AttributeError:
                    pass  # protect against calls with state not instantiated
            elif bgRole == 'value':
                bgItem = ctrl.value()
            else:
                # TODO: this is an *experimental* extension of the bgRole API
                # added in v 4.1.2-alpha. It may change in future versions
                modelObj = widget.getModelObj()
                try:
                    bgItem = modelObj.getFragmentObj(bgRole)
                except:
                    widget.warning('Invalid bgRole "%s"', bgRole)
            bgBrush, fgBrush = palette.qbrush(bgItem)
        _updatePaletteColors(widget, bgBrush, fgBrush, frameBrush)
    else:
        if bgRole in ('', 'none', 'None'):
            ss = StyleSheetTemplate.format("rgba(0,0,0,0)", "")
        else:
            bgItem, palette = None, QT_DEVICE_STATE_PALETTE
            if bgRole == 'quality':
                palette = QT_ATTRIBUTE_QUALITY_PALETTE
                bgItem = ctrl.quality()
            elif bgRole == 'state':
                bgItem = ctrl.state()
            elif bgRole == 'value':
                bgItem = ctrl.value()
            else:
                # TODO: this is an *experimental* extension of the bgRole API
                # added in v 4.1.2-alpha. It may change in future versions
                modelObj = widget.getModelObj()
                try:
                    bgItem = modelObj.getFragmentObj(bgRole)
                except:
                    widget.warning('Invalid bgRole "%s"', bgRole)
            color_ss = palette.qtStyleSheet(bgItem)
            ss = StyleSheetTemplate.format("rgba(255,255,255,128)",  color_ss)
        widget.setStyleSheet(ss)
    widget.update()  # necessary in pyqt <= 4.4
