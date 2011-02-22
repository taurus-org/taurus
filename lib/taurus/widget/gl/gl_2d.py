
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
###########################################################################

"""
gl.py: taurus wrapping of opengl
"""

from PyQt4 import Qt

import taurus
import taurus.core
import taurus.core.util
import taurus.widget

import time
class FPS:
    
    def __init__(self):
        self.__frame_nb = 0
        self.__frame_count = 0
        self.__last_time = 0
        self.__last_fps = 0

    def tick(self):
        self.__frame_nb += 1
        self.__frame_count += 1
        curr_time = time.time()
        dt = curr_time - self.__last_time
        self.__last_fps = self.__frame_count / dt
        if dt > 1.0:
            self.__last_time = curr_time
            self.__frame_count = 0
            return True
        return False
    
    @property
    def fps(self):
        return self.__last_fps
   
class Renderer(object):
    
    def __init__(self):
        gradient = Qt.QLinearGradient(Qt.QPointF(50, -20), Qt.QPointF(80, 20))
        gradient.setColorAt(0.0, Qt.Qt.white)
        gradient.setColorAt(1.0, Qt.QColor(0xa6, 0xce, 0x39))

        self._background = Qt.QBrush(Qt.QColor(64, 32, 64))
        self._circleBrush = Qt.QBrush(gradient)
        self._circlePen = Qt.QPen(Qt.Qt.black)
        self._circlePen.setWidth(1)
        self._textPen = Qt.QPen(Qt.Qt.white)
        self._textFont = Qt.QFont()
        self._textFont.setPixelSize(50)
        self._fps = FPS()
        self._stats = []
        
    def render(self, painter, event, elapsed):
        
        painter.fillRect(event.rect(), self._background)
        painter.translate(200, 200)

        painter.save()
        painter.setBrush(self._circleBrush)
        painter.setPen(self._circlePen)
        painter.rotate(elapsed * 0.030)

        r = elapsed/1000.0
        n = 30
        for i in xrange(n):
            painter.rotate(30)
            radius = 0 + 120.0*((i+r)/n)
            circleRadius = 1 + ((i+r)/n)*20;
            painter.drawEllipse(Qt.QRectF(radius, -circleRadius,
                                          circleRadius*2, circleRadius*2))
        painter.restore()

        painter.setPen(self._textPen)
        painter.setFont(self._textFont)
        painter.drawText(Qt.QRect(-50, -50, 100, 100), Qt.Qt.AlignCenter, "Qt")
        if self._fps.tick():
            self._stats.append(self._fps.fps)

class GLWidget(Qt.QGLWidget):
    
    def __init__(self, renderer = None, parent = None):
        format = Qt.QGLFormat(Qt.QGL.SampleBuffers)
        Qt.QGLWidget.__init__(self, format, parent)
        self._renderer = renderer or Renderer()
        self._elapsed = 0
        self.setFixedSize(400, 400)
        self.setAutoFillBackground(False)
    
    def animate(self):
        timer = self.sender()
        self._elapsed = (self._elapsed + timer.interval()) % 1000
        self.repaint()
    
    def paintEvent(self, event):
        painter = Qt.QPainter()
        painter.begin(self)
        #painter.setRenderHint(Qt.QPainter.Antialiasing)
        self._renderer.render(painter, event, self._elapsed)
        painter.end()


def main():
    import sys
    renderer = Renderer()
    app = Qt.QApplication(sys.argv)

    panel = Qt.QWidget()
    panel.setWindowTitle("OpenGL Demo")
    l = Qt.QHBoxLayout()
    panel.setLayout(l)
    w = GLWidget()
    l.addWidget(w)
    panel.setVisible(True)
    timer = Qt.QTimer(panel)
    Qt.QObject.connect(timer, Qt.SIGNAL("timeout()"), w.animate)
    timer.start(10)

    r = app.exec_()
    for i in w._renderer._stats[1:]:
        print "%6.2f" % i
    sys.exit(r)


if __name__ == "__main__":
    main()
    