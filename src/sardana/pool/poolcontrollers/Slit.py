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

"""This module contains the definition of a slit pseudo motor controller
for the Sardana Device Pool"""

__all__ = ["Slit"]

__docformat__ = 'restructuredtext'

from sardana import DataAccess
from sardana.pool.controller import PseudoMotorController
from sardana.pool.controller import DefaultValue, Description, Access, Type

    
class Slit(PseudoMotorController):
    """A Slit pseudo motor controller for handling gap and offset pseudo 
       motors. The system uses to real motors sl2t (top slit) and sl2b (bottom
       slit)"""
    
    gender = "Slit"
    model  = "Default Slit"
    organization = "Sardana team"
    
    pseudo_motor_roles = "Gap", "Offset"
    motor_roles = "sl2t", "sl2b"
    
    ctrl_properties = { 'sign' : { Type : float,
                                   Description  : 'Gap = sign * calculated gap\nOffset = sign * calculated offet',
                                   DefaultValue : 1 }, }
    
    axis_attributes = { 'example' : { Type : int,
                                      Access : DataAccess.ReadWrite,
                                      Description : 'test purposes' }, }

    def __init__(self, inst, props, *args, **kwargs):
        PseudoMotorController.__init__(self, inst, props, *args, **kwargs)
        self._log.debug("Created SLIT %s", inst)
        self._example = {}
        
    def CalcPhysical(self, index, pseudo_pos, curr_physical_pos):
        half_gap = pseudo_pos[0]/2.0
        if index == 1:
            ret = self.sign * (pseudo_pos[1] + half_gap)
        else:
            ret = self.sign * (half_gap - pseudo_pos[1])
        self._log.debug("Slit.CalcPhysical(%d, %s) -> %f", index, pseudo_pos, ret)
        return ret
    
    def CalcPseudo(self, index, physical_pos, curr_pseudo_pos):
        gap = physical_pos[1] + physical_pos[0]
        if index == 1:
            ret = self.sign * gap
        else:
            ret = self.sign * (physical_pos[0] - gap/2.0)
        return ret
        
    def CalcAllPseudo(self, physical_pos, curr_pseudo_pos):
        """Calculates the positions of all pseudo motors that belong to the 
           pseudo motor system from the positions of the physical motors."""
        gap = physical_pos[1] + physical_pos[0]
        return (self.sign * gap,
                self.sign * (physical_pos[0] - gap/2.0))
    
    #def CalcAllPhysical(self, pseudo_pos, curr_physical_pos):
    #    """Calculates the positions of all motors that belong to the pseudo 
    #       motor system from the positions of the pseudo motors."""
    #    half_gap = pseudo_pos[0]/2.0
    #    return (self.sign * (pseudo_pos[1] + half_gap),
    #            self.sign * (half_gap - pseudo_pos[1]))

    def SetAxisExtraPar(self, axis, parameter, value):
        self._example[axis] = value
    
    def GetAxisExtraPar(self, axis, parameter):
        return self._example.get(axis, -1)
