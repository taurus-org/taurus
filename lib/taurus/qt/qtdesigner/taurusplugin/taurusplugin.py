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

""" Every TaurusWidget should have the following Qt Designer extended capabilities:

  - Task menu:
    it means when you right click on the widget in the designer, it will have
    the following additional items:
    - 'Edit model...' - opens a customized dialog for editing the widget model

  - Property Sheet:
    it means that in the Qt Designer property sheet it will have the following
    properties customized:
    - 'model' - will have a '...' button that will open a customized dialog for
      editing the widget model (same has 'Edit model...' task menu item
"""

from __future__ import print_function
import inspect

from taurus.external.qt import Qt
from taurus.external.qt import QtDesigner

from taurus.core.util.log import Logger


def Q_TYPEID(class_name):
    """ Helper function to generate an IID for Qt."""
    return "com.trolltech.Qt.Designer.%s" % class_name

designer_logger = Logger("PyQtDesigner")


class TaurusWidgetPlugin(QtDesigner.QPyDesignerCustomWidgetPlugin):
    """TaurusWidgetPlugin"""

    def __init__(self, parent=None):
        QtDesigner.QPyDesignerCustomWidgetPlugin.__init__(self)
        self._log = Logger(self._getWidgetClassName(), designer_logger)
        self.initialized = False

    def initialize(self, formEditor):
        """ Overwrite if necessary. Don't forget to call this method in case you
            want the generic taurus extensions in your widget."""
        if self.isInitialized():
            return

        self.initialized = True

    def isInitialized(self):
        return self.initialized

    def getWidgetClass(self):
        return self.WidgetClass

    def _getWidgetClassName(self):
        return self.getWidgetClass().__name__

    def __getWidgetArgs(self, klass=None, designMode=True, parent=None):
        if klass is None:
            klass = self.getWidgetClass()
        ctor = klass.__init__
        aspec = inspect.getargspec(ctor)
        if aspec.defaults is None:
            kwspec = {}
        else:
            kwspec = dict(zip(aspec.args[-len(aspec.defaults):],
                              aspec.defaults))
        args, kwargs = [], {}
        if 'designMode' in kwspec:
            kwargs['designMode'] = designMode
        if 'parent' in kwspec:
            kwargs['parent'] = parent
        else:
            args.append(parent)
        return args, kwargs

    def createWidget(self, parent):
        try:
            klass = self.getWidgetClass()
            args, kwargs = self.__getWidgetArgs(klass=klass,
                                                designMode=True,
                                                parent=parent)
            w = klass(*args, **kwargs)
        except Exception as e:
            name = self._getWidgetClassName()
            print(100 * "=")
            print("taurus designer plugin error creating %s: %s" % (name, str(e)))
            print(100 * "-")
            import traceback
            traceback.print_exc()
            w = None
        return w

    def getWidgetInfo(self, key, dft=None):
        if not hasattr(self, '_widgetInfo'):
            self._widgetInfo = self.getWidgetClass().getQtDesignerPluginInfo()
        return self._widgetInfo.get(key, dft)

    # This method returns the name of the custom widget class that is provided
    # by this plugin.
    def name(self):
        return self._getWidgetClassName()

    def group(self):
        """ Returns the name of the group in Qt Designer's widget box that this
            widget belongs to.
            It returns 'Taurus Widgets'. Overwrite if want another group."""
        return self.getWidgetInfo('group', 'Taurus Widgets')

    def getIconName(self):
        return self.getWidgetInfo('icon')

    def icon(self):
        icon = self.getWidgetInfo('icon')
        if icon is None:
            return Qt.QIcon()
        elif isinstance(icon, Qt.QIcon):
            return icon
        else:
            if icon.find(":") == -1:
                icon = 'designer:%s' % icon
            return Qt.QIcon(icon)

    def domXml(self):
        name = str(self.name())
        lowerName = name[0].lower() + name[1:]
        return '<widget class="%s" name=\"%s\" />\n' % (name, lowerName)

    def includeFile(self):
        """Returns the module containing the custom widget class. It may include
           a module path."""
        return self.getWidgetInfo('module')

    def toolTip(self):
        tooltip = self.getWidgetInfo('tooltip')
        if tooltip is None:
            tooltip = "A %s" % self._getWidgetClassName()
        return tooltip

    def whatsThis(self):
        whatsthis = self.getWidgetInfo('whatsthis')
        if whatsthis is None:
            whatsthis = "This is a %s widget" % self._getWidgetClassName()
        return whatsthis

    def isContainer(self):
        return self.getWidgetInfo('container', False)
