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
qlogo.py: 
"""

__all__ = ["QLogo"]

__docformat__ = 'restructuredtext'

from taurus.qt import Qt
from taurus.qt.qtgui.resource import getPixmap

class QLogo(Qt.QLabel):
    
    def __init__(self, parent=None, designMode=False):
        self.__name = self.__class__.__name__
        Qt.QLabel.__init__(self, parent)
        sizePolicy = Qt.QSizePolicy(Qt.QSizePolicy.Policy(0),Qt.QSizePolicy.Policy(0))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)
        self.setScaledContents(True)
        self.setPixmap(getPixmap(":/logo.png"))

    @classmethod
    def getQtDesignerPluginInfo(cls):
        """Returns pertinent information in order to be able to build a valid
        QtDesigner widget plugin.
        
        The dictionary returned by this method should contain *at least* the 
        following keys and values:
        
            - 'module' : a string representing the full python module name (ex.: 'taurus.qt.qtgui.base')
            - 'icon' : a string representing valid resource icon (ex.: ':/designer/combobox.png')
            - 'container' : a bool telling if this widget is a container widget or not.
        
        This default implementation returns the following dictionary:
        
            { 'module'    : 'taurus.qt.qtgui.base',
              'group'     : 'Taurus Widgets',
              'icon'      : ':/designer/taurus.svg',
              'container' : False }
        
        :return: (dict) a map with pertinent designer information"""
        return { 
            'group'     : 'Taurus Widgets',
            'icon'      : ':/designer/taurus.png',
            'container' : False }

def main():
    import sys
    app = Qt.QApplication(sys.argv)
    w = QLogo()
    w.show()
    sys.exit(app.exec_())
    
if __name__ == "__main__":
    main()