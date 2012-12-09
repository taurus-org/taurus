.. _sardana-motor-overview:

.. currentmodule:: sardana.pool

==================
Motor overview
==================

The motor is one of the most used elements in sardana. A motor represents
anything that can be *changed* (and can potentially take some time to do it),
so, not only physical motors (like a stepper motors) fit into this category but
also, for example, a power supply for which the electrical current can be
modified.
As it happens with the motor controller hardware and its physical motor(s),
a sardana motor is always associated with it's sardana motor controller. 

.. figure:: /_static/sardana_server_icepap_np200.png
    :width: 680
    :align: center
    
    A diagram representing a sardana server with a several motor controllers
    and their respective motors.

The *motor* object is also exposed as a Tango_ device.

.. seealso:: 
    
    :ref:`sardana-motor-api`
        the motor :term:`API` 
    
    :class:`~sardana.tango.pool.Motor.Motor`
        the motor tango device :term:`API`

..    :class:`~sardana.pool.poolmotor.PoolMotor`
..        the motor class :term:`API` 



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
