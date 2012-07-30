.. currentmodule:: sardana.pool.controller

.. _pool-controller-howto:

==============================================================================
Writting Controllers
==============================================================================

This chapter provides the necessary information to write controllers in sardana.

An overview of the pool controller concept can be found 
:ref:`here <pool-controller-overview>`.

The complete controller :term:`API` can be found
:ref:`here <pool-controller-api>`.

What is a controller
------------------------------------------------------------------------------

A controller in sardana is a piece of software capable of *translating*
between the sardana :term:`API` and a specific hardware :term:`API`. Sardana
expects a controller to obey a specific :term:`API` in order to be able to
properly configure and operate with it. The hardware :term:`API` used by the
controller could be anything, from a pure serial line to shared memory or a
remote server written in Tango_, Taco_ or even EPICS_.

Controllers can only be written in Python_ (in future also C++ will be
possible). A controller **must** be a :term:`class` inheriting from one of the
existing controller types:

.. hlist::
    :columns: 3
    
    - :class:`MotorController`
    - :class:`CounterTimerController`
    - :class:`ZeroDController`
    - :class:`IORegisterController`

    - :class:`PseudoMotorController`
    - :class:`PseudoCounterController`

A controller is designed to incorporate a set of generic individual elements.
Each element has a corresponding *axis*. For example, in a motor
controller the elements will be motors, but in a counter/timer controller the
elements will be experimental channels.

Some controller classes are designed to target a specific type of hardware.
Other classes of controllers, the *pseudo* classes, are designed to provide a
high level view over a set of underlying lower level controller elements.

We will focus first on writting low level hardware controllers since they 
share some of the :term:`API` and after on the *pseudo* controllers.

.. _pool-motorcontroller-howto-basics:

Motor controller - The basics
------------------------------------------------------------------------------

An example of a hypothetical *Springfield* motor controller will be build
incrementaly from scratch to aid the explanation.
The examples use a :mod:`springfieldlib` module which emulates a motor hardware
access library.

The :mod:`springfieldlib` can be downloaded from
:download:`here <springfieldlib.py>`.

The Springfield motor controller can be downloaded from
:download:`here <sf_motor_ctrl.py>`.

The following code describes a minimalistic *Springfield* base motor controller
which is able to return both the state and position of a motor as well as move
a motor to the desired position:

.. literalinclude:: sf_motor_ctrl.py
   :pyobject: SpringfieldBaseMotorController

This code is shown only to demonstrate the minimalistic controller :term:`API`.
The next chapters will guide you on how to build a proper motor controller from
scratch.

Starting
~~~~~~~~~

The first thing to do is to import the necessary symbols from sardana library.
As you will see, most symbols can be imported through the
:mod:`sardana.pool.controller` module:

.. code-block:: python

    import springfieldlib

    from sardana.pool.controller import MotorController
    
    class SpringfieldMotorController(MotorController):
        """A motor controller intended from demonstration purposes only"""
        pass

The common :term:`API` to all low level controllers includes the set of methods
to:

  #. construct the controller
  #. add/delete a controller element 
  #. obtain the state of controller element(s)

.. _pool-motorcontroller-howto-constructor:

Constructor
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The constructor consists of the
:meth:`~sardana.pool.controller.Controller.__init__` method. This method is
called when you create a new controller of that type and every time the sardana
server is started. It will also be called if the controller code has changed
on the file and the new code is reloaded into sardana.

It is **NOT** mandatory to override the :meth:`~sardana.pool.controller.Controller.__init__`
from the :meth:`~sardana.pool.controller.MotorController` class. Do it only
if you need to add some initialization code. If you do it, it is **very important**
to follow the two rules:

    #. use the method signature: ``__init__(self, inst, props, *args, **kwargs)``
    #. always call the super class constructor
    
The example shows how to implement a constructor:

.. code-block:: python
    :emphasize-lines: 3
    
    class SpringfieldMotorController(MotorController):

        def __init__(self, inst, props, *args, **kwargs):
            super(SpringfieldMotorController, self).__init__(inst, props, *args, **kwargs)
            
            # initialize hardware communication
            self.springfield = springfieldlib.SpringfieldMotorHW()
            
            # do some initialization
            self._motors = {}

.. _pool-motorcontroller-howto-adddelete:

