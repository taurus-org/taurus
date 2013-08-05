
.. _sardana-installing:

==========
Installing
==========

#. Install sardana:
    #. From easy_install [1]_ ::
        
            easy_install -U sardana

    #. From source code:

        #. Download the sardana source code:
            #. from latest stable version of `sardana <http://pypi.python.org/pypi/sardana>`_ (|version|)
            #. from `SVN snapshot <https://sourceforge.net/p/sardana/code/HEAD/tarball?path=/trunk>`_
            
        #. Extract the downloaded tar.gz into a temporary directory

        #. type [2]_ ::
               
               python setup.py build
               python setup.py install

#. test the installation::
       
       python -c "import sardana; print sardana.Release.version"

You can also work from SVN trunk checkout
(please look :ref:`here <sardana-working-from-svn>` for instructions).


Windows installation shortcut
-----------------------------

This chapter provides a quick shortcut to all windows packages which are
necessary to run sardana on your windows machine

#. Install all dependencies:

    #. from `Python(x,y)`_ (by far the easiest choise)
        #. Download and install a python 2.6/2.7 compatible version of python(x,y)
           from `here <http://code.google.com/p/pythonxy>`_

    #. from scratch:
        #. Download and install `PyQwt`_ < 6.0 from `PyQwt downdoad page <http://pyqwt.sourceforge.net/download.html>`_
            #. Download and install compatible python from link in the same `PyQwt`_ page
            #. Download and install compatible `numpy`_ from link in the same `PyQwt`_ page.
            #. Download and install compatible `PyQt`_ from link in the same `PyQwt`_ page.

#. Download and install latest `PyTango`_ from `PyTango downdoad page <http://pypi.python.org/pypi/PyTango>`_
#. Download and install latest `taurus`_ from `Taurus downdoad page <http://pypi.python.org/pypi/taurus>`_
#. Finally download and install latest sardana from `Sardana downdoad page <http://pypi.python.org/pypi/sardana>`_

.. _sardana-working-from-svn:

Working directly from Git
-------------------------

Sometimes it is convenient to work directly from the git source without installing. To do so,
you can clone sardana from our main git repository::

    git clone git://git.code.sf.net/p/sardana/sardana.git sardana
    
And then you can directly execute sardana binaries (Pool, MacroServer, Sardana or spock
from the command line)::

    homer@pc001:~/workspace$ cd sardana
    homer@pc001:~/workspace/sardana$ scripts/Sardana
    
.. tip:: If you plan to work normally from git without installing, you may want
         to add the `sardana/scripts` directory to your `PATH` variable and 
         `sardana/src` to your `PYTHONPATH` variable.


.. rubric:: Footnotes

.. [1] This command requires super user previledges on linux systems. If your
       user has them you can usually prefix the command with *sudo*:
       ``sudo easy_install -U sardana``. Alternatively, if you don't have
       administrator previledges, you can install locally in your user
       directory with: ``easy_install --user sardana``
       In this case the executables are located at <HOME_DIR>/.local/bin. Make
       sure the PATH is pointing there or you execute from there.

.. [2] *setup.py install* requires user previledges on linux systems. If your
       user has them you can usually prefix the command with *sudo*: 
       ``sudo python setup.py install``. Alternatively, if you don't have
       administrator previledges, you can install locally in your user directory
       with: ``python setup.py install --user``
       In this case the executables are located at <HOME_DIR>/.local/bin. Make
       sure the PATH is pointing there or you execute from there.

.. _numpy: http://numpy.scipy.org/
.. _PLY: http://www.dabeaz.com/ply/
.. _Python(x,y): http://code.google.com/p/pythonxy/
.. _Python: http://www.python.org/

.. _SardanaPypi: http://pypi.python.org/pypi/sardana/
.. _Tango: http://www.tango-controls.org/
.. _PyTango: http://packages.python.org/PyTango/
.. _taurus: http://packages.python.org/taurus/
.. _QTango: http://www.tango-controls.org/download/index_html#qtango3
.. _taurus: http://packages.python.org/taurus/
.. _Qt: http://qt.nokia.com/products/
.. _PyQt: http://www.riverbankcomputing.co.uk/software/pyqt/
.. _PyQwt: http://pyqwt.sourceforge.net/
.. _IPython: http://ipython.org/
.. _ATK: http://www.tango-controls.org/Documents/gui/atk/tango-application-toolkit
.. _Qub: http://www.blissgarden.org/projects/qub/
.. _ESRF: http://www.esrf.eu/

