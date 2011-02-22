
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
tauruswidgetuic4.py: 
"""

# This file should be placed in the pyuic4 widget-plugins module.
# Usually it is placed in /usr/lib/python2.5/site-packages/PyQt4/uic/widget-plugins

# A plugin may raise an ImportError. In this case, the plugin will be silently
# discarded.  Any other exception that happens during plugin loading will lead
# to a program abort.


# If pluginType is MODULE, the plugin loader will call moduleInformation.  The
# variable MODULE is inserted into the local namespace by the plugin loader.
pluginType = MODULE


# moduleInformation() must return a tuple (module, widget_list).  If "module"
# is "A" and any widget from this module is used, the code generator will write
# "import A".  If "module" is "A[.B].C", the code generator will write
# "from A[.B] import C".  Each entry in "widget_list" must be unique.
def moduleInformation():
    moduleName = "taurus.widget"
    widgetNames = []
    
    import PyQt4.QtGui
    import taurus.widget
    
    for name in taurus.widget.__dict__.keys():
        if name.startswith("Tau"):
            kls = taurus.widget.__dict__[name]
            try:
                if issubclass(kls,PyQt4.QtGui.QWidget):
                    widgetNames.append(name)
            except:
                pass
            
    return moduleName, widgetNames