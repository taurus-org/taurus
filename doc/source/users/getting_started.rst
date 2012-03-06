
.. _getting_started:

===============
Getting started
===============

Installing
----------

#. Get the sardana code

    #. From easy_install [1]_::
        
            easy_install -U sardana

    #. From latest source distribution:
        #. Download the latest stable version of `sardana <http://pypi.python.org/pypi/sardana>`_ (|version|)
        #. Extract the downloaded tar.gz into a temporary directory
        #. type [2]_::
               
               python setup.py build
               python setup.py install

    #. From SVN snapshot:
        #. Download the current `SVN snapshot <http://tango-cs.svn.sourceforge.net/viewvc/tango-cs/share/Sardana/trunk/?view=tar>`_
        #. Extract the downloaded tar.gz into a temporary directory
        #. type [2]_::
               
               python setup.py build
               python setup.py install

    #. From SVN trunk checkout (please look :ref:`here <working-from-svn>` for instructions)

#. test the installation::
       
       python -c "import sardana; print sardana.Release.version"

Windows installation shortcut
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This chapter provides a quick shortcut to all windows packages which are
necessary to run sardana on your windows machine

#. Install all dependencies:

    #. from `Python(x,y)`_ (by far the easiest choise)
        #. Download and install a python 2.6/2.7 compatible version of python(x,y)
           from `here <http://code.google.com/p/pythonxy>`_

    #. from scratch:
        #. Download and install `PyQwt`_ < 6.0 from `PyQwt downdoad page <http://pyqwt.sourceforge.net/download.html>`_
            #. Download and install compatible python with from link in the same `PyQwt`_ page
            #. Download and install compatible `numpy`_ from link in the same `PyQwt`_ page.
            #. Download and install compatible `PyQt`_ from link in the same `PyQwt`_ page.

.. #. Download and install latest `PLY`_ from `PLY downdoad page <http://www.dabeaz.com/ply>`_ (necessary for jdraw synoptics only)

#. Download and install latest `PyTango`_ from `PyTango downdoad page <http://pypi.python.org/pypi/PyTango>`_
#. Download and install latest `taurus`_ from `Taurus downdoad page <http://pypi.python.org/pypi/taurus>`_

#. Finally download and install latest sardana from `Sardana downdoad page <http://pypi.python.org/pypi/sardana>`_


.. _getting-started-running-server:

Running the Sardana tango server
---------------------------------

.. note::
    if you have Tango <= 7.2.6 without all patches applied, Sardana server
    will not work due to a known bug. Please follow in instructions from
    :ref:`getting-started-running-servers-separately` instead.

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
The next chapter describes how to start up a :term:`CLI` application
called *spock* which connects to the sardana server you have just started
through an object of type *Door* called *Door_lab-01_1*.

You can skip the next chapter and go directly to
:ref:`getting-started-running-cli`.

.. _getting-started-running-servers-separately:

Running Pool and MacroServer tango servers separately
--------------------------------------------------------

.. note::
    You should only read this chapter if you are if you have Tango <= 7.2.6
    without all patches applied. If you do, please follow in instructions from
    :ref:`getting-started-running-server` instead.

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

.. _getting-started-running-cli:

Running a :term:`CLI` client
----------------------------

After the server has been started, you can start one or more client applications
(:term:`CLI`\s and/or :term:`GUI`\s) that connect to the server. Each client
connects to a specific *door* on the server. A single sardana can be configured
with many *doors* allowing multiple clients to be connected at the same time.

When the sardana server was first executed, part of the registration process
created one *door* for you so now you just have to start the client application
from the command line::

    homer@pc001:~$ spock

