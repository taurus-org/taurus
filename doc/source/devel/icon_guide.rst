.. _icon-guide:

==================
Taurus icon guide
==================

Usually the application/widget you are developing will require some icons.
Some of these icons will be used to represent a standard actions, applications,
places or status like "open a file", "desktop" or "preferences".
Each of these actions have already an associated icon that is supplied by the
operating system according to the active theme.

To aid you in the process of adding icons, taurus provides a small 
API (:mod:`taurus.qt.qtgui.resource`) which you can use to easly insert 
standard icons into your widgets.

For example, suppose you want to add a toolbox in your application's main window
where the first button triggers an "open file dialog". All you have to do is 
search for the icon name representing the action of your button in the 
:ref:`catalog <icon-catalog>` (in our case it should be **document-open**),
get the icon from taurus using :func:`taurus.qt.qtugui.resource.getThemeIcon`
and insert it into your widget. Here is an example code:

.. literalinclude:: icon_example.py

The list of available standard icon names is described in 
`Icon Naming Specification <http://standards.freedesktop.org/icon-naming-spec/icon-naming-spec-latest.html>`_ 

.. _icon-catalog:

Taurus icon catalog
-------------------

.. raw:: html
  :file: catalog.html