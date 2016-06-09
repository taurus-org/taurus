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

"""This module provides Qt color management for taurus"""

__all__ = ["Grabber", "grabWidget"]

__docformat__ = 'restructuredtext'

import time
import threading
import os.path

from taurus.external.qt import Qt
from taurus.core.util.log import Logger

_LOGGER = None


def _getLogger():
    global _LOGGER
    if _LOGGER is None:
        _LOGGER = Logger('Grabber')
    return _LOGGER


class GrabberThread(threading.Thread):

    def __init__(self, widget, fileName, period):
        threading.Thread.__init__(self, name="Grabber")
        self.daemon = True
        if period <= 0:
            raise ValueError("period MUST be greater than 0")
        self._period = period
        self._continue = True
        self._grabber = Grabber(widget, fileName)

    def run(self):
        period = self._period
        while self._continue:
            self._grabber.grabTrigger()
            time.sleep(period)

    def stop(self):
        self._continue = False


class Grabber(Qt.QObject, Logger):

    grab = Qt.pyqtSignal()

    def __init__(self, widget, fileName):
        Qt.QObject.__init__(self)
        Logger.__init__(self)
        self._widget = widget
        self._fileName = fileName
        self.grab.connect(self.onGrab)

    def grabTrigger(self):
        self.grab.emit()

    def onGrab(self):
        Grabber._grabWidget(self._widget, self._fileName)

    @staticmethod
    def _grabWidget(widget, fileName):
        _getLogger().debug("Grabbing widget to '%s':", fileName)
        try:
            pixmap = Qt.QPixmap.grabWidget(widget)
            if fileName.endswith('.svg'):
                from taurus.external.qt import QtSvg
                generator = QtSvg.QSvgGenerator()
                generator.setFileName(fileName)
                generator.setSize(pixmap.size())
                if hasattr(generator, 'setViewBox'):
                    viewBox = Qt.QRect(Qt.QPoint(0, 0), pixmap.size())
                    generator.setViewBox(viewBox)
                generator.setTitle("Taurus widget")
                generator.setDescription("An SVG drawing created by the taurus "
                                         "widget grabber")
                painter = Qt.QPainter()
                painter.begin(generator)
                try:
                    painter.drawPixmap(0, 0, -1, -1, pixmap)
                finally:
                    painter.end()
            else:
                pixmap.save(fileName, quality=100)
        except:
            _getLogger().warning("Could not save file into '%s':", fileName,
                                 exc_info=1)

    @staticmethod
    def grabWidget(widget, fileName, period=None):
        """Grabs the given widget into the given image filename. If period is
        not given (or given with None) means grab immediately once and return.
        If period is given and >0 means grab the image every period seconds

        .. warning:
            this method **MUST** be called from the same thread which created
            the widget

        :param widget: (Qt.QWidget) the qt widget to be grabbed
        :param fileName: (str) the name of the image file
        :param period: (float) period (seconds)
        """
        if period is None:
            return Grabber._grabWidget(widget, fileName)
        ret = GrabberThread(widget, fileName, period)
        ret.start()
        return ret


def grabWidget(widget, fileName, period=None):
    return Grabber.grabWidget(widget, fileName, period=period)

grabWidget.__doc__ = Grabber.grabWidget.__doc__
