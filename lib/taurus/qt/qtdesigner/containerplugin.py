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

"""
Every TaurusWidget should have the following Qt Designer extended
capabilities:

  - Task menu:
    it means when you right click on the widget in the designer, it will have
    the following additional items:

    - 'Edit model...': opens a customized dialog for editing the widget model

  - Property Sheet:
    it means that in the Qt Designer property sheet it will have the following
    properties customized:

    - 'model': will have a '...' button that will open a customized dialog for
      editing the widget model (same has 'Edit model...' task menu item
"""

from __future__ import absolute_import

from taurus.external.qt import QtDesigner
from taurus.qt.qtgui.container.qcontainer import QGroupWidget


Q_TYPEID = {'QPyDesignerContainerExtension':     'com.trolltech.Qt.Designer.Container',
            'QPyDesignerPropertySheetExtension': 'com.trolltech.Qt.Designer.PropertySheet',
            'QPyDesignerTaskMenuExtension':      'com.trolltech.Qt.Designer.TaskMenu',
            'QPyDesignerMemberSheetExtension':   'com.trolltech.Qt.Designer.MemberSheet'}


class QGroupWidgetContainerExtension(QtDesigner.QPyDesignerContainerExtension):

    def __init__(self, widget, parent=None):
        super(QGroupWidgetContainerExtension, self).__init__(parent)
        self._widget = widget
        self._page_widget = None

    def addWidget(self, widget):
        if self.count() > 0:
            raise Exception("Can only have at maximum one child")
        self._layout().addWidget(widget)
        self._page_widget = widget

    def _content(self):
        return self._widget.content()

    def _layout(self):
        return self._content().layout()

    def count(self):
        return self._layout().count()

    def currentIndex(self):
        if self.count() > 0:
            return 0
        return -1

    def insertWidget(self, index, widget):
        self.addWidget(widget)

    def remove(self, index):
        self._layout().removeWidget(self.widget(index))

    def setCurrentIndex(self, index):
        pass

    def widget(self, index):
        return self._page_widget


class QGroupWidgetExtensionFactory(QtDesigner.QExtensionFactory):

    def __init__(self, parent=None):
        super(QGroupWidgetExtensionFactory, self).__init__(parent)

    def createExtension(self, obj, iid, parent):
        if iid != Q_TYPEID['QPyDesignerContainerExtension']:
            return None
        if isinstance(obj, QGroupWidget):
            return QGroupWidgetContainerExtension(obj, parent)
        return None


def create_plugin():
    from taurus.qt.qtdesigner.taurusplugin.taurusplugin import (
        TaurusWidgetPlugin)

    class QGroupWidgetPlugin(TaurusWidgetPlugin):

        WidgetClass = QGroupWidget

        def initialize(self, formEditor):
            if self.isInitialized():
                return

            manager = formEditor.extensionManager()
            if manager:
                self.factory = QGroupWidgetExtensionFactory(manager)
                manager.registerExtensions(self.factory, Q_TYPEID[
                                           'QPyDesignerContainerExtension'])
            self.initialized = True
    return QGroupWidgetPlugin

QGroupWidgetPlugin = create_plugin()