Add/Delete motor
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Two methods are called when creating or removing an element from a controller.
These methods are :meth:`~sardana.pool.controller.Controller.AddDevice` and 
:meth:`~sardana.pool.controller.Controller.DeleteDevice`. The
:meth:`~sardana.pool.controller.Controller.AddDevice` method is called when a
new motor belonging to the controller is created in sardana. The 
:meth:`~sardana.pool.controller.Controller.DeleteDevice` method is
called when a motor belonging to the controller is removed from sardana.
The example shows an example how to implement these methods:

.. code-block:: python
    :emphasize-lines: 3, 6
    
    class SpringfieldMotorController(MotorController):

        def AddDevice(self, axis):
            self._motors[axis] = True 

        def DeleteDevice(self, axis):
            del self._motor[axis]

The code in the example initializes/clears a certain item in the *_motors*
dictionary that was previously created in the constructor. The specific code
for your controller will probably be completely different.

.. _pool-motorcontroller-howto-state:

Get motor state
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To get the state of a motor, sardana calls the
:meth:`~sardana.pool.controller.Controller.StateOne` method. This method
receives an axis as parameter and should return a sequence of three values:

- state (:obj:`~sardana.sardanadefs.State`)
- status (:obj:`str`)
- limit switches (:obj:`int`)

The state should be a member of :obj:`~sardana.sardanadefs.State` (For backward
compatibility reasons, it is also supported to return one of
:class:`PyTango.DevState`). The status could be any string. The limit switches
is a integer with bits representing the three possible limits: home, upper
and lower. Sardana provides three constants which can be *or*\ed together to
provide the desired limit switch:

.. hlist::
    :columns: 4
    
    - :attr:`~MotorController.NoLimitSwitch`
    - :attr:`~MotorController.HomeLimitSwitch`
    - :attr:`~MotorController.UpperLimitSwitch`
    - :attr:`~MotorController.LowerLimitSwitch`

To say both home and lower limit switches are active (rare!) you can do::

    limit_switches = MotorController.HomeLimitSwitch | MotorController.LowerLimitSwitch 

Here is an example of the possible implementation of 
:meth:`~sardana.pool.controller.Controller.StateOne`:

.. code-block:: python
    :emphasize-lines: 11
    
    from sardana import State

    class SpringfieldMotorController(MotorController):

        StateMap = {
            1 : State.On,
            2 : State.Moving,
            3 : State.Fault,
        }
        
        def StateOne(self, axis):
            springfield = self.springfield
            state = self.StateMap[ springfield.getState(axis) ]
            status = springfield.getStatus(axis)
            
            limit_switches = MotorController.NoLimitSwitch
            hw_limit_switches = springfield.getLimits(axis)
            if hw_limit_switches[0]:
                limit_switches |= MotorController.HomeLimitSwitch
            if hw_limit_switches[1]:
                limit_switches |= MotorController.UpperLimitSwitch
            if hw_limit_switches[2]:
                limit_switches |= MotorController.LowerLimitSwitch
            return state, status, limit_switches

.. _pool-motorcontroller-howto-value:

Get motor position
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To get the motor position, sardana calls the
:meth:`~sardana.pool.controller.Readable.ReadOne` method. This method
receives an axis as parameter and should return a valid position. Sardana
interprets the returned position as a :term:`dial position`.

Here is an example of the possible implementation of
:meth:`~sardana.pool.controller.Readable.ReadOne`:

.. code-block:: python
    :emphasize-lines: 3
    
    class SpringfieldMotorController(MotorController):

        def ReadOne(self, axis):
            position = self.springfield.getPosition(axis)
            return position

.. _pool-motorcontroller-howto-move:

Move a motor
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When an order comes for sardana to move a motor, sardana will call the
:meth:`~sardana.pool.controller.Startable.StartOne` method. This method receives
an axis and a position. The controller code should trigger the hardware motion.
The given position is always the :term:`dial position`.

Here is an example of the possible implementation of
:meth:`~sardana.pool.controller.Startable.StartOne`:

.. code-block:: python
    :emphasize-lines: 3
    
    class SpringfieldMotorController(MotorController):

        def StartOne(self, axis, position):
            self.springfield.move(axis, position)

As soon as :meth:`~sardana.pool.controller.Startable.StartOne` is invoked,
sardana expects the motor to be moving. It enters a high frequency motion
loop which asks for the motor state through calls to
:meth:`~sardana.pool.controller.Controller.StateOne`. It will keep the loop
running as long as the controller responds with ``State.Moving``.
If :meth:`~sardana.pool.controller.Controller.StateOne` raises an exception
or returns something other than ``State.Moving``, sardana will assume the motor
is stopped and exit the motion loop.

