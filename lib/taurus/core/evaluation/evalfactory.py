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
evaluation module. See __init__.py for more detailed documentation
'''
__all__ = ['EvaluationFactory', 'EvaluationDatabase', 'EvaluationDevice', 
           'EvaluationAttribute','EvaluationConfiguration', 
           'EvaluationConfigurationNameValidator', 'EvaluationDeviceNameValidator', 
           'EvaluationAttributeNameValidator']



import time, re, weakref
import numpy

import taurus
from taurus.core.taurusexception import TaurusException
from taurus.core.tauruspollingtimer import TaurusPollingTimer
from taurus.core.taurusbasetypes import MatchLevel, TaurusSWDevState, \
    SubscriptionState, TaurusEventType, TaurusAttrValue, TaurusTimeVal, \
    AttrQuality
from taurus.core.util.log import Logger
from taurus.core.util.singleton import Singleton
from taurus.core.util.safeeval import SafeEvaluator
from taurus.core.taurusfactory import TaurusFactory
from taurus.core.taurusattribute import TaurusAttribute
from taurus.core.taurusdevice import TaurusDevice
from taurus.core.taurusdatabase import TaurusDatabase
from taurus.core.taurusconfiguration import TaurusConfiguration


class AbstractEvaluationNameValidator(Singleton):
    #the object name class. *must* be implemented in subclasses
    name_pattern = '' #must be implemented in children classes
    # The following regexp pattern matches <variable>=<value> pairs    
    kvsymbols_pattern = r'([a-zA-Z_][a-zA-Z0-9_]*)=([^#;]+)'

    def __init__(self):
        """ Initialization. Nothing to be done here for now."""
        pass
    
    def init(self, *args, **kwargs):
        """Singleton instance initialization."""
        self.name_re = re.compile(self.name_pattern)
        self.kvsymbols_re = re.compile(self.kvsymbols_pattern)
        
    def isValid(self,s, matchLevel = MatchLevel.ANY):
        return self.name_re.match(s) is not None
        
    def getParams(self, s):
        m = self.attrname_re.match(s)
        if m is None:
            return None
        return m.groupdict()

    def getNames(self, s, factory=None):
        """Returns the full, normal and simple names for this object, or None if there is no match'''
        """
        raise RuntimeError('Not Allowed to call this method from subclasses')
    
    def getDeviceName(self, s, full=True):
        '''
        returns the device name for the given attribute name. 
        If full=True, the returned name includes the DB name
        '''
        m = self.name_re.match(s)
        if m is None:
            return None
        devname = m.group('devname') or EvaluationFactory.DEFAULT_DEVICE
        if full:
            return '%s;dev=%s'%(self.getDBName(s),devname)
        else:
            return 'eval://dev=%s'%devname
    
    def getDBName(self,s):
        '''returns the full data base name for the given attribute name'''
        m = self.name_re.match(s)
        if m is None:
            return None
        dbname = m.group('dbname') or EvaluationFactory.DEFAULT_DATABASE
        return "eval://db=%s"%dbname
    

class EvaluationAttributeNameValidator(AbstractEvaluationNameValidator):
    # The groups in a match object using the regexp below are:
    #    1: scheme; named as 'scheme'
    #    2: 
    #    3: database name; optional; named as 'dbname'
    #    4: 
    #    5: device name; optional; named as 'devname'
    #    6: attribute name (transformation string); named as 'attrname'
    #    7:
    #    8: substitution symbols (semicolon separated key=val pairs) ; optional; named as 'subst'
    #    9:
    #    A: fragment; optional; named as 'fragment'
    #
    #    Reconstructing the names
    #    attrname= $4
    #    devname= $3 or EvaluationFactory.DEFAULT_DEVICE
    #    fullname= "eval://dev=%s;%s%s%s"%(devname,attrname,$5,$7)
    #   
    #                 1                             2   3                     4    5                      6                    7                    8                  9 A                                                        
    name_pattern = r'^(?P<scheme>eval|evaluation)://(db=(?P<dbname>[^?#;]+);)?(dev=(?P<devname>[^?#;]+);)?(?P<attrname>[^?#;]+)(\?(?!configuration=)(?P<subst>[^#?]*))?(#(?P<fragment>.*))?$'
        
    def isValid(self,s, matchLevel = MatchLevel.ANY):
        m = self.name_re.match(s)
        if m is None: 
            return False
        elif matchLevel == MatchLevel.COMPLETE:
            return m.group('devname') is not None and m.group('dbname') is not None
        else:
            return True

    def getNames(self, s, factory=None):
        """Returns the complete, normal and short names.
        
        For example::
        
            >>> EvaluationAttributeNameValidator.getNames("eval://dev=foo;bar*blah?bar=123;blah={a/b/c/d}#[1:-3]")
            >>> ("eval://db=_DefaultEvalDB;dev=foo;123*{a/b/c/d}", "eval://dev=foo;bar*blah", "bar*blah")
        
        """
        m = self.name_re.match(s)
        if m is None:
            return None
        #The following comments are for an example name like: "eval://dev=foo;bar*blah?bar=123;blah={a/b/c/d}#[1:-3]"
        attr_name = m.group('attrname') # attr_name = "bar*blah"
        normal_name = "%s;%s"%(self.getDeviceName(s, full=False),attr_name) #normal_name = "eval://dev=foo;bar*blah"
        expanded_attr_name = self.getExpandedTransformation(s)
        fullname = "%s;%s"%(self.getDeviceName(s, full=True),expanded_attr_name) #fullname = "eval://db=_DefaultEvalDB;dev=foo;123*{a/b/c/d}"
        return fullname, normal_name, attr_name
    
    def getExpandedTransformation(self, s):
        'expands the attribute name by substituting all symbols'
        m = self.name_re.match(s)
        if m is None:
            return None
        transf = m.group('attrname')
        subst = m.group('subst') or ''
        for k,v in self.kvsymbols_re.findall(subst):
            transf = re.sub(k,v, transf)
        return transf
        

class EvaluationDeviceNameValidator(AbstractEvaluationNameValidator):
    '''A validator of names for :class:`EvaluationDevice`'''
    # The groups in a match object using the regexp below are:
    #    1: scheme; named as 'scheme'
    #    2: 
    #    3: database name; optional; named as 'dbname'
    #    4: 
    #    5: devicename; named as 'devname'
    #    6:
    #    7: substitution symbols (semicolon separated key=val pairs) ; optional; named as 'subst'
    #
    #                 1                             2   3                     4    5                    6                    7                                     
    name_pattern = r'^(?P<scheme>eval|evaluation)://(db=(?P<dbname>[^?#;]+);)?(dev=(?P<devname>[^?#;]+))(\?(?!configuration=)(?P<subst>[^#?]*))?$'
    
    def getNames(self, s, factory=None):
        """Returns the complete, normal and short names. (note: complete=normal)
        
        :param s: (str) input string describing the device
        :param factory: (TaurusFactory) [Unused]
        
        :return: (tuple<str,str,str> or None) A tuple of complete, normal and
                 short names, or None if s is an invalid device name
        """
        m = self.name_re.match(s)
        if m is None:
            return None
        #The following comments are for a name of the type: eval://dev=foo?bar=123;blah={a/b/c/d} 
        devname = m.group('devname')  # foo
        normal_name = self.getDeviceName(s, full=False) #eval://dev=foo
        full_name = self.getDeviceName(s, full=True) #eval://db=_DefaultEvalDB;dev=foo
        return full_name, normal_name, devname


class EvaluationConfigurationNameValidator(AbstractEvaluationNameValidator):
    '''A validator of names for :class:`EvaluationConfiguration`'''
    # The groups in a match object using the regexp below are:
    #    1: scheme; named as 'scheme'
    #    2: 
    #    3: database name; optional; named as 'dbname'
    #    4: 
    #    5: device name; optional; named as 'devname'
    #    6: transformationstring; named as 'attrname'
    #    7:
    #    8: substitution symbols (semicolon separated key=val pairs) ; optional; named as 'subst'
    #    9:
    #    A: configuration key; named as 'cfgkey'
    #
    #    Reconstructing the names
    #                 1                             2   3                     4    5                      6                    7                    8                  9                 A                    
    name_pattern = r'^(?P<scheme>eval|evaluation)://(db=(?P<dbname>[^?#;]+);)?(dev=(?P<devname>[^?#;]+);)?(?P<attrname>[^?#;]+)(\?(?!configuration=)(?P<subst>[^#?]*))?(\?configuration=?(?P<cfgkey>[^#?]*))$'
        
    def isValid(self,s, matchLevel = MatchLevel.ANY):
        m = self.name_re.match(s)
        if m is None: 
            return False
        elif matchLevel == MatchLevel.COMPLETE:
            return m.group('devname') is not None and m.group('dbname') is not None
        else:
            return True

    def getNames(self, s, factory=None):
        """Returns the complete, normal and short names"""
        m = self.name_re.match(s)
        if m is None:
            return None
        #The following comments are for an example name like: "eval://dev=foo;bar*blah?bar=123;blah={a/b/c/d}?configuration=label"
        cfg_key = m.group('cfgkey') # cfg_key = "label"
        attr_name = m.group('attrname')
        normal_name = "%s;%s?configuration"%(self.getDeviceName(s, full=False),attr_name) #normal_name = "eval://dev=foo;bar*blah?configuration"
        expanded_attr_name = self.getExpandedTransformation(s)
        fullname = "%s;%s?configuration"%(self.getDeviceName(s, full=True),expanded_attr_name) #fullname = "eval://db=_DefaultEvalDB;dev=foo;123*{a/b/c/d}?configuration"
        return fullname, normal_name, cfg_key
    
    def getAttrName(self, s):
        names = self.getNames(s)
        if names is None: return None
        return names[0][:-len('?configuration')] #remove the "?configuration" substring from the fullname
        
    def getExpandedTransformation(self, s):
        'expands the attribute name by substituting all symbols'
        m = self.name_re.match(s)
        if m is None:
            return None
        transf = m.group('attrname')
        subst = m.group('subst') or ''
        for k,v in self.kvsymbols_re.findall(subst):
            transf = re.sub(k,v, transf)
        return transf

class EvaluationDatabase(TaurusDatabase):
    '''
    Dummy database class for Evaluation (the Database concept is not used in the Evaluation scheme)
    
    .. warning:: In most cases this class should not be instantiated directly.
                 Instead it should be done via the :meth:`EvaluationFactory.getDataBase`
    '''
    def factory(self):
        return EvaluationFactory()
        
    def __getattr__(self, name):
        return "EvaluationDatabase object calling %s" % name


class EvaluationDevice(TaurusDevice, SafeEvaluator):
    '''
    The evaluator object. It is a :class:`TaurusDevice` and is used as the
    parent of :class:`EvaluationAttribute` objects for which it performs the
    mathematical evaluation.
    
    .. seealso:: :mod:`taurus.core.evaluation`
    
    .. warning:: In most cases this class should not be instantiated directly.
                 Instead it should be done via the :meth:`EvaluationFactory.getDevice`
    '''
    _symbols = []
    
    def __init__(self, name, **kw):
        """Object initialization."""
        self.call__init__(TaurusDevice, name, **kw)
        safedict = {}
        for s in self._symbols:
            if hasattr(self,s):
                safedict[s] = getattr(self,s)
        SafeEvaluator.__init__(self, safedict=safedict)        

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
        full_attrname = "%s;%s"%(self.getFullName(), attrname)
        return self.factory().getAttribute(full_attrname)
    
    @classmethod
    def getNameValidator(cls):
        return EvaluationDeviceNameValidator()
    
    def decode(self, event_value):
        if isinstance(event_value, int): # TaurusSWDevState
            new_sw_state = event_value
        else:
            self.info("Unexpected value to decode: %s" % str(event_value))
            new_sw_state = TaurusSWDevState.Crash
        value = TaurusAttrValue() 
        value.value = new_sw_state
        return value
    

class EvaluationAttribute(TaurusAttribute):
    '''
    A :class:`TaurusAttribute` that can be used to perform mathematical
    operations involving other arbitrary Taurus attributes. The mathematical
    operation is described in the attribute name itself. An Evaluation Attribute
    will keep references to any other attributes being referenced and it will
    update its own value whenever any of the referenced attributes change.
    
    .. seealso:: :mod:`taurus.core.evaluation` 
    
    .. warning:: In most cases this class should not be instantiated directly.
                 Instead it should be done via the :meth:`EvaluationFactory.getAttribute`
    '''
    pyStr_RegExp = re.compile(r'(?:\"[^\"]+?\")|(?:\'[^\']+?\')') #matches a single or double-quoted string
    pyVar_RegExp = re.compile("[a-zA-Z_][a-zA-Z0-9_]*") #regexp for a variable/method name (symbol)
    cref_RegExp = re.compile("\{(.+?)\}") #regexp for references to other taurus models within operation model names

    def __init__(self, name, parent, storeCallback = None):
        self.call__init__(TaurusAttribute, name, parent, storeCallback=storeCallback)
        
        self._value = TaurusAttrValue()
        self._value.config.writable = False #Evaluation Attributes are always read-only (at least for now)
        self._references = [] 
        self._validator= self.getNameValidator()
        self._transformation = None
        # reference to the configuration object
        self.__attr_config = None#taurus.core.configuration.TaurusConfiguration()
        self.__subscription_state = SubscriptionState.Unsubscribed

        
        trstring = self._validator.getExpandedTransformation(str(name)) #This should never be None because the init already ran the validator
        
        trstring, ok = self.preProcessTransformation(trstring)
        
        if ok:
            self._transformation = trstring
            self.applyTransformation()

    def __getattr__(self,name):
        return getattr(self._getRealConfig(), name)
    
    def _getRealConfig(self):
        """ Returns the current configuration of the attribute."""
        if self.__attr_config is None:
            cfg_name = "%s?configuration" % self.getFullName()
            self.__attr_config = EvaluationConfiguration(cfg_name, self)
        return self.__attr_config
    
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
        #disconnect previously referenced attributes and clean the list
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
        trimmedstring = re.sub(self.pyStr_RegExp, '', trstring) #remove literal text strings from the validation
        for s in set(re.findall(self.pyVar_RegExp, trimmedstring)):
            if s not in safesymbols:
                self.warning('Missing symbol "%s"'%s)
                return trstring, False
            
        #If all went ok, enable/disable polling based on whether there are references or not
        wantpolling = not self.isUsingEvents()
        haspolling = self.isPollingEnabled()
        if wantpolling:
            self._activatePolling()
        elif haspolling and not wantpolling:
            self.disablePolling()
            
        
        return trstring,True
                    
    def __Match2Id(self, match):
        """
        receives a re.match object for cref_RegExp. Returns the id of an
        existing taurus attribute corresponding to the match. The attribute is created
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
        return refobj        
    
    def eventReceived(self, evt_src, evt_type, evt_value):
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

        if self.isUsingEvents():
            self.fireEvent(evt_type, self._value)
        
    def applyTransformation(self):
        if self._transformation is None: return
        try:
            evaluator = self.getParentObj() 
            self._value.value = evaluator.eval(self._transformation)
            self._value.time = TaurusTimeVal.now()
            self._value.quality = AttrQuality.ATTR_VALID
            self._value.config.data_format = len(numpy.shape(self._value.value))
        except Exception, e:
            self._value.quality = AttrQuality.ATTR_INVALID
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
        v = self.read(cache=False)
        self.fireEvent(TaurusEventType.Periodic, v)
            
    def _subscribeEvents(self): 
        pass
        
    def _unsubscribeEvents(self):
        pass

    def isUsingEvents(self):
        return bool(len(self._references)) #if this attributes depends from others, then we consider it uses events
        
