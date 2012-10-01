.. currentmodule:: sardana.pool.controller

:mod:`~sardana.pool.controller`
===============================

.. automodule:: sardana.pool.controller

.. rubric:: Constants

.. autodata:: Type
.. autodata:: Access
.. autodata:: Description
.. autodata:: DefaultValue
.. autodata:: FGet
.. autodata:: FSet
.. autodata:: Memorize
.. autodata:: Memorized
.. autodata:: MemorizedNoInit
.. autodata:: NotMemorized
.. autodata:: MaxDimSize

.. rubric:: Interfaces

.. hlist::
    :columns: 3

    * :class:`Readable`
    * :class:`Startable`
    * :class:`Stopable`
    * :class:`Loadable`
    
.. rubric:: Classes

.. hlist::
    :columns: 3

    * :class:`Controller`
    * :class:`PseudoController`
    * :class:`MotorController`
    * :class:`PseudoMotorController`
    * :class:`CounterTimerController`
    * :class:`ZeroDController`
    * :class:`OneDController`    
    * :class:`TwoDController`
    * :class:`PseudoCounterController`
    * :class:`IORegisterController`


Readable interface
------------------

.. inheritance-diagram:: Readable
    :parts: 1
    
.. autoclass:: Readable
    :show-inheritance:
    :members:
    :undoc-members:


Startable interface
-------------------

.. inheritance-diagram:: Startable
    :parts: 1
    
.. autoclass:: Startable
    :show-inheritance:
    :members:
    :undoc-members:


Stopable interface
-------------------

.. inheritance-diagram:: Stopable
    :parts: 1
    
.. autoclass:: Stopable
    :show-inheritance:
    :members:
    :undoc-members:


Loadable interface
-------------------

.. inheritance-diagram:: Loadable
    :parts: 1
    
.. autoclass:: Loadable
    :show-inheritance:
    :members:
    :undoc-members:   


Abstract Controller
--------------------

.. inheritance-diagram:: Controller
    :parts: 1
    
.. autoclass:: Controller
    :private-members: __init__
    :show-inheritance:
    :members:
    :undoc-members:


Abstract Pseudo Controller
-----------------------------

.. inheritance-diagram:: PseudoController
    :parts: 1
    
.. autoclass:: PseudoController
    :show-inheritance:
    :members:
    :undoc-members:

    
Motor Controller API
---------------------

.. inheritance-diagram:: MotorController
    :parts: 1
    
.. autoclass:: MotorController
    :show-inheritance:
    :members:
    :undoc-members:


Pseudo Motor Controller API
-----------------------------

.. inheritance-diagram:: PseudoMotorController
    :parts: 1
    
.. autoclass:: PseudoMotorController
    :show-inheritance:
    :members:
    :undoc-members:
    
    
Counter Timer Controller API
----------------------------

.. inheritance-diagram:: CounterTimerController
    :parts: 1
    
.. autoclass:: CounterTimerController
    :show-inheritance:
    :members:
    :undoc-members:


0D Controller API
----------------------------

.. inheritance-diagram:: ZeroDController
    :parts: 1
    
.. autoclass:: ZeroDController
    :show-inheritance:
    :members:
    :undoc-members:


1D Controller API
----------------------------

.. inheritance-diagram:: OneDController
    :parts: 1
    
.. autoclass:: OneDController
    :show-inheritance:
    :members:
    :undoc-members:


2D Controller API
----------------------------

.. inheritance-diagram:: TwoDController
    :parts: 1
    
.. autoclass:: TwoDController
    :show-inheritance:
    :members:
    :undoc-members:


Pseudo Counter Controller API
-----------------------------

.. inheritance-diagram:: PseudoCounterController
    :parts: 1
    
.. autoclass:: PseudoCounterController
    :show-inheritance:
    :members:
    :undoc-members:


IO Register Controller API
----------------------------

.. inheritance-diagram:: IORegisterController
    :parts: 1
    
.. autoclass:: IORegisterController
    :show-inheritance:
    :members:
    :undoc-members:
