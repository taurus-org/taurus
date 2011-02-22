
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
fsotrplugin.py: 
"""


import os

from PyQt4 import QtGui, QtDesigner

import taurus.core.util

try:
    from taurus.widget.fsotr import TauFsotr
    __SUPER_CLASS = QtDesigner.QPyDesignerCustomWidgetPlugin
except:
    __SUPER_CLASS = object
    l = taurus.core.util.Logger("Designer")
    l.info("TauFsotr will not be available")

class TauFsotrPlugin(__SUPER_CLASS):
    """TauFsotrPlugin(QtDesigner.QPyDesignerCustomWidgetPlugin)
    
    Provides a Python custom plugin for Qt Designer by implementing the
    QDesignerCustomWidgetPlugin via a PyQt-specific custom plugin class.
    """

    # The __init__() method is only used to set up the plugin and define its
    # initialized variable.
    def __init__(self, parent = None):
        QtDesigner.QPyDesignerCustomWidgetPlugin.__init__(self)
        self.initialized = False


    def initialize(self, formEditor):
        if self.initialized:
            return
        self.initialized = True


    def isInitialized(self):
        return self.initialized

    # This factory method creates new instances of our custom widget with the
    # appropriate parent.
    def createWidget(self, parent):
        widget = TauFsotr(name = self.name(),parent=parent)
        return widget

    # This method returns the name of the custom widget class that is provided
    # by this plugin.
    def name(self):
        return "TauFsotr"

    # Returns the name of the group in Qt Designer's widget box that this
    # widget belongs to.
    def group(self):
        return "Tau Extra-Widgets"

    # Returns the icon used to represent the custom widget in Qt Designer's
    # widget box.
    def icon(self):
        path = ''
        try:
            path = os.path.dirname(__file__)
        except:
            pass
        path += '/images'
        icon_name = os.path.realpath(path + '/taurus.png')
        
        if not os.path.isfile(icon_name):
            icon_name = os.path.realpath(path + '/taurus.png')
        if os.path.isfile(icon_name):
            return QtGui.QIcon(icon_name)
        else:
            return QtGui.QIcon()


    # Returns a short description of the custom widget for use in a tool tip.
    def toolTip(self):
        return "A TauFsotr"

    # Returns a short description of the custom widget for use in a "What's
    # This?" help message for the widget.
    def whatsThis(self):
        return ""

    # Returns True if the custom widget acts as a container for other widgets;
    # otherwise returns False. Note that plugins for custom containers also
    # need to provide an implementation of the QDesignerContainerExtension
    # interface if they need to add custom editing support to Qt Designer.
    def isContainer(self):
        return False

    # Returns an XML description of a custom widget instance that describes
    # default values for its properties. Each custom widget created by this
    # plugin will be configured using this description.
    def domXml(self):
        return '<widget class="TauFsotr" name=\"TauFsotr\" />\n'

    # Returns the module containing the custom widget class. It may include
    # a module path.
    def includeFile(self):
        return "taurus.widget.fsotr"

