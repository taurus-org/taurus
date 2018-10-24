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

from __future__ import absolute_import
from future.utils import string_types

from builtins import zip
import re
import hashlib
import taurus
from taurus import isValidName, debug
from taurus.core import TaurusElementType

from taurus.core.taurusvalidator import (TaurusAttributeNameValidator,
                                         TaurusDeviceNameValidator,
                                         TaurusAuthorityNameValidator)

__all__ = ['EvaluationDeviceNameValidator',
           'EvaluationAttributeNameValidator']

# Pattern for python variables
PY_VAR = r'(?<![\.a-zA-Z0-9_])[a-zA-Z_][a-zA-Z0-9_]*'
PY_VAR_RE = re.compile(PY_VAR)
# Pattern for semicolon-separated <variable>=<value> pairs (in URI paths)
K_EQUALS_V = r'(%s)=([^?#=;]+)' % PY_VAR
K_EQUALS_V_RE = re.compile(K_EQUALS_V)
#
QUOTED_TEXT = '(".*?"|\'.*?\')'
QUOTED_TEXT_RE = re.compile(QUOTED_TEXT)


def _findAllTokensBetweenChars(string, start, end, n=None):
    '''Finds the text between (possibly nested) delimiters in a string.
    In case of nested delimiters, only the outermost level is
    returned. It returns a tuple of (idx,token)

    Example::

      _findAllTokensBetweenChars('{foo}bar{zig{zag}}boom', '{', '}')
      --> [(1,'foo'), (9, 'zig{zag}')]


    :param string: (str) the expression to parse
    :param start: (str) the char delimiting the start of a token
    :param end: (str) the char delimiting the end of a token
    :param n: (int or None) If an int is passed, it sets the maximum number
              of tokens to be found

    :return: (list(<int>,<str>)) a list of (idx, token) tuples. The idx is the
    position of the token in `string`
             (tokens d not include the delimiting chars not including the
             brackets)
    '''
    if start == end:
        raise ValueError('star_char must be different from end_char')
    if string.count(start) != string.count(end):
        raise ValueError('Non-matching delimiters (%i "%s" vs %i "%s")' %
                         string.count(start), start, string.count(end), end)
    tokens = []
    indexes = []
    idx = 0
    rest = string
    while len(tokens) != n:
        s = rest.find(start)
        if s < 0:
            break
        e = rest.find(end) + 1
        while rest[s:e].count(start) != rest[s:e].count(end):
            ne = rest[e:].find(end)
            e = e + 1 + ne
        tokens.append((idx + s, rest[s + 1:e - 1]))
        idx += e
        rest = rest[e:]
    return tokens


def _isQuoted(string, substring, idx):
    """returns True if position i of string is in a quoted region"""
    bfr = string[:idx]
    aft = string[idx + len(substring):]
    if (bfr.count('"') % 2 or aft.count('"') % 2 or
            bfr.count("'") % 2 or aft.count("'") % 2):
        return True
    else:
        return False


def _replacepos(string, old, new, idx):
    """return copy of string where the occurrence of substring `old` at
    position `pos` is replaced by `new`
    """
    if not string[idx:].startswith(old):
        raise Exception('invalid')
    return string[:idx] + new + string[idx + len(old):]


class EvaluationAuthorityNameValidator(TaurusAuthorityNameValidator):
    '''Validator for Evaluation authority names. For now, the only supported
    authority (in strict mode) is "//localhost":
    '''
    scheme = 'eval'
    authority = '//localhost'
    path = '(?!)'
    query = '(?!)'
    fragment = '(?!)'

    @property
    def nonStrictNamePattern(self):
        '''implement in derived classes if a "less strict" pattern is allowed
        (e.g. for backwards-compatibility, "tango://a/b/c" could be an accepted
        device name, even if it breaks RFC3986).
        '''
        return r'^(?P<scheme>eval|evaluation)://(db=(?P<dbname>[^?#;]+))$'


