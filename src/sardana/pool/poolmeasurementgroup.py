#!/usr/bin/env python

##############################################################################
##
## This file is part of Sardana
##
## http://www.tango-controls.org/static/sardana/latest/doc/html/index.html
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

"""This module is part of the Python Pool libray. It defines the base classes
for"""

__all__ = [ "PoolMeasurementGroup" ]

__docformat__ = 'restructuredtext'

import math

from poolbase import *
from pooldefs import *
from poolelement import *
from poolacquisition import *


MeasurementGroupConfiguration = \
{ 'master' : '<master name> (=<master id>)',
  'groups' : { '<group name> (=<ctrl name>) (=<ctrl id>)+' : { 'channels' : {} }
             }
}

#dict <str, obj> with (at least) keys:
#    - 'timer' : the timer channel name / timer channel id
#    - 'monitor' : the monitor channel name / monitor channel id
#    - 'units' : dict<str/int, dict> where:
#        - key: the unit name / ctrl name / ctrl id
#        - value: dict<str, dict> with (at least) keys:
#            - 'master' : the master channel name / master channel id
#            - 'trigger_mode' : 'Gate'/'Software'
#            - 'channels' where value is a dict<str, obj> with (at least) keys:
#                - 'id' : the channel name ( channel id )
#                optional keys:
#                - 'enabled' : True/False (default is True)
#                any hints:
#                - 'output' : True/False (default is True)
#                - 'plotable' : 'False'/'x'/'y1'/'y2' (default is 'y1')
#                - 'label' : prefered label (default is channel name)
#                - 'scale' : <float, float> with min/max (defaults to channel
#                            range if it is defined
#                - 'color' : int representing RGB
#    optional keys:
#    - 'label' : measurement group label (defaults to measurement group name)
#    - 'description' : measurement group description

# Example: 2 NI cards, where channel 1 of card 1 is wired to channel 1 of card 2
# at configuration time we should set:
# ctrl.setPar( <unit>, <parameter name>, <parameter value> )
# ni0ctrl.setPar(0, 'trigger_mode', AcqTriggerMode.Software)
# ni0ctrl.setPar(0, 'timer', 1) # channel 1 is the timer
# ni0ctrl.setPar(0, 'monitor', 4) # channel 4 is the monitor
# ni1ctrl.setPar(0, 'trigger_mode', AcqTriggerMode.ExternalTrigger)
# ni1ctrl.setPar(0, 'master', 0)

# when we count for 1.5 seconds:
# ni1ctrl.Load(1.5)
# ni0ctrl.Load(1.5)
# ni1ctrl.Start()
# ni0ctrl.Start()

"""

"""

class PoolMeasurementGroup(PoolGroupElement):

    def __init__(self, **kwargs):
        self._master = None
        PoolGroupElement.__init__(self, **kwargs)
        self.set_configuration(kwargs.get('config'))
        self.set_action_cache(PoolCTAcquisition("%s.CTAcquisition" % self._name))
    
    def get_type(self):
        return ElementType.MeasurementGroup
    
    def on_element_changed(self, evt_src, evt_type, evt_value):
        pass
    
    # --------------------------------------------------------------------------
    # configuration
    # --------------------------------------------------------------------------
    
    def set_configuration(self, config=None):
        if config is None:
            config = {}
            config['master'] = self.get_user_elements()[0].id
            
    
    # --------------------------------------------------------------------------
    # master
    # --------------------------------------------------------------------------
    
    def get_master(self):
        return self._master
    
    def set_master(self, master, propagate=1):
        self._master = self.get_element_by_id(master.id)
        if not propagate:
            return
        self.fire_event(EventType("master", priority=propagate), master)
    
    def set_master_name(self, name, propagate=1):
        self.set_master( self.get_element_by_name(name), propagate=propagate )
    
    master = property(get_master, set_master, doc="master channel")

    def get_trigger_mode(self):
        return self._trigger_mode
    
    def set_trigger_mode(self, trigger_mode, propagate=1):
        self._trigger_mode = trigger_mode
        if not propagate:
            return
        self.fire_event(EventType("trigger_mode", priority=propagate), trigger_mode)
    
    trigger_mode = property(get_trigger_mode, set_trigger_mode,
                            doc="active trigger mode")
    
    # --------------------------------------------------------------------------
    # acquisition
    # --------------------------------------------------------------------------
    def start_acquisition(self, value=None):
        self._aborted = False
        if not self._simulation_mode:
            self.acquisition.run(head=self)
    
    def get_acquisition(self):
        return self.get_action_cache()
    
    acquisition = property(get_acquisition, doc="acquisition object")