.. currentmodule:: sardana.pool.controller

.. _sardana-controller-howto-whatis:

====================
What is a controller
====================

A controller in sardana is a piece of software capable of *translating*
between the sardana :term:`API` and a specific hardware :term:`API`. Sardana
expects a controller to obey a specific :term:`API` in order to be able to
properly configure and operate with it. The hardware :term:`API` used by the
controller could be anything, from a pure serial line to shared memory or a
remote server written in Tango_, Taco_ or even EPICS_.

Controllers can only be written in Python_ (in future also C++ will be
possible). A controller **must** be a :term:`class` inheriting from one of the
existing controller types:

.. hlist::
    :columns: 3
    
    - :class:`MotorController`
    - :class:`CounterTimerController`
    - :class:`ZeroDController`
    - :class:`OneDController`
    - :class:`TwoDController`        
    - :class:`IORegisterController`

    - :class:`PseudoMotorController`
    - :class:`PseudoCounterController`

A controller is designed to incorporate a set of generic individual elements.
Each element has a corresponding *axis*. For example, in a motor
controller the elements will be motors, but in a counter/timer controller the
elements will be experimental channels.

Some controller classes are designed to target a specific type of hardware.
Other classes of controllers, the *pseudo* classes, are designed to provide a
high level view over a set of underlying lower level controller elements.

We will focus first on writing low level hardware controllers since they 
share some of the :term:`API` and after on the *pseudo* controllers.

.. _sardana-controller-howto-basics:

Controller - The basics
-----------------------

The first thing to do is to import the necessary symbols from sardana library.
As you will see, most symbols can be imported through the
:mod:`sardana.pool.controller` module:

.. code-block:: python

    import springfieldlib

    from sardana.pool.controller import MotorController
    
    class SpringfieldMotorController(MotorController):
        """A motor controller intended from demonstration purposes only"""
        pass

The common :term:`API` to all low level controllers includes the set of methods
to:

    #. construct the controller
    #. add/delete a controller element [#f1]_
    #. obtain the state of controller element(s) [#f2]_
    #. define, set and get extra axis attributes
    #. define, set and get extra controller attributes
    #. define, set and get extra controller properties

In the following chapters the examples will be based on a motor controller 
scenario.

The examples use a :mod:`springfieldlib` module which emulates a motor hardware
access library.

The :mod:`springfieldlib` can be downloaded from
:download:`here <springfieldlib.py>`.

The Springfield motor controller can be downloaded from
:download:`here <sf_motor_ctrl.py>`.
  
.. _sardana-controller-howto-constructor:

Constructor
~~~~~~~~~~~

The constructor consists of the
:meth:`~sardana.pool.controller.Controller.__init__` method. This method is
called when you create a new controller of that type and every time the sardana
server is started. It will also be called if the controller code has changed
on the file and the new code is reloaded into sardana.

It is **NOT** mandatory to override the :meth:`~sardana.pool.controller.Controller.__init__`
from :class:`~sardana.pool.controller.MotorController`   . Do it only
if you need to add some initialization code. If you do it, it is **very important**
to follow the two rules:

    #. use the method signature: ``__init__(self, inst, props, *args, **kwargs)``
    #. always call the super class constructor
    
The example shows how to implement a constructor for a motor controller:

.. code-block:: python
    :emphasize-lines: 3
    
    class SpringfieldMotorController(MotorController):

        def __init__(self, inst, props, *args, **kwargs):
            super(SpringfieldMotorController, self).__init__(inst, props, *args, **kwargs)
            
            # initialize hardware communication
            self.springfield = springfieldlib.SpringfieldMotorHW()
            
            # do some initialization
            self._motors = {}

.. _sardana-controller-howto-add-delete:

Add/Delete axis
~~~~~~~~~~~~~~~

Each individual element in a controller is called *axis*. An axis is represented
by a number. A controller can support one or more axes. Axis numbers don't need
to be sequencial. For example, at one time you may have created for your motor
controller instance only axis 2 and 5. 

Two methods are called when creating or removing an element from a controller.
These methods are :meth:`~sardana.pool.controller.Controller.AddDevice` and 
:meth:`~sardana.pool.controller.Controller.DeleteDevice`. The
:meth:`~sardana.pool.controller.Controller.AddDevice` method is called when a
new axis belonging to the controller is created in sardana. The 
:meth:`~sardana.pool.controller.Controller.DeleteDevice` method is
called when an axis belonging to the controller is removed from sardana.
The example shows an example how to implement these methods on a motor
controller:

