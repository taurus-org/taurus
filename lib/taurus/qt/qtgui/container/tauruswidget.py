#!/usr/bin/env python

#############################################################################
##
# This file is part of Taurus
##
# http://taurus-scada.org
##
# Copyright 2011 CELLS / ALBA Synchrotron, Bellaterra, Spain
##
# Taurus is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
##
# Taurus is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
##
# You should have received a copy of the GNU Lesser General Public License
# along with Taurus.  If not, see <http://www.gnu.org/licenses/>.
##
#############################################################################

"""This module provides basic taurus container widget"""

from __future__ import absolute_import

from taurus.external.qt import Qt
from .taurusbasecontainer import TaurusBaseContainer


__all__ = ["TaurusWidget"]

__docformat__ = 'restructuredtext'


class TaurusWidget(Qt.QWidget, TaurusBaseContainer):
    """This is a Qt.QWidget that additionally accepts a model property.
    This type of taurus container classes are specially useful if you define
    a parent taurus model to them and set all contained taurus widgets to use parent
    model. Example::

        from taurus.qt.qtgui.container import *
        from taurus.qt.qtgui.display import *

        widget = TaurusWidget()
        layout = Qt.QVBoxLayout()
        widget.setLayout(layout)
        widget.model = 'sys/database/2'
        stateWidget = TaurusLabel()
        layout.addWidget(stateWidget)
        stateWidget.model = 'sys/database/2/state'
        """

    def __init__(self, parent=None, designMode=False):
        name = self.__class__.__name__
        self.call__init__wo_kw(Qt.QWidget, parent)
        self.call__init__(TaurusBaseContainer, name, designMode=designMode)

    @classmethod
    def getQtDesignerPluginInfo(cls):
        ret = TaurusBaseContainer.getQtDesignerPluginInfo()
        if cls is TaurusWidget:
            ret['module'] = 'taurus.qt.qtgui.container'
            ret['group'] = 'Taurus Containers'
            ret['icon'] = "designer:frame.png"
            ret['container'] = True
        return ret
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # Public slots for apply/restore changes
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    @Qt.pyqtSlot()
    def applyPendingChanges(self):
        self.applyPendingOperations()

    @Qt.pyqtSlot()
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
