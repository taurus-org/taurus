.. _pool-motor-overview:

.. currentmodule:: sardana.pool

==================
Motor overview
==================

The Tango_ interface
^^^^^^^^^^^^^^^^^^^^^^^^^^

The motor interface is a first approach of what could be a complete
motor interface. It is statically linked with the Pool device server
and supports several members (Tango_ attributes) and methods (Tango_ commands).
The motor interface is always the same whatever the hardware is. It is the 
"job" of the *controller* to access the underlying hardware using the 
communication link supported by the motor controller hardware (network link,
serial line, etc.).

.. image:: /_static/motor.png

The controller code has a well-defined interface and can be written
using Python_ or C++. In both cases, it will be dynamically loaded into the 
sardana server process.

The motor controller :term:`API` can be found :class:`here <MotorController>`.

The states
""""""""""

The motor interface knows five states which are *On*, *Moving*, *Alarm*,
*Fault* and *Unknown*. A motor is in *Moving* state when it is
moving! It is in *Alarm* state when it has reached one of the limit
switches and is in *Fault* if its controller software is not available
(impossible to load it) or if a fault is reported from the hardware
controller. The motor is in the *Unknown* state if an exception occurs
during the communication between the pool and the hardware controller.
When the motor is in *Alarm* state, its status will indicate which limit
switches is active. 

The commands
""""""""""""

The motor interface supports 3 commands on top of the Tango_ classical
*Init()*, *State()* and *Status()* commands. These commands are summarized in the
following table:

==============  ================  ================
Command name    Input data type   Output data type
==============  ================  ================
Abort           void              void            
DefinePosition  Tango::DevDouble  void            
SaveConfig      void              void            
==============  ================  ================

- **Abort** : It aborts a running motion. This command does not have input or
  output argument.

- **DefinePosition** : Loads a position into controller. It has one input argument which is
  the new position value (a double). It is allowed only in the *On* or
  *Alarm* states. The unit used for the command input value is the
  physical unit: millimeters or milli-radians. It is always an absolute
  position.

- **SaveConfig** : Write some of the motor parameters in database. Today, it writes the
  motor *acceleration*, *deceleration*, *base_rate* and *velocity* into database
  as motor device properties. It is allowed only in the *On* or *Alarm*
  states

The classical Tango_ *Init()* command destroys the motor and re-creates it.


The attributes
""""""""""""""

The motor interface supports several attributes which are summarized
in the following table:

==============  =================  ===========  ========  =========  ==========
Name            Data type          Data format  Writable  Memorized  Ope/Expert  
==============  =================  ===========  ========  =========  ==========
Position        Tango::DevDouble   Scalar       R/W       No *       Ope         
DialPosition    Tango::DevDouble   Scalar       R         No         Exp         
Sign            Tango::DevLong     Scalar       R/W       Yes        Exp
Offset          Tango::DevDouble   Scalar       R/W       Yes        Exp         
Acceleration    Tango::DevDouble   Scalar       R/W       No         Exp         
Base_rate       Tango::DevDouble   Scalar       R/W       No         Exp         
Deceleration    Tango::DevDouble   Scalar       R/W       No         Exp         
Velocity        Tango::DevDouble   Scalar       R/W       No         Exp         
Limit_Switches  Tango::DevBoolean  Spectrum     R         No         Exp         
SimulationMode  Tango::DevBoolean  Scalar       R         No         Exp         
Step_per_unit   Tango::DevDouble   Scalar       R/W       Yes        Exp         
Backlash        Tango::DevLong     Scalar       R/W       Yes        Exp         
==============  =================  ===========  ========  =========  ==========

- **Position** : This is read-write scalar double attribute. With the classical Tango
  min and max_value attribute properties, it is easy to define
  authorized limit for this attribute. See the definition of the
  DialPosition and Offset attributes to get a precise definition of the
  meaning of this attribute. It is not allowed to read or write this
  attribute when the motor is in *Fault* or *Unknown* state. It is also not
  possible to write this attribute when the motor is already *Moving*. **The unit used for this attribute is the physical unit: millimeters or
  milli-radian. It is always an** **absolute** **position.** The value of this attribute is memorized in the Tango_ database but not
  by the default Tango_ system memorization. See chapter
  XXX: Unknown inset LatexCommand \ref{sub:Archiving-motor-position}:
  for details about motor position archiving.

- **DialPosition** : This attribute is the motor dial position. The following formula
  links together the Position, DialPosition, Sign and Offset attributes: ::
  
    Position = Sign * DialPosition + Offset
  
  This allows to have the motor position centered around any position
  defined by the Offset attribute (classically the X ray beam position).
  It is a read only attribute. To set the motor position, the user has
  to use the Position attribute. It is not allowed to read this
  attribute when the motor is in *Fault* or *Unknown* mode. The unit used
  for this attribute is the physical unit: millimeters or milli-radian.
  It is also always an **absolute** position.

- **Offset** : The offset to be applied in the motor position computation. By
  default set to 0. It is a memorized attribute. It is not allowed to
  read or write this attribute when the motor is in *Fault*, *Moving* or
  *Unknown* mode.

- **Sign** : The sign to be applied in the motor position computation. By
  default set to 1. It is a memorized attribute. It is not allowed to
  read or write this attribute when the motor is in *Fault*, *Moving* or
  *Unknown* mode.

- **Acceleration** : This is an expert read-write scalar double attribute. This parameter
  value is written in database when the SaveConfig command is executed.
  It is not allowed to read or write this attribute when the motor is in
  *Fault* or *Unknown* state.

- **Deceleration** : This is an expert read-write scalar double attribute. This parameter
  value is written in database when the SaveConfig command is executed.
  It is not allowed to read or write this attribute when the motor is in
  *Fault* or *Unknown* state.

- **Base_rate** : This is an expert read-write scalar double attribute. This parameter
  value is written in database when the SaveConfig command is executed.
  It is not allowed to read or write this attribute when the motor is in
  *Fault* or *Unknown* state.

- **Velocity** : This is an expert read-write scalar double attribute. This parameter
  value is written in database when the SaveConfig command is executed.
  It is not allowed to read or write this attribute when the motor is in
  *Fault* or *Unknown* state.

- **Limit_Switches** : Three limit switches are managed by this attribute. Each of the
  switch are represented by a boolean value: False means inactive while
  True means active. It is a read only attribute. It is not possible to
  read this attribute when the motor is in *Unknown* mode. It is a
  spectrum attribute with 3 values which are:

    - Data[0] : The Home switch value
    
    - Data[1] : The Upper switch value
    
    - Data[2] : The Lower switch value
    
    
- **SimulationMode** : This is a read only scalar boolean attribute. When set, all motion
  requests are not forwarded to the software controller and then to the
  hardware. When set, the motor position is simulated and is immediately
  set to the value written by the user. To set this attribute, the user
  has to used the pool device Tango_ interface. The value of the
  position, acceleration, deceleration, base_rate, velocity and offset
  attributes are memorized at the moment this attribute is set. When
  this mode is turned off, if the value of any of the previously
  memorized attributes has changed, it is reapplied to the memorized
  value. It is not allowed to read this attribute when the motor is in
  *Fault* or *Unknown* states.

- **Step_per_unit** : This is the number of motor step per millimeter or per degree. It is
  a memorized attribute. It is not allowed to read or write this
  attribute when the motor is in *Fault* or *Unknown* mode. It is also not
  allowed to write this attribute when the motor is *Moving*. The default
  value is 1.

- **Backlash** : If this attribute is defined to something different than 0, the
  motor will always stop the motion coming from the same mechanical
  direction. This means that it could be possible to ask the motor to go
  a little bit after the desired position and then to return to the
  desired position. The attribute value is the number of steps the motor
  will pass the desired position if it arrives from the "wrong"
  direction. This is a signed value. If the sign is positive, this means
  that the authorized direction to stop the motion is the increasing
  motor position direction. If the sign is negative, this means that the
  authorized direction to stop the motion is the decreasing motor
  position direction. It is a memorized attribute. It is not allowed to
  read or write this attribute when the motor is in *Fault* or *Unknown*
  mode. It is also not allowed to write this attribute when the motor is
  *Moving*. Some hardware motor controllers are able to manage this
  backlash feature. If it is not the case, the motor interface will
  implement this behavior.

All the motor devices will have the already described attributes but
some hardware motor controller supports other features which are not
covered by this list of pre-defined attributes. Using Tango_ dynamic
attribute creation, a motor device may have extra attributes used to
get/set the motor hardware controller specific features. The main
characteristics of these extra attributes are : 

- Name defined by the motor controller software (See next chapter)

- Data type is BOOLEAN, L*On*G, DOUBLE or STRING defined by the motor
  controller software (See next chapter)

- The data format is always Scalar

- The write type is READ or READ_WRITE defined by the motor controller
  software (See next chapter). If the write type is READ_WRITE, the
  attribute is memorized by the Tango_  layer


The properties
"""""""""""""""

