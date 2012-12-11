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

'''
Examples on using the evaluation scheme for exposing arbitrary non-tango quantities as taurus attributes
'''

__all__ = ['IcepapDriverParam']

from taurus.core.evaluation import EvaluationDevice
import re
import pyIcePAP

class IcepapDriverParam(EvaluationDevice):
    '''A simple example of usage of the evaluation scheme for 
    creating an icepap connection device to obtain icepap driver values.
    
    Important: note that only those members listed in `_symbols` will be available
    '''
    _symbols = ['getAxisParam']

    def __init__(self, *args, **kwargs):
        ''' Get from Database info the icepap host and port to connect. '''
        self.call__init__(EvaluationDevice, *args, **kwargs)

        # Get the icepap host and port to connect
        self.ipap = None

        try:
            db_name = self.getNameValidator().getDBName(self._full_name)
            db_name = db_name.replace('eval://','')
            db_name = db_name.replace('db=','')
            host,port = db_name.split(':')
            self.ipap = pyIcePAP.EthIcePAP(host, port)
            self.ipap.connect()
        except:
            pass
        
    def getAxisParam(self, axis, param):
        ''' return the axis parameter value. '''
        if self.ipap is None or not self.ipap.connected:
            raise Exception('Not a valid icepap connection')
        
        try:
            value = self.ipap.readParameter(axis, param)
            return float(value)
        except:
            return value
        

#===============================================================================
# Just for testing
#===============================================================================

ATTR_IPAP_POS = 'eval://db=icepap06:5000;dev=taurus.core.evaluation.ipap_example.IcepapDriverParam;getAxisParam(1,"POS")'

def test1():
    import taurus.core
    a = taurus.Attribute(ATTR_IPAP_POS)
    print "axis pos:", a.read().value
    
def test2():
    import sys
    from taurus.qt.qtgui.application import TaurusApplication
    from taurus.qt.qtgui.display import TaurusLabel
    app = TaurusApplication()
    
    tl = TaurusLabel()
    tl.setModel(ATTR_IPAP_POS)
    tl.show()

    sys.exit(app.exec_())
    
if __name__ == "__main__":
    test1()
    test2()
