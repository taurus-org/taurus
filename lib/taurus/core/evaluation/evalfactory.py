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

'''
operation module. See __init__.py for more detailed documentation
'''

import os, time, re, weakref

from taurus.core.taurusexception import TaurusException
import taurus.core
from taurus.core import OperationMode, MatchLevel, TaurusSWDevState
from taurus.core.util import SafeEvaluator

class EvaluationAttributeNameValidator(taurus.core.util.Singleton):
    # The groups in a match object using the regexp below are:
    #    1: scheme; named as 'scheme'
    #    2: 
    #    3: evaluatorname; optional; named as 'devname'
    #    4: transformationstring; named as 'attrname'
    #    5:
    #    6: substitution symbols (semicolon separated key=val pairs) ; optional; named as 'subst'
    #    7:
    #    8: fragment; optional; named as 'fragment'
    #
    #    Reconstructing the names
    #    attrname= $4
    #    devname= $3 or EvaluationFactory.DEFAULT_DEVICE
    #    fullname= "eval://evaluator=%s;%s%s%s"%(devname,attrname,$5,$7)
    #
    #                     1                             2          3                      4                    5  6                 7 8
    attrname_pattern = r'^(?P<scheme>eval|evaluation)://(evaluator=(?P<devname>[^?#;]+);)?(?P<attrname>[^?#;]+)(\?(?P<subst>[^#]*))?(#(?P<fragment>.*))?$'
    
    # The following regexp pattern matches <variable>=<value> pairs    
    kvsymbols_pattern = r'([a-zA-Z_][a-zA-Z0-9_]*)=([^#;]+)'

    def __init__(self):
        """ Initialization. Nothing to be done here for now."""
        pass
    
    def init(self, *args, **kwargs):
        """Singleton instance initialization."""
        self.attrname_re = re.compile(self.attrname_pattern)
        self.kvsymbols_re = re.compile(self.kvsymbols_pattern)
        
    def isValid(self,str, matchLevel = MatchLevel.ANY):
        m = self.attrname_re.match(str)
        if m is None: 
            return False
        elif matchLevel == MatchLevel.COMPLETE:
            return m.group('devname') is not None
        else:
            return True
        
    def getParams(self, str):
        m = self.attrname_re.match(str)
        if m is None:
            return None
        return m.groupdict()

    def getNames(self, str, factory=None):
        """Returns the complete, normal and short names"""
        m = self.attrname_re.match(str)
        if m is None:
            return None
        # "bar*blah"
        attr_name = m.group('attrname')
        devname = m.group('devname') or EvaluationFactory.DEFAULT_DEVICE
        #eval://evaluator=foo;bar*blah
        normal_name = "eval://evaluator=%s;%s"%(devname,attr_name) # ???should I put m.group(5) and m.group(7) too?
        #eval://evaluator=foo;123*{a/b/c/d}
        subst = m.group('subst') or ''
        fullname = normal_name
        for k,v in self.kvsymbols_re.findall(subst):
            fullname = re.sub(k,v, fullname) #generate a full name that expands all explicit symbol names            
        return fullname, normal_name, attr_name
    
    def getDeviceName(self, str):
        m = self.attrname_re.match(str)
        if m is None:
            return None
        devname= m.group('devname') or EvaluationFactory.DEFAULT_DEVICE
        return "eval://evaluator=%s"%devname
        
        



class EvaluationDeviceNameValidator(taurus.core.util.Singleton):
    # The groups in a match object using the regexp below are:
    #    1: scheme; named as 'scheme'
    #    2: 
    #    3: evaluatorname; named as 'devname'
    #    4:
    #    5: substitution symbols (semicolon separated key=val pairs) ; optional; named as 'subst'
    #    6:
    #    7: fragment; optional; named as 'fragment'
    #
    #                    1                             2          3                    4  5                 6 7
    devname_pattern = r'^(?P<scheme>eval|evaluation)://(evaluator=(?P<devname>[^?#;]+))(\?(?P<subst>[^#]*))?(#(?P<fragment>.*))?$'
    
    # The following regexp pattern matches <variable>=<value> pairs    
    kvsymbols_pattern = r'([a-zA-Z_][a-zA-Z0-9_]*)=([^#;]+)'

    def __init__(self):
        """ Initialization. Nothing to be done here for now."""
        pass
    
    def init(self, *args, **kwargs):
        """Singleton instance initialization."""
        self.devname_re = re.compile(self.devname_pattern)
        self.kvsymbols_re = re.compile(self.kvsymbols_pattern)
        
    def isValid(self,str, matchLevel = MatchLevel.ANY):
        return self.devname_re.match(str) is not None

    def getNames(self, str, factory=None):
        """Returns the complete, normal and short names. (note: complete=normal)
        
        :param str: (str) input string describing the device
        :param factory: (TaurusFactory) [Unused]
        
        :return: (tuple<str,str,str> or None) A tuple of complete, normal and
                 short names, or None if str is an invalid device name
        """
        m = self.devname_re.match(str)
        if m is None:
            return None
        gdict = m.groupdict() 
        #The following comments are for a name of the type: eval://evaluator=foo;?bar=123;blah={a/b/c/d} 
        devname = gdict.get('devname')  # foo
        normal_name = "eval://evaluator=%s"%(devname) #eval://evaluator=foo
        full_name = normal_name #eval://evaluator=foo
        return full_name, normal_name, devname    

