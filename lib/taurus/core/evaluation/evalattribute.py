#!/usr/bin/env python
#############################################################################
##
## This file is part of Taurus
## 
## http://taurus-scada.org
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

__all__ = ['EvaluationAttribute']

import numpy, re

from evalconfiguration import EvaluationConfiguration
from taurus import Factory
from taurus.core.taurusattribute import TaurusAttribute
from taurus.core.taurusbasetypes import SubscriptionState, TaurusEventType, \
    TaurusAttrValue, TaurusTimeVal, AttrQuality, DataType
from taurus.core.taurusexception import TaurusException
from taurus.core.taurushelper import Attribute, Manager
from taurus.core import TaurusConfigValue, DataFormat

from taurus.core.evaluation.evalvalidator import QUOTED_TEXT_RE, PY_VAR_RE

class EvaluationAttribute(TaurusAttribute):
    '''
    A :class:`TaurusAttribute` that can be used to perform mathematical
    operations involving other arbitrary Taurus attributes. The mathematical
    operation is described in the attribute name itself. An Evaluation Attribute
    will keep references to any other attributes being referenced and it will
    update its own value whenever any of the referenced attributes change.
    
    .. seealso:: :mod:`taurus.core.evaluation` 
    
    .. warning:: In most cases this class should not be instantiated directly.
                 Instead it should be done via the 
                    :meth:`EvaluationFactory.getAttribute`
    '''
    # helper class property that stores a reference to the corresponding factory
    _factory = None
    _scheme = 'eval'

    def __init__(self, name, parent, storeCallback = None):
        self.call__init__(TaurusAttribute, name, parent,
                            storeCallback=storeCallback)
        
        self._value = TaurusAttrValue()

        #Evaluation Attributes are always read-only (at least for now)
        self._value.config.writable = False
        self._value.config.label = self.getSimpleName()
        self._value.config.name = self._value.config.label
        self._references = []
        self._validator = self.getNameValidator()
        self._transformation = None
        # reference to the configuration object
        self.__attr_config = None
        self.__subscription_state = SubscriptionState.Unsubscribed

        #This should never be None because the init already ran the validator
        trstring = self._validator.getExpandedExpr(str(name))
       
        trstring, ok = self.preProcessTransformation(trstring)
        
        if ok:
            self._transformation = trstring
            self.applyTransformation()

    def __getattr__(self,name):
        return getattr(self._getRealConfig(), name)
    
    def _getRealConfig(self):
        """ Returns the current configuration of the attribute."""
        if self.__attr_config is None:
            cfg_name = "%s#" % self.getFullName()
            self.__attr_config = EvaluationConfiguration(cfg_name, self)
        return self.__attr_config
    
    @staticmethod
    def getId(obj, idFormat=r'_V%i_'):
        '''returns an id string for the given object which has the following 
           two properties:
            - It is unique for this object during all its life
            - It is a string that can be used as a variable or method name
        
        :param obj: (object) the python object whose id is requested 
        :param idFormat: (str) a format string containing a "`%i`" which,
                         when expanded must be a valid variable name 
                         (i.e. it must match
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
        
        #get symbols
        evaluator = self.getParentObj()  

        #Find references in the string, create references if needed, 
        #connect to them and substitute the references by their id
        refs = self._validator.getRefs(trstring)
        for r in refs:
            symbol = self.__ref2Id(r)
            trstring = trstring.replace('{%s}' %r, symbol)

        #validate the expression (look for missing symbols) 
        safesymbols = evaluator.getSafe().keys()        
        #remove literal text strings from the validation
        trimmedstring = re.sub(QUOTED_TEXT_RE, '', trstring)
        for s in set(re.findall(PY_VAR_RE, trimmedstring)):
            if s not in safesymbols:
                self.warning('Missing symbol "%s"'%s)
                return trstring, False

        #If all went ok, enable/disable polling based on whether 
        #there are references or not
        wantpolling = not self.isUsingEvents()
        haspolling = self.isPollingEnabled()
        if wantpolling:
            self._activatePolling()
        elif haspolling and not wantpolling:
            self.disablePolling()

        return trstring,True
              
    def __ref2Id(self, ref):
        """
        Returns the id of an
        existing taurus attribute corresponding to the match. 
        The attribute is created if it didn't previously exist.

        :param ref: (str)  string corresponding to a reference. e.g. eval:1
        """
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
        refobj = Attribute(ref)
        if refobj not in self._references:
            evaluator = self.getParentObj()
            v = refobj.read().rvalue
            # add its rvalue to the evaluator symbols
            evaluator.addSafe({self.getId(refobj) : v})
            #add the object to the reference list 
            self._references.append(refobj)             
        return refobj        
    
    def eventReceived(self, evt_src, evt_type, evt_value):
        try:
            v = evt_value.rvalue
        except AttributeError:
            self.trace('Ignoring event from %s'%repr(evt_src))
            return
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
            self._value.rvalue = evaluator.eval(self._transformation)
            self._value.time = TaurusTimeVal.now()
            self._value.quality = AttrQuality.ATTR_VALID
            value_dimension = len(numpy.shape(self._value.rvalue))            
            value_dformat = DataFormat(value_dimension)
            # TODO: this logic is related to the configuration class
            # in the future we could move it there
            self._value.config.data_format = value_dformat
            self._value.config.type = self._encodeType(self._value.rvalue,
                                                       value_dformat)
        except Exception, e:
            self._value.quality = AttrQuality.ATTR_INVALID
            msg = " the function '%s' could not be evaluated. Reason: %s" \
                    %( self._transformation, repr(e))
            self.warning(msg)
            #self.traceback(taurus.Warning)

    def _encodeType(self, value, dformat):
        ''' Encode the value type into Taurus data type. In case of non-zero 
        dimension attributes e.g. 1D, 2D the type corresponds to the type of the
        first element.

        :param value: (obj)
        :param dformat: (taurus.DataFormat)

        :return: (taurus.DataType)
        '''
        # TODO: this logic is related to the configuration class
        # in the future we could move it there
        
        try: # handle Quantities
            value = value.magnitude
        except AttributeError:
            pass
        try: # handle numpy arrays
            value = value.item(0)
        except AttributeError: # for bool, bytes, str, seq<str>...
            if dformat is DataFormat._1D:
                value = value[0]
            elif dformat is DataFormat._2D:
                value = value[0][0]
        dataType = type(value)
        return DataType.from_python_type(dataType)

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # Necessary to overwrite from TaurusAttribute
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    def isNumeric(self):
        return True
        
    def isBoolean(self):
        return isinstance(self._value.rvalue, bool)
    
    def isState(self):
        return False

    def getDisplayValue(self,cache=True):
        return str(self.read(cache=cache).rvalue)

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
                symbols[self.getId(ref)] = ref.read(cache=False).rvalue
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
        #if this attributes depends from others, then we consider it uses events
        return bool(len(self._references)) 
        
#------------------------------------------------------------------------------ 
    def __fireRegisterEvent(self, listener):
        #fire a first change event
        try:
            v = self.read()
            self.fireEvent(TaurusEventType.Change, v, listener)
        except:
            self.fireEvent(TaurusEventType.Error, None, listener)
    
    def addListener(self, listener):
        """ Add a TaurusListener object in the listeners list.
            If it is the first listener, it triggers the subscription to
            the referenced attributes.
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
        if len(self._listeners) > 1 and \
           (initial_subscription_state == SubscriptionState.Subscribed or \
           self.isPollingActive()):
            Manager().addJob(self.__fireRegisterEvent, None, (listener,))
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
