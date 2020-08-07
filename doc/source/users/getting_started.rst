
.. _getting_started:

===============
Getting started
===============

.. _installing:

Installing
----------

Installing with pip (platform-independent)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Taurus can be installed using pip. The following command will automatically
download and install the latest release of Taurus (see pip --help for options)::

       pip install taurus

You can test the installation by running::

       python -c "import taurus; print(taurus.Release.version)"


Note: some "extra" features of taurus have additional dependencies_.


Linux (Debian-based)
~~~~~~~~~~~~~~~~~~~~

Taurus is part of the official repositories of Debian (and Ubuntu
and other Debian-based distros). You can install it and all its dependencies by
doing (as root)::

       apt-get install python-taurus

Note: `python3-taurus` and `python3-taurus-pyqtgraph` packages are already
built in https://salsa.debian.org , but are not yet part of the official debian
repositories


Installing in a conda environment (platform-independent)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

First create a Conda_ environment with all the dependencies and activate it::

    conda config --add channels conda-forge
    conda config --add channels tango-controls
    # note: MacOSX users, remove "pytango" from the following command
    conda create -n py3qt5 python=3 pyqt=5 pytango lxml future guidata guiqwt ipython pillow pint ply pyqtgraph pythonqwt numpy scipy pymca click
    conda activate py3qt5

Then install taurus and taurus_pyqtgraph using pip (as explained above)

Working from Git source directly (in develop mode)
--------------------------------------------------

If you intend to do changes to Taurus itself, or want to try the latest
developments, it is convenient to work directly from the git source in
"develop" (aka "editable") mode, so that you do not need to re-install
on each change::

    # install taurus in develop mode
    git clone https://github.com/taurus-org/taurus.git
    pip install -e ./taurus  # <-- Note the -e !!

    # install taurus_pyqtgraph in develop mode
    git clone https://github.com/taurus-org/taurus_pyqtgraph.git
    pip install -e ./taurus_pyqtgraph  # <-- Note the -e !!


.. _dependencies:

Dependencies
------------

Strictly speaking, Taurus only depends on numpy_, click_, pint_ and future_
but that will leave out most of the features normally
expected of Taurus (which are considered "extras"). For example:

- Interacting with a Tango controls system requires PyTango_.

- Interacting with an Epics controls system requires pyepics_.

- Using the taurus Qt_ widgets, requires either PyQt_ (v4 or v5)
  or PySide_ (v1 or v2). Note that most development and testing of
  is done with PyQt, so many features may not be
  regularly tested with PySide and PySide2.

- The :mod:`taurus.qt.qtgui.qwt5` module requires PyQwt_, which is
  only available when using PyQt4 and python2. As an alternative
  that supports both python2 and python3 and all the Qt bindings,
  refer to the taurus_pyqtgraph_ plugin.

- The image widgets require the guiqwt_ library.

- The JDraw synoptics widgets require the PLY_ package.

- The NeXus browser widget requires PyMca5_.

- The TaurusEditor widget requires spyder_.

- The TaurusGui module requires lxml_.


For a complete list of "extra" features and their corresponding
requirements, execute the following command::

    taurus check-deps


How you install the required dependencies depends on your preferred
installation method:

- For GNU/Linux, it is in general better to install the dependencies from
  your distribution repositories if available. A Conda_ environment can be
  used alternatively (interesting for testing new features in isolation)

- For Windows users, the recommended option is to use a Conda_ environment
  (see above).

- The `taurus-test Docker container`_ provides a Docker container (based
  on Debian) with all the dependencies pre-installed (including Tango and
  Epics running environments) on which you can install taurus straight
  away.


.. _numpy: http://numpy.org/
.. _pint: http://pint.readthedocs.org/
.. _future: https://python-future.org/
.. _PLY: http://www.dabeaz.com/ply/
.. _Tango: http://www.tango-controls.org/
.. _PyTango: http://pytango.readthedocs.io
.. _Qt: http://qt.nokia.com/products/
.. _PyQt: http://www.riverbankcomputing.co.uk/software/pyqt/
.. _PySide: https://wiki.qt.io/Qt_for_Python
.. _PyQwt: http://pyqwt.sourceforge.net/
.. _taurus_pyqtgraph: https://github.com/taurus-org/taurus_pyqtgraph
.. _guiqwt: https://pypi.org/project/guiqwt/
.. _IPython: http://ipython.org
.. _PyMca5: http://pymca.sourceforge.net/
.. _pyepics: https://pypi.org/project/pyepics/
.. _spyder: http://pythonhosted.org/spyder
.. _lxml: http://lxml.de
.. _Conda: http://conda.io/docs/
.. _click: https://pypi.org/project/click/
.. _taurus-test Docker container: http://hub.docker.com/r/cpascual/taurus-test/
