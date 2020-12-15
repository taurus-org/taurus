.. _plugins:

==============
Taurus plugins
==============

Taurus can be extended by third party modules in various ways. The TEP13_
prescribes some generic rules in order to unify the plugins support by using
entry point APIs.

The following subsections describe each entry point based pluggable interface
currently supported by taurus, according to TEP13_.

CLI subcommands
-----------------------------------

- Description: register subcommands for the `taurus` CLI command. See :mod:`taurus.cli`
- Group: `taurus.cli.subcommands`
- Expected API: :class:`click.Command`
- Entry point name convention: None, the name is ignored. Suggestion: use the
  subcommand name
- Loading pattern: extension (loaded when invoking the taurus command)
- Enabling pattern: installation
- Examples: `taurus` self-registers all its subcommands (see `setup.py`)

Schemes
-----------------------------------


- Description: new schemes in taurus.core to support other sources of data.
- Group: `taurus.core.schemes`
- Expected API: python module implementing a Taurus scheme. It should at least
  provide a `TaurusFactory` specialization. See more details in the Taurus Core
  Tutorial (http://taurus-scada.org/devel/core_tutorial.html)
- Entry point name convention: the name must match the module name.
  For example: `h5file = h5file`
- Loading pattern: Driver
- Enabling pattern: installation
- Examples: taurus_tangoarchiving_ registers itself as a scheme

Formatters
-----------------------------------

- Description: adding formatter objects for taurus widgets, as used by
  :meth:`taurus.qt.qtgui.base.TaurusBaseComponent.displayValue`
- Group: `taurus.qt.formatters`
- Expected API: a formatter accepted by :meth:`taurus.qt.qtgui.TaurusBaseComponent.setFormat`
- Entry point name convention: A short descriptive string of the formatter. It
  may be used by the UI when offering the user to select formatters.
- Loading pattern: installation
- Enabling pattern: Explicit (e.g. via a selection dialog when calling
  :meth:`taurus.qt.qtgui.TaurusBaseWidget.onSetFormatter`)
- Examples: `taurus` self-registers several formatters (see `setup.py`)

Model Chooser Selectors
-----------------------------------

- Description: Adding widgets to be used by :class:`taurus.qt.qtgui.panel.TaurusModelSelector`
  for supporting models from other schemes
- Group: `taurus.model_selector.items`
- Expected API: :class:`taurus.qt.qtgui.panel.TaurusModelSelectorItem`
- Entry point name convention: the name should be a short description of the
  scheme or type of models supported by this item (e.g. `TangoArchiving = ...`).
  It is used as a tab title in :class:`taurus.qt.qtgui.panel.TaurusModelSelector`
- Loading pattern: Extension
- Enabling pattern: installation (but it may be changed in the future to a
  explicit or self-enabled pattern)
- Examples: taurus_tangoarchiving_ registers
  :class:`taurus_tangoarchiving.widget.tangoarchivingmodelchooser:TangoArchivingModelSelectorItem`
  as a model selector item

Plot widget Alternatives
-----------------------------------

- Description: alternative implementations of TaurusPlot.
- Group: `taurus.plot.alts`
- Expected API: *to be formally defined with an Abstract Base Class*. For now,
  informally, the API is defined by what is used in
  meth:`taurus.cli.alt.plot_cmd`:  at minimum, a :class:`QWidget` that has a
  `setModel` that accepts a sequence of attribute names.
- Entry point name convention: a short descriptive identifier of the
  implementation (e.g. `"qwt5"`, `"tpg"`, ...). The name is used in the UI for
  user selection of the implementation.
- Loading pattern: Extension
- Enabling pattern: explicit
- Examples: taurus_pyqtgraph_ registers :class:`taurus_tauruspyqtgraph.TaurusPlot`
  as a plot alternative

Trend widget Alternatives
-----------------------------------

- Description: alternative implementations of TaurusTrend
- Group: `taurus.trend.alts`
- Expected API:*to be formally defined with an Abstract Base Class*. For now,
  informally, the API is defined by what is used in
  meth:`taurus.cli.alt.trend_cmd`:  at minimum, a :class:`QWidget` that has a
  `setModel` that accepts a sequence of attribute names.
- Entry point name convention: a short descriptive identifier of the
  implementation (e.g. `"qwt5"`, `"tpg"`, ...). The name is used in the UI for
  user selection of the implementation.
- Loading pattern: Extension
- Enabling pattern: explicit
- Examples: taurus_pyqtgraph_ registers :class:`taurus_tauruspyqtgraph.TaurusTrend`
  as a trend alternative

Image widget Alternatives
-----------------------------------

- Description: alternative implementations of TaurusImage
- Group: `taurus.image.alts`
- Expected API: *to be formally defined with an Abstract Base Class*. For now,
  informally, the API is defined by what is used in
  meth:`taurus.cli.alt.image_cmd`:  at minimum, a :class:`QWidget` that has a
  `setModel` that accepts a sequence of attribute names. At this moment, the
  widget creator needs to accept the `wintitle` keyword argument (it may change
  when the API is formalized)
- Entry point name convention: a short descriptive identifier of the
  implementation (e.g. `"qwt5"`, `"tpg"`, ...). The name is used in the UI for
  user selection of the implementation.
- Loading pattern: Extension
- Enabling pattern: explicit
- Examples: `taurus` self-registers its
  :class:`taurus.qt.qtgui.extra_guiqwt.TaurusImageDialog` as an image widget
  alternative (see `setup.py`)

Trend2D widget Alternatives
-----------------------------------

- Description: alternative implementations of TaurusTrend2D
- Group: `taurus.trend2d.alts`
- Expected API: *to be formally defined with an Abstract Base Class*. For now,
  informally, the API is defined by what is used in
  meth:`taurus.cli.alt.trend2d_cmd`:  at minimum, a :class:`QWidget` that has a
  `setModel` that accepts a sequence of attribute names. At this moment, the
  widget creator needs to accept the following keyword arguments: `stackMode`,
  `wintitle`, `buffersize`. (it may change when the API is formalized)
- Entry point name convention: a short descriptive identifier of the
  implementation (e.g. `"qwt5"`, `"tpg"`, ...). The name is used in the UI for
  user selection of the implementation.
- Loading pattern: Extension
- Enabling pattern: explicit
- Examples: `taurus` self-registers its
  :class:`taurus.qt.qtgui.extra_guiqwt.TaurusTrend2DDialog` as trend2d widget
  alternative (see `setup.py`)

Form Factories
-----------------------------------

- Description: factories for custom "taurus value" widgets to be used in taurus
  forms. See :meth:`taurus.qt.qtgui.panel.TaurusForm.setItemFactories`
- Group: `taurus.form.item_factories`
- Expected API: a factory function that accepts a model name as its first
  argument and which returns either a :class:`taurus.qt.qtgui.panel.TaurusValue`
  type object (or `None`)
- Entry point name convention:
- Loading pattern: extension
- Enabling pattern: installation, but allowing explicit (de)selection based
  on meth:`taurus.core.util.plugin.selectEntryPoints`.
- Examples: sardana_ registers
  :func:`sardana.taurus.qt.qtgui.extra_pool.formitemfactory.pool_item_factory`
  to provide custom widgets for sardana elements in taurus forms.

qtgui submodules
-----------------------------------

.. note:: This entry point is for internal use only (to be used for backwards
          compatibility when "outsourcing" submodules).

- Description: adding submodules to :mod:`taurus.qt.qtgui`.
- Group: `taurus.qt.qtgui`
- Expected API: python module (typically exposing :class:`QWidget` classes)
- Entry point name convention: the name must match the module name
- Loading pattern: Extension (for performance, we use a
  :class:`taurus.core.util.lazymodule.LazyModule` to delay the actual import
  of the module until one of its members is actually used).
- Enabling pattern: installation
- Examples: taurus_pyqtgraph_ registers itself to be exported as
  :mod:`taurus.qt.qtgui.tpg`


.. _TEP13: http://www.taurus-scada.org/tep?TEP13.md
.. _taurus_tangoarchiving: https://github.com/taurus-org/taurus_tangoarchiving
.. _taurus_pyqtgraph: https://github.com/taurus-org/taurus_pyqtgraph
.. _sardana: https://sardana-controls.org/
