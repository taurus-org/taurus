
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
taurusplotplugin.py: 
"""

import taurusplugin
import taurus.core.util

try:
    from taurus.widget.trees import TauTreeWidget
    __SUPER_CLASS = taurusplugin.TauWidgetPlugin
except:
    __SUPER_CLASS = object
    l = taurus.core.util.Logger("Designer")
    l.info("TauTreeWidget will not be available")

class TauTreeWidgetPlugin(__SUPER_CLASS):

    """TauTreeWidget(taurusplugin.TauWidgetPlugin)
    
    Provides a Python custom plugin for Qt Designer by implementing the
    QDesignerCustomWidgetPlugin via a PyQt-specific custom plugin class.
    """

    def getWidgetClass(self):
        return TauTreeWidget

    def getIconName(self):
        return 'devs_tree.png'

    def includeFile(self):
        return "taurus.widget.trees"

