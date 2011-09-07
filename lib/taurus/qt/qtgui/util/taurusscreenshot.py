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

"""This module provides Qt color management for taurus"""

__all__ = ["Grabber", "grabWidget"]

__docformat__ = 'restructuredtext'

import time
import os.path
from taurus.qt import Qt

class Grabber(Qt.QThread):
    
    def __init__(self, widget, fileName, period, parent=None):
        Qt.QThread.__init__(self, parent=parent)
        if period <= 0:
            raise ValueError("period MUST be greater than 0")
        self._widget = widget
        self._fileName = fileName
        self._period = period
        self._continue = True
        self.connect(self, Qt.SIGNAL("grab"), self.onGrab)
        
    def run(self):
        period = self._period
        while self._continue:
            self.emit(Qt.SIGNAL("grab"))
            time.sleep(period)
    
    def stop(self):
        self._continue = False
    
    def onGrab(self):
        widget, fileName = self._widget, self._fileName
        print "grabbing",fileName
        Grabber._grabWidget(widget, fileName)
    
    @staticmethod
    def _grabWidget(widget, fileName):
        pixmap = Qt.QPixmap.grabWidget(widget)
        pixmap.save(fileName, quality=100)

    @staticmethod
    def grabWidget(widget, fileName, period=None):
        """Grabs the given widget into the given image filename. If period is
        not given (or given with None) means grab immediately once and return.
        If period is given and >0 means grab the image every period seconds
        
        .. warning:
            if period is given, you **MUST** keep a reference to the Grabber
            object returned by this function

        :param Qt.QWidget widget: the qt widget to be grabbed
        :param str fileName: the name of the image file
        :param float period
        """
        if period is None:
            return Grabber._grabWidget(widget, fileName)
        ret = Grabber(widget, fileName, period)
        ret.start()
        return ret


def grabWidget(widget, fileName, period=None):
    """Grabs the given widget into the given image filename. If period is
    not given (or given with None) means grab immediately once and return.
    If period is given and >0 means grab the image every period seconds
    
    .. warning:
        if period is given, you **MUST** keep a reference to the Grabber
        object returned by this function
    
    :param Qt.QWidget widget: the qt widget to be grabbed
    :param str fileName: the name of the image file
    :param float period
    """
    return Grabber.grabWidget(widget, fileName, period=period)
    
