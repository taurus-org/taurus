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

"""This module provides a set of basic Taurus widgets based on QLed"""
from __future__ import absolute_import

from builtins import str
from builtins import object

import weakref
try:
    from collections.abc import Sequence
except ImportError:  # bck-compat py 2.7
    from collections import Sequence

from taurus.external.qt import Qt

from taurus.core import DataFormat, AttrQuality, DataType

from taurus.qt.qtgui.base import TaurusBaseWidget
from .qled import QLed


__all__ = ["TaurusLed"]

__docformat__ = 'restructuredtext'

_QT_PLUGIN_INFO = {
    'module': 'taurus.qt.qtgui.display',
    'group': 'Taurus Display',
    'icon': "designer:ledgreen.png",
}


class _TaurusLedController(object):

    #            key     status,     color, inTrouble
    LedMap = {True: (True,    "green",    False),
              False: (False,    "black",    False),
              None: (False,    "black",     True)}

    LedQualityMap = {
        AttrQuality.ATTR_ALARM: (True,   "orange",    False),
        AttrQuality.ATTR_CHANGING: (True,     "blue",    False),
        AttrQuality.ATTR_INVALID: (True,      "red",    False),
        AttrQuality.ATTR_VALID: (True,    "green",    False),
        AttrQuality.ATTR_WARNING: (True,   "orange",    False),
        None: (False,    "black",     True)}

    def __init__(self, widget):
        self._widget = weakref.ref(widget)

    def widget(self):
        return self._widget()

    def modelObj(self):
        return self.widget().getModelObj()

    def value(self):
        widget, obj = self.widget(), self.modelObj()
        fgRole = widget.fgRole
        value = None
        if fgRole == 'rvalue':
            value = obj.rvalue
        elif fgRole == 'wvalue':
            value = obj.wvalue
        elif fgRole == 'quality':
            return obj.quality

        # handle 1D and 2D values
        if obj.data_format is not DataFormat._0D:
            idx = widget.getModelIndexValue()
            if idx:
                for i in idx:
                    value = value[i]

        return bool(value)

    def usePreferedColor(self, widget):
        return True

    def handleEvent(self, evt_src, evt_type, evt_value):
        self.update()

    def update(self):
        widget = self.widget()

        self._updateDisplay(widget)
        self._updateToolTip(widget)

    def _updateDisplay(self, widget):
        key = None
        try:
            key = self.value()
        except Exception:
            pass
        ledMap = self.LedMap
        if widget.fgRole == 'quality':
            ledMap = self.LedQualityMap
        try:
            status, color, trouble = ledMap[key]
        except:
            status, color, trouble = False, "red", True
        if self.usePreferedColor(widget):
            if status:
                color = widget.onColor
            else:
                color = widget.offColor
        widget.ledStatus = status
        widget.ledColor = color
        if trouble:
            widget.setAutoFillBackground(True)
            bg_brush = Qt.QBrush(Qt.Qt.BDiagPattern)
            palette = widget.palette()
            palette.setBrush(Qt.QPalette.Window, bg_brush)
            palette.setBrush(Qt.QPalette.Base, bg_brush)
            widget.setPalette(palette)
        else:
            widget.setAutoFillBackground(False)

    def _updateToolTip(self, widget):
        widget.setToolTip(widget.getFormatedToolTip())


class _TaurusLedControllerBool(_TaurusLedController):

    def usePreferedColor(self, widget):
        # use prefered widget color if representing the boolean read or write
        # value. If representing the quality, use the quality map
        return widget.fgRole != 'quality'

try:
    from taurus.core.tango import DevState  # TODO: Tango-centric
    class _TaurusLedControllerState(_TaurusLedController):

        #                key      status,       color, inTrouble
        LedMap = {DevState.ON: (True,    "green",    False),
                  DevState.OFF: (False,    "black",    False),
                  DevState.CLOSE: (True,    "white",    False),
                  DevState.OPEN: (True,    "green",    False),
                  DevState.INSERT: (True,    "green",    False),
                  DevState.EXTRACT: (True,    "green",    False),
                  DevState.MOVING: (True,     "blue",    False),
                  DevState.STANDBY: (True,   "yellow",    False),
                  DevState.FAULT: (True,      "red",    False),
                  DevState.INIT: (True,   "yellow",    False),
                  DevState.RUNNING: (True,     "blue",    False),
                  DevState.ALARM: (True,   "orange",    False),
                  DevState.DISABLE: (True,  "magenta",    False),
                  DevState.UNKNOWN: (False,    "black",    False),
                  None: (False,    "black",     True)}

        def value(self):
            widget, obj = self.widget(), self.modelObj()
            fgRole = widget.fgRole
            value = None
            if fgRole == 'rvalue':
                value = obj.rvalue
            elif fgRole == 'wvalue':
                value = obj.wvalue
            elif fgRole == 'quality':
                value = obj.quality
            return value

        def usePreferedColor(self, widget):
            # never use prefered widget color. Use always the map
            return False
