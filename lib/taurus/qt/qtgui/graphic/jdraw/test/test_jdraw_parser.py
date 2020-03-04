import os
from taurus.qt.qtgui.application import TaurusApplication
from taurus.qt.qtgui.graphic.jdraw import (
    TaurusJDrawGraphicsFactory,
    jdraw_parser
)
from taurus.qt.qtgui.graphic import TaurusGraphicsScene


app = TaurusApplication.instance()
if app is None:
    app = TaurusApplication([], cmd_line_parser=None)


def test_jdraw_parser():
    """Check that jdraw_parser does not break with JDBar elements"""
    fname = os.path.join(os.path.dirname(__file__), "res", "bug1077.jdw")
    factory = TaurusJDrawGraphicsFactory(None)
    p = jdraw_parser.parse(fname, factory)
    assert isinstance(p, TaurusGraphicsScene)


if __name__ == '__main__':
    test_jdraw_parser()
