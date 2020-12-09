.. _migration_to_taurus4:

==================================
Taurus 3.x to 4.x migration guide
==================================

Taurus 4 was released in July 2016 with the main goal of making Taurus scheme-agnostic
(i.e. not relying on Tango for its core functionalities).

Being a major version change,
it is not fully backwards-compatible with the previous taurus 3.x versions.

However, a design goal for the 4.x series was to smooth the transition from 3.x as much
as possible, and a backwards-compatibility layer which will mark old taurus code as
deprecated but otherwise attempt to transparently support it in Taurus4 whenever that
is possible.

Thanks to this compatibility layer, a Taurus 3 application is likely to run on taurus 4
after minimal or even no changes (but typically producing deprecation warnings and
possibly with some functionality slightly altered).

A good strategy for migrating a taurus 3 application or widget to taurus 4 is to attempt
to run it as-is with taurus 4 and then try to remove any deprecation warnings one by one.
Most changes will be related to one of the following:

- renamed methods and APIs (see the *API changes* section below),
- differences between Tango states and Taurus states (see the *Working with States* section below)
- Use of quantities for values (see the *Working with quantities* section below)


.. note::
    The main sources of information regarding the changes introduced in
    Taurus 4 are the following two Enhancement proposals:

      - TEP3_
      - TEP14_

    These changes are also treated in the `Taurus 4 slides`_


API Changes
------------

The following is a table of Taurus 3.x public members (classes, methods, attributes, etc) that became deprecated in Taurus 4

This list is a best-effort to document changes, but it may not be 100% complete (please feel free to suggest changes)

**IMPORTANT**: in some cases, the proposed alternative can be used as a drop-in replacement of the deprecated code, but in some others the code may need some adaptation.

