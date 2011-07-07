
from taurus.core.tango.sardana.pool import AbortException

class MacroServerException(Exception):
    
    def __init__(self, *args):
        Exception.__init__(self, *args)
        if args:
            a1 = args[0]
            if isinstance(a1, dict):
                self.msg = a1.get("message", a1.get("msg", None))
                self.traceback = a1.get("traceback", a1.get("tb", None))
                self.type = a1.get("type", self.__class__.__name__) 
            else:
                self.msg = str(a1)
                self.traceback = None
                self.type = self.__class__.__name__

    def __str__(self):
        return "%s: %s" % (self.type, self.msg)


class MacroServerExceptionList(MacroServerException):
    def __init__(self, *args):
        MacroServerException.__init__(self, *args)
        self.exceptions = args[0]


class MissingEnv(MacroServerException):
    pass


class UnknownEnv(MacroServerException):
    pass


class UnknownMacro(MacroServerException):
    pass


class UnknownLib(MacroServerException):
    pass


class MacroWrongParameterType(MacroServerException):
    pass


class LibError(MacroServerException):
    pass
