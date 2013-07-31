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

"""
Provides a QtObject for taurus attributes 
"""
import weakref
import re
import PyTango

from taurus.core.taurusvalidator import AttributeNameValidator
from taurus.qt import Qt
from taurus.qt.qtgui.base import TaurusBaseComponent
from taurus.core.util.safeeval import SafeEvaluator

class TaurusQAttributeFactory(object): #@this probably needs to be ported to a proper TaurusFactory
    '''A factory for TaurusQAttributes that ensures that only one 
    TaurusQAttributes is created for a given extended model.
    IMPORTANT: This API is for testing purposes.It is likely to change.  Don't rely on it'''
    def __init__(self):
        self._qAttrsByExtModel = weakref.WeakValueDictionary()
        self._count = 0
        
    def getQAttr(self, xmodel=None, id=None, autoIdformat=r'_QAttr%i_'):
        #check if the qAttr is known to this factory
        if xmodel is not None and xmodel in self._qAttrsByExtModel:
            c = self._qAttrsByExtModel[xmodel]
        #create a new qAttr
        else:
            if id is None: 
                id = autoIdformat%self._count
                self._count += 1
            c = TaurusQAttribute(xmodel=xmodel, id=id)
        self._qAttrsByExtModel[xmodel] = c
        return c
    
    
taurusQAttributeFactory = TaurusQAttributeFactory()
ATTRNAMEVALIDATOR = AttributeNameValidator()

class TaurusQAttribute(Qt.QObject, TaurusBaseComponent):
    '''A listener for taurus attributes.
    It stores the value in a numpy array and emits a 
    dataChanged signal when the data has changed.
    '''
    pyVar_RegExp = re.compile("[a-zA-Z_][a-zA-Z0-9_]*") #regexp for a variable/method name (symbol)
    cref_RegExp = re.compile("\$\{(.+?)\}") #regexp for references to qAttrs in extended models
    def __init__(self, xmodel = None, id=None):
        Qt.QObject.__init__(self)
        TaurusBaseComponent.__init__(self, self.__class__.__name__)
        self._attrnamevalidator = ATTRNAMEVALIDATOR
        self.id = id
        self.sev = SafeEvaluator()
        self._referencedQAttrs = []
        self.value = None
        self._setExtendedModel(xmodel)
        
    def _setExtendedModel(self, xmodel):
        self._xmodel = xmodel
        if xmodel is None:
            self.value = None
            self._transformationString = None
            self.setModel('')
            return
        xmodel = str(xmodel)
        #for formulas
        if xmodel.startswith('='):
            trstring, ok = self.preProcessTransformation(xmodel[1:])
            if ok:
                self._transformationString = trstring
                self.applyTransformation()
            else:
                print "!!!!!!!!!!!!!", self._transformationString
                return
        #for tango attributes
        elif self._attrnamevalidator.isValid(xmodel):
            self.setModel(xmodel)
            self.fireEvent(None, None, None) #fake event to force a reading
        else:
            self.warning('Unsupported extended model "%s". Skipping',xmodel)
#        #for nexus files
#        m = re.match(NEXUS_src,model)
#        if m is not None:
#            host,path,nxpath,slice = m.group(4,5,9,10) 
#            #@todo:open file and check the data is accessible
#            return model, nxpath, getThemeIcon('x-office-spreadsheet'), True
#        #for ascii files
#        m = re.match(ASCII_src,model)
#        if m is not None:
#            host,path, = m.group(4,5)
#        #@todo: open and check the file
#        #If nothing matches...
#        return model, model, getThemeIcon('dialog-warning'), False
        
    
    def preProcessTransformation(self, trstring):
        """
        parses the transformation string and creates the necessary symbols for
        the evaluator. It also connects any referenced qAttrs so that the
        transformation gets re-evaluated if they change.
        :param trstring: (str) a string to be pre-processed
        
        :return: (tuple<str,bool>) a tuple containing the processed string 
                 and a boolean indicating if the preprocessing was successful.
                 if ok==True, the string is ready to be evaluated
        """
        #disconnect previously referenced qAttrs and clean the list
        for c in self._referencedQAttrs:
            self.disconnect(c, Qt.SIGNAL("dataChanged"), self.applyTransformation)
        self._referencedQAttrs=[]  
        
        #reset symbols      
        self.sev.resetSafe()
        
        #Find references in the string, create qAttrs if needed, connect to them and change the string to use the qAttr id
        trstring = re.sub(self.cref_RegExp, self.__Match2Id, trstring)
        
        safesymbols = self.sev.getSafe().keys()
        #validate the expression (look for missing symbols) 
        for s in set(re.findall(self.pyVar_RegExp, trstring)):
            if s not in safesymbols:
                self.warning('Missing symbol "%s"'%s)
                return trstring, False
        return trstring,True
            
    def __Match2Id(self, match):
        """
        receives a re.match object for cref_RegExp. Returns the id of an
        existing qAttr corresponding to the match. The qAttr is created
        if it didn't previously exist.
        """
        return self.__createReference(match.groups()[0]).id
        
    def __createReference(self, ref):
        '''creates a (or gets an existing)qAttr and connects to it and adds
        its id to the safe evaluation symbols. It returns the qAttr.
        '''
        c = taurusQAttributeFactory.getQAttr(ref)
        self.connect(c, Qt.SIGNAL("dataChanged"), self.applyTransformation)
        self.sev.addSafe({c.id:c.value})
        self._referencedQAttrs.append(c)
        return c        
        
    def applyTransformation(self):
        try:
            sender = self.sender()
            if isinstance(sender, TaurusQAttribute):
                self.sev.addSafe({sender.id:sender.value})
            self.value = self.sev.eval(self._transformationString)
            self.emit(Qt.SIGNAL("dataChanged"))
        except Exception, e:
            self.warning("the function '%s' could not be evaluated. Reason: %s"%(self._transformationString, repr(e))) 
        
    def handleEvent(self, src, evt_type, val):
        '''Handles Taurus Events for this curve

        See: :meth:`TaurusBaseQAttr.handleEvent`
        '''
        model = src if src is not None else self.getModelObj()
        if model is None:
            self._values = None
            self.emit(Qt.SIGNAL('dataChanged'))
            return
        value = val if isinstance(val, PyTango.DeviceAttribute) else self.getModelValueObj()
        if not isinstance(value, PyTango.DeviceAttribute):
            self.debug("Could not get DeviceAttribute value for this event. Dropping")
            return
        self.value = value.value
        self.emit(Qt.SIGNAL('dataChanged'))
        

