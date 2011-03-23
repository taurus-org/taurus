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

"""
.. currentmodule:: taurus.core.operation

Operation extension for taurus core model.
The operation extension is a special extension that provides operation
objects. The official scheme name is 'op'.

The main usage for this extension is to provide a way of performing mathematical
operations with data from other sources.

Operation Factory uses the following object naming (**not** a strict URI!):

    op://math_expression
  
    where `math_expression` is a mathematical expression (using python syntax)
    that may have references to other taurus objects by enclosing them between
    `{` and `}`. Expressions will be evaluated using :class:`SafeEvaluator`
    which includes a large subset of mathematical functions from the
    :mod:`numpy` module.

Some examples of valid operation models are:

    - Multiplying a tango attribute by 2:
        
        `op://2*{tango://a/b/c/d}`
        
    - Adding two tango attributes together (note we can omit the `tango://` part
      because tango is the default schema in taurus)
      
        `op://{a/b/c/d}+{f/g/h/i}`
    
    - Generating an array of random values:
    
        `op://rand(256)`
        
    - Adding noise to a tango image attribute:
    
        `op://{sys/tg_test/1/short_image_ro}+10*rand(*shape({sys/tg_test/1/short_image_ro}))`
      

"""
raise NotImplementedError()
from opfactory import *