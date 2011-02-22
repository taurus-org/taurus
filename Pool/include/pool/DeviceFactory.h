#ifndef _DEVICEFACTORY_H_
#define _DEVICEFACTORY_H_

#include <Python.h>
#include <tango.h>

namespace Pool_ns 
{

class IDeviceFactory
{
public:
	virtual ~IDeviceFactory() {}
	virtual Tango::DeviceProxy *get_new_device_proxy(string &name) = 0;
	virtual PyObject *get_new_py_device_proxy(string &name) = 0;
};

}

#endif /*_DEVICEFACTORY_H_*/
