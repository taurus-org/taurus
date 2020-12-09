.. currentmodule:: taurus.qt.qtgui.extra_guiqwt

.. _taurusimage:


==================
Image's interface
==================

.. contents::

The :class:`TaurusImageDialog` widget is a Taurus Widget for displaying
**image** attributes from the control system. A contour plot 
is created from the values of the image attribute.

.. figure:: /_static/taurusimage01.png
  :align: center
  
  A TaurusImage widget displaying the `sys/tg_test/1/long_image_ro` attribute
 
Many tools may be available, such as:

- zooming and panning
- X/Y cross sections
- Annotation tools (for creating labels, shapes,...)
- add/delete images 
- ...

.. note:: The :class:`TaurusImageDialog` widget is provided by  
          the :mod:`taurus.qt.qtgui.extra_guiqwt` module which depends on 
          the :mod:`guiqwt` module being installed. If guiqwt is not installed, 
          the image widget will not be available.

.. _standalonetaurusimage:

TaurusImageDialog as a stand-alone application
----------------------------------------------

You may also use TaurusImageDialog as a stand-alone application for showing image
attributes from the control system. You can launch the stand-alone Taurus Image
with the following command::

    taurus guiqwt image [options] <model>

Run the following command for more details::

    taurus guiqwt image --help