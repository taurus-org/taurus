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

import pytest
from taurus.core.util.test.test_plugin import mock_entry_point
from taurus.cli.plot import _load_class_from_group, plot_cmd
from click.testing import CliRunner

runner = CliRunner()

class _MockPlot(object):
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.model = None

    def setModel(self, model):
        self.model = model

def test_load_good_class_from_group():
    """Check get_plot_class with several registered plot alternatives"""
    lines = ["mock{}={}:_MockPlot".format(i, __name__) for i in range(3)]
    mapping = mock_entry_point(lines)
    group_name = list(mapping.keys())[0]
    assert _load_class_from_group(group_name) == (_MockPlot, "mock0")


def test_load_onebad_class_from_group():
    """Check get_plot_class with a bad and a good plot alternatives"""
    lines = ["bad=_unimportablemod:Bad", "good={}:_MockPlot".format(__name__)]
    mapping = mock_entry_point(lines)
    group_name = list(mapping.keys())[0]
    assert _load_class_from_group(group_name) == (_MockPlot, "good")


def test_load_onlybad_class_from_group():
    """Check get_plot_class with no plot alternatives"""
    lines = ["bad=_unimportablemod:Bad"]
    mapping = mock_entry_point(lines)
    group_name = list(mapping.keys())[0]
    with pytest.raises(ImportError) as exc_info:
        _load_class_from_group(group_name)
    assert "bad = _unimportablemod:Bad" in str(exc_info.value)


def test_plot_cmd_ls_alt():
    response = runner.invoke(plot_cmd, ["--ls-alt"])
    assert response.exit_code == 0
    assert "Available alternatives" in response.output


def test_plot_cmd_use_alt():
    response = runner.invoke(plot_cmd, ["--use-alt", "_non_existent_alt_"])
    assert "Available alternatives" in response.output
    assert response.exit_code == 1


def test_plot_cmd_help():
    response = runner.invoke(plot_cmd, ["--help"])
    assert "--demo" in response.output
    assert "--ls-alt" in response.output
    assert "--use-alt" in response.output
    assert "--config" in response.output
    assert "--window-name" in response.output
    assert "--x-axis-mode" in response.output
    assert "-x" in response.output
    assert "--help" in response.output
    assert response.exit_code == 0