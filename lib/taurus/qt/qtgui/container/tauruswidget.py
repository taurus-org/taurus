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

"""This module provides basic taurus container widget"""

__all__ = ["TaurusWidget"]

__docformat__ = 'restructuredtext'

from taurus.qt import Qt
from taurusbasecontainer import TaurusBaseContainer


class TaurusWidget(Qt.QWidget, TaurusBaseContainer):
    """This is a Qt.QWidget that additionally accepts a model property.
    This type of taurus container classes are specially useful if you define
    a parent taurus model to them and set all contained taurus widgets to use parent
    model. Example::
    
        from taurus.qt.qtgui.container import *
        from taurus.qt.qtgui.display import *
        
        widget = TaurusWidget()
        layout = Qt.QBoxLayout()
        widget.setLayout(layout)
        widget.model = 'sys/database/2'
        stateWidget = TaurusValueLabel()
        layout.addWidget(stateWidget)
        stateWidget.useParentModel = True
        stateWidget.model = '/state'"""
    
    __pyqtSignals__ = ("modelChanged(const QString &)",)
    
    def __init__(self, parent = None, designMode = False):
        name = self.__class__.__name__
        self.call__init__wo_kw(Qt.QWidget, parent)
        self.call__init__(TaurusBaseContainer, name, designMode=designMode)
    
    @classmethod
    def getQtDesignerPluginInfo(cls):
        ret = TaurusBaseContainer.getQtDesignerPluginInfo()
        if cls is TaurusWidget:
            ret['module'] = 'taurus.qt.qtgui.container'
            ret['group'] = 'Taurus Containers'
            ret['icon'] = ":/designer/frame.png"
            ret['container'] = True
        return ret
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # Public slots for apply/restore changes
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    @Qt.pyqtSignature("applyPendingChanges()")
    def applyPendingChanges(self):
        self.applyPendingOperations()
    
    @Qt.pyqtSignature("resetPendingChanges()")
    def resetPendingChanges(self):
        self.resetPendingOperations()

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # QT properties 
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
   
    model = Qt.pyqtProperty("QString", TaurusBaseContainer.getModel,
                            TaurusBaseContainer.setModel,
                            TaurusBaseContainer.resetModel)
    
    useParentModel = Qt.pyqtProperty("bool", TaurusBaseContainer.getUseParentModel,
                                     TaurusBaseContainer.setUseParentModel,
                                     TaurusBaseContainer.resetUseParentModel)
    
    showQuality = Qt.pyqtProperty("bool", TaurusBaseContainer.getShowQuality,
                                  TaurusBaseContainer.setShowQuality,
                                  TaurusBaseContainer.resetShowQuality)
    
    modifiableByUser = Qt.pyqtProperty("bool", TaurusBaseContainer.isModifiableByUser,
                                  TaurusBaseContainer.setModifiableByUser,
                                  TaurusBaseContainer.resetModifiableByUser)