import sys
import pkg_resources
from types import ModuleType
from taurus.core.util.lazymodule import LazyModule


def test_lazy_import_entry_point():
    modname = "foobartest"
    pkg_name = "taurus.core.util.test"
    ep = list(pkg_resources.iter_entry_points('taurus.foobartest'))[0]
    print(ep)

    LazyModule.import_ep(modname, pkg_name, ep)

    # check that creating the LazyModule does not have side-efects
    import taurus.core.util.test
    assert modname not in sys.modules

    # import the module and check that it is a LazyModule
    import taurus.core.util.test.foobartest as lzm
    assert isinstance(lzm, LazyModule)

    # ask for a member of the lazy module
    assert lzm.foo == 1

    # ...and check that any future import of lzm will import "real" module,
    # not the lazy one

    import taurus.core.util.test.foobartest as lzm
    assert not isinstance(lzm, LazyModule)
    assert isinstance(lzm, ModuleType)