except:
    pass


class _TaurusLedControllerDesignMode(_TaurusLedController):

    def _updateDisplay(self, widget):
        widget.ledStatus = True
        if widget.ledStatus:
            widget.ledColor = widget.onColor
        else:
            widget.ledColor = widget.offColor
        widget.setAutoFillBackground(False)

    def _updateToolTip(self, widget):
        widget.setToolTip("Design mode TaurusLed")


class TaurusLed(QLed, TaurusBaseWidget):
    """A widget designed to represent with a LED image the state of a device,
    the value of a boolean attribute or the quality of an attribute."""

    DefaultModelIndex = None
    DefaultFgRole = 'rvalue'
    DefaultOnColor = "green"
    DefaultOffColor = "black"

    _deprecatedRoles = dict(value='rvalue', w_value='wvalue')

    def __init__(self, parent=None, designMode=False):
        name = self.__class__.__name__
        self._designMode = designMode
        self._modelIndex = self.DefaultModelIndex
        self._modelIndexStr = ''
        self._fgRole = self.DefaultFgRole
        self._onColor = self.DefaultOnColor
        self._offColor = self.DefaultOffColor
        self._controller = None
        self.call__init__wo_kw(QLed, parent)
        self.call__init__(TaurusBaseWidget, name, designMode=designMode)

        # if we are in design mode there will be no events so we force the
        # creation of a controller object
        if self._designMode:
            self.controller().update()

    def _calculate_controller_class(self):
        model = self.getModelObj()

        klass = _TaurusLedController
        if self._designMode:
            klass = _TaurusLedControllerDesignMode
        elif model is None:
            klass = _TaurusLedController
        elif model.isBoolean():
            klass = _TaurusLedControllerBool
        elif model.type == DataType.DevState:
            klass = _TaurusLedControllerState  # TODO: tango-centric
        return klass

    def controller(self):
        ctrl = self._controller
        # if there is a controller object and it is not the base controller...
        if ctrl is not None and not ctrl.__class__ == _TaurusLedController:
            return ctrl

        # if there is a controller object and it is still the same class...
        ctrl_klass = self._calculate_controller_class()
        if ctrl is not None and ctrl.__class__ == ctrl_klass:
            return ctrl

        self._controller = ctrl = ctrl_klass(self)
        return ctrl

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # TaurusBaseWidget overwriting
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    def handleEvent(self, evt_src, evt_type, evt_value):
        self.controller().handleEvent(evt_src, evt_type, evt_value)

    def isReadOnly(self):
        return True

    def setModel(self, m):
        # force to build another controller
        self._controller = None
        TaurusBaseWidget.setModel(self, m)

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # QT property definition
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    def getFgRole(self):
        return self._fgRole

    def setFgRole(self, fgRole):
        role = self._deprecatedRoles.get(fgRole, fgRole)
        if fgRole != role:
            self.deprecated(rel='4.0', dep='setFgRole(%s)' % fgRole,
                            alt='setFgRole(%s)' % role)
        self._fgRole = str(role)
        self.controller().update()

    def resetFgRole(self):
        self.setFgRole(self.DefaultFgRole)

    def getOnColor(self):
        """Returns the preferred led on color
        :return: led on color
        :rtype: str"""
        return self._onColor

    def setOnColor(self, color):
        """Sets the preferred led on color
        :param status: the new on color
        :type  status: str"""
        color = str(color).lower()
        if not self.isLedColorValid(color):
            raise Exception("Invalid color '%s'" % color)
        self._onColor = color
        self.controller().update()

    def resetOnColor(self):
        """Resets the preferred led on color"""
        self.setOnColor(self.DefaultOnColor)

    def getOffColor(self):
        """Returns the preferred led off color
        :return: led off color
        :rtype: str"""
        return self._offColor

    def setOffColor(self, color):
        """Sets the preferred led off color
        :param status: the new off color
        :type  status: str"""
        color = str(color).lower()
        if not self.isLedColorValid(color):
            raise Exception("Invalid color '%s'" % color)
        self._offColor = color
        self.controller().update()

    def resetOffColor(self):
        """Resets the preferred led color"""
        self.setOffColor(self.DefaultOffColor)

    def getModelIndexValue(self):
        return self._modelIndex

    def getModelIndex(self):
        return self._modelIndexStr

    def setModelIndex(self, modelIndex):
        mi = str(modelIndex)
        if len(mi) == 0:
            self._modelIndex = None
        else:
            try:
                mi_value = eval(str(mi))
            except:
                return
            if type(mi_value) == int:
                mi_value = mi_value,
            if not isinstance(mi_value, Sequence):
                return
            self._modelIndex = mi_value
        self._modelIndexStr = mi
        self.controller().update()

    def resetModelIndex(self):
        self.setModelIndex(self.DefaultModelIndex)

    @classmethod
    def getQtDesignerPluginInfo(cls):
        d = TaurusBaseWidget.getQtDesignerPluginInfo()
        d.update(_QT_PLUGIN_INFO)
        return d

    #: This property holds the unique URI string representing the model name
    #: with which this widget will get its data from. The convention used for
    #: the string can be found :ref:`here <model-concept>`.
    #:
    #: **Access functions:**
    #:
    #:     * :meth:`TaurusBaseWidget.getModel`
    #:     * :meth:`TaurusLabel.setModel`
    #:     * :meth:`TaurusBaseWidget.resetModel`
    #:
    #: .. seealso:: :ref:`model-concept`
    model = Qt.pyqtProperty("QString", TaurusBaseWidget.getModel, setModel,
                            TaurusBaseWidget.resetModel)

    #: This property holds whether or not this widget should search in the
    #: widget hierarchy for a model prefix in a parent widget.
    #:
    #: **Access functions:**
    #:
    #:     * :meth:`TaurusBaseWidget.getUseParentModel`
    #:     * :meth:`TaurusBaseWidget.setUseParentModel`
    #:     * :meth:`TaurusBaseWidget.resetUseParentModel`
    #:
    #: .. seealso:: :ref:`model-concept`
    useParentModel = Qt.pyqtProperty("bool", TaurusBaseWidget.getUseParentModel,
                                     TaurusBaseWidget.setUseParentModel,
                                     TaurusBaseWidget.resetUseParentModel)

    #: This property holds the index inside the model value that should be
    #: displayed
    #:
    #: **Access functions:**
    #:
    #:     * :meth:`TaurusLed.getModelIndex`
    #:     * :meth:`TaurusLed.setModelIndex`
    #:     * :meth:`TaurusLed.resetModelIndex`
    #:
    #: .. seealso:: :ref:`model-concept`
    modelIndex = Qt.pyqtProperty("QString", getModelIndex, setModelIndex,
                                 resetModelIndex)

    #: This property holds the foreground role.
    #: Valid values are:
    #:
    #:     #. 'value' - the value is used
    #:     #. 'w_value' - the write value is used
    #:     #. 'quality' - the quality is used
    #:
    #: **Access functions:**
    #:
    #:     * :meth:`TaurusLed.getFgRole`
    #:     * :meth:`TaurusLed.setFgRole`
    #:     * :meth:`TaurusLed.resetFgRole`
    fgRole = Qt.pyqtProperty("QString", getFgRole, setFgRole,
                             resetFgRole, doc="foreground role")

    #: This property holds the preferred led color
    #: This value is used for the cases where the model value does not contain
    #: enough information to distinguish between different On colors.
    #: For example, a bool attribute, when it is False it is displayed with the
    #: off led but when it is true it may be displayed On in any color. The
    #: prefered color would be used in this case.
    #:
    #: **Access functions:**
    #:
    #:     * :meth:`TaurusLed.getOnColor`
    #:     * :meth:`TaurusLed.setOnColor`
    #:     * :meth:`TaurusLed.resetOnColor`
    onColor = Qt.pyqtProperty("QString", getOnColor, setOnColor, resetOnColor,
                              doc="preferred led On color")

    #: This property holds the preferred led color
    #: This value is used for the cases where the model value does not contain
    #: enough information to distinguish between different Off colors.
    #: For example, a bool attribute, when it is False it is displayed with the
    #: off led but when it is true it may be displayed On in any color. The
    #: prefered color would be used in this case.
    #:
    #: **Access functions:**
    #:
    #:     * :meth:`TaurusLed.getOffColor`
    #:     * :meth:`TaurusLed.setOffColor`
    #:     * :meth:`TaurusLed.resetOffColor`
    offColor = Qt.pyqtProperty("QString", getOffColor, setOffColor, resetOffColor,
                               doc="preferred led Off color")


def demo():
    "Led"
    from .demo import taurusleddemo
    return taurusleddemo.main()


def main():
    import sys
    import taurus.qt.qtgui.application
    Application = taurus.qt.qtgui.application.TaurusApplication

    app = Application.instance()
    owns_app = app is None

    if owns_app:
        import taurus.core.util.argparse
        parser = taurus.core.util.argparse.get_taurus_parser()
        parser.usage = "%prog [options] <full_attribute_name(s)>"
        app = Application(sys.argv, cmd_line_parser=parser,
                          app_name="Taurus led demo", app_version="1.0",
                          org_domain="Taurus", org_name="Tango community")

    args = app.get_command_line_args()

    if len(args) == 0:
        w = demo()
    else:
        models = map(str.lower, args)

        w = Qt.QWidget()
        layout = Qt.QGridLayout()
        w.setLayout(layout)
        for model in models:
            led = TaurusLed()
            led.model = model
            layout.addWidget(led)
    w.show()

    if owns_app:
        sys.exit(app.exec_())
    else:
        return w

if __name__ == '__main__':
    main()
