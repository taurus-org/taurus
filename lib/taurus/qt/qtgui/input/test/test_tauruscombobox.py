from taurus.qt.qtgui.application import TaurusApplication
from taurus.qt.qtgui.input import TaurusValueComboBox
import taurus

def test_TaurusValueCombobox():
    """Check that the TaurusValueComboBox is started with the right display
    See https://github.com/taurus-org/taurus/pull/1032
    """
    # TODO: Parameterize this test
    app = TaurusApplication.instance()
    if app is None:
        app = TaurusApplication(cmd_line_parser=None)

    # test with a pint quantity
    model = 'sys/tg_test/1/short_scalar'
    a = taurus.Attribute(model)
    units = a.write(123).wvalue.units
    w = TaurusValueComboBox()
    names = [("A", 1234), ("B", "123"), ("C", 123 * units), ("E", -123)]
    w.addValueNames(names)
    w.setModel(model)
    assert(w.currentText() == "C")

    # test with a boolean (using quantities)
    model = 'sys/tg_test/1/boolean_scalar'
    a = taurus.Attribute(model)
    a.write(False)
    w = TaurusValueComboBox()
    w.addValueNames([("N", None), ("F", False), ("T", True)])
    w.setModel(model)
    assert (w.currentText() == "F")

    # test with a spectrum
    model = 'sys/tg_test/1/boolean_spectrum'
    a = taurus.Attribute(model)
    a.write([False, True, False])
    w = TaurusValueComboBox()
    w.addValueNames([
        ("A", False),
        ("B", [False, False, False]),
        ("C", [False, True, False]),
    ])
    w.setModel(model)
    assert (w.currentText() == "C")

    # test with strings
    model = 'sys/tg_test/1/string_scalar'
    a = taurus.Attribute(model)
    a.write("foobar")
    w = TaurusValueComboBox()
    w.addValueNames([("A", "foobarbaz"), ("B", "FOOBAR"), ("C", "foobar")])
    w.setModel(model)
    assert (w.currentText() == "C")

    # test non-match
    model = 'sys/tg_test/1/string_scalar'
    a = taurus.Attribute(model)
    a.write("foo")
    w = TaurusValueComboBox()
    w.addValueNames([("A", "foobarbaz"), ("B", "FOOBAR"), ("C", "foobar")])
    w.setModel(model)
    assert (w.currentText() == "")
    w.setModel(None)