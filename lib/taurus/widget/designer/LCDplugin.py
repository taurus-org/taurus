
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
LCDplugin.py: 
"""

import taurusplugin
import taurus.core.util

try:
    from taurus.widget import TauLCDValue
    __SUPER_CLASS = taurusplugin.TauWidgetPlugin
except:
    __SUPER_CLASS = object
    l = taurus.core.util.Logger("Designer")
    l.info("TauLCDValue will not be available")
    
class TauLCDValuePlugin(__SUPER_CLASS):

    """TauLCDValuePlugin(taurusplugin.TauWidgetPlugin)
    
    Provides a Python custom plugin for Qt Designer by implementing the
    QDesignerCustomWidgetPlugin via a PyQt-specific custom plugin class.
    """

    def getWidgetClass(self):
        return TauLCDValue

    def getIconName(self):
        return 'lcdnumber.png'
