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

"""Device pool extension for taurus Qt"""

__all__ = ["QPool",
           "registerExtensions"]

import taurus.core
from taurus.core.tango.sardana.poolv3 import Pool

from PyQt4 import Qt

CHANGE_EVTS = (taurus.core.TaurusEventType.Change, taurus.core.TaurusEventType.Periodic)

class QPool(Qt.QObject, Pool):
    
    def __init__(self, name, qt_parent=None, **kw):
        self.call__init__wo_kw(Qt.QObject, qt_parent)
        self.call__init__(Pool, name, **kw)



def registerExtensions():
    """Registers the pool extensions in the :class:`taurus.core.tango.TangoFactory`"""
    import taurus
    import taurus.core.tango.sardana.poolv3
    taurus.core.tango.sardana.poolv3.registerExtensions()
    factory = taurus.Factory()
    factory.registerDeviceClass('Pool', QPool)
