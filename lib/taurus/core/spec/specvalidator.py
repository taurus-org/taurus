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

"""This module contains the base taurus name validator classes"""

__all__ = ["SpecAuthorityNameValidator", "SpecDeviceNameValidator", 
           "SpecAttributeNameValidator", "SpecConfigurationNameValidator"]

__docformat__ = "restructuredtext"


from taurus.core.taurusbasetypes import MatchLevel
from taurus.core.taurusvalidator import TaurusAttributeNameValidator, TaurusBaseValidator
from taurus.core.taurusvalidator import TaurusDeviceNameValidator, TaurusAuthorityNameValidator 
from taurus.core.taurusvalidator import TaurusConfigurationNameValidator 

InvalidAlias = "nada"

class SpecAuthorityNameValidator(TaurusAuthorityNameValidator):
    protocol_prefix = '((?P<scheme>spec)://)?'
    session = '(?P<session>([\w\-_]+\.)*[\w\-_]+:([\w\-_]+\.)*[\w\-_]+)'
    # for spec://session
    complete_name = '(' + protocol_prefix + ')?' + session
    # for a/b/c
    normal_name = session
    # for devalias
    short_name = session
    
    def __init__(self):
        pass
    
    def init(self, *args, **kwargs):
        """Singleton instance initialization."""
        TaurusAuthorityNameValidator.init(self, *args, **kwargs)
        
    def getNames(self, str, factory=None):
        elems = self.getParams(str)
        if elems is None:
            return str, None
        
        session = elems.get('session')
        
        if session is None or len(session) == 0 :
            return None
        
        return 3*('%s' %(session),) 


class SpecDeviceNameValidator(TaurusDeviceNameValidator):                             
    w = TaurusBaseValidator.word
    dev = '(?P<devicename>' + w + '/' + w + ')'
    #dev = '(?P<devicename>' + w + '(/' + w + ')+)'
    # for spec://session/a/b
    complete_name = SpecAuthorityNameValidator.complete_name + '/' + dev
    # for a/b
    normal_name = SpecAuthorityNameValidator.protocol_prefix + dev
    short_name = normal_name    

    def __init__(self):
        pass
    
    def init(self, *args, **kwargs):
        """Singleton instance initialization."""
        #TaurusBaseValidator.__init__(self)
        TaurusDeviceNameValidator.init(self, *args, **kwargs)
        
    def getNames(self, str, factory=None):
        """Returns the complete, normal and short names. (note: complete=normal)
        
        :param s: (str) input string describing the device
        :param factory: (TaurusFactory) [Unused]
        
        :return: (tuple<str,str,str> or None) A tuple of complete, normal and
                 short names, or None if s is an invalid device name
        """
        elems = self.getParams(str)
        if elems is None:
            return str,None
        
        dev_name = elems.get('devicename')
        session = elems.get('session')
       
        complete = "%s/%s" % (session,dev_name)
        return complete,dev_name,dev_name

    
class SpecAttributeNameValidator(TaurusAttributeNameValidator):                       
    w = TaurusBaseValidator.word
    ##attr = '/(?P<attributename>' + w + ')'
    ##attr = '/(?P<attributename>(' + w + ')*)'

    attr = '/(?P<attributename>(' + w + ')*(/' + w + ')?(/' + w + ')?)'
    ##attr = '(?P<attributename>([\w]+)*)'
    # for spec://session/a/b/attributename 
    complete_name = SpecDeviceNameValidator.complete_name + attr
    # for a/b/attributename
    normal_name = SpecDeviceNameValidator.normal_name + attr
    # for a/b/attributename
    short_name = SpecDeviceNameValidator.short_name + attr
    
    def __init__(self):
        """ Initialization. Nothing to be done here for now."""
        pass
    
    def init(self, *args, **kwargs):
        """Singleton instance initialization."""
        #TaurusBaseValidator.__init__(self)
        TaurusAttributeNameValidator.init(self, *args, **kwargs)

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
            
        return str,normal_name,attr_name

    
class SpecConfigurationNameValidator(TaurusConfigurationNameValidator):               #util.Singleton, TaurusBaseValidator):
    w = TaurusBaseValidator.word
    conf = "\?(?i)configuration(=(?P<configparam>" + w + "))*"
    # for spec://session/a/b/attrname or session/a/b/conf
    complete_name = SpecAttributeNameValidator.complete_name + conf
    # for a/b/conf
    normal_name = SpecAttributeNameValidator.normal_name + conf
    # for a/b/conf
    short_name = SpecAttributeNameValidator.short_name + conf

    def __init__(self):
        """ Initialization. Nothing to be done here for now."""

    def init(self, *args, **kwargs):
        """Singleton instance initialization."""
        #TaurusBaseValidator.__init__(self)
        TaurusConfigurationNameValidator.init(self, *args, **kwargs)

    def getNames(self, str, factory=None):
        """Returns the complete and short names"""
        
        elems = self.getParams(str)
        if elems is None:
            return None
                
        dev_name = elems.get('devicename')
        attr_name = elems.get('attributename')
        simple = elems.get('configparam') or 'configuration'
        
        if dev_name:
            normal = dev_name + "/" + attr_name + "?configuration=" + simple
        elif attr_name:
            normal = attr_name + "?configuration=" + simple
        else:
            normal = simple
        
        ret  = str,normal,simple
        return ret
    

#===============================================================================
# Just for testing
#===============================================================================
"""
    SPEC_MODEL = spec://SESSION/DEVICE/ATTRIBUTE    where

    SESSION   = machine:spec_session                                        i.e. lid00a:carlos
    DEVICE    = TYPE/NAME where
        TYPE  = {motor, variable, counter or command}
        NAME  = spec_name or in case XXX array 1_Name/2_Name/3_Name         i.e. motor/rot
                                                                            variable/TEST 
                                                                            variable/toto/titi/tata             
    ATRRIBUTE = /ATTRIBUTE_NAME or [/value or /](Only valid for variables)  i.e. /position
                                                                                 /
                                                                                 /value
"""


model1 = "spec://lid00a:carlos"
model2 = "spec://lid00a:carlos/motor/rot"
model3 = "spec://lid00a:carlos/motor/rot/velocity"

model3 = "spec://lid00a:carlos/variable/toto/"
model3 = "spec://lid00a:carlos/variable/toto/tata/titi"
#model3 = "spec://lid00a:carlos/variable/toto/tata/titi/value"

def test1():
  db_v = SpecAuthorityNameValidator()
  f, n, s  = db_v.getNames(model1)
  print 'DB     --> Authority session = %s = %s = %s' %(f, n, s )
  device_v = SpecDeviceNameValidator()
  f, n, s  = device_v.getNames(model2)
  print 'Device --> Complete = %s DeviceName = %s, Simple = %s' %(f, n, s)
  attr_v = SpecAttributeNameValidator()
  f, n, s = attr_v.getNames(model3)
  print 'Attr   --> Completo = %s Normal = %s Attribute = %s' %(f, n, s)
  
if __name__ == "__main__":
  test1()
