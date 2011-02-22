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

"""This configuration contains base modules and classes that may be used 
by specific TaurusGui-based GUIs"""

__docformat__ = 'restructuredtext'


from PyQt4.Qt import Qt as Qt_Qt
from taurus.qt.qtgui.util import ExternalAppAction
from taurus.qt.qtgui.util import TaurusWidgetFactory
from taurus.core.util import etree
import os,sys

TAURUSGUI_AREAS = {'Left':Qt_Qt.LeftDockWidgetArea,
                'Right':Qt_Qt.RightDockWidgetArea, 
                'Top':Qt_Qt.TopDockWidgetArea, 
                'Bottom':Qt_Qt.BottomDockWidgetArea}


class ExternalApp(object):
    '''
    A description of an external application.
    Uses the same initialization as that of :class:`ExternalAppAction`
    Use :meth:`getAction` to obtain an instance of a :class:`ExternalAppAction`
    '''
#    def __init__(self, cmdargs, text=None, icon=None, parent=None):
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
    @classmethod
    def fromXml(xmlstring):
        ''' returns a ExternalApp object based on the xml string provided
        
        :param xmlstring: (unicode) XML code defining the values for the
                          cmdargs, text, icon and parent variables
        
        :return: (ExternalApp) object
        '''
        raise NotImplementedError #@todo:
        #@todo: extract the values of cmdargs, text, icon and parent from xmlstring
        return ExternalApp(cmdargs, text=text, icon=icon, parent=parent)
    


class PanelDescription(object):
    '''
    A description of a teurusgui panel. 
    This class is not a panel, but a container of the information required to
    build a panel.
    '''
    def __init__(self,name, classname=None, modulename=None, widgetname=None, 
                 area=None, sharedDataWrite=None, sharedDataRead=None, 
                 model=None):
        if classname is None and (modulename is None or widgetname is None) :
            raise ValueError('Either classname or both modulename and widgetname must be given')
        self._name = name
        self._classname = classname
        self._modulename = modulename
        self._widgetname = widgetname
        self._area = area
        if sharedDataWrite is None: sharedDataWrite = {}
        self._sharedDataWrite = sharedDataWrite
        if sharedDataRead is None: sharedDataRead = {}
        self._sharedDataRead = sharedDataRead
        self._model = model
        
    def getName(self):
        return self._name
    
    def setName(self, name):
        self._name = name 
    
    def getClassname(self):
        return self._classname
    
    def setClassname(self, classname):
        self._classname = classname
    
    def getModulename(self):
        return self._modulename
    
    def setModulename(self, modulename):
        self._modulename = modulename
    
    def getWidgetname(self):
        return self._widgetname
    
    def setWidgetname(self, widgetname):
        self._widgetname = widgetname
        
    def getArea(self):
        return self._area
    
    def setArea(self, area):
        self._area = area
        
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
        #instantiate the widget
        if self.modulename is None:
            klass = TaurusWidgetFactory().getTaurusWidgetClass(self.classname)
            w = klass()
        else:
            module = __import__(self.modulename, fromlist=[''])
            if self.classname is None:
                w = getattr(module, self.widgetname)
            else:
                klass = getattr(module, self.classname)
                w = klass()
        #set the model if setModel is True
        if self.model is not None and setModel:
            w.setModel(self.model)
        #connect (if an sdm is given)
        if sdm is not None:
            for dataUID,signalname in self.sharedDataWrite.iteritems(): 
                sdm.connectWriter(dataUID, w, signalname)
            for dataUID,slotname in self.sharedDataRead.iteritems():
                sdm.connectReader(dataUID, getattr(w,slotname))
        #set the name
        w.name = self.name
        return w
    
    def toXml(self):
        '''Returns a (unicode) XML code defining the PanelDescription object
        
        :return: xmlstring
        '''
#        raise NotImplementedError
        #@todo: save the values of properties the XML code
        #raise NotImplementedError

        root = etree.Element("PanelDescription")
        name = etree.SubElement(root, "name")
        name.text = self._name
        classname = etree.SubElement(root, "classname")
        classname.text = self._classname
        modulename = etree.SubElement(root, "modulename")
        modulename.text = self._modulename
        widgetname = etree.SubElement(root, "widgetname")
        widgetname.text = self._widgetname
        area = etree.SubElement(root, "area")
        area.text = self._area

        sharedDataWrite = etree.SubElement(root, "sharedDataWrite")
        for k,v in self._sharedDataWrite.iteritems():
            item = etree.SubElement(sharedDataWrite, "item" ,datauid=k,signalName=v)

        sharedDataRead = etree.SubElement(root, "sharedDataRead")
        for k,v in self._sharedDataRead.iteritems():
            item = etree.SubElement(sharedDataRead, "item" ,datauid=k,slotName=v)
            
        model = etree.SubElement(root, "model")
        model.text = self._model
        
        return  etree.tostring(root)
    
    @classmethod
    def fromXml(xmlstring):
        '''returns a PanelDescription object based on the xml string provided
        
        :param xmlstring: (unicode) XML code defining the values for the args
                          needed to initialize PanelDescription.
        
        :return: (PanelDescription) object
        '''
        raise NotImplementedError #@todo:
        root = etree.fromstring(xmlstring)
        name = root.find("name").text
        classname = root.find("classname").text
        modulename = root.find("modulename").text
        widgetname = root.find("widgetname").text
        area = root.find("area").text

    
        #@todo: extract the values of the required vars
        return PanelDescription(name, classname=classname, modulename=modulename, widgetname=widgetname, 
                                area=area, sharedDataWrite=sharedDataWrite, sharedDataRead=sharedDataRead, 
                                model=model)
        
    #===============================================================================
    # Properties
    #===============================================================================
    name = property(fget=getName, fset=setName)
    classname = property(fget=getClassname, fset=setClassname)
    modulename = property(fget=getModulename, fset=setModulename)
    widgetname = property(fget=getWidgetname, fset=setWidgetname)
    area = property(fget=getArea, fset=setArea)
    sharedDataWrite = property(fget=getSharedDataWrite, fset=setSharedDataWrite)
    sharedDataRead = property(fget=getSharedDataRead, fset=setSharedDataRead) 
    model = property(fget=getModel, fset=setModel) 


        
