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
        warning("fqdn_no_alias: problem resolving %s: %r", hostname, e)
        return hostname

    if aliases:
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

    # TODO: convert this into a pytest test
    #       (but need to figure out how to generalize the "www" test)

    # test nonexistent
    assert fqdn_no_alias("NONEXISTENT") == "NONEXISTENT"
    # test localhost
    assert fqdn_no_alias("localhost") == "localhost"
    # test with an existent host in your domain (with just host name)
    # TODO: this is domain-specific! it needs to be generalized somehow
    print(socket.gethostbyname_ex('www'))  # use something in your domain
    print("socket.getfqdn:", socket.getfqdn("www"))
    assert fqdn_no_alias("www") == "www.cells.es"
    # test with an aliased full hostname+domain (the alias is not resolved!)
    print(socket.gethostbyname_ex('mail.google.com'))
    print("socket.getfqdn:", socket.getfqdn("mail.google.com"))
    assert fqdn_no_alias("mail.google.com") == "mail.google.com"

