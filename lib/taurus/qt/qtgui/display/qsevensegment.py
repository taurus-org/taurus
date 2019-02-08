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

"""
qsevensegmentdisplay.py
"""

from __future__ import print_function

from taurus.external.qt import Qt


__all__ = ['Q7SegDigit']

__docformat__ = 'restructuredtext'

POLY = Qt.QPolygonF
P = Qt.QPointF


class Q7SegDigit(Qt.QWidget):
    """
    A widget representing a single seven segment digit. The style can be
    configured through the widget properties. For example, a typical LCD would
    have the following style:

        - bgColor 170, 170, 127
        - ledOnPenColor 30,30,30
        - ledOnBgColor 0,0,0
        - ledOffPenColor 160, 160, 120
        - ledOffbgColor 150, 150, 112
    """
    Leds = (
        (1, 1, 1, 0, 1, 1, 1),  # 0
        (0, 0, 1, 0, 0, 1, 0),  # 1
        (1, 0, 1, 1, 1, 0, 1),  # 2
        (1, 0, 1, 1, 0, 1, 1),  # 3
        (0, 1, 1, 1, 0, 1, 0),  # 4
        (1, 1, 0, 1, 0, 1, 1),  # 5
        (1, 1, 0, 1, 1, 1, 1),  # 6
        (1, 0, 1, 0, 0, 1, 0),  # 7
        (1, 1, 1, 1, 1, 1, 1),  # 8
        (1, 1, 1, 1, 0, 1, 0),  # 9
        (0, 0, 0, 0, 0, 0, 0),  # 10 'nothing'
        (0, 0, 0, 1, 0, 0, 0),  # 11 -
        (1, 0, 1, 1, 1, 1, 1),  # 12 a
        (0, 0, 0, 1, 1, 1, 0),  # 13 n
    )

