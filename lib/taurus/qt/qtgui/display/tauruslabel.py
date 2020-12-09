#!/usr/bin/env python

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

"""This module provides a set of basic Taurus widgets based on QLabel"""
from __future__ import absolute_import

from builtins import str
from builtins import object

try:
    from collections.abc import Sequence
except ImportError:  # bck-compat py 2.7
    from collections import Sequence
import re
import string

from taurus.core.taurusbasetypes import (TaurusElementType, TaurusEventType,
                                         AttrQuality, TaurusDevState)
from taurus.external.qt import Qt
from taurus.qt.qtgui.base import TaurusBaseWidget
from taurus.qt.qtgui.base import TaurusBaseController
from taurus.qt.qtgui.base import TaurusScalarAttributeControllerHelper
from taurus.qt.qtgui.base import TaurusConfigurationControllerHelper
from taurus.qt.qtgui.base import updateLabelBackground


__all__ = ["TaurusLabel"]

__docformat__ = 'restructuredtext'

_QT_PLUGIN_INFO = {
    'module': 'taurus.qt.qtgui.display',
    'group': 'Taurus Display',
    'icon': "designer:label.png",
}

TaurusModelType = TaurusElementType
EventType = TaurusEventType


class _SafeFormatter(string.Formatter):
    """
    Like default formatter but leaves unmatched keys in the result string
    instead of raising an exception.
    Inspired by:
    https://github.com/silx-kit/pyFAI/blob/0.19/pyFAI/utils/stringutil.py#L41
    """
    def get_field(self, field_name, args, kwargs):
        try:
            return string.Formatter.get_field(self, field_name, args, kwargs)
        except KeyError:
            return "{%s}" % field_name, field_name


class TaurusLabelController(TaurusBaseController):

    StyleSheetTemplate = "border-style: outset; border-width: 2px; border-color: {0}; {1}"

    def __init__(self, label):
        self._text = ''
        self._trimmedText = False
        self._trimPattern = re.compile('<[^<]*>')
        TaurusBaseController.__init__(self, label)

    def _setStyle(self):
        TaurusBaseController._setStyle(self)
        label = self.label()
        # if update as palette
        if self.usePalette():
            label.setFrameShape(Qt.QFrame.Box)
            label.setFrameShadow(Qt.QFrame.Raised)
            label.setLineWidth(1)

    def label(self):
        return self.widget()

    def showValueDialog(self, label):
        Qt.QMessageBox.about(label,  "Full text", self._text)

    def _needsStateConnection(self):
        label = self.label()
        ret = 'state' in (label.fgRole, label.bgRole)
        return ret

    def _updateForeground(self, label):
        fgRole, value = label.fgRole, ''

        # handle special cases (that are not covered with fragment)
        if fgRole.lower() == 'state':
            try:
                value = self.state().name
            except AttributeError:
                pass  # protect against calls with state not instantiated
        elif fgRole.lower() in ('', 'none'):
            pass
        else:
            value = label.getDisplayValue(fragmentName=fgRole)
        self._text = text = label.prefixText + value + label.suffixText

        # Checks that the display fits in the widget and sets it to "..." if
        # it does not fit the widget
        self._trimmedText = self._shouldTrim(label, text)
        if self._trimmedText:
            text = "<a href='...'>...</a>"
        label.setText_(text)

    def _shouldTrim(self, label, text):
        if not label.autoTrim:
            return False
        text = re.sub(self._trimPattern, '', text)
        font_metrics = Qt.QFontMetrics(label.font())
        size, textSize = label.size().width(), font_metrics.width(text)
        return textSize > size

    def _updateToolTip(self, label):
        if not label.getAutoTooltip():
            return
        toolTip = label.getFormatedToolTip()
        if self._trimmedText:
            toolTip = u"<p><b>Value:</b> %s</p><hr>%s" % (self._text, toolTip)
        label.setToolTip(toolTip)

    _updateBackground = updateLabelBackground


