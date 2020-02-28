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

"""This module provides an arrow based widget."""

from builtins import map
from builtins import range

import os
import math
import numpy

from taurus.external.qt import Qt
from taurus.core.units import Q_


__all__ = ["QWheelEdit"]

__docformat__ = 'restructuredtext'


class _ArrowButton(Qt.QPushButton):
    """Private class to be used by QWheelEdit for an arrow button"""

    ArrowPixmapName = "extra_icons:arrow01.svg"

    ButtonSize = 14
    IconSize = ButtonSize - 2

    def __init__(self, id, parent=None):
        Qt.QPushButton.__init__(self, parent)
        self.setAutoDefault(False)
        pixmap = self.getPixmap()
        self.setIcon(Qt.QIcon(pixmap))
        self.setIconSize(
            Qt.QSize(_ArrowButton.IconSize, _ArrowButton.IconSize))
        self.setFocusPolicy(Qt.Qt.ClickFocus)
        self.setFlat(True)
        self.setStyleSheet('_ArrowButton { border: 0px; }')
        self.setMaximumSize(_ArrowButton.ButtonSize, _ArrowButton.ButtonSize)
        #self.setMinimumSize(_ArrowButton.ButtonSize, _ArrowButton.ButtonSize)
        self._id = id
        self._inc = math.pow(10, id)


class _UpArrowButton(_ArrowButton):
    """Private class to be used by QWheelEdit for an up arrow button"""

    ArrowPixmapKey = "upArrow01"

    def __init__(self, id, parent=None):
        _ArrowButton.__init__(self, id, parent)

    def getPixmap(self):
        pm = Qt.QPixmapCache.find(_UpArrowButton.ArrowPixmapKey)
        if pm is None:
            pm = Qt.QPixmap(self.ArrowPixmapName)
            Qt.QPixmapCache.insert(_UpArrowButton.ArrowPixmapKey, pm)
        return pm


class _DownArrowButton(_ArrowButton):
    """Private class to be used by QWheelEdit for a down arrow button"""

    ArrowPixmapKey = "downArrow01"

    def __init__(self, id, parent=None):
        _ArrowButton.__init__(self, id, parent)
        self._inc = -self._inc

    def getPixmap(self):
        pm = Qt.QPixmapCache.find(_DownArrowButton.ArrowPixmapKey)
        if pm is None:
            pm = Qt.QPixmap(self.ArrowPixmapName)
            pm = pm.transformed(Qt.QTransform().rotate(180))
            Qt.QPixmapCache.insert(_DownArrowButton.ArrowPixmapKey, pm)
        return pm

class _DigitLabel(Qt.QLabel):
    """A private single digit label to be used by QWheelEdit widget"""

    PixmapKeys = list(map(str, range(10))) + ['blank', 'minus', 'point']

    def __init__(self, lbl, parent=None):
        Qt.QLabel.__init__(self, parent)
        self.setAlignment(Qt.Qt.AlignCenter)
        self.setFocusPolicy(Qt.Qt.StrongFocus)
        self.setStyleSheet(
            """QLabel:focus {background-color: rgb(180,180,255); border-width: 1px; border-style: solid; border-color: rgb(200,200,255);}""")
        self.resetSkin()
        self.setText(lbl)
        self._upButton = None
        self._downButton = None

    def setButtons(self, up, down):
        self._upButton = up
        self._downButton = down

    def keyPressEvent(self, key_event):
        if key_event.key() == Qt.Qt.Key_Up:
            self._upButton.click()
        elif key_event.key() == Qt.Qt.Key_Down:
            self._downButton.click()
        elif key_event.key() == Qt.Qt.Key_Right:
            self.focusNextChild()
        elif key_event.key() == Qt.Qt.Key_Left:
            self.focusPreviousChild()
        Qt.QLabel.keyPressEvent(self, key_event)

    def _update_skin_cache(self):
        skin = os.path.join('digits', self.getSkin())

        for i, d in enumerate(self.PixmapKeys):
            full_name = os.path.join(skin, d)
            pm = Qt.QPixmapCache.find(full_name)
            if pm is None:
                file_name = '%s.png' % full_name
                pm = Qt.QPixmap(file_name)
                if pm is None:
                    continue
                if not pm.isNull():
                    Qt.QPixmapCache.insert(full_name, pm)

    def setSkin(self, skin_name):
        self._skin = skin_name
        self._update_skin_cache()
        self.update()

    def getSkin(self):
        return self._skin

    def resetSkin(self):
        self.setSkin('Nixie')

    def setText(self, t):
        k = t
        if k == '.':
            k = 'point'
        elif k == '-':
            k = 'minus'
        elif k is None or k == '+':
            k = 'blank'

        k = os.path.join('digits', self.getSkin(), k)
        pm = Qt.QPixmapCache.find(k)
        if pm is None:
            Qt.QLabel.setText(self, t)
            return
        Qt.QLabel.setText(self, '')
        self.setPixmap(pm)

    skin = Qt.pyqtProperty('QString', getSkin, setSkin, resetSkin)


