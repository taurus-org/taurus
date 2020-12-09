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
evaluations with data from other source, as well as allowing fast interfacing
with sources of data not supported by specific schemes.

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
      EvaluationAuthority). At this point, only `//localhost` is supported.

    - The `@<evaluator>` is optional (except when referring to an
      EvaluationDevice). If not given, it defaults to `DefaultEvaluator`. See
      below for further details

    - `<expr>` is a mathematical expression (using python syntax)
      that may have references to other taurus **attributes** by enclosing them
      between `{` and `}`. Expressions will be evaluated by the evaluator device
      to which the attribute is assigned.

    - The optional `<subst>` segment is used to provide substitution symbols.
      `<subst>` is a semicolon-separated string of `<key>=<value>` strings.

The evaluator device inherits from :class:`SafeEvaluator` which by default
includes a large subset of mathematical functions from the :mod:`numpy`
module. If access to other symbols are required, a custom evaluator can
be used. `<evaluator>` is a unique identification name for the evaluator
device object and may define a source of additional symbols to be present
for the evaluation. The supported syntax for `@<evaluator>` is:

    - `@<ID>` (cannot contain dots or any of `/` `?` `#` `:` `=`). This
      indicates just an alternative name for the EvaluationDevice, It does not
      add any extra symbol to the evaluation context.

    - `@<modulename>.*` (<modulename> may include dots for submodules). It
      will make all symbols found in the given module available during the
      evaluation (i.e., it emulates doing `from <modulename> import *` in the
      evaluation context).

    - `@<modulename>.<customdeviceclass>`. Use your own custom EvaluationDevice
      based class. This allows to define custom symbols see
      :file:`<taurus>/core/evaluation/test/res/dev_example.py`, **but** note
      that this syntax is is now superseded by the "instance-based" one
      (see below), which is easier to use and provides write attribute support.

    - `@<inst>=<modulename>.<class>()` (e.g. `@c=mymod.MyClass()` ). This
      will import a class from a module, then instantiate it and then
      make the instance available for evaluation with the given name. Note that
      the `<inst>=` part may be omitted, in which case the instance will be
      available for evaluation as `self`. **IMPORTANT:** If the given class
      declares writable properties, EvaluationAttributes that access one such
      property will automatically be considered writable. See examples of usage
      in :file:`<taurus>/core/evaluation/test/res/mymod.py` and in
      :file:`<taurus>/core/evaluation/test/res/ipap_example.py`


Some examples of valid evaluation models are:

    - An attribute that multiplies a tango attribute by 2::

        eval:2*{tango:a/b/c/d}

    - Same as above, but using substitutions::

        eval:k=2;a={tango:a/b/c/d};k*a

    - An attribute that adds two tango attributes together (assuming that tango
      is set as the default scheme)::

        eval:{a/b/c/d}+{f/g/h/i}

    - An attribute that generates an array of random values::

        eval:rand(256)

    - Same as above, but with units::

        eval:Q(rand(256),'V')

    - An attribute that adds noise to a tango image attribute::

        eval:img={tango:sys/tg_test/1/short_image_ro};img+10*rand(*img.shape)

    - An attribute that accesses a method from a given module (in this
      case to use os.path.exists)::

        eval:@os.*/path.exists("/some/file")

    - Same as before, for getting today's date as an attribute::

        eval:@datetime.*/date.today().isoformat()

    - A default evaluator device named `foo`::

        eval:@foo

    - A custom evaluator device (implemented as class `MyEvalDev` in the `mymod`
      module)::

        eval:@mymod.MyEvalDev

    - A custom evaluator device (implemented as class `MyEvalDev` in the `mymod`
      module)::

        eval:@mymod.MyEvalDev

    - A writable attribute foo (implemented as a writable property of the
      `MyClass` class from the `mymod` module)::

        eval:@c=mymod.MyClass()/c.foo

      assuming that the `mymod` module defines `MyClass` as::

        class MyClass(object):
            (...)
            get_foo(self):
                (...)
            set_foo(self, value):
                (...)
            foo = property(get_foo, set_foo)
            (...)


.. note:: Previous to SEP3, a RFC3986 non-compliant syntax was used for the
          evaluation scheme (e.g., allowing names such as
          ``eval://db=foo;dev=bar;a*b?k=2;a={tango:a/b/c/d}``).
          This syntax is now deprecated and should not be used. Taurus will
          issue warnings if detected.
"""
from __future__ import absolute_import

from .evalfactory import EvaluationFactory
from .evalattribute import EvaluationAttribute
from .evalauthority import EvaluationAuthority
from .evaldevice import EvaluationDevice
