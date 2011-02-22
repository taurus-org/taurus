
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
dialog.py: 
"""

import os
from PyQt4 import QtCore, QtGui

from ui_TauPopupMenuEditorDialog import Ui_TauPopupMenuEditorDialog

class TauBaseEditorDialog(QtGui.QDialog):
    
    def __init__ (self, parent=None, flags=QtCore.Qt.WindowFlags()):
        QtGui.QDialog.__init__(self, parent, flags)

    def getImageResourceDirectory(self):
        """ Helper method that returns the default 'images' directory (absolute
            path string) that should be a directory parallel to the directory 
            where this module is located so that plugins that subclass this p."""
        try:
            return os.path.join(os.path.dirname(__file__),'..','images')
        except:
            return os.path.join('..','images')    

class TauPopupMenuEditorDialog(TauBaseEditorDialog):
    
    def __init__ (self, parent=None, flags=QtCore.Qt.WindowFlags()):
        TauBaseEditorDialog.__init__(self, parent, flags)
        self.setupUi()
    
    def setupUi(self):
        self.ui = Ui_TauPopupMenuEditorDialog()
        self.ui.setupUi(self)
        
        path = self.getImageResourceDirectory()
        plusIcon = QtGui.QIcon(os.path.realpath(os.path.join(path,'plus.png')))
        minusIcon = QtGui.QIcon(os.path.realpath(os.path.join(path,'minus.png')))
        upIcon = QtGui.QIcon(os.path.realpath(os.path.join(path,'up.png')))
        downIcon = QtGui.QIcon(os.path.realpath(os.path.join(path,'down.png')))
        forwardIcon = QtGui.QIcon(os.path.realpath(os.path.join(path,'forward.png')))
        backIcon = QtGui.QIcon(os.path.realpath(os.path.join(path,'back.png')))
        
        self.ui.newItemButton.setIcon(plusIcon);
        self.ui.deleteItemButton.setIcon(minusIcon);
        self.ui.moveItemUpButton.setIcon(upIcon);
        self.ui.moveItemDownButton.setIcon(downIcon);
        self.ui.moveItemRightButton.setIcon(forwardIcon);
        self.ui.moveItemLeftButton.setIcon(backIcon);
        
        