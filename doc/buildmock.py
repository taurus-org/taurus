#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
###########################################################################

# ----------------------------------------------------------------------------
# This class also borrows much code from the build_mock_qt.py script from
# qarbon (http://qarbon.rtfd.org/)
#
# Copyright (c) 2013 European Synchrotron Radiation Facility, Grenoble, France
#
# ----------------------------------------------------------------------------

''' Creates a tree of dirs and restructured text stub files for documenting
the API of a python module with sphinx'''

from __future__ import with_statement

import os
import sys
import glob
import re
import inspect
import shutil

# Define templates

module_init_template = """\
from __future__ import print_function

{imports}

class _MockMeta(type):
    def __getattr__(self, name):
        return _Mock()

class _Mock(object):
    __metaclass__ = _MockMeta
    def __init__(self, *a, **kw):
        object.__init__(self)
        for k,v in kw.iteritems():
            setattr(self, k, v)
    def __getattr__(*a, **kw): return _Mock()
    def __call__(*a, **kw): return _Mock()
    def __getitem__(*a, **kw): return _Mock()
    def __int__(*a, **kw): return 1
    def __contains__(*a, **kw): return False
    def __len__(*a, **kw): return 1
    def __iter__(*a, **kw): return iter([])
    def __exit__(*a, **kw): return False
    def __complex__(*a, **kw): return 1j
    def __float__(*a, **kw): return 1.0
    def __bool__(*a, **kw): return True
    def __nonzero__(*a, **kw): return True
    def __oct__(*a, **kw): return 1
    def __hex__(*a, **kw): return 0x1
    def __long__(*a, **kw): return long(1)
    def __index__(*a, **kw): return 1
"""

import_template = """import {name} as {asname}"""
mock_template = """{name} = _Mock()"""

klass_template = """\
class {klass}({super_klass}):
  pass
{members}"""

function_template = """def {function}(*a,**k): return _Mock()"""
member_template = """  {name} = {value!r}"""
constant_template = """{name} = {value!r}"""
specialfloats_template = """{name} = float('{value!r}')"""


def abspath(*path):
    """A method to determine absolute path for a given relative path to the
    directory where this .py script is located"""
    this_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.abspath(os.path.join(this_dir, *path))


def _import(name):
    __import__(name)
    return sys.modules[name]


def _is_pseudo_enum(obj):
    if not isinstance(obj, int):
        return False
    try:
        int(repr(obj))
        return False
    except:
        return True


def _is_special_float(obj):
    if not isinstance(obj, float):
        return False
    return repr(obj) in ('inf', 'nan', '-inf')


def _discard_element(name, exclude, include):
    if name in include:
        return False
    return name in exclude or name.startswith("__")


def build_class(k_name, k, exclude=(), include=()):
    '''return the source text for a mock class based on a given class'''
    methods = []
    members = []

    for element_name in dir(k):
        if _discard_element(element_name, exclude, include):
            continue
        try:
            element = getattr(k, element_name)
        except AttributeError:
            continue
        if _is_special_float(element):
            members.append(specialfloats_template.format(name=element_name,
                                                         value=element))
        elif isinstance(element, (int, float, bool, str, unicode)):
            try:  # make sure that the repr makes sense
                type(element)(repr(element))
            except:  # skip it (the _Mock.__getattr__ will deal with it)
                continue
            members.append(member_template.format(name=element_name,
                                                  value=element))
    members = "\n".join(members)

    klass_str = klass_template.format(klass=k_name,
                                      super_klass='_Mock',
                                      members=members)
    return klass_str


def build_module(module_name, imports=(), out_prefix='mock',
                 exclude=(), include=()):
    '''generate a mock package for a given module'''
    rel_dir = module_name.split(".")
    abs_dir = abspath(out_prefix, *rel_dir)
    if os.path.isdir(abs_dir):
        return
    os.makedirs(abs_dir)
    module = _import(module_name)
    fake_module_filename = os.path.join(abs_dir, "__init__.py")

    klasses = []
    constants = []
    mocks = []
    imports = set([import_template.format(name=m, asname=m) for m in imports])
    for element_name in sorted(dir(module)):
        if _discard_element(element_name, exclude, include):
            continue
        element = getattr(module, element_name)
        # internal imports (from the same package)
        if (inspect.ismodule(element) and
                element.__name__.split('.')[0] == module_name.split('.')[0]):
            # add the module to the imports set #@TODO: this does not work
            # imports.add(import_template.format(name=element.__name__,
            #                                    asname=element_name))
            # @todo: The above lines were commented because they created
            # problems with circular imports. So for now we just mock them
            mocks.append(mock_template.format(name=element_name))
            # make sure that the module is built
            build_module(element.__name__, imports=(),
                         out_prefix=out_prefix, exclude=exclude,
                         include=include)
        # classes
        elif inspect.isclass(element):
            klasses.append(build_class(element_name, element,
                                       exclude=exclude, include=include))
        # inf, and NaN constants
        elif _is_special_float(element):
            constants.append(specialfloats_template.format(name=element_name,
                                                           value=element))
        # enumerations-like objects
        elif (_is_pseudo_enum(element)):
            constants.append(mock_template.format(name=element_name))
        # constants
        elif isinstance(element, (int, float, bool, str, unicode)):
            try:  # make sure that the repr makes sense
                type(element)(repr(element))
            except:  # cannot write anything better than a mock
                constants.append(mock_template.format(name=element_name))
            constants.append(constant_template.format(name=element_name,
                                                      value=element))
        # final catch-all: it covers modules, functions and other elements
        # that aren't caught by any of the above
        elif (element_name not in imports):
            mocks.append(mock_template.format(name=element_name))

    imports = "\n".join(sorted(imports))

    module_init = module_init_template.format(imports=imports)
    mocks = "\n\n".join(mocks)
    constants = "\n\n".join(constants)
    klasses = "\n\n".join(klasses)
    with open(fake_module_filename, "w") as f:
        f.write(module_init)
        f.write("\n\n")
        f.write(mocks)
        f.write("\n\n")
        f.write(constants)
        f.write("\n\n")
        f.write(klasses)
        f.write("\n\n")


