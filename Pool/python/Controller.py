import sys
import datetime
import logging
import traceback
import PyTango

class ControllerLogHandler(logging.StreamHandler):
    
    def __init__(self):
        logging.StreamHandler.__init__(self)
        self._indent_level = 0
        self._formater = logging.Formatter(self._getFmt(self._indent_level))
        self.setFormatter(self._formater)

    def _getFmt(self,i):
        f = '%(threadName)-12s %(levelname)-8s %(asctime)s %(name)s:'
        f += self._indent_level*'\t' + '%(message)s'
        return f
        
    def incIndent(self):
        self._indent_level += 1
        self._formater._fmt = self._getFmt(self._indent_level)

    def decIndent(self):
        self._indent_level -= 1
        self._formater._fmt = self._getFmt(self._indent_level)

class Controller:
    
    class_prop = {}

    gender = None
    model = None
    organization = None
    image = None
    logo = None
    
    trace = []

    def __init__(self, inst, props):
        self.inst_name = inst
        self._indent_level = 0
        self._log = logging.getLogger("%s.%s" % (str(self.__class__), inst))
        self._log_handler = ControllerLogHandler()
        self._log.addHandler(self._log_handler)
        self._log.setLevel(logging.INFO)
        
        for prop_key in props:
           setattr(self,prop_key,props.get(prop_key))
        
        for method_name in self.trace:
            try:
                setattr(self, method_name, self.wrap(getattr(self,method_name)))
            except:
                pass

    def wrap(self, method):
        def wrapped( *args, **kw):
            msg = "%s%s" % (method.func_name, str(args))
            if len(kw): msg += str(kw)
            smsg = "[START] %s..." % msg
            emsg = "[FINISH] %s" % msg
            self._log.debug(smsg)
            self._log_handler.incIndent()
            ret = None
            try:
                ret = method(*args, **kw)
            except PyTango.DevFailed, df:
                self._log_handler.decIndent()
                self._log.debug(traceback.format_exc())
                de = df[0]
                emsg += " with error: DevFailed (%s) %s" % (de.reason, de.desc)
                self._log.warn(emsg)
                raise df
            except Exception, e:
                self._log_handler.decIndent()
                self._log.debug(traceback.format_exc())
                err = repr(e)
                if len(err) > 80: err = "%s[...]" % err[:75]
                emsg += " with error: %s" % err
                self._log.warn(emsg)
                raise e
            self._log_handler.decIndent()
            if ret:
                emsg += " = %s" % str(ret)
            self._log.debug(emsg)
            return ret
        return wrapped
        