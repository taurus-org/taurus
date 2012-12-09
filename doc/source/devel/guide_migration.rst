.. currentmodule:: sardana.pool.controller

.. _sardana-migration-guide:


===================================
Sardana migration guide
===================================

This chapter describes how to migrate different sardana components between the
different API versions.

How to migrate your macro code
===================================

API v0 -> v1
-------------

This chapter describes the necessary steps to fully migrate your macros
from *API v0* ( sardana 0.x ) to *API v1* ( sardana 1.x )

Mandatory changes
"""""""""""""""""

The following are the 2 necessary changes to make your macros work in
sardana *API v1*:

1. from::
        
        from macro import Macro, Type, Table, List
    
   to::
        
        from sardana.macroserver.macro import Macro, Type, Table, List

2. Parameter type ``Type.Motor`` should be changed ``Type.Moveable``.
   In **v0** the `Motor` meant any motor (including physical motor, pseudo
   motor). In **v1**, for consistency, `Motor` means only physical motor
   and `Moveable` means all moveable elements (including physical motor, pseudo
   motor).

New features in API v1
"""""""""""""""""""""""

This chapter is a summary of all new features in *API v1*.

1. Macros can now be functions(see :ref:`sardana-macros-howto`).

How to migrate your controller code
===================================

API v0 -> v1
-------------

This chapter describes the necessary steps to fully migrate your controller
from *API v0* ( sardana 0.x ) to *API v1* ( sardana 1.x )

Mandatory changes
"""""""""""""""""

The following are the 2 necessary changes to make your controller work in
sardana *API v1*:

1. from::
   
       import pool
       from pool import <ControllerClass>/PoolUtil
   
   to::
   
       from sardana import pool
       from sardana.pool import PoolUtil
       from sardana.pool.controller import <ControllerClass>
    
2. change contructor from::

       def __init__(self, inst, props):
           code
       
   to::
   
       def __init__(self, inst, props, *args, **kwargs):
           MotorController.__init__(self, inst, props, *args, **kwargs)
           code

   (and don't forget to call the super class constructor also with args
   and kwargs).

The following change is not mandatory but is necessary in order for your
controller to be recognized by the pool to be a *API v1* controller:

3. _log member changed from :class:`logging.Logger` to 
   :class:`taurus.core.util.Logger`. This means that you need to change code
   from::
   
        self._log.setLevel(logging.INFO)
    
   to::
        
        self._log.setLogLevel(logging.INFO)
    
   or::
    
        self._log.setLogLevel(taurus.Info)
    
   since taurus.Info == logging.INFO.
    

Optional changes
""""""""""""""""

The following changes are not necessary to make your controller work. The 
*API v1* supports the *API v0* on these matters.

1. **class members**:
  
  #. from: :attr:`~Controller.class_prop` to: :attr:`~Controller.ctrl_properties`
  #. from: :attr:`~Controller.ctrl_extra_attributes` to: :attr:`~Controller.axis_attributes`
  #. new feature in *API v1*: :attr:`~Controller.ctrl_attributes`

3. **data types**:

    #. :meth:`~Controller.StateOne` **return type**: Previously
       :meth:`~Controller.StateOne` had to return a member of 
       :class:`PyTango.DevState`. Now it **can** instead return a member of
       :class:`~sardana.sardanadefs.State`. This eliminates the need to import
       :mod:`PyTango`.
    #. In *API v0* class member (like :attr:`~Controller.ctrl_extra_attributes`)
       value for key *type* had to be a string (like 'PyTango.DevString' or
       'PyTango.DevDouble'). Now they can be a python type (like str or float).
       Please check :ref:`sardana-controller-data-type` for more information.