class EvaluationDatabase(taurus.core.TaurusDatabase):
    def factory(self):
        return EvaluationFactory()
        
    def __getattr__(self, name):
        return "EvaluationDatabase object calling %s" % name


class EvaluationDevice(taurus.core.TaurusDevice, SafeEvaluator):
    def __init__(self, name, **kw):
        """Object initialization."""
        self.call__init__(taurus.core.TaurusDevice, name, **kw)
        SafeEvaluator.__init__(self)

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
    
    @classmethod
    def getNameValidator(cls):
        return EvaluationDeviceNameValidator()
    
    def decode(self, event_value):
        if isinstance(event_value, int): # TaurusSWDevState
            new_sw_state = event_value
        else:
            self.info("Unexpected value to decode: %s" % str(event_value))
            new_sw_state = TaurusSWDevState.Crash
        value = taurus.core.TaurusAttrValue() 
        value.value = new_sw_state
        return value
        
                

class EvaluationAttribute(taurus.core.TaurusAttribute):
    pyVar_RegExp = re.compile("[a-zA-Z_][a-zA-Z0-9_]*") #regexp for a variable/method name (symbol)
    cref_RegExp = re.compile("\{(.+?)\}") #regexp for references to other taurus models within operation model names

    def __init__(self, name, parent, storeCallback = None):
        self.call__init__(taurus.core.TaurusAttribute, name, parent, storeCallback=storeCallback)
        
        self._value = taurus.core.TaurusAttrValue()
        self._references = [] 
        self._validator= self.getNameValidator()
        self._transformation = None
        
        params = self._validator.getParams(str(name)) #This should never be None because the init already ran the validator
        trstring = params.get('attrname')
        
        trstring, ok = self.preProcessTransformation(trstring)
        
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
            evaluator = self.getParentObj()
            v = refobj.read().value
            evaluator.addSafe({self.getId(refobj) : v}) # add its value to the evaluator symbols
            self._references.append(refobj) #add the object to the reference list
            refobj.addListener(self.handleReferenceEvent) #listen to events from the referenced object
        return refobj        
    
    def handleReferenceEvent(self, evt_src, evt_type, evt_value):
        try:
            v = evt_value.value
        except AttributeError:
            self.trace('Ignoring event from %s'%repr(evt_src))
            return
        #self.trace('received event from %s (%s=%s)'%(evt_src, self.getId(evt_src), v))
        #update the corresponding value
        evaluator = self.getParentObj()
        evaluator.addSafe({self.getId(evt_src) : v})
        #re-evaluate
        self.applyTransformation()
        #notify listeners that the value changed
        self.fireEvent(evt_type, self._value)
        
    def applyTransformation(self):
        if self._transformation is None: return
        try:
            evaluator = self.getParentObj() 
            self._value.value = evaluator.eval(self._transformation)
            self._value.time = taurus.core.TaurusTimeVal.fromFloat(time.time())
            self._value.quality = taurus.core.AttrQuality.ATTR_VALID
        except Exception, e:
            self._value.quality = taurus.core.AttrQuality.ATTR_INVALID
            self.warning("the function '%s' could not be evaluated. Reason: %s"%(self._transformation, repr(e)))
            #self.traceback(taurus.Warning)
            
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # Necessary to overwrite from TaurusAttribute
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    def isNumeric(self):
        return True
        
    def isBoolean(self):
        return isinstance(self._value.value, bool)
    
    def isState(self):
        return False

    def getDisplayValue(self,cache=True):
        return str(self.read(cache=cache).value)

    def encode(self, value):
        return value

    def decode(self, attr_value):
        return attr_value

    def write(self, value, with_read=True):
        raise TaurusException('Evaluation attributes are read-only')

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
                symbols[self.getId(ref)] = ref.read(cache=False).value
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
        return EvaluationFactory()
    
    @classmethod
    def getNameValidator(cls):
        return EvaluationAttributeNameValidator()