#------------------------------------------------------------------------------ 

    def factory(self):
        return EvaluationFactory()
    
    @classmethod
    def getNameValidator(cls):
        return EvaluationAttributeNameValidator()

    def __fireRegisterEvent(self, listener):
        #fire a first change event
        try:
            v = self.read()
            self.fireEvent(TaurusEventType.Change, v, listener)
        except:
            self.fireEvent(TaurusEventType.Error, None, listener)
    
    def addListener(self, listener):
        """ Add a TaurusListener object in the listeners list.
            If it is the first listener, it triggers the subscription to the referenced attributes.
            If the listener is already registered nothing happens."""
        
        #subscribe to configuration events for this attribute
        cfg = self.getConfig()
        cfg.addListener(listener)
        
        initial_subscription_state = self.__subscription_state
        
        ret = TaurusAttribute.addListener(self, listener)

        if not ret:
            return ret
        
        if self.__subscription_state == SubscriptionState.Unsubscribed:
            for refobj in self._references:
                refobj.addListener(self) #subscribe to the referenced attributes
            self.__subscription_state = SubscriptionState.Subscribed

        assert len(self._listeners) >= 1        
        #if initial_subscription_state == SubscriptionState.Subscribed:
        if len(self._listeners) > 1 and (initial_subscription_state == SubscriptionState.Subscribed or self.isPollingActive()):
            taurus.Manager().addJob(self.__fireRegisterEvent, None, (listener,))
        return ret
        
    def removeListener(self, listener):
        """ Remove a TaurusListener from the listeners list. If polling enabled 
            and it is the last element then stop the polling timer.
            If the listener is not registered nothing happens."""
        ret = TaurusAttribute.removeListener(self, listener)

        cfg = self._getRealConfig()
        cfg.removeListener(listener)
        
        if ret and not self.hasListeners():
            self._deactivatePolling()
            self.__subscription_state = SubscriptionState.Unsubscribed
        return ret
    

