#!/usr/bin/env python
from taurus.core.taurusexception import TaurusException

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

'''
operation module. See __init__.py for more detailed documentation
'''

import os

import taurus.core
from taurus.core import OperationMode, MatchLevel


class EvaluationAttribute(taurus.core.TaurusAttribute):
    pyVar_RegExp = re.compile("[a-zA-Z_][a-zA-Z0-9_]*") #regexp for a variable/method name (symbol)
    cref_RegExp = re.compile("\{(.+?)\}") #regexp for references to other taurus models within operation model names

    def __init__(self, name, parent, storeCallback = None):
        self.call__init__(taurus.core.TaurusAttribute, name, parent, storeCallback=storeCallback)
        self.sev = SafeEvaluator()
        self._processName(name)
        
    def _processName(self, name):
        if self.name is None:
            self._value = None
            self._transformationString = None
            return
        #for formulas
        name= str(name)
        trstring, ok = self.preProcessTransformation(name)
        if ok:
            self._transformationString = trstring
            self.applyTransformation()
        else:
            print "!!!!!!!!!!!!!", self._transformationString
            return

        
    def preProcessTransformation(self, trstring):
        raise NotImplementedError
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
        for c in self._references:
            self.disconnect(c, Qt.SIGNAL("dataChanged"), self.applyTransformation)
        self._references = []  
        
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
        '''creates a (or gets an existing) taurus attribute and connects to it and adds
        its id to the safe evaluation symbols. It returns the qAttr.
        Receives a taurus attribute name and creates a reference to it. 
        It also populates the safe evaluation symbols dict with 
        
        '''
        c = taurus.Attribute(ref)
        self.connect(c, Qt.SIGNAL("dataChanged"), self.applyTransformation)
        self.sev.addSafe({c.id:c.value})
        self._references.append(c)
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
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # Necessary to overwrite from TaurusAttribute
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    def isNumeric(self):
        return True
        
    def isBoolean(self):
        return False
    
    def isState(self):
        return False

    def getDisplayValue(self,cache=True):
        return str(self._value.read_value)

    def encode(self, value):
        return value

    def decode(self, attr_value):
        return attr_value

    def write(self, value, with_read=True):
        raise TaurusException('Operation attributes are read-only')

    def read(self, cache=True):
        '''returns the value of the attribute.
        
        :param cache: (bool) If True (default), the last calculated value will
                      be returned. If False, the referenced values will be re-
                      read and the transformation string will be re-evaluated
                      
        :return: attribute value
        '''
        if cache:
            return self._value
        else:
            raise NotImplementedError()
        
            

    def poll(self):
        raise NotImplementedError
            
    def _subscribeEvents(self):
        raise RuntimeError("Not allowed to call AbstractClass TaurusAttribute._subscribeEvents")
        
    def _unsubscribeEvents(self):
        raise RuntimeError("Not allowed to call AbstractClass TaurusAttribute._unsubscribeEvents")

    def isUsingEvents(self):
        raise RuntimeError("Not allowed to call AbstractClass TaurusAttribute.isUsingEvents")
#------------------------------------------------------------------------------ 
        
    def factory(self):
        return OperationFactory()

  

    def read(self, cache=True):
        return self._value
        
    def _subscribeEvents(self):
        pass
        
    def _unSubscribeEvents(self):
        pass

    def _getRealConfig(self):
        if self._config is None:
            cfg_name = "%s?configuration" % self.getFullName()
            self._config = SimulationConfiguration(cfg_name, self)
        return self._config

    def getConfig(self):
        return self._getRealConfig()

    def addListener(self, listener):
        """ Add a TaurusListener object in the listeners list.
            If it is the first element and Polling is enabled starts the 
            polling mechanism.
            If the listener is already registered nothing happens."""
        ret = taurus.core.TaurusAttribute.addListener(self, listener)
        if not ret:
            return ret

        #fire a first configuration event
        cfg_val, val = self.getConfig().getValueObj(), self.read()
        self.fireEvent(taurus.core.TaurusEventType.Config, cfg_val, listener)
        #fire a first change event
        self.fireEvent(taurus.core.TaurusEventType.Change, val, listener)
        return ret

