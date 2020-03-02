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
###########################################################################

"""This configuration contains base modules and classes that may be used
by specific TaurusGui-based GUIs"""

from builtins import object

from lxml import etree
from future.utils import string_types
from taurus.qt.qtgui.util import ExternalAppAction
from taurus.qt.qtgui.util import TaurusWidgetFactory
from taurus.core.util.log import Logger


__docformat__ = 'restructuredtext'

# this is here only for backwards compatibility. It should not be used at all


class Qt_Qt(object):
    LeftDockWidgetArea = 1
    RightDockWidgetArea = 2
    BottomDockWidgetArea = 3
    TopDockWidgetArea = 4

TAURUSGUI_AREAS = {'Left': Qt_Qt.LeftDockWidgetArea,
                   'Right': Qt_Qt.RightDockWidgetArea,
                   'Top': Qt_Qt.TopDockWidgetArea,
                   'Bottom': Qt_Qt.BottomDockWidgetArea}


class ExternalApp(object):
    '''
    A description of an external application.
    Uses the same initialization as that of :class:`ExternalAppAction`
    Use :meth:`getAction` to obtain an instance of a :class:`ExternalAppAction`
    '''

    def __init__(self, *args, **kwargs):
        ''' see :meth:`ExternalAppAction.__init__`'''
        self.args = args
        self.kwargs = kwargs

    def getAction(self):
        '''
        Returns a :class:`ExternalAppAction` with the values used when
        initializing this ExternalApp instance

        :return: (ExternalAppAction)
        '''
        return ExternalAppAction(*self.args, **self.kwargs)

    @staticmethod
    def fromXml(xmlstring):
        ''' returns a ExternalApp object based on the xml string provided

        :param xmlstring: (unicode) XML code defining the values for the
                          cmdargs, text, icon and parent variables

        :return: (ExternalApp) an instance of ExternalApp
        '''
        try:
            root = etree.fromstring(xmlstring)
        except:
            raise ValueError('Invalid XML syntax')

        commandNode = root.find("command")
        if (commandNode is not None) and (commandNode.text is not None):
            command = commandNode.text
        else:
            raise ValueError('Invalid XML: <command> is mandatory')

        paramsNode = root.find("params")
        if (paramsNode is not None) and (paramsNode.text is not None):
            params = paramsNode.text
        else:
            params = ''

        textNode = root.find("text")
        if (textNode is not None) and (textNode.text is not None):
            text = textNode.text
        else:
            text = None

        iconNode = root.find("icon")
        if (iconNode is not None) and (iconNode.text is not None):
            icon = iconNode.text
        else:
            icon = None

        return ExternalApp(" ".join((command, params)), text=text, icon=icon)


