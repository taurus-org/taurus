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

"""This module contains the base taurus name validator classes"""
from __future__ import print_function

import re
from taurus import tauruscustomsettings
from taurus.core.util.singleton import Singleton
from taurus.core.taurushelper import makeSchemeExplicit

__all__ = ["TaurusAuthorityNameValidator", "TaurusDeviceNameValidator",
           "TaurusAttributeNameValidator"]


__docformat__ = "restructuredtext"


class _TaurusBaseValidator(Singleton):
    '''This is a private base class for taurus base validators. Do not derive
    from it if you are implementing a new scheme. Derive from the public
    classes from this module instead.
    '''
    scheme = None
    auth = '(?!)'  # note: '(?!)' is a pattern that will never match
    path = '(?!)'
    query = '(?!)'
    fragment = '(?!)'

    def __init__(self):
        if self.scheme is None:
            msg = ('This is  an abstract name validator class. ' +
                   'Only scheme-specific derived classes can be instantiated')
            raise NotImplementedError(msg)

        self.name_re = re.compile(self.namePattern)
        if self.nonStrictNamePattern is not None:
            self.nonStrictName_re = re.compile(self.nonStrictNamePattern)
        else:
            self.nonStrictName_re = None

    @property
    def namePattern(self):
        '''Provides a name pattern by composing the pattern strings for the
        URI segments'''
        return self.pattern % dict(scheme=self.scheme,
                                   authority=self.authority,
                                   path=self.path,
                                   query=self.query,
                                   fragment=self.fragment)

    @property
    def nonStrictNamePattern(self):
        '''implement in derived classes if a "less strict" pattern is allowed
        (e.g. for backwards-compatibility, "tango://a/b/c" could be an accepted
        device name, even if it breaks RFC3986).
        '''
        return None

    def isValid(self, name, matchLevel=None, strict=None):
        '''Whether the name matches the validator pattern.
        If strict is False, it also tries to match against the non-strict regexp
        (It logs a warning if it matched only the non-strict alternative)

        .. note:: The "matchLevel" keyword argument is deprecated and only
                  implemented for backwards compatibility. Do not use it for
                  new classes
        '''
        # warn if the deprecated matchLevel kwarg was received
        if matchLevel is not None:
            return self._isValidAtLevel(name, matchLevel=matchLevel)
        return self.getUriGroups(name, strict=strict) is not None

    def _isValidAtLevel(self, name, matchLevel=None):
        # matchLevel is a tango-centric deprecated  argument of isValid. Warn.
        msg = ('matchLevel is a Tango-centric concept. Avoid it outside ' +
               'the tango scheme')
        from taurus import warning
        warning(msg)
        return self.isValid(name)

    def getUriGroups(self, name, strict=None):
        '''returns the named groups dictionary from the URI regexp matching.
        If strict is False, it also tries to match against the non-strict regexp
        (It logs a warning if it matched only the non-strict alternative)
        '''
        if strict is None:
            strict = getattr(tauruscustomsettings, 'STRICT_MODEL_NAMES', False)
        name = makeSchemeExplicit(name, default=self.scheme)
        m = self.name_re.match(name)
        # if it is strictly valid, return the groups
        if m is not None:
            ret = m.groupdict()
            ret['__STRICT__'] = True
            return ret
        # if we are strict (or no less-strict pattern is defined) return None
        if strict or self.nonStrictName_re is None:
            return None
        # If a less-strict pattern is defined, use it, but warn if it works
        m = self.nonStrictName_re.match(name)
        if m is None:
            return None
        else:
            from taurus import warning
            msg = ('Model name "%s" is supported but not strictly valid. \n' +
                   'It is STRONGLY recommended that you change it to \n' +
                   'strictly follow %s scheme syntax') % (name, self.scheme)
            warning(msg)
            ret = m.groupdict()
            ret['__STRICT__'] = False
            return ret

    def getParams(self, name):
        # deprecation warning
        msg = ('%s.getParams() is deprecated. Use getUriGroups() instead.' %
               self.__class__.__name__)
        from taurus import warning
        warning(msg)
        # support old group names
        groups = self.getUriGroups(name, strict=False)
        if groups is None:
            return None
        groups = dict(groups)  # copy, just in case
        groups['devicename'] = groups.get('devname')
        groups['devalias'] = groups.get('_devalias')
        groups['attributename'] = groups.get('_shortattrname')
        groups['configparam'] = groups.get('fragment')
        return groups

    def getNames(self, fullname, factory=None):
        """Returns a tuple of three elements with  (complete_name, normal_name,
        short_name) or None if no match is found.
        The definitions of each name are:

        - complete: the full URI allowing an unambiguous identification of the
          model within taurus (note: it must include the scheme).
        - normal: an unambiguous URI at the scheme level. Any parts that are
          optional and equal to the scheme's default can be stripped.
          In particular, the scheme name is typically stripped for all schemes.
        - short: a short name (not necessarily a valid URI) useful for display
          in cases where ambiguity is tolerable.

        Example: In a tango system where the default TANGO_HOST is "foo:123"
        and a device "a/b/c" has been defined with alias "bar" and having an
        attribute called "d", getNames would return:

        - for the authority::

            ('tango://foo:123', '//foo:123', 'foo:123')

        - for the device::

            ('tango://foo:123/a/b/c', 'a/b/c', 'bar')

            note: if foo:123 wasn't the default TANGO_HOST, the normal name
            would be '//foo:123/a/b/c'. Equivalent rules apply to Attribute
            normal names.

        - for the attribute::

            ('tango://foo:123/a/b/c/d', 'a/b/c/d', 'd')

            note: if foo123 wasn't the default TANGO_HOST, the normal name
            would be '//foo:123/a/b/c/d'

         - for the attribute (assuming we passed #label)::

            ('tango://foo:123/a/b/c/d#label',
             'a/b/c/d#label',
             'd#label')

         - for the attribute (assuming we did not pass a conf key)::
            ('tango://foo:123/a/b/c/d#',
             'a/b/c/d#',
             'd#')

        Note: it must always be possible to construct the 3 names from a *valid*
        **fullname** URI. If the given URI is valid but it is not the full name,
        it may still be possible in some cases to construct the 3 names, but
        it may involve using defaults provided by the scheme (which may require
        more computation than mere parsing the URI)
        """
        raise NotImplementedError('getNames must be implemented in derived ' +
                                  'classes')