class EvaluationConfiguration(TaurusConfiguration):
    '''
    A :class:`TaurusConfiguration` 
    
    .. seealso:: :mod:`taurus.core.evaluation` 
    
    .. warning:: In most cases this class should not be instantiated directly.
                 Instead it should be done via the :meth:`EvaluationFactory.getConfig`
    '''
    def __init__(self, name, parent, storeCallback = None):
        self.call__init__(TaurusConfiguration, name, parent, storeCallback=storeCallback)
        
        #fill the attr info
        i = parent.read().config
        a=parent
        d=self._getDev()
        # add dev_name, dev_alias, attr_name, attr_full_name
        i.dev_name = d.getNormalName()
        i.dev_alias = d.getSimpleName()
        i.attr_name = a.getSimpleName()
        i.attr_fullname = a.getNormalName()
        i.label = a.getSimpleName()
        self._attr_info = i
        
    def __getattr__(self, name): 
        try:
            return getattr(self._attr_info,name)
        except:
            raise AttributeError("'%s'object has no attribute '%s'"%(self.__class__.__name__, name))
    @classmethod
    def getNameValidator(cls):
        return EvaluationConfigurationNameValidator()
        
    def _subscribeEvents(self): 
        pass
    
    def _unSubscribeEvents(self):
        pass   
    
    def factory(self):
        EvaluationFactory()
    
    def getValueObj(self, cache=True):
        """ Returns the current configuration for the attribute."""
        return self._attr_info   
    