#    LedGeometries = (
#        POLY([P(67, 60), P(283, 60), P(253, 90), P(97, 90), P(67, 60)]),
#        POLY([P(60, 67), P(90, 97), P(90, 178), P(60, 193), P(60, 67)]),
#        POLY([P(290, 67), P(260, 97), P(260, 178), P(290, 193), P(290, 67)]),
#        POLY([P(67, 200), P(97, 185), P(253, 185), P(283, 200), P(253, 215), P(97, 215), P(67, 200)]),
#        POLY([P(60, 207), P(90, 222), P(90, 303), P(60, 333), P(60, 207)]),
#        POLY([P(290, 207), P(260, 222), P(260, 303), P(290, 333), P(290, 207)]),
#        POLY([P(67, 340), P(283, 340), P(253, 310), P(97, 310), P(67, 340)]),
#    )

    LedGeometriesWithFrame300x400 = (
        POLY([P(37, 30), P(263, 30), P(233, 60), P(67, 60), P(37, 30)]),
        POLY([P(30, 37), P(60, 67), P(60, 178), P(30, 193), P(30, 37)]),
        POLY([P(270, 37), P(240, 67), P(240, 178), P(270, 193), P(270, 37)]),
        POLY([P(37, 200), P(67, 185), P(233, 185), P(
            263, 200), P(233, 215), P(67, 215), P(37, 200)]),
        POLY([P(30, 207), P(60, 222), P(60, 333), P(30, 363), P(30, 207)]),
        POLY([P(270, 207), P(240, 222), P(240, 333), P(270, 363), P(270, 207)]),
        POLY([P(37, 370), P(263, 370), P(233, 340), P(67, 340), P(37, 370)]),
    )

    LedGeometriesWithoutFrame300x400 = (
        POLY([P(7, 0), P(293, 0), P(263, 30), P(37, 30), P(7, 0)]),
        POLY([P(0, 7), P(30, 37), P(30, 178), P(0, 193), P(0, 7)]),
        POLY([P(300, 7), P(270, 37), P(270, 178), P(300, 193), P(300, 7)]),
        POLY([P(7, 200), P(37, 185), P(263, 185), P(
            293, 200), P(263, 215), P(37, 215), P(7, 200)]),
        POLY([P(0, 207), P(30, 222), P(30, 363), P(0, 393), P(0, 207)]),
        POLY([P(300, 207), P(270, 222), P(270, 363), P(300, 393), P(300, 207)]),
        POLY([P(7, 400), P(293, 400), P(263, 370), P(37, 370), P(7, 400)]),
    )

    LedGeometriesWithFrame300x300 = (
        POLY([P(37, 30), P(263, 30), P(233, 60), P(67, 60), P(37, 30)]),
        POLY([P(30, 37), P(60, 67), P(60, 128), P(30, 143), P(30, 37)]),
        POLY([P(270, 37), P(240, 67), P(240, 128), P(270, 143), P(270, 37)]),
        POLY([P(37, 150), P(67, 135), P(233, 135), P(
            263, 150), P(233, 165), P(67, 165), P(37, 150)]),
        POLY([P(30, 157), P(60, 172), P(60, 233), P(30, 263), P(30, 157)]),
        POLY([P(270, 157), P(240, 172), P(240, 233), P(270, 263), P(270, 157)]),
        POLY([P(37, 270), P(263, 270), P(233, 240), P(67, 240), P(37, 270)]),
    )

    LedGeometriesWithoutFrame300x300 = (
        POLY([P(7, 0), P(293, 0), P(263, 30), P(37, 30), P(7, 0)]),
        POLY([P(0, 7), P(30, 37), P(30, 128), P(0, 143), P(0, 7)]),
        POLY([P(300, 7), P(270, 37), P(270, 128), P(300, 143), P(300, 7)]),
        POLY([P(7, 150), P(37, 135), P(263, 135), P(
            293, 150), P(263, 165), P(37, 165), P(7, 150)]),
        POLY([P(0, 157), P(30, 172), P(30, 263), P(0, 293), P(0, 157)]),
        POLY([P(300, 157), P(270, 172), P(270, 263), P(300, 293), P(300, 157)]),
        POLY([P(7, 300), P(293, 300), P(263, 270), P(37, 270), P(7, 300)]),
    )

    DftLedOnPenColor = Qt.QColor(193, 0, 0, 255)
    DftLedOnBgColor = Qt.Qt.red

    DftLedOffPenColor = Qt.QColor(30, 30, 30, 255)
    DftLedOffBgColor = Qt.QColor(40, 40, 40, 255)

    DftBgBrush = Qt.QBrush(Qt.Qt.black, Qt.Qt.SolidPattern)

    DftLedPenWidth = 5
    DftValue = ''

    DftWidth = 300
    DftHeight = 300
    DftAspectRatio = DftWidth // DftHeight
    DftUseFrame = True

    def __init__(self, parent=None, **kwargs):
        Qt.QWidget.__init__(self, parent)

        self._setLedPenWidth(Q7SegDigit.DftLedPenWidth)
        self._setValue(Q7SegDigit.DftValue)
        self._setLedOnPenColor(Q7SegDigit.DftLedOnPenColor)
        self._setLedOnBgColor(Q7SegDigit.DftLedOnBgColor)
        self._setLedOffPenColor(Q7SegDigit.DftLedOffPenColor)
        self._setLedOffBgColor(Q7SegDigit.DftLedOffBgColor)
        self._setBgBrush(Q7SegDigit.DftBgBrush)
        self._setAspectRatio(Q7SegDigit.DftAspectRatio)
        self._setUseFrame(Q7SegDigit.DftUseFrame)
        self._updatePensAndBrushes()

    def minimumSizeHint(self):
        return Qt.QSize(4, 5.9)

    def sizeHint(self):
        # return Qt.QSize(Q7SegDigit.DftWidth, Q7SegDigit.DftHeight)
        return Qt.QSize(40, 50)

    def _updatePensAndBrushes(self):
        pon = Qt.QPen(self._ledOnPenColor, self._ledPenWidth,
                      Qt.Qt.SolidLine, Qt.Qt.RoundCap, Qt.Qt.RoundJoin)
        poff = Qt.QPen(self._ledOffPenColor, self._ledPenWidth,
                       Qt.Qt.SolidLine, Qt.Qt.RoundCap, Qt.Qt.RoundJoin)
        bon = Qt.QBrush(self._ledOnBgColor, Qt.Qt.SolidPattern)
        boff = Qt.QBrush(self._ledOffBgColor, Qt.Qt.SolidPattern)
        pens, brushes = [], []
        for nLeds in Q7SegDigit.Leds:
            nPens = []
            nBrushes = []
            for onoff in nLeds:
                if onoff:
                    pen, brush = pon, bon
                else:
                    pen, brush = poff, boff
                nPens.append(pen)
                nBrushes.append(brush)
            pens.append(nPens)
            brushes.append(nBrushes)
        self._pens, self._brushes = pens, brushes
        self.update()

    def __valueStrToLedIndex(self, s):
        if s is None:
            s = 10
        elif s == '-':
            s = 11
        elif s == 'a':
            s = 12
        elif s == 'n':
            s = 13
        else:
            try:
                s = int(s)
            except:
                s = 10
        return s

    def paintEvent(self, evt):
        painter = Qt.QPainter(self)
        painter.setRenderHint(Qt.QPainter.Antialiasing)
        painter.setWindow(0, 0, self.DftWidth, self.DftHeight)
        w, h = float(self.width()), float(self.height())
        aspect = w / h
        if aspect > 0.75:
            w = h * aspect
        else:
            h = w / aspect
        painter.setViewport(0, 0, w, h)
        self._paintBorder(painter)
        self._paintSegment(painter)

    def _paintBorder(self, painter):
        if self.getUseFrame():
            painter.setPen(Qt.QPen(Qt.Qt.black, 2, Qt.Qt.SolidLine,
                                   Qt.Qt.RoundCap, Qt.Qt.RoundJoin))
            linGrad = Qt.QLinearGradient(30, 200, 200, 150)
            linGrad.setColorAt(0, Qt.Qt.darkGray)
            linGrad.setColorAt(1, Qt.Qt.white)
            linGrad.setSpread(Qt.QGradient.ReflectSpread)
            painter.setBrush(linGrad)
            border2 = Qt.QRectF(0, 0, self.DftWidth, self.DftHeight)
            painter.drawRoundRect(border2, 10, 10)
            painter.setBrush(self.getBgBrush())
            dist = 20
            border1 = Qt.QRectF(dist, dist, self.DftWidth -
                                2 * dist, self.DftHeight - 2 * dist)
            painter.drawRoundRect(border1, 5, 5)
        else:
            painter.setBrush(self.getBgBrush())
            border1 = Qt.QRectF(0, 0, self.DftWidth, self.DftHeight)
            painter.drawRect(border1)

    def _paintSegment(self, painter):
        idx = self.__valueStrToLedIndex(self._value)

        if self.getUseFrame():
            if self.DftHeight == 300:
                geom = self.LedGeometriesWithFrame300x300
            else:
                geom = self.LedGeometriesWithFrame300x400
        else:
            if self.DftHeight == 300:
                geom = self.LedGeometriesWithoutFrame300x300
            else:
                geom = self.LedGeometriesWithoutFrame300x400

        pens, brushes = self._pens[idx], self._brushes[idx]

        for i in range(7):
            seg = Qt.QPainterPath()
            seg.addPolygon(geom[i])
            painter.setPen(pens[i])
            painter.setBrush(brushes[i])
            painter.drawPath(seg)

    def __str__(self):
        _, idx = '', self.__valueStrToLedIndex(self._value)
        leds = self.Leds[idx]

        # line 0
        c = ' '
        if leds[0]:
            c = '_'
        ret = ' %c \n' % c

        # line 1
        c1, c2, c3 = ' ', ' ', ' '
        if leds[1]:
            c1 = '|'
        if leds[3]:
            c2 = '_'
        if leds[2]:
            c3 = '|'
        ret += '%c%c%c\n' % (c1, c2, c3)

        # line 2
        c1, c2, c3 = ' ', ' ', ' '
        if leds[4]:
            c1 = '|'
        if leds[6]:
            c2 = '_'
        if leds[5]:
            c3 = '|'
        ret += '%c%c%c' % (c1, c2, c3)
        return ret

    def _setValue(self, n):
        if n is None:
            self._value = n
        else:
            self._value = str(n)

    def _setLedPenWidth(self, w):
        self._ledPenWidth = w

    def _setLedOnPenColor(self, penColor):
        self._ledOnPenColor = penColor

    def _setLedOnBgColor(self, bgColor):
        self._ledOnBgColor = bgColor

    def _setLedOffPenColor(self, penColor):
        self._ledOffPenColor = penColor

    def _setLedOffBgColor(self, bgColor):
        self._ledOffBgColor = bgColor

    def _setAspectRatio(self, aspectRatio):
        self._aspectRatio = aspectRatio

    def _setBgBrush(self, bgBrush):
        if isinstance(bgBrush, Qt.QColor):
            bgBrush = Qt.QBrush(bgBrush, Qt.Qt.SolidPattern)
        self._bgBrush = bgBrush

    def _setUseFrame(self, useFrame):
        self._useFrame = useFrame

    def getLedOnPenColor(self):
        return self._ledOnPenColor

    def setLedOnPenColor(self, penColor):
        self._setLedOnPenColor(penColor)
        self._updatePensAndBrushes()

    def resetLedOnPenColor(self):
        self.setLenOnPenColor(Q7SegDigit.DftLedOnPenColor)

    def getLedOnBgColor(self):
        return self._ledOnBgColor

    def setLedOnBgColor(self, bgColor):
        self._setLedOnBgColor(bgColor)
        self._updatePensAndBrushes()

    def resetLedOnBgColor(self):
        self.setLedOnBgColor(Q7SegDigit.DftLedOnBgColor)

    def getLedOffPenColor(self):
        return self._ledOffPenColor

    def setLedOffPenColor(self, penColor):
        self._setLedOffPenColor(penColor)
        self._updatePensAndBrushes()

    def resetLedOffPenColor(self):
        self.setLenOffPenColor(Q7SegDigit.DftLedOffPenColor)

    def getLedOffBgColor(self):
        return self._ledOffBgColor

    def setLedOffBgColor(self, bgColor):
        self._setLedOffBgColor(bgColor)
        self._updatePensAndBrushes()

    def resetLedOffBgColor(self):
        self.setLedOffBgColor(Q7SegDigit.DftLedOffBgColor)

    def getBgBrush(self):
        return self._bgBrush

    def setBgBrush(self, bgBrush):
        self._setBgBrush(bgBrush)
        self.update()

    def resetBgBrush(self):
        self.setBgBrush(Q7SegDigit.DftBgBrush)

    def setValue(self, n):
        self._setValue(n)
        self.update()

    def getValue(self):
        return self._value

    def resetValue(self):
        self.setValue(Q7SegDigit.DftValue)

    def setLedPenWidth(self, w):
        self._setLedPenWidth(w)
        self._updatePensAndBrushes()

    def getLedPenWidth(self):
        return self._ledPenWidth

    def resetLedPenWidth(self):
        self.setLedPenWidth(Q7SegDigit.DftLenPenWidth)

    def setAspectRatio(self, apectRatio):
        self._setAspectRatio(apectRatio)
        self.update()

    def getAspectRatio(self):
        return self._aspectRatio

    def resetAspectRatio(self):
        self.setAspectRatio(Q7SegDigit.DftAspectRatio)

    def setUseFrame(self, useFrame):
        self._setUseFrame(useFrame)

    def getUseFrame(self):
        return self._useFrame

    def resetUseFrame(self):
        self.setUseFrame(Q7SegDigit.DftUseFrame)

    #: This property holds the led pen color when the led is light ON
    #:
    #: **Access functions:**
    #:
    #:     * :meth:`taurus.qt.qtgui.display.Q7SegDigit.getLedOnPenColor`
    #:     * :meth:`taurus.qt.qtgui.display.Q7SegDigit.setLedOnPenColor`
    #:     * :meth:`taurus.qt.qtgui.display.Q7SegDigit.resetLedOnPenColor`
    #:
    ledOnPenColor = Qt.pyqtProperty("QColor", getLedOnPenColor,
                                    setLedOnPenColor, resetLedOnPenColor)

    #: This property holds the led background color when the led is light ON
    #:
    #: **Access functions:**
    #:
    #:     * :meth:`taurus.qt.qtgui.display.Q7SegDigit.getLedOnBgColor`
    #:     * :meth:`taurus.qt.qtgui.display.Q7SegDigit.setLedOnBgColor`
    #:     * :meth:`taurus.qt.qtgui.display.Q7SegDigit.resetLedOnBgColor`
    #:
    ledOnBgColor = Qt.pyqtProperty("QColor", getLedOnBgColor,
                                   setLedOnBgColor, resetLedOnBgColor)

    #: This property holds the led pen color when the led is light OFF
    #:
    #: **Access functions:**
    #:
    #:     * :meth:`taurus.qt.qtgui.display.Q7SegDigit.getLedOffPenColor`
    #:     * :meth:`taurus.qt.qtgui.display.Q7SegDigit.setLedOffPenColor`
    #:     * :meth:`taurus.qt.qtgui.display.Q7SegDigit.resetLedOffPenColor`
    #:
    ledOffPenColor = Qt.pyqtProperty("QColor", getLedOffPenColor,
                                     setLedOffPenColor, resetLedOffPenColor)

    #: This property holds the led background color when the led is light OFF
    #:
    #: **Access functions:**
    #:
    #:     * :meth:`taurus.qt.qtgui.display.Q7SegDigit.getLedOffBgColor`
    #:     * :meth:`taurus.qt.qtgui.display.Q7SegDigit.setLedOffBgColor`
    #:     * :meth:`taurus.qt.qtgui.display.Q7SegDigit.resetLedOffBgColor`
    #:
    ledOffBgColor = Qt.pyqtProperty("QColor", getLedOffBgColor,
                                    setLedOffBgColor, resetLedOffBgColor)

    #: This property holds the background brush
    #:
    #: **Access functions:**
    #:
    #:     * :meth:`taurus.qt.qtgui.display.Q7SegDigit.getBgBrush`
    #:     * :meth:`taurus.qt.qtgui.display.Q7SegDigit.setBgBrush`
    #:     * :meth:`taurus.qt.qtgui.display.Q7SegDigit.resetBgBrush`
    #:
    bgBrush = Qt.pyqtProperty("QBrush", getBgBrush, setBgBrush, resetBgBrush)

    #: This property holds the pen width
    #:
    #: **Access functions:**
    #:
    #:     * :meth:`taurus.qt.qtgui.display.Q7SegDigit.getLedPenWidth`
    #:     * :meth:`taurus.qt.qtgui.display.Q7SegDigit.setLedPenWidth`
    #:     * :meth:`taurus.qt.qtgui.display.Q7SegDigit.resetLedPenWidth`
    #:
    ledPenWidth = Qt.pyqtProperty("int", getLedPenWidth,
                                  setLedPenWidth, resetLedPenWidth)

    #: This property holds wheater of not to draw a frame
    #:
    #: **Access functions:**
    #:
    #:     * :meth:`taurus.qt.qtgui.display.Q7SegDigit.getUseFrame`
    #:     * :meth:`taurus.qt.qtgui.display.Q7SegDigit.setUseFrame`
    #:     * :meth:`taurus.qt.qtgui.display.Q7SegDigit.resetUseFrame`
    #:
    useFrame = Qt.pyqtProperty("bool", getUseFrame, setUseFrame, resetUseFrame)

    #: This property holds the widget value
    #:
    #: **Access functions:**
    #:
    #:     * :meth:`taurus.qt.qtgui.display.Q7SegDigit.getValue`
    #:     * :meth:`taurus.qt.qtgui.display.Q7SegDigit.setValue`
    #:     * :meth:`taurus.qt.qtgui.display.Q7SegDigit.resetValue`
    #:
    value = Qt.pyqtProperty("QString", getValue, setValue, resetValue)


