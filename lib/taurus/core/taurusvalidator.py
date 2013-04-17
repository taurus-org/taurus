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

"""This module contains the base taurus name validator classes"""

__all__ = ["AbstractTangoValidator", "DatabaseNameValidator",
           "DeviceNameValidator", "AttributeNameValidator",
           "ConfigurationNameValidator"]

__docformat__ = "restructuredtext"

import re

from .taurusbasetypes import MatchLevel
from .util.singleton import Singleton

InvalidAlias = "nada"

class AbstractTangoValidator:
    
    complete_name = None
    normal_name = None
    short_name = None
    
    uri_gen_delims = "\:\/\?\#\[\]\@"
    # theoreticaly sub_delims should include '+' but we are more permissive here in tango
    #uri_sub_delims = "\!\$\&\'\(\)\*\+\,\;\="
    uri_sub_delims = "\!\$\&\'\(\)\*\,\;\="
    uri_reserved = uri_gen_delims + uri_sub_delims
    tango_word = '[^' + uri_reserved + ']+'
    protocol_prefix = 'tango://'

    def __init__(self):
        self.complete_re = re.compile("^%s$" % self.complete_name)
        self.normal_re = re.compile("^%s$" % self.normal_name)
        self.short_re = re.compile("^%s$" % self.short_name)

    def __getMatch(self,str):
        return self.complete_re.match(str) or self.normal_re.match(str) or self.short_re.match(str)

    def isValid(self,str, matchLevel = MatchLevel.ANY):
        if matchLevel == MatchLevel.ANY:
            return not self.__getMatch(str) is None
        elif matchLevel == MatchLevel.SHORT:
            return not self.short_re.match(str) is None
        elif matchLevel == MatchLevel.NORMAL:
            return not self.normal_re.match(str) is None
        elif matchLevel == MatchLevel.COMPLETE:
            return not self.complete_re.match(str) is None
        elif matchLevel == MatchLevel.SHORT_NORMAL:
            return self.isValid(str,MatchLevel.SHORT) or \
                   self.isValid(str,MatchLevel.NORMAL)
        elif matchLevel == MatchLevel.NORMAL_COMPLETE:
            return self.isValid(str,MatchLevel.NORMAL) or \
                   self.isValid(str,MatchLevel.COMPLETE)
        return False
    
    def getParams(self,str):
        m = self.__getMatch(str)
        if m is None:
            return None
        return m.groupdict()
    
    def getNames(self, str, factory=None):
        """Returns a tuple of three elements with (complete_name, normal_name, short_name)
        or None if no match is found"""
        return None


class DatabaseNameValidator(Singleton, AbstractTangoValidator):
    
    protocol_prefix = '((?P<scheme>tango)://)?'
    
    db = '(?P<host>([\w\-_]+\.)*[\w\-_]+):(?P<port>\d{1,5})'
    # for tango://host:port
    complete_name = '(' + protocol_prefix + ')?' + db
    # for a/b/c
    normal_name = db
    # for devalias
    short_name = db
    
    def __init__(self):
        pass
    
    def init(self, *args, **kwargs):
        """Singleton instance initialization."""
        AbstractTangoValidator.__init__(self)
        
    def getNames(self, str, factory=None):
        elems = self.getParams(str)
        if elems is None:
            return str, None, None
        
        host = elems.get('host')
        port = elems.get('port')
        
        if host is None or port is None or len(host) == 0 or len(port) == 0:
            return None
        
        return 3*('%s:%s' % (host,port),)


class DatabaseQueryValidator(Singleton, AbstractTangoValidator):
    """Deprecated"""
    
    query = '\?query=(?P<query>[\w\-_]+)(?P<params>(\?param=[\w\*\?\%\-_]+)*)'

    complete_name = DatabaseNameValidator.complete_name + query 
    normal_name = DatabaseNameValidator.normal_name + query
    short_name = query
    
    def __init__(self):
        pass
    
    def init(self, *args, **kwargs):
        """Singleton instance initialization."""
        AbstractTangoValidator.__init__(self)

    def getNames(self, str, factory=None):
        elems = self.getParams(str)
        if elems is None:
            return str,None
        
        query = elems.get('query')
        params = elems.get('params')
        
        short = normal = query
        if params:
            normal += str(params.split('?param=')[1:])
        return str, normal, short    
            

