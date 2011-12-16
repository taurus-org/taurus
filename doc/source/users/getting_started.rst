
.. _getting_started:

===============
Getting started
===============

.. _installing:

Installing
----------

#. Download the latest version of sardana from http://pypi.python.org/pypi/sardana.
#. Extract the downloaded tar.gz into a temporary directory
#. type::
       
       python setup.py build
       python setup.py install
       
#. test the installation::
       
       python -c "import sardana; print sardana.Release.version"

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
    #. Download and install latest `taurus`_ from `Taurus downdoad page <http://pypi.python.org/pypi/taurus>`_
    #. Download and install latest sardana from `Sardana downdoad page <http://pypi.python.org/pypi/sardana>`_


Working from SVN
----------------

You can checkout sardana from SVN from the following location::

    svn co http://tango-cs.svn.sourceforge.net/svnroot/tango-cs/share/Sardana/trunk sardana

Afterward, if you decide to work directly from SVN code (without installing):

    1. add <sardana checkout dir>/src to PYTHONPATH

.. _numpy: http://numpy.scipy.org/
.. _PLY: http://www.dabeaz.com/ply/
.. _Python(x,y): http://code.google.com/p/pythonxy/

.. _Tango: http://www.tango-controls.org/
.. _PyTango: http://packages.python.org/PyTango/
.. _taurus: http://packages.python.org/taurus/
.. _QTango: http://www.tango-controls.org/download/index_html#qtango3
.. _taurus: http://packages.python.org/taurus/
.. _Qt: http://qt.nokia.com/products/
.. _PyQt: http://www.riverbankcomputing.co.uk/software/pyqt/
.. _PyQwt: http://pyqwt.sourceforge.net/
.. _IPython: http://ipython.scipy.org/
.. _ATK: http://www.tango-controls.org/Documents/gui/atk/tango-application-toolkit
.. _Qub: http://www.blissgarden.org/projects/qub/
.. _ESRF: http://www.esrf.eu/
