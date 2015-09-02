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

"""This module contains the base class for a taurus database"""

__all__ = ["TaurusAuthority"]

__docformat__ = "restructuredtext"


from .taurusbasetypes import TaurusElementType
from .taurusmodel import TaurusModel
from .taurushelper import Factory



class TaurusAuthority(TaurusModel):
    
    default_description = "A Taurus Authority"
    
    def __init__(self, complete_name, parent=None):
        self._descr = None
        self.call__init__(TaurusModel, complete_name, parent)
    
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # TaurusModel implementation
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-    
    def cleanUp(self):
        self.trace("[TaurusAuthority] cleanUp")
        TaurusModel.cleanUp(self)

    @classmethod
    def factory(cls):
        if cls._factory is None:
            cls._factory = Factory(scheme=cls._scheme)
        return cls._factory

    @classmethod
    def getTaurusElementType(cls):
        return TaurusElementType.Authority
    
    @classmethod
    def buildModelName(cls, parent_model, relative_name):
        """build an 'absolute' model name from the parent name and the 
        'relative' name. parent_model is ignored since there is nothing above 
        the Authority object
        
        Note: This is a basic implementation. You may need to reimplement this 
              for a specific scheme if it supports "useParentModel". 
        """
        return relative_name
    
    @classmethod
    def getNameValidator(cls):
        return cls.factory().getAuthorityNameValidator()
    
    def getDescription(self,cache=True):
        if self._descr is None or not cache:
            try:
                self._descr = self.info()
            except:
                self._descr = self._getDefaultDescription()
        return self._descr

    def getDisplayDescription(self,cache=True):
        return self.getFullName()
    
    def getDisplayDescrObj(self,cache=True):
        obj = []
        obj.append(('name', self.getDisplayName(cache=cache)))
        descr = self.getDescription(cache=cache)
        obj.append(('description', descr))
        return obj

    def getChildObj(self,child_name):
        if not child_name:
            return None
        return self.getDevice(child_name)

    def _getDefaultDescription(self):
        return self.default_description
    
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # Device access method
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-    
    
    def getDevice(self, devname):
        """Returns the device object given its name"""
        import taurusdevice
        return self.factory().getObject(taurusdevice.TaurusDevice, devname)


# For backwards compatibility, we make an alias for TaurusAuthority.
# Note that no warning is issued!
TaurusDatabase = TaurusAuthority
