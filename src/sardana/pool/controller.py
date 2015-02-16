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

"""This module contains the definition of the Controller base classes"""

__all__ = ["DataAccess", "SardanaValue", "Type", "Access", "Description",
           "DefaultValue", "FGet", "FSet",
           "Memorized", "MemorizedNoInit", "NotMemorized", "MaxDimSize",
           "Controller", "Readable", "Startable", "Stopable", "Loadable",
           "MotorController", "CounterTimerController", "ZeroDController",
           "OneDController", "TwoDController",
           "PseudoMotorController", "IORegisterController"]

__docformat__ = 'restructuredtext'

import copy

from taurus.core.taurushelper import getLogLevel
from taurus.core.util.log import Logger

from sardana import DataAccess
from sardana.sardanavalue import SardanaValue
from sardana.pool.pooldefs import ControllerAPI, AcqTriggerType, AcqMode


#: Constant data type (to be used as a *key* in the definition of
#: :attr:`~Controller.axis_attributes` or :attr:`~Controller.ctrl_attributes`)
Type = 'type'

#: Constant data access (to be used as a *key* in the definition of
#: :attr:`~Controller.axis_attributes` or :attr:`~Controller.ctrl_attributes`)
Access = 'r/w type'

#: Constant description (to be used as a *key* in the definition of
#: :attr:`~Controller.axis_attributes` or :attr:`~Controller.ctrl_attributes`)
Description = 'description'

#: Constant default value (to be used as a *key* in the definition of
#: :attr:`~Controller.axis_attributes` or :attr:`~Controller.ctrl_attributes`)
DefaultValue = 'defaultvalue'

#: Constant for getter function (to be used as a *key* in the definition of
#: :attr:`~Controller.axis_attributes` or :attr:`~Controller.ctrl_attributes`)
FGet = "fget"

#: Constant for setter function (to be used as a *key* in the definition of
#: :attr:`~Controller.axis_attributes` or :attr:`~Controller.ctrl_attributes`)
FSet = "fset"

#: Constant memorize (to be used as a *key* in the definition of
#: :attr:`~Controller.axis_attributes` or :attr:`~Controller.ctrl_attributes`)
#: Possible values for this key are :obj:`Memorized`, :obj:`MemorizedNoInit`
#: and :obj:`NotMemorized`
Memorize = "memorized"

#: Constant memorized (to be used as a *value* in the :obj:`Memorize` field 
#: definition in :attr:`~Controller.axis_attributes` or 
#: :attr:`~Controller.ctrl_attributes`)
Memorized = "true"

#: Constant memorize but not write at initialization (to be used as a *value*
#: in the :obj:`Memorize` field definition in
#: :attr:`~Controller.axis_attributes` or :attr:`~Controller.ctrl_attributes`)
MemorizedNoInit = "true_without_hard_applied"

#: Constant not memorize (to be used as a *value*
#: in the :obj:`Memorize` field definition in
#: :attr:`~Controller.axis_attributes` or :attr:`~Controller.ctrl_attributes`)
NotMemorized = "false"

#: Constant MaxDimSize (to be used as a *key* in the definition of
#: :attr:`~Controller.axis_attributes` or :attr:`~Controller.ctrl_attributes`)
MaxDimSize = "maxdimsize"


