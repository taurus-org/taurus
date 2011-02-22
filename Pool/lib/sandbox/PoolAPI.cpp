#include <pool/PoolAPI.h>

namespace Pool_ns
{
	
PoolUtil *PoolUtil::_instance = NULL;
PyObject *PoolUtil::_pyinstance = NULL;

PoolUtil *PoolUtil::instance()
{
	if (_instance == NULL)
	{
		Tango::Except::throw_exception(
				(const char*)"Pool_PoolUtilSingletonNotCreated",
				(const char*)"Util singleton not created",
				(const char*)"PoolUtil::instance");
	}		
	return _instance;
}

PoolUtil::~PoolUtil()
{
	destruct();
}

Tango::Database *
PoolUtil::get_database()
{
	if(db == NULL)
		db = new Tango::Database();
	return db;
}

void PoolUtil::destruct()
{
	clean();
	if(proxies != NULL) delete proxies; proxies = NULL;
	if(py_proxies != NULL) delete py_proxies; py_proxies = NULL;
	if(dev_types != NULL) delete dev_types; dev_types = NULL;
	if(db != NULL) delete db; db = NULL;
	PoolUtil::_instance = NULL;
	PoolUtil::_pyinstance = NULL;
}

void PoolUtil::clean()
{
	CtrlDevProxyMap::iterator ite1 = proxies->begin();
	for(;ite1 != proxies->end(); ite1++)
	{
		DevProxyMap::iterator ite2 = ite1->second->begin();
		for(; ite2 != ite1->second->end(); ite2++)
		{
			delete ite2->second;	
		}
		delete ite1->second;
	}
	
	PyCtrlDevProxyMap::iterator py_ite1 = py_proxies->begin();
	for(;py_ite1 != py_proxies->end(); py_ite1++)
	{
		PyDevProxyMap::iterator py_ite2 = py_ite1->second->begin();
		for(; py_ite2 != py_ite1->second->end(); py_ite2++)
		{
			Py_DECREF(py_ite2->second);	
		}
		delete py_ite1->second;
	}
}

void PoolUtil::clean_ctrl_elems(string &ctrl_name)
{
	CtrlDevProxyMap::iterator ite1 = proxies->find(ctrl_name);
	
	// If C++ controller
	if(ite1 != proxies->end())
	{
		DevProxyMap::iterator ite2 = ite1->second->begin();
		for(; ite2 != ite1->second->end(); ite2++)
		{
			delete ite2->second;
		}
		delete ite1->second;
		proxies->erase(ite1);
	}
	// If Python controller
	else 
	{
		PyCtrlDevProxyMap::iterator ite1 = py_proxies->find(ctrl_name);
		if(ite1 != py_proxies->end())
		{
			PyDevProxyMap::iterator ite2 = ite1->second->begin();
			for(; ite2 != ite1->second->end(); ite2++)
			{
				Py_DECREF(ite2->second);	
			}
			delete ite1->second;
			py_proxies->erase(ite1);
		}
	}
}

void PoolUtil::remove_element(string &name)
{
	CtrlDevProxyMap::iterator ite1 = proxies->begin();
	for(; ite1 != proxies->end(); ite1++)
	{
		DevProxyMap::iterator ite2 = ite1->second->find(name); 
		if(ite2 != ite1->second->end())
		{
			delete ite2->second;
			ite1->second->erase(ite2);
			break;	
		}	
	}
	
	//Don't remove from the dev_types because this map is shared between the
	//C++ and Python APIs. 
	//dev_types->erase(name);
}

int32_t PoolUtil::get_version()
{
	return convert_pool_lib_release(PACKAGE_VERSION);
}

int32_t PoolUtil::convert_pool_lib_release(const char *vers_str)
{
	int32_t ret;
	
	TangoSys_MemStream str;
	string::size_type pos;
	string vers(vers_str);
	
	pos = vers.find('.');
	if (pos == string::npos)
		return -1;
	vers.erase(pos,1);
	
	pos = vers.find('.');
	if (pos == string::npos)
		return -1;
	vers.erase(pos,1);
	
	str << vers << ends;
	if (!(str >> ret))
		ret = -1;
		
	return ret;
}

string PoolUtil::get_version_str()
{
	return string(PACKAGE_VERSION);
}

Tango::DeviceProxy *PoolUtil::get_device_int(string &ctrl_name, string &name)
{
	CtrlDevProxyMap::iterator ite1 = proxies->find(ctrl_name);

	Tango::DeviceProxy *ret = NULL;

	DevProxyMap *proxy_map = NULL;

	// If controller is already registered
	if(ite1 != proxies->end())
	{
		DevProxyMap::iterator ite2 = ite1->second->find(name);
		
		// if the device is already registered for the controller 
		if(ite2 != ite1->second->end())
		{
			ret = ite2->second;
		}
		else
		{
			proxy_map = ite1->second;
		}
	}
	// Register the controller
	else
	{
		proxy_map = new DevProxyMap;
		proxies->insert(make_pair(ctrl_name,proxy_map));
	}
	
	/* If new device to be added */
	if(proxy_map != NULL)
	{
		ret = factory->get_new_device_proxy(name);
		if(ret != NULL)
		{
			proxy_map->insert(make_pair(name,ret));
			dev_types->insert(make_pair(name,ret->info().dev_class));
		}
	}
	
	return ret;
}

Tango::DeviceProxy *PoolUtil::get_device_int(string &ctrl_name, string &name, const char *type)
{
	string name_lower(name);
	transform(name_lower.begin(),name_lower.end(),
			  name_lower.begin(),::tolower);

	Tango::DeviceProxy *ret = get_device_int(ctrl_name, name_lower);

	DevTypeMap::iterator it = dev_types->find(name_lower);	 
	
	if(it->second != type)
	{
		remove_element(name_lower);
		ret = NULL;
	}
	
	return ret;	
}

Tango::DeviceProxy *PoolUtil::get_device(string &ctrl_name, string &name)
{
	string name_lower(name);
	transform(name_lower.begin(),name_lower.end(),
			  name_lower.begin(),::tolower);
	return get_device_int(ctrl_name, name_lower);
}

Tango::DeviceProxy *PoolUtil::get_motor(string &ctrl_name, string &motor_name)
{
	Tango::DeviceProxy *ret = get_phy_motor(ctrl_name, motor_name);
	
	if(ret == NULL)
		ret = get_pseudo_motor(ctrl_name, motor_name);
		
	return ret;	
}

Tango::DeviceProxy *PoolUtil::get_phy_motor(string &ctrl_name, string &motor_name)
{
	return get_device_int(ctrl_name, motor_name, "Motor");
}

Tango::DeviceProxy *PoolUtil::get_pseudo_motor(string &ctrl_name, string &pseudo_motor_name)
{
	return get_device_int(ctrl_name, pseudo_motor_name, "PseudoMotor");
}

Tango::DeviceProxy *PoolUtil::get_motor_group(string &ctrl_name, string &motor_group_name)
{
	return get_device_int(ctrl_name, motor_group_name, "MotorGroup");
}

Tango::DeviceProxy *PoolUtil::get_exp_channel(string &ctrl_name, string &exp_channel_name)
{
	Tango::DeviceProxy *ret = get_ct_channel(ctrl_name, exp_channel_name);
	
	if(ret == NULL)
		ret = get_zerod_channel(ctrl_name, exp_channel_name);

	if(ret == NULL)
		ret = get_oned_channel(ctrl_name, exp_channel_name);

	if(ret == NULL)
		ret = get_twod_channel(ctrl_name, exp_channel_name);
		
	if(ret == NULL)
		ret = get_pseudo_counter_channel(ctrl_name, exp_channel_name);

	return ret;	
}

Tango::DeviceProxy *PoolUtil::get_ct_channel(string &ctrl_name, string &exp_channel_name)
{
	return get_device_int(ctrl_name, exp_channel_name, "CTExpChannel");	
}

Tango::DeviceProxy *PoolUtil::get_zerod_channel(string &ctrl_name, string &exp_channel_name)
{
	return get_device_int(ctrl_name, exp_channel_name, "ZeroDExpChannel");	
}

Tango::DeviceProxy *PoolUtil::get_oned_channel(string &ctrl_name, string &exp_channel_name)
{
	return get_device_int(ctrl_name, exp_channel_name, "OneDExpChannel");	
}

Tango::DeviceProxy *PoolUtil::get_twod_channel(string &ctrl_name, string &exp_channel_name)
{
	return get_device_int(ctrl_name, exp_channel_name, "TwoDExpChannel");	
}

Tango::DeviceProxy *PoolUtil::get_pseudo_counter_channel(string &ctrl_name, string &exp_channel_name)
{
	return get_device_int(ctrl_name, exp_channel_name, "PseudoCounter");	
}

Tango::DeviceProxy *PoolUtil::get_measurement_group(string &ctrl_name, string &mnt_grp_name)
{
	return get_device_int(ctrl_name, mnt_grp_name, "MeasurementGroup");	
}

Tango::DeviceProxy *PoolUtil::get_com_channel(string &ctrl_name, string &com_channel_name)
{
	return get_device_int(ctrl_name, com_channel_name, "CommunicationChannel");	
}

Tango::DeviceProxy *PoolUtil::get_ioregister(string &ctrl_name, string &ioregister_name)
{
	return get_device_int(ctrl_name, ioregister_name, "IORegister");	
}
}
