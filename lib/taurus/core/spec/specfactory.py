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

'''
Spec module. See __init__.py for more detailed documentation
'''
__all__ = ['SpecFactory']

try:
    from .specmanager import SpecManager
    from SpecClient_gevent.SpecCounter import SpecCounter
    from SpecClient_gevent import SpecMotor
    from SpecClient_gevent.SpecCommand import SpecCommand
    from SpecClient_gevent.SpecVariable import SpecVariable
except ImportError: 
    #note that if SpecClient is not installed the factory will not be available
    logger= taurus.core.util.info('cannot import spec module.\
                                   Taurus will not support the "spec" scheme')
    raise

from taurus.core.util.enumeration import Enumeration
from taurus.core.util.log import Logger
from taurus.core.util.singleton import Singleton
from taurus.core.tauruspollingtimer import TaurusPollingTimer
from taurus.core.taurusfactory import TaurusFactory

from specattribute import SpecAttribute
from specdatabase import SpecDatabase
from specdevice import SpecDevice  
from specconfiguration import SpecConfiguration


from taurus.core.taurusexception import TaurusException

import functools
import gevent
import Queue
import threading
import time
import weakref


import atexit
@atexit.register
def goodbye():
    try:
        from taurus import Factory
        f = Factory('spec')
        f.onExit()
    except:    
        pass


class SpecFactory(Singleton, TaurusFactory, Logger):
    """
    A Singleton class that provides Spec related objects.
    """

    schemes = ("spec",)

    def __init__(self):
        """ Initialization. Nothing to be done here for now."""
        pass

    def init(self, *args, **kwargs):
        """Singleton instance initialization."""
        name = self.__class__.__name__
        self.call__init__(Logger, name)
        self.call__init__(TaurusFactory)
        self.dbs = weakref.WeakValueDictionary()
        self.devs = weakref.WeakValueDictionary()
        self.attrs = weakref.WeakValueDictionary() 
        self.configs = weakref.WeakValueDictionary()
        self.specObjs = weakref.WeakValueDictionary()

        self.scheme = 'spec'
        #Spec Manager
        self.specManager = SpecManager()
        self.validType = {'command':True, 
                          'counter':True, 
                          'motor':True, 
                          'variable':True}
        self.listeners = []
        self._objects_queue = Queue.Queue()

        self._stop_cond = False

        #Spec Listener
        self.sl = threading.Thread(target=self.listener, name='sl')

        #Spec Event Dispatcher
        self.sed = threading.Thread(target=self.getSpecEvents, name='sed')
        
        self.new_object_watcher = None
        self.events_queue = Queue.Queue()
        self._spec_queue = Queue.Queue()

        self.sed.setDaemon(True)
        self.sl.setDaemon(True)
        self.sed.start()
        self.sl.start() 


    def onExit(self):
        self._stop_cond = True 
        time.sleep(1)

#--------- Spec Event Dispatcher
    def getSpecEvents(self):
        '''
            Checking events_queue and when there is an event, 
            it propagate the event to the corresponding attribute 
        '''
        while True:
            if not self.events_queue.empty():
                name, value = self.events_queue.get()
                self.transmitSpecEvent(name,value)

    def transmitSpecEvent(self, fullname, value):
        attr = self.getAttribute(fullname)
        if attr is not None:  
            attr.onSpecEvent(fullname, value)
        else:
            self.debug('Attribute %s does not exist' %fullname)