.. code-block:: python
    :emphasize-lines: 3, 6
    
    class SpringfieldMotorController(MotorController):

        def AddDevice(self, axis):
            self._motors[axis] = True 

        def DeleteDevice(self, axis):
            del self._motor[axis]

.. _sardana-controller-howto-axis-state:

Get axis state
~~~~~~~~~~~~~~

To get the state of an axis, sardana calls the
:meth:`~sardana.pool.controller.Controller.StateOne` method. This method
receives an axis as parameter and should return either:

    - state (:obj:`~sardana.sardanadefs.State`) or
    - a sequence of two elements:
        - state (:obj:`~sardana.sardanadefs.State`)
        - status (:obj:`str`)
        
(For motor controller see :ref:`get motor state <sardana-motorcontroller-howto-axis-state>` ):

The state should be a member of :obj:`~sardana.sardanadefs.State` (For backward
compatibility reasons, it is also supported to return one of
:class:`PyTango.DevState`). The status could be any string.

If you return a :obj:`~sardana.sardanadefs.State` object, sardana will compose a
status string with:

    <axis name> is in <state name>

Here is an example of the possible implementation of 
:meth:`~sardana.pool.controller.Controller.StateOne` :

.. code-block:: python
    :emphasize-lines: 11
    
    from sardana import State

    class SpringfieldMotorController(MotorController):

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


.. _sardana-controller-howto-axis-attributes:

Extra axis attributes
~~~~~~~~~~~~~~~~~~~~~

