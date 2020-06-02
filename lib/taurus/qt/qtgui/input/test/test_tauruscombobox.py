from taurus.qt.qtgui.application import TaurusApplication
from taurus.qt.qtgui.input import TaurusValueComboBox
from taurus.core.units import UR
import taurus
import pytest
from taurus.external.qt import PYSIDE2


@pytest.mark.parametrize(
    "model,names,value,expected",
    [
        # test with quantities
        ('eval:@taurus.core.evaluation.test.res.mymod.MyClass()/self.foo',
         [("A", 1234), ("B", "123"), ("C", 123 * UR.mm), ("E", -123)],
         123 * UR.mm,
         "C",
         ),
        # test with a boolean
        ('sys/tg_test/1/boolean_scalar',
         [("N", None), ("F", False), ("T", True)],
         False,
         "F",
         ),
        # test with a boolean spectrum
        ('sys/tg_test/1/boolean_spectrum',
         [
             ("A", False),
             ("B", [False, False, False]),
             ("C", [False, True, False]),
         ],
         [False, True, False],
         "C",
         ),
        # test with a string
        ('sys/tg_test/1/string_scalar',
         [("A", "foobarbaz"), ("B", "FOOBAR"), ("C", "foobar")],
         "foobar",
         "C",
         ),
        # test non-match
        ('sys/tg_test/1/string_scalar',
         [("A", "foobarbaz"), ("B", "FOOBAR"), ("C", "foobar")],
         "foo",
         "",
         ),
    ]
)
def test_TaurusValueCombobox(qtbot, model, names, value, expected):
    """Check that the TaurusValueComboBox is started with the right display
    See https://github.com/taurus-org/taurus/pull/1032
    """
    a = taurus.Attribute(model)
    a.write(value)
    w = TaurusValueComboBox()
    qtbot.addWidget(w)
    # ----------------------------------
    # workaround: avoid PySide2 segfaults when adding quantity to combobox
    # https://bugreports.qt.io/browse/PYSIDE-683
    if isinstance(value, UR.Quantity) and PYSIDE2:
        pytest.skip("avoid segfault due to PYSIDE-683 bug")
    # ----------------------------------
    w.addValueNames(names)
    qtbot.wait_until(lambda: w.count() == len(names), timeout=3200)
    try:
        with qtbot.waitSignal(w.valueChangedSignal, timeout=3200):
            w.setModel(model)
        assert w.currentText() == expected
    finally:
        del a
        # set model to None as an attempt to avoid problems in atexit()
        with qtbot.waitSignal(w.valueChangedSignal, timeout=3200):
            w.setModel(None)