class Controller(object):
    """Base controller class. Do **NOT** inherit from this class directly
    
    :param str inst: controller instance name
    :param dict props: a dictionary containning pairs of property name,
                       property value
    :arg args: 
    :keyword kwargs:"""

    #: .. deprecated:: 1.0
    #:     use :attr:`~Controller.ctrl_properties` instead
    class_prop = {}

    #: A sequence of :obj:`str` representing the controller features
    ctrl_features = []

    #: .. deprecated:: 1.0
    #:     use :attr:`~Controller.axis_attributes` instead
    ctrl_extra_attributes = {}

    #: A :class:`dict` containing controller properties where:
    #:
    #: - key : (:obj:`str`) controller property name
    #: - value : :class:`dict` with with three :obj:`str` keys ("type",
    #:   "description" and "defaultvalue" case insensitive):
    #:
    #:     - for :obj:`Type`, value is one of the values described in
    #:       :ref:`sardana-controller-data-type`
    #:
    #:     - for :obj:`Description`, value is a :obj:`str` description of the
    #:       property.
    #:       if is not given it defaults to empty string.
    #:
    #:     - for :obj:`DefaultValue`, value is a python object or None if no
    #:       default value exists for the property.
    #: 
    #: Example::
    #:
    #:     from sardana.pool.controller import MotorController, \
    #:         Type, Description, DefaultValue
    #: 
    #:     class MyCtrl(MotorController):
    #:          
    #:         ctrl_properties = \
    #:         {
    #:             'host' : { Type : str,
    #:                        Description : "host name" },
    #:             'port' : { Type : int, 
    #:                        Description : "port number",
    #:                        DefaultValue: 5000 }
    #:         }
    #:
    ctrl_properties = {}

    #: A :class:`dict` containning controller extra attributes where:
    #:
    #: - key : (:obj:`str`) controller attribute name
    #: - value : :class:`dict` with :obj:`str` possible keys: "type",
    #:   "r/w type", "description", "fget", "fset" and "maxdimsize"
    #:   (case insensitive):
    #:
    #:     - for :obj:`Type`, value is one of the values described in
    #:       :ref:`sardana-controller-data-type`
    #:
    #:     - for :obj:`Access`, value is one of 
    #:       :obj:`~sardana.sardanadefs.DataAccess` ("read" or "read_write"
    #:       (case insensitive) strings are also accepted) [default: ReadWrite]
    #:
    #:     - for :obj:`Description`, value is a :obj:`str` description of the
    #:       attribute [default: "" (empty string)]
    #:
    #:     - for :obj:`FGet`, value is a :obj:`str` with the method name for
    #:       the attribute getter [default: "get"<controller attribute name>]
    #:
    #:     - for :obj:`FSet`, value is a :obj:`str` with the method name for
    #:       the attribute setter. [default, if :obj:`Access` = "read_write":
    #:       "set"<controller attribute name>]
    #:
    #:     - for :obj:`DefaultValue`, value is a python object or None if no
    #:       default value exists for the attribute. If given, the attribute is
    #:       set when the controller is first created.
    #:
    #:     - for :obj:`Memorize`, value is a :obj:`str` with possible values:
    #:       :obj:`Memorized`, :obj:`MemorizedNoInit` and
    #:       :obj:`NotMemorized` [default: :obj:`Memorized`]
    #:
    #:       .. versionadded:: 1.1
    #:
    #:     - for :obj:`MaxDimSize`, value is a :obj:`tuple` with possible values:
    #:         - for scalar **must** be an empty tuple ( () or [] )
    #:           [default: ()]
    #:         - for 1D arrays a sequence with one value (example: (1024,))
    #:           [default: (2048,)]
    #:         - for 1D arrays a sequence with two values (example: (1024, 1024))
    #:           [default: (2048, 2048)]
    #:
    #:       .. versionadded:: 1.1
    #:
    #: .. versionadded:: 1.0
    #: 
    #: Example::
    #:      
    #:     from sardana.pool.controller import PseudoMotorController, \
    #:         Type, Description, DefaultValue, DataAccess
    #: 
    #:     class HKLCtrl(PseudoMotorController):
    #:          
    #:         ctrl_attributes = \
    #:         {
    #:             'ReflectionMatrix' : { Type : ( (float,), ),
    #:                                    Description : "The reflection matrix",
    #:                                    Access : DataAccess.ReadOnly,
    #:                                    FGet : 'getReflectionMatrix', },    
    #:         }
    #:         
    #:         def getReflectionMatrix(self):
    #:             return ( (1.0, 0.0), (0.0, 1.0) )
    ctrl_attributes = {}

    #: A :class:`dict` containning controller extra attributes for each axis
    #: where:
    #:
    #: - key : (:obj:`str`) axis attribute name
    #: - value : :class:`dict` with three :obj:`str` keys
    #:   ("type", "r/w type", "description" case insensitive):
    #:
    #:     - for :obj:`Type`, value is one of the values described in
    #:       :ref:`sardana-controller-data-type`
    #:
    #:     - for :obj:`Access`, value is one of 
    #:       :obj:`~sardana.sardanadefs.DataAccess` ("read" or "read_write"
    #:       (case insensitive) strings are also accepted)
    #:
    #:     - for :obj:`Description`, value is a :obj:`str` description of the
    #:       attribute
    #:
    #:     - for :obj:`DefaultValue`, value is a python object or None if no
    #:       default value exists for the attribute. If given, the attribute is
    #:       set when the axis is first created.
    #:
    #:     - for :obj:`Memorize`, value is a :obj:`str` with possible values:
    #:       :obj:`Memorized`, :obj:`MemorizedNoInit` and
    #:       :obj:`NotMemorized` [default: :obj:`Memorized`]
    #:
    #:       .. versionadded:: 1.1
    #:
    #:     - for :obj:`MaxDimSize`, value is a :obj:`tuple` with possible values:
    #:         - for scalar **must** be an empty tuple ( () or [] )
    #:           [default: ()]
    #:         - for 1D arrays a sequence with one value (example: (1024,))
    #:           [default: (2048,)]
    #:         - for 1D arrays a sequence with two values (example: (1024, 1024))
    #:           [default: (2048, 2048)]
    #:
    #:       .. versionadded:: 1.1
    #:
    #: .. versionadded:: 1.0
    #: 
    #: Example::
    #:      
    #:     from sardana.pool.controller import MotorController, \
    #:         Type, Description, DefaultValue, DataAccess
    #: 
    #:     class MyMCtrl(MotorController):
    #:          
    #:         axis_attributes = \
    #:         {
    #:             'EncoderSource' : { Type : str,
    #:                                 Description : 'motor encoder source', },
    #:         }
    #:         
    #:         def getAxisPar(self, axis, name):
    #:             name = name.lower()
    #:             if name == 'encodersource':
    #:                 return self._encodersource[axis]
    #:         
    #:         def setAxisPar(self, axis, name, value):
    #:             name = name.lower()
    #:             if name == 'encodersource':
    #:                 self._encodersource[axis] = value
    axis_attributes = {}

    #: A :class:`dict` containing the standard attributes present on each axis
    #: device
    standard_axis_attributes = {}

    #: A :obj:`str` representing the controller gender
    gender = None

    #: A :obj:`str` representing the controller model name
    model = 'Generic'

    #: A :obj:`str` representing the controller organization
    organization = 'Sardana team'

    #: A :obj:`str` containning the path to the image file
    image = None

    #: A :obj:`str` containning the path to the image logo file
    logo = None
    
    def __init__(self, inst, props, *args, **kwargs):
        self._inst_name = inst
        self._log = Logger("Controller.%s" % inst)
        self._log.log_obj.setLevel(getLogLevel())
        self._args = args
        self._kwargs = kwargs
        self._api_version = self._findAPIVersion()
        for prop_name, prop_value in props.items():
            setattr(self, prop_name, prop_value)

    def _findAPIVersion(self):
        """*Internal*. By default return the Pool Controller API
        version of the pool where the controller is running"""
        return ControllerAPI

    def _getPoolController(self):
        """*Internal*."""
        if hasattr(self, '_kwargs'):
            kw = self._kwargs
            if kw is not None:
                ctrl_wr = kw.get('pool_controller')
                if ctrl_wr is not None:
                    return ctrl_wr()

    def AddDevice(self, axis):
        """**Controller API**. Override if necessary. Default implementation
        does nothing.

        :param int axis: axis number"""
        pass

    def DeleteDevice(self, axis):
        """**Controller API**. Override if necessary. Default implementation
        does nothing.

        :param int axis: axis number"""
        pass

    @property
    def inst_name(self):
        """**Controller API**. The controller instance name.

        .. deprecated:: 1.0
            use :meth:`~Controller.GetName` instead"""
        return self._inst_name

    def GetName(self):
        """**Controller API**. The controller instance name.

        :return: the controller instance name
        :rtype: str

        .. versionadded:: 1.0"""
        return self._inst_name

    def GetAxisName(self, axis):
        """**Controller API**. The axis name.

        :return: the axis name
        :rtype: str

        .. versionadded:: 1.0"""
        ctrl = self._getPoolController()
        if ctrl is not None:
            return ctrl.get_element(axis=axis).name
        return str(axis)

    def PreStateAll(self):
        """**Controller API**. Override if necessary.
        Called to prepare a read of the state of all axis.
        Default implementation does nothing."""
        pass

    def PreStateOne(self, axis):
        """**Controller API**. Override if necessary.
        Called to prepare a read of the state of a single axis.
        Default implementation does nothing.

        :param int axis: axis number"""
        pass

    def StateAll(self):
        """**Controller API**. Override if necessary.
        Called to read the state of all selected axis.
        Default implementation does nothing."""
        pass

    def StateOne(self, axis):
        """**Controller API**. Override is MANDATORY.
        Called to read the state of one axis.
        Default implementation raises :exc:`NotImplementedError`."""
        raise NotImplementedError("StateOne must be defined in the controller")

    #def SetCtrlPar(self, unit, parameter, value):
    def SetCtrlPar(self, parameter, value):
        """**Controller API**. Override if necessary.
        Called to set a parameter with a value. Default implementation sets
        this object member named '_'+parameter with the given value.

        .. versionadded:: 1.0"""
        setattr(self, '_' + parameter, value)

    #def GetCtrlPar(self, unit, parameter):
    def GetCtrlPar(self, parameter):
        """**Controller API**. Override if necessary.
        Called to set a parameter with a value. Default implementation returns
        the value contained in this object's member named '_'+parameter.

        .. versionadded:: 1.0"""
        return getattr(self, '_' + parameter)

    #def SetAxisPar(self, unit, axis, parameter, value):
    def SetAxisPar(self, axis, parameter, value):
        """**Controller API**. Override is MANDATORY.
        Called to set a parameter with a value on the given axis. Default
        implementation calls deprecated :meth:`~Controller.SetPar` which, by
        default, raises :exc:`NotImplementedError`.

        .. versionadded:: 1.0"""
        return self.SetPar(axis, parameter, value)

    #def GetAxisPar(self, unit, axis, parameter):
    def GetAxisPar(self, axis, parameter):
        """**Controller API**. Override is MANDATORY.
        Called to get a parameter value on the given axis. Default
        implementation calls deprecated :meth:`~Controller.GetPar` which, by
        default, raises :exc:`NotImplementedError`.

        .. versionadded:: 1.0"""
        return self.GetPar(axis, parameter)

    def SetAxisExtraPar(self, axis, parameter, value):
        """**Controller API**. Override if necessary.
        Called to set a parameter with a value on the given axis. Default
        implementation calls deprecated :meth:`~Controller.SetExtraAttributePar`
        which, by default, raises :exc:`NotImplementedError`.

        .. versionadded:: 1.0"""
        return self.SetExtraAttributePar(axis, parameter, value)

    def GetAxisExtraPar(self, axis, parameter):
        """**Controller API**. Override if necessary.
        Called to get a parameter value on the given axis. Default
        implementation calls deprecated :meth:`~Controller.GetExtraAttributePar`
        which, by default, raises :exc:`NotImplementedError`.

        .. versionadded:: 1.0"""
        return self.GetExtraAttributePar(axis, parameter)

    def SetPar(self, axis, parameter, value):
        """**Controller API**. Called to set a parameter with a value on
        the given axis. Default implementation raises
        :exc:`NotImplementedError`.

        .. deprecated:: 1.0
            use :meth:`~Controller.SetAxisPar` instead"""
        raise NotImplementedError("SetAxisPar must be defined in the "
                                  "controller")

    def GetPar(self, axis, parameter):
        """**Controller API**. Called to get a parameter value on the given
        axis. Default implementation raises :exc:`NotImplementedError`.

        .. deprecated:: 1.0
            use :meth:`~Controller.GetAxisPar` instead"""
        raise NotImplementedError("GetAxisPar must be defined in the "
                                  "controller")

    def SetExtraAttributePar(self, axis, parameter, value):
        """**Controller API**. Called to set a parameter with a value on the
        given axis. Default implementation raises :exc:`NotImplementedError`.

        .. deprecated:: 1.0
            use :meth:`~Controller.SetAxisExtraPar` instead"""
        raise NotImplementedError("SetAxisExtraPar must be defined in the "
                                  "controller")

    def GetExtraAttributePar(self, axis, parameter):
        """**Controller API**. Called to get a parameter value on the given
        axis. Default implementation raises :exc:`NotImplementedError`.

        .. deprecated:: 1.0
            use :meth:`~Controller.GetAxisExtraPar` instead"""
        raise NotImplementedError("GetAxisExtraPar must be defined in the "
                                  "controller")

    def GetAxisAttributes(self, axis):
        """**Controller API**. Override if necessary.
        Returns a dictionary of all attributes per axis.
        Default implementation returns a new :class:`dict` with the standard
        attributes plus the :attr:`~Controller.axis_attributes`

        :param int axis: axis number
        :return: a dict containing attribute information as defined in
                 :attr:`~Controller.axis_attributes`

        .. versionadded:: 1.0"""
        ret = copy.deepcopy(self.standard_axis_attributes)
        axis_attrs = copy.deepcopy(self.axis_attributes)
        old_axis_attrs = copy.deepcopy(self.ctrl_extra_attributes)
        ret.update(axis_attrs)
        ret.update(old_axis_attrs)
        return ret

    def SendToCtrl(self, stream):
        """**Controller API**. Override if necessary.
        Sends a string to the controller.
        Default implementation raises :exc:`NotImplementedError`.

        :param str stream: stream to be sent
        :return: any relevant information e.g. response of the controller
        :rtype: str"""
        raise NotImplementedError("SendToCtrl not implemented")


