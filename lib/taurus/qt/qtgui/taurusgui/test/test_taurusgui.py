from taurus.qt.qtgui.taurusgui import TaurusGui, utils
from taurus.external.qt import PYSIDE2
import pytest

p1 = utils.PanelDescription(
    "testpanel1",
    classname="taurus.qt.qtgui.panel.TaurusForm",
    model=["eval:1"],
    widget_properties={
        "withButtons": False,
        "foobar": 34
    }
)

@pytest.mark.xfail(PYSIDE2, reason="This test is known to fail with PySide2")
def test_paneldescription(qtbot):
    gui = TaurusGui(confname=__file__, configRecursionDepth=0)
    w1 = gui.getPanel('testpanel1').widget()
    qtbot.addWidget(gui)
    qtbot.addWidget(w1)
    assert w1.withButtons is False
    assert w1.isWithButtons() is False
    assert not hasattr(w1, "foobar")
    assert w1.modifiableByUser is False