Each axis is associated a set of standard attributes. These attributes depend
on the type of controller (example, a motor will have velocity, acceleration but
a counter won't).

Additionally, you can specify an additional set of extra attributes on each axis.

Lets suppose that a Springfield motor controller can do close loop on hardware.
We could define an extra motor attribute on each axis that (de)actives close
loop on demand.

The first thing to do is to specify which are the extra attributes.
This is done through the :attr:`~sardana.pool.controller.Controller.axis_attributes`.
This is basically a dictionary were the keys are attribute names and the value
is a dictionary describing the folowing properties for each attribute:

===================== ========= ============================================  ======================================================= ===============================================
config. parameter     Mandatory Key                                           Default value                                           Example
===================== ========= ============================================  ======================================================= ===============================================
data type & format    Yes       :obj:`~sardana.pool.controller.Type`          ---                                                     :obj:`int`
data access           No        :obj:`~sardana.pool.controller.Access`        :obj:`~sardana.pool.controller.Access.ReadWrite`        :obj:`~sardana.pool.controller.Access.ReadOnly`
description           No        :obj:`~sardana.pool.controller.Description`   "" (empty string)                                       "the motor encoder source"
default value         No        :obj:`~sardana.pool.controller.DefaultValue`  ---                                                     12345
getter method name    No        :obj:`~sardana.pool.controller.FGet`          "get" + <name>                                          "getEncoderSource"
setter method name    No        :obj:`~sardana.pool.controller.FSet`          "set" + <name>                                          "setEncoderSource"
memorize value        No        :obj:`~sardana.pool.controller.Memorize`      :obj:`~sardana.pool.controller.Memorized`               :obj:`~sardana.pool.controller.NotMemorized`
max dimension size    No        :obj:`~sardana.pool.controller.MaxDimSize`    Scalar: ``()``; 1D: ``(2048,)``; 2D: ``(2048, 2048)``   ``(2048,)``
===================== ========= ============================================  ======================================================= ===============================================

Here is an example of how to specify the scalar, boolean, read-write *CloseLoop*
extra attribute in a Springfield motor controller:

.. code-block:: python
    :emphasize-lines: 6, 14, 17
    
    from sardana import DataAccess
    from sardana.pool.controller import Type, Description, DefaultValue, Access, FGet, FSet
    
    class SpringfieldMotorController(MotorController):
    
        axis_attributes = { 
            "CloseLoop" : {
                    Type         : bool,
                    Description  : "(de)activates the motor close loop algorithm",
                    DefaultValue : False,
                },
        }
        
        def getCloseLoop(self, axis):
            return self.springfield.isCloseLoopActive(axis)
        
        def setCloseLoop(self, axis, value):
            self.springfield.setCloseLoop(axis, value)

When sardana needs to read the close loop value, it will first check if the
controller has the method specified by the :obj:`~sardana.pool.controller.FGet`
keyword (we didn't specify it in 
:attr:`~sardana.pool.controller.Controller.axis_attributes` so it defaults to
*getCloseLoop*). It will then call this controller method which
should return a value compatible with the attribute data type.

As an alternative, to avoid filling the controller code with pairs of get/set
methods, you can choose not to write the getCloseLoop and setCloseLoop methods.
This will trigger sardana to call the 
:meth:`~sardana.pool.controller.Controller.GetAxisExtraPar`
/:meth:`~sardana.pool.controller.Controller.SetAxisExtraPar` pair of methods.
The disadvantage is you will end up with a forest of :keyword:`if` ... 
:keyword:`elif` ... :keyword:`else` statements. Here is the alternative
implementation:

.. code-block:: python
    :emphasize-lines: 6, 14, 18
    
    from sardana import DataAccess
    from sardana.pool.controller import Type, Description, DefaultValue, Access, FGet, FSet
    
    class SpringfieldMotorController(MotorController):
    
        axis_attributes = { 
            "CloseLoop" : {
                    Type         : bool,
                    Description  : "(de)activates the motor close loop algorithm",
                    DefaultValue : False,
                },
        }
        
        def GetAxisExtraPar(self, axis, parameter):
            if parameter == 'CloseLoop':
                return self.springfield.isCloseLoopActive(axis)
        
        def SetAxisExtraPar(self, axis, parameter, value):
            if parameter == 'CloseLoop':
                 self.springfield.setCloseLoop(axis, value)

Sardana gives you the choice: we leave it up to you to decide which is the
better option for your specific case.

.. _sardana-controller-howto-controller-attributes:

Extra controller attributes
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Besides extra attributes per axis, you can also define extra attributes at the
controller level.
In order to do that you have to specify the extra controller attribute(s) within 
the :attr:`~sardana.pool.controller.Controller.ctrl_attributes` member. The
syntax for this dictionary is the same as the one used for
:attr:`~sardana.pool.controller.Controller.axis_attributes`.

Here is an example on how to specify a read-only float matrix attribute called
*ReflectionMatrix* at the controller level:

.. code-block:: python 

    class SpringfieldMotorController(MotorController):
    
        ctrl_attributes = { 
            "ReflectionMatrix" : {
                    Type         : ( (float,), ),
                    Description  : "The reflection matrix",
                    Access : DataAccess.ReadOnly,
                },
        }
        
        def getReflectionMatrix(self):
            return ( (1.0, 0.0), (0.0, 1.0) )

Or, similar to what you can do with axis attributes:

.. code-block:: python

    class SpringfieldMotorController(MotorController):
    
        ctrl_attributes = \
        { 
            "ReflectionMatrix" : {
                    Type         : ( (float,), ),
                    Description  : "The reflection matrix",
                    Access : DataAccess.ReadOnly,
                },
        }
        
        def GetCtrlPar(self, name):
            if name == "ReflectionMatrix":
                return ( (1.0, 0.0), (0.0, 1.0) )

.. _sardana-controller-howto-controller-properties:

Extra controller properties
~~~~~~~~~~~~~~~~~~~~~~~~~~~

A more static form of attributes can be defined at the controller level.
These *properties* are loaded into the controller at the time of object
construction. They are accessible to your controller at any time but it is
not possible for a user from outside to modify them.
The way to define :attr:`~sardana.pool.controller.Controller.ctrl_properties` is
very similar to the way you define extra axis attributes or extra controller
attributes.

Here is an example on how to specify a host and port properties:

.. code-block:: python

    class SpringfieldMotorController(MotorController):
    
        ctrl_properties = \
        {
            "host" : { 
                    Type : str,
                    Description : "host name"
                },
            "port" : {
                    Type : int, 
                    Description : "port number",
                    DefaultValue: springfieldlib.SpringfieldMotorHW.DefaultPort 
               },
        }

        def __init__(self, inst, props, *args, **kwargs):
            super(SpringfieldMotorController, self).__init__(inst, props, *args, **kwargs)
            
            host = self.host
            port = self.port
                        
            # initialize hardware communication
            self.springfield = springfieldlib.SpringfieldMotorHW(host=host, port=port)
            
            # do some initialization
            self._motors = {}

As you can see from lines 15 and 16, to access your controller properties
simply use ``self.<property name>``. Sardana assures that every property has a
value. In our case, when a SpringfieldMotorController is created, if port
property is not specified by the user (example: using the ``defctrl`` macro in
spock), sardana assignes the default value
``springfieldlib.SpringfieldMotorHW.DefaultPort``. On the other hand, since host
has no default value, if it is not specified by the user, sardana will complain
and fail to create and instance of SpringfieldMotorController.

.. _sardana-controller-howto-error-handling:

Error handling
~~~~~~~~~~~~~~

When you write a controller it is important to properly handle errors
(example: motor power overload, hit a limit switch, lost of communication with
the hardware).

These are the two basic sardana rules you should have in mind:

#. The exceptions which are not handled by the controller are handled by sardana,
   usually by re-raising the exception (when sardana runs as a Tango_ DS a
   translation is done from the Python_ exception to a Tango_ exception).
   The :meth:`~sardana.pool.controller.Controller.StateOne` method is handled a
   little differently: the state is set to ``Fault`` and the status will contain
   the exception information.

#. When the methods which are supposed to return a value (like
   :meth:`~sardana.pool.controller.Controller.GetAxisPar`) don't return a value
   compatible with the expected data type (including :obj:`None`) a 
   :exc:`TypeError` exception is thrown.

