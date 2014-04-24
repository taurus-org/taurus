
.. _sardana-spock:

=====
Spock
=====

*Spock* is the prefered :term:`CLI` for sardana. It is based on IPython_. Spock
automatically loads other IPython_ extensions like the ones for PyTango_ and
*pylab*. It as been extended in sardana to provide a customized interface for
executing macros and automatic access to sardana elements.

Spock tries to mimic SPEC_'s command line interface. Most SPEC_ commands are
available from spock console.

.. figure:: /_static/spock_snapshot01.png
    :height: 600
    :align: center
    
    Spock :term:`CLI` in action

Starting spock from the command line
------------------------------------

To start spock just type in the command line::

    marge@machine02:~$ spock

This will start spock with a "default profile" for the user your are logged
with. There may be many sardana servers running on your system so the first
time you start spock, it will ask you to which sardana system you want to
connect to by asking to which of the existing doors you want to use::

    marge@machine02:~$ spock
    Profile 'spockdoor' does not exist. Do you want to create one now ([y]/n)? 
    Available Door devices from homer:10000 :
    On Sardana LAB-01:
        LAB-01-D01 (running)
        LAB-01-D02 (running)
    On Sardana LAB-02:
        LAB-02-D01
    Please select a Door from the list? LAB-01-D01
    Storing ipy_profile_spockdoor.py in /home/marge/.ipython... [DONE]

.. note::
    If only one Door exists in the entire system, spock will automatically
    connect to that door thus avoiding the previous questions.

Afterward, spock :term:`CLI` will start normally:

.. sourcecode:: spock

    Spock 7.2.1 -- An interactive sardana client.

    help      -> Spock's help system.
    object?   -> Details about 'object'. ?object also works, ?? prints more.

    Spock's sardana extension 1.0 loaded with profile: spockdoor (linked to door 'LAB-01-D01')

    LAB-01-D01 [1]: 

Starting spock with a custom profile
------------------------------------

spock allows each user to start a spock session with different configurations
(known in spock as *profiles*). All you have to do is start spock with 
the profile name as an option. 

If you use ipython version > 0.10 you can do it using **--profile** option::

    spock --profile=<profile name>
    
Example::

    marge@machine02:~$ spock --profile=D1
    
    
Otherwise (ipython version 0.10) you can do it using **-p** option::

    spock -p <profile name>
    
Example::

    marge@machine02:~$ spock -p D1

The first time a certain profile is used you will be asked to which door you
want to connect to (see previous chapter).

Spock IPython_ Primer
---------------------

As mentioned before, spock console is based on IPython_. Everything you can do
in IPython is available in spock. The IPython_ documentation provides excelent
tutorials, tips & tricks, cookbooks, videos, presentations and reference guide.
For comodity we summarize some of the most interesting IPython_ chapters here:

.. hlist::
    :columns: 2

    * `IPython web page <http://ipython.org/>`_
    * :ref:`tutorial`
    * :ref:`tips`
    * :ref:`command_line_options`

Executing macros
----------------

Executing sardana macros in spock is the most useful feature of spock. It is
very simple to execute a macro: just type the macro name followed by a space
separated list of parameters (if the macro has any parameters). For example,
one of the most used macros is the
:class:`~sardana.macroserver.macros.standard.wa` (stands for "where all") that
shows all current motor positions. To execute it just type:

.. sourcecode:: spock

    LAB-01-D01 [1]: wa
    
    Current Positions  (user, dial)

       Energy       Gap    Offset
     100.0000   43.0000  100.0000
     100.0000   43.0000  100.0000

(:term:`user` for :term:`user position` (number above); :term:`dial` for
:term:`dial position` (number below).)
   
A similar macro exists that only shows the desired motor positions
(:class:`~sardana.macroserver.macros.standard.wm`):

.. sourcecode:: spock

    LAB-01-D01 [1]: wm gap offset
                    Gap     Offset
    User                          
     High         500.0      100.0
     Current      100.0       43.0
     Low            5.0     -100.0
    Dial                          
     High         500.0      100.0
     Current      100.0       43.0
     Low            5.0     -100.0

To get the list of all existing macros use
:class:`~sardana.macroserver.macros.expert.lsmac`:

.. sourcecode:: spock

    LAB-01-D01 [1]: lsdef
                   Name        Module                                            Brief Description
    ------------------- ------------- ------------------------------------------------------------
                 a2scan         scans two-motor scan.     a2scan scans two motors, as specifi[...]
                 a2scan         scans three-motor scan .     a3scan scans three motors, as sp[...]
                  ascan         scans Do an absolute scan of the specified motor.     ascan s[...]
                defmeas        expert                               Create a new measurement group
                  fscan         scans N-dimensional scan along user defined paths.     The mo[...]
                    lsa         lists                                   Lists all existing objects
                    lsm         lists                                             Lists all motors
                  lsmac        expert                                            Lists all macros.
                     mv      standard                   Move motor(s) to the specified position(s)
                    mvr      standard            Move motor(s) relative to the current position(s)
                     wa      standard                                     Show all motor position.
                     wm      standard                   Show the position of the specified motors.
    <...>

