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

"""This module is designed to provide a factory class for taurus Qt actions """

from __future__ import absolute_import

from future.utils import string_types

from taurus.core.util.log import Logger
from taurus.core.util.singleton import Singleton
from taurus.external.qt import Qt

from . import taurusaction


__all__ = ["ActionFactory"]

__docformat__ = 'restructuredtext'


class ActionFactory(Singleton, Logger):
    """A Singleton class designed to provide Action related objects."""

    def __init__(self):
        """ Initialization. Nothing to be done here for now."""
        pass

    def init(self, *args):
        """Singleton instance initialization."""
        self.call__init__(Logger, 'ActionFactory')
        self.actions = self.__getActions()
        self.menus = self.__getMenus()

    def __getClasses(self, super_class):
        ret = {}
        klass_type = type(super_class)
        for name in dir(taurusaction):
            klass = getattr(taurusaction, name)
            if klass == super_class:
                continue
            if (type(klass) == klass_type and issubclass(klass, super_class)):
                ret[klass.menuID] = klass
        return ret

    def __getActions(self):
        """Calculates the map of existing action classes"""
        return self.__getClasses(taurusaction.TaurusAction)

    def __getMenus(self):
        """Calculates the map of existing menu classes"""
        return self.__getClasses(taurusaction.TaurusMenu)

    def getActions(self):
        return self.actions

    def getMenus(self):
        return self.menus

    def getNewAction(self, widget, id):
        klass = self.actions.get(id)
        if klass is None:
            return None
        return klass(widget)

    def getNewMenu(self, widget, data):
        import xml.dom.minidom
        doc = xml.dom.minidom.parseString(data)
        m_node = doc.childNodes[0]
        return self.buildMenu(widget, m_node)

    def buildAction(self, widget, a_node):
        if not a_node.hasAttribute('class'):
            return None

        id = a_node.getAttribute('class')
        action = self.getNewAction(widget, id)

        # if node has alternative label, display it instead
        if a_node.hasAttribute('label'):
            action.setText(a_node.getAttribute('label'))

        if a_node.hasAttribute('checkable'):
            action.setCheckable(bool(a_node.getAttribute('checkable')))

        if a_node.hasAttribute('icon'):
            icon = a_node.getAttribute('icon')
            # TODO
            # action.setIcon(icon)
        return action

    def buildMenu(self, widget, m_node):
        menu = None
        if m_node.hasAttribute('class'):
            klass = self.menus.get(m_node.getAttribute('class'))
            if klass is None:
                return None
            menu = klass(widget)
        else:
            menu = taurusaction.TaurusMenu(widget)
            menu.buildFromXML(m_node)
        return menu

    def createAction(self, parent, text, shortcut=None, icon=None, tip=None,
                     toggled=None, triggered=None, data=None,
                     context=Qt.Qt.WindowShortcut):
        """Create a QAction"""
        action = Qt.QAction(text, parent)
        if triggered is not None:
            action.triggered.connect(triggered)
        if toggled is not None:
            action.toggled.connect(toggled)
            action.setCheckable(True)
        if icon is not None:
            if isinstance(icon, string_types):
                icon = Qt.QIcon.fromTheme(icon)
            action.setIcon(icon)
        if shortcut is not None:
            action.setShortcut(shortcut)
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        if data is not None:
            action.setData(data)
        # TODO: Hard-code all shortcuts and choose context=Qt.WidgetShortcut
        # (this will avoid calling shortcuts from another dockwidget
        #  since the context thing doesn't work quite well with these widgets)
        action.setShortcutContext(context)
        return action
