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

"""A pure Qt led widget"""

__all__ = ["LedColor", "LedStatus", "LedSize", "QLed", "QLedOld"]

__docformat__ = 'restructuredtext'

import sys

from taurus.external.qt import Qt
from taurus.core.util.enumeration import Enumeration
from taurus.qt.qtgui.icon import getCachedPixmap
from taurus.qt.qtgui.display.qpixmapwidget import QPixmapWidget

LedColor = Enumeration("LedColor",  [
                       "BLUE", "GREEN", "RED", "YELLOW", "ORANGE", "MAGENTA", "GRENOBLE", "BLACK", "WHITE"])
LedStatus = Enumeration("LedStatus", ["ON", "OFF"])
LedSize = Enumeration("LedSize",   [("SMALL", 24), ("LARGE", 48)])


class QLed(QPixmapWidget):
    """A Led"""
    DefaultLedPattern = "leds_images256:led_{color}_{status}.png"
    DefaultLedColor = "green"
    DefaultLedStatus = True
    DefaultLedInverted = False
    DefaultBlinkingInterval = 0

    def __init__(self, parent=None, designMode=False):
        self._ledStatus = self.DefaultLedStatus
        self._ledColor = self.DefaultLedColor
        self._ledPatternName = self.DefaultLedPattern
        self._ledInverted = self.DefaultLedInverted
        self._ledName = self.toLedName()
        self._timer = None
        QPixmapWidget.__init__(self, parent)
        self._refresh()

    def sizeHint(self):
        if self.layout() is None:
            return Qt.QSize(24, 24)
        return QPixmapWidget.sizeHint(self)

    def minimumSizeHint(self):
        """Overwrite the default minimum size hint (0,0) to be (16,16)
        :return: the minimum size hint 16,16
        :rtype: PyQt4.Qt.QSize"""
        return Qt.QSize(8, 8)

    def toLedName(self, status=None, color=None, inverted=None):
        """Gives the led name for the given status and color. If status or
        color are not given, the current led status or color are used.

        :param status: the status
        :type  status: bool
        :param color: the color
        :type  color: str
        :return: string containing the led name
        :rtype: str"""
        if status is None:
            status = self._ledStatus
        if color is None:
            color = self._ledColor
        if inverted is None:
            inverted = self._ledInverted
        if inverted:
            status = not status
        status = status and "on" or "off"
        return self._ledPatternName.format(color=color, status=status)

    def isLedColorValid(self, name):
        """Determines if the given color name is valid.
        :param color: the color
        :type  color: str
        :return: True is the given color name is valid or False otherwise
        :rtype: bool"""
        return name.upper() in LedColor

    def _refresh(self):
        """internal usage only"""
        self._ledName = self.toLedName()
        pixmap = getCachedPixmap(self._ledName)
        self.setPixmap(pixmap)
        return self.update()

    @classmethod
    def getQtDesignerPluginInfo(cls):
        return {
            'module': 'taurus.qt.qtgui.display',
            'group': 'Taurus Display',
            'icon': "designer:ledred.png",
            'container': False,
        }

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # QT property definition
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    def getLedPatternName(self):
        """Returns the current led pattern name
        :return: led pattern name
        :rtype: str"""
        return self._ledPatternName

    def setLedPatternName(self, name):
        """Sets the led pattern name. Should be a string containing a path
        to valid images. The string can contain the keywords:

            1. {status} - transformed to 'on' of 'off' according to the status
            2. {color} - transformed to the current led color

        Example: **:leds/images256/led_{color}_{status}.png** will be transformed
        to **:leds/images256/led_red_on.png** when the led status is True and
        the led color is red.

        :param name: new pattern
        :type  name: str"""
        self._ledPatternName = str(name)
        self._refresh()

    def resetLedPatternName(self):
        """Resets the led pattern to **:leds/images256/led_{color}_{status}.png**."""
        self.setLedPatternName(self.DefaultLedPattern)

    def getLedStatus(self):
        """Returns the led status
        :return: led status
        :rtype: bool"""
        return self._ledStatus

    def setLedStatus(self, status):
        """Sets the led status
        :param status: the new status
        :type  status: bool"""
        self._ledStatus = bool(status)
        self._refresh()

    def resetLedStatus(self):
        """Resets the led status"""
        self.setLedStatus(self.DefaultLedStatus)

    def toggleLedStatus(self):
        """toggles the current status of the led"""
        self.setLedStatus(not self.getLedStatus())

    def getLedInverted(self):
        """Returns if the led is inverted.
        :return: inverted mode
        :rtype: bool"""
        return self._ledInverted

    def setLedInverted(self, inverted):
        """Sets the led inverted mode
        :param status: the new inverted mode
        :type  status: bool"""
        self._ledInverted = bool(inverted)
        self._refresh()

    def resetLedInverted(self):
        """Resets the led inverted mode"""
        self.setLedInverted(self.DefaultLedInverted)

    def getLedColor(self):
        """Returns the led color
        :return: led color
        :rtype: str"""
        return self._ledColor

    def setLedColor(self, color):
        """Sets the led color
        :param status: the new color
        :type  status: str"""
        color = str(color).lower()
        if not self.isLedColorValid(color):
            raise Exception("Invalid color '%s'" % color)
        self._ledColor = color
        self._refresh()

    def resetLedColor(self):
        """Resets the led color"""
        self.setLedColor(self.DefaultLedColor)

    def setBlinkingInterval(self, interval):
        """sets the blinking interval (the time between status switching).
        Set to a nonpositive number for disabling blinking

        :param interval: (int) the blinking interval in millisecs. Set to 0 for disabling blinking
        """
        if interval > 0:
            if self._timer is None:
                self._timer = Qt.QTimer(self)
                self._timer.timeout.connect(self.toggleLedStatus)
            self._timer.start(interval)
        else:
            if self._timer is not None:
                self._timer.stop()
                self._timer = None

    def getBlinkingInterval(self):
        """returns the blinking interval

        :return: (int) blinking interval or 0 if blinking is not enabled.
        """
        if self._timer is None:
            return 0
        else:
            return self._timer.interval()

    def resetBlinkingInterval(self):
        """resets the blinking interval"""
        self.setBlinkingInterval(self.__class__.DefaultBlinkingInterval)

    #: This property holds the led status: False means OFF, True means ON
    #:
    #: **Access functions:**
    #:
    #:     * :meth:`QLed.getLedStatus`
    #:     * :meth:`QLed.setLedStatus`
    #:     * :meth:`QLed.resetLedStatus`
    ledStatus = Qt.pyqtProperty("bool", getLedStatus, setLedStatus,
                                resetLedStatus, doc="led status")

    #: This property holds the led color
    #:
    #: **Access functions:**
    #:
    #:     * :meth:`QLed.getLedColor`
    #:     * :meth:`QLed.setLedColor`
    #:     * :meth:`QLed.resetLedColor`
    ledColor = Qt.pyqtProperty("QString", getLedColor, setLedColor,
                               resetLedColor, doc="led color")

    #: This property holds the led inverted: False means do not invert the
    #. status, True means invert the status
    #:
    #: **Access functions:**
    #:
    #:     * :meth:`QLed.getLedInverted`
    #:     * :meth:`QLed.setLedInverted`
    #:     * :meth:`QLed.resetLedInverted`
    ledInverted = Qt.pyqtProperty("bool", getLedInverted, setLedInverted,
                                  resetLedInverted, doc="led inverted mode")

    #: This property holds the led pattern name
    #:
    #: **Access functions:**
    #:
    #:     * :meth:`QLed.getLedPatternName`
    #:     * :meth:`QLed.setLedPatternName`
    #:     * :meth:`QLed.resetLedPatternName`
    ledPattern = Qt.pyqtProperty("QString", getLedPatternName, setLedPatternName,
                                 resetLedPatternName, doc="led pattern name")

    #: This property holds the blinking interval in millisecs. 0 means no blinking
    #:
    #: **Access functions:**
    #:
    #:     * :meth:`QLed.getBlinkingInterval`
    #:     * :meth:`QLed.setBlinkingInterval`
    #:     * :meth:`QLed.resetBlinkingInterval`
    blinkingInterval = Qt.pyqtProperty("int", getBlinkingInterval, setBlinkingInterval,
                                       resetBlinkingInterval, doc="blinking interval")