Miscellaneous
~~~~~~~~~~~~~

    - :class:`~sardana.macroserver.macros.lists.lsm` shows the list of
      motors.
    - :class:`~sardana.macroserver.macros.lists.lsct` shows the list of
      counters.
    - :class:`~sardana.macroserver.macros.lists.lsmeas` shows the list of
      measurement groups
    - :class:`~sardana.macroserver.macros.lists.lsctrl` shows the list of
      controllers
    - :class:`~sardana.macroserver.macros.expert.sar_info` *object*
      displays detailed information about an element

Stopping macros
---------------

Some macros may take a long time to execute. To stop a macro in the middle of
its execution type :kbd:`Control+c`.

Macros that move motors or acquire data from sensors will automatically stop all
motion and/or all acquisition.

Exiting spock
-------------

To exit spock type :kbd:`Control+d` or :samp:`exit()` inside a spock console.

Getting help
------------

spock not only knows all the macros the sardana server can run but it also
information about each macro parameters, result and documentation. Therefore it
can give you precise help on each macro. To get help about a certain macro just
type the macro name directly followed by a question mark('?'):

.. sourcecode:: spock

    LAB-01-D01 [1]: ascan?
    
    Syntax:
            ascan <motor> <start_pos> <final_pos> <nr_interv> <integ_time>
    
    Do an absolute scan of the specified motor.
        ascan scans one motor, as specified by motor. The motor starts at the
        position given by start_pos and ends at the position given by final_pos.
        The step size is (start_pos-final_pos)/nr_interv. The number of data points collected
        will be nr_interv+1. Count time is given by time which if positive,
        specifies seconds and if negative, specifies monitor counts. 
    
    Parameters:
            motor : (Motor) Motor to move
            start_pos : (Float) Scan start position
            final_pos : (Float) Scan final position
            nr_interv : (Integer) Number of scan intervals
            integ_time : (Float) Integration time
    
Moving motors
-------------

A single motor may be moved using the
:class:`~sardana.macroserver.macros.standard.mv` *motor* *position* macro.
Example:

.. sourcecode:: spock

    LAB-01-D01 [1]: mv gap 50

will move the *gap* motor to 50. The prompt only comes back after the motion as
finished.

Alternatively, you can have the motor position displayed on the screen as it is
moving by using the :class:`~sardana.macroserver.macros.standard.umv` macro
instead. To stop the motor(s) before they have finished moving, type
:kbd:`Control+c`.

You can use the :class:`~sardana.macroserver.macros.standard.mvr` *motor*
*relative_position* macro to move a motor relative to its current position:

.. sourcecode:: spock

    LAB-01-D01 [1]: mvr gap 2
    
will move *gap* by two user units.

Counting
--------

You can count using the :class:`~sardana.macroserver.macros.standard.ct` *value*
macro. Without arguments, this macro counts for one second using the active
measurement group set by the environment variable *ActiveMntGrp*.


.. sourcecode:: spock

    Door_lab-01_1 [1]: ct 1.6

    Wed Jul 11 11:47:55 2012

      ct01  =         1.6
      ct02  =         3.2
      ct03  =         4.8
      ct04  =         6.4
    
To see the list of available measurement groups type
:class:`~sardana.macroserver.macros.lists.lsmeas`. The active measuremnt group
is marked with an asterisk (*):

.. sourcecode:: spock

    Door_lab-01_1 [1]: lsmeas

      Active        Name   Timer Experim. channels                                          
     -------- ---------- ------- -----------------------------------------------------------
        *       mntgrp01    ct01 ct01, ct02, ct03, ct04                                     
                mntgrp21    ct04 ct04, pcII0, pcII02                                        
                mntgrp24    ct04 ct04, pcII0

to switch active measurement groups type
:class:`~sardana.macroserver.macros.env.senv` **ActiveMntGrp** *mg_name*.

You can also create, modify and select measurement groups using the
:class:`~sardana.spock.magic.expconf` command

Scanning
--------

Sardana provides a catalog of different standard scan macros. Absolute-position
motor scans such as :class:`~sardana.macroserver.macros.scan.ascan`,
:class:`~sardana.macroserver.macros.scan.a2scan` and
:class:`~sardana.macroserver.macros.scan.a3scan` move one, two or three motors
at a time. Relative-position motor scans are
:class:`~sardana.macroserver.macros.scan.dscan`,
:class:`~sardana.macroserver.macros.scan.d2scan` and
:class:`~sardana.macroserver.macros.scan.d3scan`. The relative-position scans
all return the motors to their starting positions after the last point. Two
motors can be scanned over a grid of points using the
:class:`~sardana.macroserver.macros.scan.mesh` scan. 

*Continuous* versions exist of many of the standard scan macros (e.g.
:class:`~sardana.macroserver.macros.scan.ascanc`,
:class:`~sardana.macroserver.macros.scan.d3scanc`,
:class:`~sardana.macroserver.macros.scan.meshc`,...). The continuous scans
differ from their standard counterparts (also known as *step* scans) in that
the data acquisition is done without stopping the motors. Continuous scans are
generally faster but less precise than step scans, and some details must be
considered (see :ref:`sardana-users-scan`).

