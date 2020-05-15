import sys
from types import ModuleType
from taurus.core.util.lazymodule import LazyModule

from pkg_resources import EntryPoint, Requirement, WorkingSet


def test_LazyModule():

    # create an entry point for taurus.core.util.test.dumm
    w = WorkingSet()
    d = w.find(Requirement.parse('taurus'))
    ep = EntryPoint.parse("dummy_mod = taurus.core.util.test.dummy", dist=d)
    modname = ep.name

    # lazy load the ep module as taurus.fbt
    LazyModule.import_ep(modname, "taurus", ep)

    # check that lazy-loading did not import the entry point modules
    assert modname not in sys.modules
    assert ep.module_name not in sys.modules

    # import the module and check that it is a LazyModule
    import taurus.dummy_mod as lzm
    assert isinstance(lzm, LazyModule)

    # same again
    import taurus.dummy_mod as lzm
    assert isinstance(lzm, LazyModule)

    # now access a member of the lazy module
    assert lzm.foo == 1

    # ...and check that any subsequent import will return a "real" module,
    # not a lazy one

    import taurus.dummy_mod as lzm
    assert not isinstance(lzm, LazyModule)
    assert isinstance(lzm, ModuleType)
