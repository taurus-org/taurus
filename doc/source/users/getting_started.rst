
.. _getting_started:

===============
Getting started
===============

.. _installing:

Installing
----------

Linux
~~~~~

#. Download the latest version of taurus from http://pypi.python.org/pypi/taurus
#. Extract the downloaded tar.gz into a temporary directory
#. type::
       
       python setup.py build
       python setup.py install
#. test the installation::
       
       python -c "import taurus; print taurus.Release.version"
    
Windows
~~~~~~~

#. Download the latest windows binary from http://pypi.python.org/pypi/taurus
#. Run the installation excecutable
#. test the installation::
       
       C:\Python26\python -c "import taurus; print taurus.Release.version"

Windows installation shortcut
#############################

This chapter provides a quick shortcut to all windows packages which are
necessary to run taurus on your windows machine

#. from `Python(x,y)`_
    #. Download and install a python 2.6/2.7 compatible version of python(x,y)
       from `here <http://code.google.com/p/pythonxy>`_

#. from scratch:
    #. Download and install `PyQwt`_ < 6.0 from `PyQwt downdoad page <http://pyqwt.sourceforge.net/download.html>`_
        #. Download and install compatible python with from link in the same `PyQwt`_ page
        #. Download and install compatible `numpy`_ from link in the same `PyQwt`_ page.
        #. Download and install compatible `PyQt`_ from link in the same `PyQwt`_ page.

#. Finally:
    #. Download and install latest `PLY`_ from `PLY downdoad page <http://www.dabeaz.com/ply>`_ (necessary for jdraw synoptics only)
    #. Download and install latest `PyTango`_ from `PyTango downdoad page <http://pypi.python.org/pypi/PyTango>`_
    #. Download and install latest taurus from `Taurus downdoad page <http://pypi.python.org/pypi/taurus>`_

Working from SVN
----------------

You can checkout taurus from SVN from the following location::

    svn co http://tango-cs.svn.sourceforge.net/svnroot/tango-cs/gui/taurus/trunk taurus

Afterward, if you decide to work directly from SVN code (without installing):

    1. add <taurus checkout dir>/lib to PYTHONPATH
    2. build the resources once::
    
        python setup.py build_resources

.. _dependencies:

Dependencies
------------

.. graphviz::

    digraph dependencies {
        size="8,3";
        Taurus      [shape=box,label="taurus 2.0"];
        PyTango     [shape=box,label="PyTango 7.1.0"];
        Python      [shape=box,label="Python >=2.6"];
        numpy       [shape=box,label="numpy >=1.1.0"];
        PyQt        [shape=box,label="PyQt >=4.4.3"];
        PyQwt       [shape=box,label="PyQwt >=5.2.0"];
        Qub         [shape=box,label="Qub >=1.1.0"];
        qtcontrols  [shape=box,label="qtcontrols >=1.1.0"];
        PyMca       [shape=box,label="PyMca >=4.4.1"];
        ply         [shape=box,label="PLY"];
        
        Taurus -> Python;
        Taurus -> PyTango;
        Taurus -> PyQt         [label="taurus.qt only"];
        Taurus -> PyQwt        [label="taurus.qt only"];
        Taurus -> Qub          [style=dotted, label="taurus.qt.qtgui.image only"];
        Taurus -> qtcontrols   [style=dotted, label="taurus.qt.qtgui.gauge only"];
        Taurus -> PyMca        [style=dotted, label="taurus.qt.qtgui.extra_nexus only"];
        Taurus -> ply          [style=dotted, label="taurus.qt.qtgui.graphic.jdraw only"];
        Taurus -> numpy;
    } 

Taurus has dependencies on some python libraries. After you installed taurus you
can check the state of the dependencies by doing::

    >>> import taurus
    >>> taurus.check_dependencies()
    Checking required dependencies of taurus.core...
        Checking for Python >=2.6.0... [OK] (Found 2.6.2)
        Checking for PyTango >=7.1.0... [OK] (Found 7.1.0)
    Checking required dependencies of taurus.qt...
        Checking for PyQt >=4.4.3... [OK] (Found 4.5.0)
        Checking for PyQwt >=5.2.0... [OK] (Found 5.2.1)
    Checking OPTIONAL dependencies of taurus.qt...
        Checking for Qub >=1.0.0... [OK] (Found 1.0.0)
        Checking for qtcontrols >=1.0.0... [OK] (Found 1.0.0)
    
- You may already have PyTango_ installed. You will need PyTango 7 or later.
  You can check by doing::

      python -c 'import PyTango; print PyTango.Release.version'

  If that fails or it reports and older version follow the `PyTango installation steps`_
  to properly install PyTango.

- You may already have PyQt_ installed. You will need PyQt 4.4 or later.
  You can check by doing::

      python -c 'import PyQt4.Qt; print PyQt4.Qt.QT_VERSION_STR'

Optional packages
~~~~~~~~~~~~~~~~~

- The plotting widgets are only available if you have PyQwt_.
  You may already have PyQwt_ installed. You will need PyQwt 5.2.0 or later.
  You can check it by doing::

      python -c 'import PyQt4.Qwt5; print PyQt4.Qwt5.QWT_VERSION_STR'

- The image widgets are only available if you have Qub_. Qub_ is a graphical
  library provided by the BLISS group in ESRF_.
  You may already have Qub_ installed. You will need Qub for qt4.
  You can check it by doing::

      python -c 'import Qub'
    
- The Gauge widgets are only available if you have the python extension of
  qtcontrols. qtcontrols is part of QTango_.

- The JDraw synoptics widgets are only available if you have the :mod:`ply` 
  package installed.


.. _numpy: http://numpy.scipy.org/
.. _PLY: http://www.dabeaz.com/ply/
.. _Python(x,y): http://code.google.com/p/pythonxy/
.. _Tango: http://www.tango-controls.org/
.. _PyTango: http://packages.python.org/PyTango/
.. _`PyTango installation steps`: http://packages.python.org/PyTango/start.html#getting-started
.. _QTango: http://www.tango-controls.org/download/index_html#qtango3
.. _Qt: http://qt.nokia.com/products/
.. _PyQt: http://www.riverbankcomputing.co.uk/software/pyqt/
.. _PyQwt: http://pyqwt.sourceforge.net/
.. _IPython: http://ipython.scipy.org/
.. _Qub: http://www.blissgarden.org/projects/qub/
.. _ESRF: http://www.esrf.eu/
