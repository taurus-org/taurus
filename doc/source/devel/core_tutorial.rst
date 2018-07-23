
.. currentmodule:: taurus.core

.. _taurus-core-tutorial:

=====================
taurus core tutorial
=====================

The core has been designed to provide a model-based abstraction to the various 
sources of data and/or control objects supported via the Taurus schemes (we use 
the term "model" to refer to the model component in an MVC driven architecture). 

A scheme is a plugin for Taurus that provides the glue between Taurus and a
given source of data and/or of objects that can be controlled. For example, 
schemes exist for various control system libraries (such as
Tango_, or EPICS_) as well as for processing data (e.g. the
:mod:`taurus.core.evaluation` scheme).

Each scheme implements at least a Factory (derived from 
:class:`taurus.core.TaurusFactory`) which provides Taurus model objects ,
for a given model name.

.. _model-concept:

Model concept
-------------

All Taurus Elements (Devices, Attributes, etc) are model objects with an 
associated unique name. The model name is an URI (as defined in RFC3986_).

In practice, the URIs have the following form (for a complete and rigorous 
description refer to RFC3986_):

[<scheme>:][<authority>][<path>][?<query>][#<fragment>]

Notes: 

- The <authority>, if present, starts by '//'
- The <path>, if present, starts by '/' (except for relative URIs)

A model object (also referred to occasionally as Taurus Element) is an instance 
of a class derived from one of :class:`taurus.core.TaurusAuthority`, 
:class:`taurus.core.TaurusDevice`, :class:`taurus.core.TaurusAttribute`.


Examples of model names
-----------------------

Different schemes may choose different conventions to name the models that they
provide. 

The following are some examples for the :mod:`taurus.core.tango` scheme:

The full Taurus model name for a Tango device `sys/tg_test/1` registered in
a Tango Database running on `machine:10000` is:

``tango://machine:10000/sys/tg_test/1``

Now, if we assume that:

  - ``tango`` is set as the default scheme and that
  - ``machine:10000`` is set as the default TANGO_HOST
  - and that ``tgtest1`` is set as an alias of ``sys/tg_test/1``

then the same Tango device could be accessed as:

``tgtest1``

In the case of Tango attributes, here are some equivalent examples given the
above assumptions:
  
``tango://machine:10000/sys/tg_test/1/double_scalar``,
 
``sys/tg_test/1/double_scalar``,

``tango:tgtest1/double_scalar``,

``tgtest1/double_scalar``

See :mod:`taurus.core.tango` for a more exhaustive description and more
examples related to Tango.

The following are some examples for the :mod:`taurus.core.evaluation` scheme:

An evaluation attribute that generates an array of dimensionless random
values when read:
    
``eval:rand(256)``

An evaluation attribute that applies a multiplication factor to an existing 
tango attribute (and which is updated every time that the tango attribute 
changes):

``eval:123.4*{tango:sys/tg_test/1/double_scalar}``

Or one that adds noise to a tango image attribute:
    
``eval:img={tango:sys/tg_test/1/short_image_ro};img+10*rand(*img.shape)``

And, by using custom evaluators, one can easily access virtually anything
available from a python module. For example, using the datetime module
to get today's date as a Taurus attribute:

``eval:@datetime.*/date.today().isoformat()``

See :mod:`taurus.core.evaluation` for a more exhaustive description and some 
tricks with the Evaluation scheme and the custom evaluators.

Now an example for the :mod:`taurus.core.epics` scheme. The model name for the 
EPICS process variable (PV) "my:example.RBV" is:

``epics:my:example.RBV``

Note that you can create your own schemes and add them to taurus (e.g., a 
scheme to access your own home-brew control system). Some schemes that are in 
our TO-DO list are:

- A scheme to access datasets in HDF5 files as Taurus attributes
- A scheme to access ranges of cells in a spreadsheet file as Taurus attributes
- A scheme to access column/row data in ASCII files as Taurus attributes
- A scheme to access data from mySQL databases as Taurus attributes
- A scheme to access Tango-archived data as Taurus attributes
 
model access
------------

Taurus users are encouraged to write code that is "scheme-agnostic",
that is, that it neither assumes the availability of certain schemes nor uses
any scheme-specific feature. For this, Taurus provides several high-level 
scheme-agnostic helpers to obtain the Taurus Element associated to a given 
model name:

- :func:`taurus.Authority`
- :func:`taurus.Device`
- :func:`taurus.Attribute`
- :func:`taurus.Object`

The first three helpers require you to know which type of Element (i.e., 
Attribute, Device or Authority) is represented by the model name. If you do not know that
beforehand, you can use :meth:`taurus.Object` which will automatically find the 
type and provide you with the corresponding model object (but of course this is 
slightly less efficient than using one of the first three helpers).

These helpers will automatically find out which scheme corresponds to the given 
model and will delegate the creation of the model object to the corresponding 
scheme-specific Factory. Therefore, the returned model object will be of a 
specialized subclass of the corresponding Taurus generic Element and it 
will expose the scheme-agnostic API plus optionally some scheme-specific 
methods (e.g., :class:`taurus.core.tango.TangoDevice` objects provide all the 
API of a :class:`taurus.core.TaurusDevice` but they also provide all the methods 
from a :class:`PyTango.DeviceProxy`)

For example, obtaining the device model object for a TangoTest Device
can be done as follows::

    import taurus
    testDev = taurus.Device('sys/tg_test/1')
    
or, using :meth:`taurus.Object`::
 
    import taurus
    testDev = taurus.Object('sys/tg_test/1')
    
Also for example, obtaining the Taurus Attribute model corresponding to the 
EPICS Process Variable called "my:example.RBV" is just::

    import taurus
    testDev = taurus.Attribute('epics:my:example.RBV')

Taurus also provides other helpers to access lower level objects for dealing
with models:

- :func:`taurus.Factory`
- :func:`taurus.Manager`

And also some useful methods to validate names, find out the element type(s) 
for a given name and other related tasks:

- :func:`taurus.isValidName`
- :func:`taurus.getValidTypesForName`
- :func:`taurus.getSchemeFromName`


Advantages of accessing Tango via Taurus over PyTango
-----------------------------------------------------

If you are familiar with PyTango_ you may be asking yourself what is the real 
advantage of using taurus instead of PyTango_ directly for accessing Tango 
objects. There are actually many benefits from using taurus. Here is a list of 
the most important ones.

*integration with other schemes*
    Taurus is not just Tango. For example, you can treat a Tango Attribute just 
    as you would treat an EPICS attribute, and use them both in the same 
    application. 

*model unicity:*
    you may request the same model many times without performance hit, since
    taurus will give you the same object::
        
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

*model intelligence:*
    taurus is clever enough to know that, for example, 'sys/tg_test/1' 
    represents the same model as 'tango:SYS/Tg_TEST/1' so::
    
        >>> import taurus
        >>> sim1 = taurus.Device('sys/tg_test/1')
        >>> sim2 = taurus.Device('tango:SYS/Tg_TEST/1')
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
.. _EPICS: http://www.aps.anl.gov/epics/
.. _RFC3986: https://tools.ietf.org/html/rfc3986