class TaurusAuthorityNameValidator(_TaurusBaseValidator):
    '''Base class for Authority name validators.
    The namePattern will be composed from URI segments as follows:

    <scheme>:<authority>[/<path>][?<query>][#<fragment>]

    Derived classes must provide attributes defining a regexp string for each
    URI segment (they can be empty strings):

    - scheme
    - authority
    - path
    - query
    - fragment
    '''
    pattern = r'^(?P<scheme>%(scheme)s):' + \
              r'(?P<authority>%(authority)s)' + \
              r'((?=/)(?P<path>%(path)s))?' + \
              r'(\?(?P<query>%(query)s))?' + \
              r'(#(?P<fragment>%(fragment)s))?$'

    def getNames(self, name, factory=None):
        '''basic implementation for getNames for authorities. You may
        reimplement it in your scheme if required'''
        groups = self.getUriGroups(name)
        if groups is None:
            return None
        complete = '%(scheme)s:%(authority)s' % groups
        normal = '%(authority)s' % groups
        short = ('%(authority)s' % groups).strip('/')
        return complete, normal, short


class TaurusDeviceNameValidator(_TaurusBaseValidator):
    '''Base class for Device name validators.
    The namePattern will be composed from URI segments as follows:

    <scheme>:[<authority>/]<path>[?<query>][#<fragment>]

    Derived classes must provide attributes defining a regexp string for each
    URI segment (they can be empty strings):

    - scheme
    - authority
    - path
    - query
    - fragment

    Additionally, the namePattern resulting from composing the above segments
    must contain a named group called "devname" (normally within the
    path segment).
    '''
    pattern = r'^(?P<scheme>%(scheme)s):' + \
              r'((?P<authority>%(authority)s)($|(?=[/#?])))?' + \
              r'(?P<path>%(path)s)' + \
              r'(\?(?P<query>%(query)s))?' + \
              r'(#(?P<fragment>%(fragment)s))?$'


class TaurusAttributeNameValidator(_TaurusBaseValidator):
    '''Base class for Attribute name validators.
    The namePattern will be composed from URI segments as follows:

    <scheme>:[<authority>/]<path>[?<query>][#<fragment>]

    Derived classes must provide attributes defining a regexp string for each
    URI segment (they can be empty strings):

    - scheme
    - authority
    - path
    - query
    - fragment

    Additionally, the namePattern resulting from composing the above segments
    must contain a named group called "attrname" (normally within the
    path segment).
    '''
    pattern = r'^(?P<scheme>%(scheme)s):' + \
              r'((?P<authority>%(authority)s)($|(?=[/#?])))?' + \
              r'(?P<path>%(path)s)' + \
              r'(\?(?P<query>%(query)s))?' + \
              r'(#(?P<fragment>%(fragment)s))?$'


class TaurusDatabaseNameValidator(TaurusAuthorityNameValidator):
    '''Backwards-compatibility only. Use TaurusAuthorityNameValidator instead'''

    def __init__(self, *args, **kwargs):
        msg = ('%s is deprecated. Use "Authority" instead of "Database"' %
               self.__class__.__name__)
        from taurus import warning
        warning(msg)
        return TaurusAuthorityNameValidator.__init__(self, *args, **kwargs)


if __name__ == '__main__':

    class FooAttributeNameValidator(TaurusAttributeNameValidator):
        scheme = 'foo'
        authority = '[^?#/]+'
        path = '[^?#]+'
        query = '(?!)'
        fragment = '[^?#]*'

    v = FooAttributeNameValidator()
    name = 'foo://bar#label'
    print(v.isValid(name))
    print(v.getUriGroups(name))
