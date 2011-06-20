
.. _getting_started:

===============
Getting started
===============

.. _installing:

Installing
----------

#. Download the latest version of sardana from http://www.tango-controls.org/download.
#. Extract the downloaded tar.gz into a temporary directory
#. type::
       
       python setup.py build
       python setup.py install 
#. test the installation::
       
       python -c "import sardana; print sardana.Release.version"
       

Working from SVN
----------------

You can checkout taurus from SVN from the following location::

    svn co http://tango-cs.svn.sourceforge.net/svnroot/tango-cs/share/sardana/trunk sardana

Afterward, if you decide to work directly from SVN code (without installing):

    1. add <sardana checkout dir>/src to PYTHONPATH

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
