.. currentmodule:: sardana.pool.controller

.. _sardana-countertimercontroller-howto-basics:

=======================================
How to write a counter/timer controller
=======================================

The basics
----------

An example of a hypothetical *Springfield* counter/timer controller will be build
incrementally from scratch to aid in the explanation.

By now you should have read the general controller basics chapter. You should
be able to create a CounterTimerController with:

- a proper constructor,
- add and delete axis methods
- get axis state


.. code-block:: python

    import springfieldlib

    from sardana.pool.controller import CounterTimerController

    class SpringfieldCounterTimerController(CounterTimerController):

        def __init__(self, inst, props, *args, **kwargs):
            super(SpringfieldCounterTimerController, self).__init__(inst, props, *args, **kwargs)
            
            # initialize hardware communication
            self.springfield = springfieldlib.SpringfieldCounterHW()
            
            # do some initialization
            self._counters = {}

        def AddDevice(self, axis):
            self._counters[axis] = True 

        def DeleteDevice(self, axis):
            del self._counters[axis]

        StateMap = {
            1 : State.On,
            2 : State.Moving,
            3 : State.Fault,
        }
       
        def StateOne(self, axis):
            springfield = self.springfield
            state = self.StateMap[ springfield.getState(axis) ]
            status = springfield.getStatus(axis)
            return state, status
           
The examples use a :mod:`springfieldlib` module which emulates a counter/timer
hardware access library.

The :mod:`springfieldlib` can be downloaded from
:download:`here <springfieldlib.py>`.

The Springfield counter/timer controller can be downloaded from
:download:`here <sf_ct_ctrl.py>`.

The following code describes a minimal *Springfield* base counter/timer controller
which is able to return both the state and value of an individual counter as
well as to start an acquisition:

.. literalinclude:: sf_ct_ctrl.py
   :pyobject: SpringfieldBaseCounterTimerController

This code is shown only to demonstrate the minimal controller :term:`API`.
The advanced counter/timer controller chapters describe how to account for more
complex behaviour like reducing the number of hardware accesses.

.. todo:: finish counter/timer controller howto


        
.. _ALBA: http://www.cells.es/
.. _ANKA: http://http://ankaweb.fzk.de/
.. _ELETTRA: http://http://www.elettra.trieste.it/
.. _ESRF: http://www.esrf.eu/
.. _FRMII: http://www.frm2.tum.de/en/index.html
.. _HASYLAB: http://hasylab.desy.de/
.. _MAX-lab: http://www.maxlab.lu.se/maxlab/max4/index.html
.. _SOLEIL: http://www.synchrotron-soleil.fr/

.. _Tango: http://www.tango-controls.org/
.. _Taco: http://www.esrf.eu/Infrastructure/Computing/TACO/
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
