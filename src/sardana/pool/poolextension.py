#!/usr/bin/env python

##############################################################################
##
## This file is part of Sardana
##
## http://www.sardana-controls.org/
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

"""This module is part of the Python Sardana libray. It defines the base
classes for sardana value translation"""

__all__ = ["CannotTranslateException",
           "register_controller_value_translator",
           "register_controller_state_translator",
           "ControllerValueTranslator", "ControllerStateTranslator"]

__docformat__ = 'restructuredtext'

from sardana.sardanavalue import SardanaValue

__CTRL_STATE_TRANSLATORS = {}
__CTRL_VALUE_TRANSLATORS = {}


class CannotTranslateException(Exception):

    def __init__(self, *args, **kwargs):
        super(CannotTranslateException, self).__init__(*args, **kwargs)


class BaseControllerTranslator(object):

    def translate(self, value):
        raise CannotTranslateException

    def __call__(self, value):
        return self.translate(value)


class ControllerValueTranslator(BaseControllerTranslator):
    pass


class ControllerStateTranslator(BaseControllerTranslator):
    pass


def register_controller_value_translator(klass, *args, **kwargs):
    if not issubclass(klass, ControllerValueTranslator):
        raise Exception("Cannot register controller value translator. " \
                        "Class must inherit from ControllerValueTranslator")
    __CTRL_VALUE_TRANSLATORS[klass] = klass(*args, **kwargs)


def register_controller_state_translator(klass, *args, **kwargs):
    if not issubclass(klass, ControllerStateTranslator):
        raise Exception("Cannot register controller value translator. " \
                        "Class must inherit from ControllerStateTranslator")
    __CTRL_STATE_TRANSLATORS[klass] = klass(*args, **kwargs)


def translate_ctrl_value(value):
    if isinstance(value, SardanaValue):
        return value

    for _, translator in __CTRL_VALUE_TRANSLATORS.items():
        try:
            return translator(value)
        except CannotTranslateException:
            continue

    # Fallback translator
    return SardanaValue(value=value)
