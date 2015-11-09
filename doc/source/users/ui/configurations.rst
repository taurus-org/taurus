.. currentmodule:: taurus.qt.qtgui.panel

.. _configurations:

=============================================
Taurus Configuration Browser User's Interface
=============================================

.. contents::

Taurus provides a user interface that allows to browse, visualize and
delete some branch of the different perspectives of a Taurus GUI.
The panels and instruments are organized in branches inside the perspectives.
The file storing the perspective configuration information is a file with
the .ini extension and it can be opened thanks to the taurusconfigbrowser
application.


Taurus Configuration Browser Application
----------------------------------------

You may browse the configuration of a certain Taurus  GUI by launching
the taurusconfigbrowser application with the following command::

	taurusconfigbrowser <configuration.ini>

Run the following command for more details::

    taurusconfigbrowser --help

In the figure below the taurusconfigbrowser application shows a taurus
configuration .ini file containing three perspectives: 'LAST',
'second_perspective' and 'third_perspective'. 'LAST' is a perspective stored
just before the closure of the Taurus GUI; it reflects the state of the GUI
just before the last closure. The other two perspectives have been stored
intentionally during the Taurus GUI execution.

In the figure the 'second_perspective' is unfolded and the panels contained
in this perspective can be visualized.

.. figure:: /_static/taurusconfigbrowser.png
  :align: center