Spock is an `IPython`_ based :term:`CLI`. When you start spock without arguments
it will assume a default profile called *spockdoor*. The first time spock is
executed, it will inform you that profile *spockdoor* doesn't exist and it will
offer to create one. Just answer 'y'. After, it will ask you to which *door*
should the default *spockdoor* profile connect to. Select the door name
corresponding to your sardana server (*Door_lab-01_1*) and press return. by now
you should get an output like this::

    homer@pc001:~$ spock
    Profile 'spockdoor' does not exist. Do you want to create one now ([y]/n)? y
    Available Door devices from pc151:10000 :
    Door_lab-01_1 (a.k.a. Door/lab-01/1)
    Door name from the list? Door_lab-01_1
    
    Storing ipython_config.py in /home/homer/.config/ipython/profile_spockdoor... [DONE]
    Spock 1.0.0 -- An interactive laboratory application.

    help      -> Spock's help system.
    object?   -> Details about 'object'. ?object also works, ?? prints more.

    IPython profile: spockdoor

    Connected to Door_lab-01_1

    Door_lab-01_1 [1]: 

That't it! You now have a running sardana client. Still not impressed, I see!
The next chapter describes how to start adding new elements to your sardana
environment.

Populating your sardana with items
----------------------------------

One of sardana's goals is to allow you to execute *procedures* (what we call in
sardana *macros*, hence from here on we will use the term *macro*). A *macro*
is basically a piece of code. You can write macros using the `Python`_ language
to do all sorts of things. The sky is the limit here!

Sardana comes with a catalog of *macros* that help users in a laboratory to run
their experiments [3]_. Most of these *macros* involve interaction with sardana
elements like motors and experimental channels. Therefore, the first step in
a new sardana demo is to populate your system with some elements. Fortunately,
sardana comes with a *macro* called *sar_demo* that does just that. To execute
this *macro* just type on the command line *sar_demo*. You should get an ouput
like this::

    Door_lab-01_1 [1]: sar_demo
    Creating controllers motctrl01, ctctrl01... [DONE]
    Creating motors mot01, mot02, mot03, mot04... [DONE]
    Creating measurement group measgrp01... [DONE]
    
    Door_lab-01_1 [2]: 

You should now have in your sardana system a set of simulated motors and
counters with which you can play.

You can type:
    
    1. :class:`~sardana.macroserver.macros.standard.wa` - which will show the positions of all motors
    2. :class:`~sardana.macroserver.macros.standard.mv` *mot01 100* - which will move mot01 to position 100
    3. :class:`~sardana.macroserver.macros.scan.ascan` *mot01 0 100 10 0.1* - will start an absolute step scan

.. hint:: for clearing sardana from the elements created by the demo, execute ``clear_sar_demo``

.. _working-from-svn:

Working from SVN
----------------

You can checkout sardana from SVN from the following location::

    svn co http://tango-cs.svn.sourceforge.net/svnroot/tango-cs/share/Sardana/trunk Sardana

You can directly execute sardana binaries (Pool, MacroServer, Sardana or spock
from the command line)::

    homer@pc001:~$ cd Sardana
    homer@pc001:~/Sardana$ scripts/Sardana

.. rubric:: Footnotes

.. [1] This command requires super user previledges on linux systems. If your
       user has them you can usually prefix the command with *sudo*::
       
           homer@pc001:~$ sudo easy_install -U sardana
       
       Alternatively, if you don't have adminstrator previledges, you can
       install locally in your user directory with::
       
           homer@pc001:~$ easy_install --user sardana
       
       In this case the executables are located at <HOME_DIR>/.local/bin. Make
       sure the PATH is pointing there or you execute from there.

.. [2] *setup.py install* requires user previledges on linux systems. If your
       user has them you can usually prefix the command with *sudo*::
       
           homer@pc001:~$ sudo python setup.py install
    
       Alternatively, if you don't have adminstrator previledges, you can
       install locally in your user directory with::
       
           homer@pc001:~$ python setup.py install --user
       
       In this case the executables are located at <HOME_DIR>/.local/bin. Make
       sure the PATH is pointing there or you execute from there.

.. [3] The sardana standard macro catalog can be found
       :ref:`here <standard-macro-catalog>` 
       
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