For a motion to work properly, it is therefore, **very important** that
:meth:`~sardana.pool.controller.Controller.StateOne` responds correctly.

.. _pool-motorcontroller-howto-stop:

Stop a motor
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

It is possible to stop a motor when it is moving. When sardana is ordered to
stop a motor motion, it invokes the :meth:`~sardana.pool.controller.Stopable.StopOne`
method. This method receives an axis parameter. The controller should make
sure the desired motor is *gracefully* stopped, if possible, respecting the
configured motion parameters (like deceleration and base_rate).

Here is an example of the possible implementation of
:meth:`~sardana.pool.controller.Stopable.StopOne`:

.. code-block:: python
    :emphasize-lines: 3
    
    class SpringfieldMotorController(MotorController):

        def StopOne(self, axis):
            self.springfield.stop(axis)

.. _pool-motorcontroller-howto-abort:

Abort a motor
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In a danger situation (motor moving a table about to hit a wall), it is
desirable to abort a motion *as fast as possible*. When sardana is ordered to
abort a motor motion, it invokes the :meth:`~sardana.pool.controller.Stopable.AbortOne`
method. This method receives an axis parameter. The controller should make
sure the desired motor is stopped as fast as it can be done, possibly losing
track of position. 

Here is an example of the possible implementation of
:meth:`~sardana.pool.controller.Stopable.AbortOne`:

.. code-block:: python
    :emphasize-lines: 3
    
    class SpringfieldMotorController(MotorController):

        def AbortOne(self, axis):
            self.springfield.abort(axis)

.. note::
    
    The default implementation of :meth:`~sardana.pool.controller.Stopable.StopOne`
    calls :meth:`~sardana.pool.controller.Stopable.AbortOne` so, if your
    controller cannot distinguish stopping from aborting, it is sufficient
    to implement :meth:`~sardana.pool.controller.Stopable.AbortOne`.

.. _pool-motorcontroller-howto-standard-axis-attributes:

Standard axis attributes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

By default, sardana expects every axis to have a set of attributes:

- acceleration
- deceleration
- velocity
- base rate
- steps per unit

To set and retrieve the value of these attributes, sardana invokes pair of
methods: :meth:`~sardana.pool.controller.Controller.GetAxisPar`
/:meth:`~sardana.pool.controller.Controller.SetAxisPar`

Here is an example of the possible implementation:

.. code-block:: python
    :emphasize-lines: 3, 18
    
    class SpringfieldMotorController(MotorController):

        def GetAxisPar(self, axis, name):
            springfield = self.springfield
            name = name.lower()
            if name == "acceleration":
                v = springfield.getAccelerationTime(axis)
            elif name == "deceleration":
                v = springfield.getDecelerationTime(axis)
            elif name == "base_rate":
                v = springfield.getMinVelocity(axis)
            elif name == "velocity":
                v = springfield.getMaxVelocity(axis)
            elif name == "step_per_unit":
                v = springfield.getStepPerUnit(axis)
            return v

        def SetAxisPar(self, axis, name, value):
            springfield = self.springfield
            name = name.lower()
            if name == "acceleration":
                springfield.setAccelerationTime(axis, value)
            elif name == "deceleration":
                springfield.setDecelerationTime(axis, value)
            elif name == "base_rate":
                springfield.setMinVelocity(axis, value)
            elif name == "velocity":
                springfield.setMaxVelocity(axis, value)
            elif name == "step_per_unit":
                springfield.setStepPerUnit(axis, value)

.. seealso:: 

    :ref:`pool-motorcontroller-whattodo`
        What to do when your hardware motor controller doesn't support
        steps per unit

.. _pool-motorcontroller-howto-extra-axis-attributes:

Extra axis attributes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can specify your controller to have extra attributes on each motor.

Lets suppose our Springfield motor controller can do close loop on hardware.
We could define an extra motor attribute on each axis that (de)actives close
loop on demand.

The first thing to do is to specify which are the extra attributes.
This is done through the :attr:`~sardana.pool.controller.Controller.axis_attributes`.
This is basically a dictionary were the keys are attribute names and the value
is a dictionary describing the folowing properties for each attribute:

===================== ========= ============================================  ======================================================= ===============================================
config. parameter     Mandatory Key                                           Default value                                           Example
===================== ========= ============================================  ======================================================= ===============================================
data type & format    Yes       :obj:`~sardana.pool.controller.Type`          ---                                                     :obj:`int`
data access           No        :obj:`~sardana.pool.controller.Access`        :obj:`~sardana.pool.controller.Access.ReadWrite`        :obj:`~sardana.pool.controller.Access.ReadOnly`
description           No        :obj:`~sardana.pool.controller.Description`   "" (empty string)                                       "the motor encoder source"
default value         No        :obj:`~sardana.pool.controller.DefaultValue`  ---                                                     12345
getter method name    No        :obj:`~sardana.pool.controller.FGet`          "get" + <name>                                          "getEncoderSource"
setter method name    No        :obj:`~sardana.pool.controller.FSet`          "set" + <name>                                          "setEncoderSource"
memorize value        No        :obj:`~sardana.pool.controller.Memorize`      :obj:`~sardana.pool.controller.Memorized`               :obj:`~sardana.pool.controller.NotMemorized`
max dimension size    No        :obj:`~sardana.pool.controller.MaxDimSize`    Scalar: ``()``; 1D: ``(2048,)``; 2D: ``(2048, 2048)``   ``(2048,)``
===================== ========= ============================================  ======================================================= ===============================================

Here is an example of how to specify the scalar, boolean, read-write *CloseLoop*
extra attribute in our the Springfield motor controller:

.. code-block:: python
    :emphasize-lines: 6, 14, 17
    
    from sardana import DataAccess
    from sardana.pool.controller import Type, Description, DefaultValue, Access, FGet, FSet
    
    class SpringfieldMotorController(MotorController):
    
        axis_attributes = { 
            "CloseLoop" : {
                    Type         : bool,
                    Description  : "(de)activates the motor close loop algorithm",
                    DefaultValue : False,
                },
        }
        
        def getCloseLoop(self, axis):
            return self.springfield.isCloseLoopActive(axis)
        
        def setCloseLoop(self, axis, value):
            self.springfield.setCloseLoop(axis, value)

When sardana needs to read the close loop value, it will first check if the
controller has the method specified by the :obj:`~sardana.pool.controller.FGet`
keyword (we didn't specify it in 
:attr:`~sardana.pool.controller.Controller.axis_attributes` so it defaults to
*getCloseLoop*). It will then call this controller method which
should return a value compatible with the attribute data type.

As an alternative, to avoid filling the controller code with pairs of get/set
methods, you can choose not to write the getCloseLoop and setCloseLoop methods.
This will trigger sardana to call the 
:meth:`~sardana.pool.controller.Controller.GetAxisExtraPar`
/:meth:`~sardana.pool.controller.Controller.SetAxisExtraPar` pair of methods.
The disadvantage is you will end up with a forest of :keyword:`if` ... 
:keyword:`elif` ... :keyword:`else` statements. Here is the alternative
implementation:

.. code-block:: python
    :emphasize-lines: 6, 14, 18
    
    from sardana import DataAccess
    from sardana.pool.controller import Type, Description, DefaultValue, Access, FGet, FSet
    
    class SpringfieldMotorController(MotorController):
    
        axis_attributes = { 
            "CloseLoop" : {
                    Type         : bool,
                    Description  : "(de)activates the motor close loop algorithm",
                    DefaultValue : False,
                },
        }
        
        def GetAxisExtraPar(self, axis, parameter):
            if parameter == 'CloseLoop':
                return self.springfield.isCloseLoopActive(axis)
        
        def SetAxisExtraPar(self, axis, parameter, value):
            if parameter == 'CloseLoop':
                 self.springfield.setCloseLoop(axis, value)

Sardana gives you the choice: we leave it up to you to decide which is the
better option for your specific case.

.. _pool-motorcontroller-howto-extra-controller-attributes:

Extra controller attributes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Besides extra attributes per axis, you can also define extra attributes at the
controller level.
In order to do that you have to specify the extra controller attribute(s) within 
the :attr:`~sardana.pool.controller.Controller.ctrl_attributes` member. The
syntax for this dictionary is the same as the one used for
:attr:`~sardana.pool.controller.Controller.axis_attributes`.

Here is an example on how to specify a read-only float matrix attribute called
*ReflectionMatrix* at the controller level:

.. code-block:: python 

    class SpringfieldMotorController(MotorController):
    
        ctrl_attributes = { 
            "ReflectionMatrix" : {
                    Type         : ( (float,), ),
                    Description  : "The reflection matrix",
                    Access : DataAccess.ReadOnly,
                },
        }
        
        def getReflectionMatrix(self):
            return ( (1.0, 0.0), (0.0, 1.0) )

