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

__all__ = ["YYYDevice"]

"""
For create your basic scheme device.
Remplace XXX for the name of your scheme. i.e. tango
Remplace YYY for the name of your Scheme. i.e. Tango
"""

from taurus.core.taurusbasetypes import TaurusAttrValue, TaurusSWDevState
from taurus.core.taurusdevice import TaurusDevice
from taurus import Factory

class YYYDevice(TaurusDevice):
    '''
    An YYY device object. 
    @todo: For the moment is a dummy object. Eventually we may map it to an epics record.
    
    .. seealso:: :mod:`taurus.core.xxx`
    
    .. warning:: In most cases this class should not be instantiated directly.
                 Instead it should be done via the :meth:`YYYFactory.getDevice`
    '''
    
    # helper class property that stores a reference to the corresponding factory
    _factory = None
    _scheme = 'XXX'

    def __init__(self, name, **kw):
        """Object initialization."""
        self.call__init__(TaurusDevice, name, **kw)
    
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # TaurusDevice necessary overwrite
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    def _createHWObject(self):
        try:
            #We used the connector between HW and YYY (we should use DB)
            name = self.getFullName()
            f = self.factory()
            #TODO
            #i.e. return f.getSchemeObj(name) or return YYYTaurusInterface(self.getFullName())
        except:
            self.warning('Could not create XXX HW object  %s' % self.getFullName())
            self.traceback()

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    def getAttribute(self, attrname):
        """Returns the attribute object given its name"""
        full_attrname = "%s/%s"%(self.getFullName(), attrname)
        return self.factory().getAttribute(full_attrname)
    
    
    def decode(self, event_value):
        if isinstance(event_value, int): 
            new_sw_state = event_value
        else:
            self.info("Unexpected value to decode: %s" % str(event_value))
            new_sw_state = TaurusSWDevState.Crash
        value = TaurusAttrValue() 
        value.value = new_sw_state
        return value
        