class EvaluationFactory(Singleton, TaurusFactory, Logger):
    """
    A Singleton class that provides Evaluation related objects.
    """

    schemes = ("eval","evaluation")
    DEFAULT_DEVICE = '_DefaultEvaluator'
    DEFAULT_DATABASE = '_DefaultEvalDB'
    def __init__(self):
        """ Initialization. Nothing to be done here for now."""
        pass

    def init(self, *args, **kwargs):
        """Singleton instance initialization."""
        name = self.__class__.__name__
        self.call__init__(Logger, name)
        self.call__init__(TaurusFactory)
        self.eval_attrs = weakref.WeakValueDictionary()
        self.eval_devs = weakref.WeakValueDictionary()
        self.eval_configs = weakref.WeakValueDictionary()
        
    def findObjectClass(self, absolute_name):
        """Operation models are always OperationAttributes
        """
        if EvaluationConfiguration.isValid(absolute_name):
            return EvaluationConfiguration
        elif EvaluationDevice.isValid(absolute_name):
            return EvaluationDevice
        elif EvaluationAttribute.isValid(absolute_name):
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
            fullname, normalname, devname = names
            d = self.eval_devs.get(fullname, None)
            if d is None:
                tmp = devname.rsplit('.', 1)
                if len(tmp)==2:
                    modulename, classname = tmp
                    try:
                        m = __import__(modulename, globals(), locals(), [classname], -1)
                        DevClass = getattr(m, classname)
                    except:
                        self.warning('Problem importing "%s"'%devname)
                        raise
                elif len(tmp)==1:
                    DevClass = EvaluationDevice 
                db = self.getDatabase()
                d = DevClass(fullname, parent=db, storeCallback=self._storeDev) #use full name
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
        a = self.eval_attrs.get(attr_name, None) #first try with the given name
        if a is None: #if not, try with the full name
            validator = EvaluationAttribute.getNameValidator()
            names = validator.getNames(attr_name)
            if names is None:
                raise TaurusException("Invalid evaluation attribute name %s" % attr_name)
            fullname = names[0]
            a = self.eval_attrs.get(fullname, None)
            if a is None: #if the full name is not there, create one
                dev = self.getDevice(validator.getDeviceName(attr_name))
                a = EvaluationAttribute(fullname, parent=dev, storeCallback=self._storeAttr) #use full name
        return a

    def getConfiguration(self, param):
        """getConfiguration(param) -> taurus.core.taurusconfiguration.TaurusConfiguration

        Obtain the object corresponding to the given attribute or full name.
        If the corresponding configuration already exists, the existing instance
        is returned. Otherwise a new instance is stored and returned.

        @param[in] param taurus.core.taurusattribute.TaurusAttribute object or full configuration name
           
        @return a taurus.core.taurusattribute.TaurusAttribute object
        @throws TaurusException if the given name is invalid.
        """
        if isinstance(param, str):
            return self._getConfigurationFromName(param)
        return self._getConfigurationFromAttribute(param)

    def _getConfigurationFromName(self, cfg_name):
        cfg = self.eval_configs.get(cfg_name, None) #first try with the given name
        if cfg is None: #if not, try with the full name
            validator = EvaluationConfiguration.getNameValidator()
            names = validator.getNames(cfg_name)
            if names is None:
                raise TaurusException("Invalid evaluation configuration name %s" % cfg_name)
            fullname = names[0]
            cfg = self.eval_configs.get(fullname, None)
            if cfg is None: #if the full name is not there, create one
                attr = self.getAttribute(validator.getAttrName(cfg_name))
                cfg = EvaluationConfiguration(names[0], parent=attr, storeCallback=self._storeConfig) #use full name
        return cfg
        
    def _getConfigurationFromAttribute(self, attr):
        cfg = attr.getConfig()
        cfg_name = attr.getFullName() + "?configuration"
        self.eval_configs[cfg_name] = cfg
        return cfg
    
    def _storeDev(self, dev):
        name = dev.getFullName()
        exists = self.eval_devs.get(name)
        if exists is not None:
            if exists == dev: 
                self.debug("%s has already been registered before" % name)
                raise DoubleRegistration
            else:
                self.debug("%s has already been registered before with a different object!" % name)
                raise DoubleRegistration
        self.eval_devs[name] = dev
    
    def _storeAttr(self, attr):
        name = attr.getFullName()
        exists = self.eval_attrs.get(name)
        if exists is not None:
            if exists == attr: 
                self.debug("%s has already been registered before" % name)
                raise DoubleRegistration
            else:
                self.debug("%s has already been registered before with a different object!" % name)
                raise DoubleRegistration
        self.eval_attrs[name] = attr
        
    def _storeConfig(self, fullname, config):
        #name = config.getFullName()
        name = fullname
        exists = self.eval_configs.get(name)
        if exists is not None:
            if exists == config: 
                self.debug("%s has already been registered before" % name)
                raise DoubleRegistration
            else:
                self.debug("%s has already been registered before with a different object!" % name)
                raise DoubleRegistration
        self.eval_configs[name] = config
        
    def addAttributeToPolling(self, attribute, period, unsubscribe_evts = False):
        """Activates the polling (client side) for the given attribute with the
           given period (seconds).

           :param attribute: (taurus.core.tango.TangoAttribute) attribute name.
           :param period: (float) polling period (in seconds)
           :param unsubscribe_evts: (bool) whether or not to unsubscribe from events
        """
        tmr = self.polling_timers.get(period, TaurusPollingTimer(period))
        self.polling_timers[period] = tmr
        tmr.addAttribute(attribute, self.isPollingEnabled())
        
    def removeAttributeFromPolling(self, attribute):
        """Deactivate the polling (client side) for the given attribute. If the
           polling of the attribute was not previously enabled, nothing happens.

           :param attribute: (str) attribute name.
        """
        p = None
        for period,timer in self.polling_timers.iteritems():
            if timer.containsAttribute(attribute):
                timer.removeAttribute(attribute)
                if timer.getAttributeCount() == 0:
                    p = period
                break
        if p:
            del self.polling_timers[period]
            

    

