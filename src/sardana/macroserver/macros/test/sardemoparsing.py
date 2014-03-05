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

from taurus.core.taurushelper import Device 
# TODO taurus.core.tango.sardana will be moved by SEP10
from taurus.core.tango.sardana.macroserver import registerExtensions
from taurus.core.util.singleton import Singleton
from sardana import sardanacustomsettings

class SarDemoParsing(Singleton):
    '''Class to parse _SAR_DEMO environment variable with cross checking with
       the MacroServer (given by 'UNITTEST_DOOR_NAME') 
    '''
    def __init__(self, door_name=None):
        if door_name is None:
            door_name = getattr(sardanacustomsettings,'UNITTEST_DOOR_NAME')
        registerExtensions()
        try:
            self.door = Device(door_name)
            self.ms = self.door.macro_server
        except ValueError:
            raise 'The  door %s does not exist' %(door_name)

        self.controllers = []        
        self.cts = []
        self.motors = []
        self.pseudos = []
        self.zerods = []
        self.oneds = []
        self.twods = []

        try:
            self.env = self.ms.getEnvironment()['_SAR_DEMO']['elements']
            self.envCtrl = self.ms.getEnvironment()['_SAR_DEMO']['controllers']
        except KeyError:
            raise 'sar_demo has not been executed for this door %' %(door_name) 

    def getElementOfType(self, elem_type):
        '''Return the name of element(s) of given elem type  
        '''
        return self.ms.getElementNamesOfType(elem_type)

    def getElements(self, elem_type=None):
        '''Return the name of sardemo element(s) of given elem type  
        '''
        elems = []
        if not elem_type:
            elem_type = 'all'
        if elem_type.lower() == 'moveable' or elem_type.lower == 'all':
            elems +=  self.getMoveables()
        if elem_type.lower() == 'motor' or elem_type.lower == 'all':
            elems +=  self.getMotors()
        if elem_type.lower() == 'pseudomotor' or elem_type.lower == 'all':
            elems +=  self.getPseudoMotors()
        if elem_type.lower() == 'controller' or elem_type.lower == 'all':
            elems +=  self.getControllers()
        if elem_type.lower() == 'ctexpchannel' or elem_type.lower == 'all':
            elems +=  self.getCTs()
        if elem_type.lower() == 'zerodexpchannel' or elem_type.lower == 'all':
            elems +=  self.getZerods()
        if elem_type.lower() == 'onedexpchannel' or elem_type.lower == 'all':
            elems +=  self.getOneds()
        if elem_type.lower() == 'twodexpchannel' or elem_type.lower == 'all':
            elems +=  self.getTwods()
        return elems
     
        
    def getMoveables(self):
        '''Return the name of moveable(s) defined by SarDemo 
        '''
        return self.getMotors() + self.getPseudoMotors()
        
    def getControllers(self):
        '''Return the name of controllers(s) defined by SarDemo 
        '''
        if len(self.controllers):
            return self.controllers
        controllers = self.getElementOfType('controller')
        [self.controllers.append(i) 
            for i in controllers if i in self.envCtrl is not None]
        return self.controllers
            
    def getCTs(self):
        '''Return the name of counter timer exp channel(s) defined by SarDemo 
        '''
        if len(self.cts):
            return self.cts
        cts = self.getElementOfType('ctexpchannel')
        [self.cts.append(i) for i in cts if i in self.env is not None]
        return self.cts

    def getMotors(self):
        '''Return the name of motor(s) defined by SarDemo 
        '''
        if len(self.motors):
            return self.motors
        motors = self.getElementOfType('motor')
        [self.motors.append(i) for i in motors if i in self.env is not None]
        return self.motors

    def getPseudoMotors(self):
        '''Return the name of pseudomotor(s) defined by SarDemo 
        '''
        if len(self.pseudos):
            return self.pseudos
        pseudos = self.getElementOfType('pseudomotor')
        [self.pseudos.append(i) for i in pseudos if i in self.env is not None]
        return self.pseudos

    def getZerods(self):
        '''Return the name of zerod exp channel(s) defined by SarDemo 
        '''
        if len(self.zerods):
            return self.zerods
        zerods = self.getElementOfType('zerodexpchannel')
        [self.zerods.append(i) for i in zerods if i in self.env is not None]
        return self.zerods

    def getOneds(self):
        '''Return the name of one exp channel(s) defined by SarDemo 
        '''
        if len(self.oneds):
            return self.oneds
        oneds = self.getElementOfType('onedexpchannel')
        [self.oneds.append(i) for i in oneds if i in self.env is not None]
        return self.oneds

    def getTwods(self):
        '''Return the name of two exp channel(s) defined by SarDemo 
        '''
        if len(self.twods):
            return self.twods
        twods = self.getElementOfType('twodexpchannel')
        [self.twods.append(i) for i in twods if i in self.env is not None]
        return self.twods
    
    def changeDoor(self, door_name):
        '''Change the door name and reset all lists 
        '''
        self.__init__(door_name)


if __name__ == '__main__':    
    s = SarDemoParsing()
    print s.env
    print s.getControllers()
    print s.getCTs()
    print s.getMotors()
    print s.getPseudoMotors()
    print s.getZerods()
    print s.getOneds()
    print s.getTwods()
    print s.getElementOfType('Motor')
    print s.getElements('Moveable')


    
