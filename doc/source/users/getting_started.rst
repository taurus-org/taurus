
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


Note: pip is already included in python>2.7.9 (or python 3.4.0 for the 3.x series)

Installing from PyPI manually (platform-independent)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You may alternatively install from a downloaded release package:

#. Download the latest release of taurus from http://pypi.python.org/pypi/taurus
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

#. Download the latest windows binary from http://pypi.python.org/pypi/taurus
#. Run the installation executable
#. test the installation::

       C:\Python27\python -c "import taurus; print taurus.Release.version"

Windows installation shortcut
#############################

This chapter provides a quick shortcut to all windows packages which are
necessary to run taurus on your windows machine

#. from `Python(x,y)`_
    #. Download and install a python 2.7 compatible version of python(x,y)
       from `here <http://python-xy.github.io/>`_

#. from scratch:
    #. Download and install `PyQwt`_ < 6.0 from `PyQwt downdoad page <http://pyqwt.sourceforge.net/download.html>`_
        #. Download and install compatible python from link in the same `PyQwt`_ page
        #. Download and install compatible `numpy`_ from link in the same `PyQwt`_ page.
        #. Download and install compatible `PyQt`_ from link in the same `PyQwt`_ page.

#. Finally:
    #. Download and install latest `PLY`_ from `PLY downdoad page <http://www.dabeaz.com/ply>`_ (necessary for jdraw synoptics only)
    #. Download and install latest `PyTango`_ from `PyTango downdoad page <http://pypi.python.org/pypi/PyTango>`_
    #. Download and install latest Taurus from `Taurus downdoad page <http://pypi.python.org/pypi/taurus>`_

Working from Git source directly (in develop mode)
--------------------------------------------------

If you intend to do changes in Taurus itself, it is convenient to work 
directly from the git source in "develop" mode, so that you do not need 
to re-install on each change.

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
        PyTango     [shape=box,label="PyTango >=7.1.0"];
        pyepics     [shape=box,label="pyepics >=3.2.4"];
        PyQt        [shape=box,label="PyQt >=4.8"];
        PyQwt       [shape=box,label="PyQwt >=5.2.0"];
        guiqwt      [shape=box,label="guiqwt >=2.3.0"];
        PyMca5      [shape=box,label="PyMca5 >=5.1.2"];
        ply         [shape=box,label="PLY >=2.3"];

        Taurus -> Python;
        Taurus -> numpy;
        Taurus -> PyTango      [style=dotted, label="only for using Tango"];
        Taurus -> pyepics      [style=dotted, label="only for using EPICS"];
        Taurus -> PyQt         [label="taurus.qt only"];
        Taurus -> PyQwt        [label="taurus.qt only"];
        Taurus -> guiqwt       [style=dotted, label="taurus.qt.qtgui.extra_guiqwt only"];
        Taurus -> PyMca5       [style=dotted, label="taurus.qt.qtgui.extra_nexus only"];
        Taurus -> ply          [style=dotted, label="taurus.qt.qtgui.graphic.jdraw only"];
    }

Taurus has dependencies on some python libraries. After you installed taurus you
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
