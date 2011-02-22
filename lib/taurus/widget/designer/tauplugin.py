
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
taurusplugin.py: 
"""

""" Every TauWidget should have the following Qt Designer extended capabilities:

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

import os, os.path

from PyQt4 import QtCore, QtGui, QtDesigner

import taurus.core
import taurus.core.util
import taurus.widget

from taurus.widget.resources import qrc_extra_icons_designer


taurus.core.TauManager().setOperationMode(taurus.core.OperationMode.OFFLINE)

import dialog

def Q_TYPEID(class_name):
    """ Helper function to generate an IID for Qt. Returns a QString."""
    return QtCore.QString("com.trolltech.Qt.Designer.%s" % class_name)


class TauWidgetPlugin(QtDesigner.QPyDesignerCustomWidgetPlugin, taurus.core.util.Logger):
    """TauWidgetPlugin"""
    
    def __init__(self, parent = None):
        QtDesigner.QPyDesignerCustomWidgetPlugin.__init__(self)
        self.call__init__(taurus.core.util.Logger, self.__class__.__name__)
        self.initialized = False
    
    def initialize(self, formEditor):
        """ Overwrite if necessary. Don't forget to call this method in case you
            want the generic taurus extensions in your widget.""" 
        if self.isInitialized():
            return
        
        manager = formEditor.extensionManager()
        
        if manager:
            self.menuFactory = self.initializeMenuFactory(manager)
                
        #    self.propertySheetFactory = self.initializePropertySheetFactory(manager)
        
        self.initialized = True
        
    def isInitialized(self):
        return self.initialized

    def getWidgetClass(self):
        return taurus.widget.TauWidget

    def _getWidgetClassName(self):
        return self.getWidgetClass().__name__

    def createWidget(self, parent):
        try:
            klass = self.getWidgetClass()
            w = klass(parent, designMode = True)
        except Exception, e:
            self.warning("Failed to create widget: %s" % str(e))
            self.traceback()
            w = None
        return w
    
    def initializeMenuFactory(self,manager):
        factory = TauTaskMenuFactory(manager)
        extension_iid = Q_TYPEID("TaskMenu")
        manager.registerExtensions(factory, extension_iid)
        return factory
    
    def initializePropertySheetFactory(self,manager):
        """TODO"""
        return None

    # This method returns the name of the custom widget class that is provided
    # by this plugin.
    def name(self):
        return self._getWidgetClassName()
        
    def group(self):
        """ Returns the name of the group in Qt Designer's widget box that this 
            widget belongs to.
            It returns 'Tau Widgets'. Overwrite if want another group."""
        return "Tau Widgets"

    def getIconName(self):
        return 'taurus.png'

    def icon(self):
        icon_name = ':/designer/%s' % self.getIconName()
        return QtGui.QIcon(icon_name)
    
    def domXml(self):
        name = str(self.name())
        lowerName = name[0].lower() + name[1:]
        return '<widget class="%s" name=\"%s\" />\n' % (name, lowerName)

    def includeFile(self):
        """Returns the module containing the custom widget class. It may include
           a module path. Returns 'taurus.widget'. Overwrite if your widget is 
           located in another file."""
        return "taurus.widget"

    def toolTip(self):
        return "A %s" % self._getWidgetClassName()

    def whatsThis(self):
        return "This is a %s widget" % self._getWidgetClassName()
    
    def isContainer(self):
        return False
        

class TauModelEditDialog(QtGui.QDialog):
    pass


class TauTaskMenuFactory(QtDesigner.QExtensionFactory):
    """ TauTaskMenuFactory(QtDesigner.QExtensionFactory)
        
        Provides a menu extension for the taurus widgets with the additional items:
        - 'Edit model...' - opens a customized dialog for editing the widget 
          model
    """
    
    def __init__(self, parent = None):
        QtDesigner.QExtensionFactory.__init__(self, parent)
    
    # This standard factory function returns an object to represent a task
    # menu entry.
    def createExtension(self, obj, iid, parent):
        if iid != Q_TYPEID("TaskMenu"):
            return None
        
        # We pass the instance of the custom widget to the object representing
        # the task menu entry so that the contents of the custom widget can be
        # modified.
        if isinstance(obj, taurus.widget.TauBaseWidget):
            return TauTaskMenuExtension(obj, parent)
        
        return None


