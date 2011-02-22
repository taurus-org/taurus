#ifndef _POOLFACTORY_H_
#define _POOLFACTORY_H_

#include <pool/DeviceFactory.h>
#include <devapi.h>

namespace Pool_ns
{

class DefaultDeviceFactory: public IDeviceFactory
{
protected:
	PyObject *pDevProxyClass;
	
public:
	DefaultDeviceFactory();	
	virtual ~DefaultDeviceFactory();

	virtual Tango::DeviceProxy *get_new_device_proxy(string &name);
	virtual PyObject *get_new_py_device_proxy(string &name);
};

class LoggingDeviceFactory: public DefaultDeviceFactory
{
public:
	LoggingDeviceFactory();	
	virtual ~LoggingDeviceFactory();

	virtual Tango::DeviceProxy *get_new_device_proxy(string &name);
	virtual PyObject *get_new_py_device_proxy(string &name);
};

class LoggingDeviceProxy: public Tango::DeviceProxy
{
public:
        LoggingDeviceProxy(string &name, CORBA::ORB *orb=NULL): DeviceProxy(name,orb) {}
	LoggingDeviceProxy(const char *name, CORBA::ORB *orb=NULL): DeviceProxy(name,orb) {}
	
	 Tango::DeviceData command_inout(string &name);

	 Tango::DeviceData command_inout(const char *co) {
	     string str(co);return command_inout(str);}

	 Tango::DeviceData command_inout(string &str, Tango::DeviceData &data);
	 
	 Tango::DeviceData command_inout(const char *co, Tango::DeviceData &data);
};



}
#endif /*_POOLFACTORY_H_*/
