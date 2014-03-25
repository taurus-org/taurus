.. currentmodule:: sardana.macroserver.macros.test.base

:mod:`~sardana.macroserver.macros.test`
========================================

.. automodule:: sardana.macroserver.macros.test.base

.. rubric:: Decorator
.. autofunction:: macroTest

.. decorator:: testRun

   Specializations of macroTest for test runables.

.. decorator:: testStop

   Specializations of macroTest for test stopables.

.. decorator:: testFail

   Specializations of macroTest for test fallibles.


.. rubric:: Functions

.. hlist::
    :columns: 3

    * :class:`BaseMacroTestCase`
    * :class:`RunMacroTestCase`
    * :class:`RunStopMacroTestCase`


BaseMacroTestCase
-----------------

.. inheritance-diagram:: BaseMacroTestCase
    :parts: 1

.. autoclass:: BaseMacroTestCase
    :inherited-members:
    :members:
    :undoc-members:

RunMacroTestCase
----------------

.. inheritance-diagram:: RunMacroTestCase
    :parts: 1

.. autoclass:: RunMacroTestCase
    :inherited-members:
    :members:
    :undoc-members:

RunStopMacroTestCase
--------------------

.. inheritance-diagram:: RunStopMacroTestCase
    :parts: 1

.. autoclass:: RunStopMacroTestCase
    :inherited-members:
    :members:
    :undoc-members:
