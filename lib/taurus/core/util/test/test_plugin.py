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

from taurus.core.util.plugin import selectEntryPoints, EntryPointAlike

import pkg_resources
import random
import string


def _random_string(length, chars=string.ascii_lowercase, prefix='', suffix=''):
    """
    Return a random string with given length, prefix and suffix.
    The random characters are chosen from the chars iterable (lowercase
    letters by default)
    """
    r = ''.join(random.choice(chars) for i in range(length))
    return prefix + r + suffix


def mock_entry_point(lines, group=None, dist_name=None):
    """
    Registers a fake distribution that advertises a group of entry points
    (defined by the `lines argument as a sequence of parseable strings).
    The group name is give by the `group` argument (or generated
    randomly if not given). The fake distribution name is given by the
    `dist_name` argument (or generated randomly if not given).

    The function registers (so they are discoverable, e.g. with
    :method:`pkg_resources.iter_entry_points`) and also returns the mapping
    dictionary.
    """
    if group is None:
        group = _random_string(8, prefix='dummygroup_')
    if dist_name is None:
        dist_name = _random_string(8, prefix='dummydist_')

    # create a dummy pkg_resources distribution based on a clone of taurus
    w = pkg_resources.working_set
    d = w.find(pkg_resources.Requirement.parse('taurus'))
    d = d.clone(project_name=dist_name)
    w.add(d, dist_name)

    # create a fake entry point mapping (with group name testgroup))
    mapping = pkg_resources.EntryPoint.parse_map({group: lines}, dist=d)

    # add mapping to the fake distro so that it can be discovered
    d._ep_map = mapping

    # return the mapping
    return mapping


def test_selectEntryPoints():

    # create a fake entry point mapping (with group name testgroup))
    group = _random_string(8, prefix='dummygroup_')
    names = ['foo1', 'foo2', 'baz1', 'baz2', 'bar1', 'bar2']
    mock_entry_point(
        lines=["{0} = obj_{0}".format(n) for n in names],
        group=group
    )

    # check the selectEntryPoints function
    all = selectEntryPoints(group)
    assert isinstance(all[0], pkg_resources.EntryPoint)
    assert [ep.name for ep in all] == sorted(names)

    none_included = selectEntryPoints(group, include=())
    assert len(none_included) == 0

    all_excluded = selectEntryPoints(group, exclude=('.*',))
    assert len(all_excluded) == 0

    some = selectEntryPoints(
        group,
        exclude=("foo2",),
        include=("bar2", "b.*1", "f.*")
    )
    assert [ep.name for ep in some] == ["bar2", "bar1", "baz1", "foo1"]

    mixed = selectEntryPoints(
        group,
        exclude=("b.*",),
        include=(123, "f.*", EntryPointAlike(321, name="boo"))
    )
    assert [ep.name for ep in mixed] == ["123", "foo1", "foo2", "boo"]
    assert mixed[0].load() == 123
    assert mixed[-1].load() == 321
