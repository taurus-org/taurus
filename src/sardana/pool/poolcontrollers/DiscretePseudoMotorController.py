#!/usr/bin/env python

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

"""This module contains the definition of a discrete pseudo motor controller
for the Sardana Device Pool"""

__all__ = ["DiscretePseudoMotorController"]

__docformat__ = 'restructuredtext'

import json

from sardana import DataAccess
from sardana.pool.controller import PseudoMotorController
from sardana.pool.controller import Type, Access, Description

CALIBRATION = 'Calibration'
LABELS = 'Labels'


class DiscretePseudoMotorController(PseudoMotorController):
    """A discrete pseudo motor controller which converts physical motor positions
    to discrete values"""
    
    gender = "DiscretePseudoMotorController"
    model  = "PseudoMotor"
    organization = "Sardana team"
    image = ""

    pseudo_motor_roles = ("OutputMotor",)
    motor_roles = ("InputMotor",)

    axis_attributes = {CALIBRATION:#type hackish until arrays supported
                        {Type : str,
                         Description : 'Flatten list of a list of triples and [min,cal,max]',
                         Access : DataAccess.ReadWrite,
                         'fget' : 'get%s' % CALIBRATION,
                         'fset' : 'set%s' % CALIBRATION},
                       LABELS:#type hackish until arrays supported
                        {Type : str,
                         Description : 'String list with the meaning of each discrete position',
                         Access : DataAccess.ReadWrite,
                         'fget' : 'get%s' % LABELS,
                         'fset' : 'set%s' % LABELS}
                      }


    def __init__(self, inst, props, *args, **kwargs):
        PseudoMotorController.__init__(self, inst, props, *args, **kwargs)
        self._calibration = None
        self._positions = None
        self._labels = None


    def GetAxisAttributes(self, axis):
        axis_attrs = PseudoMotorController.GetAxisAttributes(self, axis)
        axis_attrs = dict(axis_attrs)
        axis_attrs['Position']['type'] = float
        return axis_attrs


    def CalcPseudo(self, axis, physical_pos, curr_pseudo_pos):
        llabels = len(self._labels)
        positions = self._positions
        calibration = self._calibration
        lcalibration = len(calibration)

        value = physical_pos[0]
        #case 0: nothing to translate, only round about integer the attribute value
        if llabels == 0:
            return int(value)
        #case 1: only uses the labels. Available positions in POSITIONS
        elif lcalibration == 0:
            value = int(value)
            try: positions.index(value)
            except: raise Exception("Invalid position.")
            else: return value
        #case 1+fussy: the physical position must be in one of the defined
        #ranges, and the DiscretePseudoMotor position is defined in labels
        elif llabels == lcalibration:
            for fussyPos in calibration:
                if value >= fussyPos[0] and value <= fussyPos[2]:
                    return positions[calibration.index(fussyPos)]
            #if the loop ends, current value is not in the fussy areas.
            raise Exception("Invalid position.")
        else:
            raise Exception("Bad configuration on axis attributes.")


    def CalcPhysical(self, axis, pseudo_pos, curr_physical_pos):
        #If Labels is well defined, the write value must be one this struct
        llabels = len(self._labels)
        positions = self._positions
        calibration = self._calibration
        lcalibration = len(calibration)
        value = pseudo_pos[0]

        #case 0: nothing to translate, what is written goes to the attribute
        if llabels == 0:
            return value
        #case 1: only uses the labels. Available positions in POSITIONS
        elif lcalibration == 0:
            self._log.debug("Value = %s", value)
            try: positions.index(value)
            except: raise Exception("Invalid position.")
            return value
        #case 1+fussy: the write to the to the DiscretePseudoMotorController
        #is translated to the central position of the calibration.
        elif llabels == lcalibration:
            self._log.debug("Value = %s", value)
            try: destination = positions.index(value)
            except: raise Exception("Invalid position.")
            self._log.debug("destination = %s", destination)
            calibrated_position = calibration[destination][1]#central element
            self._log.debug("calibrated_position = %s", calibrated_position)
            return calibrated_position


    def getLabels(self,axis):
        #hackish until we support DevVarDoubleArray in extra attrs
        labels = self._labels
        positions = self._positions
        labels_str = ""
        for i in range(len(labels)):
            labels_str += "%s:%d "%(labels[i],positions[i])
        return labels_str[:-1]#remove the final space


    def setLabels(self,axis,value):
        #hackish until we support DevVarStringArray in extra attrs
        labels = []
        positions = []
        for pair in value.split():
            l,p = pair.split(':')
            labels.append(l)
            positions.append(int(p))
        if len(labels) == len(positions):
            self._labels = labels
            self._positions = positions
        else:
            raise Exception("Rejecting labels: invalid structure")


    def getCalibration(self,axis):
        return json.dumps(self._calibration)


    def setCalibration(self,axis,value):
        try:
            self._calibration = json.loads(value)
        except:
            raise Exception("Rejecting calibration: invalid structure")
