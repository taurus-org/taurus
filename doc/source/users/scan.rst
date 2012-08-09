
.. currentmodule:: sardana.macroserver.macros.scan

.. _sardana-users-scan:

=====
Scans
=====

Perhaps the most used type of macro is the scan macros. In general terms, we call *scan* to a macro that moves one or more motors and adquires data along the path of the motor(s).

.. note:: Sardana provides a :ref:`Scan Framework <macroserver-macros-scanframework>`
   for developing scan macros so that the scan macros behave in a consistent way.
   Unless otherwise especified, the following discusion refers to scan macros
   based on such framework.

The various scan macros mostly differ in how many motors are moved and the definition of their paths.

Typically, the selection of which data is going to be acquired depends on the Active :ref:`Measurement group <sardana-measurement-group>` and is *not* fixed by the macro itself (although there is no limitation in this sense).

Depending on whether the motors are stopped before acquiring the data or not, we can classify the scan macros in *step* scans or *continuous* scans, respectively.


Step scans
----------

In a step scan, the motors (or  motor) are moved to given points, and once they reach each point they stop. Then, one or more channels are acquired for a certain amount of time, and only when the data acquisition is finished, the motors proceed to the next point.

In this way, the position associated to a data readout is well known and constant along the acquisition time.

Some examples of step scan macros are: :class:`~sardana.macroserver.macros.scan.ascan`, :class:`~sardana.macroserver.macros.scan.a2scan`, ... :class:`~sardana.macroserver.macros.scan.dscan`, :class:`~sardana.macroserver.macros.scan.d2scan`, ... :class:`~sardana.macroserver.macros.scan.mesh`. 

Continuous scans
----------------

In a continuous scan, the motors are not stopped for acquisition, which therefore takes place while the motors are moving. The most common reason for using this type of scan is optimizing the acquisition time by not having to wait for motors to accelerate and decelerate between acquisitions.

.. note:: The synchronization of movement and acquisition can be done via
   hardware or via software. Currently Sardana only provides an interface for
   software-synchronized continuous scans. An API abstracting the specificities
   of hardware-synchronized systems has not been yet implemented, and therefore
   it cannot be supported by Sardana yet.

The (software-synchronized) continuous scans introduce some constraints and issues that should be considered.

#. If a continuous scan involves moving more than one motor simultaneously (as it is done, e.g. in :class:`~sardana.macroserver.macros.scan.a2scan`), then the movements of the motors should be synchronized so that they all start their path at the same time and finish it at the same time. 
#. If motors do not maintain a constant velocity along the path of their movement, the trajectories followed when using more than one motor may not be linear.
#. While in step scans it is possible to scan two pseudomotors that access the same physical motors (e.g. the *gap* and *offset* of a slit, being both pseudomotors accessing the same physical motors attached to each blade of the slit), in a continuous scan the motions cannot be decoupled in a synchronized way.
#. In order to optimize the acquisition time, Sardana attempts to perform as many acquisitions aas allowed during the scan time. Due to the uncertainty in the delay times involved, it is not possible to knw before hand how many acquisitions will be completed. In other words, the number of acquired points along a ascanc is not fixed (but it is guaranteed to as large as possible).
  

In order to address the first two issues, the :ref:`scan framework <macroserver-macros-scanframework>` attempts the following:

* If the motors support changing their velocity, Sardana will adjust the velocities of the motors so that they all start and finish the required path simultaneously. For motors that specify a range of allowed velocities, this range will be used (for motors that do not specify a maximum allowed velocity, the current "top velocity" will be assumed to be the maximum)
* For motors that can maintain a constant velocity after an acceleration phase (this is the case for most physical motors), Sardana will transparently extend the user-given path both at the beginning and the end in order to allow for the motors to move at constant velocity along all the user defined path (i.e., the motors are allowed time and room to accelerate before reaching the start of the path and to decelerate after the end of the nominal path selected by the user) 
   

Some examples of continuous scan macros are: :class:`~sardana.macroserver.macros.scan.ascanc`, :class:`~sardana.macroserver.macros.scan.a2scanc`, ... :class:`~sardana.macroserver.macros.scan.dscanc`, :class:`~sardana.macroserver.macros.scan.d2scanc`, ... :class:`~sardana.macroserver.macros.scan.meshc`. 

.. seealso:: For more information about the implementation details of the scan
             macros in Sardana, see 
             :ref:`scan framework <macroserver-macros-scanframework>`

