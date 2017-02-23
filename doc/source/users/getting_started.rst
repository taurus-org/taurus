
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

Installing from sources manually (platform-independent)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You may alternatively install from a downloaded release package:

#. Download the latest sources of taurus from http://pypi.python.org/pypi/taurus
#. Extract the downloaded source into a temporary directory and change to it
#. run::

       python setup.py install

#. test the installation::

       python -c "import taurus; print taurus.Release.version"

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
"develop" mode, so that you do not need to re-install on each change.

You can clone taurus from our main git repository::

    git clone https://github.com/taurus-org/taurus.git taurus

Then, to work on develop mode, just do::

    cd taurus
    python setup.py develop

.. _dependencies:

Dependencies
------------

.. graphviz::

    digraph dependencies {
        size="8,3";
        Taurus      [shape=box,label="taurus 4.0"];
        Python      [shape=box,label="Python >=2.7"];
        numpy       [shape=box,label="numpy >=1.1.0"];
        lxml        [shape=box,label="lxml >=2.1"];
        PyTango     [shape=box,label="PyTango >=7.1.0"];
        pyepics     [shape=box,label="pyepics >=3.2.4"];
        PyQt        [shape=box,label="PyQt >=4.8"];
        PyQwt       [shape=box,label="PyQwt >=5.2.0"];
        guiqwt      [shape=box,label="guiqwt >=2.3.0"];
        PyMca5      [shape=box,label="PyMca5 >=5.1.2"];
        ply         [shape=box,label="PLY >=2.3"];

        Taurus -> Python;
        Taurus -> numpy;
        Taurus -> lxml;
        Taurus -> PyTango      [style=dotted, label="only for using Tango"];
        Taurus -> pyepics      [style=dotted, label="only for using EPICS"];
        Taurus -> PyQt         [style=dotted, label="taurus.qt only"];
        Taurus -> PyQwt        [style=dotted, label="taurus.qt only"];
        Taurus -> guiqwt       [style=dotted, label="taurus.qt.qtgui.extra_guiqwt only"];
        Taurus -> PyMca5       [style=dotted, label="taurus.qt.qtgui.extra_nexus only"];
        Taurus -> ply          [style=dotted, label="taurus.qt.qtgui.graphic.jdraw only"];
    }

Taurus has dependencies on some python libraries. After you install taurus you
can check the state of the dependencies by doing::

    import taurus
    taurus.check_dependencies()
    
- If you want to interact with a Tango controls system, you need PyTango_ 7 or later
  installed. You can check by doing::

    python -c 'import PyTango; print PyTango.Release.version'
    
- If you want to interact with an EPICS controls system,you need pyepics_

- For using the taurus Qt widgets, you will need PyQt_ 4.8 or later 
  (PyQt5 support comming soon). You can check by doing::

    python -c 'import PyQt4.Qt; print PyQt4.Qt.QT_VERSION_STR'

- The :mod:`taurus.qt.qtgui.plot` module requires PyQwt_ 5.2.0 or later.
  (this dependency will be dropped soon). You can check it by doing::

      python -c 'import PyQt4.Qwt5; print PyQt4.Qwt5.QWT_VERSION_STR'

- The image widgets require the guiqwt_ library.

- The JDraw synoptics widgets require the PLY_ package.

- The NeXus browser widget requires PyMca5_.


.. note:: For Windows users: many of these dependencies are already satisfied
          by installing the `Python(x,y)`_ bundle. Also, most can be installed
          from PyPI_ (e.g. using pip). For some versions, PyPI may not provide
          pre-built windows binaries, so pip may try to compile from sources,
          which takes long and may not succeed without some further work. In
          those cases, one may use windows binaries from other versions and/or
          wheel packages from the Silx_WheelHouse_.


.. _numpy: http://numpy.org/
.. _PLY: http://www.dabeaz.com/ply/
.. _Python(x,y): http://python-xy.github.io/
.. _Tango: http://www.tango-controls.org/
.. _PyTango: http://packages.python.org/PyTango/
.. _Qt: http://qt.nokia.com/products/
.. _PyQt: http://www.riverbankcomputing.co.uk/software/pyqt/
.. _PyQwt: http://pyqwt.sourceforge.net/
.. _guiqwt: https://pypi.python.org/pypi/guiqtw
.. _IPython: http://ipython.or/g
.. _PyMca5: http://pymca.sourceforge.net/
.. _pyepics: http://pypi.python.org/pypi/pyepics
.. _Silx_WheelHouse: http://www.silx.org/pub/wheelhouse/
.. _PyPI: https://pypi.python.org/pypi
