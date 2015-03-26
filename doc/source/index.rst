
Welcome to Taurus's Home Page!
=============================================

    |image1| |image2| |image3|



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
from the `project page <http://sourceforge.net/projects/sardana>`_.

Projects related to Taurus
---------------------------

- Taurus uses PyQt_ for the GUIs (Pyside_ support planned)
- Tango_ is supported vis PyTango_ 
- Taurus is part of the Sardana_ suite


.. |image1| image::  _static/taurusform_example02.png
    :align: middle
    :height: 180

.. |image2| image::  _static/taurusplot03.png
    :align: middle
    :height: 180

.. |image3| image::  _static/taurus_tree01.png
    :align: middle
    :height: 180


.. toctree::
    :hidden:

    Home Page <http://taurus-scada.org>
    Project Page <http://sourceforge.net/projects/sardana>
    Download from PyPI <http://pypi.python.org/pypi/taurus>
    docs

:Last Update: |today|


.. _Tango: http://www.tango-controls.org/
.. _PyTango: http://packages.python.org/PyTango/
.. _EPICS: http://www.aps.anl.gov/epics/
.. _PyQt: http://www.riverbankcomputing.co.uk/software/pyqt/
.. _Sardana: http://sardana-controls.org
.. _PySide: http://pyside.org
.. _LGPL: http://www.gnu.org/licenses/lgpl.html
.. _PyPi: http://pypi.python.org/pypi/taurus 
.. _Documentation: http://taurus.readthedocs.org

