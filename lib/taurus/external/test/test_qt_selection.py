import os
import sys
import importlib
import pytest
from taurus import tauruscustomsettings as ts


@pytest.mark.parametrize(
    "qt_api, default_qt_api, installed, imported, expected",
    [
        # no explicit selection, all bindings installed
        ("", "", "all", None, "pyqt5"),
        (None, "", "all", None, "pyqt5"),
        # no explicit selection, only one binding installed
        (None, "", "PyQt5", None, "pyqt5"),
        (None, "", "PyQt4", None, "pyqt"),
        (None, "", "PySide2", None, "pyside2"),
        (None, "", "PySide", None, "pyside"),
        # no explicit selection, with default selection, all installed
        (None, "pyqt5", "all", None, "pyqt5"),
        (None, "pyqt", "all", None, "pyqt"),
        (None, "pyqt4", "all", None, "pyqt"),
        (None, "pyside2", "all", None, "pyside2"),
        (None, "pyside", "all", None, "pyside"),
        # explicit selection, all bindings installed
        ("pyqt5", "", "all", None, "pyqt5"),
        ("pyqt", "", "all", None, "pyqt"),
        ("pyqt4", "", "all", None, "pyqt"),
        ("pyside2", "", "all", None, "pyside2"),
        ("pyside", "", "all", None, "pyside"),
        ("pyqt5", "pyqt4", "all", None, "pyqt5"),
        ("pyqt", "pyqt5", "all", None, "pyqt"),
        ("pyqt4", "pyqt5", "all", None, "pyqt"),
        # unsupported selection
        ("unsupported_binding", "", "all", None, ImportError),
        (None, "unsupported_binding", "all", None, ImportError),
        ("pyqt5", "", "none", None, ImportError),
        ("pyqt5", "", "PyQt4", None, ImportError),
        ("pyqt", "", "PyQt5", None, ImportError),
        ("pyside2", "", "PySide", None, ImportError),
        ("pyside", "", "PySide2", None, ImportError),
        # previously imported binding
        (None, "", "all", ("PyQt5",), "pyqt5"),
        (None, "", "all", ("PyQt4",), "pyqt"),
        (None, "", "all", ("PySide2",), "pyside2"),
        (None, "", "all", ("PySide",), "pyside"),
        (None, "", "all", ("PySide.QtCore",), "pyside"),
        (None, "", "all", (".QtCore", "PyQt4"), "pyqt"),
        ("pyqt5", "pyqt4", "all", ("PySide2",), "pyside2"),
    ],
)
@pytest.mark.forked  # run in separate process to avoid side-effects
def test_qt_select(
    monkeypatch, qt_api, default_qt_api, installed, imported, expected
):
    """Check that the selection of Qt binding by taurus.external.qt works"""
    # temporarily remove qt bindings from sys.modules
    monkeypatch.delitem(sys.modules, "taurus.external.qt", raising=False)
    for binding in "PyQt5", "PyQt4", "PySide2", "PySide":
        monkeypatch.delitem(sys.modules, binding, raising=False)
        monkeypatch.delitem(sys.modules, binding + ".QtCore", raising=False)
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
    monkeypatch.setenv("AVAILABLE_QT_MOCKS", installed)
    # emulate an already-imported binding
    if imported is not None:
        importlib.import_module(*imported)
    # Now that the environment is clean and ready, test the shim
    if not isinstance(expected, str):
        with pytest.raises(expected):
            from taurus.external.qt import API
    else:
        from taurus.external.qt import API

        assert API == expected
