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
__all__ = ["SpecManager"]

"""This module contains the spec manager classes"""
import time

from taurus.core.taurusexception import TaurusException
#Spec included
from SpecClient_gevent.SpecConnectionsManager import SpecConnectionsManager
from SpecClient_gevent.Spec import Spec
from SpecClient_gevent.SpecCounter import SpecCounter
from SpecClient_gevent import SpecMotor
from SpecClient_gevent.SpecCommand import SpecCommand
from SpecClient_gevent.SpecVariable import SpecVariable
from SpecClient_gevent import SpecConnection, SpecChannel
from SpecClient_gevent import SpecEventsDispatcher

#: sardana element state enumeration
from taurus.core.util import Enumeration
from taurus.core.taurusexception import TaurusException

InvalidAlias = "nada"

#: sardana element state enumeration
from taurus.core.util import Enumeration
State = Enumeration("State", ( \
                            "On",
                            "Off",
                            "Close",
                            "Open",
                            "Insert",
                            "Extract",
                            "Moving",
                            "Standby",
                            "Fault",
                            "Init",
                            "Running",
                            "Alarm",
                            "Disable",
                            "Unknown",
                            "Invalid") )

#-------------------------------------------------------------------------------
class SpecManager():
    '''
        This class provide a interface for interactuar with the "specdevice" 
        defined in the session
        
        in fulldevNameValidator     = session/var_type/var_name
    '''  

    def getState(self, obj, obj_type):
        '''
        Used sardana state codification
        '''
        if obj_type  == 'motor':
            s = obj.getState()
            if (SpecMotor.NOTINITIALIZED == s):     #0
                return State.Disable
            elif (SpecMotor.UNUSABLE == s):         #1
                return  State.Fault
            elif (SpecMotor.READY == s):            #2
                return  State.On
            elif (SpecMotor.MOVESTARTED == s):      #3
                return State.Moving
            elif (SpecMotor.MOVING == s):           #4
                return State.Moving
            elif (SpecMotor.ONLIMIT == s):          #5
                return  State.Alarm
        else:
            return  State.Moving ##On

    def get_attribute_list(self):
        if obj_type  == 'motor':
            return ['acceleration', 'base_rate', 'slew_rate', 'step_size', 'velocity', 'offset', 'position', 'limit_switches', 'power', 'state', 'status']
        elif obj_type  == 'variable':
            return ['value']

    def read_attribute(self, obj, obj_type, attr): 
        if attr == 'state':
            return self.getState(obj, obj_type)
        #try:         
        if obj_type  == 'motor':
            if attr == 'position':
                return obj.getPosition()
            return obj.getParameter(attr)
        elif obj_type  == 'variable':
            try:
                value = obj.getValue()
                if attr=='/' or attr=='value': 
                    return value
                else: 
                    s = attr.split('/')
                    if s.__len__()==1:
                        return value[s[0]]
                    else:
                        return value[s[0]][s[1]]  
            except:
                raise TaurusException("Invalid attribute")

        elif obj_type == 'command':
            #Execute the command
            obj()
        elif obj_type  == 'counter':
            pass
        return 0
        #except:
        #    self.warning('Error, invalid parameter, %s' %attr)

    def write_attribute(self, obj, obj_type, attr, value):
    #try:
        if obj_type  == 'motor':
            if attr == 'position':
                return obj.move(float(value))
            obj.setParameter(attr, value)
        elif obj_type  == 'variable':
            #TODO   
            if attr=='/' or attr=='value': 
                obj.setValue(value)
            else: 
                array = obj.getValue()  
                s = attr.split('/')
                if s.__len__()==1:
                    try:
                        array[s[0]][None] = value
                    except:
                        array[s[0]] = value                    
                else:
                    array[s[0]][s[1]] = value
                obj.setValue(array)
           
        elif obj_type  == 'command':
            #set a new command
            obj.setCommand(value)
        elif obj_type  == 'counter':
            pass



    def write_read_attribute(self, obj, obj_type, attr, value):
        self.write_attribute(obj, obj_type, attr, value)
        return self.read_attribute(obj, obj_type, attr)


