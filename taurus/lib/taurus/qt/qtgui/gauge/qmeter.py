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

"""This module contains a collection of Qt meter widgets"""

__docformat__ = 'restructuredtext'

import sys
import math

from taurus.qt import Qt
from taurus.qt.qtgui.display import QPixmapWidget

class QBaseMeter(QPixmapWidget):
    
    DefaultMinimum        = 0.0
    DefaultMaximum        = 100.0
    DefaultMinimumAlarm   = 10.0
    DefaultMaximumAlarm   = 90.0
    DefaultMinimumWarning = 20.0
    DefaultMaximumWarning = 80.0
    DefaultValue          = 0.0
    DefaultValueOffset    = 0.0
    DefaultDigitOffset    = 1.0
    DefaultSteps          = 8
    DefaultValueFont      = Qt.QFont()
    DefaultDigitFont      = Qt.QFont()
    
    def __init__(self, parent=None, designMode=None):
        self._minimum = self._min = self.DefaultMinimum
        self._maximum = self._max = self.DefaultMaximum
        self._minimumWarning = self.DefaultMinimumWarning
        self._maximumWarning = self.DefaultMaximumWarning
        self._minimumAlarm = self.DefaultMinimumAlarm
        self._maximumAlarm = self.DefaultMaximumAlarm
        self._value = self.DefaultValue
        self._valueOffset = self.DefaultValueOffset
        self._digitOffset = self.DefaultDigitOffset
        self._valueFont = self.DefaultValueFont
        self._digitFont = self.DefaultDigitFont
        #self._valueFont.setPointSize(25)
        #self._digitFont.setPointSize(20)
        self._steps = self.DefaultSteps
        self._autoRangeIt()
        QPixmapWidget.__init__(self, parent=parent, designMode=designMode)

    def _autoRangeIt(self):
        ret = self._rangeIt(self._minimum, self._maximum, self._min, self._max,
                            self._steps, True)
        self._min, self._max, ret = ret
        self._setDirty()
        return ret

    def _rangeIt(self, minimum, maximum, orig_min, orig_max, steps, left=False, inc=5.0):
        _min, _max, scale, factor = minimum, maximum, 0.0, 0.0
        diff = abs(_max - _min)
        
        # calculate increment
        while (inc * steps > (maximum - minimum)):
            new_inc = inc / 10
            if new_inc > 0: inc = new_inc
            else: break
        
        # calculate scale
        while diff > scale:
            factor += inc
            scale = factor * steps 
        
        while True:
            if _max < 0: _max = _min - math.fmod(_min, steps)
            else: _max = 0.0
            while _max < maximum: _max += factor
            _min = _max - scale
            if _min < minimum:
                break
            factor += inc
            scale = factor * steps
        
        if left:
            while (_min + factor) <= minimum:
                _min += factor
                _max += factor
        return _min, _max, (_min != orig_min) or (_max != orig_max)
         
        
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # QT property definition
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    
    def getMinimum(self):
        return self._minimum
    
    def setMinimum(self, min):
        self._minimum = float(min)
        self._autoRangeIt() 
        self.update()

    def resetMinimum(self):
        self.setMinimum(self.DefaultMinimum)
    
    def getMaximum(self):
        return self._maximum
    
    def setMaximum(self, max):
        self._maximum = float(max)
        self._autoRangeIt()
        self.update()

    def resetMaximum(self):
        self.setMaximum(self.DefaultMaximum)

    def getMinimumWarning(self):
        return self._minimumWarning
    
    def setMinimumWarning(self, min):
        self._minimumWarning = float(min)
        self._autoRangeIt() 
        self.update()

    def resetMinimumWarning(self):
        self.setMinimumWarning(self.DefaultMinimumWarning)
    
    def getMaximumWarning(self):
        return self._maximumWarning
    
    def setMaximumWarning(self, max):
        self._maximumWarning = float(max)
        self._autoRangeIt()
        self.update()

    def resetMaximumWarning(self):
        self.setMaximum(self.DefaultMaximumWarning)

    def getMinimumAlarm(self):
        return self._minimumAlarm
    
    def setMinimumAlarm(self, min):
        self._minimumAlarm = float(min)
        self._autoRangeIt() 
        self.update()

    def resetMinimumAlarm(self):
        self.setMinimumAlarm(self.DefaultMinimumAlarm)
    
    def getMaximumAlarm(self):
        return self._maximumAlarm
    
    def setMaximumAlarm(self, max):
        self._maximumAlarm = float(max)
        self._autoRangeIt()
        self.update()

    def resetMaximumAlarm(self):
        self.setMaximumAlarm(self.DefaultMaximumAlarm)

    def getValue(self):
        return self._value
    
    def setValue(self, value):
        self._value = float(value)
        self.update()

    def resetValue(self):
        self.setValue(self.DefaultValue)

    def getSteps(self):
        return self._steps
    
    def setSteps(self, steps):
        steps = int(steps)
        if steps < 2:
            raise Exception("Invalid steps. Must be >= 2")
        self._steps = steps
        self._autoRangeIt()
        self.update()

    def resetSteps(self):
        self.setSteps(self.DefaultSteps)
        
    def getValueOffset(self):
        return self._valueOffset
    
    def setValueOffset(self, valueOffset):
        self._valueOffset = float(valueOffset)
        self._autoRangeIt()
        self.update()

    def resetValueOffset(self):
        self.setValueOffset(self.DefaultValueOffset)

    def getDigitOffset(self):
        return self._digitOffset
    
    def setDigitOffset(self, digitOffset):
        self._digitOffset = float(digitOffset)
        self._autoRangeIt()
        self.update()

    def resetDigitOffset(self):
        self.setDigitOffset(self.DefaultDigitOffset)
                
    def getValueFont(self):
        return self._valueFont
    
    def setValueFont(self, valueFont):
        self._valueFont = valueFont
        self._setDirty()
        self.update()

    def resetValueFont(self):
        self.setValue(self.DefaultValueFont)
        
    def getDigitFont(self):
        return self._digitFont
    
    def setDigitFont(self, digitFont):
        self._digitFont = digitFont
        self._setDirty()
        self.update()

    def resetDigitFont(self):
        self.setDigitFont(self.DefaultDigitFont)

    @classmethod
    def getQtDesignerPluginInfo(cls):
        # explicitly do NOT expose this base meter to the designer
        return
    
    #: This property holds the minimum value
    #:
    #: **Access functions:**
    #:
    #:     * :meth:`QBaseMeter.getMinimum`
    #:     * :meth:`QBaseMeter.setMinimum`
    #:     * :meth:`QBaseMeter.resetMinimum`
    minimum = Qt.pyqtProperty("double", getMinimum, setMinimum,
                              resetMinimum, doc="minimum value")

    #: This property holds the maximum value
    #:
    #: **Access functions:**
    #:
    #:     * :meth:`QBaseMeter.getMaximum`
    #:     * :meth:`QBaseMeter.setMaximum`
    #:     * :meth:`QBaseMeter.resetMaximum`
    maximum = Qt.pyqtProperty("double", getMaximum, setMaximum,
                              resetMaximum, doc="maximum value")
                              
    #: This property holds the value
    #:
    #: **Access functions:**
    #:
    #:     * :meth:`QBaseMeter.getValue`
    #:     * :meth:`QBaseMeter.setValue`
    #:     * :meth:`QBaseMeter.resetValue`
    value = Qt.pyqtProperty("double", getValue, setValue, resetValue, doc="value")

    #: This property holds the minimum alarm value
    #:
    #: **Access functions:**
    #:
    #:     * :meth:`QBaseMeter.getMinimumAlarm`
    #:     * :meth:`QBaseMeter.setMinimumAlarm`
    #:     * :meth:`QBaseMeter.resetMinimumAlarm`
    minimumAlarm = Qt.pyqtProperty("double", getMinimumAlarm, setMinimumAlarm,
                                   resetMinimumAlarm, doc="minimum alarm")

    #: This property holds the maximum alarm value
    #:
    #: **Access functions:**
    #:
    #:     * :meth:`QBaseMeter.getMaximumAlarm`
    #:     * :meth:`QBaseMeter.setMaximumAlarm`
    #:     * :meth:`QBaseMeter.resetMaximumAlarm`
    maximumAlarm = Qt.pyqtProperty("double", getMaximumAlarm, setMaximumAlarm,
                                   resetMaximumAlarm, doc="maximum alarm")

    #: This property holds the minimum warning value
    #:
    #: **Access functions:**
    #:
    #:     * :meth:`QBaseMeter.getMinimumWarning`
    #:     * :meth:`QBaseMeter.setMinimumWarning`
    #:     * :meth:`QBaseMeter.resetMinimumWarning`
    minimumWarning = Qt.pyqtProperty("double", getMinimumWarning, setMinimumWarning,
                                   resetMinimumWarning, doc="minimum warning")

    #: This property holds the maximum warning value
    #:
    #: **Access functions:**
    #:
    #:     * :meth:`QBaseMeter.getMaximumWarning`
    #:     * :meth:`QBaseMeter.setMaximumWarning`
    #:     * :meth:`QBaseMeter.resetMaximumWarning`
    maximumWarning = Qt.pyqtProperty("double", getMaximumWarning, setMaximumWarning,
                                   resetMaximumWarning, doc="maximum warning")

    #: This property holds the number of steps
    #:
    #: **Access functions:**
    #:
    #:     * :meth:`QBaseMeter.getSteps`
    #:     * :meth:`QBaseMeter.setSteps`
    #:     * :meth:`QBaseMeter.resetSteps`
    steps = Qt.pyqtProperty("int", getSteps, setSteps, resetSteps, doc="steps")
    
    #: This property holds the value offset
    #:
    #: **Access functions:**
    #:
    #:     * :meth:`QBaseMeter.getValueOffset`
    #:     * :meth:`QBaseMeter.setValueOffset`
    #:     * :meth:`QBaseMeter.resetValueOffset`
    valueOffset = Qt.pyqtProperty("double", getValueOffset, setValueOffset,
                                  resetValueOffset, doc="value offset")

    #: This property holds the digit offset
    #: Used to place scale digits offset. On manometer distance from the 
    #: center on thermometer distance form left
    #:
    #: **Access functions:**
    #:
    #:     * :meth:`QBaseMeter.getDigitOffset`
    #:     * :meth:`QBaseMeter.setDigitOffset`
    #:     * :meth:`QBaseMeter.resetDigitOffset`
    digitOffset = Qt.pyqtProperty("double", getDigitOffset, setDigitOffset,
                                  resetDigitOffset, doc="digit offset")
    
    #: This property holds the value font
    #:
    #: **Access functions:**
    #:
    #:     * :meth:`QBaseMeter.getValueFont`
    #:     * :meth:`QBaseMeter.setValueFont`
    #:     * :meth:`QBaseMeter.resetValueFont`
    valueFont = Qt.pyqtProperty("QFont", getValueFont, setValueFont,
                                resetValueFont, doc="value font")

    #: This property holds the digit font
    #:
    #: **Access functions:**
    #:
    #:     * :meth:`QBaseMeter.getDigitFont`
    #:     * :meth:`QBaseMeter.setDigitFont`
    #:     * :meth:`QBaseMeter.resetDigitFont`
    digitFont = Qt.pyqtProperty("QFont", getDigitFont, setDigitFont,
                                resetDigitFont, doc="digit font")