class Startable(object):
    """A Startable interface. A controller for which it's axis are 'startable'
    (like a motor, for example) should implement this interface

    .. note: Do not inherit directly from :class:`Startable`."""

    def PreStartAll(self):
        """**Controller API**. Override if necessary.
        Called to prepare a start of all axis (whatever pre-start means).
        Default implementation does nothing."""
        pass

    def PreStartOne(self, axis, value):
        """**Controller API**. Override if necessary.
        Called to prepare a start of the given axis (whatever pre-start means).
        Default implementation returns True.

        :param int axis: axis number
        :param float value: new value
        :return: True means a successfull pre-start or False for a failure
        :rtype: bool"""
        return True

    def StartOne(self, axis, value):
        """**Controller API**. Override if necessary.
        Called to do a start of the given axis (whatever start means).
        Default implementation raises :exc:`NotImplementedError`

        :param int axis: axis number
        :param float value: new value"""
        raise NotImplementedError("StartOne must be defined in the controller")

    def StartAll(self):
        """**Controller API**. Override is MANDATORY!
        Default implementation does nothing."""
        pass


class Stopable(object):
    """A Stopable interface. A controller for which it's axis are 'stoppable'
    (like a motor, for example) should implement this interface

    .. note: Do not inherit directly from :class:`Stopable`."""

    def AbortOne(self, axis):
        """**Controller API**. Override is MANDATORY!
        Default implementation raises :exc:`NotImplementedError`.
        Aborts one of the axis

        :param int axis: axis number"""
        raise NotImplementedError("AbortOne must be defined in te controller")

    def AbortAll(self):
        """**Controller API**. Override if necessary.
        Aborts all active axis of this controller. Default implementation
        calls :meth:`~Controller.AbortOne` on each active axis.

        .. versionadded:: 1.0"""
        exceptions = []
        axes = self._getPoolController().get_element_axis().keys()
        for axis in axes:
            try:
                self.AbortOne(axis)
            except:
                import sys
                exceptions.append(sys.exc_info())
        if len(exceptions) > 0:
            raise Exception(exceptions)

    def StopOne(self, axis):
        """**Controller API**. Override if necessary.
        Stops one of the axis.
        *This method is reserved for future implementation.*
        Default implementation calls :meth:`~Controller.AbortOne`.

        :param int axis: axis number

        .. versionadded:: 1.0"""
        self.AbortOne(axis)

    def StopAll(self):
        """**Controller API**. Override if necessary.
        Stops all active axis of this controller.
        *This method is reserved for future implementation.*
        Default implementation calls :meth:`~Controller.StopOne` on each
        active axis.

        .. versionadded:: 1.0"""
        exceptions = []
        axes = self._getPoolController().get_element_axis().keys()
        for axis in axes:
            try:
                self.StopOne(axis)
            except:
                import sys
                exceptions.append(sys.exc_info())
        if len(exceptions) > 0:
            raise Exception(exceptions)