class DeviceNameValidator(Singleton, AbstractTangoValidator):
    
    w = AbstractTangoValidator.tango_word
    dev = '(?P<devicename>' + w + '/' + w + '/' + w + ')'
    # for tango://host:port/a/b/c/attrname or host:port/a/b/c
    complete_name = DatabaseNameValidator.complete_name + '/' + dev
    # for a/b/c
    normal_name = DatabaseNameValidator.protocol_prefix + dev
    # for devalias
    short_name = '(?P<devalias>'+ w + ')'

    def __init__(self):
        pass
    
    def init(self, *args, **kwargs):
        """Singleton instance initialization."""
        AbstractTangoValidator.__init__(self)
        
    def getNames(self, str, factory=None):
        elems = self.getParams(str)
        if elems is None:
            return str,None
        
        dev_name = elems.get('devicename')
        alias = elems.get('devalias')
        
        host = elems.get('host')
        port = elems.get('port')
        
        if factory is None:
            return dev_name or '', dev_name or '', alias or ''

        db = None
        try:
            if host and port:
                db = factory.getDatabase("%s:%s" % (host,port))
                #db = PyTango.Database(host,int(port))
            else:
                #db = PyTango.Database()
                db = factory.getDatabase()
        except:
            return dev_name or '', dev_name or '', alias or ''
        
        if dev_name:
            alias = db.getElementAlias(dev_name) or dev_name
        else:
            dev_name = db.getElementFullName(alias)
        
        complete = "%s:%s/%s" % (host,port,dev_name)
        return complete, dev_name, alias


class DeviceQueryValidator(Singleton, AbstractTangoValidator):
    """Deprecated"""
    query = DatabaseQueryValidator.query

    complete_name = DeviceNameValidator.complete_name + query 
    normal_name = DeviceNameValidator.normal_name + query
    short_name = DeviceNameValidator.short_name + query

    def __init__(self):
        pass
    
    def init(self, *args, **kwargs):
        """Singleton instance initialization."""
        AbstractTangoValidator.__init__(self)    

    def getNames(self,str, factory=None):
        elems = self.getParams(str)
        if elems is None:
            return str,None
        
        query = elems.get('query')
        params = elems.get('params')
        
        short = query
        if params:
            short += str(params.split('?param=')[1:])
        return str,short    

    
class AttributeNameValidator(Singleton, AbstractTangoValidator):
    
    w = AbstractTangoValidator.tango_word
    attr = '/(?P<attributename>' + w + ')'
    # for tango://host:port/a/b/c/attributename or host:port/a/b/c/attributename
    complete_name = DeviceNameValidator.complete_name + attr
    # for a/b/c/attributename
    normal_name = DeviceNameValidator.normal_name + attr
    # for devalias/attributename
    short_name = DeviceNameValidator.short_name + attr
    
    def __init__(self):
        """ Initialization. Nothing to be done here for now."""
        pass
    
    def init(self, *args, **kwargs):
        """Singleton instance initialization."""
        AbstractTangoValidator.__init__(self)

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
    
    
class ConfigurationNameValidator(Singleton, AbstractTangoValidator):
    
    w = AbstractTangoValidator.tango_word
    conf = "\?(?i)configuration(=(?P<configparam>" + w + "))*"
    # for tango://host:port/a/b/c/attrname or host:port/a/b/c/attrname
    complete_name = AttributeNameValidator.complete_name + conf
    # for a/b/c/attrname
    normal_name = AttributeNameValidator.normal_name + conf
    # for devalias/attrname
    short_name = AttributeNameValidator.short_name + conf

    def __init__(self):
        """ Initialization. Nothing to be done here for now."""

    def init(self, *args, **kwargs):
        """Singleton instance initialization."""
        AbstractTangoValidator.__init__(self)

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
    

