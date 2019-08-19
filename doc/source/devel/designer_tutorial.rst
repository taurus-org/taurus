.. _taurusqtdesigner-tutorial:

============================
Taurus Qt Designer tutorial
============================

Taurus widgets behave just as any other Qt widget, and as such, they can be used
to create GUIs in a regular way, both programmatically or using the Qt designer.
For convenience, Taurus provides the `taurus designer` command that launches the
standard Qt designer application extended to show also the widgets provided by
Taurus.

To launch it, just execute::
  
  taurus designer

.. tip::

  ``--help`` argument will give you the complete list of options


.. figure:: /_static/designer01.png
  :scale: 75

You can then design your application/widget using not only the standard Qt
widgets but also the taurus widgets.

You can use the Taurus Qt Designer to define a full GUI, but instead
we recommend to create the GUIs using the
:ref:`TaurusGUI framework <taurusgui_newgui>` and use the
Taurus Qt Designer just for creating widgets to be inserted as panels in a
:class:`taurus.qt.qtgui.taurusgui.TaurusGui`-based GUI.



Using the .ui file
-------------------

The Qt designer will produce a .ui file that is an XML representation of the
application/widget that you designed.

This .ui file can then be used in your own widget by using the
:func:`taurus.qt.qtgui.util.UILoadable` decorator.

See `TEP11 <http://sf.net/p/sardana/wiki/SEP11/>`_ for more details.