class Readable(object):
    """A Readable interface. A controller for which it's axis are 'readable'
    (like a motor, counter or 1D for example) should implement this interface

    .. note: Do not inherit directly from Readable."""

    def PreReadAll(self):
        """**Controller API**. Override if necessary.
        Called to prepare a read of the value of all axis.
        Default implementation does nothing."""
        pass

    def PreReadOne(self, axis):
        """**Controller API**. Override if necessary.
        Called to prepare a read of the value of a single axis.
        Default implementation does nothing.

        :param int axis: axis number"""
        pass

    def ReadAll(self):
        """**Controller API**. Override if necessary.
        Called to read the value of all selected axis
        Default implementation does nothing."""
        pass

    def ReadOne(self, axis):
        """**Controller API**. Override is MANDATORY!
        Default implementation raises :exc:`NotImplementedError`

        :param int axis: axis number
        :return: the axis value
        :rtype: object
        """
        raise NotImplementedError("ReadOne must be defined in the controller")


class Loadable(object):
    """A Loadable interface. A controller for which it's axis are 'loadable'
    (like a counter, 1D or 2D for example) should implement this interface

    .. note: Do not inherit directly from Loadable."""

    def PreLoadAll(self):
        """**Controller API**. Override if necessary.
        Called to prepare loading the integration time / monitor value.
        Default implementation does nothing."""
        pass

    def PreLoadOne(self, axis, value):
        """**Controller API**. Override if necessary.
        Called to prepare loading the master channel axis with the integration
        time / monitor value.
        Default implementation returns True.

        :param int axis: axis number
        :param float value: integration time /monitor value
        :return: True means a successfull PreLoadOne or False for a failure
        :rtype: bool"""
        return True

    def LoadAll(self):
        """**Controller API**. Override if necessary.
        Called to load the integration time / monitor value.
        Default implementation does nothing."""
        pass

    def LoadOne(self, axis, value):
        """**Controller API**. Override is MANDATORY!
        Called to load the integration time / monitor value.
        Default implementation raises :exc:`NotImplementedError`.
        
        :param int axis: axis number
        :param float value: integration time /monitor value"""
        raise NotImplementedError("LoadOne must be defined in the controller")