class EvaluationDeviceNameValidator(TaurusDeviceNameValidator):
    '''Validator for Evaluation device names. Apart from the standard named
    groups (scheme, authority, path, query and fragment), the following named
    groups are created:

     - devname: device name (either _evalname or _evaldotname)
     - [_evalname]: evaluation instance name (aka non-dotted dev name)
     - [_evaldotname]: evaluation instance dotted name (if dotted name given)
     - [_old_devname]: devname without "@". Only in non-strict mode
     - [_dbname] and [_subst]: unused. Only if non-strict mode

    Note: brackets on the group name indicate that this group will only contain
    a string if the URI contains it.
    '''

    scheme = 'eval'
    authority = EvaluationAuthorityNameValidator.authority
    _evaldotname = (
        r'((?P<_evalinstname>\w+)=)?' +
        r'(?P<_evalmodname>(\w+\.)*\w+)\.' +
        r'(?P<_evalclassname>(\w+|\*))' +
        r'(?P<_evalclassparenths>\(("[^"]*"|\'[^\']*\'|[^\'"/])*?\))?'
        )
     # _evaldotname = r'(?P<_evaldotname>(\w+=)?(\w+\.)+(\w+(\(\))?|\*)))'
    _evaluatorname = (r'((?P<_evalname>[^/?#:\.=]+)|(?P<_evaldotname>%s))' %
                      _evaldotname)
    devname = r'(?P<devname>@%s)' % _evaluatorname
    path = r'(?!//)/?%s' % devname
    query = '(?!)'
    fragment = '(?!)'

    def getUriGroups(self, name, strict=None):
        '''reimplemented from :class:`TaurusDeviceNameValidator` to provide
        backwards compatibility with ol syntax'''
        groups = TaurusDeviceNameValidator.getUriGroups(self, name,
                                                        strict=strict)
        if groups is not None and not groups['__STRICT__']:
            _old_devname = groups['_old_devname']
            groups['devname'] = '@%s' % _old_devname
            if '.' in _old_devname:
                groups['_evalname'] = None
                groups['_evaldotname'] = _old_devname
            else:
                groups['_evalname'] = _old_devname
                groups['_evaldotname'] = None
        return groups

    def getNames(self, fullname, factory=None):
        '''reimplemented from :class:`TaurusDeviceNameValidator`'''
        from .evalfactory import EvaluationFactory
        # TODO: add mechanism to select strict mode instead of hardcoding here
        groups = self.getUriGroups(fullname)
        if groups is None:
            return None

        authority = groups.get('authority')
        if authority is None:
            f_or_fklass = factory or EvaluationFactory
            groups['authority'] = authority = f_or_fklass.DEFAULT_AUTHORITY

        complete = 'eval:%(authority)s/%(devname)s' % groups
        normal = '%(devname)s' % groups
        short = normal.lstrip('@')

        return complete, normal, short

    @property
    def nonStrictNamePattern(self):
        '''In non-strict mode support old-style eval names
        '''
        p = r'^(?P<scheme>eval|evaluation)://(db=(?P<_dbname>[^?#;]+);)?' + \
            r'(dev=(?P<_old_devname>%s))' % self._evaluatorname + \
            r'(\?(?!configuration=)(?P<_subst>[^#?]*))?$'
        return p