#---------- Spec Listener
    def listener(self):
        try:
            self.new_object_watcher = gevent.get_hub().loop.async()
            self.new_object_watcher.start(self._deal_with_spec) 
        except:
            pass
        #e = threading.Event()
        while not self._stop_cond:
            #gevent.get_hub().wait(self.new_object_watcher) 
            #gevent.wait() #(timeout=100/1000.0)
            time.sleep(10/1000.0)
            #e.wait()


    def _deal_with_spec(self):
        if self._spec_queue.empty():
            return
        action, arg = self._spec_queue.get()
        if action == "register":
          gevent.spawn(self._register_var, arg)
        elif action == "read":
          gevent.spawn(self._read_spec_value, arg)
        elif action == "write":
          gevent.spawn(self._write_spec_value, arg[0], arg[1])
    
    def _read_spec_value(self, fullname):
        print fullname
        attr = fullname.rsplit('/',1)[1]
        obj_name = fullname.rsplit('/',1)[0]
        obj_type = fullname.split('/',2)[1]    
        obj = self.getSpecObj(obj_name)
        value = self.specManager.read_attribute(obj, obj_type, attr)
        self._objects_queue.put_nowait(value)

    def _write_spec_value(self, fullname, value):
        attr = fullname.rsplit('/',1)[1]
        obj_name = fullname.rsplit('/',1)[0]
        obj_type = fullname.split('/',2)[1]        
        obj = self.getSpecObj(obj_name)
        self.specManager.write_attribute(obj, obj_type, attr, value)
       
    def register(self, name):
        self.listeners.append(functools.partial(self.varUpdated, name)) 
        return self.listeners[-1]

    def register_var(self, fullname):
        if self.new_object_watcher is None:
            return None
        self._spec_queue.put_nowait(("register",fullname))
        self.new_object_watcher.send()
        return self._objects_queue.get()

    def _register_var(self,fullname):
        #name, session, timeout = self._new_object_args
        name = fullname.split('/')[2]
        session = fullname.split('/')[0]         
        self._objects_queue.put_nowait(self.createSpecObj(fullname))

    def varUpdated(self, fullname, value):
        #print fullname
        self.events_queue.put_nowait((fullname, value))

