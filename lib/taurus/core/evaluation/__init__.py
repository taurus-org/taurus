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

"""
.. currentmodule:: taurus.core.evaluation

Evaluation extension for taurus core model.

The evaluation extension is a special extension that provides evaluation
objects. The official scheme name is 'eval'.

The main usage for this extension is to provide a way of performing mathematical
evaluations with data from other sources.

The Evaluation Factory (:class:`EvaluationFactory`) uses the following object
naming for referring to attributes (:class:`EvaluationAttribute`):

    `eval:[//<authority>][@<evaluator>/][<subst>;]<expr>`

or the following for referring to evaluation devices
(:class:`EvaluationDevice`):

    `eval:[//<authority>]@<evaluator>`

or the following for referring to an evaluation authority
(:class:`EvaluationAuthority`):

    `eval://<authority>`

where:

    - The `<authority>` segment is optional (except when referring to an
      EvaluationDatabase). At this point, only `//localhost` is supported.

    - The `@<evaluator>` is optional (except when referring to an
      EvaluationDevice). If not given, it defaults to `DefaultEvaluator`.

    - `<expr>` is a mathematical expression (using python syntax)
      that may have references to other taurus **attributes** by enclosing them
      between `{` and `}`. Expressions will be evaluated by the evaluator device
      to which the attribute is assigned.

    - The evaluator device inherits from :class:`SafeEvaluator` which by default
      includes a large subset of mathematical functions from the :mod:`numpy`
      module.

    - `<evaluator>` is a unique identification name for the evaluator device
      object. This allows to use different evaluator objects which may have
      different symbols available for evaluation. As an alternative approach, it
      is also possible to use custom-made evaluator devices as long as they
      inherit from :class:`EvaluationDevice`. To use a custom-made evaluator,
      you should construct the `<evaluator>` as `<modulename>.<classname>`
      where:

          - `<modulename>` is a python module name and

          - `<classname>` is the name of a class in `<modulename>` that derives
            from :class:`EvaluationDevice`

      See :file:`<taurus>/core/evaluation/dev_example.py` for an example of a
      custom Evaluator

    - The optional `<subst>` segment is used to provide substitution symbols.
      `<subst>` is a semicolon-separated string of `<key>=<value>` strings.


Some examples of valid evaluation models are:

    - An attribute that multiplies a tango attribute by 2:

        `eval:2*{tango:a/b/c/d}`

    - Same as above, but using substitutions:

        `eval:k=2;a={tango:a/b/c/d};k*a`

    - An attribute that adds two tango attributes together (assuming that tango
      is set as the default scheme)

        `eval:{a/b/c/d}+{f/g/h/i}`

    - An attribute that generates an array of random values:

        `eval:rand(256)`

    - An attribute that adds noise to a tango image attribute:

        `eval:img={tango:sys/tg_test/1/short_image_ro};img+10*rand(*img.shape)`

    - A default evaluator device named `foo`:

        `eval:@foo`

    - A custom evaluator device (implemented as class `MyEval` in the `mymod`
      module):

        `eval:@mymod.MyClass`


.. note:: Previous to SEP3, a RFC3986 non-compliant syntax was used for the
          evaluation scheme (e.g., allowing names such as
          ``tango://db=foo;dev=bar;a*b?k=2;a={tango:a/b/c/d}``).
          This syntax is now deprecated and should not be used. Taurus will
          issue warnings if detected.
"""

from evalfactory import EvaluationFactory
from evalattribute import EvaluationAttribute
from evalauthority import EvaluationAuthority
from evaldevice import EvaluationDevice