class TaurusGuiComponentDescription(object):
    '''
    A base class for describing a taurusgui component.
    '''

    def __init__(self, name, classname=None, modulename=None, widgetname=None,
                 sharedDataWrite=None, sharedDataRead=None,
                 model=None, floating=True, **kwargs):
        self._name = name
        self._modulename = modulename
        self.setClassname(classname)
        self.setWidgetname(widgetname)
        if self.classname is None and (self.modulename is None or self.widgetname is None):
            raise ValueError(
                'Module info must be given (except if passing a Taurus class name)')
        self._floating = floating
        if sharedDataWrite is None:
            sharedDataWrite = {}
        self._sharedDataWrite = sharedDataWrite
        if sharedDataRead is None:
            sharedDataRead = {}
        self._sharedDataRead = sharedDataRead
        self._model = model

    def getName(self):
        return self._name

    def setName(self, name):
        self._name = name

    def getClassname(self):
        return self._classname

    def setClassname(self, classname):
        if classname is not None and '.' in classname:
            modulename, classname = classname.rsplit('.', 1)
            self.setModulename(modulename)
        self._classname = classname

    def getModulename(self):
        return self._modulename

    def setModulename(self, modulename):
        self._modulename = modulename

    def getWidgetname(self):
        return self._widgetname

    def setWidgetname(self, widgetname):
        if widgetname is not None and '.' in widgetname:
            modulename, widgetname = widgetname.rsplit('.', 1)
            self.setModulename(modulename)
        self._widgetname = widgetname

    def getArea(self):
        raise DeprecationWarning('getArea is deprecated')
        return self._area

    def setArea(self, area):
        raise DeprecationWarning('setArea is deprecated')
        self._area = area

    def isFloating(self):
        return self._floating

    def setFloating(self, floating):
        self._floating = floating

    def getSharedDataWrite(self):
        return self._sharedDataWrite

    def setSharedDataWrite(self, sharedDataWrite):
        self._sharedDataWrite = sharedDataWrite

    def getSharedDataRead(self):
        return self._sharedDataRead

    def setSharedDataRead(self, sharedDataRead):
        self._sharedDataRead = sharedDataRead

    def getModel(self):
        return self._model

    def setModel(self, model):
        self._model = model

    def getWidget(self, sdm=None, setModel=True):
        ''' Returns the widget to be inserted in the panel

        :param sdm: (SharedDataManager) if given, the widget will be registered as reader
                    and/or writer in this manager as defined by the sharedDataRead and sharedDataWrite properties
        :param setModel: (bool) if True (default) the widget will be given the model deined in the model property

        :return: (QWidget) a new widget instance matching the description
        '''
        # instantiate the widget
        if self.modulename is None:
            klass = TaurusWidgetFactory().getWidgetClass(self.classname)
            w = klass()
        else:
            module = __import__(self.modulename, fromlist=[''])
            if self.classname is None:
                w = getattr(module, self.widgetname)
            else:
                klass = getattr(module, self.classname)
                w = klass()
        # set the model if setModel is True
        if self.model is not None and setModel:
            w.setModel(self.model)
        # connect (if an sdm is given)
        if sdm is not None:
            for dataUID, signalname in self.sharedDataWrite.items():
                sdm.connectWriter(dataUID, w, signalname)
            for dataUID, slotname in self.sharedDataRead.items():
                sdm.connectReader(dataUID, getattr(w, slotname))
        # set the name
        w.name = self.name
        return w

    def toXml(self):
        '''Returns a (unicode) XML code defining the PanelDescription object

        :return: xmlstring
        '''

        root = etree.Element("PanelDescription")
        name = etree.SubElement(root, "name")
        name.text = self._name
        classname = etree.SubElement(root, "classname")
        classname.text = self._classname
        modulename = etree.SubElement(root, "modulename")
        modulename.text = self._modulename
        widgetname = etree.SubElement(root, "widgetname")
        widgetname.text = self._widgetname
        floating = etree.SubElement(root, "floating")
        floating.text = str(self._floating)

        sharedDataWrite = etree.SubElement(root, "sharedDataWrite")
        for k, v in self._sharedDataWrite.items():
            item = etree.SubElement(
                sharedDataWrite, "item", datauid=k, signalName=v)

        sharedDataRead = etree.SubElement(root, "sharedDataRead")
        for k, v in self._sharedDataRead.items():
            item = etree.SubElement(
                sharedDataRead, "item", datauid=k, slotName=v)

        model = etree.SubElement(root, "model")
        model.text = self._model

        return etree.tostring(root, pretty_print=True, encoding='unicode')

    @staticmethod
    def fromXml(xmlstring):
        '''returns a PanelDescription object based on the xml string provided

        :param xmlstring: (unicode) XML code defining the values for the args
                          needed to initialize PanelDescription.

        :return: (PanelDescription) object
        '''

        try:
            root = etree.fromstring(xmlstring)
        except:
            return None

        nameNode = root.find("name")
        if (nameNode is not None) and (nameNode.text is not None):
            name = nameNode.text
        else:
            return None

        classnameNode = root.find("classname")
        if (classnameNode is not None) and (classnameNode.text is not None):
            classname = classnameNode.text
        else:
            classname = None

        modulenameNode = root.find("modulename")
        if (modulenameNode is not None) and (modulenameNode.text is not None):
            modulename = modulenameNode.text
        else:
            modulename = None

        widgetnameNode = root.find("widgetname")
        if (widgetnameNode is not None) and (widgetnameNode.text is not None):
            widgetname = widgetnameNode.text
        else:
            widgetname = None

        floatingNode = root.find("floating")
        if (floatingNode is not None) and (floatingNode.text is not None):
            floating = floatingNode.text == str(True)
        else:
            floating = True

        sharedDataWrite = {}
        sharedDataWriteNode = root.find("sharedDataWrite")
        if (sharedDataWriteNode is not None) and (sharedDataWriteNode.text is not None):
            for child in sharedDataWriteNode:
                if (child.get("datauid") is not None) and (child.get("signalName") is not None):
                    sharedDataWrite[child.get("datauid")] = child.get(
                        "signalName")

        if not len(sharedDataWrite):
            sharedDataWrite = None

        sharedDataRead = {}
        sharedDataReadNode = root.find("sharedDataRead")
        if (sharedDataReadNode is not None) and (sharedDataReadNode.text is not None):
            for child in sharedDataReadNode:
                if (child.get("datauid") is not None) and (child.get("slotName") is not None):
                    sharedDataRead[
                        child.get("datauid")] = child.get("slotName")

        if not len(sharedDataRead):
            sharedDataRead = None

        modelNode = root.find("model")
        if (modelNode is not None) and (modelNode.text is not None):
            model = modelNode.text
        else:
            model = None

        return PanelDescription(name, classname=classname, modulename=modulename, widgetname=widgetname,
                                floating=floating, sharedDataWrite=sharedDataWrite, sharedDataRead=sharedDataRead,
                                model=model)

    #=========================================================================
    # Properties
    #=========================================================================
    name = property(fget=getName, fset=setName)
    classname = property(fget=getClassname, fset=setClassname)
    modulename = property(fget=getModulename, fset=setModulename)
    widgetname = property(fget=getWidgetname, fset=setWidgetname)
    floating = property(fget=isFloating, fset=setFloating)
    sharedDataWrite = property(
        fget=getSharedDataWrite, fset=setSharedDataWrite)
    sharedDataRead = property(fget=getSharedDataRead, fset=setSharedDataRead)
    model = property(fget=getModel, fset=setModel)


