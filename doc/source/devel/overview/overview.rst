.. _sardana-devel-global-overview:

================
Global overview
================

This chapter gives an overview of the sardana architecture and describes each of
the different components in some detail.
If you find this document to be to technical please consider reading the
:ref:`sardana-overview` guide first.

The following chapters assume a that you have a minimum knowledge of the Tango_
system and basic computer science.

Architecture
-------------

Sardana is a distributed control system. It is based on the
:term:`client-server model`.
The communication protocol used by Sardana between servers and clients is Tango_.
The sardana server consists of a sardana tango device server (:term:`SDS`).
Client applications (both :term:`GUI`  and :term:`CLI` can connect to the sardana
server through the high level sardana client :term:`API` or through the low
level pure Tango_ channels.

Sardana server (:term:`SDS`)
""""""""""""""""""""""""""""

This server runs as an :term:`OS` :term:`daemon`. Once configured, this server
acts as a container of device objects which can be accessed by the outside
world as *tango device objects*.
Typically, a sardana server will consist of:

    - a low level *Pool* object which manages all the server objects related to
      motion control and data acquisition (controllers, motors, counters,
      experiment channels, etc).
    - a *Macro Server* object which manages the execution of macros (procedures)
      and client connection points (called doors).
    - a set of low level objects (controllers, motors, counters, experiment 
      channels, etc) controlled by the Pool object
    - a set of *Door* objects managed by the macro server.

.. figure:: /_static/sardana_server_empty.png
    :width: 500
    :align: center
    
    A diagram representing a sardana server with its objects

A sardana server may contain only a Pool object or a Macro Server object or both.
It may **NOT** contain more than one Pool object or more than one Macro Server object.

If necessary, your sardana system may be splitted into two (or more) sardana servers.
A common configuration is to have a sardana server with a Pool (in this case we call 
the server a *Device Pool* server) and a second server with a Macro Server (this server
is called *MacroServer* server).

The following chapters describe each of the Sardana objects in more detail.

.. toctree::
   :maxdepth: 2

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