.. _sardana-coding-guide:

==============================
Sardana development guidelines
==============================

Overview
---------

This document describes sardana from the perspective of developers. Most 
importantly, it gives information for people who want to contribute code to the 
development of sardana. So if you want to help out, read on!

How to contribute to sardana
----------------------------

Sardana development is managed with the `Sardana sourceforge project
<https://sourceforge.net/projects/sardana/>`_. 

Apart from directly contributing code, you can contribute to sardana in many
ways, such as reporting bugs or proposing new features. In all cases you will
probably need a sourceforge account and you are strongly encouragedto subscribe to the
`sardana-devel and sardana-users mailing lists <https://sourceforge.net/p/sardana/mailman/>_`.

The rest of this document will focus on how to contribute code.

Cloning and forking sardana from Git
------------------------------------

You are welcome to clone the Sardana code from our main Git repository::

    git clone git://git.code.sf.net/p/sardana/sardana.git sardana

Code contributions (bug patches, new features) are welcome,
but the review process/workflow for accepting new code is yet to be discussed. For the
moment, use the sardana-devel mailing list for proposing patches.

Note that you can also `fork the git repository in sourceforge
<https://sourceforge.net/p/sardana/sardana.git/fork>`_ to get your own
sourceforge-hosted clone of the sardana repository to which you will have full
access. This will create a new git repository associated to your personal account in
sourceforge, so that your changes can be easily shared and eventually merged
into the official repository.
 
The old SVN code repository
---------------------------

After the release of Sardana 1.2 the Sardana code was migrated from its previous
host in a SVN server to its current Git repository

The old SVN repository is still `accessible for reference
<https://sourceforge.net/p/sardana/code/>`_, but writing has been disabled and
its contents are frozen as of 2013-07-31. For development, see the instructions
above on cloning from Git

Documentation
-------------

All standalone documentation should be written in plain text (``.rst``) files
using reStructuredText_ for markup and formatting. All such
documentation should be placed in directory :file:`docs/source` of the sardana
source tree. The documentation in this location will serve as the main source
for sardana documentation and all existing documentation should be converted
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
  word ``sardana`` (like :file:`sardanautil.py`) to avoid import mistakes.
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

The following code can serve as a template for writing new python modules to
sardana::

    #!/usr/bin/env python
    # -*- coding: utf-8 -*-

    ##############################################################################
    ##
    ## This file is part of Sardana
    ## 
    ## http://www.tango-controls.org/static/sardana/latest/doc/html/index.html
    ##
    ## Copyright 2011 CELLS / ALBA Synchrotron, Bellaterra, Spain
    ## 
    ## Sardana is free software: you can redistribute it and/or modify
    ## it under the terms of the GNU Lesser General Public License as published by
    ## the Free Software Foundation, either version 3 of the License, or
    ## (at your option) any later version.
    ## 
    ## Sardana is distributed in the hope that it will be useful,
    ## but WITHOUT ANY WARRANTY; without even the implied warranty of
    ## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    ## GNU Lesser General Public License for more details.
    ## 
    ## You should have received a copy of the GNU Lesser General Public License
    ## along with Sardana.  If not, see <http://www.gnu.org/licenses/>.
    ##
    ##############################################################################

    """A :mod:`sardana` module written for template purposes only"""

    __all__ = ["SardanaDemo"]
    
    __docformat__ = "restructuredtext"
    
    class SardanaDemo(object):
        """This class is written for template purposes only"""
        
    def main():
        print "SardanaDemo"s
    
    if __name__ == "__main__":
        main()


.. _Tango: http://www.tango-controls.org/
.. _tango_cs: https://sourceforge.net/projects/tango-cs/
.. _reStructuredText:  http://docutils.sourceforge.net/rst.html
.. _Sphinx: http://sphinx.pocoo.org/
