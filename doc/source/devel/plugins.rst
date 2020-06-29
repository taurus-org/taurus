.. _plugins:

==============
Taurus plugins
==============

.. note:: The taurus plugins API is still experimental. Current entry point
         group names, and expected entry point objects API may be modified or
         removed in later versions.

Taurus can be extended by third party modules in various ways. For example, a
mechanism exists since before v4.0.0 to use add new schemes to the
`taurus.core` module. But these extension mechanisms grew organically and
independently of each other, resulting in several non-consistent plugin APIs.
This has been long-standing pending issue as can be seen by date of the draft
of the TEP13_

Since taurus v4.3 we started introducing some experimental `pkg_resources`-
based entry points, in an effort to test their viability for being used as a
more generic and standard mechanism for plugins. Here we describe such
APIs which, for now and until TEP13_ is approved, should be still considered
experimental.


Entry point-based plugins:
--------------------------

The following table lists the entry-point groups used by taurus, with links to
the appropriate docs.

+---------------------------------+----------------------------------------+-------+
| Entry point group               | Description                            | Notes |
+=================================+========================================+=======+
| taurus.qt.qtgui                 | submodules of taurus.qt.qtgui          | 1     |
+---------------------------------+----------------------------------------+-------+
| taurus.cli.subcommands          | click subcommands for the `taurus`     | 2     |
|                                 | command.                               |       |
+---------------------------------+----------------------------------------+-------+
| taurus.model_selector.items     | items for `TaurusModelSelector`        | 3     |
+---------------------------------+----------------------------------------+-------+
| taurus.qt.formatters            | formatter objects for taurus widgets   | 4     |
+---------------------------------+----------------------------------------+-------+
| - taurus.plot.alts              | Alternative implementations for        | 2     |
| - taurus.trend.alts             | various basic widgets. To be used in   |       |
| - taurus.trend2d.alts           | in, e.g. the `taurus plot` subcommand, |       |
| - taurus.image.alts             | etc.                                   |       |
+---------------------------------+----------------------------------------+-------+
| taurus.form.item_factories      | Factories for custom "taurus value"    | 5     |
|                                 | widgets to be used in taurus forms     |       |
+---------------------------------+----------------------------------------+-------+
| taurus.core.schemes             | Schemes in taurus.core                 | 6     |
+---------------------------------+----------------------------------------+-------+


Notes:

1. For internal use only (used backwards compatibility when "outsourcing"
submodules).
2. See :mod:`taurus.cli`
3. See :class:`taurus.qt.qtgui.panel.TaurusModelSelector`
4. See :meth:`taurus.qt.qtgui.base.TaurusBaseComponent.displayValue`
5. See :meth:`taurus.qt.qtgui.panel.TaurusForm.setItemFactories`





.. _TEP13: http://www.taurus-scada.org/tep?TEP13.md
