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

"""This module provides base class for all taurus container widgets"""

__all__ = ["TaurusBaseContainer"]

__docformat__ = 'restructuredtext'

from taurus.external.qt import Qt

from taurus.qt.qtgui.base import TaurusBaseComponent, TaurusBaseWidget


class TaurusBaseContainer(TaurusBaseWidget):
    """Base class for the Taurus container widgets.
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

    def __init__(self, name='', parent=None, designMode=False):
        name = name or self.__class__.__name__

        self.call__init__(TaurusBaseWidget, name,
                          parent, designMode=designMode)

        self.defineStyle()
        self.designMode = designMode

    def taurusChildren(self, objs=None):
        '''
        returns a list of all taurus children of this taurus container (recurses down
        skipping non-taurus widgets)

        :param objs: (list<objects>) if given, the search starts at the objects
                     passed in this list

        :return: (list<TaurusBaseWidget>)
        '''
        if objs is None:
            objs = self.children()
        result = []
        for o in objs:
            if isinstance(o, TaurusBaseWidget):
                result.append(o)
            else:
                result += self.taurusChildren(o.children())
        return result

    def defineStyle(self):
        self.updateStyle()

    def sizeHint(self):
        #        if self.designMode:
        #            return Qt.QSize(150, 150)
        return Qt.QWidget.sizeHint(self)

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # TaurusBaseWidget over writing
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    def isReadOnly(self):
        return True

    def updateStyle(self):
        if self.getShowQuality():
            self.setAutoFillBackground(True)
            # TODO: get quality/state from model and update accordingly
        else:
            self.setAutoFillBackground(False)
            # TODO: restore colors
        TaurusBaseWidget.updateStyle(self)

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # Pending operations related methods
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    def getPendingOperations(self):
        pending_ops = []

        for child in Qt.QObject.children(self):
            if isinstance(child, TaurusBaseComponent):
                pending_ops += child.getPendingOperations()
        return pending_ops

    def resetPendingOperations(self):
        self.debug("Reset changes")
        for child in Qt.QObject.children(self):
            if isinstance(child, TaurusBaseComponent):
                child.resetPendingOperations()

    def hasPendingOperations(self):
        ret = False
        for child in Qt.QObject.children(self):
            if isinstance(child, TaurusBaseComponent):
                ret |= child.hasPendingOperations()
        return ret

    def handleEvent(self, evt_src, evt_type, evt_value):
        if not self._setText or not self.getShowText():
            return
        modelObj = self.getModelObj()
        if modelObj:
            txt = modelObj.getDisplayName(complete=False)
        else:
            txt = self.getNoneValue()
        self._setText(txt)

#    @classmethod
#    def getQtDesignerPluginInfo(cls):
#        """Returns pertinent information in order to be able to build a valid
#        QtDesigner widget plugin
#
#        The dictionary returned by this method should contain *at least* the
#        following keys and values:
#        - 'module' : a string representing the full python module name (ex.: 'taurus.qt.qtgui.base')
#        - 'icon' : a string representing valid resource icon (ex.: 'designer:combobox.png')
#        - 'container' : a bool telling if this widget is a container widget or not.
#
#        This default implementation returns the following dictionary:
#            { 'group'     : 'Taurus Containers',
#              'icon'      : 'designer:widget.png',
#              'container' : True }
#
#        :return: (dict) a map with pertinent designer information"""
#        ret = TaurusBaseWidget.getQtDesignerPluginInfo()
#        ret['module'] = 'taurus.qt.qtgui.container'
#        ret['group'] = 'Taurus Containers'
#        ret['icon'] = "designer:widget.png"
#        ret['container'] = True
#        return ret
