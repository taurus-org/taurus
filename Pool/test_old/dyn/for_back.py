import PyTango
import sys
import time

class PyCb:
    def __init__(self):
        self.proxy = None
        self.cb_executed = 0
        self.mov_done = 0
	self.strange_state_error = 0
        
    def get_init_value(self):
        da = self.proxy.read_attribute("Position")
        self.init_pos = da.value
                
    def push_event(self,event):
        print "One more event"
        self.cb_executed += 1
#	self.when = time.asctime(time.localtime())
        self.when = time.time()
        if not event.err:
            print self.when,": Event received:",event.attr_name,", value =",event.attr_value.value
            state = event.attr_value.value
	    print "state =",state
            
            if state == PyTango.DevState.ON:
                time.sleep(0.2)
		try:
               	    da = self.proxy.read_attribute("Position")
		except PyTango.DevFailed,e:
		    print "Get an exception while reading the position",e
		    return
                print "Mov number",self.mov_done," (",self.cb_executed,"), arrived at position",da.value,
                if da.value == self.init_pos:
                    da.value += 200.0
                else:
                    da.value -= 200.0
                print ", going to pos",da.value
		try:
                    self.proxy.write_attribute(da)
		except PyTango.DevFailed, e:
		    print "Get an exception while writing the new value",e
                    sys.exit(-1)
            elif state == PyTango.DevState.MOVING:
                self.mov_done += 1            
            else: 
                print "Received a strange state =",state
		self.strange_state_error += 1
		if self.strange_state_error == 3:
                    sys.exit(-1) 
        else:
	    print self.when,"Error flag set in event"
            print event.errors
            sys.exit(-1)  

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print "usage: for_back <motor name>"
        sys.exit(-1)
        
    motor_name = sys.argv[1]
    motor_proxy = PyTango.DeviceProxy(motor_name)
    motor_proxy.set_timeout_millis(20000)
    cb = PyCb()
    cb.proxy = motor_proxy
    cb.get_init_value()
    ev = motor_proxy.subscribe_event("State",PyTango.EventType.CHANGE,cb,[])

# Sleep for one week
    
    time.sleep(604800.0)
    
    