class TauTaskMenuExtension(QtDesigner.QPyDesignerTaskMenuExtension):
    """ TauTaskMenuExtension(QtDesigner.QPyDesignerTaskMenuExtension)
    
        Provides a task menu entry to enable text in the highlighted text
        editor to be edited via a dialog.
    """
    
    def __init__(self, taurusWidget, parent):
    
        QtDesigner.QPyDesignerTaskMenuExtension.__init__(self, parent)
        
        self.taurusWidget = taurusWidget
        
        # Create the action to be added to the form's existing task menu
        # and connect it to a slot in this class.
        
        self.editModelAction = QtGui.QAction("Edit model...", self)
        self.connect(self.editModelAction, QtCore.SIGNAL("triggered()"),
                     self.editModel)

        self.editPopupMenuAction = QtGui.QAction("Edit popup menu...", self)
        self.connect(self.editPopupMenuAction, QtCore.SIGNAL("triggered()"),
                     self.editPopupMenu)
    
    def preferredEditAction(self):
    
        return self.editModelAction
    
    def taskActions(self):
        return [self.editModelAction, self.editPopupMenuAction]
    
    # The editModel() slot is called when the action that represents our task
    # menu entry is triggered. We open a dialog, passing the custom widget as
    # an argument.
    @QtCore.pyqtSignature("editModel()")
    def editModel(self):
    
        dialog = TauModelEditDialog(self.taurusWidget)
        dialog.exec_()
    
    @QtCore.pyqtSignature("editPopupMenu()")
    def editPopupMenu(self):
        d = dialog.TauPopupMenuEditorDialog(self.taurusWidget)
        d.exec_()
        pass
        
        
class TauPropertyExtensionFactory(QtDesigner.QExtensionFactory):
    """ TauPropertyExtensionFactory(QtDesigner.QExtensionFactory)
        Provides a property extension for the taurus widgets. 
    """
    def __init__(self, parent = None):
    
        QtDesigner.QExtensionFactory.__init__(self, parent)
    
    # This standard factory function returns an object to represent a task
    # menu entry.
    def createExtension(self, obj, iid, parent):
    
        if iid != Q_TYPEID("TaskMenu"):
            return None
        
        # We pass the instance of the custom widget to the object representing
        # the task menu entry so that the contents of the custom widget can be
        # modified.
        if isinstance(obj, TauValueLabel):
            return TauPropertySheetExtension(obj, parent)
        
        return None


class TauPropertySheetExtension(QtDesigner.QPyDesignerPropertySheetExtension):
    """TauPropertySheetExtension(QtDesigner.QPyDesignerPropertySheetExtension)

    """
    
    def __init__(self, taurusWidget, parent):
    
        QtDesigner.QPyDesignerPropertySheetExtension.__init__(self, parent)
        
        self.taurusWidget = taurusWidget
        
    def hasReset(self, index):
        pass
    
    def indexOf(self, name):
        pass
    
    def isAttribute(self, index):
        pass
    
    def isChanged(self, index):
        pass

    def isVisible(self, index):
        pass
    
    def property(self, index):
        pass
    
    def propertyGroup(self, index):
        pass
    
    def propertyName(self, index):
        pass
    
    def reset(self, index):
        pass
    
    def setAttribute(self, index, b):
        pass

    def setChanged(self, index, changed):
        pass

    def setProperty(self, index, value):
        pass
    
    def setPropertyGroup (self, index, group):
        pass
    
    def setVisible (self, index, b):
        pass