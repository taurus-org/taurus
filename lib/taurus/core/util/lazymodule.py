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
This module provides LazyModule for loading plugin modules in lazy way -
only when members of actual plugin are requested.
"""

__all__ = ["LazyModule"]

from types import ModuleType
import sys

from taurus import warning, info


class LazyModule(ModuleType):
    """It provides a ModuleType object that acts as a placeholder for modules
    registered via entry-points. It replaces the actual module without actually
    importing it until a member of the module is requested, which automatically
    triggers the load of the entry-point and the substitution of this
    placeholder by the actual module
    """
    def __init__(self, name, package, entry_point):
        """

        :param name: name of the module
        :param package: name of the package to which the module belongs
        :param entry_point: entry-point for the module
        """
        super(LazyModule, self).__init__(name)
        self.__package__ = package
        self.ep = entry_point

    def __getattr__(self, member):
        try:
            mod = self.ep.load()
            # Replace lazy module with actual module for package
            setattr(sys.modules[self.__package__], self.__name__, mod)
            # Replace lazy module with actual module in sys.modules
            modname = "%s.%s" % (self.__package__, self.__name__)
            sys.modules[modname] = mod
        except Exception as e:
            warning('Could not load plugin "%s". Reason: %s', self.ep.name, e)
            return None
        return getattr(mod, member)

    @staticmethod
    def import_ep(name, package, entry_point):
        """
        Lazily imports a module defined in an entry point. The LazyModule is
        inserted in sys.modules as <package>.<name>

        :param name: name of the module
        :param package: name of the package to which the module belongs
        :param entry_point: entry-point for a module
        :return: A LazyModule object
        """
        m = LazyModule(name, package, entry_point)
        setattr(sys.modules[package], name, m)
        modname = "{}.{}".format(package, name)
        sys.modules[modname] = m
        info(
            'Plugin "%s" lazy-loaded as "%s"',
            entry_point.module_name,
            modname
        )
        return m
