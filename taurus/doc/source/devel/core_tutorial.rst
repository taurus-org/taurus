
.. currentmodule:: taurus.core

.. _taurus-core-tutorial:

=====================
taurus core tutorial
=====================

The core module, besides other things, is a container for models (we will use 
the term "model" to refer to the model component in an MVC driven architecture).

The core as been designed to provide models for Tango_ but can also be extended 
to provide models for other libraries like SPEC_ or EPICS_. That is why you will
never find yourself writting code to create Device objects directly.
Instead, all requests for taurus objects should go through one of the two major 
``taurus.core`` components:

  - :class:`taurus.core.TaurusManager`
  - :class:`taurus.core.TaurusFactory`

An important aspect of the core is that it is only dependent on PyTango_. This
means that you could potentially use taurus.core inside your python device server
to access any other tango elements (database, devices, attributes...)

But before I show you how to access these objects, a word on the taurus concept of
model.

.. _model-concept:

model concept
-------------

The model in taurus is tipically any server based object like Database, Device, 
Attribute. Each model has a unique name (model name). This name is a string 
with a Uniform Resouce Identifier (URI) format.

::

    foo://username:password@example.com:8042/over/there/index.dtb;type=animal?name=ferret#nose
    \ /   \________________/\_________/ \__/\_________/ \___/ \_/ \_________/ \_________/ \__/
     |           |               |        |     |         |     |       |            |     |
  scheme     userinfo         hostname  port  path  filename extension parameter(s) query fragment
          \________________________________/
                      authority

For Tango:

- The 'scheme' must be the string "tango" (lowercase mandatory)

- The 'authority' is the Tango database (<hostname> and <port> mandatory)

- The 'path' is the Tango object, which can be a Device or Attribute.
  For device it must have the format _/_/_ or alias 
  For attribute it must have the format _/_/_/_ or devalias/_
  
- The 'filename' and 'extension' are always empty

- The 'parameter' is always empty

- The 'the query' is valid when the 'path' corresponds to an Attribute. Valid
  queries must have the format configuration=<config param>. Valid 
  configuration parameters are: label, format, description, unit, display_unit, 
  standard_unit, max_value, min_value, max_alarm, min_alarm, 
  max_warning, min_warning. in this case the Tango object is a Configuration

So, for example, the full model name for the tango device `sys/tg_test/1` is: 

``tango://machine:10000/sys/tg_test/1``

taurus uses the tango scheme by default so the previous name can be shortened to:

``machine:10000/sys/tg_test/1``

and if you have a TANGO_HOST (or tango.rc) pointing to `machine:10000` you can
even reduce the previous name to a shorter one:

``sys/tg_test/1``

Below follows a non exaustive list of taurus models that convers 99% of the needs:

- *scheme*: the URI scheme (aka protocol)

  - Syntax: ``<string>://``
  - For tango is always: ``tango://``
  
- *database*

  - For tango: ``[<scheme>]<host>:<port>``
  - example: ``tango://machine:10000``
  
- *device*

  - For tango: ``[<database>/]<string>/<string>/<string> | [<database>/]<string>``
  - examples: ``tango://machine:10000/sys/tg_test/1``, ``sys/tg_test/1``, ``tango://tg_test1``, ``tg_test1``
  
- *attribute*

  - For tango: ``<device>/<string>``
  - examples: ``tango://machine:10000/sys/tg_test/1/position``, ``sys/tg_test/1/double_scalar``, ``tango://tg_test1/double_scalar``, ``tg_test1/double_scalar``

- *attribute configuration parameter*

  - For tango: ``<attribute>?configuration=<string>``
  - example: ``sys/tg_test/1/double_scalar?configuration=label``

model access
------------

As mentioned above, a model object is obtained through the :class:`taurus.core.TaurusManager` 
and :class:`taurus.core.TaurusFactory` classes.
To simplify the API, taurus provides some functions that hide the access to the
:class:`taurus.core.TaurusManager` and :class:`taurus.core.TaurusFactory` classes. So here is 
how you get a model object for a device called `sys/tg_test/1`::

    import taurus
    tautest = taurus.Device('sys/tg_test/1')

