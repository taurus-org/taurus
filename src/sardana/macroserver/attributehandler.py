import logging, threading, weakref
import operator, types

import taurus.core.util
        
class AttributeLogHandler(logging.Handler):
    
    def __init__(self, dev, attr_name, level=logging.NOTSET, max_buff_size=0):
        logging.Handler.__init__(self, level)
        self._attr_name = attr_name
        self._level = level
        self._max_buff_size = max_buff_size
        self._dev = weakref.ref(dev)
        
        dev.set_change_event(attr_name, True, False)
        attr_list = dev.get_device_attr()
        attr = attr_list.get_attr_by_name(attr_name)
        attr.set_value([])

        self._buff = taurus.core.util.LIFO(max_buff_size)

    def emit(self, record):
        output = self.getRecordMessage(record)
        self.appendBuffer(output)
        self.sendText(output)

    def getRecordMessage(self, record):
        return record.getMessage().split('\n')
    
    def sendText(self, output):
        self._dev().push_change_event(self._attr_name, output)
            
    def read(self, attr):
        """Read from the buffer and assign to the attribute value"""
        attr.set_value(self._buff.getCopy())
    
    def clearBuffer(self):
        self._buff.clear()
        
    def appendBuffer(self, d):
        if operator.isSequenceType(d):
            if type(d) in types.StringTypes:
                self._buff.append(d)
            else:
                self._buff.extend(d)
        else:
            self._buff.append(str(d))
    
    def sync(self):
        pass
    
    def finish(self):
        pass
    
AttributeBufferedLogHandler = AttributeLogHandler