class MotorController(Controller, Startable, Stopable, Readable):
    """Base class for a motor controller. Inherit from this class to implement
    your own motor controller for the device pool.

    A motor controller should support these axis parameters:

        - acceleration
        - deceleration
        - velocity
        - base_rate
        - step_per_unit

    These parameters are configured through the
    :meth:`~Controller.GetAxisPar`/:meth:`~Controller.SetAxisPar`
    API (in version <1.0 the methods were called
    :meth:`~Controller.GetPar`/:meth:`~Controller.SetPar`. Default
    :meth:`~Controller.GetAxisPar` and
    :meth:`~Controller.SetAxisPar` still call
    :meth:`~Controller.GetPar` and :meth:`~Controller.SetPar`
    respectively in order to maintain backward compatibility).
    """

    #: A constant representing no active switch.
    NoLimitSwitch = 0

    #: A constant representing an active *home* switch.
    #: You can *OR* two or more switches together. For example, to say both
    #: upper and lower limit switches are active::
    #:
    #:    limit_switches = self.HomeLimitSwitch | self.LowerLimitSwitch
    HomeLimitSwitch = 1

    #: A constant representing an active *upper limit* switch.
    #: You can *OR* two or more switches together. For example, to say both
    #: upper and lower limit switches are active::
    #:
    #:    limit_switches = self.UpperLimitSwitch | self.LowerLimitSwitch
    UpperLimitSwitch = 2

    #: A constant representing an active *lower limit* switch.
    #: You can *OR* two or more switches together. For example, to say both
    #: upper and lower limit switches are active::
    #:
    #:    limit_switches = self.UpperLimitSwitch | self.LowerLimitSwitch
    LowerLimitSwitch = 4

    #: A :class:`dict` containing the standard attributes present on each axis
    #: device
    standard_axis_attributes = {
        'Position'       : { 'type' : float,
                             'description' : 'Position', },
        'DialPosition'   : { 'type' : float,
                             'description' : 'Dial Position', },
        'Offset'         : { 'type' : float,
                             'description' : 'Offset', },
        'Sign'           : { 'type' : float,
                             'description' : 'Sign', },
        'Step_per_unit'  : { 'type' : float,
                             'description' : 'Steps per unit', },
        'Acceleration'   : { 'type' : float,
                             'description' : 'Acceleration time (s)', },
        'Deceleration'   : { 'type' : float,
                             'description' : 'Deceleration time (s)', },
        'Base_rate'      : { 'type' : float,
                             'description' : 'Base rate', },
        'Velocity'       : { 'type' : float,
                             'description' : 'Velocity', },
        'Backlash'       : { 'type' : float,
                             'description' : 'Backlash', },
        'Limit_switches' : { 'type' : (bool,),
                             'description' : "This attribute is the motor "\
                              "limit switches state. It's an array with 3 \n"\
                              "elements which are:\n"\
                              "0 - The home switch\n"\
                              "1 - The upper limit switch\n"\
                              "2 - The lower limit switch\n"\
                              "False means not active. True means active", },
    }
    standard_axis_attributes.update(Controller.standard_axis_attributes)

    #: A :obj:`str` representing the controller gender
    gender = 'Motor controller'

    def GetAxisAttributes(self, axis):
        """**Motor Controller API**. Override if necessary.
        Returns a sequence of all attributes per axis.
        Default implementation returns a :class:`dict` containning:

        - Position
        - DialPosition
        - Offset
        - Sign
        - Step_per_unit
        - Acceleration
        - Deceleration
        - Base_rate
        - Velocity
        - Backlash
        - Limit_switches

        plus all attributes contained in :attr:`~Controller.axis_attributes`

        .. note::
            Normally you don't need to Override this method. You just implement
            the class member :attr:`~Controller.axis_attributes`. Typically,
            you will need to Override this method in two cases:

                - certain axes contain a different set of extra attributes
                  which cannot be simply defined in
                  :attr:`~Controller.axis_attributes`
                - some axes (or all) don't implement a set of standard
                  moveable parameters (ex.: if a motor controller is created to
                  control a power supply, it may have a position (current) and
                  a velocity (ramp speed) but it may not have acceleration)

        :param int axis: axis number
        :return: a dict containing attribute information as defined in
                 :attr:`~Controller.axis_attributes`

        .. versionadded:: 1.0"""
        return Controller.GetAxisAttributes(self, axis)

    def DefinePosition(self, axis, position):
        """**Motor Controller API**. Override is recommended!
           This method is called to load a new motor position.
           Default implementation does nothing.
        """
#        raise NotImplementedError("DefinePosition must be defined in the "
#                                  "controller")
        pass


