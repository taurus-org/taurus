import os
import sys
import pytest
from taurus import tauruscustomsettings as ts


@pytest.mark.parametrize(
    "qt_api, default_qt_api, available, expected",
    [
        # no explicit selection, all bindings available
        ("", "", "all", "pyqt5"),
        (None, "", "all", "pyqt5"),
        # no explicit selection, only one binding available
        (None, "", "PyQt5", "pyqt5"),
        (None, "", "PyQt4", "pyqt"),
        (None, "", "PySide2", "pyside2"),
        (None, "", "PySide", "pyside"),
        # no explicit selection, with default selection, all available
        (None, "pyqt5", "all", "pyqt5"),
        (None, "pyqt",  "all", "pyqt"),
        (None, "pyqt4",  "all", "pyqt"),
        (None, "pyside2",  "all", "pyside2"),
        (None, "pyside",  "all", "pyside"),
        # explicit selection, all bindings available
        ("pyqt5", "", "all", "pyqt5"),
        ("pyqt", "", "all", "pyqt"),
        ("pyqt4", "", "all", "pyqt"),
        ("pyside2", "", "all", "pyside2"),
        ("pyside", "", "all", "pyside"),
        ("pyqt5", "pyqt4", "all", "pyqt5"),
        ("pyqt", "pyqt5", "all", "pyqt"),
        ("pyqt4", "pyqt5", "all", "pyqt"),
        # unsupported selection
        ("unsupported_binding", "", "all", ImportError),
        (None, "unsupported_binding", "all", ImportError),
        ("pyqt5", "", "none", ImportError),
        ("pyqt5", "", "PyQt4", ImportError),
        ("pyqt", "", "PyQt5", ImportError),
        ("pyside2", "", "PySide", ImportError),
        ("pyside", "", "PySide2", ImportError),
    ]
)
@pytest.mark.forked  # run in separate process to avoid side-effects
def test_qt_select(monkeypatch, qt_api, default_qt_api, available, expected):
    """Check that the selection of Qt binding by taurus.external.qt works"""
    # temporarily remove qt bindings from sys.modules
    monkeypatch.delitem(sys.modules, "taurus.external.qt", raising=False)
    for binding in "PyQt5", "PyQt4", "PySide2", "PySide":
        monkeypatch.delitem(sys.modules, binding, raising=False)
        monkeypatch.delitem(sys.modules, binding+".QtCore", raising=False)
    # monkeypatch QT_API and DEFAULT_QT_API with the values from arguments
    if qt_api is None:
        monkeypatch.delenv("QT_API", raising=False)
    else:
        monkeypatch.setenv("QT_API", qt_api)
    monkeypatch.setattr(ts, "DEFAULT_QT_API", default_qt_api)
    # avoid initializations
    monkeypatch.setattr(ts, "QT_AUTO_INIT_LOG", False)
    monkeypatch.setattr(ts, "QT_AUTO_REMOVE_INPUTHOOK", False)
    monkeypatch.setattr(ts, "QT_AVOID_ABORT_ON_EXCEPTION", False)
    # provide importable mocks for all supported bindings
    monkeypatch.syspath_prepend(os.path.join(os.path.dirname(__file__), "res"))
    monkeypatch.setenv("AVAILABLE_QT_MOCKS", available)
    # Now that the environment is clean, test the shim
    if not isinstance(expected, str):
        with pytest.raises(expected):
            from taurus.external.qt import API
    else:
        from taurus.external.qt import API
        assert API == expected
