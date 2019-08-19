.. currentmodule:: taurus.qt.qtgui.panel

.. _configurations:

=============================================
Taurus Configuration Browser User's Interface
=============================================

.. contents::

Taurus provides an user interface for browsing TaurusMainWindow setting 
files (.ini files), allowing a power user to visualize and edit the 
different perspectives of a Taurus GUI.
The configuration tree is organized in branches, with the perspective 
at the root.

Taurus Configuration Browser Application
----------------------------------------

You may browse the configuration of a TaurusMainWindow-based application
(e.g. any TaurusGUI) by launching the taurus config application
with the following command::

	taurus config [<configuration.ini>]

Run the following command for more details::

    taurus config --help

In the figure below the taurusconfigbrowser application shows a taurus
configuration .ini file containing three perspectives: 'LAST',
'second_perspective' and 'third_perspective'. 'LAST' is an special perspective
automatically stored just before the closing of the Taurus GUI; it reflects 
the state of the GUI just before the last closing. The other two perspectives
were saved explicitly during the Taurus GUI execution.

.. figure:: /_static/taurusconfigbrowser.png
  :align: center

  taurusconfigbrowser with a perspective unfolded to show the panel entries
