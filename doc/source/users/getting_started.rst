
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

       python -c "import taurus; print taurus.Release.version"

Note: pip is already included in python>2.7.9

Note: some "extra" features of taurus have additional dependencies_.

Installing from sources manually (platform-independent)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You may alternatively install from a downloaded release package:

#. Download the latest sources of taurus from http://pypi.python.org/pypi/taurus
#. Extract the downloaded source into a temporary directory and change to it
#. run::

       pip install .

#. test the installation::

       python -c "import taurus; print taurus.Release.version"

Note: some "extra" features of taurus have additional dependencies_.

Linux (Debian-based)
~~~~~~~~~~~~~~~~~~~~

Since v3.0, Taurus is part of the official repositories of Debian (and Ubuntu
and other Debian-based distros). You can install it and all its dependencies by
doing (as root)::

       aptitude install python-taurus

(see more detailed instructions in `this step-by-step howto
<https://sourceforge.net/p/sardana/wiki/Howto-SardanaFromScratch/>`__)


Windows
~~~~~~~

#. Install the `Python(x,y)`_ bundle (alternatively, you could install Python,
   PyQt_, PLY_, and other dependencies_ independently, but `Python(x,y)`_
   will save you much worries about versions).
#. Download the latest Taurus windows binary from http://pypi.python.org/pypi/taurus
#. Run the installation executable
#. test the installation::

       C:\Python27\python -c "import taurus; print taurus.Release.version"


Working from Git source directly (in develop mode)
--------------------------------------------------

If you intend to do changes to Taurus itself, or want to try the latest
developments, it is convenient to work directly from the git source in
"develop" (aka "editable") mode, so that you do not need to re-install
on each change.

You can clone taurus from our main git repository::

    git clone https://github.com/taurus-org/taurus.git taurus

Then, to work in develop mode, just do::

    pip install -e ./taurus


.. _dependencies:

Dependencies
------------

Strictly speaking, Taurus only depends on numpy, but that will leave
out most of the features normally expected of Taurus (which are
considered "extras"). For example:

- Interacting with a Tango controls system requires PyTango_.

- Interacting with an Epics controls system requires pyepics_.

- Using the taurus Qt widgets, requires PyQt_ 4.x (4.8 <= v < 5).
  (PyQt5 support coming soon).

- The :mod:`taurus.qt.qtgui.plot` module requires PyQwt_.

- The image widgets require the guiqwt_ library.

- The JDraw synoptics widgets require the PLY_ package.

- The NeXus browser widget requires PyMca5_.

- The TaurusEditor widget requires spyder_.

- The TaurusGui module requires lxml_.


For a complete list of "extra" features and their corresponding
requirements, execute the following command::

    python -c 'import taurus; taurus.check_dependencies()'


How you install the required dependencies depends on your preferred
installation method:

- For GNU/Linux, it is in general better to install the dependencies from
  your distribution repositories if available.

- For Windows users: many of these dependencies are already satisfied
  by installing the `Python(x,y)`_ bundle. Also, most can be installed
  from PyPI_ (e.g. using pip). For some versions, PyPI may not provide
  pre-built windows binaries, so pip may try to compile from sources,
  which takes long and may not succeed without some further work. In
  those cases, one may use windows binaries from other versions and/or
  wheel packages from the Silx_WheelHouse_.

- In general, you can use pip to install dependencies for a given
  extra feature (if they are in PyPI or in one of your configured
  indexes). Use::

      pip install taurus[NAME_OF_EXTRA]

- The Conda_ package management system may also be used to install
  most of the required dependencies.

- The `taurus-test Docker container`_ provides a Docker container (based
  on Debian) with all the dependencies pre-installed (including Tango and
  Epics running environments) on which you can install taurus straight
  away.


.. _numpy: http://numpy.org/
.. _PLY: http://www.dabeaz.com/ply/
.. _Python(x,y): http://python-xy.github.io/
.. _Tango: http://www.tango-controls.org/
.. _PyTango: http://pytango.readthedocs.io
.. _Qt: http://qt.nokia.com/products/
.. _PyQt: http://www.riverbankcomputing.co.uk/software/pyqt/
.. _PyQwt: http://pyqwt.sourceforge.net/
.. _guiqwt: https://pypi.python.org/pypi/guiqtw
.. _IPython: http://ipython.org
.. _PyMca5: http://pymca.sourceforge.net/
.. _pyepics: http://pypi.python.org/pypi/pyepics
.. _spyder: http://pythonhosted.org/spyder
.. _lxml: http://lxml.de
.. _Silx_WheelHouse: http://www.silx.org/pub/wheelhouse/
.. _PyPI: http://pypi.python.org/pypi
.. _Conda: http://conda.io/docs/
.. _taurus-test Docker container: http://hub.docker.com/r/cpascual/taurus-test/