class Q7SegDisplay(Qt.QWidget):

    def __init__(self, qt_parent=None):
        Qt.QWidget.__init__(self, qt_parent)
        self.__init()

    def __init(self):
        l = Qt.QHBoxLayout()
        l.setSpacing(10)
        l.setContentsMargins(5, 5, 5, 5)
        self.setLayout(l)

        self._digits = []
        for i in range(5):
            d = Q7SegDigit()
            d.setUseFrame(False)
            d.setValue(i)
            l.addWidget(d, 0)
            self._digits.append(d)
        self.setAutoFillBackground(True)
        palette = Qt.QPalette()
        brush = Qt.QBrush(Qt.Qt.black)
        palette.setBrush(Qt.QPalette.Active, Qt.QPalette.Window, brush)
        self.setPalette(palette)


def __setBgBrush():
    global digitWidget
    color = Qt.QColorDialog.getColor(Qt.Qt.red)
    if color.isValid():
        digitWidget.setBgBrush(color)


def __setLedOnPenColor():
    global digitWidget
    color = Qt.QColorDialog.getColor(Qt.Qt.red)
    if color.isValid():
        digitWidget.setLedOnPenColor(color)


def __setLedOnBgColor():
    global digitWidget
    color = Qt.QColorDialog.getColor(Qt.Qt.red)
    if color.isValid():
        digitWidget.setLedOnBgColor(color)


