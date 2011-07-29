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

""" """

__all__ = ["Controller", "MotorController", "CounterTimerController",
           "PseudoMotorController" ]

__docformat__ = 'restructuredtext'

import sys
import datetime
import weakref
import taurus.core.util.log

from pooldefs import AcqTriggerType

class Controller:
    """Base controller class. Do **NOT** inherit from this class directly"""

    #: .. deprecated:: 1.0
    #:     use :attr:`Controller.ctrl_properties` instead
    class_prop = {}
    
    #: A sequence of :class:`str` representing the controller features
    ctrl_features = []
    
    #: .. deprecated:: 1.0
    #:     Deprecated: use :attr:`Controller.axis_attributes` instead
    ctrl_extra_attributes = {}
    
    #: A :class:`dict` containning controller properties where:
    #: - key : (:class:`str`) controller property name
    #: - value : :class:`dict` with with three :class:`str` keys ("type", "description" and "defaultvalue" case insensitive):
    #:
    #:     - for key="type", value is one of the values described in :ref:`pool-controller-data-type`
    #:     - for key="description", value is a :class:`str` description of the property.
    #:       if is not given it defaults to empty string.
    #:     - for key="defaultvalue", value is a python object or None if no default value exists for the property
    #:       if is not given it defaults to None value.
    ctrl_properties = {}
    
    #: A :class:`dict` containning controller extra attributes where:
    #:
    #: - key : (:class:`str`) controller attribute name
    #: - value : :class:`dict` with :class:`str` possible keys: "type", "r/w type", "description", "fget" and "fset" (case insensitive):
    #:     - for key="type", value is one of the values described in :ref:`pool-controller-data-type`
    #:     - for key="r/w type", value is one of "read" or "read_write" (case insensitive)
    #:     - for key="description", value is a :class:`str` description of the attribute
    #:     - for key="fget", value is a :class:`str` with the method name for the attribute getter
    #:       if is not given it defaults to "get"<controller attribute name>
    #:     - for key="fset", value is a :class:`str` with the method name for the attribute setter
    #:       if is not given and "r/w type"="read_write" it defaults to "set"<controller attribute name>
    #:
    #: .. versionadded:: 1.0
    ctrl_attributes = {}

    #: A :class:`dict` containning controller extra attributes for each axis where:
    #:
    #: - key : (:class:`str`) axis attribute name
    #: - value : :class:`dict` with three :class:`str` keys ("type", "r/w type", "description" case insensitive):
    #:     - for key="type", value is one of the values described in :ref:`pool-controller-data-type`
    #:     - for key="r/w type", value is one of "read" or "read_write" (case insensitive)
    #:     - for key="description", value is a :class:`str` description of the attribute
    #:
    #: .. versionadded:: 1.0
    axis_attributes = {}
    
    #: A :class:`str` representing the controller gender
    gender = None
    
    #: A :class:`str` representing the controller model name
    model = None
    
    #: A :class:`str` representing the controller organization
    organization = None
    
    #: A :class:`str` containning the path to the image file
    image = None
    
    #: A :class:`str` containning the path to the image logo file
    logo = None
    
    def __init__(self, inst, props):
        self.inst_name = inst
        self._log = taurus.core.util.log.Logger("Controller.%s" % inst)
        self._log.log_obj.setLevel(taurus.getLogLevel())
        for k, v in props.items():
            if k.startswith("__"):
                v = weakref.ref(v)
            setattr(self, k, v)
    
    def PreStateAll(self):
        """**Controller API**. Overwrite as necessary.
        Called to prepare a read of the state of all axis.
        Default implementation does nothing."""
        pass
    
    def PreStateOne(self, axis):
        """**Controller API**. Overwrite as necessary.
        Called to prepare a read of the state of a single axis.
        Default implementation does nothing.
        
        :param int axis: axis number"""
        pass
    
    def StateAll(self):
        """**Controller API**. Overwrite as necessary.
        Called to read the state of all selected axis.
        Default implementation does nothing."""
        pass
    
    #def SetCtrlPar(self, unit, parameter, value):
    def SetCtrlPar(self, parameter, value):
        """**Controller API**. Overwrite as necessary.
        Called to set a parameter with a value.
        Default implementation sets this object member named '_'+parameter with
        the given value.
        
        .. versionadded:: 1.0"""
        setattr(self, '_'+parameter, value)

    #def GetCtrlPar(self, unit, parameter):
    def GetCtrlPar(self, parameter):
        """**Controller API**. Overwrite as necessary.
        Called to set a parameter with a value.
        Default implementation returns the value contained in this object's
        member named '_'+parameter.
        
        .. versionadded:: 1.0"""
        return getattr(self, '_'+parameter)
    
    #def SetAxisPar(self, unit, axis, parameter, value):
    def SetAxisPar(self, axis, parameter, value):
        """**Controller API**. Overwrite as necessary.
        Called to set a parameter with a value on the given axis.
        Default implementation calls deprecated :meth:`Controller.SetPar`.
        
        .. versionadded:: 1.0"""
        return self.setPar(axis, parameter, value)
    
    #def GetAxisPar(self, unit, axis, parameter):
    def GetAxisPar(self, axis, parameter):
        """**Controller API**. Overwrite as necessary.
        Called to get a parameter value on the given axis.
        Default implementation calls deprecated :meth:`Controller.GetPar`.
        
        .. versionadded:: 1.0"""
        return self.getPar(axis, parameter)
    
    def SetExtraAxisPar(self, axis, parameter, value):
        """**Controller API**. Overwrite as necessary.
        Called to set a parameter with a value on the given axis.
        Default implementation calls deprecated :meth:`Controller.SetExtraAttributePar`.
        
        .. versionadded:: 1.0"""
        return self.SetExtraAttributePar(axis, parameter, value)
    
    def GetAxisExtraPar(self, axis, parameter):
        """**Controller API**. Overwrite as necessary.
        Called to get a parameter value on the given axis.
        Default implementation calls deprecated :meth:`Controller.GetExtraAttributePar`.
        
        .. versionadded:: 1.0"""
        return self.GetExtraAttributePar(axis, parameter)

    def SetPar(self, axis, parameter, value):
        """**Controller API**. *Dreprecated: use setAxisPar instead.*.
        Called to set a parameter with a value on the given axis.
        Default implementation raises NotImplementedError.

        .. deprecated:: 1.0
            Deprecated: use :meth:`Controller.SetAxisPar` instead"""
        raise NotImplementedError

    def GetPar(self, axis, parameter):
        """**Controller API**. *Dreprecated: use setAxisPar instead.*.
        Called to get a parameter value on the given axis.
        Default implementation raises NotImplementedError.

        .. deprecated:: 1.0
            Deprecated: use :meth:`Controller.GetAxisPar` instead"""
        raise NotImplementedError

    def SetExtraAttributePar(self, axis, parameter, value):
        """**Controller API**. *Dreprecated: use setAxisExtraPar instead.*.
        Called to set a parameter with a value on the given axis.
        Default implementation raises NotImplementedError.

        .. deprecated:: 1.0
            Deprecated: use :meth:`Controller.SetAxisExtraPar` instead"""
        raise NotImplementedError

    def GetExtraAttributePar(self, axis, parameter):
        """**Controller API**. *Dreprecated: use setAxisExtraPar instead.*.
        Called to get a parameter value on the given axis.
        Default implementation raises NotImplementedError.

        .. deprecated:: 1.0
            Deprecated: use :meth:`Controller.GetAxisExtraPar` instead"""
        raise NotImplementedError
        
    @classmethod
    def GetStandardAxisAttributes(self, axis):
        """**Controller API**. Overwrite as necessary.
        Returns a sequence of standard attributes per axis.
        Default implementation returns empty :class:`tuple`.
        
        :param int axis: axis number
        :return: sequence of standard attributes
        
        .. versionadded:: 1.0"""
        return ()


