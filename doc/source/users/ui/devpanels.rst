.. currentmodule:: taurus.qt.qtgui.panel

======================================
Taurus Device Panels User's Interface
======================================

There are two different widgets that can be used to provide a view on a Taurus
Device: :class:`TaurusDevicePanel` and :class:`TaurusDevPanel`.
The first is a compact widget that gives access to attributes and commands
of a given device. The second is a full main window application that
provides the same access plus a device selector and a trend widget in a more
configurable (but less compact way).

.. _taurusdevicepanel:

TaurusDevicePanel as a stand-alone application
----------------------------------------------

The :class:`TaurusDevicePanel` can be launched as a stand-alone application with
the following command::

    taurus dev [options] [<device_name>]

Run the following command for more details::

    taurus dev --help

.. _tauruspanel:

TaurusPanel as a stand-alone application
----------------------------------------

The :class:`TaurusDevPanel` can be launched as a stand-alone application with
the following command::

    taurus panel [options] [<device_name>]

Run the following command for more details::

    taurus panel --help


