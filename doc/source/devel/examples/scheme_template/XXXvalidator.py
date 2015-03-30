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

#Todo: this is very outdated *and* tango-centric. Needs complete rewriting.


__all__ = ["YYYDatabaseNameValidator", "YYYDeviceNameValidator", 
           "YYYAttributeNameValidator", "YYYConfigurationNameValidator"]

__docformat__ = "restructuredtext"

"""
For create your basic scheme validator.
Remplace XXX for the name of your scheme. i.e. tango
Remplace YYY for the name of your Scheme. i.e. Tango
"""

from taurus.core.taurusbasetypes import MatchLevel
from taurus.core.taurusvalidator import TaurusAttributeNameValidator, TaurusBaseValidator
from taurus.core.taurusvalidator import TaurusDeviceNameValidator, TaurusAuthorityNameValidator 
from taurus.core.taurusvalidator import TaurusConfigurationNameValidator 

InvalidAlias = "nada"

class YYYDatabaseNameValidator(TaurusAuthorityNameValidator):
    # TODO Create your own grammatical expression. i.e    
    #protocol_prefix = '((?P<scheme>XXX)://)?'
    #session = '(?P<session>([\w\-_]+\.)*[\w\-_]+:([\w\-_]+\.)*[\w\-_]+)'
    #complete_name = '(' + protocol_prefix + ')?' + session
    #normal_name = session
    #short_name = session
    
    def __init__(self):
        pass
    
    def init(self, *args, **kwargs):
        """Singleton instance initialization."""
        TaurusAuthorityNameValidator.init(self, *args, **kwargs)
        
    def getNames(self, str):
        elems = self.getParams(str)
        if elems is None:
            return str, None
        
        session = elems.get('session')
        
        if session is None or len(session) == 0 :
            return None
        
        return 3*('%s' %(session),) 


class YYYDeviceNameValidator(TaurusDeviceNameValidator): 
    # TODO Create your own grammatical expression. i.e                                
    #w = TaurusBaseValidator.word
    #dev = '(?P<devicename>' + w + '/' + w + ')'
    #complete_name = YYYDatabaseNameValidator.complete_name + '/' + dev
    #normal_name = YYYDatabaseNameValidator.protocol_prefix + dev
    #short_name = normal_name    

    def __init__(self):
        pass
    
    def init(self, *args, **kwargs):
        """Singleton instance initialization."""
        TaurusDeviceNameValidator.init(self, *args, **kwargs)
        
    def getNames(self, str):
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

    
class YYYAttributeNameValidator(TaurusAttributeNameValidator):        
    # TODO Create your own grammatical expression. i.e                 
    #w = TaurusBaseValidator.word
    #attr = '/(?P<attributename>(' + w + ')*(/' + w + ')?(/' + w + ')?)'
    #complete_name = SpecDeviceNameValidator.complete_name + attr
    #normal_name = SpecDeviceNameValidator.normal_name + attr
    #short_name = SpecDeviceNameValidator.short_name + attr
    
    def __init__(self):
        """ Initialization. Nothing to be done here for now."""
        pass
    
    def init(self, *args, **kwargs):
        """Singleton instance initialization."""
        TaurusAttributeNameValidator.init(self, *args, **kwargs)

    def getNames(self, str):
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

    
class YYYConfigurationNameValidator(TaurusConfigurationNameValidator):
    # TODO Create your own grammatical expression. i.e               
    #w = TaurusBaseValidator.word
    #conf = "\?(?i)configuration(=(?P<configparam>" + w + "))*"
    #complete_name = YYYAttributeNameValidator.complete_name + conf
    #normal_name = YYYAttributeNameValidator.normal_name + conf
    #short_name = YYYAttributeNameValidator.short_name + conf

    def __init__(self):
        """ Initialization. Nothing to be done here for now."""

    def init(self, *args, **kwargs):
        """Singleton instance initialization."""
        #TaurusBaseValidator.__init__(self)
        TaurusConfigurationNameValidator.init(self, *args, **kwargs)

    def getNames(self, str):
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

    
