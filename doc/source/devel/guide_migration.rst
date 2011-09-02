.. currentmodule:: sardana.pool

.. _sardana-migration-guide:


===================================
Sardana migration guide
===================================

This chapter describes how to migrate different sardana components between the
different API versions.

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
       from sardana.pool.controller import <ControllerClass>/PoolUtil

2. Make sure that in AddDevice/DeleteDevice you call the super class 
   :meth:`~Controller.AddDevice`/:meth:`~Controller.DeleteDevice`. Not doing so
   will prevent the default implementation of :meth:`~Controller.AbortAll` from
   work properly!

The following change is not mandatory but is necessary in order for your
controller to be recognized by the pool to be a *API v1* controller:

3. change contructor from::

       def __init__(self, inst, props)
       
   to::
   
       def __init__(self, inst, props, *args, **kwargs)

   (and don't forget to call the super class constructor also with args
   and kwargs).

Optional changes
""""""""""""""""

The following changes are not necessary to make your controller work. The 
*API v1* supports the *API v0* on these matters.

1. **class members**:
  
  #. from: :attr:`~Controller.class_prop` to: :attr:`~Controller.ctrl_properties`
  #. from: :attr:`~Controller.ctrl_extra_attributes` to: :attr:`~Controller.axis_attributes`
  #. new feature in *API v1*: :attr:`~Controller.ctrl_attributes`

3. **data types**:

    #. :meth:`~Controller.StateOne` **return type**: Previously StateOne had to
       return a member of :class:`PyTango.DevState`. Now it **can** instead return
       a member of :class:`sardana.State`. This eliminates the need to import
       :mod:`PyTango`.
    #. In *API v0* class member (like :attr:`~Controller.ctrl_extra_attributes`)
       value for key *type* had to be a string (like 'PyTango.DevString' or
       'PyTango.DevDouble'). Now they can be a python type (like str or float).
       Please check :ref:`pool-controller-data-type` for more information.

4. **generic controller method names**:

    #. from: :meth:`~Controller.GetPar` to: :meth:`~Controller.GetAxisPar`
    #. from: :meth:`~Controller.SetPar` to: :meth:`~Controller.SetAxisPar`
    #. from: :meth:`~Controller.GetExtraAttributePar` to: :meth:`~Controller.GetAxisExtraPar`
    #. from: :meth:`~Controller.SetExtraAttributePar` to: :meth:`~Controller.SetAxisExtraPar`
    #. new feature in *API v1*: :meth:`~Controller.GetCtrlPar`, :meth:`~Controller.SetCtrlPar`
    #. new feature in *API v1*: :meth:`~Controller.AbortAll` (has default 
       implementation which calls :meth:`~Controller.AbortOne` for each axis)

5. **pseudo motor controller method names**:

    #. from: :meth:`~PseudoMotorController.calc_pseudo` to: :meth:`~PseudoMotorController.CalcPseudo`
    #. from: :meth:`~PseudoMotorController.calc_physical` to: :meth:`~PseudoMotorController.CalcPhysical`
    #. from: :meth:`~PseudoMotorController.calc_all_pseudo` to: :meth:`~PseudoMotorController.CalcAllPseudo`
    #. from: :meth:`~PseudoMotorController.calc_all_physical` to: :meth:`~PseudoMotorController.CalcAllPhysical`
    #. new feature in *API v1*: :meth:`~PseudoMotorController.getMotor`
    #. new feature in *API v1*: :meth:`~PseudoMotorController.getPseudoMotor`

New features in API v1
"""""""""""""""""""""""

This chapter is a summary of all new features in *API v1*.

1. All Controllers now have a :attr:`~Controller.ctrl_attributes` class member
   to define extra controller attributes (and new methods:
   :meth:`~Controller.GetCtrlPar`, :meth:`~Controller.SetCtrlPar`)
2. For :attr:`~Controller.ctrl_properties`, :attr:`~Controller.`axis_attributes`
   and :attr:`~Controller.ctrl_extra_attributes`:
    
   - new (more pythonic) syntax. Old syntax is still supported:
       - can replace data type strings for python type ('PyTango.DevDouble' -> float)
       - Default behavior. Example: before data access needed to be described explicitly.
         Now it is read-write by default.
       - support for 2D
       - new keys 'fget' and 'fset' override default method calls
3. no need to import :mod:`PyTango` (:meth:`~Controller.StateOne` can return
   sardana.State.On instead of PyTango.DevState.ON)
4. new :meth:`~Controller.AbortAll` (with default implementation which calls
   :meth:`~Controller.AbortOne` for each axis)
5. PseudoMotorController has new :meth:`~PseudoMotorController.getMotor` and 
   :meth:`~PseudoMotorController.getPseudoMotor`
