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
            self.springfield = springfieldlib.SpringfieldMotorController()
            
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
    :emphasize-lines: 3, 5, 8
    
    class SpringfieldMotorController(MotorController):

        MaxDevice = 128

        def AddDevice(self, axis):
            self._motors[axis] = True 

        def DeleteDevice(self, axis):
            del self._motor[axis]

First you need to specify the maximum number of motors this controller is
capable of handling. This is done in line 3 through the usage of the class
member ``MaxDevice``.
  
The code in the example initializes/clears a certain item in the *_motors*
dictionary that was previously created in the constructor. The specific code
for your controller will probably be completely different.

.. _pool-motorcontroller-howto-state:

Get motor state
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To get the state of a motor, sardana calls the
:meth:`~sardana.pool.controller.Controller.StateOne` method. This method
receives an axis as parameter and should return a sequence of three values:

- state (:obj:`~sardana.sardanadefs.State` (For backward compatibility reasons,
  it is also supported to return one of :class:`PyTango.DevState`)).
- status (:obj:`str`)
- limit switches (:obj:`int`)

The status could be any string. The limit switches is a integer with bits
representing the three possible limits: home, upper and lower.
Sardana provides three constants which can be *or*\ed together to provide the
desired limit switch:

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

===================== ========= ============================================  ================================================= =============================================
config. parameter     Mandatory Key                                           Default value                                     Example
===================== ========= ============================================  ================================================= =============================================
data type & format    Yes       :obj:`~sardana.pool.controller.Type`          ---                                               :obj:`int`
data access           No        :obj:`~sardana.pool.controller.Access`        :obj:`~sardana.pool.controller.Access.ReadWrite`  Access.ReadOnly
description           No        :obj:`~sardana.pool.controller.Description`   "" (empty string)                                 "the motor encoder source"
default value         No        :obj:`~sardana.pool.controller.DefaultValue`  ---                                               12345
getter method name    No        :obj:`~sardana.pool.controller.FGet`          "get" + <name>                                    "getEncoderSource"
setter method name    No        :obj:`~sardana.pool.controller.FSet`          "set" + <name>                                    "setEncoderSource"
memorize value        No        :obj:`~sardana.pool.controller.Memorize`      :obj:`~sardana.pool.controller.Memorized`         :obj:`~sardana.pool.controller.NotMemorize`
===================== ========= ============================================  ================================================= =============================================

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