class QLedOld(Qt.QLabel):
    ledDirPattern = ":leds/images%(size)d"

    def __init__(self, parent=None, ledsize=LedSize.SMALL,
                 ledcolor=LedColor.GREEN):
        Qt.QLabel.__init__(self, parent)

        self.ledsize = ledsize
        self.status = LedStatus.OFF
        self.ledcolor = ledcolor

        self.setObjectName("Led")
        sizePolicy = Qt.QSizePolicy(
            Qt.QSizePolicy.Policy(0), Qt.QSizePolicy.Policy(0))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)

        # no need to call changeColor. changeSize calls it for us
        self.changeSize(ledsize)

        self.retranslateUi(self)
        Qt.QMetaObject.connectSlotsByName(self)

    def toLedName(self, status, color):
        name = "led" + LedColor.whatis(color).lower()
        if status == LedStatus.OFF:
            name += LedStatus.whatis(status).lower()
        return name

    def toCompleteLedName(self, size, status, color):
        ret = self.ledDirPattern % {"size": size}
        ret += "/" + self.toLedName(status, color) + ".png"
        return ret

    def tr(self, string):
        return Qt.QApplication.translate("Led", string, None, Qt.QApplication.UnicodeUTF8)

    def retranslateUi(self, Led):
        Led.setWindowTitle(self.tr("Form"))

    def on(self):
        if self.status == LedStatus.OFF:
            self.status = LedStatus.ON
            self.setPixmap(self.onled)

    def off(self):
        if self.status == LedStatus.ON:
            self.status = LedStatus.OFF
            self.setPixmap(self.offled)

    def changeSize(self, ledSize):
        self.ledsize = ledSize
        self.resize(ledSize, ledSize)
        self.setMinimumSize(Qt.QSize(ledSize, ledSize))
        self.setMaximumSize(Qt.QSize(ledSize, ledSize))

        # force a call to led color to change the place from which the images
        # are fetched
        self.changeColor(self.ledcolor)

    def changeColor(self, ledColor):
        self.ledcolor = ledColor

        off_pixmap_name = self.toCompleteLedName(
            self.ledsize, LedStatus.OFF, ledColor)
        self.offled = Qt.QPixmap(off_pixmap_name)
        on_pixmap_name = self.toCompleteLedName(
            self.ledsize, LedStatus.ON, ledColor)
        self.onled = Qt.QPixmap(on_pixmap_name)

        if self.status == LedStatus.OFF:
            self.setPixmap(self.offled)
        else:
            self.setPixmap(self.onled)

    def _setProblemsBackground(self, doIt=True):
        if doIt:
            self.setAutoFillBackground(True)
            bg_brush = Qt.QBrush()
            bg_brush.setStyle(Qt.Qt.BDiagPattern)
            palette = self.palette()
            palette.setBrush(Qt.QPalette.Window, bg_brush)
            palette.setBrush(Qt.QPalette.Base, bg_brush)
        else:
            self.setAutoFillBackground(False)


def main():
    """hello"""

    app = Qt.QApplication.instance()
    owns_app = app is None

    if owns_app:
        from taurus.qt.qtgui.application import TaurusApplication
        app = TaurusApplication(sys.argv, cmd_line_parser=None)

    w = Qt.QWidget()
    layout = Qt.QGridLayout()
    layout.setContentsMargins(2, 2, 2, 2)
    layout.setSpacing(2)
    w.setLayout(layout)
    for i, color in enumerate(LedColor.keys()):
        led = QLed()
        led.ledColor = color
        led.ledStatus = True
        layout.addWidget(led, i, 0)
        led = QLed()
        led.ledColor = color
        led.ledStatus = False
        layout.addWidget(led, i, 1)
        led = QLed()
        led.ledColor = color
        led.blinkingInterval = 500
        layout.addWidget(led, i, 2)
    w.show()

    if owns_app:
        sys.exit(app.exec_())
    else:
        return w

if __name__ == "__main__":
    main()
