#ifndef _POOLAPI_H_
#define _POOLAPI_H_

#include <Python.h>
#include <map>
#include <tango.h>
#include <config.h>
#include <pool/DeviceFactory.h>

namespace Pool_ns
{

class Pool;

class PoolUtil
{
public:
	PyObject_HEAD

	int32_t sample_py_attr;
	
private:
	static PoolUtil		*_instance;
	static PyObject		*_pyinstance;
protected:

	Tango::Database 	*db;	

	IDeviceFactory		*factory;
	
	/**
	 * @warning ¡Contructor is not invoked! Should not do any member 
	 *          initialization here!
	 */	
	PoolUtil() {}

	/*
	 * a map of: key = pool element name
	 *           value = corresponding DeviceProxy 
	 */
	typedef std::map<std::string, Tango::DeviceProxy *> DevProxyMap;
	typedef std::map<std::string, PyObject *> PyDevProxyMap;
	
	/**
	 * a map of:   key = controller name
	 *           value = a map of:   key = pool element name
	 *                             value = corresponding DeviceProxy 
	 */
	typedef std::map<std::string, DevProxyMap *> CtrlDevProxyMap; 
	typedef std::map<std::string, PyDevProxyMap *> PyCtrlDevProxyMap;
	
	/**
	 * a map of:   key = controller name
	 *           value = a map of:   key = pool element name (tango device name or alias)
	 *                             value = corresponding DeviceProxy 
	 */
	CtrlDevProxyMap *proxies;
	PyCtrlDevProxyMap *py_proxies;

	/**
	 * a map of:   key = pool element name (tango device name or alias)
	 *           value = device class 
	 */
	typedef std::map<std::string,std::string> DevTypeMap;

	/**
	 * a map of:   key = pool element name (tango device name or alias)
	 *           value = device class 
	 */	
	DevTypeMap *dev_types; 
	
	void remove_element(string &);
	void remove_py_element(string &);
	
	Tango::DeviceProxy *get_device_int(string &, string &);
	Tango::DeviceProxy *get_device_int(string &, string &, const char *);

	PyObject *get_py_device_int(string &, string &);
	PyObject *get_py_device_int(string &, string &, const char *);
	
	string get_device_class(string &);
	
	Tango::Database *get_database();
	
	/**
	 * A small function to convert Pool lib release string to a number
	 */
	int32_t convert_pool_lib_release(const char *);
	
public:
	
	
	static PoolUtil *init(IDeviceFactory *);
	static PyObject *pyinit(PyTypeObject *, IDeviceFactory *);
	
	static PoolUtil *instance();
	static PyObject *pyinstance();
	
	~PoolUtil();
	
	void destruct();
	void clean();
	void clean_ctrl_elems(string &);

	/**
	 * Get the Pool library version number.
	 *
	 * @return The Pool library release number coded in 3 digits
	 * (for instance 010,020,100,110,....)
	 */	
	int32_t get_version();

	/**
	 * Get the Pool library version number.
	 *
	 * @return The Pool library release number coded as X.Y.Z
	 */
	string get_version_str();	
	
	Tango::DeviceProxy *get_device(string &, string &);
	PyObject *get_py_device(string &, string &);
	
	Tango::DeviceProxy *get_motor(string &, string &);
	Tango::DeviceProxy *get_phy_motor(string &, string &);
	Tango::DeviceProxy *get_pseudo_motor(string &, string &);
	Tango::DeviceProxy *get_motor_group(string &, string &);
	Tango::DeviceProxy *get_exp_channel(string &, string &);
	Tango::DeviceProxy *get_ct_channel(string &, string &);
	Tango::DeviceProxy *get_zerod_channel(string &, string &);
	Tango::DeviceProxy *get_oned_channel(string &, string &);
	Tango::DeviceProxy *get_twod_channel(string &, string &);
	Tango::DeviceProxy *get_pseudo_counter_channel(string &, string &);
	Tango::DeviceProxy *get_measurement_group(string &, string &);
	Tango::DeviceProxy *get_com_channel(string &, string &);
	Tango::DeviceProxy *get_ioregister(string &, string &);
    

	PyObject *get_py_motor(string &, string &);
	PyObject *get_py_phy_motor(string &, string &);
	PyObject *get_py_pseudo_motor(string &, string &);
	PyObject *get_py_motor_group(string &, string &);
	PyObject *get_py_exp_channel(string &, string &);
	PyObject *get_py_ct_channel(string &, string &);
	PyObject *get_py_zerod_channel(string &, string &);
	PyObject *get_py_oned_channel(string &, string &);
	PyObject *get_py_twod_channel(string &, string &);
	PyObject *get_py_pseudo_counter_channel(string &, string &);
	PyObject *get_py_measurement_group(string &, string &);
	PyObject *get_py_com_channel(string &, string &);
	PyObject *get_py_ioregister(string &, string &);
    
};

class PyStandaloneDeviceFactory: public IDeviceFactory
{
	PyObject *pDevProxyClass;
	
public:
	PyStandaloneDeviceFactory();
	virtual ~PyStandaloneDeviceFactory();

	virtual Tango::DeviceProxy *get_new_device_proxy(string &name);
	virtual PyObject *get_new_py_device_proxy(string &name);
};

}

#endif /*_POOLAPI_H_*/
