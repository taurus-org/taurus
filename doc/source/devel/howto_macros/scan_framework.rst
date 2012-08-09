
.. _macroserver-macros-scanframework:

===============
Scan Framework
===============

In general terms, we call *scan* to a macro that moves one or more motors and
adquires data along the path of the motor(s).

While a scan macro could be written from scratch, Sardana provides a higher-
level API (the *scan framework*) that greatly simplifies the development of scan
macros by taking care of the details about synchronization of motors and of
acquisitions.