4. **generic controller method names**:

    #. from: :meth:`~Controller.GetPar` to: :meth:`~Controller.GetAxisPar`
    #. from: :meth:`~Controller.SetPar` to: :meth:`~Controller.SetAxisPar`
    #. from: :meth:`~Controller.GetExtraAttributePar` to: :meth:`~Controller.GetAxisExtraPar`
    #. from: :meth:`~Controller.SetExtraAttributePar` to: :meth:`~Controller.SetAxisExtraPar`
    #. new feature in *API v1*: :meth:`~Controller.GetCtrlPar`, :meth:`~Controller.SetCtrlPar`
    #. new feature in *API v1*: :meth:`~Stopable.AbortAll` (has default 
       implementation which calls :meth:`~Stopable.AbortOne` for each axis)

5. **pseudo motor controller method names**:

    #. from: :meth:`~PseudoMotorController.calc_pseudo` to: :meth:`~PseudoMotorController.CalcPseudo`
    #. from: :meth:`~PseudoMotorController.calc_physical` to: :meth:`~PseudoMotorController.CalcPhysical`
    #. from: :meth:`~PseudoMotorController.calc_all_pseudo` to: :meth:`~PseudoMotorController.CalcAllPseudo`
    #. from: :meth:`~PseudoMotorController.calc_all_physical` to: :meth:`~PseudoMotorController.CalcAllPhysical`
    #. new feature in *API v1*: :meth:`~PseudoMotorController.GetMotor`
    #. new feature in *API v1*: :meth:`~PseudoMotorController.GetPseudoMotor`

New features in API v1
"""""""""""""""""""""""

This chapter is a summary of all new features in *API v1*.

*New controller features:*

1. All Controllers now have a :attr:`~Controller.ctrl_attributes` class member
   to define extra controller attributes (and new methods:
   :meth:`~Controller.GetCtrlPar`, :meth:`~Controller.SetCtrlPar`)
2. For :attr:`~Controller.ctrl_properties`, :attr:`~Controller.axis_attributes`
   and :attr:`~Controller.ctrl_extra_attributes`:
    
   - new (more pythonic) syntax. Old syntax is still supported:
       - can replace data type strings for python type ('PyTango.DevDouble' -> float)
       - Default behavior. Example: before data access needed to be described explicitly.
         Now it is read-write by default.
       - support for 2D
       - new keys 'fget' and 'fset' override default method calls
3. no need to import :mod:`PyTango` (:meth:`~Controller.StateOne` can return
   sardana.State.On instead of PyTango.DevState.ON)
4. PseudoMotorController has new :meth:`~PseudoMotorController.GetMotor` and 
   :meth:`~PseudoMotorController.GetPseudoMotor`
5. new :meth:`~Stopable.AbortAll` (with default implementation which calls
   :meth:`~Stopable.AbortOne` for each axis)
6. new :meth:`~Stopable.StopOne` (with default implementation which calls
   :meth:`~Stopable.AbortOne`)
7. new :meth:`~Stopable.StopAll` (with default implementation which calls
   :meth:`~Stopable.StoptOne` for each axis)
8. new :meth:`~Controller.GetAxisAttributes` allows features like:
    1. per axis customized dynamic attributes
    2. Basic interface (example: motor without velocity or acceleration)
    3. Discrete motor (declare position has an integer instead of a float).
       No need for IORegisters anymore
9. New :class:`~MotorController` constants:
    - :class:`~MotorController.HomeLimitSwitch`;
    - :class:`~MotorController.UpperLimitSwitch`;
    - :class:`~MotorController.LowerLimitSwitch`

*New acquisition features:*

1. Measurement group has a new *Configuration* attribute which contains the full
   description of the experiment in JSON format

*New Tango API features:*

1. Controllers are now Tango devices
2. Pool has a default PoolPath (points to <pool install dir>/poolcontrollers)
3. Create* commands can receive JSON object or an old style list of parameters
4. new CreateElement command (can replace CreateMotor, CreateExpChannel, etc)
5. Pool Abort command: aborts all elements (non pseudo elements)
6. Pool Stop command: stops all elements (non pseudo elements)
7. Controller Abort command: aborts all controller elements
8. Controller Stop command: stops all controller elements
9. Controllers have a LogLevel attribute which allows remote python logging
   management

*Others:*

1. Pool device is a python device :-)
2. many command line parameters help logging, debugging