At first you may think that this code contradicts what I said before about not 
creating taurus models directly. This is because taurus.Device is a function, not a 
python class. Here is the equivalent code accessing the low level taurus library::

    import taurus.core
    manager = taurus.core.TaurusManager()
    factory = manager.getFactory() # by default the factory scheme is 'tango'
    tautest = factory.getDevice('sys/tg_test/1')

In line 2 taurus gives you a reference to the singleton object of class 
:class:`taurus.core.TaurusManager`. In line 3 the manager gives you a singleton 
reference to a tango implementation of the class :class:`taurus.core.TaurusFactory` 
(should be :class:`taurus.core.tango.TangoFactory`). In line 4, the factory gives 
you a tango implementation of the class :class:`taurus.core.TaurusDevice` (should be
:class:`taurus.core.tango.TangoDevice`).

If you don't know which type of object your model name represents, you can use::

    import taurus
    tautest = taurus.Object('sys/tg_test/1')

or the equivalent low level API::

    import taurus.core
    manager = taurus.core.TaurusManager()
    tautest = manager.getObject('sys/tg_test/1')

Note, however, that that using the Object API is slightly slower since you are
implicitly asking taurus to search for the appropriate model type that corresponds
to the model name you gave.

Similarly, if you need access to an attribute (say double_scalar) the code should be::

    import taurus
    position = taurus.Attribute('sys/tg_test/1/double_scalar')

or if you have already a taurus device::

    import taurus
    tautest = taurus.Device('sys/tg_test/1')
    position = tautest.getAttribute('double_scalar')

Advantages over PyTango
-----------------------

If you are familiar with PyTango_ you may be asking yourself what is the real 
advantage of using taurus instead of PyTango_ directly. There are actually many 
benefits from using taurus. Here is a list of the most important ones.

*model unicity:*
    you may request as many times as you like for the same model name and taurus
    will give you the same object::
        
        >>> import taurus
        >>> sim1 = taurus.Device('sys/tg_test/1')
        >>> sim2 = taurus.Device('sys/tg_test/1')
        >>> print sim1 == sim2
        True
    
    Whereas in PyTango_ the same code always results in the construction of new
    DeviceProxy objects::
    
        >>> import PyTango
        >>> sim1 = PyTango.DeviceProxy('sys/tg_test/1')
        >>> sim2 = PyTango.DeviceProxy('sys/tg_test/1')
        >>> print sim1 == sim2
        False

*model inteligence:*
    taurus is clever enough to know that, for example, 'sys/tg_test/1' represents
    the same model as 'tango://SYS/Tg_TEST/1' so::
    
        >>> import taurus
        >>> sim1 = taurus.Device('sys/tg_test/1')
        >>> sim2 = taurus.Device('tango://SYS/Tg_TEST/1')
        >>> print sim1 == sim2
        True
    
*tango event abstraction:*
    taurus cleverly hides the complexities and restrictions of the tango event 
    system. With taurus you can:
    
      - subscribe to the same event multiple times
      - handle tango events from any thread
    
    Some optimizations are also done to ensure that the tango event thread is
    not blocked by the user event handle code.
    
.. _Tango: http://www.tango-controls.org/
.. _PyTango: http://packages.python.org/PyTango/
.. _QTango: http://www.tango-controls.org/download/index_html#qtango3
.. _`PyTango installation steps`: http://packages.python.org/PyTango/start.html#getting-started
.. _Qt: http://qt.nokia.com/products/
.. _PyQt: http://www.riverbankcomputing.co.uk/software/pyqt/
.. _PyQwt: http://pyqwt.sourceforge.net/
.. _IPython: http://ipython.scipy.org/
.. _ATK: http://www.tango-controls.org/Documents/gui/atk/tango-application-toolkit
.. _Qub: http://www.blissgarden.org/projects/qub/
.. _numpy: http://numpy.scipy.org/
.. _SPEC: http://www.certif.com/
.. _EPICS: http://www.aps.anl.gov/epics/