class TaurusLabelControllerAttribute(TaurusScalarAttributeControllerHelper, TaurusLabelController):

    def __init__(self, label):
        TaurusScalarAttributeControllerHelper.__init__(self)
        TaurusLabelController.__init__(self, label)

    def _setStyle(self):
        TaurusLabelController._setStyle(self)
        label = self.label()
        label.setDynamicTextInteractionFlags(
            Qt.Qt.TextSelectableByMouse | Qt.Qt.LinksAccessibleByMouse)


class TaurusLabelControllerConfiguration(TaurusConfigurationControllerHelper, TaurusLabelController):

    def __init__(self, label):
        TaurusConfigurationControllerHelper.__init__(self)
        TaurusLabelController.__init__(self, label)

    def _setStyle(self):
        TaurusLabelController._setStyle(self)
        label = self.label()
        label.setDynamicTextInteractionFlags(Qt.Qt.NoTextInteraction)


#-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
# Design time controllers for label
#-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

class TaurusLabelControllerDesignMode(object):

    def _updateLength(self, lcd):
        lcd.setNumDigits(6)

    def getDisplayValue(self, write=False):
        v = self.w_value()
        if not write:
            v = self.value()
        return "%6.2f" % v

    def value(self):
        return 99.99

    def w_value(self):
        return 0.0

    def quality(self):
        return AttrQuality.ATTR_VALID

    def state(self):
        return TaurusDevState.Ready

    def _updateToolTip(self, lcd):
        lcd.setToolTip("Some random value for design purposes only")


class TaurusLabelControllerAttributeDesignMode(TaurusLabelControllerDesignMode, TaurusLabelControllerAttribute):

    def __init__(self, label):
        TaurusLabelControllerDesignMode.__init__(self)
        TaurusLabelControllerAttribute.__init__(self, label)


class TaurusLabelControllerConfigurationDesignMode(TaurusLabelControllerDesignMode, TaurusLabelControllerConfiguration):

    def __init__(self, label):
        TaurusLabelControllerDesignMode.__init__(self)
        TaurusLabelControllerConfiguration.__init__(self, label)

    def getDisplayValue(self, write=False):
        return "%6.2f" % -99.99

    def _updateToolTip(self, lcd):
        lcd.setToolTip(
            "Some random configuration value for design purposes only")


_CONTROLLER_MAP = {
    None: None,
    TaurusModelType.Unknown: None,
    TaurusModelType.Attribute: TaurusLabelControllerAttribute,
    TaurusModelType.Configuration: TaurusLabelControllerConfiguration,
}

_DESIGNER_CONTROLLER_MAP = {
    None: TaurusLabelControllerAttributeDesignMode,
    TaurusModelType.Unknown: TaurusLabelControllerAttributeDesignMode,
    TaurusModelType.Attribute: TaurusLabelControllerAttributeDesignMode,
    TaurusModelType.Configuration: TaurusLabelControllerConfigurationDesignMode,
}


