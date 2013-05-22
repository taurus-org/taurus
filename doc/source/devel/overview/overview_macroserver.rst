.. _sardana-macroserver-overview:

=====================
Macro Server overview
=====================

The Macro Server object is the sardana server object which manages all high
level sardana objects related to macro execution, namely doors, macro libraries
and macros themselves.

The main purpose of the Macro Server is to run *macros*. Macros are just pieces
of Python_ code (functions or classes) which reside in a macro library (Python_
file). Macros can be written by anyone with knowledge of Python_.

The Macro Server is exposed on the sardana server as a Tango_ device.
Through configuration, the Macro Server can be told to connect to a
Pool device. This is the most common configuration.
You can, however, tell the Macro Server to connect to more than one Pool device
or to no Pool devices at all.

When connected to a Pool device(s), the Macro Server uses the Pool device
introspection :term:`API` to discover which elements are available. The existing
macros will be able to access these elements (through parameters passed to the
macro or using the macro :term:`API`) and act on them.

In order to be able to run macros, you must first connect to the Macro Server
entry point object called *Door*. A single Macro Server can have many active
Doors at the same time but a Door can only run one macro at a time.
Each Door is exposed on the sardana server as a Tango_ device.

You are not in any way restricted to the standard macros provided by the sardana
system. You can write as many macros as you need. Writing your own macros is
easy. The macro equivalent of Python_\'s *Hello, World!* example::

    from sardana.macroserver.macro import macro
    
    @macro()
    def hello_world(self):
        self.output("Hello, World!")


Here is a simple example of a macro to move any moveable element to a certain
value::

    from sardana.macroserver.macro import macro, Type
    
    @macro([ ["moveable", Type.Moveable, None, "moveable to move"],
             ["position", Type.Float, None, "absolute position"] ])
    def my_move(self, moveable, position):
        """This macro moves a moveable to the specified position"""

        moveable.move(position)
        self.output("%s is now at %s", moveable, moveable.getPosition())

Information on how to write your own sardana macros can be found 
:ref:`here <sardana-macros-howto>`.

The complete macro :term:`API` can be found :ref:`here <sardana-macro-api>`.

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
