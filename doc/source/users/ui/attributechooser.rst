.. currentmodule:: tau.qt.qtgui.panel

.. _attributechooser:

=================================
AttributeChooser User's Interface
=================================

.. note:: The AttributeChooser widget has been superseded by the TaurusModelChooser
          widget. See  :ref:`TaurusModelChooser User's Interface Guide <modelchooser>`

The  :class:`TaurusAttributeChooser` is a widget used by Taurus applications for
prompting the user to choose one or more attributes of the control system.

.. figure:: /_static/attributechooser01.png
  :align: center

To select the attributes using :class:`TaurusAttributeChooser`, you typically do the
following:

1. Select a device from those available in the `Devices` list (#1 in the figure)
2. Now select one or more attributes of this device from the `Attributes` list
   (#2 in the figure).
3. Add them to the `Chosen Attributes` list (#3 in the figure) by either using
   the `Add` button (the down arrow icon) or by double-clicking in their names in list #2.
4. Repeat previous steps if you want to add other attributes or use the
   `Remove` button (the up-arrow icon) to remove attributes from the chosen
   `Chosen Attributes` list.
5. Click the `Apply` button to apply the changes when satisfied.
   
**Important**: The list of devices (#1 of the figure) can be quite long. You can
filter it by typing part of the device name in the `Enter path` box (#4 in the
figure).