class CounterTimerController(Controller, Readable, Startable, Stopable, Loadable):
    """Base class for a counter/timer controller. Inherit from this class to
    implement your own counter/timer controller for the device pool.

    A counter timer controller should support these controller parameters:

        - timer
        - monitor
        - trigger_type"""

    #: A :class:`dict` containing the standard attributes present on each axis
    #: device
    standard_axis_attributes = {
        'Value'       : { 'type' : float,
                          'description' : 'Value', },
    }
    standard_axis_attributes.update(Controller.standard_axis_attributes)

    #: A :obj:`str` representing the controller gender
    gender = 'Counter/Timer controller'

    def __init__(self, inst, props, *args, **kwargs):
        Controller.__init__(self, inst, props, *args, **kwargs)
        self._timer = None
        self._monitor = None
        self._master = None
        self._trigger_type = AcqTriggerType.Unknown

    def PreStartAllCT(self):
        """**Counter/Timer Controller API**. Override if necessary.
        Called to prepare an acquisition of all selected axis.
        Default implementation does nothing.

        .. deprecated:: 1.0
            use :meth:`~CounterTimerController.PreStartAll` instead"""
        pass

    def PreStartOneCT(self, axis):
        """**Counter/Timer Controller API**. Override if necessary.
        Called to prepare an acquisition a single axis.
        Default implementation returns True.

        :param int axis: axis number
        :return: True means a successfull PreStartOneCT or False for a failure
        :rtype: bool

        .. deprecated:: 1.0
            use :meth:`~CounterTimerController.PreStartOne` instead"""
        return True

    def StartOneCT(self, axis):
        """**Counter/Timer Controller API**. Override if necessary.
        Called to start an acquisition of a selected axis.
        Default implementation does nothing.

        :param int axis: axis number

        .. deprecated:: 1.0
            use :meth:`~CounterTimerController.StartOne` instead"""
        pass

    def StartAllCT(self):
        """**Counter/Timer Controller API**. Override is MANDATORY!
        Called to start an acquisition of a selected axis.
        Default implementation raises :exc:`NotImplementedError`.

        .. deprecated:: 1.0
            use :meth:`~CounterTimerController.StartAll` instead"""
        raise NotImplementedError("StartAll must be defined in the "
                                  "controller")

    def PreStartAll(self):
        """**Controller API**. Override if necessary.
        Called to prepare a write of the position of all axis. Default
        implementation calls deprecated
        :meth:`~CounterTimerController.PreStartAllCT` which, by default, does
        nothing.

        .. versionadded:: 1.0"""
        return self.PreStartAllCT()

    def PreStartOne(self, axis, value=None):
        """**Controller API**. Override if necessary.
        Called to prepare a write of the position of a single axis.
        Default implementation calls deprecated
        :meth:`~CounterTimerController.PreStartOneCT` which, by default,
        returns True.

        :param int axis: axis number
        :param float value: the value
        :return: True means a successfull pre-start or False for a failure
        :rtype: bool

        .. versionadded:: 1.0"""
        return self.PreStartOneCT(axis)

    def StartOne(self, axis, value=None):
        """**Controller API**. Override if necessary.
        Called to write the position of a selected axis. Default
        implementation calls deprecated
        :meth:`~CounterTimerController.StartOneCT` which, by default, does
        nothing.

        :param int axis: axis number
        :param float value: the value"""
        return self.StartOneCT(axis)

    def StartAll(self):
        """**Controller API**. Override is MANDATORY!
        Default implementation calls deprecated
        :meth:`~CounterTimerController.StartAllCT` which, by default, raises
        :exc:`NotImplementedError`."""
        return self.StartAllCT()


class ZeroDController(Controller, Readable, Stopable):
    """Base class for a 0D controller. Inherit from this class to
    implement your own 0D controller for the device pool."""

    #: A :class:`dict` containing the standard attributes present on each axis
    #: device
    standard_axis_attributes = {
        'Value'       : { 'type' : float,
                          'description' : 'Value', },
    }
    standard_axis_attributes.update(Controller.standard_axis_attributes)
    
    #: A :obj:`str` representing the controller gender
    gender = '0D controller'

    def AbortOne(self, axis):
        """This method is not executed by the system.
        Default implementation does nothing.

        :param int axis: axis number"""
        pass


class OneDController(Controller, Readable, Startable, Stopable, Loadable):
    """Base class for a 1D controller. Inherit from this class to
    implement your own 1D controller for the device pool.
    
    .. versionadded:: 1.2"""

    standard_axis_attributes = {
        'Value'       : { 'type' : (float,),
                          'description' : 'Value',
                          'maxdimsize' : (16*1024,) },
    }
    standard_axis_attributes.update(Controller.standard_axis_attributes)

    #: A :obj:`str` representing the controller gender
    gender = '1D controller'
        
    def GetAxisPar(self, axis, parameter):
        """**Controller API**. Override is MANDATORY.
        Called to get a parameter value on the given axis.
        If parameter == 'data_source', default implementation returns None, 
        meaning let sardana decide the proper URI for accessing the axis value. 
        Otherwise, default implementation calls deprecated
        :meth:`~Controller.GetPar` which, by default, raises
        :exc:`NotImplementedError`.

        .. versionadded:: 1.2"""
        if parameter.lower() == 'data_source':
            return None
        return self.GetPar(axis, parameter)


class TwoDController(Controller, Readable, Startable, Stopable, Loadable):
    """Base class for a 2D controller. Inherit from this class to
    implement your own 2D controller for the device pool."""

    standard_axis_attributes = {
        'Value'       : { 'type' : ((float,),),
                          'description' : 'Value',
                          'maxdimsize' : (4*1024, 4*1024) },
    }
    standard_axis_attributes.update(Controller.standard_axis_attributes)

    #: A :obj:`str` representing the controller gender
    gender = '2D controller'

    def GetAxisPar(self, axis, parameter):
        """**Controller API**. Override is MANDATORY.
        Called to get a parameter value on the given axis.
        If parameter == 'data_source', default implementation returns None, 
        meaning let sardana decide the proper URI for accessing the axis value. 
        Otherwise, default implementation calls deprecated
        :meth:`~Controller.GetPar` which, by default, raises
        :exc:`NotImplementedError`.

        .. versionadded:: 1.2"""
        if parameter.lower() == 'data_source':
            return None
        return self.GetPar(axis, parameter)


class PseudoController(Controller):
    """Base class for all pseudo controllers.

    .. note: Do not inherit directly from :class:`PseudoController`."""

    def _getElem(self, index_or_role, roles, local_cache, ids):
        """*Iternal*."""
        elem = local_cache.get(index_or_role)
        if elem is None:
            pool = self._getPoolController().pool
            if type(index_or_role) == int:
                index = index_or_role
                role = roles[index]
            else:
                role = index_or_role
                index = roles.index(role)
            motor_id = ids[index]
            elem = pool.get_element_by_id(motor_id)
            local_cache[index] = local_cache[role] = elem
        return elem


