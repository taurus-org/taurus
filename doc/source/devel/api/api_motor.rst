.. currentmodule:: sardana.pool.poolmotor

.. _sardana-motor-api:

===================
Motor API reference
===================

The motor is one of the most used elements in sardana. A motor represents
anything that can be *changed* (and can potentially take some time to do it).

This chapter explains the generic motor :term:`API` in the context of sardana.
In sardana there are, in fact, two Motor :term:`API`\s. To better explain why,
let's consider the case were sardana server is running as a Sardana Tango
device server:

.. image:: /_static/sardana_server_internal_motor.png
    :width: 680
    :align: center

Every motor in sardana is represented in the sardana kernel as a
:class:`PoolMotor`. The :class:`PoolMotor` :term:`API` is not directly
accessible from outside the sardana server. This is a low level :term:`API`
that is only accessbile to someone writing a server extension to sardana. At
the time of writing, the only available sardana server extension is Tango.

The second motor interface consists on the one provided by the server extension,
which is in this case the one provided by the Tango motor device interface:
:class:`~sardana.tango.pool.Motor.Motor`. The Tango motor interface tries to
mimic the as closely as possible the :class:`PoolMotor` :term:`API`.

.. seealso:: 
    
    :ref:`sardana-motor-overview`
        the motor overview 

    :class:`~sardana.tango.pool.Motor.Motor`
        the motor tango device :term:`API`
    
..    :class:`~sardana.pool.poolmotor.PoolMotor`
..        the motor class :term:`API`

A motor will have, at least, a ``state``, and a ``position``. The state
indicates at any time if the motor is stopped, in alarm or moving. The
position, indicates the current :term:`user position`. Unless a motor
controller is specifically programmed not to, it's motors will also have:

**limit switches**
    the three limit switches (home, upper and lower). Each switch is
    represented by a boolean value: False means inactive while True means
    active.
    
    low level :attr:`PoolMotor` API.
    
    high level Tango Motor API: limit_switches tango attribute
        
**acceleration**
    motor acceleration (usually acceleration time in seconds, but it's up to
    the motor controller class to decide)
    
    :attr:`~PoolMotor.acceleration`
    
**deceleration**
    motor deceleration (usually deceleration time in seconds, but it's up to
    the motor controller class to decide)

    :attr:`~PoolMotor.deceleration`
    
**velocity**
    top velocity

    :attr:`~PoolMotor.velocity`

**base rate**
    initial velocity

    :attr:`~PoolMotor.base_rate`

**dial position**
    the :term:`dial position`

    :attr:`~PoolMotor.dial_position`

**offset**
    the offset to be applied in the motor position computation [default: 0.0]

    :attr:`~PoolMotor.offset`

**sign**
    the sign to be applied in the motor position computation [default: 1,
    possible values are (1, -1)]

    :attr:`~PoolMotor.sign`

**Steps per unit**
    This is the number of motor steps per :term:`user position` [default:
    1.0]

    :attr:`~PoolMotor.step_per_unit`

**backlash**
    If this is defined to be something different than 0, the motor will
    always stop the motion coming from the same mechanical direction. This
    means that it could be possible to ask the motor to go a little bit after
    the desired position and then to return to the desired position. The value
    is the number of steps the motor will pass the desired position if it
    arrives from the "wrong" direction. This is a signed value. If the sign is
    positive, this means that the authorized direction to stop the motion is
    the increasing motor position direction. If the sign is negative, this
    means that the authorized direction to stop the motion is the decreasing
    motor position direction. 

    :attr:`~PoolMotor.backlash`
    
**instability_time**
    This property defines the time in milliseconds that the software
    managing a motor movement will wait between it detects the end of the
    motion and the last motor position reading. It is typically used for motors
    that move mechanics which have an instability time after each motion.
    
    :attr:`~PoolMotor.instability_time`

The available operations are:

start move absolute (:term:`user position`\)
    starts to move the motor to the given absolute user position
    
    :meth:`~PoolMotor.start_move`

stop
    stops the motor in an orderly fashion
    
abort
    stops the motor motion as fast as possible (possibly without
    deceleration time and loss of position)

Motor state
-----------

On a sardana tango server, the motor state can be obtained by reading the state
attribute or by executing the state command. The diagram shows the internal
sequence of calls.

.. image:: /_static/sardana_server_internal_motor_read_state_flow.png
    :width: 680
    :align: center

Motor position
--------------

The motor's current :term:`user position` can be obtained by reading the
position attribute. The diagram shows the internal sequence of calls.

.. image:: /_static/sardana_server_internal_motor_read_position_flow.png
    :width: 680
    :align: center

Motion
------

The most useful thing to do with a motor is, of course, to move it. To move a
motor to another absolute :term:`user position` you have to write the value
into the position attribute.

.. image:: /_static/sardana_server_internal_motor_write_position_flow.png
    :width: 680
    :align: center

Before allowing a movement, some pre-conditions are automatically checked by
tango (not represented in the diagram):

    - motor is in a proper state;
    - requested position is within the allowed motor boundaries (if
      defined)

Then, the :term:`dial position` is calculated taking into account the *offset*,
*signal* as well as a possible *backlash*.

Afterward, and because the motor may be part of a pseudo motor system, other
pre-conditions are checked:

    - is the final :term:`dial position` (including backlash) within the
      motor boundaries (if defined)
    - will the resulting motion end in an allowed position for all the
      pseudo motors that depend on this motor

After all pre-conditions are checked, the motor will deploy a motion *job* into
the sardana kernel engine which will trigger a series of calls to the
underlying motor controller.

The motor awaits for the :meth:`~sardana.pool.controller.Startable.PreStartOne`
to signal that the motion will be possible to return successfully from the move
request.

The next diagram shows the state machine of a motor.

.. graphviz:: motion.dot
    :alt: Basic motion diagram
    :caption:
        Basic motion diagram. The black state transitions are the ones which
        can be triggered by a *user*.
        For simplicity, only the most relevant states involved in a motor
        motion are shown. Error states are omited




