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

Sardana consists of a software library which contains sardana kernel engine, a
server and a client library which allow sardana to run as a
:term:`client-server <client-server model>` based distributed control system.
The communication protocols between servers and clients are
:term:`plug-ins <plug-in>` in sardana. At this time, the only
implemented protocol is Tango_. In earlier versions, sardana was tightly
connected to Tango_. This documentation, is therefore centered in the
Tango_ server implementation. When other comunication protocols become
available, the documentation will be revised.

Client applications (both :term:`GUI`  and :term:`CLI`) can connect to the
sardana server through the high level sardana client :term:`API` or through the
low level pure Tango_ channels.
Client applications can be build with the purpose of *operating* an existing
sardana server or of *configuring* it.

Sardana server (:term:`SDS`)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The sardana server consists of a sardana tango device server (:term:`SDS`)
running a sardana kernel engine.
This server runs as an :term:`OS` :term:`daemon`. Once configured, this server
acts as a container of device objects which can be accessed by the outside
world as *tango device objects*.
Typically, a sardana server will consist of:

    - a low level **Pool** object which manages all the server objects related
      to motion control and data acquisition (controllers, motors, counters,
      experiment channels, etc).
    - a **Macro Server** object which manages the execution of macros
      (procedures) and client connection points (called doors).
    - a set of low level objects (controllers, motors, counters, experiment 
      channels, etc) controlled by the Pool object
    - a set of **Door** objects managed by the macro server. A Door is the
      preferred access point from a client application to the to the sardana
      server

.. figure:: /_static/sardana_server.png
    :width: 400
    :align: center
    
    A diagram representing a sardana server with its objects

A sardana server may contain only a Pool object or a Macro Server object or both.
It may **NOT** contain more than one Pool object or more than one Macro Server object.

If necessary, your sardana system may be splitted into two (or more) sardana servers.
A common configuration is to have a sardana server with a Pool (in this case we call 
the server a *Device Pool* server) and a second server with a Macro Server (this server
is called *MacroServer* server).

The following figures show some of the possible alternative configurations

.. figure:: /_static/pool_server.png
    :width: 256
    :align: center
      
    1 - Sardana configured to be a single Pool DS (no MacroServer present)

.. figure:: /_static/macroserver_server.png
    :width: 256
    :align: center
      
    2 - Sardana configured to be a single MacroServer DS (no Pool present)

.. figure:: /_static/macroserver_pool_server.png
    :width: 256
    :align: center
      
    3 - Sardana configured with a MacroServer DS connecting to an underlying
    Pool DS

.. figure:: /_static/sardana_pool_server.png
    :width: 512
    :align: center
      
    4 - Sardana configured with a Sardna DS connecting to another underlying
    Pool DS

The following chapters describe each of the Sardana objects in more detail.


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
.. _IPython: http://ipython.org/
.. _ATK: http://www.tango-controls.org/Documents/gui/atk/tango-application-toolkit
.. _Qub: http://www.blissgarden.org/projects/qub/
.. _numpy: http://numpy.scipy.org/
.. _SPEC: http://www.certif.com/
.. _EPICS: http://www.aps.anl.gov/epics/
