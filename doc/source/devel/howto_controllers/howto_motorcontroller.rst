.. currentmodule:: sardana.pool.controller

.. _sardana-motorcontroller-howto-basics:

===============================
How to write a motor controller
===============================

The basics
----------

An example of a hypothetical *Springfield* motor controller will be build
incrementally from scratch to aid in the explanation.

By now you should have read the general controller basics chapter. You should
now have a MotorController with a proper constructor, add and delete axis methods:

.. code-block:: python

    import springfieldlib

    from sardana.pool.controller import MotorController

    class SpringfieldMotorController(MotorController):

        def __init__(self, inst, props, *args, **kwargs):
            super(SpringfieldMotorController, self).__init__(inst, props, *args, **kwargs)
            
            # initialize hardware communication
            self.springfield = springfieldlib.SpringfieldMotorHW()
            
            # do some initialization
            self._motors = {}

        def AddDevice(self, axis):
            self._motors[axis] = True 

        def DeleteDevice(self, axis):
            del self._motor[axis]

The *get axis state* method has some details that will be explained below.

The examples use a :mod:`springfieldlib` module which emulates a motor hardware
access library.

The :mod:`springfieldlib` can be downloaded from
:download:`here <springfieldlib.py>`.

The Springfield motor controller can be downloaded from
:download:`here <sf_motor_ctrl.py>`.

The following code describes a minimal *Springfield* base motor controller
which is able to return both the state and position of a motor as well as move
a motor to the desired position:

.. literalinclude:: sf_motor_ctrl.py
   :pyobject: SpringfieldBaseMotorController

This code is shown only to demonstrate the minimal controller :term:`API`.
The advanced motor controller chapters describe how to account for more complex
behaviour like reducing the number of hardware accesses or synchronize motion of
multiple motors.
 
.. _sardana-motorcontroller-howto-axis-state:

Get motor state
~~~~~~~~~~~~~~~

To get the state of a motor, sardana calls the
:meth:`~sardana.pool.controller.Controller.StateOne` method. This method
receives an axis as parameter and should return a sequence of three values:

To get the state of a motor, sardana calls the
:meth:`~sardana.pool.controller.Controller.StateOne` method. This method
receives an axis as parameter and should return either:

    - state (:obj:`~sardana.sardanadefs.State`) or
    - a sequence of two elements:
        - state (:obj:`~sardana.sardanadefs.State`)
        - status (:obj:`str`) *or* limit switches (:obj:`int`)      
    - a sequence of three elements:
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

If you don't return a status, sardana will compose a status string with:

    <axis name> is in <state name>

If you don't return limit switches, sardana will assume all limit switches are
off.

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

.. _sardana-motorcontroller-howto-value:

Get motor position
~~~~~~~~~~~~~~~~~~

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

.. _sardana-motorcontroller-howto-move:

Move a motor
~~~~~~~~~~~~

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

.. _sardana-motorcontroller-howto-stop:

Stop a motor
~~~~~~~~~~~~

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

.. _sardana-motorcontroller-howto-abort:

Abort a motor
~~~~~~~~~~~~~

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

.. _sardana-motorcontroller-howto-standard-axis-attributes:

Standard axis attributes
~~~~~~~~~~~~~~~~~~~~~~~~

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

    :ref:`sardana-motorcontroller-what-to-do`
        What to do when your hardware motor controller doesn't support
        steps per unit

.. _sardana-motorcontroller-define-position:

Define a position
~~~~~~~~~~~~~~~~~

Sometimes it is useful to reset the current position to a certain value.
Imagine you are writing a controller for a hardware controller which handles
stepper motors. When the hardware is asked for a motor position it will
probably answer some value from an internal register which is
incremented/decremented each time the motor goes up/down a step. Probably this
value as physical meaning so the usual procedure is to move the motor to a known
position (home switch, for example) and once there, set a meaningful position to
the current position. Some motor controllers support reseting the internal
register to the desired value. If your motor controller can do this the
implementation is as easy as writing the 
:meth:`~sardana.pool.controller.MotorController.DefinePosition` and call the
proper code of your hardware library to do it:

.. code-block:: python

    class SpringfieldMotorController(MotorController):

        def DefinePosition(self, axis, position):
            self.springfield.setCurrentPosition(axis, position)

.. seealso:: 

    :ref:`sardana-motorcontroller-what-to-do`
       
        What to do when your hardware motor controller doesn't support
        defining the position

.. _sardana-motorcontroller-what-to-do:

What to do when...
~~~~~~~~~~~~~~~~~~

This chapter describes common difficult situations you may face when writing
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
    feature. This can be easily done, but it requires you to make some changes
    in your code.
    
    We will now assume that the Springfield motor controller doesn't support
    steps per unit feature. The first thing that needs to be done is to modify the
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


Advanced topics
---------------

.. _sardana-motorcontroller-howto-timestamp-position:

Timestamp a motor position
~~~~~~~~~~~~~~~~~~~~~~~~~~

When you read the position of a motor from the hardware sometimes it is
necessary to associate a timestamp with that position so you can track the
position of a motor in time.

If sardana is executed as a Tango device server, reading the position
attribute from the motor device triggers the execution of your controller's 
:meth:`~sardana.pool.controller.Readable.ReadOne` method. Tango responds with 
the value your controller returns from the call to
:meth:`~sardana.pool.controller.Readable.ReadOne` and automatically assigns
a timestamp. However this timestamp has a certain delay since the time the
value was actually read from hardware and the time Tango generates the timestamp.

To avoid this, sardana supports returning in 
:meth:`~sardana.pool.controller.Readable.ReadOne` an object that contains both
the value and the timestamp instead of the usual :class:`numbers.Number`.
The object must be an instance of :class:`~sardana.sardanavalue.SardanaValue`.

Here is an example of associating a timestamp in
:meth:`~sardana.pool.controller.Readable.ReadOne`:

.. code-block:: python

    import time
    from sardana.pool.controller import SardanaValue 

    class SpringfieldMotorController(MotorController):

       def ReadOne(self, axis):
           return SardanaValue(value=self.springfield.getPosition(axis),
                               timestamp=time.time())

If your controller communicates with a Tango device, Sardana also supports
returning a :class:`~PyTango.DeviceAttribute` object. Sardana will use this
object's value and timestamp. Example:

.. code-block:: python

    class TangoMotorController(MotorController):

       def ReadOne(self, axis):
           return self.device.read_attribute("position")

.. _sardana-motorcontroller-howto-mutiple-motion:

Multiple motion synchronization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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
            