class MotorController(Controller):
    """Base class for a motor controller. Inherit from this class to implement
    your own motor controller for the device pool.
    
    A motor controller should support these axis parameters:
    
        - acceleration
        - deceleration
        - velocity
        - base_rate
        - step_per_unit
    
    These parameters are configured through the GetAxisPar/SetAxisPar API (in
    version <1.0 the methods were called GetPar/SetPar. Default GetAxisPar and
    SetAxisPar still call these methods to maintain backward compatibility).
    """
    
    def PreReadAll(self):
        """**Motor Controller API**. Overwrite as necessary.
        Called to prepare a read of the position of all axis.
        Default implementation does nothing."""
        pass
    
    def PreReadOne(self, axis):
        """**Motor Controller API**. Overwrite as necessary.
        Called to prepare a read of the position of a single axis.
        Default implementation does nothing.
        
        :param int axis: axis number"""
        pass
    
    def ReadAll(self):
        """**Motor Controller API**. Overwrite as necessary.
        Called to read the position of all selected axis.
        Default implementation does nothing."""
        pass
    
    def PreStartAll(self):
        """**Motor Controller API**. Overwrite as necessary.
        Called to prepare a write of the position of all axis.
        Default implementation does nothing."""
        pass
    
    def PreStartOne(self, axis, position):
        """**Motor Controller API**. Overwrite as necessary.
        Called to prepare a write of the position of a single axis.
        Default implementation returns True.
        
        :param int axis: axis number
        :param float position: new position
        :return: True means a successfull PreStart or False for a failure
        :rtype: bool"""
        return True
    
    def StartOne(self, axis, position):
        """**Motor Controller API**. Overwrite as necessary.
        Called to write the position of a selected axis
        Default implementation does nothing.
        
        :param int axis: axis number
        :param float position: new position"""
        pass
    
    @classmethod
    def GetStandardAxisAttributes(self, axis):
        """**Motor Controller API**. Overwrite as necessary.
        Returns a sequence of standard attributes per axis.
        Default implementation returns a :class:`tuple` containning:
        
        - acceleration
        - deceleration
        - base_rate
        - velocity
        - step_per_unit
        - offset
        - dialposition
        - backlash
        - sign
        - limit_switches
        
        :param int axis: axis number
        :return: sequence of standard attributes
        
        .. versionadded:: 1.0"""
        return "acceleration", "deceleration", "base_rate", "velocity", \
            "step_per_unit", "offset", "dialposition", "backlash", "sign", \
            "limit_switches"