def __setLedOffPenColor():
    global digitWidget
    color = Qt.QColorDialog.getColor(Qt.Qt.red)
    if color.isValid():
        digitWidget.setLedOffPenColor(color)


def __setLedOffBgColor():
    global digitWidget
    color = Qt.QColorDialog.getColor(Qt.Qt.red)
    if color.isValid():
        digitWidget.setLedOffBgColor(color)


def main1():
    import sys
    a = Qt.QApplication([])
    panel = Qt.QWidget()
    l = Qt.QHBoxLayout(panel)
    digitWidget = Q7SegDigit()
    digitWidget.setValue(int(sys.argv[1]))
    l.addWidget(digitWidget)
    l.addWidget(Q7SegDigit())
    l.addWidget(Q7SegDigit())
    l.setSpacing(0)
    panel.setVisible(True)
    a.exec_()


def main2():
    import sys
    a = Qt.QApplication([])
    dw = Q7SegDigit()
    dw.setValue(int(sys.argv[1]))
    dw.setVisible(True)
    print(dw)
    a.exec_()


def main3():
    a = Qt.QApplication([])
    dw = Q7SegDisplay()
    # dw.setValue(int(sys.argv[1]))
    dw.setVisible(True)
    a.exec_()


def main():
    global digitWidget
    a = Qt.QApplication([])
    panel = Qt.QWidget()
    l = Qt.QFormLayout(panel)
    digitWidget = Q7SegDigit()
    digitWidget.setStyleSheet("background-color:red;")
    valueLineEdit = Qt.QLineEdit(digitWidget.getValue())
    valueLineEdit.setMaxLength(1)
    ledPenWidthWidget = Qt.QSpinBox()
    ledPenWidthWidget.setRange(0, 20)
    ledPenWidthWidget.setValue(digitWidget.getLedPenWidth())
    bgBrushWidget = Qt.QPushButton("Bg brush")
    LedOnPenColor = Qt.QPushButton("ON pen color")
    LedOnBgColor = Qt.QPushButton("ON bg color")
    LedOffPenColor = Qt.QPushButton("OFF pen color")
    LedOffBgColor = Qt.QPushButton("OFF bg color")

    l.addRow("Value", digitWidget)
    l.addRow("Digit", valueLineEdit)
    l.addRow("Pen width", ledPenWidthWidget)
    l.addRow(bgBrushWidget)
    l.addRow(LedOnPenColor)
    l.addRow(LedOnBgColor)
    l.addRow(LedOffPenColor)
    l.addRow(LedOffBgColor)
    valueLineEdit.textChanged.connect(digitWidget.setValue)
    ledPenWidthWidget.valueChanged.connect(digitWidget.setLedPenWidth)
    bgBrushWidget.clicked.connect(__setBgBrush)
    LedOnPenColor.clicked.connect(__setLedOnPenColor)
    LedOnBgColor.clicked.connect(__setLedOnBgColor)
    LedOffPenColor.clicked.connect(__setLedOffPenColor)
    LedOffBgColor.clicked.connect(__setLedOffBgColor)
    panel.setVisible(True)
    a.exec_()


if __name__ == "__main__":
    main3()
