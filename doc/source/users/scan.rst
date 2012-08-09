
.. currentmodule:: sardana.macroserver.macros.scan

.. _sardana-users-scan:

===============
Scans 
===============

Perhaps the most used type of macro is the scan macros. In general terms, 'we
call *scan* to a macro that moves one or more motors and adquires data along the
path of the motor(s)'.

The various scan macros mostly differ in how many motors are moved and the
definition of their paths.

Typically, the selection of which data is going to be acquired depends on the
Active :ref:`Measurement group <sardana-measurement-group>` and is therefore in
most cases *not* fixed by the macro itself (although there is no limitation in
this sense).

Depending on whether the motors are stopped before acquiring the data or not, we
can classify the scan macros in 'step' scans or 'continuous' scans,
respectively.


Step scans
----------

In a step scan, the motors (or  motor) are moved to given points, and once they
reach each point they stop. Then, one or more channels are acquired for a
certain amount of time, and only when the data acquisition is finished, the motors
proceed to the next point.

In this way, the position associated to a data readout is well known and
constant along the acquisition time.

Typical examples of step scan macros are: :class:`~sardana.macroserver.macros.scan.ascan`, 
:class:`~sardana.macroserver.macros.scan.a2scan`, ... 
:class:`~sardana.macroserver.macros.scan.dscan`, 
:class:`~sardana.macroserver.macros.scan.d2scan`, ... 
:class:`~sardana.macroserver.macros.scan.mesh`. 

Continuous scans
----------------

In a continuous scan, the motors are not stopped for acquisition, which
therefore takes place while the motors are moving. The most common reason for
using this type of scan is optimizing the acquisition time by not having to wait
for motors to accelerate and decelerate between acquisitions.

But there are several details that must be considered

Typical examples of continuous scan macros are: :class:`~sardana.macroserver.macros.scan.ascanc`, 
:class:`~sardana.macroserver.macros.scan.a2scanc`, ... 
:class:`~sardana.macroserver.macros.scan.dscanc`, 
:class:`~sardana.macroserver.macros.scan.d2scanc`, ... 
:class:`~sardana.macroserver.macros.scan.meshc`. 

.. seealso:: For more information about the implementation details of the scan
             macros in Sardana, see 
             :ref:`scan framework <macroserver-macros-scanframework>`

