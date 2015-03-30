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
__all__ = ["SpecAttribute"]

import taurus.core
from taurus.core import SubscriptionState, TaurusEventType
from specvalidator import SpecAttributeNameValidator
from specconfiguration import SpecConfiguration

from taurus.core.taurusattribute import TaurusAttribute
from taurus.core.taurusbasetypes import TaurusAttrValue, TaurusEventType,\
         AttrQuality, TaurusTimeVal
from taurus import Factory

import numpy, time, numbers


class SpecAttribute(TaurusAttribute):
    '''
    A :class:`TaurusAttribute` that gives access to an Spec Process Variable.
    
    .. seealso:: :mod:`taurus.core.spec` 
    
    .. warning:: In most cases this class should not be instantiated directly.
                 Instead it should be done via the :meth:`SpecFactory.getAttribute`
    '''

    # helper class property that stores a reference to the corresponding factory
    _factory = None
    _scheme = 'spec'

    def __init__(self, name, parent, storeCallback = None):
        self.call__init__(TaurusAttribute, name, parent, storeCallback=storeCallback)
        self.deviceName = self.getNormalName().split('/')[1]
        self.attrName = self.getSimpleName() 
        try:
            #Spec Obj
            self.obj = parent.getHWObj()
            #Spec Event
            self.valueCache = None #self.obj.read_attribute(self.attrName)      
        except:
            self.warning('Error, Try to create attribute without parent (=None)')
            raise

        self._value = TaurusAttrValue()
        self._value.value = None
        self._value.w_value = None
        #self._value.config.writable = True                             
#        self._references = [] 
#        #self._validator= self.getNameValidator()
#        self._transformation = None
        # reference to the configuration object
        self.__attr_config = None   #taurus.core.TaurusConfiguration()
        self.__attr_timestamp = 0
        #self.isanumber = False

      
    def onSpecEvent(self, name, value):
        #import pdb; pdb.set_trace()
        #self.warning('  * onSpecEvent %s was updated to %s' %(name,value))       
#        if self.valueCache == value: # or self.deviceName != str:
#            return
        self.valueCache = value

        self._value = self.decode_spec(value)
        #
        #self.__subscription_event.set()
        self.fireEvent(TaurusEventType.Change, self._value)

    def __getattr__(self,name):
        return getattr(self._getRealConfig(), name)
    
    def _getRealConfig(self):
        """ Returns the current configuration of the attribute."""
        if self.__attr_config is None:
            cfg_name = "%s?configuration" % self.getFullName()
            self.__attr_config = SpecConfiguration(cfg_name, self)
        return self.__attr_config
           
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # Necessary to overwrite from TaurusAttribute
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    def isNumeric(self):
        return True
        #return isinstance(self._value.value , numbers.Number)
        #return self.isanumber
        
    def isBoolean(self):
        return isinstance(self._value.value, bool)
    
    def isState(self):
        return False

    def getDisplayValue(self,cache=True):
        return str(self.read(cache=cache).value)

    def encode(self, attr):
        """
            Encode the given attr, it could be TaurusAttrValue 
                or a simple numeric value  
        """
        if isinstance(attr, TaurusAttrValue):
            attr =  attr.value

        #if isinstance(attr , numbers.Number):
        #if self.isNumeric():
        #    attr = float(attr)
        #else:
        attr = str(attr)
        return attr 

    def decode(self, attr):
        #if isinstance(obj, TaurusAttrValue):
        return self.decode_spec(attr)

    def decode_spec(self, attr):
        if isinstance(attr, TaurusAttrValue):
            attr = attr.value
        #print type(attr)
        #TODO check  
        #if self.isNumeric():
        #if isinstance(attr , numbers.Number):
        #    print 'number'
        #    attr = float(attr)
        #else:
        #print 'str'
        attr = str(attr) 

        self._value.value = attr
        #cp name
        self._value.name = self.attrName
        
        #if attr.write_access:
        self._value.w_value = attr
        #if attr.timestamp is None: 
        self._value.time = TaurusTimeVal.now()
        #else:
        #    attr_value.time = TaurusTimeVal.fromtimestamp(attr.timestamp)
        #if attr.severity > 0:
        #    attr_value.quality = AttrQuality.ATTR_ALARM
        #else:
        self._value.quality = AttrQuality.ATTR_VALID
        self._value.config.data_format = len(numpy.shape(self._value.value))
        return self._value

    def write(self, value, with_read=True):
        f =  self.factory() 
        if type(value)== str:
            if value.find('$')>=0:
                value = value[1:]               
                newfullname = "%s/%s/value" %(self.getFullName().rsplit("/",2)[0],value)
                attr = f.getAttribute(newfullname)
                value = attr.read()
        value = self.encode(value)
        #Dont fire my write_event #TODO ask for this?
        self.valueCache = value                                                 

        f.writeSpecObj(self.getFullName(), value)