class PanelDescription(TaurusGuiComponentDescription):
    '''
    A description of a taurusgui panel.
    This class is not a panel, but a container of the information required to
    build a panel.
    '''

    def __init__(self, *args, **kwargs):
        """

        Constructor. The following arguments are processed (the rest are
        directly passed to the constructor of
        :class:`TaurusGuiComponentDescription` )

        :param instrumentkey: (str)
        :param model_in_config: (bool) whther to store model in settigns file or not
        :param modifiable_by_user: (bool) whether user can edit widget or not
        :param widget_formatter: (str) formatter used by this widget
        :param widget_properties: (dict) a dictionary of property_names:values
                                  to be set on the widget

        """
        self.instrumentkey = kwargs.pop('instrumentkey', None)
        self.icon = kwargs.pop("icon", None)
        self.model_in_config = kwargs.pop("model_in_config", None)
        self.modifiable_by_user = kwargs.pop("modifiable_by_user", None)
        self.widget_formatter = kwargs.pop("widget_formatter", None)
        self.widget_properties = kwargs.pop("widget_properties", {})
        TaurusGuiComponentDescription.__init__(self, *args, **kwargs)

    @staticmethod
    def fromPanel(panel):
        name = str(panel.objectName())
        classname = panel.getWidgetClassName()
        modulename = panel.getWidgetModuleName()
        # in the case of classes known to the TaurusWidgetFactory,
        # do not store the modulename
        if modulename.startswith('taurus.') and \
           classname in TaurusWidgetFactory().getWidgetClassNames():
            modulename = None
        widgetname = None
        floating = panel.isFloating()
        sharedDataWrite = None
        sharedDataRead = None
        model = getattr(panel.widget(), 'model', None)
        if model is None or isinstance(model, string_types):
            pass
        elif hasattr(model, '__iter__'):
            # if model is a sequence, convert to space-separated string
            try:
                model = " ".join(model)
            except Exception as e:
                msg = ('Cannot convert %s to a space-separated string: %s' %
                       (model, e))
                Logger().debug(msg)
                model = None
        else:
            # ignore other "model" attributes (they are not from Taurus)
            model = None

        return PanelDescription(
            name,
            classname=classname,
            modulename=modulename,
            widgetname=widgetname,
            floating=floating,
            sharedDataWrite=sharedDataWrite,
            sharedDataRead=sharedDataRead,
            model=model,
            icon=panel.icon,
            model_in_config=panel.model_in_config,
            modifiable_by_user=panel.modifiable_by_user,
            widget_formatter=panel.widget_formatter,
            widget_properties=panel.widget_properties
            )


class ToolBarDescription(TaurusGuiComponentDescription):
    '''
    A description of a toolbar to be inserted in a TaurusGUI.
    '''
    pass


class AppletDescription(TaurusGuiComponentDescription):
    '''
    A description of a widget to be inserted in the "applets bar" of the TaurusGUI.
    '''
    pass