Or, similar to what you can do with axis attributes:

.. code-block:: python

    class SpringfieldMotorController(MotorController):
    
        ctrl_attributes = \
        { 
            "ReflectionMatrix" : {
                    Type         : ( (float,), ),
                    Description  : "The reflection matrix",
                    Access : DataAccess.ReadOnly,
                },
        }
        
        def GetCtrlPar(self, name):
            if name == "ReflectionMatrix":
                return ( (1.0, 0.0), (0.0, 1.0) )

.. _pool-motorcontroller-howto-controller-properties:

Controller properties
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A more static form of attributes can be defined at the controller level.
These *properties* are loaded into the controller at the time of object
construction. They are accessible to your controller at any time but it is
not possible for a user from outside to modify them.
The way to define :attr:`~sardana.pool.controller.Controller.ctrl_properties` is
very similar to the way you define extra axis attributes or extra controller
attributes.

Here is an example on how to specify a host and port properties:

.. code-block:: python

    class SpringfieldMotorController(MotorController):
    
        ctrl_properties = \
        {
            "host" : { 
                    Type : str,
                    Description : "host name"
                },
            "port" : {
                    Type : int, 
                    Description : "port number",
                    DefaultValue: springfieldlib.SpringfieldMotorHW.DefaultPort 
               },
        }

        def __init__(self, inst, props, *args, **kwargs):
            super(SpringfieldMotorController, self).__init__(inst, props, *args, **kwargs)
            
            host = self.host
            port = self.port
                        
            # initialize hardware communication
            self.springfield = springfieldlib.SpringfieldMotorHW(host=host, port=port)
            
            # do some initialization
            self._motors = {}

As you can see from lines 15 and 16, to access your controller properties
simply use ``self.<property name>``. Sardana assures that every property has a
value. In our case, when a SpringfieldMotorController is created, if port
property is not specified by the user (example: using the ``defctrl`` macro in
spock), sardana assignes the default value
``springfieldlib.SpringfieldMotorHW.DefaultPort``. On the other hand, since host
has no default value, if it is not specified by the user, sardana will complain
and fail to create and instance of SpringfieldMotorController.


.. _pool-motorcontroller-howto-define-position:

Define a position
~~~~~~~~~~~~~~~~~

Sometimes it is useful to reset the current position to a certain value.
Imagine you are writting a controller for a hardware controller which handles
stepper motors. When the hardware is asked for a motor position it will
probably answer some value from an internal register which is
incremented/decremented each time the motor goes up/down a step. Probably this
value as physical meaning so the usual procedure is to move the motor to a known
position (home switch, for example) and once there, set a meaningful position to
the current position. Some motor controllers support reseting the internal
register to the desired value. If your motor controller can do this the
implementation is as easy as writting the 
:meth:`~sardana.pool.controller.MotorController.DefinePosition` and call the
proper code of your hardware library to do it:

.. code-block:: python

    class SpringfieldMotorController(MotorController):

        def DefinePosition(self, axis, position):
            self.springfield.setCurrentPosition(axis, position)

.. seealso:: 

    :ref:`pool-motorcontroller-whattodo`
       
        What to do when your hardware motor controller doesn't support
        defining the position

.. _pool-motorcontroller-howto-handle-errors:

Handle errors
~~~~~~~~~~~~~

When you write a controller it is important to properly handle errors
(example: motor power overload, hit a limit switch, lost of communication with
the hardware).

These are the two basic sardana rules you should have in mind:

#. The exceptions which are not handled by the controller are handled by sardana,
   usually by re-raising the exception (when sardana runs as a Tango_ DS a
   translation is done from the Python_ exception to a Tango_ exception).
   The :meth:`~sardana.pool.controller.Controller.StateOne` method is handled a
   little differently: the state is set to ``Fault`` and the status will contain
   the exception information.

#. When the methods which are supposed to return a value (like
   :meth:`~sardana.pool.controller.Controller.GetAxisPar`) don't return a value
   compatible with the expected data type (including :obj:`None`) a 
   :exc:`TypeError` exception is thrown.

In every method you should carefully choose how to do handle the possible
exceptions/errors. 

Usually, catch and handle is the best technique since it is the code of your
controller which knows exactly the workings of the hardware. You can
discriminate errors and decide a proper handle for each. Essencially, this
technique consists of:

#. catching the error (if an exception: with :keyword: try ... :keyword:except
   clause, if an expected return of a function: with a keyword:`if` ... 
   :keyword:`elif` ... :keyword:`else` statement, etc)

#. raise a proper exception (could be the same exception that has been catched)
   or, if in :meth:`~sardana.pool.controller.Controller.StateOne`, return the
   apropriate error state (``Fault``, ``Alarm``) and a descriptive status.
    
Here is an example: if the documentation of the underlying library says that:

    `reading the motor closeloop raises CommunicationFailed if it is not
    possible to communicate with the Springfield hardware`

    `reading the motor state raises MotorPowerOverload if the motors
    has a power overload or a MotorTempTooHigh when the motor
    temperature is too high`

then you should handle the exception in the controller and return a proper
state information::

    def getCloseLoop(self, axis):
        # Here the "proper exception" to raise in case of error is actually the
        # one that is raised from the springfield library so handling the
        # exception is transparent. Nice!
        return self.springfield.isCloseLoopActive(axis)

    def StateOne(self, axis):
        springfield = self.springfield
        
        try:
            state = self.StateMap[ springfield.getState(axis) ]
            status = springfield.getStatus(axis)
        except springfieldlib.MotorPowerOverload:
            state = State.Fault
            status = "Motor has a power overload"
        except springfieldlib.MotorTempTooHigh:
            temp = springfield.getTemperature(axis)
            state = State.Alarm
            status = "Motor temperature is too high (%f degrees)" % temp      

        limit_switches = MotorController.NoLimitSwitch
        hw_limit_switches = springfield.getLimits(axis)
        if hw_limit_switches[0]:
            limit_switches |= MotorController.HomeLimitSwitch
        if hw_limit_switches[1]:
            limit_switches |= MotorController.UpperLimitSwitch
        if hw_limit_switches[2]:
            limit_switches |= MotorController.LowerLimitSwitch
        return state, status, limit_switches

Hiding the exception is usually a **BAD** technique since it prevents the user
from finding what was the cause of the problem. You should only use it in
extreme cases (example: if there is a bug in sardana which crashes the server
if you try to properly raise an exception, then you can **temporarely** use
this technique until the bug is solved).

Example::

    def getCloseLoop(self, axis):
        # BAD error handling technique
        try:
            return self.springfield.isCloseLoopActive(axis)
        except:
            pass

.. _pool-motorcontroller-whattodo:

What to do when...
~~~~~~~~~~~~~~~~~~

This chapter describes common difficult situations you may face when writting
a motor controller in sardana, and possible solutions to solve them. 

*my controller doesn't support steps per unit*
    Many (probably, most) hardware motor controllers don't support steps per
    unit at the hardware level. This means that your sardana controller should
    be able to emulate steps per unit at the software level. 
    This can be easily done, but it requires you to make some changes in your
    code.
    
    We will assume now that the Springfield motor controller doesn't support
    steps per unit feature. The first that needs to be done is to modify the
    :meth:`~sardana.pool.controller.Controller.AddDevice` method so it is able to
    to store the resulting conversion factor between the hardware read position
    and the position the should be returned (the *step_per_unit*).
    The :meth:`~sardana.pool.controller.Readable.ReadOne` also needs to be
    rewritten to make the proper calculation.
    Finally :meth:`~sardana.pool.controller.Controller.GetAxisPar` / 
    :meth:`~sardana.pool.controller.Controller.SetAxisPar` methods need to 
    be rewritten to properly get/set the step per unit value:

    .. code-block:: python

        class SpringfieldMotorController(MotorController):

            def AddDevice(self, axis):
                self._motor[axis] = dict(step_per_unit=1.0)

            def ReadOne(self, axis):
                step_per_unit = self._motor[axis]["step_per_unit"]
                position = self.springfield.getPosition(axis)
                return position / step_per_unit
            
            def GetAxisPar(self, axis, name):
                springfield = self.springfield
                name = name.lower()
                if name == "acceleration":
                    v = springfield.getAccelerationTime(axis)
                elif name == "deceleration":
                    v = springfield.getDecelerationTime(axis)
                elif name == "base_rate":
                    v = springfield.getMinVelocity(axis)
                elif name == "velocity":
                    v = springfield.getMaxVelocity(axis)
                elif name == "step_per_unit":
                    v = self._motor[axis]["step_per_unit"]
                return v

            def SetAxisPar(self, axis, name, value):
                springfield = self.springfield
                name = name.lower()
                if name == "acceleration":
                    springfield.setAccelerationTime(axis, value)
                elif name == "deceleration":
                    springfield.setDecelerationTime(axis, value)
                elif name == "base_rate":
                    springfield.setMinVelocity(axis, value)
                elif name == "velocity":
                    springfield.setMaxVelocity(axis, value)
                elif name == "step_per_unit":
                    self._motor[axis]["step_per_unit"] = value                

