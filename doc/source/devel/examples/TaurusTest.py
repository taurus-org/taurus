from __future__ import print_function
import PyTango
import sys
import math


class TaurusTest(PyTango.Device_4Impl):

    def __init__(self, cl, name):
        PyTango.Device_4Impl.__init__(self, cl, name)
        TaurusTest.init_device(self)

    def delete_device(self):
        print("[Device delete_device method] for device", self.get_name())

    def init_device(self):
        print("In ", self.get_name(), "::init_device()")
        self.set_state(PyTango.DevState.ON)
        self.get_device_properties(self.get_device_class())
        self._position = 50.0
        self._velocity = 20.0
        self._acceleration = 4.0
        self._simulation_mode = False
        self._abscissas = [x / 50.0 for x in range(1024)]
        self._curve = [math.sin(x) for x in self._abscissas]

    def always_executed_hook(self):
        print("In ", self.get_name(), "::always_excuted_hook()")

    def read_attr_hardware(self, data):
        print("In ", self.get_name(), "::read_attr_hardware()")

    def read_Position(self, attr):
        attr.set_value(self._position)

    def write_Position(self, attr):
        self._position = attr.get_write_value()

    def read_Velocity(self, attr):
        attr.set_value(self._velocity)

    def is_Velocity_allowed(self, req_type):
        if req_type == PyTango.AttReqType.WRITE_REQ:
            return True
        return self._velocity < 5

    def write_Velocity(self, attr):
        self._velocity = attr.get_write_value()

    def read_Acceleration(self, attr):
        attr.set_value(self._acceleration)

    def write_Acceleration(self, attr):
        self._acceleration = attr.get_write_value()

    def read_SimulationMode(self, attr):
        attr.set_value(self._simulation_mode)

    def write_SimulationMode(self, attr):
        self._simulation_mode = attr.get_write_value()

    def read_Abscissas(self, attr):
        attr.set_value(self._abscissas)

    def read_Curve(self, attr):
        attr.set_value(self._curve)

    def write_Curve(self, attr):
        self._curve = attr.get_write_value()

    def create_device_cb(self, device_name):
        print("About to create device", device_name)

    def CreateTaurusTestDevice(self, device_name):
        klass = self.get_device_class()
        klass.create_device(device_name, cb=self.create_device_cb)

    def DeleteTaurusTestDevice(self, device_name):
        klass = self.get_device_class()
        klass.delete_device(device_name)


class TaurusTestClass(PyTango.DeviceClass):

    #    Class Properties
    class_property_list = {
    }

    #    Device Properties
    device_property_list = {
    }

    #    Command definitions
    cmd_list = {
        'CreateTaurusTestDevice':
            [[PyTango.DevString, 'device name'],
             [PyTango.DevVoid, ""]],
        'DeleteTaurusTestDevice':
            [[PyTango.DevString, 'device name'],
             [PyTango.DevVoid, ""]],
    }

    #    Attribute definitions
    attr_list = {
        'Position':
            [[PyTango.DevDouble,
              PyTango.SCALAR,
              PyTango.READ_WRITE],
             {
                'label': "Gap",
                'unit': "mm",
                'format': "%8.3f",
                'max value': 1000,
                'min value': -1000,
                'max alarm': 900,
                'min alarm': -900,
                'max warning': 800,
                'min warning': -800,
            }],
        'Velocity':
            [[PyTango.DevDouble,
              PyTango.SCALAR,
              PyTango.READ_WRITE],
             {
                'label': "Speed",
                'unit': "nm/s",
                'format': "%6.2f",
                'max value': 100,
                'min value': 0,
                'max alarm': 95,
                'min alarm': 5,
                'max warning': 90,
                'min warning': 10,
            }],
        'Acceleration':
            [[PyTango.DevDouble,
              PyTango.SCALAR,
              PyTango.READ_WRITE],
             {
                'label': "Acceleration",
                'unit': "nm/s/s",
                'format': "%6.2f",
                'max value': 100,
                'min value': 0,
                'max alarm': 95,
                'min alarm': 2,
                'max warning': 90,
                'min warning': 1,
            }],
        'SimulationMode':
            [[PyTango.DevBoolean,
              PyTango.SCALAR,
              PyTango.READ_WRITE],
             {
                'label': "Simulation mode",
            }],
        'Abscissas':
            [[PyTango.DevDouble,
              PyTango.SPECTRUM,
              PyTango.READ, 1024],
             {
                'label': "X values for Curve 1",
            }],
        'Curve':
            [[PyTango.DevDouble,
              PyTango.SPECTRUM,
              PyTango.READ_WRITE, 1024],
             {
                'label': "Curve 1",
            }],

    }

    def __init__(self, name):
        PyTango.DeviceClass.__init__(self, name)
        self.set_type(name)
        print("In TaurusTestClass  constructor")


if __name__ == '__main__':
    try:
        py = PyTango.Util(sys.argv)
        py.add_TgClass(TaurusTestClass, TaurusTest, 'TaurusTest')

        U = PyTango.Util.instance()
        U.server_init()
        U.server_run()

    except PyTango.DevFailed as e:
        print('-------> Received a DevFailed exception:', e)
    except Exception as e:
        print('-------> An unforeseen exception occured....', e)
