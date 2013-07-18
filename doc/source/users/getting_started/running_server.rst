.. _sardana-getting-started-running-server:

Running Sardana as a tango server
---------------------------------

.. note::

    if you have Tango <= 7.2.6 without all patches applied, Sardana server
    will not work due to a known bug. Please follow the instructions from
    :ref:`sardana-getting-started-running-servers-separately` instead.

Sardana is based on a client-server architecture. On the server part, sardana
can be setup with many different configurations. Advanced details on sardana
server configuration can be found here **<LINK>**.

This chapter describes how to run sardana server with it's simplest
configuration. The only decision you have to make is which name you will give
to your system. From here on *lab-01* will be used as the system name. Please
replace this name with your own system name whenever apropriate.

The sardana server is called (guess what) *Sardana*. To start the server just
type in the command line::

    homer@pc001:~$ Sardana lab-01

The first time the server is executed, it will inform you that server *lab-01*
is not registered and it will offer to register it. Just answer 'y'. This will
register a new instance of Sardana called *lab-01* and the server will be
started. You should get an output like this::

    homer@pc001:~$ Sardana lab-01
    lab-01 does not exist. Do you wish create a new one (Y/n) ? y
    DServer/Sardana/Lab-01 has no event channel defined in the database - creating it

That't it! You now have a running sardana server. Not very impressive, is it?
The :ref:`sardana-getting-started-running-cli` chapter describes how to start up a
:term:`CLI` application called *spock* which connects to the sardana server you
have just started through an object of type *Door* called *Door_lab-01_1*.

You can therefore skip the next chapter and go directly to 
:ref:`sardana-getting-started-running-cli`.

.. _sardana-getting-started-running-servers-separately:

Running Pool and MacroServer tango servers separately
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. note::

    You should only read this chapter if you have Tango <= 7.2.6
    without all patches applied. If you do, please follow in instructions from
    :ref:`sardana-getting-started-running-server` instead.

It is possible to separate sardana server into two different servers (in the
first sardana versions, this was actually the only way start the sardana
system). These servers are called *Pool* and *MacroServer*. The *Pool* server
takes care of hardware communication and *MacroServer* executes procedures
(macros) using a connection to Pool(s) server(s).

To start the Pool server just type in the command line::

    homer@pc001:~$ Pool lab-01

The first time the server is executed, it will inform you that server *lab-01*
is not registered and it will offer to register it. Just answer 'y'. This will
register a new instance of Pool called *lab-01* and the server will be
started. You should get an output like this::

    homer@pc001:~$ Pool lab-01
    lab-01 does not exist. Do you wish create a new one (Y/n) ? y
    DServer/Pool/Lab-01 has no event channel defined in the database - creating it

Next, start the MacroServer server in the command line::

    homer@pc001:~$ MacroServer lab-01

The first time the server is executed, it will inform you that server *lab-01*
is not registered and it will offer to register it. Just answer 'y'. Next, it
will ask you to which Pool(s) you want your MacroServer to communicate with.
Select the previously created Pool from the list, press :kbd:`Return` once and
:kbd:`Return` again to finish with Pool selection. This will register a new
instance of MacroServer called *lab-01* and the server will be started.
You should get an output like this::

    homer@pc001:~$ MacroServer lab-01
    lab-01 does not exist. Do you wish create a new one (Y/n) ? 
    Pool_lab-01_1 (a.k.a. Pool/lab-01/1) (running)
    Please select pool to connect to (return to finish): Pool_lab-01_1
    Please select pool to connect to (return to finish): 
    DServer/MacroServer/lab-01 has no event channel defined in the database - creating it


.. _numpy: http://numpy.scipy.org/
.. _PLY: http://www.dabeaz.com/ply/
.. _Python(x,y): http://code.google.com/p/pythonxy/
.. _Python: http://www.python.org/

.. _SardanaPypi: http://pypi.python.org/pypi/sardana/
.. _Tango: http://www.tango-controls.org/
.. _PyTango: http://packages.python.org/PyTango/
.. _taurus: http://packages.python.org/taurus/
.. _QTango: http://www.tango-controls.org/download/index_html#qtango3
.. _taurus: http://packages.python.org/taurus/
.. _Qt: http://qt.nokia.com/products/
.. _PyQt: http://www.riverbankcomputing.co.uk/software/pyqt/
.. _PyQwt: http://pyqwt.sourceforge.net/
.. _IPython: http://ipython.org/
.. _ATK: http://www.tango-controls.org/Documents/gui/atk/tango-application-toolkit
.. _Qub: http://www.blissgarden.org/projects/qub/
.. _ESRF: http://www.esrf.eu/

