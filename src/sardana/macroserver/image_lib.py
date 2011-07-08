import numpy
import PyTango

try:
    import EdfFile
    EDF = 1
except:
    EDF = 0

FROM_TANGO_TO_NUMPY_TYPE = {
   PyTango.DevBoolean : numpy.bool8,
   PyTango.DevUChar : numpy.ubyte,
   PyTango.DevShort : numpy.short,
   PyTango.DevUShort : numpy.ushort,
   PyTango.DevLong : numpy.int32,
   PyTango.DevULong : numpy.uint32,
   PyTango.DevLong64 : numpy.int64,
   PyTango.DevULong64 : numpy.uint64,
   PyTango.DevString : numpy.str,
   PyTango.DevDouble : numpy.float64,
   PyTango.DevFloat : numpy.float32,
}

class Img:
    def __init__(self, channel):
        self.name = channel.getName().lower()
        self.img_channel = channel
        self.img_src = self.img_channel.read_attribute("AttributeName").value
        self.img_dev_name, sep, self.img_attr_name = self.img_src.rpartition("/")
        self.img_dev = PyTango.DeviceProxy(self.img_dev_name)
        self.img_attr_cfg = self.img_dev.get_attribute_config_ex([self.img_attr_name])[0]
        self.data = None
        self.enabled = False
        self.path = None

    def get_data(self,cache=False):
        if cache and not self.data is None:
            return self.data
        self.data = self.img_dev.read_attribute_as_str(self.img_attr_name)
        if not self.data is None:
            self.data = numpy.ndarray(buffer=self.data.value, 
                                      shape=(self.data.dim_y,self.data.dim_x),
                                      dtype=FROM_TANGO_TO_NUMPY_TYPE[self.img_attr_cfg.data_type])
        return self.data

    def save_data_as_edf(self, header, filename, cache=False):
        if not self.enabled:
            return
        data = self.get_data(cache=cache)
        edf_file = EdfFile.EdfFile(filename)
        edf_file.WriteImage(header, data)        
        