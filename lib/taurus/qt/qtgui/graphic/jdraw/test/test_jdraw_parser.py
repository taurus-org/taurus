import os
from taurus.external.qt.QtCore import PYSIDE2
import pytest


from taurus.qt.qtgui.graphic.jdraw import (
    TaurusJDrawGraphicsFactory,
    jdraw_parser
)
from taurus.qt.qtgui.graphic import TaurusGraphicsScene


@pytest.mark.skipif(PYSIDE2, reason="Avoid segfault when using PySide2")
def test_jdraw_parser(qtbot):
    """Check that jdraw_parser does not break with JDBar elements"""
    fname = os.path.join(os.path.dirname(__file__), "res", "bug1077.jdw")
    factory = TaurusJDrawGraphicsFactory(None)
    p = jdraw_parser.parse(fname, factory)
    assert isinstance(p, TaurusGraphicsScene)


if __name__ == '__main__':
    test_jdraw_parser()
