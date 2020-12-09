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

"""[DEPRECATED] Rope patch for better performance.
Based on spyder.rope_patch"""

__all__ = ["apply"]

__docformat__ = 'restructuredtext'


from taurus.core.util.log import deprecated
deprecated(dep='taurusropepatch module', rel='4.0.1')


def apply():
    """Monkey patching rope for better performances"""
    import rope
    if rope.VERSION not in ('0.9.3', '0.9.2'):
        raise ImportError("rope %s can't be patched" % rope.VERSION)

    # Patching pycore.PyCore, so that forced builtin modules (i.e. modules
    # that were declared as 'extension_modules' in rope preferences)
    # will be indeed recognized as builtins by rope, as expected
    from rope.base import pycore

    class PatchedPyCore(pycore.PyCore):

        def get_module(self, name, folder=None):
            """Returns a `PyObject` if the module was found."""
            # check if this is a builtin module
            pymod = self._builtin_module(name)
            if pymod is not None:
                return pymod
            module = self.find_module(name, folder)
            if module is None:
                raise pycore.ModuleNotFoundError(
                    'Module %s not found' % name)
            return self.resource_to_pyobject(module)
    pycore.PyCore = PatchedPyCore

    # Patching BuiltinFunction for the calltip/doc functions to be
    # able to retrieve the function signatures with forced builtins
    from rope.base import builtins, pyobjects
    from spyder.utils.dochelpers import getargs


    class PatchedBuiltinFunction(builtins.BuiltinFunction):

        def __init__(self, returned=None, function=None, builtin=None,
                     argnames=[], parent=None):
            builtins._BuiltinElement.__init__(self, builtin, parent)
            pyobjects.AbstractFunction.__init__(self)
            self.argnames = argnames
            if not argnames and builtin:
                self.argnames = getargs(self.builtin)
            if self.argnames is None:
                self.argnames = []
            self.returned = returned
            self.function = function
    builtins.BuiltinFunction = PatchedBuiltinFunction

    # Patching BuiltinName for the go to definition feature to simply work
    # with forced builtins
    from rope.base import libutils
    import inspect

    class PatchedBuiltinName(builtins.BuiltinName):

        def _pycore(self):
            p = self.pyobject
            while p.parent is not None:
                p = p.parent
            if isinstance(p, builtins.BuiltinModule) and p.pycore is not None:
                return p.pycore

        def get_definition_location(self):
            if not inspect.isbuiltin(self.pyobject):
                _lines, lineno = inspect.getsourcelines(self.pyobject.builtin)
                path = inspect.getfile(self.pyobject.builtin)
                pycore = self._pycore()
                if pycore and pycore.project:
                    resource = libutils.path_to_resource(pycore.project, path)
                    module = pyobjects.PyModule(pycore, None, resource)
                    return (module, lineno)
            return (None, None)
    builtins.BuiltinName = PatchedBuiltinName
