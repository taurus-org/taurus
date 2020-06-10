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


"""Unit tests for TaurusCommandButton"""


import pytest
from taurus.qt.qtgui.button import TaurusCommandButton
from taurus.external.qt import Qt

try:
    # The following are Tango-centric imports.
    # TODO: change them if/when TaurusCommandbuttongets generalized
    from PyTango import CommunicationFailed
    from taurus.core.tango.test import taurus_test_ds  # pytest fixture
    _TANGO_MISSING = False
except:
    _TANGO_MISSING = True


@pytest.mark.skipif(_TANGO_MISSING, reason="tango-dependent test")
def test_timeout(qtbot, taurus_test_ds):
    """Check that the timeout property works"""
    w = TaurusCommandButton(command='Sleep')
    qtbot.addWidget(w)

    try:
        w.setModel(taurus_test_ds)

        # set the parameter for the sleep command to 0.2 seconds
        w.setParameters([.2])

        # Create a callback to check the result of the execution
        def _check_result(res):
            return res == .2

        # Check that the button emits commandExecuted when timeout > exec time
        w.setTimeout(10)
        assert w.getTimeout() == 10
        with qtbot.waitSignal(w.commandExecuted, check_params_cb=_check_result):
            qtbot.mouseClick(w, Qt.Qt.LeftButton)

        # Check that, if timeout < exec time, commandExecuted is NOT emited
        # and CommunicationFailed is raised
        w.setTimeout(.1)
        assert w.getTimeout() == .1
        with pytest.raises(CommunicationFailed):
            with qtbot.assertNotEmitted(w.commandExecuted):
                # call _onClicked instead of emulating a click to bypass
                # the @ProtectTaurusMessageBox protection of onClicked()
                w._onClicked()
    finally:
        # just in case this helps avoiding problems at exit
        w.setModel(None)