As it happens with :class:`~sardana.macroserver.macros.standard.ct`, the scan
macros will also use the active measurement group to decide which experiment
channels will be involved in the operation.

Here is the output of performing an
:class:`~sardana.macroserver.macros.scan.ascan` of the gap in a slit:

.. sourcecode:: spock

    LAB-01-D01 [1]: ascan gap 0.9 1.1 20 1
    ScanDir is not defined. This operation will not be stored persistently. Use "senv ScanDir <abs directory>" to enable it
    Scan #4 started at Wed Jul 11 12:56:47 2012. It will take at least 0:00:21
     #Pt No    gap       ct01      ct02      ct03
      0        0.9          1       4604      8939
      1       0.91          1       5822      8820
      2       0.92          1       7254      9544
      3       0.93          1       9254      8789
      4       0.94          1      11265      8804
      5       0.95          1      13583      8909
      6       0.96          1      15938      8821
      7       0.97          1      18076      9110
      8       0.98          1      19638      8839
      9       0.99          1      20825      8950
     10          1          1      21135      8917
     11       1.01          1      20765      9013
     12       1.02          1      19687      9135
     13       1.03          1      18034      8836
     14       1.04          1      15876      8901
     15       1.05          1      13576      8933
     16       1.06          1      11328      9022
     17       1.07          1       9244      9205
     18       1.08          1       7348      8957
     19       1.09          1       5738      8801
     20        1.1          1       4575      8975
    Scan #4 ended at Wed Jul 11 12:57:18 2012, taking 0:00:31.656980 (dead time was 33.7%)



Scan storage
~~~~~~~~~~~~

As you can see, by default, the scan is not recorded into any file. To store
your scans in a file, you must set the environment variables **ScanDir** and
**ScanFile**:

.. sourcecode:: spock

    LAB-01-D01 [1]: senv ScanDir /tmp
    ScanDir = /tmp
    
    LAB-01-D01 [2]: senv ScanFile scans.h5
    ScanFile = scans.h5
    
Sardana will activate a proper recorder to store the scans persistently
(currently, *.h5* will store in `NeXus`_ format. All other extensions are
interpreted as `SPEC`_ format).

You can also store in multiples files by assigning the **ScanFile** with a list
of files:
    
.. sourcecode:: spock

    LAB-01-D01 [2]: senv ScanFile "['scans.h5', 'scans.dat']"
    ScanFile = ['scans.h5', 'scans.dat']

Viewing scan data
~~~~~~~~~~~~~~~~~

Sardana provides a scan data viewer for scans which were stored in a `NeXus`_
file. Without arguments, :class:`~sardana.macroserver.macros.scan.showscan`
will show you the result of the last scan in a :term:`GUI`:

.. figure:: /_static/spock_snapshot02.png
    :height: 600
    
    Scan data viewer in action

:class:`~sardana.macroserver.macros.scan.showscan` *scan_number* will display
data for the given scan number.

The history of scans is available through the
:class:`~sardana.macroserver.macros.scan.scanhist` macro:

.. sourcecode:: spock

    LAB-01-D01 [1]: scanhist
       #                           Title            Start time              End time        Stored
     --- ------------------------------- --------------------- --------------------- -------------
       1    dscan mot01 20.0 30.0 10 0.1   2012-07-03 10:35:30   2012-07-03 10:35:30   Not stored!
       3    dscan mot01 20.0 30.0 10 0.1   2012-07-03 10:36:38   2012-07-03 10:36:43   Not stored!
       4   ascan gap01 10.0 100.0 20 1.0              12:56:47              12:57:18   Not stored!
       5     ascan gap01 1.0 10.0 20 0.1              13:19:05              13:19:13      scans.h5


Using spock as a Python_ console
--------------------------------

You can write any Python_ code inside a spock console since spock uses IPython_
as a command line interpreter. For example, the following will work inside a
spock console:

.. sourcecode:: spock

    LAB-01-D01 [1]: def f():
               ...:     print("Hello, World!")
               ...:
               ...:
    
    LAB-01-D01 [2]: f()
    Hello, World!
    

Using spock as a Tango_ console
-------------------------------

As metioned in the beggining of this chapter, the sardana spock automatically
activates the PyTango_ 's ipython console extension. Therefore all Tango_
features are automatically available on the sardana spock console. For example,
creating a :class:`~PyTango.DeviceProxy` will work inside the sardana spock
console:

.. sourcecode:: spock

    LAB-01-D01 [1]: tgtest = PyTango.DeviceProxy("sys/tg_test/1")
    
    LAB-01-D01 [2]: print( tgtest.state() )
    RUNNING

.. rubric:: Footnotes

.. [#] The PyTango_ ipython documentation can be found :ref:`here <itango>`

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
.. _`PyTango installation steps`: http://packages.python.org/PyTango/start.html#getting-started
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
.. _NeXus: http://www.nexusformat.org/