class OperationFactory(taurus.core.util.Singleton, taurus.core.TaurusFactory, taurus.core.util.Logger):
    """A Singleton class designed to provide Operation related objects."""

    schemes = ("op","operation")
    
    def __init__(self):
        """ Initialization. Nothing to be done here for now."""
        pass

    def init(self, *args, **kwargs):
        """Singleton instance initialization."""
        name = self.__class__.__name__
        self.call__init__(taurus.core.util.Logger, name)
        self.call__init__(taurus.core.TaurusFactory)


        
    def findObjectClass(self, absolute_name):
        """Operation models are always OperationAttributes
        """
        return OperationAttribute

    def getDatabase(self, db_name=None):
        """getDatabase(string db_name) -> taurus.core.TaurusDatabase
           
        Obtain the object corresponding to the given database name or the 
        default database if db_name is None.
        If the corresponding database object already exists, the existing 
        instance is returned. Otherwise a new instance is stored and returned.
           
        @param[in] db_name database name string. It should be formed like: 
                           <schema>://<authority>. If <schema> is ommited then 
                           it will use the default schema. if db_name is None, 
                           the default database is used
                           
        @return a taurus.core.TaurusDatabase object 
        @throws TaurusException if the given name is invalid.
        """
        if not db_name is None:
            validator = SimulationDatabase.getNameValidator()
            params = validator.getParams(db_name)
            if params is None:
                raise taurus.core.TaurusException("Invalid database name %s." % db_name)
        
        if not hasattr(self, "_db"):
            self._db = SimulationDatabase("sim:01")
        return self._db

    def getDevice(self, dev_name):
        """getDevice(string dev_name) -> taurus.core.TaurusDevice
           
        Obtain the object corresponding to the given device name. If the 
        corresponding device already exists, the existing instance is returned. 
        Otherwise a new instance is stored and returned.
           
        @param[in] dev_name the device name string. It should be formed like:
                            <schema>://<authority>/<device name>. If <schema> 
                            is ommited then it will use the default schema. 
                            If authority is ommited then it will use the 
                            default authority for the schema.
        
        @return a taurus.core.TaurusDevice object 
        @throws TaurusException if the given name is invalid.
        """
        validator = SimulationDevice.getNameValidator()
        params = validator.getParams(dev_name)
        if params is None:
            raise taurus.core.TaurusException("Invalid device name %s." % dev_name)

        if not hasattr(self, "_dev"):
            db = self.getDatabase("sim:01")
            self._dev = SimulationDevice("sim:01/a/b/c", parent=db, storeCallback=self._storeDev)
        return self._dev
        
    def getAttribute(self, attr_name):
        """getAttribute(string attr_name) -> taurus.core.TaurusAttribute

        Obtain the object corresponding to the given attribute name.
        If the corresponding attribute already exists, the existing instance
        is returned. Otherwise a new instance is stored and returned.

        @param[in] attr_name string attribute name
             
        @return a taurus.core.TaurusAttribute object 
        @throws TaurusException if the given name is invalid.
        """
        validator = SimulationAttribute.getNameValidator()
        params = validator.getParams(attr_name)
        
        if params is None:
            raise taurus.core.TaurusException("Invalid attribute name %s." % attr_name)
        
        if not hasattr(self, "_attr"):
            dev = self.getDevice("sim:01/a/b/c")
            SimulationAttribute("sim:01/a/b/c/d", parent=dev, storeCallback=self._storeAttr)
        return self._attr

    def getConfiguration(self, param):
        """getConfiguration(param) -> taurus.core.TaurusConfiguration

        Obtain the object corresponding to the given attribute or full name.
        If the corresponding configuration already exists, the existing instance
        is returned. Otherwise a new instance is stored and returned.

        @param[in] param taurus.core.TaurusAttribute object or full configuration name
           
        @return a taurus.core.TaurusAttribute object
        @throws TaurusException if the given name is invalid.
        """
        if isinstance(param, str):
            return self._getConfigurationFromName(param)
        return self._getConfigurationFromAttribute(param)

    def _getConfigurationFromName(self, name):
        validator = SimulationConfiguration.getNameValidator()
        params = validator.getParams(name)
                
        if params is None:
            raise taurus.core.TaurusException("Invalid configuration name %s." % name)

        if not hasattr(self, "_conf"):
            name = "sim:01/a/b/c/d?configuration"
            attr = self.getAttribute("sim:01/a/b/c/d")
            SimulationConfiguration(name, attr, storeCallback=self._storeConfig)
        return self._config
    
    def _getConfigurationFromAttribute(self, attr):
        if not hasattr(self, "_conf"):
            name = "sim:01/a/b/c/d?configuration"
            SimulationConfiguration(name, attr, storeCallback=self._storeConfig)
        return self._config
    
    def _storeDev(self, dev):
        self._dev = dev
    
    def _storeAttr(self, attr):
        self._attr = attr
        
    def _storeConfig(self, name, config):
        self._config = config