def guess_submodules_from_package(module_name, exclude=(), include=()):
    '''returns a list of submodule names found in a given package name.
    If module_name is not implemented as a package, it returns an empty list'''
    if module_name in exclude:
        return []
    module = _import(module_name)
    try:
        modulefile = inspect.getfile(module)
    except TypeError:
        return []
    if not (modulefile.endswith('__init__.py') or
            modulefile.endswith('__init__.pyc')):
        return []

    pkgdir, _ = os.path.split(modulefile)
    # explore pkgdir to find subdirs with __init__.py files
    g = glob.glob(os.path.join(pkgdir, '*', '__init__.py'))
    names = [re.findall(r".+\/(.*)\/__init__.py", s)[0] for s in g]
    # explore pkgdir to find .py files
    g = glob.glob(os.path.join(pkgdir, '*.py'))
    names += [re.findall(r".+\/(.*).py", s)[0] for s in g]
    # explore pkgdir to find .pyc files
    g = glob.glob(os.path.join(pkgdir, '*.pyc'))
    names += [re.findall(r".+\/(.*).pyc", s)[0] for s in g]
    # explore pkgdir to find .so files
    g = glob.glob(os.path.join(pkgdir, '*.so'))
    names += [re.findall(r".+\/(.*).so", s)[0] for s in g]
    # build list with full module names and filter out non-importable
    # submodules
    full_module_names = []
    for sm_name in names:
        name = '.'.join((module_name, sm_name))
        # skip __main__ and __init__, etc and excluded (unless included)
        if (name not in include and
                (name in exclude or sm_name.startswith('__'))):
            continue
        # check if the module is indeed importable
        try:
            print name
            _import(name)
            full_module_names.append(name)
        except:
            print '!'
            pass
    return full_module_names


def build_full_module(module_name, exclude=(), include=(), out_prefix='mock'):
    '''build a full mocked package (modules and submodules, recursively) for the
    given module'''
    rel_dir = module_name.split(".")
    abs_dir = abspath(out_prefix, *rel_dir)
    if os.path.isdir(abs_dir):
        shutil.rmtree(abs_dir)

    build_module(module_name, imports=(), exclude=exclude, include=include,
                 out_prefix=out_prefix)

    # recursive call for submodules
    for name in guess_submodules_from_package(module_name, exclude=exclude):
        build_full_module(name, exclude=exclude, include=include,
                          out_prefix=out_prefix)


def _zipdir(basedir, archivename):
    '''function to zip directories. Adapted from:
    http://stackoverflow.com/questions/296499
    '''
    from zipfile import ZipFile, ZIP_DEFLATED
    from contextlib import closing
    assert os.path.isdir(basedir)
    with closing(ZipFile(archivename, "w", ZIP_DEFLATED)) as z:
        for root, dirs, files in os.walk(basedir):
            # NOTE: ignore empty directories
            for fn in files:
                absfn = os.path.join(root, fn)
                zfn = absfn[len(basedir) + len(os.sep):]  # XXX: relative path
                z.write(absfn, zfn)


def build_mocks_for_taurus(output='mock.zip'):
    '''builds mocks for the packages required by taurus. The mocks are written
    into the given output directory (or a zip file if output ends with ".zip")
    '''
    import sys
    import tempfile

    if output.endswith('.zip'):
        zfile, outdir = output, tempfile.mkdtemp()
    else:
        zfile, outdir = None, output

    module_names = ['PyTango', 'PyMca5', 'numpy', 'PyQt4', 'sip', 'lxml',
                    'guidata', 'guiqwt', 'spyderlib', 'IPython', 'ply']
    #module_names = ['numpy']

    exclude = ['exec', 'None',
               'spyderlib.scientific_startup',
               'spyderlib.spyder',
               'spyderlib.widgets.externalshell.start_ipython_kernel']
    include = ['__version__']

    for module_name in module_names:
        build_full_module(module_name, exclude=exclude, include=include,
                          out_prefix=outdir)
    if zfile:
        _zipdir(outdir, zfile)  # compress the dir into the zip file
        shutil.rmtree(outdir)  # delete the dir
    print '\nMocks written in %s' % output


if __name__ == "__main__":
    build_mocks_for_taurus()