#===============================================================================
# Just for testing
#===============================================================================
def test1():
    f = EvaluationFactory()
    d = f.getDevice('eval://dev=foo')
    a = f.getAttribute('eval://2*bar?bar={sys/tg_test/1/short_scalar}')
    c = f.getConfiguration('eval://2*{sys/tg_test/1/short_scalar}?configuration=label')
    cp = a.getConfig()
    print "FACTORY:", f
    print "DEVICE:", d
    print "ATTRIBUTE", a, a.getSimpleName()
    print "CONFIGURATION", c, c.getSimpleName()
    print "CONFIGPROXY", cp, cp.getSimpleName()
    print
    print c.getValueObj()
    print c.getUnit()
    

def test2():
    a=taurus.Attribute('eval://[{sys/tg_test/1/short_scalar},{sys/tg_test/1/double_scalar}, {sys/tg_test/1/short_scalar}+{sys/tg_test/1/double_scalar}]')
    #a=taurus.Attribute('eval://2*{sys/tg_test/1/short_scalar}+rand()')  
    class Dummy:
        n=0
        def eventReceived(self, s,t,v):
            print self.n, v
            self.n += 1
    kk = Dummy()
    a.addListener(kk)
    while kk.n <= 2:
        time.sleep(1)
    a.removeListener(kk)
