
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
containersplugin.py: 
"""

from PyQt4 import Qt

import taurusplugin
import taurus.core.util

try:
    from taurus.widget import TauJDrawSynopticsView
    __SUPER_CLASS = taurusplugin.TauWidgetPlugin
except:
    __SUPER_CLASS = object
    l = taurus.core.util.Logger("Designer")
    l.info("TauJDrawSynopticsView will not be available")

class TauJDrawSynopticsViewPlugin(__SUPER_CLASS):

    """TauJDrawSynopticsViewPlugin(taurusplugin.TauWidgetPlugin)
    
    Provides a Python custom plugin for Qt Designer by implementing the
    QDesignerCustomWidgetPlugin via a PyQt-specific custom plugin class.
    """

    def getWidgetClass(self):
        return TauJDrawSynopticsView
        
    def createWidget(self, parent):
        widget = taurusplugin.TauWidgetPlugin.createWidget(self, parent)
        bg_brush = Qt.QBrush(Qt.QPixmap(':/designer/taurus.png'))
        scene = Qt.QGraphicsScene(parent)
        scene.setBackgroundBrush(bg_brush)
        widget.setScene(scene)
        return widget

    def getIconName(self):
        return 'graphicsview.png'

    def isContainer(self):
        return True

try:
    from taurus.widget import TauGraphicsView
    __SUPER_CLASS = taurusplugin.TauWidgetPlugin
except:
    __SUPER_CLASS = object
    l = taurus.core.util.Logger("Designer")
    l.info("TauGraphicsView will not be available")
    
class TauGraphicsViewPlugin(__SUPER_CLASS):

    """TauGraphicsViewPlugin(taurusplugin.TauWidgetPlugin)
    
    Provides a Python custom plugin for Qt Designer by implementing the
    QDesignerCustomWidgetPlugin via a PyQt-specific custom plugin class.
    """

    def getWidgetClass(self):
        return TauGraphicsView
        
    def createWidget(self, parent):
        widget = taurusplugin.TauWidgetPlugin.createWidget(self, parent)
        bg_brush = Qt.QBrush(Qt.QPixmap(':/designer/taurus.png'))
        scene = Qt.QGraphicsScene(parent)
        scene.setBackgroundBrush(bg_brush)
        widget.setScene(scene)
        return widget

    def getIconName(self):
        return 'graphicsview.png'

    def isContainer(self):
        return True
    
try:
    from taurus.widget import TauFrame
    __SUPER_CLASS = taurusplugin.TauWidgetPlugin
except:
    __SUPER_CLASS = object
    l = taurus.core.util.Logger("Designer")
    l.info("TauFrame will not be available")
    
class TauFramePlugin(__SUPER_CLASS):

    """TauFramePlugin(taurusplugin.TauWidgetPlugin)
    
    Provides a Python custom plugin for Qt Designer by implementing the
    QDesignerCustomWidgetPlugin via a PyQt-specific custom plugin class.
    """

    def getWidgetClass(self):
        return TauFrame

    def getIconName(self):
        return 'frame.png'

    def isContainer(self):
        return True
    
try:
    from taurus.widget import TauGroupBox
    __SUPER_CLASS = taurusplugin.TauWidgetPlugin
except:
    __SUPER_CLASS = object
    l = taurus.core.util.Logger("Designer")
    l.info("TauGroupBox will not be available")
    
class TauGroupBoxPlugin(__SUPER_CLASS):

    """TauGroupBoxPlugin(taurusplugin.TauWidgetPlugin)
    
    Provides a Python custom plugin for Qt Designer by implementing the
    QDesignerCustomWidgetPlugin via a PyQt-specific custom plugin class.
    """

    def getWidgetClass(self):
        return TauGroupBox

    def getIconName(self):
        return 'groupbox.png'

    def isContainer(self):
        return True
    

