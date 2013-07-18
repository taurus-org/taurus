.. _sardana-getting-started-running-cli:

Running the client
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
corresponding to your sardana server (*Door_lab-01_1*) and press return. By now
you should get an output like this::

    homer@pc001:~$ spock
    Profile 'spockdoor' does not exist. Do you want to create one now ([y]/n)? y
    Available Door devices from sardanamachine:10000 :
    Door_lab-01_1 (a.k.a. Door/lab-01/1)
    Door name from the list? Door_lab-01_1
    
    Storing ipython_config.py in /home/homer/.config/ipython/profile_spockdoor... [DONE]
    Spock 1.0.0 -- An interactive laboratory application.

    help      -> Spock's help system.
    object?   -> Details about 'object'. ?object also works, ?? prints more.

    IPython profile: spockdoor

    Connected to Door_lab-01_1

    Door_lab-01_1 [1]: 

That's it! You now have a running sardana client. Still not impressed, I see!
The next chapter describes how to start adding new elements to your sardana
environment.

Populating your sardana with items
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

One of sardana's goals is to allow you to execute *procedures* (what we call in
sardana *macros*, hence from here on we will use the term *macro*). A *macro*
is basically a piece of code. You can write macros using the `Python`_ language
to do all sorts of things. The sky is the limit here!

Sardana comes with a :ref:`catalog of macros<sardana-standard-macro-catalog>` that help
users in a laboratory to run their experiments. Most of these *macros*
involve interaction with sardana elements like motors and experimental channels.
Therefore, the first step in a new sardana demo is to populate your system with
some elements. Fortunately, sardana comes with a *macro* called *sar_demo* that
does just that. To execute this *macro* just type on the command line
:class:`~sardana.macroserver.macros.demo.sar_demo`.
You should get an output like this:

.. sourcecode:: spock
    
    Door_lab-01_1 [1]: sar_demo

    Creating controllers motctrl01, ctctrl01... [DONE]
    Creating motors mot01, mot02, mot03, mot04... [DONE]
    Creating measurement group mntgrp01... [DONE]
    
You should now have in your sardana system a set of simulated motors and
counters with which you can play.

.. hint::

    for clearing sardana from the elements created by the demo, execute
    :class:`~sardana.macroserver.macros.demo.clear_sar_demo`

The next chapter (:ref:`spock <sardana-spock>`) will give you a complete overview
of spock's interface.


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