Each motor device has a set of properties. Five of these properties
are automatically managed by the pool software and must **NOT** be changed
by the user. These properties are named:
- id,
- ctrl_id
- axis
- _Acceleration
- _Velocity
- _Base_rate
- _Deceleration

The user properties are:

======================  =============
Property name           Default value
======================  =============
Sleep_before_last_read  0            
======================  =============

This property defines the time in milliseconds that the software
managing a motor movement will wait between it detects the end of the
motion and the last motor position reading.
It is typically used for motors that move mechanics which have an instability
time after each motion.

Getting motor state and limit switches using event
""""""""""""""""""""""""""""""""""""""""""""""""""

The simplest way to know if a motor is moving is to survey its state.
If the motor is moving, its state will be *Moving*. When the motion is
over, its state will be back to *On* (or *Alarm* if a limit switch has
been reached). The pool motor interface allows client interested by
motor state or motor limit switches value to use the Tango_ event
system subscribing to motor state change event. As soon as a motor
starts a motion, its state is changed to *Moving* and an event is sent.
As soon as the motion is over, the motor state is updated ans another
event is sent. In the same way, as soon as a change in the limit
switches value is detected, a change event is sent to client(s) which
have subscribed to change event on the Limit_Switches attribute. 

Reading the motor position attribute
""""""""""""""""""""""""""""""""""""