class EvaluationFactory(taurus.core.util.Singleton, taurus.core.TaurusFactory, taurus.core.util.Logger):
    """A Singleton class designed to provide Operation related objects."""

    schemes = ("eval","evaluation")
    DEFAULT_DEVICE = '_DefaultEvaluator'
    DEFAULT_DATABASE = '_DefaultEvalDB'
    def __init__(self):
        """ Initialization. Nothing to be done here for now."""
        pass

    def init(self, *args, **kwargs):
        """Singleton instance initialization."""
        name = self.__class__.__name__
        self.call__init__(taurus.core.util.Logger, name)
        self.call__init__(taurus.core.TaurusFactory)
        self.eval_attrs = weakref.WeakValueDictionary()
        self.eval_devs = weakref.WeakValueDictionary()
        
    def findObjectClass(self, absolute_name):
        """Operation models are always OperationAttributes
        """
        if EvaluationDevice.isValid(absolute_name):
            return EvaluationDevice
        elif EvaluationDevice.isValid(absolute_name):
            return EvaluationAttribute
        else:
            self.debug("Not able to find Object class for %s" % absolute_name)
            self.traceback()
            return None

    def getDatabase(self, db_name=None):
        """Obtain the EvaluationDatabase object.
        
        :param db_name: (str) this is ignored because only one database is supported
                           
        :return: (EvaluationDatabase)
        """
        if not hasattr(self, "_db"):
            self._db = EvaluationDatabase(self.DEFAULT_DATABASE)
        return self._db

    def getDevice(self, dev_name):
        """Obtain the object corresponding to the given device name. If the 
        corresponding device already exists, the existing instance is returned. 
        Otherwise a new instance is stored and returned.
           
        :param dev_name: (str) the device name string. See
                         :mod:`taurus.core.evaluation` for valid device names
        
        :return: (EvaluationDevice)
         
        @throws TaurusException if the given name is invalid.
        """
        d = self.eval_devs.get(dev_name, None)
        if d is None:
            validator = EvaluationDevice.getNameValidator()
            names = validator.getNames(dev_name)
            if names is None:
                raise TaurusException("Invalid evaluator device name %s" % dev_name)
            db = self.getDatabase()
            d = EvaluationDevice(names[0], parent=db, storeCallback=self._storeDev) #use full name
        return d
        
    def getAttribute(self, attr_name):
        """Obtain the object corresponding to the given attribute name. If the 
        corresponding attribute already exists, the existing instance is
        returned. Otherwise a new instance is stored and returned. The evaluator
        device associated to this attribute will also be created if necessary.
           
        :param attr_name: (str) the attribute name string. See
                          :mod:`taurus.core.evaluation` for valid attribute names
        
        :return: (EvaluationAttribute)
         
        @throws TaurusException if the given name is invalid.
        """
        a = self.eval_attrs.get(attr_name, None)
        if a is None:
            validator = EvaluationAttribute.getNameValidator()
            names = validator.getNames(attr_name)
            if names is None:
                raise TaurusException("Invalid evaluator attribute name %s" % dev_name)
            dev = self.getDevice(validator.getDeviceName(attr_name))
            a = EvaluationAttribute(names[0], parent=dev, storeCallback=self._storeAttr) #use full name
        return a

    def getConfiguration(self, param):
        return None

    def _getConfigurationFromName(self, name):
        return None
    
    def _getConfigurationFromAttribute(self, attr):
        return None
    
    def _storeDev(self, dev):
        name = dev.getFullName()
        exists = self.eval_devs.get(name)
        if exists is not None:
            if exists == dev: 
                self.debug("%s has already been registered before" % name)
                raise taurus.core.DoubleRegistration
            else:
                self.debug("%s has already been registered before with a different object!" % name)
                raise taurus.core.DoubleRegistration
        self.eval_devs[name] = dev
    
    def _storeAttr(self, attr):
        name = attr.getFullName()
        exists = self.eval_attrs.get(name)
        if exists is not None:
            if exists == attr: 
                self.debug("%s has already been registered before" % name)
                raise taurus.core.DoubleRegistration
            else:
                self.debug("%s has already been registered before with a different object!" % name)
                raise taurus.core.DoubleRegistration
        self.eval_attrs[name] = attr
        
    def _storeConfig(self, name, config):
        pass
    
    

#===============================================================================
# Just for testing
#===============================================================================
if __name__ == "__main__":
#    f = EvaluationFactory()
#    #d = f.getDevice('eval://evaluator=foo')
#    a = f.getAttribute('eval://2*{sys/tg_test/1/short_scalar}+{sys/tg_test/1/double_scalar}')
    import taurus.core
    a=taurus.Attribute('eval://[{sys/tg_test/1/short_scalar},{sys/tg_test/1/double_scalar}, {sys/tg_test/1/short_scalar}+{sys/tg_test/1/double_scalar}]')
#    a=taurus.Attribute('eval://2*{sys/tg_test/1/short_scalar}')
    evt_ct = 0
    def kk(s,t,v):
        global evt_ct
        print evt_ct, v
        evt_ct += 1

    a.addListener(kk)
    while evt_ct <= 10:
        time.sleep(1)
        
