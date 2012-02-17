
.. _getting_started:

===============
Getting started
===============

.. _installing:

Installing
----------

You will need super user previledges in linux to do this!

#. From easy_install::
    
        easy_install -U sardana

#. From latest source distribution:
    #. Download the latest version of sardana from `here <http://pypi.python.org/pypi/sardana>`_.
    #. Extract the downloaded tar.gz into a temporary directory
    #. type::
           
           python setup.py build
           python setup.py install
       
#. test the installation::
       
       python -c "import sardana; print sardana.Release.version"

Windows installation shortcut
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This chapter provides a quick shortcut to all windows packages which are
necessary to run sardana on your windows machine

#. from `Python(x,y)`_
    #. Download and install a python 2.6/2.7 compatible version of python(x,y)
       from `here <http://code.google.com/p/pythonxy>`_

#. from scratch:
    #. Download and install `PyQwt`_ < 6.0 from `PyQwt downdoad page <http://pyqwt.sourceforge.net/download.html>`_
        #. Download and install compatible python with from link in the same `PyQwt`_ page
        #. Download and install compatible `numpy`_ from link in the same `PyQwt`_ page.
        #. Download and install compatible `PyQt`_ from link in the same `PyQwt`_ page.

#. Finally:
    #. Download and install latest `PLY`_ from `PLY downdoad page <http://www.dabeaz.com/ply>`_ (necessary for jdraw synoptics only)
    #. Download and install latest `PyTango`_ from `PyTango downdoad page <http://pypi.python.org/pypi/PyTango>`_
    #. Download and install latest `taurus`_ from `Taurus downdoad page <http://pypi.python.org/pypi/taurus>`_
    #. Download and install latest sardana from `Sardana downdoad page <http://pypi.python.org/pypi/sardana>`_


.. _getting_started_running_server:

Running the server
------------------

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
their experiments [1]_. Most of these *macros* involve interaction with sardana
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

Working from SVN
----------------

You can checkout sardana from SVN from the following location::

    svn co http://tango-cs.svn.sourceforge.net/svnroot/tango-cs/share/Sardana/trunk sardana

Afterward, if you decide to work directly from SVN code (without installing):

    1. add <sardana checkout dir>/src to PYTHONPATH

.. rubric:: Footnotes

.. [1] The sardana standard macro catalog can be found
       :ref:`here <standard-macro-catalog>` 
       
.. _numpy: http://numpy.scipy.org/
.. _PLY: http://www.dabeaz.com/ply/
.. _Python(x,y): http://code.google.com/p/pythonxy/
.. _Python: http://www.python.org/

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
