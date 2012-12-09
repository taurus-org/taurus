
.. _sardana-pool-overview:

==============
Pool overview
==============

The Pool object is the sardana server object which manages all other hardware level
sardana objects related with motion control and data acquisition. This object is
exposed to the world as a Tango_ device. It's :term:`API` consists of a series
of methods (Tango_ commands) and members (Tango_ attributes) which allow
external applications to create/remove/rename and monitor the different hardware
level sardana objects.

The Pool could be seen as a kind of intelligent device container to
control the experiment hardware. It has two basic features which are:

1. Hardware access using dynamically created/deleted devices
   according to the experiment needs

2. Management of some very common and well defined actions regularly done
   on a laboratory/factory (motion control, data acquisition, etc.)


Hardware access
---------------

Core hardware access
~~~~~~~~~~~~~~~~~~~~

Most of the times, it is possible to define a list of very common objects found
in most of the experiments. Objects commonly used to drive an experiment
usually fit in one of the following categories:

- *Moveables*
    - Motor
    - Pseudo motor
    - Group of moveables
    - IORegister (a.k.a. discrete motor)
- *Experimental channels*
    - Counter/Timer
    - 0D (Multimeter like)
    - 1D (:term:`MCA` like)
    - 2D (:term:`CCD` like)
    - Pseudo Counter
- *Communication channels*

Each different controlled hardware object will also be exposed as an independent
Tango_ class. The sardana device server will embed all these Tango_ classes
together. The pool Tango_ device is the "container interface" and allows the
user to create/delete classical Tango_ devices which are instances of these
embedded classes.


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
