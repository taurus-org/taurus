.. currentmodule:: taurus.qt.qtgui.panel

.. _modelchooser:

===================================
TaurusModelChooser User's Interface
===================================

The  :class:`TaurusModelChooser` is a tree based widget used by Taurus applications for
prompting the user to choose one or more attribute/device names of the control system.

.. figure:: /_static/taurusmodelchooser01.png
  :align: center

To select the attributes using :class:`TaurusModelChooser`, you typically do the
following:

1. Browse the tree to locate the devices and/or attributes you are interested in.
2. Now select one or more device/attributes (tip: you can use the CTRL key for 
   multiple selection)
3. Add them to the `Chosen models` list (the bottom part of the widget) by using
   the `Add` button (the "+" icon).
4. Repeat previous steps if you want to add other models or use the
   `Remove` button (the "-" icon) to remove models from the
   `Chosen models` list.
5. Click the `Update Models` button to apply the changes when satisfied.
   
**Important**: The tree can be quite dense. You can
filter it by typing part of the device name in the `Filter` box (#4 in the
figure).