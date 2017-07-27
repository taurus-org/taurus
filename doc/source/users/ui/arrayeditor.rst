.. currentmodule:: taurus.qt.qtgui.plot

.. _arrayeditor:

=============
Array Editor
=============

The :class:`ArrayEditor` is a widget for graphically editing a spectrum.

.. figure:: /_static/taurusarrayeditor01.png
  :align: center
  
It consists of two :ref:`plots <taurusplot_ui>` and a *control point area*. The plot
on top shows the current and modified spectrum. The other plot shows
the difference between the current and the modified spectrum. The Control point
area shows details on the control points that have been defined.

The spectrum can be modified by adding control points and moving them 
along the vertical axis, either by setting the value in the controls area or by
dragging them in the plots.

Control points are added by double-clicking in a position of the plot or by
using the `Add` button (which allows the user to define a regular grid of
control points).

The currently selected control point is highlighted both in the plots and in the
controls area.

The arrow buttons in the controls area will help in propagating the related
value to the other control points to  the left or to the right of the selected
one.
