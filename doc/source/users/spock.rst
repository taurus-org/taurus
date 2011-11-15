
.. _sardana-spock:

======
Spock
======

*Spock* is the prefered :term:`CLI` for sardana.

*Spock* itself is an IPython_ based :term:`CLI` for pure PyTango_.
This is what we will call "pure Spock" [#]_ in this document.
*Spock* as been extended in sardana to provide a customized interface for executing
macros and automatic access to sardana elements. This is what we will loosly call
*spock* in this document.

*Spock* tries to mimic SPEC_'s command line interface. Most SPEC_ commands
are available from *spock* console.

.. figure:: /_static/spock_snapshot01.png
    :height: 600
    
    Spock :term:`CLI` in action

Starting spock from the command line
-------------------------------------

To start *spock* just type in the command line::

    marge@machine02:~$ spock

This will start *spock* with a "default profile" for the user your are logged with.
There may be many sardana servers running on your system so the first time you
start *spock*, it will ask you to which sardana system you want to connect to by
asking to which of the existing doors you want to use::

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
-------------------------------------

*Spock* allows each user to start a spock session with different configurations
(known in *spock* as *profiles*). All you have to do is start *spock* with::

    spock -p <profile name>
    
Example::

    marge@machine02:~$ spock -p D1

The first time a certain profile is used you will be asked to which door you want
to connect to (see previous chapter).

Executing macros
-----------------

Executing sardana macros in *spock* is the most useful feature of *spock*. It is very
simple to execute a macro: just type the macro name followed by a space separated
list of parameters (if the macro has any parameters). For example, one of the most
used macros is the **wa** (stands for "where all") that shows all current motor
positions. To execute it just type:

.. sourcecode:: spock

    LAB-01-D01 [1]: wa
    Current Positions  (user, dial)

       Energy       Gap    Offset
     100.0000   43.0000  100.0000
     100.0000   43.0000  100.0000
     
A similar macro exists that only shows the desired motor positions (**wm**):

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

To get the list of all existing macros: **lsdef**:

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

Stopping macros
---------------

Some macros may take a long time to execute. To stop a macro in the middle of
its executing type :kbd:`Control+c`.

Macros that move motors or acquire data from sensors will automatically stop all
motion and/or all acquisition.

Exiting spock
-------------

To exit *spock* type :kbd:`Control+d` or :samp:`exit()` inside a *spock* console.

Getting help
------------

*Spock* not only knows all the macros the sardana server can run but it also
information about each macro parameters, result and documentation.
Therefore it can give you precise help on each macro. To get help about a certain
macro just type the macro name directly followed by a question mark('?'):

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
--------------

A single motor may be moved using the *mv** *motor* *position* macro. Example:

.. sourcecode:: spock

    LAB-01-D01 [1]: mv gap 50

will move the *gap* motor to 50 millimeters. The prompt only comes back after
the motion as finished.

Alternatively, you can have the motor position displayed on the screen as it is
moving by invoking the **umv** macro. To stop the motor(s) before they have
finished moving, type :kbd:`Control+c`.

You can use the **mvr** *motor* *relative_position* macro to move a motor
relative to its current position:

.. sourcecode:: spock

    LAB-01-D01 [1]: mvr gap 2
    
will move *gap* by one millimeter.


Using spock as a Python_ console
---------------------------------

You can write any Python_ code inside a *spock* console since spock uses
IPython_ as a command line interpreter. For example, the following will work
inside a *spock* console:

.. sourcecode:: spock

    LAB-01-D01 [1]: def f():
               ...:     print("Hello, World!")
               ...:
               ...:
    
    LAB-01-D01 [2]: f()
    Hello, World!
    

Using spock as a Tango_ console
---------------------------------

As metioned in the beggining of this chapter, the sardana *spock* is an extension
of PyTango_ 's "pure spock" console. Therefore all Tango_ features from "pure spock"
are automatically available on the sardana *spock* console. For example, creating
a :class:`~PyTango.DeviceProxy` will work inside the sardana *spock* console:

.. sourcecode:: spock

    LAB-01-D01 [1]: tgtest = PyTango.DeviceProxy("sys/tg_test/1")
    
    LAB-01-D01 [2]: print( tgtest.state() )
    RUNNING

.. rubric:: Footnotes

.. [#] The PyTango_ spock documentation can be found :ref:`here <spock>`

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
.. _IPython: http://ipython.scipy.org/
.. _ATK: http://www.tango-controls.org/Documents/gui/atk/tango-application-toolkit
.. _Qub: http://www.blissgarden.org/projects/qub/
.. _numpy: http://numpy.scipy.org/
.. _SPEC: http://www.certif.com/
.. _EPICS: http://www.aps.anl.gov/epics/