#--- SpecManager
    def createSpecObj(self, fullname):
        session = fullname.split('/')[0]
        obj_type = fullname.split('/')[1]
        dev_name = fullname.split('/')[2]
        #try:
        #    Spec(session)
        #except:
        #    raise TaurusException("Invalid Spec session, %s" % session)
        if self.validType.has_key(obj_type):
            # Name, Type, TimeOut
            try:
                if obj_type == 'motor':
                    event = fullname+'/position'
                    obj = SpecMotor.SpecMotor(dev_name, session, 
                            callbacks={"motorStateChanged":self.register(event), 
                            "motorPositionChanged":self.register(event)})
                elif obj_type == 'variable':
                    event = fullname+'/value'                                 
                    obj = SpecVariable(dev_name, session, 1000, 
                            callbacks={"update":self.register(event})
                elif obj_type == 'command':
                    obj = SpecCommand(dev_name, session, 1000, 
                            callbacks={"TODO":self.register(fullname)})
                elif obj_type == 'counter':
                    obj = SpecCounter(dev_name, session, 1000, 
                            callbacks={"TODO":self.register(fullname)}) 

                return obj
            except:
                msg = "The obj %s does not exist" % self.name + \
                         "in the session %s" % self.session
                self.debug(msg)
        else:
            raise TaurusException("Invalid Spec type, %s" % obj_type)

 #---
    def getSpecObj(self, fullname):
        #import pdb ; pdb.set_trace()
        #fullname = session/name i.e. lid00a:carlos/TEST
        
        obj = self.specObjs.get(fullname, None)
        #t = time.time()
        while obj is None:
            #TODO Add timeout?
            obj = self.register_var(fullname)
            #t= t+1 
        self.specObjs[fullname] = obj
        return obj

    def readSpecObj(self, fullname):
        self._spec_queue.put(("read", fullname))
        self.new_object_watcher.send()
        return self._objects_queue.get()

    def writeSpecObj(self, fullname, value):
        self._spec_queue.put(("write", (fullname, value)))
        self.new_object_watcher.send()
           
    def registerSpecObj(self, fullname):
        self.listeners.append(functools.partial(self.varUpdated, fullname)) 
        return self.listeners[-1]


#----------
       
    def findObjectClass(self, absolute_name):
        """
        Obtain the class object corresponding to the given name.
        """
        if SpecConfiguration.isValid(absolute_name):
            return SpecConfiguration
        elif SpecDatabase.isValid(absolute_name):
            return SpecDatabase
        elif SpecDevice.isValid(absolute_name):
            return SpecDevice
        elif SpecAttribute.isValid(absolute_name):
            return SpecAttribute
        else:
            self.debug("Not able to find Object class for %s" % absolute_name)
            self.traceback()
            return None

    def getAuthority(self, db_name):
        """Obtain the SpecDatabase object.
        
        :param db_name: (str) this is ignored because only one dummy database 
                        is supported
                           
        :return: (SpecDatabase)
        """
        validator = SpecDatabase.getNameValidator()

        if not validator.isValid(db_name):
            raise TaurusException("Invalid Spec database name %s" % db_name)

        params = validator.getParams(db_name)
        fullname = params.get('session')
        db = self.dbs.get(fullname, None)
        if db is None: 
            db = SpecDatabase(fullname)
            self.dbs[fullname] = db
        return db
    


    def getDevice(self, dev_name):
        """Obtain the SpecDevice object.
        
        :param dev_name: (str) this is ignored because only one dummy 
                         device is supported
                           
        :return: (SpecDevice)
        
        .. todo:: Spec records may be implemented as taurus devices...
        """
        validator = SpecDevice.getNameValidator()

        if not validator.isValid(dev_name):
            raise TaurusException("Invalid Spec device name %s" % dev_name)

        params = validator.getParams(dev_name)
        session = params.get('session')
        fullname = session + '/' + params.get('devicename')     
        d = self.devs.get(fullname, None) 
        if d is None: 
            db = self.getAuthority(session)
            d = SpecDevice(fullname, parent=db)
            self.devs[fullname] = d
        return d
    
    def getAttribute(self, attr_name):
        """Obtain the object corresponding to the given attribute name. If the 
        corresponding attribute already exists, the existing instance is
        returned. Otherwise a new instance is stored and returned. The 
        device associated to this attribute will also be created if necessary.
           
        :param attr_name: (str) the attribute name string. See
                          :mod:`taurus.core.spec` for valid attribute names
        
        :return: (SpecAttribute)
         
        @throws TaurusException if the given name is invalid.
        """
        validator = SpecAttribute.getNameValidator()

        if not validator.isValid(dev_name):
            raise TaurusException("Invalid Spec device name %s" % attr_name)

        params = validator.getParams(attr_name)
        session = params.get('session')
        devicename = params.get('devicename')
        attributename = params.get('attributename')
        fullname = session+'/'+devicename+'/'+attributename
        a = self.attrs.get(fullname, None)
        if a is None: 
            dev = self.getDevice(session+'/'+devicename)
            a = SpecAttribute(fullname, parent=dev)
            self.attrs[fullname] = a
        return a

    def getConfiguration(self, param):
        """getConfiguration(param) -> taurus.core.TaurusConfiguration

        Obtain the object corresponding to the given attribute or full name.
        If the corresponding configuration already exists, the existing instance
        is returned. Otherwise a new instance is stored and returned.

        @param[in] param taurus.core.TaurusAttribute object or full 
                   configuration name
           
        @return a taurus.core.TaurusAttribute object
        @throws TaurusException if the given name is invalid.
        """
        if isinstance(param, str):
            return self._getConfigurationFromName(param)
        return self._getConfigurationFromAttribute(param)

    def _getConfigurationFromName(self, cfg_name):
        cfg = self.configs.get(cfg_name, None) #first try with the given name
        if cfg is None: #if not, try with the full name
            validator = SpecConfiguration.getNameValidator()
            names = validator.getNames(cfg_name)
            if names is None:
                raise TaurusException(("Invalid evaluation configuration" +
                                       " name %s" % cfg_name))
            fullname = names[0]
            attr = self.getAttribute(fullname.split('?')[0])
            cfg = SpecConfiguration(fullname, parent=attr)
            self.configs[cfg_name] = cfg
        return cfg
        
    def _getConfigurationFromAttribute(self, attr):
        #TODO
        cfg = attr.getConfig()
        cfg_name = attr.getFullName() + "?configuration"
        self.configs[cfg_name] = cfg
        return cfg

    def _storeDb(self, db):
        pass

    

    def _storeDev(self, dev):
        pass
    
    def _storeAttr(self, attr):
        pass
        
    def _storeConfig(self, fullname, config):
        pass
        
    def addAttributeToPolling(self, attribute, period, unsubscribe_evts = False):
        """Activates the polling (client side) for the given attribute with the
           given period (seconds).

           :param attribute: (taurus.core.spec.SpecAttribute) attribute name.
           :param period: (float) polling period (in seconds)
           :param unsubscribe_evts: (bool) whether or not to unsubscribe 
                                    from events
        """
        tmr = self.polling_timers.get(period,TaurusPollingTimer(period))
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

    #Centralize checking validations (using Taurus)
    def getDatabaseNameValidator(self):
        """Return SpecDatabaseNameValidator"""
        import specvalidator
        return specvalidator.SpecDatabaseNameValidator()
        
    def getDeviceNameValidator(self):
        """Return SpecDeviceNameValidator"""
        import specvalidator
        return specvalidator.SpecDeviceNameValidator()

    def getAttributeNameValidator(self):
        """Return SpecAttributeNameValidator"""
        import specvalidator
        return specvalidator.SpecAttributeNameValidator()

    def getConfigurationNameValidator(self): # TODO: This is broken now that getConfigurationNameValidator does not exist
        """Return SpecConfigurationNameValidator"""
        import specvalidator
        return specvalidator.SpecConfigurationNameValidator()
            
#===============================================================================
# Just for testing
#===============================================================================
def assosiative_array():
    #from specdevice import SpecDevice
    f = SpecFactory()
    #d = f.getDevice('lid00a:carlos/variable/asso_arry')
    time.sleep(2)
    value = f.readSpecObj('lid00a:carlos/variable/TEST/value')
 
    print 'value = ', value

def test0():
    f = SpecFactory()
    db = f.getAuthority("spec://lid00a:carlos")
    d = f.getDevice('spec://lid00a:carlos/motor/rot')
    a = f.getAttribute('spec://lid00a:carlos/motor/rot/velocity')
    print "FACTORY:", f
    print "DB:", db, db.getSimpleName(), db.getNormalName(), db.getFullName()
    print "DEV:", d, d.getSimpleName(), d.getNormalName(), d.getFullName()
    print "ATTR:", a, a.getSimpleName(), a.getNormalName(), a.getFullName()
    
def test1():
    f = SpecFactory()
    a = f.getAttribute('spec://lid00a:carlos/variable/TEST/value')
    #value  = a.read()
    #print 'Value = ', value.value
    #if isinstance(value, taurus.core.TaurusAttrValue):
    #    value.value = value.value+2   
    ##a.write(value.value+2)
    #a.write(value)
    #value  = a.read()
    #print 'Value(+2) = ', value.value 
    time.sleep(100)  

def test2():
    a=taurus.Attribute('spec://lid00a:carlos/variable/TEST/value')
    class Dummy:
        n=0
        def eventReceived(self, s,t,v):
            print "DUMMY:",self.n, v.value
            self.n += 1
    kk = Dummy()
    a.addListener(kk)
    while kk.n <= 2:
        time.sleep(1)
    a.removeListener(kk)
    while kk.n <= 20:
        time.sleep(1) 


    
def test3():
    import sys
    from taurus.qt.qtgui.application import TaurusApplication
    from taurus.qt.qtgui.panel import TaurusForm
    #from taurus.qt.qtgui.plot import TaurusTrend
    from taurus.qt.qtgui.display import TaurusLabel
    from taurus.core.spec.specfactory import SpecFactory

    from taurus.qt import Qt
    from taurus.qt.QtCore import QObject 
    from taurus.qt import QtCore
    
    import taurus
    f = taurus.Factory('spec')
    
    app = TaurusApplication()

    f = SpecFactory()
    w = TaurusLabel()
    w.setModel('spec://lid00a:carlos/variable/TEST/value')

    a=w.getModelObj()
    w.show()
    r=app.exec_()
    f._stop_cond = True
    print ' stop thread set to true', f._stop_cond
    time.sleep(1)
    sys.exit(r)



def test5():
    from taurus.core.spec.specattribute import SpecAttribute   
    from taurus.core.spec.specfactory import SpecFactory    
    f = SpecFactory()
    db1 = f.getAuthority('spec://lid00a:carlos')
    db2 = f.getAuthority('spec://lid00a:carlos')

    d1 = f.getDevice('spec://lid00a:carlos/variable/TEST')
    d2 = f.getDevice('spec://lid00a:carlos/variable/TEST2')

    a1 = f.getAttribute('spec://lid00a:carlos/variable/TEST/value')
    a2 = f.getAttribute('lid00a:carlos/variable/TEST2/value')
    a3 = f.getAttribute('spec://lid00a:carlos/variable/TEST2/value')
    time.sleep(100)  


def test6():
    f = SpecFactory()

    v = f.getSpecObj('lid00a:carlos/variable/TEST')

    time.sleep(20)


def test_Var():
    from taurus.core.spec.specfactory import SpecFactory    
    f = SpecFactory()
    test = f.getDevice('spec://lid00a:carlos/variable/TEST')
    print 'TestVar TEST = %s',  test.getValueObj().value

    toto = f.getDevice('spec://lid00a:carlos/variable/toto')
    

if __name__ == "__main__":
    #test_attr()
    test3()
    #assosiative_array()
    #test_Var()
    #test5()
