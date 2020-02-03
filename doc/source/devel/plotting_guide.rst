.. _plotting-guide:

=====================
Taurus plotting guide
=====================

*TL;DR*: Use taurus_pyqtgraph_

In taurus, the following dependencies are used for its various plotting widgets:

- PyQwt5_: for the `TaurusPlot` and `TaurusTrend` implemented in :mod:`taurus.qt.qtgui.qwt5`
  (former :mod:`taurus.qt.qtgui.plot`). PyQwt5 is unmaintained, removed from debian10, and only works with py2+Qt4,
  so it needs to be replaced urgently. **DO NOT BASE ANY NEW DEVELOPMENT ON THIS**
- guiqwt_: for `TaurusImageDialog` and `TaurusTrend2DDialog` implemented in :mod:`taurus.qt.qtgui.extra_guiqwt`.
  It does not depend at all of PyQwt5, and supports py2, py3 and Qt4, Qt5 so replacing it is not urgent
  (but still it should be eventually replaced by pyqtgraph-based widgets)
- pyqtgraph_: for `TaurusPlot` and `TaurusTrend` implementions in :mod:`taurus.qt.qtgui.qtgui.tpg` provided by the
  taurus_pyqtgraph_ plugin. It supports py2, py3 and Qt4, Qt5 and is the intended replacement for all taurus plotting
  widgets (TEP17_).

Even if the TEP17_ is not yet accepted, in practice the taurus_pyqtgraph_ widgets are the best (in some cases the only)
option for new developments involving plotting.

A lot of `features are already implemented in taurus_pyqtgraph <https://github.com/taurus-org/taurus_pyqtgraph#features-implementation-checklist>`_
and some features are already better than in the PyQwt5 implementations.

Still, some features available in the old PyQwt5-based implementations of `TaurusPlot` and `TaurusTrend` are still
missing in the pyqtgraph-based implementations (any help with this is welcome). The main ones are:

- persistence of user changes related to models (but this is not needed for use cases where the models are set
  programmatically and not altered by the user)
- full support of tango archiving in TaurusTrend (but basic support already available with the taurus_tangoarchiving_ plugin)
- maturity (certainly these classes are less tested than the qwt5 ones!)


Tips for Getting started with taurus_pyqtgraph_
------------------------------------------------

1. install the plugin (the module will be installed as :mod:`taurus_pyqtgraph` **and** at the same time will be available as
   :mod:`taurus.qt.qtgui.tpg`)
2. The philosophy is that you should use `tpg` as an extension to regular pyqtgraph_ widgets. Therefore you should read
   `the official pyqtgraph docs <http://www.pyqtgraph.org/documentation>`_ , and also run the official demo with
   `python -m pyqtgraph.examples`
3. :mod:`taurus_pyqtgraph` also has `some examples <https://github.com/taurus-org/taurus_pyqtgraph/tree/master/taurus_pyqtgraph/examples>`_.
   Have a look at them. Also have a look at the `__main__` sections of the files in the :mod:`taurus_pyqtgraph` module
4. See `this tutorial <https://github.com/sardana-org/sardana-followup/blob/master/20180605-Prague/08-taurus_pyqtgraph/08-taurus_pyqtgraph.md>`_.



.. _PyQwt5: https://github.com/PyQwt/PyQwt5
.. _guiqwt: https://pythonhosted.org/guiqwt/
.. _pyqtgraph: http://www.pyqtgraph.org/
.. _taurus_pyqtgraph: https://github.com/taurus-org/taurus_pyqtgraph
.. _taurus_tangoarchiving: https://github.com/taurus-org/tangoarchiving-scheme
.. _TEP17: https://github.com/cpascual/taurus/blob/tep17/doc/source/tep/TEP17.md