In every method you should carefully choose how to do handle the possible
exceptions/errors. 

Usually, catch and handle is the best technique since it is the code of your
controller which knows exactly the workings of the hardware. You can
discriminate errors and decide a proper handle for each. Essencially, this
technique consists of:

#. catching the error (if an exception: with :keyword:`try` ... :keyword:`except`
   clause, if an expected return of a function: with a :keyword:`if` ... 
   :keyword:`elif` ... :keyword:`else` statement, etc)

#. raise a proper exception (could be the same exception that has been catched)
   or, if in :meth:`~sardana.pool.controller.Controller.StateOne`, return the
   apropriate error state (``Fault``, ``Alarm``) and a descriptive status.
    
Here is an example: if the documentation of the underlying library says that:

    `reading the motor closeloop raises CommunicationFailed if it is not
    possible to communicate with the Springfield hardware`

    `reading the motor state raises MotorPowerOverload if the motors
    has a power overload or a MotorTempTooHigh when the motor
    temperature is too high`

then you should handle the exception in the controller and return a proper
state information::

    def getCloseLoop(self, axis):
        # Here the "proper exception" to raise in case of error is actually the
        # one that is raised from the springfield library so handling the
        # exception is transparent. Nice!
        return self.springfield.isCloseLoopActive(axis)

    def StateOne(self, axis):
        springfield = self.springfield
        
        try:
            state = self.StateMap[ springfield.getState(axis) ]
            status = springfield.getStatus(axis)
        except springfieldlib.MotorPowerOverload:
            state = State.Fault
            status = "Motor has a power overload"
        except springfieldlib.MotorTempTooHigh:
            temp = springfield.getTemperature(axis)
            state = State.Alarm
            status = "Motor temperature is too high (%f degrees)" % temp      

        limit_switches = MotorController.NoLimitSwitch
        hw_limit_switches = springfield.getLimits(axis)
        if hw_limit_switches[0]:
            limit_switches |= MotorController.HomeLimitSwitch
        if hw_limit_switches[1]:
            limit_switches |= MotorController.UpperLimitSwitch
        if hw_limit_switches[2]:
            limit_switches |= MotorController.LowerLimitSwitch
        return state, status, limit_switches

Hiding the exception is usually a **BAD** technique since it prevents the user
from finding what was the cause of the problem. You should only use it in
extreme cases (example: if there is a bug in sardana which crashes the server
if you try to properly raise an exception, then you can **temporarely** use
this technique until the bug is solved).

Example::

    def getCloseLoop(self, axis):
        # BAD error handling technique
        try:
            return self.springfield.isCloseLoopActive(axis)
        except:
            pass

.. rubric:: Footnotes

.. [#f1] Pseudo controllers don't need to manage their individual axis. Therefore,
         for pseudos you will not implement these methods
         

.. [#f2] For pseudo controllers, sardana will calculate the state of each pseudo
         axis based on the state of the elements that serve as input to the
         pseudo controller. Therefore, for pseudos you will not implement these
         methods 
        
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
