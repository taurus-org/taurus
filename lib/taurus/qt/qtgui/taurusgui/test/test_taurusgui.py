from taurus.qt.qtgui.application import TaurusApplication
from taurus.qt.qtgui.taurusgui import TaurusGui, utils

app = TaurusApplication.instance()
if app is None:
    app = TaurusApplication([], cmd_line_parser=None)

p1 = utils.PanelDescription(
    "testpanel1",
    classname="taurus.qt.qtgui.panel.TaurusForm",
    model=["eval:1"],
    widget_properties={
        "withButtons": False,
        "foobar": 34
    }
)


def test_paneldescription():
    gui = TaurusGui(confname=__file__, configRecursionDepth=0)
    w1 = gui.getPanel('testpanel1').widget()
    assert w1.withButtons is False
    assert w1.isWithButtons() is False
    assert not hasattr(w1, "foobar")
    assert w1.modifiableByUser is False