For each motor, the key attribute is its position. Special care has
been taken on this attribute management. When the motor is not moving,
reading the Position attribute will generate calls to the controller
and therefore hardware access. When the motor is moving, its position
is automatically read every 100 milliseconds and stored in the Tango_
polling buffer. This means that a client reading motor Position
attribute while the motor is moving will get the position from the
Tango_ polling buffer and will not generate extra controller calls. It
is also possible to get a motor position using the Tango_ event system.
When the motor is moving, an event is sent to the registered clients
when the change event criterion is true. By default, this change event
criterion is set to be a difference in position of 5. It is tunable on
a motor basis using the classical motor Position attribute abs_change
property or at the pool device basis using its DefaultMotPos_AbsChange
property. Anyway, not more than 10 events could be sent by second.
Once the motion is over, the motor position is made unavailable from
the Tango_ polling buffer and is read a last time after a tunable
waiting time (Sleep_bef_last_read property). A forced change event
with this value is sent to clients using events. 

.. _ALBA: http://www.cells.es/
.. _ANKA: http://http://ankaweb.fzk.de/
.. _ELETTRA: http://http://www.elettra.trieste.it/
.. _ESRF: http://www.esrf.eu/
.. _FRMII: http://www.frm2.tum.de/en/index.html
.. _HASYLAB: http://hasylab.desy.de/
.. _MAX-lab: http://www.maxlab.lu.se/maxlab/max4/index.html
.. _SOLEIL: http://www.synchrotron-soleil.fr/


.. _Tango: http://www.tango-controls.org/
.. _PyTango: http://packages.python.org/PyTango/
.. _Taurus: http://packages.python.org/taurus/
.. _QTango: http://www.tango-controls.org/download/index_html#qtango3
.. _Qt: http://qt.nokia.com/products/
.. _PyQt: http://www.riverbankcomputing.co.uk/software/pyqt/
.. _PyQwt: http://pyqwt.sourceforge.net/
.. _Python: http://www.python.org/
.. _IPython: http://ipython.scipy.org/
.. _ATK: http://www.tango-controls.org/Documents/gui/atk/tango-application-toolkit
.. _Qub: http://www.blissgarden.org/projects/qub/
.. _numpy: http://numpy.scipy.org/
.. _SPEC: http://www.certif.com/
.. _EPICS: http://www.aps.anl.gov/epics/