class QWheelEdit(Qt.QFrame):
    """A widget designed to handle numeric scalar values. It allows interaction
    based on single digit as well as normal value edition."""

    numberChanged = Qt.pyqtSignal(float)
    numberEdited = Qt.pyqtSignal(float)
    returnPressed = Qt.pyqtSignal()

    DefaultIntDigitCount = 6
    DefaultDecDigitCount = 2

    def __init__(self, parent=None):
        """__init__(self, parent = None) -> QWheelEdit

        Constructor

        @param[in] parent (QWidget) the parent widget (optional, default is None
                          meaning there is no parent
        """
        Qt.QFrame.__init__(self, parent)
        Qt.QGridLayout(self)
        self._roundFunc = None
        self._previous_value = 0
        self._value = 0
        self._value_str = '0'
        self._minValue = numpy.finfo('d').min  # -inf
        self._maxValue = numpy.finfo('d').max  # inf
        self._editor = None
        self._editing = False
        self._hideEditWidget = True
        self._showArrowButtons = True
        self._forwardReturn = False
        self._validator = Qt.QDoubleValidator(self)
        self._validator.setNotation(self._validator.StandardNotation)
        self._setDigits(QWheelEdit.DefaultIntDigitCount,
                        QWheelEdit.DefaultDecDigitCount)
        self._setValue(0)

        self._build()
        self.setDigitCountAction = Qt.QAction("Change digits", self)
        self.setDigitCountAction.triggered.connect(self._onSetDigitCount)
        self.addAction(self.setDigitCountAction)
        self.setContextMenuPolicy(Qt.Qt.ActionsContextMenu)

    def _getMinPossibleValue(self):
        """_getMinPossibleValue(self) -> None

        Determines which is the minimum possible value that can be represented
        with the current total number of digits.

        @return (float) the minimum possible value
        """
        decmax = 0
        for i in range(self.getDecDigitCount()):
            decmax += 9 * math.pow(10, -(i + 1))
        return -math.pow(10.0, self.getIntDigitCount()) + 1 - decmax

    def _getMaxPossibleValue(self):
        """_getMaxPossibleValue(self) -> None

        Determines which is the maximum possible value that can be represented
        with the current total number of digits.

        @return (float) the maximum possible value
        """
        decmax = 0
        for i in range(self.getDecDigitCount()):
            decmax += 9 * math.pow(10, -(i + 1))
        return math.pow(10.0, self.getIntDigitCount()) - 1 + decmax

    def _build(self):
        """_build(self) -> None

        Builds this widget sub-items"""

        l = self.layout()
        l.setSpacing(0)
        l.setContentsMargins(0, 0, 0, 0)

        id = self.getIntDigitCount()
        dd = self.getDecDigitCount()
        digits = self.getDigitCount()

        self._upButtons = Qt.QButtonGroup()
        self._downButtons = Qt.QButtonGroup()
        self._digitLabels = []
        for l in self._digitLabels:
            l.setAlignment(Qt.AlignCenter)

        showDot = self.getDecDigitCount() > 0

        signLabel = _DigitLabel('+')
        signLabel.setFocusPolicy(Qt.Qt.NoFocus)
        signLabel.setAlignment(Qt.Qt.AlignRight | Qt.Qt.AlignVCenter)
        self._digitLabels.append(signLabel)
        l.addWidget(signLabel, 1, 0)
        l.setRowMinimumHeight(1, signLabel.minimumSizeHint().height())
        l.setColumnMinimumWidth(0, _ArrowButton.ButtonSize)
        l.setColumnStretch(0, 1)

        for i in range(id):
            col = i + 1
            d = _DigitLabel('0')
            up = _UpArrowButton(id - i - 1)
            down = _DownArrowButton(id - i - 1)
            d.setButtons(up, down)
            up.setFocusProxy(d)
            down.setFocusProxy(d)
            self._upButtons.addButton(up, col)
            self._downButtons.addButton(down, col)
            self._digitLabels.append(d)
            if self.getShowArrowButtons():
                l.addWidget(up, 0, col)
                l.addWidget(down, 2, col)
            l.addWidget(d, 1, col)

        if showDot:
            dotLabel = _DigitLabel('.')
            dotLabel.setFocusPolicy(Qt.Qt.NoFocus)
            dotLabel.setAlignment(Qt.Qt.AlignCenter)
            self._digitLabels.append(dotLabel)
            l.addWidget(dotLabel, 1, id + 1)

        for i in range(id, digits):
            col = i + 1
            if showDot:
                col += 1
            d = _DigitLabel('0')
            up = _UpArrowButton(id - i - 1)
            down = _DownArrowButton(id - i - 1)
            d.setButtons(up, down)
            up.setFocusProxy(d)
            down.setFocusProxy(d)
            self._upButtons.addButton(up, col)
            self._downButtons.addButton(down, col)
            self._digitLabels.append(d)
            if self.getShowArrowButtons():
                l.addWidget(up, 0, col)
                l.addWidget(down, 2, col)
            l.addWidget(d, 1, col)

        self._upButtons.buttonClicked.connect(self.buttonPressed)
        self._downButtons.buttonClicked.connect(self.buttonPressed)

        ed = Qt.QLineEdit(self)
        ed.setFrame(False)
        ed.returnPressed.connect(self.editingFinished)
        ed.editingFinished.connect(self.hideEditWidget)
        rect = Qt.QRect(l.cellRect(1, 0).topLeft(),
                        l.cellRect(1, l.columnCount() - 1).bottomRight())
        ed.setGeometry(rect)
        ed.setAlignment(Qt.Qt.AlignRight)
        ed.setValidator(self._validator)
        ed.setVisible(False)
        self._editor = ed

        self._updateValidator()

        # set the minimum height for the widget
        # (otherwise the hints seem to be ignored by the layouts)
        min_height = max(ed.minimumSizeHint().height(),
                         signLabel.minimumSizeHint().height())
        if self.getShowArrowButtons():
            min_height += 2 * _ArrowButton.ButtonSize
        self.setMinimumHeight(min_height)

        self.clearWarning()

    def _clear(self):
        """_clear(self) -> None

        Clears this widget sub-items"""

        self._upButtons.buttonClicked.disconnect(self.buttonPressed)
        self._downButtons.buttonClicked.disconnect(self.buttonPressed)

        for b in self._upButtons.buttons():
            self._upButtons.removeButton(b)
            b.setParent(None)
            b.destroy()
        for b in self._downButtons.buttons():
            self._downButtons.removeButton(b)
            b.setParent(None)
            b.destroy()
        for label in self._digitLabels:
            label.setParent(None)
            label.destroy()
        self._digitLabels = None
        self._upButtons.setParent(None)
        self._downButtons.setParent(None)
        self._upButtons = None
        self._downButtons = None
        self._editor.setParent(None)
        self._editor.destroy()
        self._editor = None

    def _setDigits(self, int_nb=None, dec_nb=None):
        """_setDigits(self, int_nb=None, dec_nb=None) -> None

        Sets the number of digits that this widget shows. It will ensure that
        the current value can be displayed (i.e., int_nb will be forced to be
        large enough for displaying the integer representation of the value)

        @param[in] int_nb (int) number of integer digits (optional, default is
                   None, meaning use the existing number of integer digits
        @param[in] dec_nb (int) number of decimal digits (optional, default is
                   None, meaning use the existing number of decimal digits
        """

        if not int_nb is None:
            self._intDigitCount = int_nb
        if not dec_nb is None:
            self._decDigitCount = dec_nb

        # make sure that the current value can be displayed
        self._intDigitCount = max(self._intDigitCount, len("%d" % self._value))

        self._digitCount = self._intDigitCount + self._decDigitCount
        total_chars = self._digitCount
        total_chars += 1  # for sign
        if self._decDigitCount > 0:
            total_chars += 1  # for dot
        self._valueFormat = '%%+0%d.%df' % (total_chars, self._decDigitCount)
        self._updateValidator()
        # we call setValue to update the self._value_str
        self._setValue(self.getValue())

    def _buildValueStr(self, v):
        """_buildValueStr(self, v) -> str

        Builds a string representation of the given value according to the
        number of digits this widget can currently represent

        @param[in] v (float) the value to be translated

        @return (str) a proper string representation of the given value
        """
        if v is None:
            ret = (self._valueFormat % 0).replace('0', '-')
        else:
            ret = self._valueFormat % v
            if ret.endswith('nan'):
                ret = ret.replace('0', ' ')
        self._value_str = ret
        return ret

    def _updateDigits(self):
        """_updateDigits(self) -> None

        Updates this widget contents (sub-widgets) according to the current
        widget configuration
        """
        self._clear()
        self._build()
        self._updateValue(False, False)

    def _updateValue(self, trigValueChanged=True, trigValueEdited=True):
        """_updateValue(self, trigValueChanged=True, trigValueEdited=True) -> None

        Updates this widget displayed value and potentially send signal(s)

        @param[in] trigValueChanged (bool) (optional, default is True) wheather or
                   not to send signal 'valueChanged(double)'
        @param[in] trigValueEdited (bool) (optional, default is True) wheather or
                   not to send signal 'valueEdit(double)'
        """
        v, v_str = self.getValue(), self.getValueStr()

        if len(v_str) > len(self._digitLabels):
            # do auto adjust
            if '.' in v_str:
                dc = list(map(len, v_str.split('.')))
            else:
                dc = len(v_str), 0
            self._setDigits(*dc)
            v_str = self._buildValueStr(v)
            self._clear()
            self._build()

        for i, c in enumerate(v_str):
            self._digitLabels[i].setText(c)

        if trigValueChanged:
            self.numberChanged.emit(v)

        if trigValueEdited:
            self.numberEdited.emit(v)

    def setRoundFunc(self, roundFunc):
        """setRoundFunc(self, roundFunc) -> None

        Sets the rounding function to use when calling _setValue(). This allows you to
        filter invalid user input

        @param[in] roundFunc (callable) the rounding function to use
        """
        self._roundFunc = roundFunc

    def getPreviousValue(self):
        """getPreviousValue(self) -> float

        Gives the previous value of this widget

        @return (float) the previous value of this widget
        """
        return self._previous_value

    def _setValue(self, v):
        """_setValue(self, v) -> None

        Sets value of this widget. If the given value exceeds any limit, the
        value is NOT set.
        """
        if v is None:
            return
        if self._roundFunc:
            v = self._roundFunc(v)
        if v > self._validator.top() or v < self._validator.bottom():
            Qt.QMessageBox.warning(
                self,
                "Invalid Value",
                "'{}' is out of the allowed range ({}, {})".format(
                    v,
                    self._validator.bottom(),
                    self._validator.top(),
                )
            )
            return
        self._previous_value = self._value
        self._value = v

        str_value = self._buildValueStr(v)
        ed = self.getEditWidget()
        if ed is not None:
            ed.setText(str_value)


    def setWarning(self, msg):
        """setWarning(self, msg) -> None

        Activates the warning style for this widget. This means a violet border
        and a tooltip with the given message.

        @param[in] msg (str) the message to be displayed as tooltip
        """
        self.setStyleSheet(
            'QWheelEdit {border: 1px solid; border-radius: 4px; border-color: violet}')
        self.setToolTip(msg)

    def clearWarning(self):
        """clearWarning(self) -> None

        Clears the warning style. If not in warning mode, nothing is done.
        """
        self.setStyleSheet(
            'QWheelEdit {border: 1px solid; border-radius: 4px; border-color: rgba(0,0,0,0)}')
        self.setToolTip('')

    def buttonPressed(self, b):
        """buttonPressed(self, b) -> None

        Slot executed when an arrow button is pressed from the button group

        @param[in] b (_ArrowButton) the button which was pressed
        """
        if self._editing:
            self.hideEditWidget()
        else:
            self._setValue(self.getValue() + b._inc)
            self._updateValue()

    def _onSetDigitCount(self):
        text, ok = Qt.QInputDialog.getText(
            self,
            "Change digits",
            "Enter digits as <int_nb>.<dec_nb>",
            text="{:d}.{:d}".format(
                self.getIntDigitCount(),
                self.getDecDigitCount()
            )
        )
        if ok:
            try:
                dc = list(map(int, text.split('.')))
                self.setDigitCount(*dc)
            except Exception as e:
                Qt.QMessageBox.warning(
                    self,
                    "Invalid digit count specification",
                    'Invalid specification: "{}"\nReason:{}'.format(text, e)
                )
                self._onSetDigitCount()

    def setDigitCount(self, int_nb, dec_nb):
        """setDigitCount(self, int_nb, dec_nb) -> None

        Updates the displayed digits.

        @param[in] int_nb(int) number of integer digits
        @param[in] dec_nb(int) number of decimal digits
        """
        self._setDigits(int_nb=int_nb, dec_nb=dec_nb)
        self._updateDigits()

    def getDigitCount(self):
        """getDigitCount(self) -> int

        Gets the total number of digits this widget displays

        @return (int) the total number of digits this widget displays
        """
        return self._digitCount

    def getIntDigitCount(self):
        """getIntDigitCount(self) -> int

        Gets the number of integer digits this widget displays

        @return (int) the number of integer digits this widget displays
        """
        return self._intDigitCount

    def setIntDigitCount(self, n):
        """setIntDigitCount(self, n) -> None

        Sets the number of integer digits this widget displays

        @param[in] n (int) the number of integer digits to display
        """
        self._setDigits(int_nb=n)
        self._updateDigits()

    def resetIntDigitCount(self):
        """resetIntDigitCount(self) -> None

        Resets the number of integer digits this widget displays to DefaultIntDigitCount
        """
        self.setIntDigitCount(QWheelEdit.DefaultIntDigitCount)

    def getDecDigitCount(self):
        """getDecDigitCount(self) -> int

        Gets the number of decimal digits this widget displays

        @return (int) the number of decimal digits this widget displays
        """
        return self._decDigitCount

    def setDecDigitCount(self, n):
        """setDecDigitCount(self, n) -> None

        Sets the number of decimal digits this widget displays

        @param[in] n (int) the number of decimal digits to display
        """

        self._setDigits(dec_nb=n)
        self._updateDigits()

    def resetDecDigitCount(self):
        """resetDecDigitCount(self) -> None

        Resets the number of decimal digits this widget displays to DefaultDecDigitCount
        """
        self.setDecDigitCount(QWheelEdit.DefaultDecDigitCount)

    def setValue(self, v):
        """setValue(self, v) -> None

        Sets the value of this widget.
        Send a 'valueChanged(double)' Qt signal

        @param[in] v (float/Quantity) the value to be set
        """
        if isinstance(v, Q_):
            v = v.magnitude
        self._setValue(v)
        self._updateValue(trigValueEdited=False)

    def resetValue(self):
        """resetValue(self) -> None

        Resets the value of this widget to 0.0
        """
        self.setValue(0.0)

    def getValue(self):
        """getValue(self) -> float

        Gets the current value of this widget

        @return (float) the value currently displayed by the widget
        """
        return self._value

    def getValueStr(self):
        """getValueStr(self) -> str

        Gets the current value string of this widget

        @return (str) the value currently displayed by the widget
        """
        return self._value_str

    def getMinValue(self):
        """getMinValue(self) -> float

        Gets the minimum allowed value

        @return (float) the minimum allowed value
        """
        return self._minValue

    def setMinValue(self, v):
        """setMinValue(self, v) -> None

        Sets the minimum allowed value for the widget

        @param[in] v (float) the new minimum allowed value
        """
        self._minValue = v
        self._updateValidator()

    def _updateValidator(self):
        min_ = max(self._minValue, self._getMinPossibleValue())
        max_ = min(self._maxValue, self._getMaxPossibleValue())
        self._validator.setRange(min_, max_, self._decDigitCount)

    def resetMinValue(self):
        """resetMinValue(self) -> None

        Resets the minimum allowed value to -inf
        """
        self.setMinValue(numpy.finfo('d').min)

    def getMaxValue(self):
        """getMaxValue(self) -> float

        Gets the maximum allowed value

        @return (float) the maximum allowed value
        """
        return self._maxValue

    def setMaxValue(self, v):
        """setMaxValue(self, v) -> None

        Sets the maximum allowed value for the widget

        @param[in] v (float) the new maximum allowed value
        """
        self._maxValue = v
        self._updateValidator()

    def resetMaxValue(self):
        """resetMaxValue(self) -> None

        Resets the maximum allowed value to +inf
        """
        self.setMaxValue(numpy.finfo('d').max)

    def getAutoRepeat(self):
        return self._upButtons.buttons()[0].autoRepeat()

    def setAutoRepeat(self, v):
        for b in self._upButtons.buttons():
            b.setAutoRepeat(v)
        for b in self._downButtons.buttons():
            b.setAutoRepeat(v)

    def resetAutoRepeat(self):
        self.setAutoRepeat(False)

    def getAutoRepeatDelay(self):
        return self._upButtons.buttons()[0].autoRepeatDelay()

    def setAutoRepeatDelay(self, milisecs):
        for b in self._upButtons.buttons():
            b.setAutoRepeatDelay(milisecs)
        for b in self._downButtons.buttons():
            b.setAutoRepeatDelay(milisecs)

    def getAutoRepeatInterval(self):
        return self._upButtons.buttons()[0].autoRepeatInterval()

    def setAutoRepeatInterval(self, milisecs):
        for b in self._upButtons.buttons():
            b.setAutoRepeatInterval(milisecs)
        for b in self._downButtons.buttons():
            b.setAutoRepeatInterval(milisecs)

    def getEditWidget(self):
        """getEditWidget(self) -> QWidget

        Gets the widget object used when the user manually sets the value

        @return (QWidget) the widget used for editing
        """
        return self._editor

    def editingFinished(self):
        """editingFinished(self) -> None

        Slot called when the user finishes editing
        """
        ed = self.getEditWidget()
        v = float(ed.text())
        self._setValue(v)
        self._updateValue()

    def showEditWidget(self):
        """showEditWidget(self) -> None

        Forces the edition widget to be displayed
        """
        ed, l = self.getEditWidget(), self.layout()
        rect = Qt.QRect(l.cellRect(1, 0).topLeft(), l.cellRect(1,
                                                               l.columnCount() - 1).bottomRight())
        ed.setGeometry(rect)
        ed.setAlignment(Qt.Qt.AlignRight)
        ed.setText(self.getValueStr())
        ed.selectAll()
        ed.setFocus()
        ed.setVisible(True)
        self._editing = True

    def hideEditWidget(self):
        """hideEditWidget(self) -> None

        Forces the edition widget to be hidden
        """
        ed = self.getEditWidget()
        ed.setVisible(False)
        self._editing = False
        self.setFocus()

    def wheelEvent(self, evt):
        numDegrees = evt.delta() // 8
        numSteps = numDegrees // 15
        #w = Qt.QApplication.focusWidget()
        w = self.focusWidget()
        if not isinstance(w, _DigitLabel):
            return Qt.QFrame.wheelEvent(self, evt)

        if numSteps > 0:
            inc = w._upButton._inc
        else:
            inc = -w._downButton._inc
        numSteps *= inc
        self.setValue(self.getValue() + numSteps)
        evt.accept()

    def mouseDoubleClickEvent(self, mouse_event):
        """mouseDoubleClickEvent(self, mouse_event)

        Executed when user presses double click. This widget shows the edition
        widget when this happens
        """
        self.showEditWidget()

    def keyPressEvent(self, key_event):
        """keyPressEvent(self, key_event) -> None

        Exectuted when the user presses a key.
        F2 enters/leaves edition mode. ESC leaves edition mode
        """
        k = key_event.key()
        if k == Qt.Qt.Key_F2:
            if self._editing:
                self.hideEditWidget()
            else:
                self.showEditWidget()
            return
        elif k == Qt.Qt.Key_Escape:
            if self._editing:
                self.hideEditWidget()
                return
        elif k in (Qt.Qt.Key_Return, Qt.Qt.Key_Enter):
            if self._editing:
                self.hideEditWidget()
            else:
                self.returnPressed.emit()

        # TODO Decide when to emit editingFinished for completeness
        Qt.QWidget.keyPressEvent(self, key_event)

    def getShowArrowButtons(self):
        return self._showArrowButtons

    def setShowArrowButtons(self, yesno):
        self._showArrowButtons = yesno
        self._updateDigits()

    def resetShowArrowButtons(self):
        self.setShowArrowButtons(True)

    def getHideEditWidget(self):
        """getHideEditWidget(self) -> bool

        Gets the info if edition widget should be hidden when 'focusOut' event
        occurs.

        @return (bool)
        """
        return self._hideEditWidget

    def setHideEditWidget(self, focus_out=True):
        """setFocusOut(self, focus_out=True) -> None

        Sets if edition widget should be hidden when 'focusOut' event occurs.
        If set to False, edition widget is hidden only when 'F2', 'Esc',
        'Enter' and arrow button are pressed. Default set to True.

        @param[in] focus_out (bool) whether or not to hide edition widget
        after 'focusOut' event.
        """
        if focus_out and not self._hideEditWidget:
            ed = self.getEditWidget()
            ed.editingFinished.connect(self.hideEditWidget)
            self._hideEditWidget = True
        elif not focus_out and self._hideEditWidget:
            ed = self.getEditWidget()
            ed.editingFinished.disconnect(self.hideEditWidget)
            self._hideEditWidget = False

    def isReturnForwarded(self):
        """isReturnForwarded(self) -> bool

        Gets the info if returnPressed is forwarded.

        @return (bool)
        """
        return self._forwardReturn

    def setReturnForwarded(self, forward_rtn=False):
        """setReturnForwarded(self, forward_rtn=False) -> None

        Sets forwarding of returnPressed. If set to True, returnPressed from
        edition widget emits returnPressed of 'QWheelEdit' widget.

        @param[in] forward_rtn (bool) whether or not to forward returnPressed
        signal
        """
        if forward_rtn and not self._forwardReturn:
            ed = self.getEditWidget()
            ed.returnPressed.connect(self.returnPressed)
            self._forwardReturn = True

        elif not forward_rtn and self._forwardReturn:
            ed = self.getEditWidget()
            ed.returnPressed.disconnect(self.returnPressed)
            self._forwardReturn = False

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # QT properties
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    showArrowButtons = Qt.pyqtProperty("bool", getShowArrowButtons,
                                       setShowArrowButtons,
                                       resetShowArrowButtons)

    integerDigits = Qt.pyqtProperty("int", getIntDigitCount,
                                    setIntDigitCount, resetIntDigitCount)

    decimalDigits = Qt.pyqtProperty("int", getDecDigitCount,
                                    setDecDigitCount, resetDecDigitCount)

    value = Qt.pyqtProperty("double", getValue,
                            setValue, resetValue)

    minValue = Qt.pyqtProperty("double", getMinValue,
                               setMinValue, resetMinValue)

    maxValue = Qt.pyqtProperty("double", getMaxValue,
                               setMaxValue, resetMaxValue)

    autoRepeat = Qt.pyqtProperty("bool", getAutoRepeat,
                                 setAutoRepeat, resetAutoRepeat)

    autoRepeatDelay = Qt.pyqtProperty("int", getAutoRepeatDelay,
                                      setAutoRepeatDelay)

    autoRepeatInterval = Qt.pyqtProperty("int", getAutoRepeatInterval,
                                         setAutoRepeatInterval)


