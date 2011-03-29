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
.. currentmodule:: taurus.core.evaluation

Evaluation extension for taurus core model.
The evaluation extension is a special extension that provides evaluation
objects. The official scheme name is 'evaluation', but it can be shortened to 'eval'.

The main usage for this extension is to provide a way of performing mathematical
evaluations with data from other sources.

Evaluation Factory uses the following object naming (which is **not** a strict URI!):

    `eval://<math_expression>[;evaluator=<evaluatorname>]`
    
    or:
    
    `eval://evaluator=<evaluatorname>`
  
    where:
    
    - The first form of the naming returns a :class:`EvaluationAttribute` and
      the second form returns a :class:`EvaluationDevice`
  
    - in the first form of the naming, the `evaluator=<evaluatorname>` is an
      optional segment which defaults to `evaluator=DefaultTaurusEvaluator` if
      not present.
      
    - `<math_expression>` is a mathematical expression (using python syntax)
      that may have references to other taurus objects by enclosing them between
      `{` and `}`. Expressions will be evaluated using :class:`SafeEvaluator`
      which includes a large subset of mathematical functions from the
      :mod:`numpy` module.
      
    - <evaluatorname> is a unique identification name for the evaluator object.
      This allows to use different evaluator objects which may have different
      symbols available for evaluation

Some examples of valid evaluation models are:

    - Multiplying a tango attribute by 2:
        
        `eval://2*{tango://a/b/c/d}`
        
    - Adding two tango attributes together (note we can omit the `tango://` part
      because tango is the default schema in taurus)
      
        `eval://{a/b/c/d}+{f/g/h/i}`
    
    - Generating an array of random values:
    
        `eval://rand(256)`
        
    - Adding noise to a tango image attribute:
    
        `eval://{sys/tg_test/1/short_image_ro}+10*rand(*shape({sys/tg_test/1/short_image_ro}))`
        
    - Using resources to calculate the voltage from the Intensity and the Resistance:
    
        `eval://{res://I}*{res://R}`
        
        or, quivalent, using the `${}` shortcut:
        
        `eval://${I}*${R}`
        
    - Referencing to an evaluator device named `foo`:
    
        `eval://evaluator=foo`
        
    - Referencing to an evaluator device named `foo` and assigning custom symbols to it:
    
        `eval://evaluator=foo?bar={tango://a/b/c/d};blah=23`
        
        
    - Multiplying a blah times bar (both `blah` and `bar` are known to evaluator `foo`):
        
        `eval://evaluator=foo;blah*bar`
        
    - Same as the previous 2, but all in one line:
    
        `eval://evaluator=foo;blah*bar?bar={tango://a/b/c/d};blah=23`

"""
#raise NotImplementedError()
from evalfactory import *