class TaurusLabel(Qt.QLabel, TaurusBaseWidget):

    DefaultPrefix = ''
    DefaultSuffix = ''
    DefaultBgRole = 'quality'
    DefaultFgRole = 'rvalue'
    DefaultShowText = True
    DefaultModelIndex = None
    DefaultAutoTrim = True
    DefaultAlignment = Qt.Qt.AlignRight | Qt.Qt.AlignVCenter

    _deprecatedRoles = dict(value='rvalue', w_value='wvalue')

    def __init__(self, parent=None, designMode=False):
        self._safeFormatter = _SafeFormatter()
        self._prefix = self.DefaultPrefix
        self._suffix = self.DefaultSuffix
        self._permanentText = None
        self._bgRole = self.DefaultBgRole
        self._fgRole = self.DefaultFgRole
        self._modelIndex = self.DefaultModelIndex
        self._autoTrim = self.DefaultAutoTrim
        self._modelIndexStr = ''
        self._controller = None
        self._dynamicTextInteractionFlags = True
        name = self.__class__.__name__
        self.call__init__wo_kw(Qt.QLabel, parent)
        self.call__init__(TaurusBaseWidget, name, designMode=designMode)

        self.setAlignment(self.DefaultAlignment)

        self.linkActivated.connect(self.showValueDialog)

        # if we are in design mode there will be no events so we force the
        # creation of a controller object
        if self._designMode:
            self.controllerUpdate()

        # register configurable properties
        self.registerConfigProperty(
            self.getPermanentText, self._setPermanentText, "permanentText"
            )

    def _calculate_controller_class(self):
        ctrl_map = _CONTROLLER_MAP
        if self._designMode:
            ctrl_map = _DESIGNER_CONTROLLER_MAP

        model_type = self.getModelType()
        # ugly workaround to adapt TaurusLabel to tep14 without refactoring
        # TODO: proper refactoring of TaurusValue to supress the Conf API
        if model_type == TaurusModelType.Attribute and self.modelFragmentName:
            model_type = TaurusModelType.Configuration
        ctrl_klass = ctrl_map.get(model_type, TaurusLabelController)
        return ctrl_klass

    def controller(self):
        ctrl = self._controller
        # if there is a controller object and it is not the base controller...
        if ctrl is not None and not ctrl.__class__ == TaurusLabelController:
            return ctrl

        # if there is a controller object and it is still the same class...
        ctrl_klass = self._calculate_controller_class()
        if ctrl_klass is None:
            return None
        elif ctrl.__class__ == ctrl_klass:
            return ctrl

        self._controller = ctrl = ctrl_klass(self)
        return ctrl

    def controllerUpdate(self):
        ctrl = self.controller()
        if ctrl is not None:
            ctrl.update()

    def showValueDialog(self, *args):
        ctrl = self.controller()
        if ctrl is not None:
            ctrl.showValueDialog(self)

    def resizeEvent(self, event):
        #    # recheck the display every time we resize to make sure the text should
        #    # become trimmed or not
        if not getattr(self, '_inResize', False):
            self._inResize = True
            self.controllerUpdate()
            self._inResize = False
        Qt.QLabel.resizeEvent(self, event)

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # TaurusBaseWidget overwriting
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    def handleEvent(self, evt_src, evt_type, evt_value):
        ctrl = self.controller()
        if ctrl is not None:
            ctrl.handleEvent(evt_src, evt_type, evt_value)

    def isReadOnly(self):
        return True

    def setModel(self, m):
        # force to build another controller
        self._controller = None
        self._permanentText = None
        TaurusBaseWidget.setModel(self, m)
        if self.modelFragmentName:
            self.setFgRole(self.modelFragmentName)

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # QT property definition
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

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
        self.controllerUpdate()

    def getModelMimeData(self):
        mimeData = TaurusBaseWidget.getModelMimeData(self)
        mimeData.setText(self.text())
        return mimeData

    def resetModelIndex(self):
        self.setModelIndex(self.DefaultModelIndex)

    def getBgRole(self):
        return self._bgRole

    def setBgRole(self, bgRole):
        """
        Set the background role. The label background will be set according
        to the current palette and the role. Valid roles are:
        - 'none' : no background
        - 'state' a color depending on the device state
        - 'quality' a color depending on the attribute quality
        - 'rvalue' a color depending on the rvalue of the attribute
        - <arbitrary member name> a color based on the value of an arbitrary
        member of the model object (warning: experimental feature!)

        .. warning:: the <arbitrary member name> support is still experimental
                     and its API may change in future versions
        """
        self._bgRole = str(bgRole)
        self.controllerUpdate()

    def resetBgRole(self):
        """Reset the background role to its default value"""
        self.setBgRole(self.DefaultBgRole)

    def getFgRole(self):
        """get the foreground role for this label (see :meth:`setFgRole`)"""
        return self._fgRole

    def setFgRole(self, fgRole):
        """Set what is shown as the foreground (the text) of the label
        Valid Roles are:

        - 'rvalue' the read value of the attribute
        - 'wvalue' the write value of the attribute
        - 'none' : no text
        - 'quality' - the quality of the attribute is displayed
        - 'state' - the device state
        """
        # warn about deprecated roles
        role = self._deprecatedRoles.get(fgRole, fgRole)
        if fgRole != role:
            self.deprecated(rel='4.0', dep='setFgRole(%s)' % fgRole,
                            alt='setFgRole(%s)' % role)
        self._fgRole = str(role)
        self.controllerUpdate()

    def resetFgRole(self):
        """Reset the foreground role to its default value"""
        self.setFgRole(self.DefaultFgRole)

    def getPrefixText(self):
        return self._prefix

    def setPrefixText(self, prefix):
        self._prefix = str(prefix)
        self.controllerUpdate()

    def resetPrefixText(self):
        self.setPrefixText(self.DefaultPrefix)

    def getSuffixText(self):
        return self._suffix

    def setSuffixText(self, suffix):
        self._suffix = str(suffix)
        self.controllerUpdate()

    def resetSuffixText(self):
        self.setSuffixText(self.DefaultSuffix)

    def getPermanentText(self):
        return self._permanentText

    def _setPermanentText(self, text):
        self._permanentText = text
        if text is not None:
            self.setText_(text)

    def setText_(self, text):
        """Method to expose QLabel.setText"""
        Qt.QLabel.setText(self, text)

    def setText(self, text):
        """Reimplementation of setText to set permanentText"""
        self._setPermanentText(text)

    def setAutoTrim(self, trim):
        """Enable/disable auto-trimming of the text. If trim is True, the text
        in the label will be trimmed when it doesn't fit in the available space

        :param trim: (bool)
        """
        self._autoTrim = trim
        self.controllerUpdate()

    def setDynamicTextInteractionFlags(self, flags):
        if self.hasDynamicTextInteractionFlags():
            Qt.QLabel.setTextInteractionFlags(self, flags)

    def hasDynamicTextInteractionFlags(self):
        return self._dynamicTextInteractionFlags

    def setTextInteractionFlags(self, flags):
        Qt.QLabel.setTextInteractionFlags(self, flags)
        self._dynamicTextInteractionFlags = False

    def resetTextInteractionFlags(self):
        Qt.QLabel.resetTextInteractionFlags(self)
        self.dynamicTextInteractionFlags = True

    def getAutoTrim(self):
        """
        Whether auto-trimming of the text is enabled.

        :return: (bool)
        """
        return self._autoTrim

    def resetAutoTrim(self):
        """Reset auto-trimming to its default value"""
        self.setAutoTrim(self.DefaultAutoTrim)

    def resetFormat(self):
        """reimplement to update controller if format is changed"""
        TaurusBaseWidget.resetFormat(self)
        self.controllerUpdate()

    def displayValue(self, v):
        """Reimplementation of displayValue for TaurusLabel"""
        if self._permanentText is None:
            value = TaurusBaseWidget.displayValue(self, v)
        else:
            value = self._permanentText

        dev = None
        attr = None

        modeltype = self.getModelType()
        if modeltype == TaurusElementType.Device:
            dev = self.getModelObj()
        elif modeltype == TaurusElementType.Attribute:
            attr = self.getModelObj()
            dev = attr.getParent()

        try:
            v = self._safeFormatter.format(value, dev=dev, attr=attr)
        except Exception as e:
            self.warning(
                "Error formatting display (%r). Reverting to raw string", e)
            v = value

        return v

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
    #:     * :meth:`TaurusLabel.getModelIndex`
    #:     * :meth:`TaurusLabel.setModelIndex`
    #:     * :meth:`TaurusLabel.resetModelIndex`
    #:
    #: .. seealso:: :ref:`model-concept`
    modelIndex = Qt.pyqtProperty(
        "QString", getModelIndex, setModelIndex, resetModelIndex)

    #: This property holds a prefix text
    #:
    #: **Access functions:**
    #:
    #:     * :meth:`TaurusLabel.getPrefixText`
    #:     * :meth:`TaurusLabel.setPrefixText`
    #:     * :meth:`TaurusLabel.resetPrefixText`
    prefixText = Qt.pyqtProperty("QString", getPrefixText, setPrefixText,
                                 resetPrefixText, doc="prefix text")

    #: This property holds a suffix text
    #:
    #: **Access functions:**
    #:
    #:     * :meth:`TaurusLabel.getSuffixText`
    #:     * :meth:`TaurusLabel.setSuffixText`
    #:     * :meth:`TaurusLabel.resetSuffixText`
    suffixText = Qt.pyqtProperty("QString", getSuffixText, setSuffixText,
                                 resetSuffixText, doc="suffix text")

    #: This property holds the foreground role (the text).
    #: Valid values are:
    #:
    #:     #. ''/'None' - no value is displayed
    #:     #. 'rvalue' - the value is displayed
    #:     #. 'wvalue' - the write value is displayed
    #:     #. 'quality' - the quality is displayed
    #:     #. 'state' - the device state is displayed
    #:
    #: **Access functions:**
    #:
    #:     * :meth:`TaurusLabel.getFgRole`
    #:     * :meth:`TaurusLabel.setFgRole`
    #:     * :meth:`TaurusLabel.resetFgRole`
    fgRole = Qt.pyqtProperty("QString", getFgRole, setFgRole,
                             resetFgRole, doc="foreground role")

    #: This property holds the background role.
    #: Valid values are ''/'None', 'quality', 'state'
    #:
    #: **Access functions:**
    #:
    #:     * :meth:`TaurusLabel.getBgRole`
    #:     * :meth:`TaurusLabel.setBgRole`
    #:     * :meth:`TaurusLabel.resetBgRole`
    bgRole = Qt.pyqtProperty("QString", getBgRole, setBgRole,
                             resetBgRole, doc="background role")

    #: Specifies wether the text will be trimmed when it doesn't fit in the
    #: available space
    #:
    #: **Access functions:**
    #:
    #:     * :meth:`TaurusLabel.getAutoTrim`
    #:     * :meth:`TaurusLabel.setAutoTrim`
    #:     * :meth:`TaurusLabel.resetAutoTrim`
    autoTrim = Qt.pyqtProperty("bool", getAutoTrim, setAutoTrim,
                               resetAutoTrim, doc="auto trim text")

    #: Specifies whether the user can drag data from this widget
    #:
    #: **Access functions:**
    #:
    #:     * :meth:`TaurusLabel.isDragEnabled`
    #:     * :meth:`TaurusLabel.setDragEnabled`
    #:     * :meth:`TaurusLabel.resetDragEnabled`
    dragEnabled = Qt.pyqtProperty("bool", TaurusBaseWidget.isDragEnabled,
                                  TaurusBaseWidget.setDragEnabled,
                                  TaurusBaseWidget.resetDragEnabled,
                                  doc="enable dragging")

    #: Specifies how the label should interact with user input if it displays
    #: text.
    #:
    #: **Access functions:**
    #:
    #:     * :meth:`TaurusLabel.textInteractionFlags`
    #:     * :meth:`TaurusLabel.setTextInteractionFlags`
    #:     * :meth:`TaurusLabel.resetTextInteractionFlags
    try:
        textInteractionFlags = Qt.pyqtProperty(Qt.Qt.TextInteractionFlag,
                                               Qt.QLabel.textInteractionFlags,
                                               setTextInteractionFlags,
                                               resetTextInteractionFlags,
                                               doc="Specifies how the label should interact with user input if it displays text.")
    except TypeError:  # Old PyQt4 version only accept strings for the type arg
        textInteractionFlags = Qt.pyqtProperty("int",
                                               Qt.QLabel.textInteractionFlags,
                                               setTextInteractionFlags,
                                               resetTextInteractionFlags,
                                               doc="Specifies how the label should interact with user input if it displays text.")


def demo():
    "Label"
    from .demo import tauruslabeldemo
    return tauruslabeldemo.main()


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
                          app_name="Taurus label demo", app_version="1.0",
                          org_domain="Taurus", org_name="Tango community")

    args = app.get_command_line_args()

    if len(args) == 0:
        w = demo()
    else:
        w = Qt.QWidget()
        layout = Qt.QGridLayout()
        w.setLayout(layout)
        for model in args:
            label = TaurusLabel()
            label.model = model
            layout.addWidget(label)
    w.show()

    if owns_app:
        sys.exit(app.exec_())
    else:
        return w

if __name__ == '__main__':
    main()
