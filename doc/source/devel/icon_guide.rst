.. _icon-guide:

==================
Taurus icon guide
==================

Usually the application/widget you are developing will require some icons.
Some of these icons will be used to represent a standard actions, applications,
places or status like "open a file", "desktop" or "preferences".

Qt (and therefore, Taurus) supports `theme icons`_ for many common cases.
You can access them via the standard :meth:`QIcon.fromTheme` method. Using theme icons will make
your application be more integrated with the rest of the system, but keep in mind
that different people will see the icons differently depending on their default
theme (so do not use a theme icon for something not related to its `specification`_
just because in *your* theme it happens to look as what you want)

Apart from the theme icons, Taurus provides some collections of icons (and you can
add more (see :mod:`taurus.qt.qtgui.icon`). The paths containing these collections
are automatically added to `QDir`'s search paths under various prefixes when you
import `taurus.qt.qtgui` (or any of its submodules).

The following example shows how to use theme and non-theme icons in your
application:

.. literalinclude:: icon_example.py


.. _icon-catalog:

Taurus icon catalog
-------------------

In order to explore the icon collections provided by Taurus, you can use the
`taurus icons` application, which will let you browse the icons.

.. figure:: /_static/taurusiconcatalog-01.png
  :align: center

By clicking on an icon of the catalog, you will obtain a larger view of the icon as well as
detailed information on how to access it from your application.

.. figure:: /_static/taurusiconcatalog-details01.png
  :align: center

.. _theme icons: https://specifications.freedesktop.org/icon-theme-spec/icon-theme-spec-latest.html
.. _specification: http://specifications.freedesktop.org/icon-naming-spec/icon-naming-spec-latest.html
