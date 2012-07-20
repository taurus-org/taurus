.. currentmodule:: sardana.pool.poolmotor

.. _pool-motor-api:

===================
Motor API reference
===================

The motor is one of the most used elements in sardana. A motor represents
anything that can be *changed* (and can potentially take some time to do it).

A motor will have, at least, a **state**, and a **position**. 
The state indicates at any time if the motor is available, in alarm or moving.
The position, indicates the current :term:`user position`.
Unless a motor controller is specifically programmed not to, it's motors will
also have:

**limit switches**
    the three limit switches (home, upper and lower). Each
    switch is represented by a boolean value: False means inactive while
    True means active.
    
    :attr:`~PoolMotor.limit_switches`
        
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
    This is the number of motor steps per :term:`user position` [default: 1.0]

    :attr:`~PoolMotor.step_per_unit`

**backlash**
    If this is defined to be something different than 0, the motor will always
    stop the motion coming from the same mechanical direction. This means that
    it could be possible to ask the motor to go
    a little bit after the desired position and then to return to the
    desired position. The value is the number of steps the motor will pass
    the desired position if it arrives from the "wrong" direction. This is a
    signed value. If the sign is positive, this means that the authorized
    direction to stop the motion is the increasing motor position direction.
    If the sign is negative, this means that the authorized direction to stop
    the motion is the decreasing motor position direction. 

    :attr:`~PoolMotor.backlash`
    
**instability_time**
    This property defines the time in milliseconds that the software
    managing a motor movement will wait between it detects the end of the
    motion and the last motor position reading.
    It is typically used for motors that move mechanics which have an instability
    time after each motion.
    
    :attr:`~PoolMotor.instability_time`

The available operations are:

start move absolute (:term:`user position`\)
    starts to move the motor to the given absolute user position
    
    :meth:`~PoolMotor.start_move`

stop
    stops the motor in an orderly fashion
    
abort
    stops the motor motion as fast as possible (possibly without deceleration
    time and loss of position)

Motion 
-------

The most important operation on a motor is, of course, to move it. The following
diagram shows the state machine of a motor.

.. graphviz:: motion.dot

The black state transitions are the ones which can be triggered by a *user*.

.. seealso:: 
    
    :ref:`pool-motor-overview`
        the motor overview 
    
..    :class:`~sardana.pool.poolmotor.PoolMotor`
..        the motor class :term:`API`

    :class:`~sardana.tango.pool.Motor.Motor`
        the motor tango device :term:`API`

