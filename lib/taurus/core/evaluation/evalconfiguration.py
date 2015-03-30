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

__all__ = ["EvaluationConfiguration"]

from taurus import Factory
from taurus.core.taurusconfiguration import TaurusConfiguration

class EvaluationConfiguration(TaurusConfiguration):
    '''
    A :class:`TaurusConfiguration` 
    
    .. seealso:: :mod:`taurus.core.evaluation` 
    
    .. warning:: In most cases this class should not be instantiated directly.
                 Instead it should be done via the 
                        :meth:`EvaluationFactory.getConfig`
    '''

    # helper class property that stores a reference to the corresponding factory
    _factory = None
    _scheme = 'eval'

    def __init__(self, name, parent, storeCallback = None):
        self.call__init__(TaurusConfiguration, name, parent, 
                            storeCallback=storeCallback)
        self._attr_info = parent.read().config
        
    def __getattr__(self, name): 
        try:
            return getattr(self._attr_info,name)
        except:
            raise AttributeError(" '%s'object has no attribute '%s'" \
                                    %(self.__class__.__name__, name) )
        
    def _subscribeEvents(self): 
        pass
    
    def _unSubscribeEvents(self):
        pass   
    
    def getValueObj(self, cache=True):
        """ Returns the current configuration for the attribute."""
        return self._attr_info  

