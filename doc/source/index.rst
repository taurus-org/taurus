
Welcome to Taurus's Home Page!
=============================================

    |image1| 

Taurus is a python framework for control and data acquisition CLIs and GUIs
in scientific/industrial environments.
It supports multiple control systems or data sources: Tango_, EPICS_, spec... 
New control system libraries can be integrated through plugins.

For non-programmers: Taurus allows the creation of fully-featured GUI (with 
forms, plots, synoptics, etc) from scratch in a few minutes using a "wizard",
which can also be customized and expanded by drag-and-dropping elements 
around at execution time.

For programmers: Taurus gives full control to more advanced users to create 
and customize CLIs and GUIs programmatically using Python and a very simple 
and economical API which abstracts data sources as "models".

Of course, Taurus is Free Software (under LGPL). You can download it from PyPi_,
access its Documentation_ or get support from its community and the latest code
from the `project page <https://github.com/taurus-org/taurus>`_.

Projects related to Taurus
---------------------------

- Taurus uses PyQt_ for the GUIs 
- Tango_ is supported vis PyTango_ 
- Taurus is part of the Sardana_ suite


.. |image1| image::  _static/taurus_showcase01.png
    :align: middle
    :height: 180

.. toctree::
    :hidden:

    Home Page <http://www.taurus-scada.org>
    Project Page <https://github.com/taurus-org/taurus>
    Download from PyPI <http://pypi.python.org/pypi/taurus>
    docs

:Last Update: |today|
:Release: |release|


.. image:: https://img.shields.io/pypi/pyversions/taurus.svg
    :target: https://pypi.python.org/pypi/taurus
    :alt: Python Versions
    
.. image:: https://img.shields.io/pypi/l/taurus.svg
    :target: https://pypi.python.org/pypi/taurus
    :alt: License
    
.. image:: https://img.shields.io/pypi/v/taurus.svg
    :target: https://pypi.python.org/pypi/taurus
    :alt: Latest Version

.. image:: https://badge.fury.io/gh/taurus-org%2Ftaurus.svg
    :target: https://github.com/taurus-org/taurus
    :alt: GitHub
    
.. image:: https://readthedocs.org/projects/taurus/badge/
    :target: http://taurus-scada.org/docs.html
    :alt: Documentation
    
.. image:: https://travis-ci.org/taurus-org/taurus.svg?branch=develop
    :target: https://travis-ci.org/taurus-org/taurus
    :alt: Travis

.. image:: https://ci.appveyor.com/api/projects/status/rxeo3hsycilnyn9k/branch/develop?svg=true
    :target: https://ci.appveyor.com/project/taurusorg/taurus/branch/develop
    :alt: Appveyor


.. _Tango: http://www.tango-controls.org/
.. _PyTango: http://packages.python.org/PyTango/
.. _EPICS: http://www.aps.anl.gov/epics/
.. _PyQt: http://www.riverbankcomputing.co.uk/software/pyqt/
.. _Sardana: http://sardana-controls.org
.. _LGPL: http://www.gnu.org/licenses/lgpl.html
.. _PyPi: http://pypi.python.org/pypi/taurus 
.. _Documentation: http://taurus-scada.org/docs.html