+-----------------------------------------------+---------------------------------------------------------------+
| Member                                        |                 Alternative(s)                                |
+===============================================+===============================================================+
| TaurusConfigValue                             |                   TaurusAttribute / TaurusAttrValue           |
+-----------------------------------------------+---------------------------------------------------------------+
| TaurusConfigurationProxy                      |                   TaurusAttribute                             |
+-----------------------------------------------+---------------------------------------------------------------+
| TaurusConfiguration                           |                   TaurusAttribute                             |
+-----------------------------------------------+---------------------------------------------------------------+
| Configuration (helper)                        |                   Attribute (helper)                          |
+-----------------------------------------------+---------------------------------------------------------------+
| Database (helper)                             |                   Authority (helper)                          |
+-----------------------------------------------+---------------------------------------------------------------+
| TaurusManager.{g,s}etOperationMode            |                    --                                         |
+-----------------------------------------------+---------------------------------------------------------------+
+-----------------------------------------------+---------------------------------------------------------------+
| xxxAttrValue.<foo>                            |                                                               |
| *(where <foo> is any config option)*          | xxxAttribute.<foo>                                            |
+-----------------------------------------------+---------------------------------------------------------------+
| xxxAttribute.value                            | xxxAttribute.rvalue                                           |
+-----------------------------------------------+---------------------------------------------------------------+
| xxxAttribute.w_value                          | xxxAttribute.wvalue                                           |
+-----------------------------------------------+---------------------------------------------------------------+
| xxxAttribute.has_failed                       | xxxAttribute.error                                            |
+-----------------------------------------------+---------------------------------------------------------------+
+-----------------------------------------------+---------------------------------------------------------------+
| TangoAttribute.{g,s}etDescription             | TangoAttribute.description                                    |
+-----------------------------------------------+---------------------------------------------------------------+
| TangoAttribute.isInformDeviceOfErrors         | --                                                            |
+-----------------------------------------------+---------------------------------------------------------------+
| TangoAttribute.displayValue                   |  str                                                          |
+-----------------------------------------------+---------------------------------------------------------------+
| TangoAttribute.getDisplayValue                | TangoAttribute.getLabel                                       |
+-----------------------------------------------+---------------------------------------------------------------+
| TangoAttribute.getDisplayUnit                 | TangoAttribute.rvalue.units                                   |
+-----------------------------------------------+---------------------------------------------------------------+
| TangoAttribute.getStandardUnit                | TangoAttribute.rvalue.units                                   |
+-----------------------------------------------+---------------------------------------------------------------+
| TangoAttribute.getUnit                        | TangoAttribute.rvalue.units                                   |
+-----------------------------------------------+---------------------------------------------------------------+
| TangoAttribute.unit                           | TangoAttribute.rvalue.units                                   |
+-----------------------------------------------+---------------------------------------------------------------+
| TangoAttribute.getDisplayWriteValue           | --                                                            |
+-----------------------------------------------+---------------------------------------------------------------+
| TangoAttribute.getWritable                    | TangoAttribute.isWritable                                     |
+-----------------------------------------------+---------------------------------------------------------------+
| TangoAttribute.is{Scalar,Spectrum,Image}      | TangoAttribute.data_format                                    |
+-----------------------------------------------+---------------------------------------------------------------+
| TangoAttribute.getMaxDim{X,Y}                 | TangoAttribute.getMaxDim                                      |
+-----------------------------------------------+---------------------------------------------------------------+
| TangoAttribute.getShape                       | *introspect the value shape if applicable*                    |
+-----------------------------------------------+---------------------------------------------------------------+
| TangoAttribute.getParam                       | TangoAttribute.getAttributeInfoEx                             |
+-----------------------------------------------+---------------------------------------------------------------+
| TangoAttribute.setParam                       | *use PyTango*                                                 |
+-----------------------------------------------+---------------------------------------------------------------+
| TangoAttribute.getConfig                      | self  *(merged)*                                              |
+-----------------------------------------------+---------------------------------------------------------------+
| TangoAttribute.getCRanges                     | TangoAttribute .range + .alarms + .warnings                   |
+-----------------------------------------------+---------------------------------------------------------------+
| TangoAttribute.getCLimits                     | TangoAttribute.range                                          |
+-----------------------------------------------+---------------------------------------------------------------+
| TangoAttribute.getMinValue                    | TangoAttribute.range                                          |
+-----------------------------------------------+---------------------------------------------------------------+
| TangoAttribute.getMaxValue                    | TangoAttribute.range                                          |
+-----------------------------------------------+---------------------------------------------------------------+
| TangoAttribute.climits                        | TangoAttribute.range                                          |
+-----------------------------------------------+---------------------------------------------------------------+
| TangoAttribute.getCAlarms                     | TangoAttribute.alarms                                         |
+-----------------------------------------------+---------------------------------------------------------------+
| TangoAttribute.getMinAlarm                    | TangoAttribute.alarms                                         |
+-----------------------------------------------+---------------------------------------------------------------+
| TangoAttribute.getMaxAlarm                    | TangoAttribute.alarms                                         |
+-----------------------------------------------+---------------------------------------------------------------+
| TangoAttribute.min_alarm                      | TangoAttribute.alarms                                         |
+-----------------------------------------------+---------------------------------------------------------------+
| TangoAttribute.max_alarm                      | TangoAttribute.alarms                                         |
+-----------------------------------------------+---------------------------------------------------------------+
| TangoAttribute.calarms                        | TangoAttribute.alarms                                         |
+-----------------------------------------------+---------------------------------------------------------------+
| TangoAttribute.getCWarnings                   | TangoAttribute.warnings                                       |
+-----------------------------------------------+---------------------------------------------------------------+
| TangoAttribute.getMinWarning                  | TangoAttribute.warnings                                       |
+-----------------------------------------------+---------------------------------------------------------------+
| TangoAttribute.getMaxWarning                  | TangoAttribute.warnings                                       |
+-----------------------------------------------+---------------------------------------------------------------+
| TangoAttribute.min_warning                    | TangoAttribute.warnings                                       |
+-----------------------------------------------+---------------------------------------------------------------+
| TangoAttribute.max_warning                    | TangoAttribute.warnings                                       |
+-----------------------------------------------+---------------------------------------------------------------+
| TangoAttribute.cwarnings                      | TangoAttribute.warnings                                       |
+-----------------------------------------------+---------------------------------------------------------------+
+-----------------------------------------------+---------------------------------------------------------------+
| TangoDevice.getState                          | TangoDevice.stateObj.read().rvalue *tango* or                 |
|                                               | .state  *agnostic*                                            |
+-----------------------------------------------+---------------------------------------------------------------+
| TangoDevice.state() *PyTango.DeviceProxy API* | TangoDevice.stateObj.read(cache=False).rvalue *tango* or      |
|                                               | .state  *agnostic*                                            |
+-----------------------------------------------+---------------------------------------------------------------+
| TangoDevice.getStateObj                       | TangoDevice.stateObj  *tango* or                              |
|                                               | .factory.getAttribute(state_full_name)  *agnostic*            |
+-----------------------------------------------+---------------------------------------------------------------+
| TangoDevice.getSWState                        | TangoDevice.state                                             |
+-----------------------------------------------+---------------------------------------------------------------+
| TangoDevice.getValueObj                       | TangoDevice.stateObj.read  *tango* or                         |
|                                               | .state  *agnostic*                                            |
+-----------------------------------------------+---------------------------------------------------------------+
| TangoDevice.getDisplayValue                   | TangoDevice.stateObj.read().rvalue.name  *tango*  or          |
|                                               | .state.name  *agnostic*                                       |
+-----------------------------------------------+---------------------------------------------------------------+
| TangoDevice.getHWObj                          | TangoDevice.getDeviceProxy                                    |
+-----------------------------------------------+---------------------------------------------------------------+
| TangoDevice.isValidDev                        | (TangoDevice.getDeviceProxy() is not None)                    |
+-----------------------------------------------+---------------------------------------------------------------+
| TangoDevice.getDescription                    | TangoDevice.description                                       |
+-----------------------------------------------+---------------------------------------------------------------+
+-----------------------------------------------+---------------------------------------------------------------+
| TangoDatabase                                 | TangoAuthority                                                |
+-----------------------------------------------+---------------------------------------------------------------+
| TangoAuthority.getHWObj                       | TangoAuthority.getDeviceProxy                                 |
+-----------------------------------------------+---------------------------------------------------------------+
| TangoAuthority.getValueObj                    | TangoAuthority.getTangoDB                                     |
+-----------------------------------------------+---------------------------------------------------------------+
| TangoAuthority.getDisplayValue                | TangoAuthority.getFullName                                    |
+-----------------------------------------------+---------------------------------------------------------------+
| TangoAuthority.getDescription                 | TangoAuthority.description                                    |
+-----------------------------------------------+---------------------------------------------------------------+
+-----------------------------------------------+---------------------------------------------------------------+
| TangoFactory.getAttributeInfo                 | TangoFactory.getAttribute                                     |
+-----------------------------------------------+---------------------------------------------------------------+
| TangoFactory.getConfiguration                 | TangoFactory.getAttribute                                     |
+-----------------------------------------------+---------------------------------------------------------------+
| TangoDevice.{g,s}etOperationMode              | --                                                            |
+-----------------------------------------------+---------------------------------------------------------------+