*my controller doesn't support defining the position*
    Some controllers may not be able to reset the position to a different value.
    In these cases, your controller code should be able to emulate such a
    feature.
    This can be easily done, but it requires you to make some changes in your
    code.
    
    We will now assume that the Springfield motor controller doesn't support
    steps per unit feature. The first that needs to be done is to modify the
    :meth:`~sardana.pool.controller.Controller.AddDevice` method so it is able
    to store the resulting offset between the hardware read position and the
    position the should be returned (the *define_position_offset*).
    The :meth:`~sardana.pool.controller.Readable.ReadOne` also needs to be
    rewritten to take the *define_position_offset* into account.
    Finally :meth:`~sardana.pool.controller.MotorController.DefinePosition`
    needs to be written to update the *define_position_offset* to the desired
    value:

    .. code-block:: python

        class SpringfieldMotorController(MotorController):

            def AddDevice(self, axis):
                self._motor[axis] = dict(define_position_offset=0.0)

            def ReadOne(self, axis):
                dp_offset = self._motor[axis]["define_position_offset"]
                position = self.springfield.getPosition(axis)
                return position + dp_offset
            
            def DefinePosition(self, axis, position):
                current_position = self.springfield.getPosition(axis)
                self._motor[axis]["define_position_offset"] = position - current_position

Motor controller - Advanced topics
------------------------------------------------------------------------------

This chapter describes an extended :term:`API` that allows you to better
synchronize motions involing more than one motor, as well as optimize 
hardware communication (in case the hardware interface also supports this).
 
Often it is the case that the experiment/procedure the user runs requires to
move more than one motor at the same time.
Imagine that the user requires motor at axis 1 to be moved to 100mm and motor
axis 2 to be moved to -20mm.
Your controller will receive two consecutive calls to
:meth:`~sardana.pool.controller.Startable.StartOne`:

.. code-block:: python

    StartOne(1, 100)
    StartOne(2, -20)
    
and each StartOne will probably connect to the hardware (through serial line, 
socket, Tango_ or EPICS_) and ask the motor to be moved.
This will do the job but, there will be a slight desynchronization between the
two motors because hardware call of motor 1 will be done before hardware call
to motor 2.

Sardana provides an extended *start motion* which gives you the possibility
to improve the syncronization (and probably reduce communications) but your 
hardware controller must somehow support this feature as well.

The complete start motion :term:`API` consists of four methods:

    - :meth:`~sardana.pool.controller.Startable.PreStartAll`
    - :meth:`~sardana.pool.controller.Startable.PreStartOne`
    - :meth:`~sardana.pool.controller.Startable.StartOne`
    - :meth:`~sardana.pool.controller.Startable.StartAll`

Except for :meth:`~sardana.pool.controller.Startable.StartOne`, the
implemenation of all other start methods is optional and their default
implementation does nothing (:meth:`~sardana.pool.controller.Startable.PreStartOne`
actually returns ``True``).

So, actually, the complete algorithm for motor motion in sardana is::

    /FOR/ Each controller(s) implied in the motion
         - Call PreStartAll()
    /END FOR/
     
    /FOR/ Each motor(s) implied in the motion
         - ret = PreStartOne(motor to move, new position)
         - /IF/ ret is not true
            /RAISE/ Cannot start. Motor PreStartOne returns False
         - /END IF/         
         - Call StartOne(motor to move, new position)
    /END FOR/
     
    /FOR/ Each controller(s) implied in the motion
         - Call StartAll()
    /END FOR/

So, for the example above where we move two motors, the complete sequence of
calls to the controller is:

.. code-block:: python
    
    PreStartAll()

    if not PreStartOne(1, 100):
        raise Exception("Cannot start. Motor(1) PreStartOne returns False")
    if not PreStartOne(2, -20):
        raise Exception("Cannot start. Motor(2) PreStartOne returns False")

    StartOne(1, 100)
    StartOne(2, -20)

    StartAll()

Sardana assures that the above sequence is never interrupted by other calls,
like a call from a different user to get motor state.
    