def main():
    import taurus.qt.qtgui.icon  # otherwise the arrows don't show in the demo
    global arrowWidget

    def resetAll():
        arrowWidget.resetIntDigitCount()
        arrowWidget.resetDecDigitCount()
        arrowWidget.resetMinValue()
        arrowWidget.resetMaxValue()
        arrowWidget.resetValue()

    def setNAN():
        arrowWidget.setValue(float('nan'))

    def setNone():
        arrowWidget.setValue(None)

    a = Qt.QApplication([])
    panel = Qt.QWidget()
    l = Qt.QFormLayout(panel)
    button_layout = Qt.QVBoxLayout()
    arrowWidget = QWheelEdit(panel)
    isb, dsb = Qt.QSpinBox(panel), Qt.QSpinBox(panel)
    minv, maxv = Qt.QDoubleSpinBox(panel), Qt.QDoubleSpinBox(panel)
    resetbutton = Qt.QPushButton("Reset", panel)
    resetbutton.setDefault(True)
    nanbutton = Qt.QPushButton("Set NAN", panel)
    nonebutton = Qt.QPushButton("Set None", panel)
    hideEditCB = Qt.QCheckBox()
    hideEditCB.setChecked(True)
    showarrowbutton = Qt.QCheckBox("", panel)

    l.addRow("Value", arrowWidget)
    l.addRow("Integer digits:", isb)
    l.addRow("Decimal digits:", dsb)
    l.addRow("Minimum value:", minv)
    l.addRow("Maximum value:", maxv)
    l.addRow("Show arrows:", showarrowbutton)
    l.addRow("hideEditCB", hideEditCB)
    l.addRow(button_layout)
    button_layout.addWidget(nanbutton)
    button_layout.addWidget(nonebutton)
    button_layout.addWidget(resetbutton)
    isb.setValue(arrowWidget.getIntDigitCount())
    dsb.setValue(arrowWidget.getDecDigitCount())
    minv.setRange(numpy.finfo('d').min, numpy.finfo('d').max)
    maxv.setRange(numpy.finfo('d').min, numpy.finfo('d').max)
    minv.setValue(arrowWidget.getMinValue())
    maxv.setValue(arrowWidget.getMaxValue())
    showarrowbutton.setChecked(arrowWidget.getShowArrowButtons())
    isb.valueChanged.connect(arrowWidget.setIntDigitCount)
    dsb.valueChanged.connect(arrowWidget.setDecDigitCount)
    minv.valueChanged.connect(arrowWidget.setMinValue)
    showarrowbutton.stateChanged.connect(arrowWidget.setShowArrowButtons)
    nanbutton.clicked.connect(setNAN)
    nonebutton.clicked.connect(setNone)
    hideEditCB.toggled.connect(arrowWidget.setHideEditWidget)
    resetbutton.clicked.connect(resetAll)
    panel.setVisible(True)
    a.exec_()

if __name__ == "__main__":
    main()