#    while kk.n <= 20:
#        time.sleep(1)        
    
def test3():
    import sys
    from taurus.qt.qtgui.application import TaurusApplication
    from taurus.qt.qtgui.panel import TaurusForm
    #from taurus.qt.qtgui.plot import TaurusTrend
    #from taurus.qt.qtgui.display import TaurusLabel
    app = TaurusApplication()
    
    w = TaurusForm()
#    w=TaurusTrend()
#    w=TaurusLabel()

    w.setModel(['eval://2*short_scalar?short_scalar={sys/tg_test/1/short_scalar}',
                'sys/tg_test/1/short_scalar', 'eval://a<100?a={sys/tg_test/1/short_scalar}', 
                'eval://10*rand()', 'eval://dev=taurus.core.evaluation.dev_example.FreeSpaceDevice;getFreeSpace("/")/1024/1024'])
#    w.setModel(['eval://2*short_scalar?short_scalar={sys/tg_test/1/short_scalar}'])
#    w.setModel(['sys/tg_test/1/short_scalar'])
#    w.setModel('eval://2*{sys/tg_test/1/short_scalar}?configuration=label')
#    w.setModel('eval://2*{sys/tg_test/1/short_scalar}')
#    w.setModel('sys/tg_test/1/short_scalar?configuration=label')
#    w.setModel('sys/tg_test/1/short_scalar')

#    a=w.getModelObj()
#    print a, a.read().value
    
#    a=w.getModelObj()
#    a.setUnit('asd')
#    c=a.getConfig()

    w.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    test3()
    
        
