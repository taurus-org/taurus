.. _coding-guide:

==============================
Taurus development guidelines
==============================

Overview
---------

This document describes taurus from the perspective of developers. Most 
importantly, it gives information for people who want to contribute to the 
development of taurus. So if you want to help out, read on!

How to contribute to taurus
----------------------------

Taurus is part of Tango_ and, more specifically, part of Sardana_. Until release
3.1 (included) the development of Taurus was managed within the `tango-cs
sourceforge project <https://sourceforge.net/projects/tango-cs/>`_  and its
source code was hosted in the Tango SVN repository. Starting from right after
the Taurus 3.1 release, the source code hosting and general project management
(tickets, mailing list, etc) is managed within the Sardana `Sardana
sourceforge project <https://sourceforge.net/projects/sardana/>`_.

The Taurus source code is now hosted in a `subdirectory
<http://sourceforge.net/p/sardana/sardana.git/ci/master/tree/taurus/>`_ of the
`main Sardana git repository <http://sourceforge.net/p/sardana/sardana.git>`_. 

See `instructions from Sardana about cloning and forking the sardana git
repository <http://www.sardana-controls.org/devel/guide_coding.html>`_.


Documentation
-------------

All standalone documentation should be written in plain text (``.rst``) files
using reStructuredText_ for markup and formatting. All such
documentation should be placed in directory :file:`docs/source` of the taurus
source tree. The documentation in this location will serve as the main source
for taurus documentation and all existing documentation should be converted
to this format.

Coding conventions
------------------

* In general, we try to follow the standard Python style conventions as
  described in
  `Style Guide for Python Code  <http://www.python.org/peps/pep-0008.html>`_
* Code **must** be python 2.6 compatible
* Use 4 spaces for indentation
* In the same file, different classes should be separated by 2 lines
* use ``lowercase`` for module names. If possible prefix module names with the
  word ``taurus`` (like :file:`taurusutil.py`) to avoid import mistakes.
* use ``CamelCase`` for class names
* python module first line should be::

    #!/usr/bin/env python
* python module should contain license information (see template below)
* avoid poluting namespace by making private definitions private (``__`` prefix)
  or/and implementing ``__all__`` (see template below)
* whenever a python module can be executed from the command line, it should 
  contain a ``main`` function and a call to it in a ``if __name__ == "__main__"``
  like statement (see template below)
* document all code using Sphinx_ extension to reStructuredText_

The following code can serve as a template for writting new python modules to
taurus::

    #!/usr/bin/env python

    #############################################################################
    ##
    ## This file is part of Taurus, a Tango User Interface Library
    ## 
    ## http://www.tango-controls.org/static/taurus/latest/doc/html/index.html
    ##
    ## Copyright 2011 CELLS / ALBA Synchrotron, Bellaterra, Spain
    ## 
    ## Taurus is free software: you can redistribute it and/or modify
    ## it under the terms of the GNU Lesser General Public License as published by
    ## the Free Software Foundation, either version 3 of the License, or
    ## (at your option) any later version.
    ## 
    ## Taurus is distributed in the hope that it will be useful,
    ## but WITHOUT ANY WARRANTY; without even the implied warranty of
    ## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    ## GNU Lesser General Public License for more details.
    ## 
    ## You should have received a copy of the GNU Lesser General Public License
    ## along with Taurus.  If not, see <http://www.gnu.org/licenses/>.
    ##
    #############################################################################

    """A :mod:`taurus` module written for template purposes only"""

    __all__ = ["TaurusDemo"]
    
    __docformat__ = "restructuredtext"
    
    class TaurusDemo(object):
        """This class is written for template purposes only"""
        
    def main():
        print "TaurusDemo"
    
    if __name__ == "__main__":
        main()

Special notes about Qt programming
-----------------------------------

The following Qt guidelines are intended to ensure compatibility between all 
PyQt4/PySide versions.

1. Avoid importing PyQt4/PySide directly.
   Imports like::
   
       from PyQt4 import Qt
       from PyQt4 import QtCore
       from PyQt4 import QtGui
       from PyQt4 import QtNetwork
       from PyQt4 import QtWebKit
       from PyQt4 import Qwt5
   
   Should be replaced by::
   
       from taurus.qt import Qt
       from taurus.qt import QtCore
       from taurus.qt import QtGui
       from taurus.qt import QtNetwork
       from taurus.qt import QtWebKit
       from taurus.qt import Qwt5

2. Usage of :class:`~PyQt4.QString` is **discouraged**. You should always use
   :class:`str`. QString objects don't exist in PySide or in the new PyQt4
   API 2. Code like::
   
       my_string = Qt.QString(" hello ")
       my_string2 = my_string.trimmed()
       label.setText(my_string2)
       print label.text()
   
   Should be replaced by::
   
       my_string = " hello "
       my_string2 = my_string.strip()
       label.setText(my_string2)
       print str(label.text())         # never assume Qt objects return str.

   For compatibility reasons, QString and QStringList are always available
   (even when using PySide or PyQt4 with API >=2) from :mod:`taurus.qt.Qt`.
   Note that if you are using PySide or PyQt4 with API >=2 then QString is 
   actually :class:`str` and QStringList is actually :class:`list`!
   
3. Usage of :class:`~PyQt4.QVariant` is **discouraged**. QVariant objects
   don't exist in PySide or in the new PyQt4 API 2. Code like::
   
       def setData(self, index, qvalue, role=Qt.Qt.EditRole):
           value = qvalue.toString()
           self.buffer[index.column()] = value
       
       def data(self, index, role=Qt.Qt.DisplayRole):
           value = self.buffer[index.column()]
           
           if role == Qt.Qt.DisplayRole:
               return Qt.QVariant(value)
           else:
               return Qt.QVariant()

   Should be replaced by::
   
       def setData(self, index, qvalue, role=Qt.Qt.EditRole):
           value = Qt.from_qvariant(qvalue, str)
           self.buffer[index.column()] = value
       
       def data(self, index, role=Qt.Qt.DisplayRole):
           value = self.buffer[index.column()]
           
           if role == Qt.Qt.DisplayRole:
               return Qt.to_qvariant(value)
           else:
               return Qt.from_qvariant()

   For compatibility reasons, QVariant are always available
   (even when using PySide or PyQt4 with API >=2) from :mod:`taurus.qt.Qt`.
   Note that if you are using PySide or PyQt4 with API >=2 then QVariant(pyobj)
   if function that returns actually pyobj (exactly the same as
   :func:`~taurus.qt.Qt.from_qvariant`.)

.. _Tango: http://www.tango-controls.org/
.. _Sardana: http://www.sardana-controls.org/
.. _tango_cs: https://sourceforge.net/projects/tango-cs/
.. _reStructuredText:  http://docutils.sourceforge.net/rst.html
.. _Sphinx: http://sphinx.pocoo.org/