class PseudoMotorController(PseudoController):
    """Base class for a pseudo motor controller. Inherit from this class to
    implement your own pseudo motor controller for the device pool.

    Every Pseudo Motor implementation must be a subclass of this class.
    Current procedure for a correct implementation of a Pseudo Motor class:

    - mandatory:
        - define the class level attributes
          :attr:`~PseudoMotorController.pseudo_motor_roles`,
          :attr:`~PseudoMotorController.motor_roles`
        - write :meth:`~PseudoMotorController.CalcPseudo` method
        - write :meth:`~PseudoMotorController.CalcPhysical` method.
    - optional:
        - write :meth:`~PseudoMotorController.CalcAllPseudo` and
          :meth:`~PseudoMotorController.CalcAllPhysical` if great performance
          gain can be achived"""

    #: a sequence of strings describing the role of each pseudo motor axis in
    #: this controller
    pseudo_motor_roles = ()

    #: a sequence of strings describing the role of each motor in  this
    #: controller
    motor_roles = ()

    #: A :class:`dict` containing the standard attributes present on each axis
    #: device
    standard_axis_attributes = {
        'Position'       : { 'type' : float,
                             'description' : 'Position', },
    }

    #: A :obj:`str` representing the controller gender
    gender = 'Pseudo motor controller'
    
    def __init__(self, inst, props, *args, **kwargs):
        self.__motor_role_elements = {}
        self.__pseudo_motor_role_elements = {}
        PseudoController.__init__(self, inst, props, *args, **kwargs)

    def CalcAllPseudo(self, physical_pos, curr_pseudo_pos):
        """**Pseudo Motor Controller API**. Override if necessary.
           Calculates the positions of all pseudo motors that belong to the
           pseudo motor system from the positions of the physical motors.
           Default implementation does a loop calling
           :meth:`PseudoMotorController.calc_pseudo` for each pseudo motor role.

           :param sequence<float> physical_pos: a sequence containing physical
                                                motor positions
           :param sequence<float> curr_pseudo_pos: a sequence containing the
                                                   current pseudo motor
                                                   positions
           :return: a sequece of pseudo motor positions (one for each pseudo
                    motor role)
           :rtype: sequence<float>

           .. versionadded:: 1.0"""
        ret = []
        for i in range(len(self.pseudo_motor_roles)):
            ret.append(self.CalcPseudo(i+1, physical_pos, curr_pseudo_pos))
        return ret

    def CalcAllPhysical(self, pseudo_pos, curr_physical_pos):
        """**Pseudo Motor Controller API**. Override if necessary.
           Calculates the positions of all motors that belong to the pseudo
           motor system from the positions of the pseudo motors.
           Default implementation does a loop calling
           :meth:`PseudoMotorController.calc_physical` for each motor role.

           :param sequence<float> pseudo_pos: a sequence containing pseudo motor
                                              positions
           :param sequence<float> curr_physical_pos: a sequence containing the
                                                     current physical motor
                                                     positions
           :return: a sequece of motor positions (one for each motor role)
           :rtype: sequence<float>

           .. versionadded:: 1.0"""
        ret = []
        for i in range(len(self.motor_roles)):
            pos = self.CalcPhysical(i+1, pseudo_pos, curr_physical_pos)
            ret.append(pos)
        return ret

    def CalcPseudo(self, axis, physical_pos, curr_pseudo_pos):
        """**Pseudo Motor Controller API**. Override is **MANDATORY**.
           Calculate pseudo motor position given the physical motor positions

           :param int axis: the pseudo motor role axis
           :param sequence<float> physical_pos: a sequence containing motor
                                                positions
           :param sequence<float> curr_pseudo_pos: a sequence containing the
                                                   current pseudo motor
                                                   positions
           :return: a pseudo motor position corresponding to the given axis
                    pseudo motor role
           :rtype: float

           .. versionadded:: 1.0"""
        return self.calc_pseudo(axis, physical_pos)

    def CalcPhysical(self, axis, pseudo_pos, curr_physical_pos):
        """**Pseudo Motor Controller API**. Override is **MANDATORY**.
           Calculate physical motor position given the pseudo motor positions.

           :param axis: the motor role axis
           :type axis: int
           :param pseudo_pos: a sequence containing pseudo motor positions
           :type pseudo_pos: sequence<float>
           :param curr_physical_pos: a sequence containing the current physical
                                     motor positions
           :type curr_physical_pos: sequence<float>
           :return: a motor position corresponding to the given axis motor role
           :rtype: float

           .. versionadded:: 1.0"""
        return self.calc_physical(axis, pseudo_pos)

    def calc_all_pseudo(self, physical_pos):
        """**Pseudo Motor Controller API**. Override if necessary.
           Calculates the positions of all pseudo motors that belong to the
           pseudo motor system from the positions of the physical motors.
           Default implementation does a loop calling
           :meth:`PseudoMotorController.calc_pseudo` for each pseudo motor role.

           :param sequence<float> physical_pos: a sequence of physical motor
                                                positions
           :return: a sequece of pseudo motor positions (one for each pseudo
                    motor role)
           :rtype: sequence<float>

           .. deprecated:: 1.0
               implement :meth:`~PseudoMotorController.CalcAllPseudo` instead"""
        ret = []
        for i in range(len(self.pseudo_motor_roles)):
            ret.append(self.calc_pseudo(i+1, physical_pos))
        return ret


    def calc_all_physical(self, pseudo_pos):
        """**Pseudo Motor Controller API**. Override if necessary.
           Calculates the positions of all motors that belong to the pseudo
           motor system from the positions of the pseudo motors.
           Default implementation does a loop calling
           :meth:`PseudoMotorController.calc_physical` for each motor role.

           :param pseudo_pos: a sequence of pseudo motor positions
           :type pseudo_pos: sequence<float>
           :return: a sequece of motor positions (one for each motor role)
           :rtype: sequence<float>

           .. deprecated:: 1.0
               implement :meth:`~PseudoMotorController.CalcAllPhysical`
               instead"""
        ret = []
        for i in range(len(self.motor_roles)):
            pos = self.calc_physical(i+1, pseudo_pos)
            ret.append(pos)
        return ret

    def calc_pseudo(self, axis, physical_pos):
        """**Pseudo Motor Controller API**. Override is **MANDATORY**.
           Calculate pseudo motor position given the physical motor positions

           :param int axis: the pseudo motor role axis
           :param sequence<float> physical_pos: a sequence of motor positions
           :return: a pseudo motor position corresponding to the given axis
                    pseudo motor role
           :rtype: float

           .. deprecated:: 1.0
               implement :meth:`~PseudoMotorController.CalcPseudo` instead"""
        raise NotImplementedError("CalcPseudo must be defined in te controller")

    def calc_physical(self, axis, pseudo_pos):
        """**Pseudo Motor Controller API**. Override is **MANDATORY**.
           Calculate physical motor position given the pseudo motor positions.

           :param axis: the motor role axis
           :type axis: int
           :param pseudo_pos: a sequence of pseudo motor positions
           :type pseudo_pos: sequence<float>
           :return: a motor position corresponding to the given axis motor role
           :rtype: float

           .. deprecated:: 1.0
               implement :meth:`~PseudoMotorController.CalcPhysical` instead"""
        raise NotImplementedError("CalcPhysical must be defined in the "
                                  "controller")

    def GetMotor(self, index_or_role):
        """Returns the motor for a given role/index.

        .. warning::
            * Use with care: Executing motor methods can be dangerous!

            * Since the controller is built before any element (including
              motors), this method will **FAIL** when called from the controller
              constructor

        :param index_or_role: index number or role name
        :type index_or_role: int or str
        :return: Motor object for the given role/index
        :rtype: :class:`~sardana.pool.poolmotor.PoolMotor`"""
        return self._getElem(index_or_role, self.motor_roles,
                             self.__motor_role_elements,
                             self._kwargs['motor_ids'])

    def GetPseudoMotor(self, index_or_role):
        """Returns the pseudo motor for a given role/index.

        .. warning::
            * Use with care: Executing pseudo motor methods can be dangerous!

            * Since the controller is built before any element (including pseudo
              motors), this method will **FAIL** when called from the controller
              constructor

        :param index_or_role: index number or role name
        :type index_or_role: int or str
        :return: PseudoMotor object for the given role/index
        :rtype: :class:`~sardana.pool.poolpseudomotor.PoolPseudoMotor`"""
        dict_ids = self._getPoolController().get_element_ids()
        dict_axis = self._getPoolController().get_element_axis()
        pseudo_motor_ids = []
        for akey, aname in dict_axis.items():
            pseudo_motor_ids.append(dict_ids.keys()[dict_ids.values().index(aname)])
        return self._getElem(index_or_role, self.pseudo_motor_roles,
                             self.__pseudo_motor_role_elements,
                             pseudo_motor_ids)
