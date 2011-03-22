
.. _getting_started:

===============
Getting started
===============

.. _installing:

Installing
----------

#. Download the latest version of taurus from http://www.tango-controls.org/download.
#. Extract the downloaded tar.gz into a temporary directory
#. type::
       
       python setup.py build
       python setup.py install 
#. test the installation::
       
       python -c "import taurus; print taurus.Release.version"
       

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
        
        Taurus -> Python;
        Taurus -> PyTango;
        Taurus -> PyQt         [label="taurus.qt only"];
        Taurus -> PyQwt        [label="taurus.qt only"];
        Taurus -> Qub          [style=dotted, label="taurus.qt.qtgui.image only"];
        Taurus -> qtcontrols   [style=dotted, label="taurus.qt.qtgui.gauge only"];
        Taurus -> PyMca        [style=dotted, label="taurus.qt.qtgui.extra_nexus only"];
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

- The image widgets are only available if you have Qub_. Qub is a graphical library
  provided by the BLISS group in ESRF_.
  You may already have Qub_ installed. You will need Qub for qt4.
  You can check it by doing::

      python -c 'import Qub'
    
- The Gauge widgets are only available if you have the python extension of
  qtcontrols. qtcontrols is part of QTango_.

- The JDraw synoptics widgets are only available if you have the :mod:`ply` 
  package installed.

.. _qtdesigner_config:

Qt Designer configuration
-------------------------

Taurus ships with a designer startup script called **taurusdesigner** that 
configures the qt designer environment for taurus and starts it up.

If you absolutely need to use the existing designer binary directly, you will 
need to do some configuration in order to be able to access taurus widgets with
the Qt Designer. You need to specify the directory that the designer python 
plugin should search for taurus qt widgets.
The following chapters describe how to configure the designer in the different
platforms.

Linux
~~~~~

assuming taurus is installed in :file:`/usr/lib/python2.6/dist-packages` you
should add to/create the :envvar:`PYQTDESIGNERPATH` environment variable::

    export PYQTDESIGNERPATH=/usr/lib/python2.6/dist-packages/taurus/qt/qtdesigner:$PYQTDESIGNERPATH

Troubleshooting:
    If you start the Qt Designer and you don't see any taurus widgets on the
    widgets panel, make sure you have the PyQt_ designer plugin for python
    installed. You can check this by going to 
    :menuselection:`Help --> About plugins`. You should see a window with 
    :ref:`qtdesigner-plugins`. Check that an item called
    :file:`libpythonplugin.so` exists. If not, check that PyQt_ is properly
    installed.
    
    .. _qtdesigner-plugins:
    
    .. figure:: /_static/designer_plugins01.png
        :align: center
        
        Available designer plugins

Windows
~~~~~~~

assuming taurus is installed in :file:`C:\\Python2.6\\dist-packages` you should 
add a :envvar:`PYQTDESIGNERPATH` environment variable 
(:menuselection:`Start --> Control Panel --> System --> Advanced panel --> Environment variables`)
with the value :file:`C:\\Python2.6\\dist-packages\\taurus\\qt\\qtdesigner`

.. _Tango: http://www.tango-controls.org/
.. _PyTango: http://packages.python.org/PyTango/
.. _QTango: http://www.tango-controls.org/download/index_html#qtango3
.. _`PyTango installation steps`: http://packages.python.org/PyTango/start.html#getting-started
.. _Qt: http://qt.nokia.com/products/
.. _PyQt: http://www.riverbankcomputing.co.uk/software/pyqt/
.. _PyQwt: http://pyqwt.sourceforge.net/
.. _IPython: http://ipython.scipy.org/
.. _ATK: http://www.tango-controls.org/Documents/gui/atk/tango-application-toolkit
.. _Qub: http://www.blissgarden.org/projects/qub/
.. _ESRF: http://www.esrf.eu/
