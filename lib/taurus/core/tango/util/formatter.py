# -*- coding: utf-8 -*-

##############################################################################
##
# This file is part of Taurus, a Tango User Interface Library
##
# http://www.tango-controls.org/static/taurus/latest/doc/html/index.html
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
##############################################################################

__all__ = ["tangoFormatter"]

def tangoFormatter(dtype=None, basecomponent=None, **kwargs):
    """
    The tango formatter callable. Returns the string formatting base on
    the Tango Attribute configuration `format` (Display.Format in Tango DB)

    :param dtype: (object) data type
    :param basecomponent: widget
    :param kwargs: other keyword arguments

    :return: the string formatting
    """
    fmt = "{0}"
    if basecomponent is not None:
        # get the TangoAttribute Spec format
        spec_format = basecomponent.modelObj.format[1:]
        if dtype is Quantity:
            fmt = "{{:~{spec_format}}}".format(tformat=spec_format)
        else:
            fmt = "{{:{spec_format}}}".format(tformat=spec_format)

    return fmt