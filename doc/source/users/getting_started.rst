
.. _getting_started:

===============
Getting started
===============

.. _installing:

Installing
----------

Linux (Debian-based)
~~~~~~~~~~~~~~~~~~~~

Since v3.0, Taurus is part of the official repositories of Debian (and Ubuntu
and other Debian-based distros). You can install it and all its dependencies by
doing (as root)::

       aptitude install python-taurus
       
(see more detailed instructions in `this step-by-step howto
<https://sourceforge.net/p/sardana/wiki/Howto-SardanaFromScratch/>`__)


Linux (generic)
~~~~~~~~~~~~~~~

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

Working from Git
----------------

Sometimes it is convenient to work directly from the git source without
installing. Taurus code is hosted in a `subdirectory
<http://sourceforge.net/p/sardana/sardana.git/ci/master/tree/taurus/>`_ of the
`main Sardana git repository <http://sourceforge.net/p/sardana/sardana.git>`_

You can clone sardana from our main git repository::

    git clone git://git.code.sf.net/p/sardana/sardana.git sardana

and you will find the taurus code in the `sardana/taurus` directory.

Then, if you decide to work directly from Git code (without installing):

    1. add <sardana_root_dir>/taurus/lib to PYTHONPATH
    2. add <sardana_root_dir>/taurus/scripts to PATH
    3. build the resources::
    
        cd <sardana_root_dir>/taurus
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

- The image widgets are provided by the guiqwt_ library. The widgets based on
  this library replace the previously used Qub_-based image widget which is now
  considered deprecated in Taurus
    
- The Gauge widgets are only available if you have the python extension of
  qtcontrols. qtcontrols is part of QTango_.

- The JDraw synoptics widgets are only available if you have the :mod:`ply` 
  package installed.
  
- The NeXus browser widget is only available if you have PyMca_ installed


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
.. _guiqwt: http://code.google.com/p/guiqwt/
.. _IPython: http://ipython.scipy.org/
.. _Qub: http://www.blissgarden.org/projects/qub/
.. _PyMca: http://pymca.sourceforge.net/