Working with quantities
------------------------

One of the most visible changes in Taurus 4 is its use of quantities for the values
of numeric attributes.

In Taurus 4 all the values of numeric (float or integer) attributes and their associated
properties (such as limits, warning levels, etc.) are :class:`pint.Quantity` objects provided
by the :mod:`pint` python module. A Quantity is essentially the combination of a `magnitude`
and a `unit`. In taurus 3.x all values were just "magnitudes", and their units were either
implicit or loosely described as a free string property, but not enforced in any way.

By using Quantities Taurus 4 can automatically verify the dimensional validity of
operations and provide support for I/O using user-preferred units.

Taurus 3 applications use `.value` or `.w_value` to get the read or write
magnitude of a taurus value, respectively. In taurus 4 these would be equivalent
to `.rvalue.magnitude` and `.wvalue.magnitude`, but the recommended way to adapt
a Taurus 3 application is to use the Quantity objects, not their magnitudes
(i.e., `rvalue` and `wvalue`) and refactor the code if necessary.

For example, given the following taurus 3 code **where we assume that ampli is in meters**::

    v = taurus.Attribute('sys/tg_test/1/ampli').read()
    foo = 5 + v.value  # here "5" is implicitly assumed to mean "5 meters"

a lazy conversion to avoid deprecation warnings in taurus 4 would be::

    v = taurus.Attribute('sys/tg_test/1/ampli').read()
    foo = 5 + v.rvalue.magnitude

...which is a very direct translation (and exactly what the automated backwards
compatibility layer already does for you). However, the recommended
conversion should use Quantities rather than magnitudes, e.g::

    from taurus.core.units import UR  # import the taurus unit registry
    v = taurus.Attribute('sys/tg_test/1/ampli').read()
    foo = 5 * UR.meters + v.value  # use explicit units

Or, using the Quantity constructor instead of the `Unit Registry`::

    from taurus.core.units import Q_  # import the taurus Quantity factory
    v = taurus.Attribute('sys/tg_test/1/ampli').read()
    foo = Q_("5 meters")  + v.value

Finally, note that when using Quantities, you do not need to care about
matching the units, as long as they are dimensionally compatible::

    foo = Q_("15 feet") + v.value


Working with Device states
--------------------------

Taurus 4 is all about being "scheme-agnostic". This means that the taurus core
(and ideally the main widgets as well) should not assume that the model objects
(attributes, devices, authorities) are of one specific source type (Tango, Epics,
Evaluation...)

This implies that the APIs should be scheme-agnostic. In Taurus 3, the concept
of *device state* is completely "tango-centric" and it has been replaced in
Taurus 4 by a much more generic one where the devices are either "ready" or "not
ready" (this is of course much less informative, but it is generic enough to
accomodate schemes where the sources of data may not even be hardware-related).

In Taurus 4, the Taurus device states are defined in the
`taurus.core.TaurusDevState` enumeration, and the tango device states are
supported by the tango scheme in `taurus.core.tango.DevState` enumeration, which
is a numerically-compatible translation of `PyTango.DevState`

Some taurus 3.x applications may implement logic that depends on Tango states,
or maybe display information based on the rich palette of Tango state colors.
In these cases, when converting the application to Taurus 4 one needs to decide
if the simple Taurus states are enough (in which case one should refactor the
logic and use `device.state` to get the *Taurus* device state) or if the richer
tango states are required to the point of sacrificing the scheme-agnosticism of
the application (in which case one can use `device.stateObj.read().rvalue` to
obtain the *Tango* device state)




.. _TEP3: http://sf.net/p/tauruslib/wiki/TEP3
.. _TEP14: http://sf.net/p/tauruslib/wiki/TEP14
.. _`Taurus 4 slides`: https://indico.esrf.fr/indico/event/4/session/6/contribution/17/material/slides/
