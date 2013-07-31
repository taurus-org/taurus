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

# if pluginType is CW_FILTER, the plugin loader will call the getFilter
# method, which must be defined
pluginType = CW_FILTER

# the variables CW_FILTER, MATCH and NO_MATCH are inserted into the
# local namespace by the plugin loader

# getFilter must return a callable that accepts three arguments.
# The filter will be called with widget name, base class name and
# module name as given in the UI file
# the filter must return a tuple
# (match_result, data)
# If the filter matches, "match_result" is MATCH and "data"
# contains the modified argument tuple
# In the other case, "match_result" is NO_MATCH, and data is ignored

# Any other result will load to an error and a program exit

def getFilter():
    import taurus.qt.qtgui.util
    WF = taurus.qt.qtgui.util.TaurusWidgetFactory
    wf = WF()
    taurus_widgets = wf.getWidgets()
        
    def _taurusfilter(widgetname, baseclassname, module):
        if widgetname in taurus_widgets:
            return (MATCH, (widgetname, baseclassname, taurus_widgets[widgetname][0]))
        else:
            return (NO_MATCH, None)
         
    return _taurusfilter