Suppose the springfield library tells us in the documentation that:

    ... to move multiple motors at the same time use::
    
        moveMultiple(seq<pair<axis, position>>)
    
    Example::
    
        moveMultiple([[1, 100], [2, -20]])

We can modify our motor controller to take profit of this hardware feature:

.. code-block:: python
    
    class SpringfieldMotorController(MotorController):
        
        def PreStartAll(self):
            # clear the local motion information dictionary
            self._moveable_info = []

        def StartOne(self, axis, position):
            # store information about this axis motion
            motion_info = axis, position
            self._moveable_info.append(motion_info)

        def StartAll(self):
            self.springfield.moveMultiple(self._moveable_info)
            
A similar principle applies when sardana asks for the state and position of
multiple axis. The two sets of methods are, in these cases:

.. hlist::
    :columns: 2

    - :meth:`~sardana.pool.controller.Controller.PreStateAll`
    - :meth:`~sardana.pool.controller.Controller.PreStateOne`
    - :meth:`~sardana.pool.controller.Controller.StateAll`
    - :meth:`~sardana.pool.controller.Controller.StateOne`
    - :meth:`~sardana.pool.controller.Readable.PreReadAll`
    - :meth:`~sardana.pool.controller.Readable.PreReadOne`
    - :meth:`~sardana.pool.controller.Readable.ReadAll`
    - :meth:`~sardana.pool.controller.Readable.ReadOne`

The main differences between these sets of methods and the ones from start motion
is that :meth:`~sardana.pool.controller.Controller.StateOne` / 
:meth:`~sardana.pool.controller.Readable.ReadOne` methods are called **AFTER**
the corresponding :meth:`~sardana.pool.controller.Controller.StateAll` / 
:meth:`~sardana.pool.controller.Readable.ReadAll` counterparts and they are
expeced to return the state/position of the requested axis.

The internal sardana algorithm to read position is::

    /FOR/ Each controller(s) implied in the reading
         - Call PreReadAll()
    /END FOR/
     
    /FOR/ Each motor(s) implied in the reading
         - PreReadOne(motor to read)
    /END FOR/
     
    /FOR/ Each controller(s) implied in the reading
         - Call ReadAll()
    /END FOR/
     
    /FOR/ Each motor(s) implied in the reading
         - Call ReadOne(motor to read)
    /END FOR/

Here is an example assuming the springfield library tells us in the
documentation that:

    ... to read the position of multiple motors at the same time use::
    
        getMultiplePosition(seq<axis>) -> dict<axis, position>
    
    Example::
    
        positions = getMultiplePosition([1, 2])

The new improved code could look like this::

    class SpringfieldMotorController(MotorController):
        
        def PreRealAll(self):
            # clear the local position information dictionary
            self._position_info = []
        
        def PreReadOne(self, axis):
            self._position_info.append(axis)
        
        def ReadAll(self):
            self._positions = self.springfield.getMultiplePosition(self._position_info)
        
        def ReadOne(self, axis):
            return self._positions[axis]
        
.. _ALBA: http://www.cells.es/
.. _ANKA: http://http://ankaweb.fzk.de/
.. _ELETTRA: http://http://www.elettra.trieste.it/
.. _ESRF: http://www.esrf.eu/
.. _FRMII: http://www.frm2.tum.de/en/index.html
.. _HASYLAB: http://hasylab.desy.de/
.. _MAX-lab: http://www.maxlab.lu.se/maxlab/max4/index.html
.. _SOLEIL: http://www.synchrotron-soleil.fr/

.. _Tango: http://www.tango-controls.org/
.. _Taco: http://www.esrf.eu/Infrastructure/Computing/TACO/
.. _PyTango: http://packages.python.org/PyTango/
.. _Taurus: http://packages.python.org/taurus/
.. _QTango: http://www.tango-controls.org/download/index_html#qtango3
.. _Qt: http://qt.nokia.com/products/
.. _PyQt: http://www.riverbankcomputing.co.uk/software/pyqt/
.. _PyQwt: http://pyqwt.sourceforge.net/
.. _Python: http://www.python.org/
.. _IPython: http://ipython.org/
.. _ATK: http://www.tango-controls.org/Documents/gui/atk/tango-application-toolkit
.. _Qub: http://www.blissgarden.org/projects/qub/
.. _numpy: http://numpy.scipy.org/
.. _SPEC: http://www.certif.com/
.. _EPICS: http://www.aps.anl.gov/epics/
