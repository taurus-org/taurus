#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

"""helper methods for sardana sphinx documentation"""

__expr = ('or',)

def process_type(t, obj_type='class'):
    t = t.strip()
    if not t: return ''
    if t in __expr: return t
    if t.count(' or '):
       i = t.index(' or ')
       return ' '.join(map(process_type, (t[:i],'or', t[i+4:])))
    if not t.count('<') or not t.count('>'): return ':%s:`%s`' % (obj_type, t)
    
    #process a container template
    start, stop = t.index('<'), t.index('>')
    main_type = t[:start]
    main_type = process_type(main_type)
    types = t[start+1:stop].split(',')
    types = ', '.join(map(process_type, types))
    return "%s <%s>" % (main_type, types)

def process_param(line):
    new_lines = []
    try:
        prefix, param, desc = line.split(':', 2)
        p, param_name = param.split()
        desc = desc.strip()
        if desc[0] == '(' :
            pos = desc.find(')')
            if pos != -1:
                elem_type = desc[1:pos]
                klass = process_type(elem_type)
                desc = desc[pos+1:]
                new_lines.append('%s:type %s: %s' % (prefix, param_name, klass))
        new_lines.append('%s:param %s: %s' % (prefix, param_name, desc))
    except Exception, e:
        print "Sardana sphinx extension: Not able to process param: '%s'" % line
        print "      Reason:",str(e)
        new_lines.append(line)
    return new_lines

def process_return(line):
    new_lines = []
    try:
        prefix, param, desc = line.split(':', 2)
        desc = desc.strip()
        if desc[0] == '(' :
            pos = desc.find(')')
            if pos != -1:
                elem_type = desc[1:pos]
                klass = process_type(elem_type)
                desc = desc[pos+1:]
                new_lines.append('%s:rtype: %s' % (prefix, klass))
        new_lines.append('%s:return: %s' % (prefix, desc))
    except Exception, e:
        print "Sardana sphinx extension: Not able to process 'return': '%s'" % line
        print "      Reason:",str(e)
        new_lines.append(line)
    return new_lines

def process_raise(line):
    new_lines = []
    try:
        prefix, param, desc = line.split(':', 2)
        desc = desc.strip()
        klass = ''
        if desc[0] == '(' :
            pos = desc.find(')')
            if pos != -1:
                elem_type = desc[1:pos]
                klass = "(" + process_type(elem_type, obj_type='exc') + ")"
                desc = desc[pos+1:]
        new_lines.append('%s:raise: %s %s' % (prefix, klass, desc))
    except Exception, e:
        print "Sardana sphinx extension: Not able to process 'raise': '%s'" % line
        print "      Reason:", str(e)
        new_lines.append(line)
    return new_lines

def _is_return(line):
    ret = line.startswith(':return')
    ret |= line.startswith(':returns')
    return ret

def _is_param(line):
    ret = line.startswith(':param')
    ret |= line.startswith(':parameter')
    ret |= line.startswith(':arg')
    ret |= line.startswith(':argument')
    ret |= line.startswith(':key')
    ret |= line.startswith(':keyword')
    return ret

def _is_raise(line):
    ret = line.startswith(':raise')
    ret |= line.startswith(':except')
    return ret

def process_docstring(app, what, name, obj, options, lines):
    ret = []
    for nb, line in enumerate(lines):
        line_strip = line.strip()
        if _is_param(line_strip):
            ret.extend(process_param(line))
        elif _is_return(line_strip):
            ret.extend(process_return(line))
        elif _is_raise(line_strip):
            ret.extend(process_raise(line))
        else:
            ret.append(line)
    
    del lines[:]
    lines.extend(ret)

import inspect
from sphinx.util.inspect import getargspec

def _format_method_args(obj):
    if inspect.isbuiltin(obj) or \
           inspect.ismethoddescriptor(obj):
        # can never get arguments of a C function or method
        return None
    argspec = getargspec(obj)
    if argspec[0] and argspec[0][0] in ('cls', 'self'):
        del argspec[0][0]
    return inspect.formatargspec(*argspec)

def _format_function_args(obj):
    if inspect.isbuiltin(obj) or \
           inspect.ismethoddescriptor(obj):
        # cannot introspect arguments of a C function or method
        return None
    try:
        argspec = getargspec(obj)
    except TypeError:
        # if a class should be documented as function (yay duck
        # typing) we try to use the constructor signature as function
        # signature without the first argument.
        try:
            argspec = getargspec(obj.__new__)
        except TypeError:
            argspec = getargspec(obj.__init__)
            if argspec[0]:
                del argspec[0][0]
    args = inspect.formatargspec(*argspec)
    # escape backslashes for reST
    args = args.replace('\\', '\\\\')
    return args

def process_signature(app, what, name, obj, options, signature, return_annotation):
    if hasattr(obj, "__wrapped__"):
        if what == "method":
            from taurus.core.util.wrap import wrapped
            obj = wrapped(obj)
            signature = _format_method_args(obj)
            return signature, return_annotation
                
    
def setup(app):
    #app.connect('autodoc-process-docstring', process_docstring)
    app.connect('autodoc-process-signature', process_signature)