class EvaluationAttributeNameValidator(TaurusAttributeNameValidator):
    '''Validator for Evaluation attribute names. Apart from the standard named
    groups (scheme, authority, path, query and fragment), the following named
    groups are created:

     - attrname: attribute name. same as concatenating _subst with _expr
     - _expr: a mathematical expression
     - _evalrefs: a list of eval refs found in the name (see :meth:`getRefs`)
     - [_subst]: a semicolon-separated repetition of key=value (for replacing
       them in _expr)
     - [devname]: as in :class:`EvaluationDeviceNameValidator`
     - [_evalname]: evaluation instance name (aka non-dotted dev name)
     - [_evaldotname]: evaluator instance dotted name (if dotted name given)
     - [_old_devname]: devname without "@". Only in non-strict mode
     - [_dbname] and [_subst]: unused. Only if non-strict mode
     - [cfgkey] same as fragment (for bck-compat use only)

    Note: brackets on the group name indicate that this group will only contain
    a value if the URI contains it.
    '''
    scheme = 'eval'
    authority = EvaluationAuthorityNameValidator.authority
    path = ((r'(?!//)/?(%s/)?' +
             r'(?P<attrname>(?P<_subst>(%s;)+)?(?P<_expr>[^@?#]+))') %
            (EvaluationDeviceNameValidator.devname, K_EQUALS_V)
            )
    query = '(?!)'
    fragment = '(?P<cfgkey>[^# ]*)'

    @staticmethod
    def expandExpr(expr, substmap):
        '''expands expr by substituting all keys in map by their value.
        Note that eval references in expr (i.e. text within curly brackets)
        is not substituted.

        :param expr: (str) string that may contain symbols defined in symbolMap
        :param symbolMap: (dict or str) dictionary whose keys (strings) are
                          symbols to be substituted in `expr` and whose values
                          are the corresponding replacements. Alternatively, a
                          string containing a semi-colon separated list of
                          symbol=value pairs can also be passed.
        '''
        if isinstance(substmap, string_types):
            substmap = dict(K_EQUALS_V_RE.findall(substmap))
        ret = expr
        protected = {}

        # temporarily replace the text within quotes by hash-based placeholders
        for s in QUOTED_TEXT_RE.findall(expr):
            placeholder = hashlib.md5(s.encode('utf-8')).hexdigest()
            protected[placeholder] = s
            ret = re.sub(s, placeholder, ret)

        # Substitute each k by its v in the expr (unless they are in
        # references)
        for k, v in substmap.items():
            # create a pattern for matching complete word k
            # unless it is within between curly brackets
            keyPattern = r'(?<!\w)%s(?!\w)(?![^\{]*\})' % k
            # substitute matches of keyPattern by their value
            ret = re.sub(keyPattern, v, ret)

        # restore the protected strings
        for placeholder, s in protected.items():
            ret = re.sub(placeholder, s, ret)
        return ret

    @staticmethod
    def getRefs(expr, ign_quoted=True):
        '''Find the attribute references (strings within brackets) in an eval
        expression. In case of nested references, only the outermost level is
        returned.

        Example: val.getRefs('{foo}bar{zig{zag}}boom') --> ['foo', 'zig{zag}']

        :param expr: (str) the expression to parse
        :param ign_quoted: If True (default) ignore refs within quotes

        :return (list<str>) a list of refs (not including the brackets)
        '''
        refs = _findAllTokensBetweenChars(expr, '{', '}')

        # print expr
        # print '0123456789012345678901234567890123456789'
        # print refs

        if refs and not ign_quoted:
            _, refs = list(zip(*refs))
            return refs

        ret = []
        for i, ref in refs:
            if not _isQuoted(expr, "{" + ref + "}", i):
                ret.append(ref)
        return ret

    @staticmethod
    def replaceUnquotedRef(string, substring, repl):
        """Return a copy of string where first non-quoted occurrence of
        `substring`
         is replaced by `repl`

        :param string: (str) string to be used
        :param substring: (str) substring to be replaced
        :param repl: (str) replacement

        :return: (str)

        """
        idx = string.find(substring)
        while _isQuoted(string, substring, idx):
            idx = string.find(substring, idx + 1)
        return _replacepos(string, substring, repl, idx)

    def isValid(self, name, matchLevel=None, strict=None):
        '''reimplemented from :class:`TaurusAttributeNameValidator` to do extra
        check on references validity (recursive)
        '''
        # Standard implementation
        if matchLevel is not None:
            groups = self._isValidAtLevel(name, matchLevel=matchLevel)
        else:
            groups = self.getUriGroups(name, strict=strict)
        if groups is None:
            return False

        # now check the references
        for ref in groups['_evalrefs']:
            if not isValidName(ref, etypes=(TaurusElementType.Attribute,),
                               strict=strict):
                debug('"%s" is invalid because ref "%s" is not a ' +
                      'valid attribute', name, ref)
                return False
        return True

    def getUriGroups(self, name, strict=None):
        '''reimplemented from :class:`TaurusAttributeNameValidator` to provide
        backwards compatibility with old syntax'''

        # mangle refs before matching the pattern to sanitize them
        refs = self.getRefs(name, ign_quoted=False)
        refs_dict = {}
        _name = name
        for i, ref in enumerate(refs):
            refs_dict['__EVALREF_%d__' % i] = '{%s}' % ref
            _name = _name.replace('{%s}' % ref, '{__EVALREF_%d__}' % i, 1)

        _groups = TaurusAttributeNameValidator.getUriGroups(self, _name,
                                                            strict=strict)
        if _groups is None:
            return None

        # create the groups dict with unmangled refs in its values
        groups = {}
        for n, g in _groups.items():
            if isinstance(g, string_types):  # avoid None or boolean values
                g = g.format(**refs_dict)
            groups[n] = g

        if not groups['__STRICT__']:
            # adapt attrname to what would be in strict mode
            _subst = groups['_subst'] or ''
            _expr = groups['_expr']
            if _subst:
                groups['attrname'] = "%s;%s" % (_subst.rstrip(';'), _expr)
            else:
                groups['attrname'] = _expr

            # adapt devname to what would be in strict mode
            old_devname = groups['_old_devname']
            if old_devname is None:
                groups['devname'] = None
            else:
                groups['devname'] = '@%s' % old_devname

        # check that there are not ";" in the expr (ign. quoted text and refs)
        sanitized_expr = QUOTED_TEXT_RE.sub('', groups['_expr'])
        for ref in self.getRefs(sanitized_expr, ign_quoted=False):
            sanitized_expr = sanitized_expr.replace(ref, '')
        if ";" in sanitized_expr:
            return None

        # add a group containing refs in attrname (ign. those in quoted text)
        groups['_evalrefs'] = self.getRefs(groups['attrname'], ign_quoted=True)

        return groups

    def _getSimpleNameFromExpression(self, expression):
        """Get the simple name of an evaluationAttribute from an expression"""
        name = expression
        for ref in self.getRefs(expression, ign_quoted=True):
            manager = taurus.core.TaurusManager()
            scheme = manager.getScheme(ref)
            _f = taurus.Factory(scheme)
            attrNameValidator = _f.getAttributeNameValidator()
            _, _, simple_name = attrNameValidator.getNames(ref)
            name = self.replaceUnquotedRef(name, '{%s}' % ref, simple_name)
        return name

    def _expandRefNames(self, attrname):
        """Expand the refs in an eval name to their full names"""
        name = attrname
        for ref in self.getRefs(attrname, ign_quoted=True):
            manager = taurus.core.TaurusManager()
            scheme = manager.getScheme(ref)
            _f = taurus.Factory(scheme)
            attrNameValidator = _f.getAttributeNameValidator()
            full_name, _, _ = attrNameValidator.getNames(ref)
            if full_name is None:
                debug('Cannot expand the fullname of %s' % ref)
                return None
            name = self.replaceUnquotedRef(name, '{%s}' % ref,
                                           '{%s}' % full_name)
        return name

    def getNames(self, fullname, factory=None, fragment=False):
        '''reimplemented from :class:`TaurusDeviceNameValidator`'''
        from .evalfactory import EvaluationFactory
        groups = self.getUriGroups(fullname)
        if groups is None:
            return None

        f_or_fklass = factory or EvaluationFactory

        authority = groups.get('authority')
        if authority is None:
            groups['authority'] = authority = f_or_fklass.DEFAULT_AUTHORITY

        devname = groups.get('devname')
        if devname is None:
            groups['devname'] = devname = f_or_fklass.DEFAULT_DEVICE

        complete = 'eval:%s/%s/%s' % (authority, devname, groups['attrname'])
        complete = self._expandRefNames(complete)

        normal = groups['attrname']
        if devname != f_or_fklass.DEFAULT_DEVICE:
            normal = '%s/%s' % (devname, normal)
        if authority != f_or_fklass.DEFAULT_AUTHORITY:
            normal = '%s/%s' % (authority, normal)
        short = self._getSimpleNameFromExpression(groups['_expr'])

        # return fragment if requested
        if fragment:
            key = groups.get('fragment', None)
            return complete, normal, short, key
        return complete, normal, short

    @property
    def nonStrictNamePattern(self):
        '''In non-strict mode support old-style eval config names
        '''
        p = r'^(?P<scheme>eval|evaluation)://(db=(?P<_dbname>[^?#;]+);)?' + \
            r'(dev=(?P<_old_devname>[^?#;]+);)?' + \
            r'(?P<_expr>[^?#;]+)' + \
            r'(\?(?P<_substquery>(?!configuration=)(?P<_subst>%s(;%s)*)))?' % \
            (K_EQUALS_V, K_EQUALS_V) + \
            r'(\?(?P<query>configuration(=' + \
            '(?P<fragment>(?P<cfgkey>[^#?]*)))?))?$'

        return p

    def getExpandedExpr(self, name):
        '''
        Returns the expanded expression from the attribute name URI

        :param name: (str) eval attribute URI

        :return: (str) the expression (from the name )expanded with any
                 substitution k,v pairs also defined in the name
        '''
        groups = self.getUriGroups(name)
        if groups is None:
            return None
        _expr = groups['_expr']
        _subst = groups['_subst']
        return self.expandExpr(_expr, _subst or {})

    def getAttrName(self, s):
        #@TODO: Maybe this belongs to the factory, not the validator
        # TODO: this is pre-tep14 API from the
        # EvaluationConfigurationNameValidator. Check usage and remove.
        names = self.getNames(s)
        if names is None:
            return None
        return names[0]

    def getDeviceName(self, name):
        #@TODO: Maybe this belongs to the factory, not the validator
        '''Obtain the fullname of the device from the attribute name'''
        from .evalfactory import EvaluationFactory
        groups = self.getUriGroups(name)
        if groups is None:
            return None
        authority = groups.get('authority')
        if authority is None:
            authority = EvaluationFactory.DEFAULT_AUTHORITY
        devname = groups.get('devname')
        if devname is None:
            devname = EvaluationFactory.DEFAULT_DEVICE
        return 'eval:%s/%s' % (authority, devname)

    def getDBName(self, s):
        #@TODO: Maybe this belongs to the factory, not the validator
        '''returns the full data base name for the given attribute name'''
        from .evalfactory import EvaluationFactory
        m = self.name_re.match(s)
        if m is None:
            return None
        dbname = m.group('dbname') or EvaluationFactory.DEFAULT_DATABASE
        return "eval://db=%s" % dbname


if __name__ == '__main__':
    pass