#        if with_read:
#            value = self.obj.write_read_attribute(name, value)
#            self._value = self.decode(value)
#            self.poll()
#            return self._value
#        else:
#            #self.obj.write_attribute(name, value)
#            value = self.obj.setValue(value)


    def read(self, cache=True):
        '''returns the value of the attribute.
        
        :param cache: (bool) If True (default), the last calculated value will
                      be returned. If False, the referenced values will be re-
                      read and the transformation string will be re-evaluated 
                      
        :return: attribute value
        '''  

#        if cache:
#            #TODO check refresh and add timer
#            dt = (time.time() - self.__attr_timestamp)*1000
#            #if dt < self.getPollingPeriod():
#            if not self.valueCache is None: # and dt < self.getPollingPeriod():
#                return self.decode(self.valueCache)
#            else:
#                return self.read(cache=False)  


##        value = self.obj.read_attribute(self.attrName)
        self.__attr_timestamp = time.time()
        #value = self.obj.getValue()
        f =  self.factory()

        #value =f.getSpecObj(self.getNormalName())
        ##import pdb; pdb.set_trace()
        #value = self.obj.getValue()
        #import pdb;pdb.set_trace()
        value = f.readSpecObj(self.getFullName())
        #self.isanumber =  isinstance(value , numbers.Number)
        #self.warning(' ---- READ = %s  %s' %(value, type(value)))
        self.valueCache = value
        #return value
        #Decode as TaurusAttribute
        self._value = self.decode(value)
        return self._value
 
    def poll(self):

        v = self.read(cache=False)  
        #self.__subscription_event.set()
        f = self.factory()
        f.__subscription_event.set()
        self.fireEvent(TaurusEventType.Periodic, v)

    def _subscribeEvents(self): 
        pass
        
    def _unsubscribeEvents(self):
        pass

    def isUsingEvents(self):
        return True #TODO
        #return bool(len(self._references)) 

#===============================================================================
# Just for testing
#===============================================================================
def test():
    import taurus
    from taurus.core.spec.specattribute import SpecAttribute
    from taurus.core.spec.specdevice import SpecDevice
    d = SpecDevice('spec://lid00a:carlos/motor/rot')
    a = SpecAttribute('spec://lid00a:carlos/motor/rot/position', d)
    print a.getFullName()
    dev = a.getParentObj()
    obj = dev.getHWObj()
    attrName = a.attrName
    print dev.read_attribute(attrName)

def test2():
    import taurus, time
    from taurus.core.spec.specfactory import SpecFactory
    f = SpecFactory()
    d = f.getDevice('spec://lid00a:carlos/motor/rot')
    a = f.getAttribute('spec://lid00a:carlos/motor/rot/position')
    while True:
        value = a.read()#["value"]  
        print 'Value = ', value 
        time.sleep(1)
    #a.write(2)

def test4():
    import taurus
    from taurus.core.spec.specdevice import SpecDevice
    from taurus.core.spec.specattribute import SpecAttribute   
    d = SpecDevice('spec://lid00a:carlos/variable/TEST')
    a = SpecAttribute('spec://lid00a:carlos/variable/TEST/value', d) 
    data = a.read()
    print 'Before write = ',data 
    if isinstance(data, TaurusAttrValue):
        data.value = data.value+2   
    else:
        data = data + 2
    a.write(data, with_read=False)
    print 'AFTER write = ',a.read()   




def test5():
    import taurus
    from taurus.core.spec.specdevice import SpecDevice
    from taurus.core.spec.specattribute import SpecAttribute   
    d = SpecDevice('spec://lid00a:carlos/variable/TEST')
    a = SpecAttribute('spec://lid00a:carlos/variable/TEST/value', d)
    value = 10 
    value =  a.decode(value)
    print 'DECODE ', value
    value =  a.encode(value)
    print 'ENCODE ', value

    #where $TEST2 is a variable
    #a.write('$TEST2')


def test6():
    from taurus.core.spec.specfactory import SpecFactory
    #import pdb; pdb.set_trace()
    f = SpecFactory()
    #d = f.getDevice('spec://lid00a:carlos/variable/toto')
    #import pdb; pdb.set_trace()
    a = f.getAttribute('spec://lid00a:carlos/variable/www/uno/uno')
    out = a.read()
    print '\n\n*** Result = ', out.value, 'type = ', type(out.value) 

    return 
    value =  a.encode(out)
    print 'ENCODE ', value
    value =  a.decode(out)
    print 'DECODE ', value

    a = f.getAttribute('spec://lid00a:carlos/variable/TEST/value')
    value = a.read()
    print 'TEST= ', value 
    a.write(value*2)
    value = a.read()
    print 'TEST*2= ', value  


def test7():
    from taurus.qt.qtgui.panel import TaurusForm
    import sys
    from taurus.qt import Qt

    model = 'spec://lid00a:carlos/variable/TEST/value'
    app = Qt.QApplication(sys.argv)
    dialog = TaurusForm()
    dialog.setModel(model)
    dialog.show()
    
    sys.exit(app.exec_())    

if __name__ == "__main__":
    #test()
    #test2()
    #test3()
    test7()
    #test4()
