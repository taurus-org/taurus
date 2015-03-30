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
__all__ = ["SpecAuthority"]

from taurus.core.taurusauthority import TaurusAuthority
from taurus import Factory

class SpecAuthority(TaurusAuthority):
    '''
    Dummy authority class for Spec 
    
    .. warning:: In most cases this class should not be instantiated directly.
                 Instead it should be done via the :meth:`SpecFactory.getDataBase`
    '''

    # helper class property that stores a reference to the corresponding factory
    _factory = None
    _scheme = 'spec'

    def __init__(self, session, parent=None, storeCallback=None):
        #self.dbObj = SpecDeviceManager(session)      
        # Everything went ok so now we are sure we can store the object
        if not storeCallback is None:
            storeCallback(self)
        self.session = session
        self.call__init__(TaurusAuthority, session, parent)

    def getDevice(self, devNameValidator):
        try:
            #return self.dbObj.getDevice(devNameValidator)
            return self.factory.getSpecObj("%s/%s" %(self.session, devNameValidator))
        except:
            print "The device %s is not define in the Spec session" %(devNameValidator)
            return None     
            
#    def __getattr__(self, name):
#        if not self.dbObj is None: 
#            return getattr(self.dbObj,name)
#        return None
        #return "SpecAuthority object calling %s" % name

    '''
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # TaurusModel implementation
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-    

    # helper class property that stores a reference to the corresponding factory
    _factory = None
    @classmethod
    def factory(cls):
        if cls._factory is None:
            cls._factory = Factory(scheme='spec')
        return cls._factory
    '''   

    def getValueObj(self):
        """
            return dbObj which is a spec session manager
        """
        return self.dbObj
         

#===============================================================================
# Just for testing
#===============================================================================
def test():
    models = ["spec://lid00a:carlos","spec://must:fail"]
    for i in range(models.__len__()):
        session = models[i].split("//")[1]
        db = SpecAuthority(session)
        if db.getValueObj().isValidSession():
            print "It is a right db, ", session
        else:
            print "Wrong db session ", session

if __name__ == "__main__":
    test()
