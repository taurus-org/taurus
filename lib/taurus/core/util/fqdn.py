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
This module contains provides the fqdn_no_alias function.
"""

import socket
from taurus import warning


def fqdn_no_alias(hostname):
    """
    Normalize hostname so that it is a full name (including domain name).

    .. note:: this is similar to socket.getfqdn, but it avoids translating
              aliases into their "real" address.
    """
    if hostname == "localhost" or "." in hostname:
        # optimization: leave localhost or names including domain as they are
        return hostname
    try:
        real, aliases, _ = socket.gethostbyname_ex(hostname)
    except (socket.gaierror, socket.herror) as e:
        # return the given hostname in case of error
        return hostname

    if aliases:
        if hostname == real or hostname in aliases:
            # in some corner cases (e.g. when defining several aliases in a
            # hosts file), the hostname may be one of the aliases.
            return hostname

        # return alias if it exists
        if len(aliases) > 1:
            # warn in the (unusual) case that there is more than 1 alias
            warning("fqdn_no_alias: %s has %d aliases. Using the first one",
                    hostname,
                    len(aliases)
                    )
        return aliases[0]
    else:
        # if there are no aliases, return real
        return real


if __name__ == '__main__':

    # TODO: once we move to PyTest, test_fqdn_no_alias could be put in the
    #       official tests (test_fqdn_no_alias_local would require to be
    #       generalized)

    def test_fqdn_no_alias():
        """tests for test_fqdn_no_alias"""
        assert fqdn_no_alias("NONEXISTENT") == "NONEXISTENT"
        # test localhost
        assert fqdn_no_alias("localhost") == "localhost"
        # test with an aliased full hostname+domain (alias should not resolv!)
        print(socket.gethostbyname_ex('mail.google.com'))
        print("socket.getfqdn:", socket.getfqdn("mail.google.com"))
        assert fqdn_no_alias("mail.google.com") == "mail.google.com"


    def test_fqdn_no_alias_local(name="www"):
        import re
        # test with an existent host in your domain
        print(socket.gethostbyname_ex(name))
        print("socket.getfqdn:", socket.getfqdn(name))
        assert re.match(name + r"\.[a-zA-Z0-9\.-]+", fqdn_no_alias(name))


    test_fqdn_no_alias()
    test_fqdn_no_alias_local()



