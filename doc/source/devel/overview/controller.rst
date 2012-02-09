.. _pool-controller-overview:

===================
Controller overview
===================

Each different hardware object is directly controlled by another object called
*controller*. This object is responsible for mapping the communication
between a set of hardware objects (example motors) and the underlying hardware
(example: a motor controller crate).

The *controller* object is also exposed as a Tango_ device. Usually a 
*controller* is capable of handling several hardware objects. For example, a
motor controller crate is capable of controlling several motors (generally
called *axis* [#]_).

The *controller* objects can be created/deleted/renamed dynamically in a running
pool.

A specific type of *controller* needs to be created to handle each specific type
of hardware. Therefore, to each type of *controller* it is associated a specific
software component. Users can write a specific controller software component
(:term:`plug-in`) that is able to communicate with the specific hardware.
You can this way extend the initial pool capabilities to talk to all kinds of
different hardware.

Controller plug-ins can be written in Python_ or C++. Each controller code is
basically a Python or C++ class that needs to obey a specific :term:`API`.

Here is an a extract of a pertinent part of a Python_ motor controller code that
is able to talk to a Newport motor controller::

    class NSC200Controller(MotorController):
        """This class is the Tango Sardana motor controller for the Newport NewStep
        handheld motion controller NSC200.
        This controller communicates through a Device Pool serial communication
        channel."""

        ctrl_properties = \
            { 'SerialCh' : { 'Type' : str,
                             'Description' : 'Communication channel name for the serial line' },
              'SwitchBox': { 'Type' : bool,
                             'Description' : 'Using SwitchBox',
                             'DefaultValue' : False},
              'ControllerNumber' : { 'Type' : int, 
                                     'Description' : 'ControllerNumber',
                                     'DefaultValue' : 1 } }

        def __init__(self, inst, props, *args, **kwargs):
            MotorController.__init__(self, inst, props, *args, **kwargs)
                
            self.serial = None
            self.serial_state_event_id = -1

            if self.SwitchBox:
                self.MaxDevice = 8

        def AddDevice(self, axis):
            if axis > 1 and not self.SwitchBox:
                raise Exception("Without using a Switchbox only axis 1 is allowed")
            
            if self.SwitchBox:
                self._setCommand("MX", axis)

        def DeleteDevice(self, axis):
            pass
        
        _STATE_MAP = { NSC200.MOTOR_OFF : State.Off, NSC200.MOTOR_ON : State.On,
                       NSC200.MOTOR_MOVING : State.Moving }
        
        def StateOne(self, axis):
            if self.SwitchBox:
                self._setCommand("MX", axis)
                
            status = int(self._queryCommand("TS"))
            status = self._STATE_MAP.get(status, State.Unknown)
            register = int(self._queryCommand("PH"))
            lower = int(NSC200.getLimitNegative(register))
            upper = int(NSC200.getLimitPositive(register))

            switchstate = 0
            if lower == 1 and upper == 1: switchstate = 6
            elif lower == 1: switchstate = 4
            elif upper == 1: switchstate = 2
            return status, "OK", switchstate

        def ReadOne(self, axis):
            try:
                if self.SwitchBox:
                    self._setCommand("MX", axis)
                return float(self._queryCommand("TP"))
            except:
                raise Exception("Error reading position, axis not available")

        def PreStartOne(self, axis, pos):
            return True

        def StartOne(self, axis, pos):
            if self.SwitchBox:
                self._setCommand("MX", axis)
            status = int(self._queryCommand("TS"))
            if status == NSC200.MOTOR_OFF:
                self._setCommand("MO","")
            self._setCommand("PA", pos)
            self._log.debug("[DONE] sending position")
                
        def StartAll(self):
            pass

        def AbortOne(self, axis):
            if self.SwitchBox:
                self._setCommand("MX", axis)
            self._setCommand("ST", "")

Information on how to write controllers can be found
:ref:`here <pool-controllers>`. The complete controller :term:`API` can be found
:ref:`here <pool-controller-api>`.

.. rubric:: Footnotes

.. [#] The term *axis* will be used from here on to refer to the ID of
       a specific hardware object (like a motor) with respect to its *controller*.

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