class CounterTimerController(Controller):
    """Base class for a counter/timer controller. Inherit from this class to 
    implement your own counter/timer controller for the device pool.
    
    A counter timer controller should support these controller parameters:
    
        - timer
        - monitor
        - trigger_type"""
    
    def __init__(self, inst, props):
        Controller.__init__(self, inst, props)
        self._timer = None
        self._monitor = None
        self._master = None
        self._trigger_type = AcqTriggerType.Unknown
    
    def PreReadAll(self):
        """**Counter/Timer Controller API**. Overwrite as necessary.
        Called to prepare a read of the value of all axis.
        Default implementation does nothing."""
        pass
    
    def PreReadOne(self, axis):
        """**Counter/Timer Controller API**. Overwrite as necessary.
        Called to prepare a read of the value of a single axis.
        Default implementation does nothing.
        
        :param int axis: axis number"""
        pass
    
    def ReadAll(self):
        """**Counter/Timer Controller API**. Overwrite as necessary.
        Called to read the value of all selected axis
        Default implementation does nothing."""
        pass
    
    def PreStartAllCT(self):
        """**Counter/Timer Controller API**. Overwrite as necessary.
        Called to prepare an acquisition of all selected axis.
        Default implementation does nothing."""
        pass
    
    def PreStartOneCT(self, axis):
        """**Counter/Timer Controller API**. Overwrite as necessary.
        Called to prepare an acquisition a single axis.
        Default implementation returns True.
        
        :param int axis: axis number
        :return: True means a successfull PreStartOneCT or False for a failure
        :rtype: bool"""
        return True
    
    def StartOneCT(self, axis):
        """**Counter/Timer Controller API**. Overwrite as necessary.
        Called to start an acquisition of a selected axis.
        Default implementation does nothing.
        
        :param int axis: axis number"""
        pass
    
    def PreLoadAll(self):
        """**Counter/Timer Controller API**. Overwrite as necessary.
        Called to prepare loading the integration time / monitor value.
        Default implementation does nothing."""
        pass
    
    def PreLoadOne(self, axis, value):
        """**Counter/Timer Controller API**. Overwrite as necessary.
        Called to prepare loading the master channel axis with the integration 
        time / monitor value.
        Default implementation returns True.
        
        :param int axis: axis number
        :return: True means a successfull PreLoadOne or False for a failure
        :rtype: bool"""
        return True
    
    def LoadAll(self):
        """**Counter/Timer Controller API**. Overwrite as necessary.
        Called to load the integration time / monitor value.
        Default implementation does nothing."""
        pass


class PseudoMotorController(Controller):
    """Base class for a pseudo motor controller. Inherit from this class to 
    implement your own pseudo motor controller for the device pool.

    Every Pseudo Motor implementation must be a subclass of this class.
    Current procedure for a correct implementation of a Pseudo Motor class:
    
    - mandatory: define the class level attributes :attr:`PseudoMotorController.pseudo_motor_roles`,
                 :attr:`PseudoMotorController.motor_roles` and
                 :attr:`Controller.class_prop` (if any).
    - mandatory: write :meth:`PseudoMotorController.calc_pseudo` method
    - mandatory: write :meth:`PseudoMotorController.calc_physical` method.
    - optional: write :meth:`PseudoMotorController.calc_all_pseudo` 
                and :meth:`PseudoMotorController.calc_all_physical` if great
                performance gain can be achived"""

    #: a sequence of strings describing the role of each pseudo motor axis in
    #: this controller
    pseudo_motor_roles = ()

    #: a sequence of strings describing the role of each motor 
    motor_roles = ()

    def calc_all_pseudo(self, physical_pos):
        """**Pseudo Motor Controller API**. Overwrite as necessary.
           Calculates the positions of all pseudo motors that belong to the
           pseudo motor system from the positions of the physical motors.
           Default implementation does a loop calling :meth:`PseudoMotorController.calc_pseudo`
           for each pseudo motor role.
           
           :param physical_pos: a sequence of physical motor positions
           :type physical_pos: sequence<float>
           :return: a sequece of pseudo motor positions (one for each pseudo motor role)
           :rtype: sequence<float>"""
        ret = []
        for i in xrange(self.get_pseudo_motor_nb()):
            ret.append(self.calc_pseudo(i+1, physical_pos))
        return ret
    
    def calc_all_physical(self, pseudo_pos):
        """**Pseudo Motor Controller API**. Overwrite as necessary.
           Calculates the positions of all motors that belong to the pseudo 
           motor system from the positions of the pseudo motors.
           Default implementation does a loop calling :meth:`PseudoMotorController.calc_physical`
           for each motor role.
           
           :param pseudo_pos: a sequence of pseudo motor positions
           :type pseudo_pos: sequence<float>
           :return: a sequece of motor positions (one for each motor role)
           :rtype: sequence<float>"""

        """Calculates the positions of all motors that belong to the pseudo 
           motor system from the positions of the pseudo motors."""
        ret = []
        for i in xrange(len(self.motor_roles)):
            pos = self.calc_physical(i+1, pseudo_pos)
            ret.append(pos)
        return ret
    
    def calc_physical(self, axis, pseudo_pos):
        """**Pseudo Motor Controller API**. Overwrite is **MANDATORY**.
           Calculate physical motor position given the pseudo motor positions.
           
           :param axis: the motor role axis
           :type axis: int
           :param pseudo_pos: a sequence of pseudo motor positions
           :type pseudo_pos: sequence<float>
           :return: a motor position corresponding to the given axis motor role
           :rtype: float"""
        raise Exception("calc_physical must be redefined")
    
    def calc_pseudo(self, axis, physical_pos):
        """**Pseudo Motor Controller API**. Overwrite is **MANDATORY**.
           Calculate pseudo motor position given the physical motor positions
           
           :param axis: the pseudo motor role axis
           :type axis: int
           :param physical_pos: a sequence of motor positions
           :type physical_pos: sequence<float>
           :return: a pseudo motor position corresponding to the given axis pseudo motor role
           :rtype: float"""
        raise Exception("calc_pseudo must be redefined")