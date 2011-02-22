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

"""
widgetgen.py: 
"""

#!/usr/bin/env python

import os, sys

usage = "usage: %s <widget class name> <widget super class> <output file name> [<qt designer plugin file>]" % os.path.basename(sys.argv[0])

DftModule = "taurus.widget"
DftIconFilename = "label.png"
DftIsContainer = str(False)

def go(class_name, super_class, output_name):

    path = ''
    try:
        path = os.path.dirname(__file__)
    except:
        pass
    input_name = os.path.realpath(path) + '/tauruswidget_template'

    try:
        output = open(output_name, 'w')
    except:
        raise

    try:
        input = open(input_name, 'r')
    except:
        output.close()
        raise

    for s in input:
        o = s.replace('<_SuperClass_>', super_class)
        o = o.replace('<_TaurusClass_>', class_name)
        o = o.replace('<_Module_>', DftModule)
        o = o.replace('<_IconFileName_>', DftIconFilename)
        o = o.replace('<_Container_>', DftIsContainer)
        output.write(o)
    
    input.close()
    output.close()
    

def go_with_designer(class_name, super_class, output_name, plugin_output_name):
    
    go(class_name, super_class, output_name)

    path = ''
    try:
        path = os.path.dirname(__file__)
    except:
        pass
    input_name = os.path.realpath(path) + '/tauruswidget_qtdesignerplugin_template'
    
    try:
        output = open(plugin_output_name, 'w')
    except:
        raise

    try:
        input = open(input_name, 'r')
    except:
        output.close()
        raise
    
    for s in input:
        o = s.replace('<_SuperClass_>',super_class)
        o = o.replace('<_TaurusClass_>',class_name)
        o = o.replace('<_Module_>', DftModule)
        o = o.replace('<_IconFileName_>', DftIconFilename)
        o = o.replace('<_Container_>', DftIsContainer)
        output.write(o)

    input.close()
    output.close()
    
if __name__ == "__main__":
    
    argc = len(sys.argv)
    if argc < 4:
        print usage
    elif argc == 4:
        go(sys.argv[1],sys.argv[2],sys.argv[3])
    else:
        go_with_designer(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4])
        