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


Taurus is Free Software developed in open way. Contributions to code,
documentation, etc. are always welcome.

The "official" Taurus source code is hosted in a `git repository
<http://sf.net/p/tauruslib/taurus.git>`_.

The details in how to contribute are described in the TEP7_ document.


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

- Code in Taurus should follow the standard Python style conventions as
  described in PEP8_. Specially:

  - Use 4 spaces for indentation
  - Respect the maximum of 79 characters per line
  - Surround top-level function and class definitions with two blank lines.
  - use ``lower_case`` for module names. If possible prefix module names with the
    word ``taurus`` (like :file:`taurusutil.py`) to avoid import mistakes.
  - use ``CamelCase`` for class names
  - use ``lower_case`` for method names, except in the context of taurus.qt
    where the prevailing convention is ``mixedCase`` due to influence from PyQt

- Code must be python 2.7 compatible, and, if possible, new contributions
  should also consider being compatible with python3.5 (to prepare for
  python3 support)
- Every python module file should contain license information (see template below).
  The preferred license is the LGPL_. If you need/want to use a different one,
  it should be compatible with the LGPL v3+.
- avoid polluting namespace by making private definitions private (``__`` prefix)
  or/and implementing ``__all__`` (see template below)
- whenever a python module can be executed from the command line, it should
  contain a ``main`` function and a call to it in a ``if __name__ == "__main__"``
  like statement (see template below)
- All public API code should be documented (modules, classes and public API) using
  Sphinx_ extension to reStructuredText_

The following code can serve as a template for writing new python modules to
taurus::

    #!/usr/bin/env python

    #############################################################################
    ##
    # This file is part of Taurus
    ##
    # http://taurus-scada.org
    ##
    # Copyright 2011 CELLS / ALBA Synchrotron, Bellaterra, Spain
    ##
    # Taurus is free software: you can redistribute it and/or modify
    # it under the terms of the GNU Lesser General Public License as published by
    # the Free Software Foundation, either version 3 of the License, or
    # (at your option) any later version.
    ##
    # Taurus is distributed in the hope that it will be useful,
    # but WITHOUT ANY WARRANTY; without even the implied warranty of
    # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    # GNU Lesser General Public License for more details.
    ##
    # You should have received a copy of the GNU Lesser General Public License
    # along with Taurus.  If not, see <http://www.gnu.org/licenses/>.
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
PyQt4, PyQt5 and PySide versions.

1. Avoid importing PyQt / PySide directly. Imports like::
   
        from PyQt4 import Qt
        from PyQt4 import QtCore
        from PyQt4 import QtGui
        from PyQt4 import QtNetwork
        from PyQt4 import QtWebKit
        from PyQt4 import Qwt5
   
   Should be replaced by::
   
       from taurus.external.qt import Qt
       from taurus.external.qt import QtCore
       from taurus.external.qt import QtGui
       from taurus.external.qt import QtNetwork
       from taurus.external.qt import QtWebKit
       from taurus.external.qt import Qwt5

2. Since Taurus v>=4.0, Qt-based code in Taurus may assume
   that `PyQt API v2`_ is used. PyQt API 1 code, which was supported by Taurus 3,
   is no longer guaranteed to work.

   - Use standard python strings (e.g., use :class:`str` for Qt strings instead of
     :class:`QString`). Code like::

         my_string = Qt.QString(" hello ")
         my_string2 = my_string.trimmed()

     Should be replaced by::

         my_string = " hello "
         my_string2 = my_string.strip()


   - Do not use :class:`QVariant`. QVariant objects don't exist in
     PySide or in the new PyQt4 API 2. Code like::

          def setData(self, index, qvalue, role=Qt.Qt.EditRole):
              value = qvalue.toString()  # this assumes qvalue to be a :class:`QVariant`
              self.buffer[index.column()] = value

          def data(self, index, role=Qt.Qt.DisplayRole):
              value = self.buffer[index.column()]

              if role == Qt.Qt.DisplayRole:
                  return Qt.QVariant(value)
              else:
                  return Qt.QVariant()

     Should be replaced by::

          def setData(self, index, value, role=Qt.Qt.EditRole):
              self.buffer[index.column()] = value  # value is already a python object

          def data(self, index, role=Qt.Qt.DisplayRole):
              value = self.buffer[index.column()]

              if role == Qt.Qt.DisplayRole:
                  return value
              else:
                  return None

     For compatibility reasons, :func:`~taurus.external.qt.Qt` defines `QVariant` and
     `from_qvariant` which is internally used used to write code that supports both
     API v1 and v2 for QVariant. But new code in Taurus v>=4 may assume v2 only.

3. Use `new-style signals`_.
   Old-style code like the following::

       class MyWidget(Qt.QWidget):

       def foo(self):
           self.connect(self, Qt.SIGNAL('mySignal(int)', self.bar))
           self.emit(Qt.SIGNAL('mySignal(int)', 123))

   Should be replaced by::

       class MyWidget(Qt.QWidget):

           mySignal = Qt.pyqtSignal(int)

           def foo(self):
               self.mySignal.connect(self.bar)
               self.mySignal.emit(123)

4. Use of :class:`taurus.qt.qtgui.application.TaurusApplication` instead of
   :class:`QApplication` is recommended (it takes care of various
   initialization and exit tasks that are convenient).

.. _reStructuredText:  http://docutils.sourceforge.net/rst.html
.. _Sphinx: http://www.sphinx-doc.org
.. _TEP7: http://sf.net/p/tauruslib/wiki/TEP7/
.. _PEP8: http://www.python.org/peps/pep-0008.html
.. _LGPL: http://www.gnu.org/licenses/lgpl.html
.. _`PyQt API v2`: http://pyqt.sourceforge.net/Docs/PyQt4/incompatible_apis.html
.. _`new-style signals`: http://pyqt.sourceforge.net/Docs/PyQt4/new_style_signals_slots.html