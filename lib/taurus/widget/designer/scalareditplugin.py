
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
scalareditplugin.py: 
"""

import taurusplugin

class TauWheelEditPlugin(taurusplugin.TauWidgetPlugin):

    """TauWheelEditPlugin(taurusplugin.TauWidgetPlugin)
    
    Provides a Python custom plugin for Qt Designer by implementing the
    QDesignerCustomWidgetPlugin via a PyQt-specific custom plugin class.
    """

    def getWidgetClass(self):
        import taurus.widget
        return taurus.widget.TauWheelEdit

    def getIconName(self):
        return 'lineedit.png'


class TauValueLineEditPlugin(taurusplugin.TauWidgetPlugin):

    """TauValueLineEditPlugin(taurusplugin.TauWidgetPlugin)
    
    Provides a Python custom plugin for Qt Designer by implementing the
    QDesignerCustomWidgetPlugin via a PyQt-specific custom plugin class.
    """

    def getWidgetClass(self):
        import taurus.widget
        return taurus.widget.TauValueLineEdit

    def getIconName(self):
        return 'lineedit.png'
        
class TauValueSpinBoxPlugin(taurusplugin.TauWidgetPlugin):

    """TauValueSpinBoxPlugin(taurusplugin.TauWidgetPlugin)
    
    Provides a Python custom plugin for Qt Designer by implementing the
    QDesignerCustomWidgetPlugin via a PyQt-specific custom plugin class.
    """

    def getWidgetClass(self):
        import taurus.widget
        return taurus.widget.TauValueSpinBox

    def getIconName(self):
        return 'spinbox.png'
    
class TauValueCheckBoxPlugin(taurusplugin.TauWidgetPlugin):

    """TauValueCheckBoxPlugin(taurusplugin.TauWidgetPlugin)
    
    Provides a Python custom plugin for Qt Designer by implementing the
    QDesignerCustomWidgetPlugin via a PyQt-specific custom plugin class.
    """

    def getWidgetClass(self):
        import taurus.widget
        return taurus.widget.TauValueCheckBox

    def getIconName(self):
        return 'checkbox.png'