Point = Qt.QPointF
Color = Qt.QColor
RadialGradient = Qt.QRadialGradient
Brush = Qt.QBrush
Rect = Qt.QRect
Polygon = Qt.QPolygon

class QManoMeter(QBaseMeter):

    DefaultAngle = 240
    DefaultFrameWidth = 40
    DefaultValueOffset = -100
    DefaultDigitOffset = 105
    DefaultShowScaleColor = True
    DefaultShowScaleTicks = True
    DefaultShowScaleText = True
    DefaultShowValueText = True
    
    def __init__(self, parent=None, designMode=False):
        self._angle = self.DefaultAngle
        self._frameWidth = self.DefaultFrameWidth
        self._showScaleColor = self.DefaultShowScaleColor
        self._showScaleTicks = self.DefaultShowScaleTicks
        self._showScaleText = self.DefaultShowScaleText
        self._showValueText = self.DefaultShowValueText
        self._bg_cache = None
        QBaseMeter.__init__(self, parent=parent, designMode=designMode)

    def minimumSizeHint(self):
        return Qt.QSize(64, 64)

    def _initCoords(self, painter):
        w, h = self.width(), self.height()
        side = min(w, h)
        painter.translate(w/2, h/2)
        painter.scale(side/335.0, side/335.0)
    
    @property
    def bg_cache(self):
        if self._bg_cache is not None:
            return self._bg_cache

        back1 = RadialGradient(Point(0.0, 0.0), 180.0, Point(-35.0, 145.0))
        back1.setColorAt(0.0, Color(250, 250, 250))
        back1.setColorAt(1.0, Color(20, 20, 20))
        back1Brush = Brush(back1)

        back2 = RadialGradient(Point(0.0, 0.0), 225.0, Point(76.5, 135.0))
        back2.setColorAt(0.0, Color(10, 10, 10))
        back2.setColorAt(1.0, Color(250, 250, 250))
        back2Brush = Brush(back2)
        
        shield = RadialGradient(Point(0, 0), 182, Point(-12.0, -15.0))
        shield.setColorAt(0.0, Qt.Qt.white)
        shield.setColorAt(0.5, Color(240, 240, 240))
        shield.setColorAt(1.0, Color(215, 215, 215))
        shieldBrush = Brush(shield)
        
        tickTriangle = Polygon([-6, 141, 6, 141, 0, 129])
        
        self._bg_cache = [back1Brush, back2Brush, shieldBrush, tickTriangle] 
        return self._bg_cache

    def recalculatePixmap(self):
        pixmap = Qt.QPixmap(self.size())
        pixmap.fill(Qt.Qt.transparent)
        painter = Qt.QPainter(pixmap)
        painter.setRenderHint(Qt.QPainter.Antialiasing)
        self._initCoords(painter)
        
        pen = Qt.QPen(Qt.Qt.black)
        pen.setWidth(4)
        
        fw = self.frameWidth
        back1Brush, back2Brush, shieldBrush, tickTriangle = self.bg_cache
        painter.setBrush(back1Brush)
        painter.drawEllipse(-162, -162, 324, 324)
        painter.setPen(Qt.Qt.NoPen)
        painter.setBrush(back2Brush)
        painter.drawEllipse(-162+fw/4, -162+fw/4, 324-fw/2, 324-fw/2)

        # internal scale circle
        painter.setBrush(shieldBrush)
        painter.setPen(pen)
        painter.drawEllipse(-162+fw/2, -162+fw/2, 324-fw, 324-fw)
        
        painter.setPen(Qt.Qt.NoPen)
        steps = self._steps
        angle = self._angle
        minimum, maximum = self._min, self._max
        minWarning,  maxWarning = self.minimumWarning,  self.maximumWarning
        minAlarm,  maxAlarm = self.minimumAlarm,  self.maximumAlarm
        fullrange = maximum - minimum
        min_angle = (360.0 - angle) / 2.0
        max_angle = 360.0 - min_angle

        if self.showScaleColor:
            redBrush = Brush(Qt.Qt.red)
            orangeBrush = Brush(Color(255, 127, 0))
            greenBrush = Brush(Qt.Qt.green)
            
            painter.save()
            scale_rect = Rect(-162+fw/2+1, -162+fw/2+1, 324-fw-2, 324-fw-2)
            min_alarm_angle = (angle * (minAlarm - minimum) / fullrange)
            painter.rotate(90 + min_angle + min_alarm_angle)
            painter.setBrush(redBrush)
            if minimum <= minAlarm and minAlarm < minWarning:
                painter.drawPie(scale_rect, 0, min_alarm_angle*16)
    
            min_warning_angle =  (angle * (minWarning - minAlarm) / fullrange)
            painter.rotate(min_warning_angle)
            painter.setBrush(orangeBrush)
            if minAlarm <= minWarning and minWarning < maxWarning:
                painter.drawPie(scale_rect, 0, min_warning_angle*16)
    
            max_warning_angle = (angle * (maxWarning - minWarning) / fullrange)
            painter.rotate(max_warning_angle)
            painter.setBrush(greenBrush)
            if minWarning <= maxWarning and maxWarning < maxAlarm:
                painter.drawPie(scale_rect, 0, max_warning_angle*16)
    
            max_alarm_angle = (angle * (maxAlarm - maxWarning) / fullrange)
            painter.rotate(max_alarm_angle)
            painter.setBrush(orangeBrush)
            if maxWarning <= maxAlarm and maxAlarm < maximum:
                painter.drawPie(scale_rect, 0, max_alarm_angle*16)
            
            max_angle = (angle * (maximum - maxAlarm) / fullrange)
            painter.rotate(max_angle)
            painter.setBrush(redBrush)
            if maxAlarm <= maximum:
                painter.drawPie(scale_rect, 0, max_angle*16)
    
            painter.restore()

            painter.setBrush(shieldBrush)
            painter.drawEllipse(-162+fw/2+12, -162+fw/2+12, 324-fw-2-24, 324-fw-2-24)
        painter.rotate(min_angle)

        # draw ticks
        if self.showScaleTicks:
            painter.save()
            painter.setBrush(Brush(Qt.Qt.black))
            line_length = 10
            tick_steps = 4*steps
            tick_stepsf = float(tick_steps)
            angle_step = angle / tick_stepsf
            for i in range(tick_steps+1):
                painter.setPen(pen)
                if i % 4: painter.drawLine(0, 140, 0, 140-line_length)
                else:
                    painter.setPen(Qt.Qt.NoPen)
                    painter.drawConvexPolygon(tickTriangle)
    
                painter.rotate(angle_step)
                pen.setWidth(3)
                if i % 2:
                    line_length = 10
                else:
                    line_length = 5
            painter.restore()
        
        digitOffset = self.digitOffset
        if self.showScaleText and digitOffset:
            painter.setPen(Qt.Qt.black)
            painter.rotate(-min_angle)
            painter.setFont(self.digitFont)
            stepsf = float(steps)
            angle_step = angle / stepsf
            min_angle = 90 + min_angle
            for i in range(steps+1):
                v = minimum + i*fullrange/ stepsf
                if abs(v) < 0.000001: v = 0.0;
                val = Qt.QString(str(v))
                textSize = painter.fontMetrics().size(Qt.Qt.TextSingleLine, val)
                painter.save()
                ang = min_angle+(i*angle_step)
                ang = math.pi*ang/180.0 # convert to radians
                painter.translate(digitOffset * math.cos(ang), digitOffset * math.sin(ang))
                painter.drawText(Point(textSize.width()/-2.0, textSize.height()/4.0), val)
                painter.restore()
        return pixmap
    
    _Hand = -4, 0, -1, 129, 1, 129, 4, 0, 8,-50, -8,-50
    
    def paintEvent(self, paintEvent):
        QBaseMeter.paintEvent(self, paintEvent)
        painter = Qt.QPainter(self)
        painter.setRenderHint(Qt.QPainter.Antialiasing)
        self._initCoords(painter)
        hand = self._Hand
        path = Qt.QPainterPath(Point(hand[0], hand[1]))
        for i in range(2,10,2):
            path.lineTo(hand[i], hand[i+1])
        
        path.cubicTo( 8.1, -51.0,  5.0, -48.0,  0.0, -48.0)
        path.cubicTo(-5.0, -48.0, -8.1, -51.0, -8.0, -50.0)
        
        value = self.value
        minimum, maximum = self._min, self._max
        minWarning,  maxWarning = self.minimumWarning,  self.maximumWarning
        minAlarm,  maxAlarm = self.minimumAlarm,  self.maximumAlarm
        fullrange = maximum - minimum
        
        painter.save()
        painter.rotate(60.0)
        painter.setPen(Qt.Qt.NoPen)
        painter.setBrush(Brush(Qt.Qt.black))
        
        painter.rotate(((value - minimum) * 240.0) / fullrange)
        painter.drawPath(path)
        painter.drawEllipse(-10, -10, 20, 20)
        painter.restore()

        offset = self.valueOffset
        if offset and self._showValueText:
            if value <= minAlarm or value >= maxAlarm:
                painter.setPen(Qt.Qt.red)
            painter.setFont(self.valueFont)
            s = Qt.QString(str(value))
            size = painter.fontMetrics().size(Qt.Qt.TextSingleLine, s)
            painter.drawText(Point(size.width() / -2.0, int(0-offset)), s)

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # QT property definition
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    def getAngle(self):
        return self._angle
    
    def setAngle(self, angle):
        self._angle = float(angle)
        self._autoRangeIt()
        self.update()

    def resetAngle(self):
        self.setAngle(self.DefaultAngle)

    def getFrameWidth(self):
        return self._frameWidth
    
    def setFrameWidth(self, frameWidth):
        self._frameWidth = int(frameWidth)
        self._autoRangeIt()
        self.update()

    def resetFrameWidth(self):
        self.setFrameWidth(self.DefaultFrameWidth)

    def getShowScaleColor(self):
        return self._showScaleColor
    
    def setShowScaleColor(self, showScaleColor):
        self._showScaleColor = bool(showScaleColor)
        self._autoRangeIt()
        self.update()

    def resetShowScaleColor(self):
        self.setShowScaleColor(self.DefaultShowScaleColor)

    def getShowScaleTicks(self):
        return self._showScaleTicks
    
    def setShowScaleTicks(self, showScaleTicks):
        self._showScaleTicks = bool(showScaleTicks)
        self._autoRangeIt()
        self.update()

    def resetShowScaleTicks(self):
        self.setShowScaleTicks(self.DefaultShowScaleTicks)

    def getShowScaleText(self):
        return self._showScaleText
    
    def setShowScaleText(self, showScaleText):
        self._showScaleText = bool(showScaleText)
        self._autoRangeIt()
        self.update()

    def resetShowScaleText(self):
        self.setShowScaleText(self.DefaultShowScaleText)

    def resetShowScaleTicks(self):
        self.setShowScaleTicks(self.DefaultShowScaleTicks)

    def getShowValueText(self):
        return self._showValueText
    
    def setShowValueText(self, showValueText):
        self._showValueText = bool(showValueText)
        self.update()

    def resetShowValueText(self):
        self.setShowValueText(self.DefaultShowValueText)

    @classmethod
    def getQtDesignerPluginInfo(cls):
        return {
            'module' : 'taurus.qt.qtgui.gauge',
            'group' : 'Taurus Display',
            'icon' : ":/designer/circular_gauge.png",
            'container' : False,
        }

    #: This property holds the angle
    #:
    #: **Access functions:**
    #:
    #:     * :meth:`QManoMeter.getAngle`
    #:     * :meth:`QManoMeter.seAngle`
    #:     * :meth:`QManoMeter.resetAngle`
    angle = Qt.pyqtProperty("double", getAngle, setAngle, resetAngle, doc="angle")


    #: This property holds the frame width
    #:
    #: **Access functions:**
    #:
    #:     * :meth:`QManoMeter.getFrameWidth`
    #:     * :meth:`QManoMeter.setFrameWidth`
    #:     * :meth:`QManoMeter.resetFrameWidth`
    frameWidth = Qt.pyqtProperty("int", getFrameWidth, setFrameWidth,
                                 resetFrameWidth, doc="frame width")

    #: This property holds if should show scale color 
    #:
    #: **Access functions:**
    #:
    #:     * :meth:`QManoMeter.getShowScaleColor`
    #:     * :meth:`QManoMeter.setShowScaleColor`
    #:     * :meth:`QManoMeter.resetShowScaleColor`
    showScaleColor = Qt.pyqtProperty("bool", getShowScaleColor,
                                     setShowScaleColor, resetShowScaleColor,
                                     doc="show scale color")

    #: This property holds if should show scale ticks 
    #:
    #: **Access functions:**
    #:
    #:     * :meth:`QManoMeter.getShowScaleTicks`
    #:     * :meth:`QManoMeter.setShowScaleTicks`
    #:     * :meth:`QManoMeter.resetShowScaleTicks`
    showScaleTicks = Qt.pyqtProperty("bool", getShowScaleTicks,
                                     setShowScaleTicks, resetShowScaleTicks,
                                     doc="show scale ticks")

    #: This property holds if should show scale text 
    #:
    #: **Access functions:**
    #:
    #:     * :meth:`QManoMeter.getShowScaleText`
    #:     * :meth:`QManoMeter.setShowScaleText`
    #:     * :meth:`QManoMeter.resetShowScaleText`
    showScaleText = Qt.pyqtProperty("bool", getShowScaleText,
                                    setShowScaleText, resetShowScaleText,
                                    doc="show scale text")

    #: This property holds if should show value text 
    #:
    #: **Access functions:**
    #:
    #:     * :meth:`QManoMeter.getShowValueText`
    #:     * :meth:`QManoMeter.setShowValueText`
    #:     * :meth:`QManoMeter.resetShowValueText`
    showValueText = Qt.pyqtProperty("bool", getShowValueText,
                                    setShowValueText, resetShowValueText,
                                    doc="show value text")
                            
def main():
    import demo.qmeterdemo
    demo.qmeterdemo.demo()

if __name__ == "__main__":
    main()
    
    
    