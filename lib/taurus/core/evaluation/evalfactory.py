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

import os, time

import taurus.core
from taurus.core import OperationMode, MatchLevel
from taurus.core.util import SafeEvaluator


class EvaluationAttributeNameValidator(util.Singleton):
    evalattrname = '^((eval|evaluation):)(//([^/?#]*))?([^?#;]*)(;evaluator=([^?#;]*))(\?([^#]*))?'
    
    def __init__(self):
        """ Initialization. Nothing to be done here for now."""
        pass
    
    def init(self, *args, **kwargs):
        """Singleton instance initialization."""
        self.complete_re = re.compile("^%s$" % self.complete_name)
        self.normal_re = re.compile("^%s$" % self.normal_name)
        self.short_re = re.compile("^%s$" % self.short_name)

    def getNames(self, str, factory=None):
        """Returns the complete and short names"""
        
        elems = self.getParams(str)
        if elems is None:
            return None
        
        dev_name = elems.get('devicename')
        attr_name = elems.get('attributename')
        
        if dev_name:
            normal_name = dev_name + "/" + attr_name
        else:
            normal_name = attr_name
            
        return str, normal_name, attr_name
    

class EvaluationDatabase(taurus.core.TaurusDatabase):
    def factory(self):
        return EvaluationFactory()
        
    def __getattr__(self, name):
        return "EvaluationDatabase object calling %s" % name


class EvaluationDevice(taurus.core.TaurusDevice, SafeEvaluator):
    def __init__(self, name, **kw):
        """Object initialization."""
        self.call__init__(taurus.core.TaurusDevice, name, **kw)
        self.SafeEvaluator.__init__(self)

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # TaurusModel necessary overwrite
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # helper class property that stores a reference to the corresponding factory
    _factory = None
    
    @classmethod
    def factory(cls):
        if cls._factory is None:
            cls._factory = taurus.Factory(scheme='eval')
        return cls._factory
    
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # TaurusDevice necessary overwrite
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    def _createHWObject(self):
        return 'Evaluation'
    
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    def getAttribute(self, attrname):
        """Returns the attribute object given its name"""
        raise TaurusException('getAttribute() cannot be called on %s'%self.__class__.__name__)
        
                

class EvaluationAttribute(taurus.core.TaurusAttribute):
    pyVar_RegExp = re.compile("[a-zA-Z_][a-zA-Z0-9_]*") #regexp for a variable/method name (symbol)
    cref_RegExp = re.compile("\{(.+?)\}") #regexp for references to other taurus models within operation model names

    def __init__(self, name, parent, storeCallback = None):
        self.call__init__(taurus.core.TaurusAttribute, name, parent, storeCallback=storeCallback)
        
        self._value = taurus.core.TaurusAttrValue()
        self._references = [] 

        name = str(name)
        trstring, ok = self.preProcessTransformation(name)
        if ok:
            self._transformation = trstring
            self.applyTransformation()
    
    @staticmethod
    def getId(obj, idFormat=r'_V%i_'):
        '''returns an id string for the given object which has the following two properties:
        
            - It is unique for this object during all its life
            - It is a string that can be used as a variable or method name
        
        :param obj: (object) the python object whose id is requested 
        :param idFormat: (str) a format string containing a "`%i`" which, when expanded
                         must be a valid variable name (i.e. it must match
                         `[a-zA-Z_][a-zA-Z0-9_]*`). The default is `_V%i_`
        '''
        return idFormat%id(obj)
        
    def preProcessTransformation(self, trstring):
        """
        parses the transformation string and creates the necessary symbols for
        the evaluator. It also connects any referenced attributes so that the
        transformation gets re-evaluated if they change.
        
        :param trstring: (str) a string to be pre-processed
        
        :return: (tuple<str,bool>) a tuple containing the processed string 
                 and a boolean indicating if the preprocessing was successful.
                 if ok==True, the string is ready to be evaluated
        """
        #disconnect previously referenced qAttrs and clean the list
        for ref in self._references:
            ref.removeListener(self)
        self._references = []  
        
        #reset symbols
        evaluator = self.getParentObj()  
        evaluator.resetSafe()
        
        #Find references in the string, create references if needed, 
        #connect to them and substitute the references by their id
        trstring = re.sub(self.cref_RegExp, self.__Match2Id, trstring)
        
        #validate the expression (look for missing symbols) 
        safesymbols = evaluator.getSafe().keys()
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
        ref = match.groups()[0]
        refobj = self.__createReference(ref)
        return self.getId(refobj)
        
    def __createReference(self, ref):
        '''
        Receives a taurus attribute name and creates/retrieves a reference to
        the attribute object. If the object was not already referenced, it adds
        it to the reference list and adds its id and current value to the
        symbols dictionary of the evaluator.
        
        :param ref: (str) 
        
        :return: (TaurusAttribute) 
        
        '''
        refobj = taurus.Attribute(ref)
        if refobj not in self._references:
            refobj.addListener(self.handleReferenceEvent) #listen to events from the referenced object
            evaluator = self.getParentObj()  
            evaluator.addSafe({self.getId(refobj) : refobj.read().value}) # add its value to the evaluator symbols
            self._references.append(refobj) #add the object to the reference list
        return refobj        
    
    def handleReferenceEvent(self, evt_src, evt_type, evt_value):
        #update the corresponding value
        evaluator = self.getParentObj()  
        evaluator.addSafe({evt_src : evt_value.value})
        #re-evaluate
        self.applyTransformation()
        #notify listeners that the value changed
        self.fireEvent(evt_type, evt_value)
        
    def applyTransformation(self):
        try:
            evaluator = self.getParentObj()  
            self._value.read_value = evaluator.eval(self._transformation)
            self._value.time_stamp = time.time()
            self._value.quality = taurus.core.AttrQuality.ATTR_VALID
        except Exception, e:
            self._value.quality = taurus.core.AttrQuality.ATTR_INVALID
            self.warning("the function '%s' could not be evaluated. Reason: %s"%(self._transformation, repr(e)))
            
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # Necessary to overwrite from TaurusAttribute
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    def isNumeric(self):
        return True
        
    def isBoolean(self):
        return isinstance(self._value.read_value, bool)
    
    def isState(self):
        return False

    def getDisplayValue(self,cache=True):
        return str(self.read(cache=cache).read_value)

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
        if not cache:
            symbols = {}
            for ref in self._references:
                symbols[self.getId(ref)] = ref.read(cache=False)
            evaluator = self.getParentObj()  
            evaluator.addSafe(symbols)
            self.applyTransformation()
        return self._value    

    def poll(self):
        pass
            
    def _subscribeEvents(self):
        pass
        
    def _unsubscribeEvents(self):
        pass

    def isUsingEvents(self):
        False
#------------------------------------------------------------------------------ 

    def factory(self):
        return OperationFactory()
    
    @classmethod
    def getNameValidator(cls):
        return EvaluationAttributeNameValidator()



class EvaluationFactory(taurus.core.util.Singleton, taurus.core.TaurusFactory, taurus.core.util.Logger):
    """A Singleton class designed to provide Operation related objects."""

    schemes = ("eval","evaluation")
    
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