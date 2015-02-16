#!/usr/bin/env python
# -*- coding: utf-8 -*-

##############################################################################
##
## This file is part of Sardana
## 
## http://www.sardana-controls.org/
##
## Copyright 2011 CELLS / ALBA Synchrotron, Bellaterra, Spain
## 
## Sardana is free software: you can redistribute it and/or modify
## it under the terms of the GNU Lesser General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
## 
## Sardana is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU Lesser General Public License for more details.
## 
## You should have received a copy of the GNU Lesser General Public License
## along with Sardana.  If not, see <http://www.gnu.org/licenses/>.
##
##############################################################################

"""Parameter parsing"""

__all__ = ['AbstractParam', 'Param', 'ParamRepeat', 'ParamList']
           
import sys

class AbstractParam:
    
    def __init__(self, name=None, desc=None):
        self.name     = name
        self.desc     = desc
        
    def getParam(self,idx=0):
        return self

    def getParamStr(self):
        return "<"+self.name+">"

    def getParamDescr(self):
        str = self.name + " (" + self.type + ") - " + self.desc
        if self.defvalue != 'None':
            str = str + "\nDefault value: " + self.defvalue 
        return str

    def getParamCount(self):
        return 1

    def formatParamValue(self,value):
        return value
    
    def __str__(self):
        return "%s(%s)" % (self.__class__.__name__, self.name)

class Param(AbstractParam):
    
    def __init__(self, name=None, type_name=None, desc=None, defvalue=None,
                 from_array=None):
        AbstractParam.__init__(self,name=name,desc=desc)
        self.type     = type_name
        self.defvalue = defvalue

        if from_array is not None:
            for key in ['name', 'type', 'desc', 'defvalue']:
                setattr(self, key, from_array.read())
    
    def formatParamValue(self,value):
        ret = value
        if self.type == "File":
            f = open(ret,'r')
            ret = f.read()
            f.close()
        return ret
    
          
class ParamRepeat(AbstractParam):
    def __init__(self, name=None, desc=None, opts=None, param_def=None,
                 from_array=None):
        AbstractParam.__init__(self,name=name,desc=desc)
        self.opts      = opts
        self.param_def = param_def

        if from_array is not None:
            self.name = from_array.read()
            type_name = from_array.read() 
            if type_name != 'ParamRepeat':
                msg = 'Expecting "ParamRepeat" type, got ' + type_name
                raise ValueError, msg
            self.desc = from_array.read()
            opt_str = from_array.read()
            opt_list = opt_str.split(', ')
            opts = {}
            for opt_str in opt_list:
                name, val = opt_str.split('=')
                if val == repr(None):
                    val = None
                else:
                    try:    val = int(val)
                    except: pass
                opts[name] = val
            self.opts = opts
            self.param_def = ParamList(from_array=from_array)

    def getParam(self,idx=0):
        idx = idx % len(self.param_def.pars)
        return self.param_def.getParam(idx)
        
    def getParamStr(self):
        return "[" + self.param_def.getParamStr() + " ]"

    def getParamDescr(self):
        return self.param_def.getParamDescr()
        
    def getParamCount(self):
        return self.param_def.getParamCount()
    
    def formatParamValue(self,value):
        return self.param_def.formatParamValue(value)

 
class ParamList(AbstractParam):
    
    def __init__(self, from_array):
        AbstractParam.__init__(self,name="ParamList",desc="List of parameters")
    
        self.pars = []
        self.has_param_repeat = False
        
        npars = int(from_array.read())
        for i in range(npars):
            if from_array[1] == 'ParamRepeat':
                par = ParamRepeat(from_array=from_array)
                self.has_param_repeat = True
            else:
                par = Param(from_array=from_array)
            self.pars.append(par)
    
    def getParam(self,idx=0):
        par_nb = len(self.pars)
        if idx < par_nb:
            par = idx
            return self.pars[idx].getParam(0)
        else:
            for i in range(par_nb):
                local_idx = idx - i
                local_nb = self.pars[i].getParamCount()
                if local_idx < local_nb:
                    return self.pars[i].getParam(local_idx)        

    def getParamStr(self):
        str = ""
        for par in self.pars:
            str = str + " " + par.getParamStr()
        return str

    def getParamDescr(self):
        str = ""
        for par in self.pars:
            str = str + "\n" + par.getParamDescr()
        return str

    def getParamCount(self):
        nb = 0
        for par in self.pars:
            local_nb = par.getParamCount()
            if local_nb == sys.maxint: 
                return sys.maxint
            nb += local_nb
        return nb
    
    def formatParamValue(self,value):
        
        # for now we are not able to handle ParamRepeat with special value format
        if self.has_param_repeat:
            return value
        
        for i,v in enumerate(value):
            value[i] = self.pars[i].formatParamValue(v)
        return value