#                             self._kwargs['pseudo_motor_roles'])


class PseudoCounterController(Controller):
    """Base class for a pseudo counter controller. Inherit from this class to
    implement your own pseudo counter controller for the device pool.

    Every Pseudo Counter implementation must be a subclass of this class.
    Current procedure for a correct implementation of a Pseudo Counter class:

    - mandatory:
        - define the class level attributes
          :attr:`~PseudoCounterController.counter_roles`,
        - write :meth:`~PseudoCounterController.Calc` method"""

    #: a sequence of strings describing the role of each pseudo counter axis in
    #: this controller
    pseudo_counter_roles = ()

    #: a sequence of strings describing the role of each counter in this
    #: controller
    counter_roles = ()

    #: A :class:`dict` containing the standard attributes present on each axis
    #: device
    standard_axis_attributes = {
        'Value'       : { 'type' : float,
                          'description' : 'Value', },
    }

    #: A :obj:`str` representing the controller gender
    gender = 'Pseudo counter controller'
    
    def Calc(self, axis, values):
        """**Pseudo Counter Controller API**. Override is **MANDATORY**.
           Calculate pseudo counter position given the counter values.

           :param int axis: the pseudo counter role axis
           :param sequence<float> values: a sequence containing current values
                                          of underlying elements
           :return: a pseudo counter value corresponding to the given axis
                    pseudo counter role
           :rtype: float

           .. versionadded:: 1.0"""
        return self.calc(axis, values)

    def calc(self, axis, values):
        """**Pseudo Counter Controller API**. Override is **MANDATORY**.
           Calculate pseudo counter value given the counter values.

           :param int axis: the pseudo counter role axis
           :param sequence<float> values: a sequence containing current values
                                          of underlying elements
           :return: a pseudo counter value corresponding to the given axis
                    pseudo counter role
           :rtype: float

           .. deprecated:: 1.0
               implement :meth:`~PseudoCounterController.Calc` instead"""
        raise NotImplementedError("Calc must be defined in te controller")

    def CalcAll(self, values):
        """**Pseudo Counter Controller API**. Override if necessary.
           Calculates all pseudo counter values from the values of counters.
           Default implementation does a loop calling
           :meth:`PseudoCounterController.Calc` for each pseudo counter role.

           :param sequence<float> values: a sequence containing current values
                                          of underlying elements
           :return: a sequece of pseudo counter values (one for each pseudo
                    counter role)
           :rtype: sequence<float>

           .. versionadded:: 1.2"""
        f, n = self.Calc, len(self.pseudo_counter_roles)
        return [ f(i+1, values) for i in range(n) ]


class IORegisterController(Controller, Readable):
    """Base class for a IORegister controller. Inherit from this class to
    implement your own IORegister controller for the device pool.
    """

    #: .. deprecated:: 1.0
    #:     use :attr:`~Controller.axis_attributes` instead
    predefined_values = ()

    #: A :class:`dict` containing the standard attributes present on each axis
    #: device
    standard_axis_attributes = {
        'Value'       : { 'type' : float,
                          'description' : 'Value', },
    }

    #: A :obj:`str` representing the controller gender
    gender = 'I/O register controller'
    
    def __init__(self, inst, props, *args, **kwargs):
        Controller.__init__(self, inst, props, *args, **kwargs)

    def WriteOne(self):
        """**IORegister Controller API**. Override if necessary."""
        pass