#===============================================================================
# Just for testing
#===============================================================================
def test_variable():
    from specdevice import SpecDevice
    mng = SpecManager()

    #READ
    #Simple Variable
    obj1 = SpecVariable('TEST', 'lid00a:carlos', 1000)
    value1 = mng.read_attribute(obj1, 'variable', 'value')
    print '*** TEST value  = ', value1  
    #assosiative_array Variable
    obj2 = SpecVariable('toto', 'lid00a:carlos', 1000)
    value2 = mng.read_attribute(obj2, 'variable', "tata/tata")
    print '*** toto[tata][tata] value  = ', value2  


    #WRITE      
    #Simple Variable
    obj1 = SpecVariable('TEST', 'lid00a:carlos', 1000)
    mng.write_attribute(obj1, 'variable', 'value', value1*2) 
    #assosiative_array Variable
    obj2 = SpecVariable('toto', 'lid00a:carlos', 1000)
    mng.write_attribute(obj2, 'variable', "tata/tata", value2*2)


    #READ
    #Simple Variable
    obj1 = SpecVariable('TEST', 'lid00a:carlos', 1000)
    value = mng.read_attribute(obj1, 'variable', 'value')
    print '*** TEST valuex2  = ', value  
    #assosiative_array Variable
    obj2 = SpecVariable('toto', 'lid00a:carlos', 1000)
    value = mng.read_attribute(obj2, 'variable', "tata/tata")
    print '*** toto[tata][tata] valuex2  = ', value  


def test_move():
    print ' --- TEST move ---'
    from taurus.core.spec.specmanager import SpecDeviceManager
    from SpecClient_gevent import SpecMotor
    mng = SpecDeviceManager('lid00a:carlos')

    d = mng.getDevice('motor/rot')
    #obj = SpecMotor.SpecMotorA('rot', 'lid00a:carlos')
    obj = d.getObj()
    pos = obj.getPosition()
    print 'Position (start) = %s' %(str(pos)) 
    obj.moveRelative(2)
    #time.sleep(1)
    pos = obj.getPosition()
    print 'Position (after move) = %s' %(str(pos)) 
    obj.moveRelative(-2)
    #time.sleep(1)
    pos = obj.getPosition()    
    print 'Position (opposite move) = %s' %(str(pos)) 

 

def test_r_w():
    print ' --- TEST read write ---'
    from taurus.core.spec.specmanager import SpecDeviceManager
    from SpecClient_gevent import SpecMotor
    mng = SpecDeviceManager('lid00a:carlos')
    d = mng.getDevice('motor/rot')
    pos = d.read_attribute('position')
    print 'read position = %s' %(str(pos)) 

    pos = d.write_read_attribute('position', 1)
    print 'W/R position = 1 = %s' %(str(pos)) 
    
    pos = d.write_read_attribute('position', 0)
    print 'W/R position = 0 = %s' %(str(pos)) 
    
    #error with motors
    pos = d.write_read_attribute('position', 0) 

    d = mng.getDevice('variable/TEST')
    value = d.read_attribute('value')
    print 'read TEST = %s' %(str(value))
    value = d.write_read_attribute('value', value+2)     
    print 'write/read TEST(+2) = %s' %(str(value))
    value = d.write_read_attribute('value', value-2)     
    print 'write/read TEST(-2) = %s' %(str(value))

def test_state():
    print ' --- TEST STATE ---'
    from taurus.core.spec.specmanager import SpecDeviceManager
    from SpecClient_gevent import SpecMotor
    mng = SpecDeviceManager('lid00a:carlos')
    d = mng.getDevice('motor/rot')
    print d.getState()



#    from taurus.qt import Qt

def printUpdate(str, int):
    taurus.core.util.warning('SIGNAL %s was updated to %s' %(str,int)) 

def test_listener():
    mng = SpecDeviceManager('lid00a:carlos')
    
    d = mng.getDevice('variable/TEST')
    d2 = mng.getDevice('variable/TEST2')
    #d.getListener()
    v=d.getObj()
    v2=d2.getObj()
###TODO    
    Qt.QObject.connect(d.getListener(), Qt.SIGNAL('UpdateObj(str, int)'), printUpdate)
    #del(d2)
    time.sleep(100)

if __name__ == "__main__":
    test_variable()
    #test_listener()
    #read_demo()
    #test_r_w2()
    #test_state()
    #test_r_w()
    #test_move()
