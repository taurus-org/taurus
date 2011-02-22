#include <pool/PoolAPI.h>
#include "structmember.h"

namespace Pool_ns
{

/*******************************************************************************
 * 
 * Standalone device factory stuff
 * 
 ******************************************************************************/

PyStandaloneDeviceFactory::PyStandaloneDeviceFactory()
{
    pDevProxyClass = NULL;	
}

PyStandaloneDeviceFactory::~PyStandaloneDeviceFactory()
{
    Py_XDECREF(pDevProxyClass);
}

Tango::DeviceProxy *PyStandaloneDeviceFactory::get_new_device_proxy(string &name)
{
    return NULL;
}

PyObject *PyStandaloneDeviceFactory::get_new_py_device_proxy(string &name)
{
    PyObject *pInstance;
    if(pDevProxyClass == NULL)
    {
        PyObject *pModDict = PyImport_GetModuleDict();
        
        PyObject *pModName = PyString_FromString("PyTango");
        
        PyObject *pModule;
        bool new_module = false;
        if(PyDict_Contains(pModDict,pModName) == 1)
        {
            pModule = PyImport_AddModule("PyTango");
        }
        else
        {
            pModule = PyImport_ImportModule("PyTango");
            new_module = pModule != NULL;	
        }
        
        Py_DECREF(pModName);
        
        if(pModule != NULL)
        {
            // pDict is borrowed
            PyObject *pDict = PyModule_GetDict(pModule);
            
            pDevProxyClass = PyDict_GetItemString(pDict, "DeviceProxy");

            if (pDevProxyClass == NULL || !PyCallable_Check(pDevProxyClass))
            {
                //Do something?
            }
        }
        else
        {
            //TODO manage case for not knowing PyTango
            // Maybe throw a python exception	
        }
    }

    if(pDevProxyClass != NULL)
    {
        // Create an instance of the class
        PyObject *param = Py_BuildValue("(s)",name.c_str());
        pInstance = PyObject_CallObject(pDevProxyClass, param);
        Py_DECREF(param);
        if(pInstance == NULL)
            pInstance = Py_BuildValue("");
    }
    else
    {
        pInstance = Py_BuildValue("");
    }	
    return pInstance;
}


/*******************************************************************************
 * 
 * pool module stuff
 * 
 ******************************************************************************/

static char *pool_doc = (char *)"The Sardana Device Pool interface.";

/** Structure for global functions */
static PyMethodDef pool_methods[] = {
    {NULL}  /* Sentinel */
};

/*******************************************************************************
 * 
 * pool.PoolUtil Stuff
 * 
 ******************************************************************************/

static void PoolUtil_dealloc(PoolUtil *self)
{
    self->destruct();
    self->ob_type->tp_free((PyObject*)self);
}

// @deprecated 
static int PoolUtil_init(PyObject *self, PyObject *args, PyObject *kwds)
{
    /*
    if (self != NULL) 
    {
        PoolUtil *util = (PoolUtil*)self;
        //TODO: Init python members here 
    }
    */
    return 0;
}

static PyObject *PoolUtil_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    PyObject *pyself;
    PoolUtil *self;

    try
    {
        pyself = PoolUtil::pyinstance();
        Py_INCREF(pyself);
    }
    catch(Tango::DevFailed &e)
    {
        pyself = PoolUtil::pyinit(type, NULL);
        if (pyself != NULL) 
        {
            //TODO: Init python members here
            self = (PoolUtil*)pyself; 
        }
    }
    return pyself;
}

PyObject *PoolUtil_get_version(PoolUtil *self)
{
    return PyInt_FromLong(static_cast<long>(self->get_version()));
}

PyObject *PoolUtil_get_version_str(PoolUtil *self)
{
    return PyString_FromString(self->get_version_str().c_str());
}

/** 
 * Method wrapper for PoolUtil.get_device
 */
PyObject *PoolUtil_get_device(PoolUtil *self, PyObject *args)
{
    char *controller_name;
    char *device_name;
    
    if(!PyArg_ParseTuple(args,"ss",&controller_name,&device_name))
        return NULL;
    
    string ctrl_name(controller_name);
    string dev_name(device_name);

    return self->get_py_device(ctrl_name,dev_name);
}

PyObject *PoolUtil_get_motor(PoolUtil *self, PyObject *args)
{
    char *controller_name;
    char *device_name;
    
    if(!PyArg_ParseTuple(args,"ss",&controller_name,&device_name))
        return NULL;	
    
    string ctrl_name(controller_name);
    string dev_name(device_name);
    return self->get_py_motor(ctrl_name,dev_name);
}

PyObject *PoolUtil_get_phy_motor(PoolUtil *self, PyObject *args)
{
    char *controller_name;
    char *device_name;
    
    if(!PyArg_ParseTuple(args,"ss",&controller_name,&device_name))
        return NULL;	
    
    string ctrl_name(controller_name);
    string dev_name(device_name);
    return self->get_py_phy_motor(ctrl_name,dev_name);
}

PyObject *PoolUtil_get_pseudo_motor(PoolUtil *self, PyObject *args)
{
    char *controller_name;
    char *device_name;
    
    if(!PyArg_ParseTuple(args,"ss",&controller_name,&device_name))
        return NULL;	
    
    string ctrl_name(controller_name);
    string dev_name(device_name);
    return self->get_py_pseudo_motor(ctrl_name,dev_name);
}

PyObject *PoolUtil_get_motor_group(PoolUtil *self, PyObject *args)
{
    char *controller_name;
    char *device_name;
    
    if(!PyArg_ParseTuple(args,"ss",&controller_name,&device_name))
        return NULL;	
    
    string ctrl_name(controller_name);
    string dev_name(device_name);
    return self->get_py_motor_group(ctrl_name,dev_name);
}

PyObject *PoolUtil_get_exp_channel(PoolUtil *self, PyObject *args)
{
    char *controller_name;
    char *device_name;
    
    if(!PyArg_ParseTuple(args,"ss",&controller_name,&device_name))
        return NULL;	
    
    string ctrl_name(controller_name);
    string dev_name(device_name);
    return self->get_py_exp_channel(ctrl_name,dev_name);
}

PyObject *PoolUtil_get_ct_channel(PoolUtil *self, PyObject *args)
{
    char *controller_name;
    char *device_name;
    
    if(!PyArg_ParseTuple(args,"ss",&controller_name,&device_name))
        return NULL;	
    
    string ctrl_name(controller_name);
    string dev_name(device_name);
    return self->get_py_ct_channel(ctrl_name,dev_name);
}

PyObject *PoolUtil_get_zerod_channel(PoolUtil *self, PyObject *args)
{
    char *controller_name;
    char *device_name;
    
    if(!PyArg_ParseTuple(args,"ss",&controller_name,&device_name))
        return NULL;	
    
    string ctrl_name(controller_name);
    string dev_name(device_name);
    return self->get_py_zerod_channel(ctrl_name,dev_name);
}

PyObject *PoolUtil_get_oned_channel(PoolUtil *self, PyObject *args)
{
    char *controller_name;
    char *device_name;
    
    if(!PyArg_ParseTuple(args,"ss",&controller_name,&device_name))
        return NULL;	
    
    string ctrl_name(controller_name);
    string dev_name(device_name);
    return self->get_py_oned_channel(ctrl_name,dev_name);
}

PyObject *PoolUtil_get_twod_channel(PoolUtil *self, PyObject *args)
{
    char *controller_name;
    char *device_name;
    
    if(!PyArg_ParseTuple(args,"ss",&controller_name,&device_name))
        return NULL;	
    
    string ctrl_name(controller_name);
    string dev_name(device_name);
    return self->get_py_twod_channel(ctrl_name,dev_name);
}

PyObject *PoolUtil_get_pseudo_counter_channel(PoolUtil *self, PyObject *args)
{
    char *controller_name;
    char *device_name;
    
    if(!PyArg_ParseTuple(args,"ss",&controller_name,&device_name))
        return NULL;	
    
    string ctrl_name(controller_name);
    string dev_name(device_name);
    return self->get_py_pseudo_counter_channel(ctrl_name,dev_name);
}

PyObject *PoolUtil_get_measurement_group(PoolUtil *self, PyObject *args)
{
    char *controller_name;
    char *device_name;
    
    if(!PyArg_ParseTuple(args,"ss",&controller_name,&device_name))
        return NULL;	
    
    string ctrl_name(controller_name);
    string dev_name(device_name);
    return self->get_py_measurement_group(ctrl_name,dev_name);
}

PyObject *PoolUtil_get_com_channel(PoolUtil *self, PyObject *args)
{
    char *controller_name;
    char *device_name;
    
    if(!PyArg_ParseTuple(args,"ss",&controller_name,&device_name))
        return NULL;	
    
    string ctrl_name(controller_name);
    string dev_name(device_name);
    return self->get_py_com_channel(ctrl_name,dev_name);
}

PyObject *PoolUtil_get_ioregister(PoolUtil *self, PyObject *args)
{
    char *controller_name;
    char *device_name;
    
    if(!PyArg_ParseTuple(args,"ss",&controller_name,&device_name))
        return NULL;	
    
    string ctrl_name(controller_name);
    string dev_name(device_name);
    return self->get_py_ioregister(ctrl_name,dev_name);
}
/** 
 * Structure for PoolUtil exported methods 
 */
static PyMethodDef PoolUtil_methods[] = {
    { "get_version", (PyCFunction)PoolUtil_get_version, METH_NOARGS, "Get The pool library release number coded in 3 digits" },
    { "get_version_str", (PyCFunction)PoolUtil_get_version_str, METH_NOARGS, "Get The pool library release string coded as 'X.Y.Z'" },
    { "get_device", (PyCFunction)PoolUtil_get_device, METH_VARARGS, "Returns a PyTango.DeviceProxy object" },
    { "get_motor", (PyCFunction)PoolUtil_get_motor, METH_VARARGS, "Returns a PyTango.DeviceProxy for a motor inside the Pool" },
    { "get_phy_motor", (PyCFunction)PoolUtil_get_phy_motor, METH_VARARGS, "Returns a PyTango.DeviceProxy for a physical motor inside the Pool" },
    { "get_pseudo_motor", (PyCFunction)PoolUtil_get_pseudo_motor, METH_VARARGS, "Returns a PyTango.DeviceProxy for a pseudo motor inside the Pool" },
    { "get_motor_group", (PyCFunction)PoolUtil_get_motor_group, METH_VARARGS, "Returns a PyTango.DeviceProxy for a motor group inside the Pool" },
    { "get_exp_channel", (PyCFunction)PoolUtil_get_exp_channel, METH_VARARGS, "Returns a PyTango.DeviceProxy for an experiment channel inside the Pool" },
    { "get_ct_channel", (PyCFunction)PoolUtil_get_exp_channel, METH_VARARGS, "Returns a PyTango.DeviceProxy for a counter/timer channel inside the Pool" },
    { "get_zerod_channel", (PyCFunction)PoolUtil_get_exp_channel, METH_VARARGS, "Returns a PyTango.DeviceProxy for a 0D experiment channel inside the Pool" },
    { "get_oned_channel", (PyCFunction)PoolUtil_get_exp_channel, METH_VARARGS, "Returns a PyTango.DeviceProxy for a 1D experiment channel inside the Pool" },
    { "get_twod_channel", (PyCFunction)PoolUtil_get_exp_channel, METH_VARARGS, "Returns a PyTango.DeviceProxy for a 2D experiment channel inside the Pool" },
    { "get_pseudo_counter_channel", (PyCFunction)PoolUtil_get_pseudo_counter_channel, METH_VARARGS, "Returns a PyTango.DeviceProxy for a pseudo couter experiment channel inside the Pool" },
    { "get_measurement_group", (PyCFunction)PoolUtil_get_measurement_group, METH_VARARGS, "Returns a PyTango.DeviceProxy for a measurement group inside the Pool" },
    { "get_com_channel", (PyCFunction)PoolUtil_get_com_channel, METH_VARARGS, "Returns a PyTango.DeviceProxy for a CommunicationChannel inside the Pool" },
    { "get_ioregister", (PyCFunction)PoolUtil_get_ioregister, METH_VARARGS, "Returns a PyTango.DeviceProxy for a IORegister inside the Pool" },
    {NULL}  /* Sentinel */
};

/** 
 * Structure for PoolUtil exported members 
 */
static PyMemberDef PoolUtil_members[] = {
    { (char *)"version", T_INT, 
      offsetof(PoolUtil,sample_py_attr), 
      READONLY, 
      (char *)"The PoolUtil version" },	
      {NULL}  /* Sentinel */
};


static const char *PoolUtil_doc = "The Sardana Device Pool Util interface.";


static PyTypeObject PoolUtilType = {
    PyObject_HEAD_INIT(NULL)
    0,                           /*ob_size*/
    "pool.PoolUtil",             /*tp_name*/
    sizeof(PoolUtil),            /*tp_basicsize*/
    0,                           /*tp_itemsize*/
    (destructor)PoolUtil_dealloc,/*tp_dealloc*/
    0,                           /*tp_print*/
    0,                           /*tp_getattr*/
    0,                           /*tp_setattr*/
    0,                           /*tp_compare*/
    0,                           /*tp_repr*/
    0,                           /*tp_as_number*/
    0,                           /*tp_as_sequence*/
    0,                           /*tp_as_mapping*/
    0,                           /*tp_hash */
    0,                           /*tp_call*/
    0,                           /*tp_str*/
    0,                           /*tp_getattro*/
    0,                           /*tp_setattro*/
    0,                           /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT,          /*tp_flags*/
#if PY_VERSION_HEX < 0x02050000
    (char*)PoolUtil_doc,         /* tp_doc */
#else    
    PoolUtil_doc,                /* tp_doc */
#endif
    0,                           /* tp_traverse */
    0,                           /* tp_clear */
    0,                           /* tp_richcompare */
    0,                           /* tp_weaklistoffset */
    0,                           /* tp_iter */
    0,                           /* tp_iternext */
    PoolUtil_methods,            /* tp_methods */
    PoolUtil_members,            /* tp_members */
    0,                           /* tp_getset */
    0,                           /* tp_base */
    0,                           /* tp_dict */
    0,                           /* tp_descr_get */
    0,                           /* tp_descr_set */
    0,                           /* tp_dictoffset */
    PoolUtil_init,               /* tp_init */
    PyType_GenericAlloc,         /* tp_alloc */
    PoolUtil_new,                /* tp_new */    
};

#ifndef PyMODINIT_FUNC	/* declarations for DLL import/export */
#define PyMODINIT_FUNC void
#endif

PyMODINIT_FUNC
initpool(void) 
{
    PyObject* m;

    if (PyType_Ready(&PoolUtilType) < 0)
        return;

    m = Py_InitModule3("pool", pool_methods, pool_doc);

    Py_INCREF(&PoolUtilType);
    PyModule_AddObject(m, "PoolUtil", (PyObject *)&PoolUtilType);
}

/*******************************************************************************
 * 
 * PoolUtil Stuff related to Python
 * 
 ******************************************************************************/

PyObject *PoolUtil::pyinstance()
{
    if (_pyinstance == NULL)
    {
        Tango::Except::throw_exception(
                (const char*)"Pool_PoolUtilSingletonNotCreated",
                (const char*)"Util singleton not created",
                (const char*)"PoolUtil::instance");
    }		
    return _pyinstance;
}

PyObject *PoolUtil::pyinit(PyTypeObject *type, IDeviceFactory *f)
{
    if(_pyinstance == NULL)
    {
        _pyinstance = type->tp_alloc(type, 0);
        
        PoolUtil *self = (PoolUtil*)_pyinstance;
        
        if(f != NULL)
            self->factory = f;
        else
            self->factory = new PyStandaloneDeviceFactory;

        self->db = NULL;
        self->proxies = new CtrlDevProxyMap;
        self->py_proxies = new PyCtrlDevProxyMap;
        self->dev_types = new DevTypeMap;
    }
    return _pyinstance;
}

PoolUtil *PoolUtil::init(IDeviceFactory *f)
{
    if (_instance == NULL)
    {
        PyObject *pModDict = PyImport_GetModuleDict();
        
        PyObject *pModName = PyString_FromString("pool");
        PyObject *pModule = NULL;
        int res = PyDict_Contains(pModDict,pModName); 
        if(res == 1)
            pModule = PyImport_AddModule("pool");
        else if(res == 0)
            pModule = PyImport_ImportModule("pool");
        else if(res == -1)
        {
            PyErr_Clear();
            Tango::Except::throw_exception(
                    (const char *)"Pool_PythonError",
                    (const char *)"Unexpected python error",
                    (const char *)"PoolAPI::init()");
        }
        
        Py_DECREF(pModName);
        
        PyObject *pyself = NULL;
        if(pModule != NULL)
        {
            // pDict is borrowed
            PyObject *pDict = PyModule_GetDict(pModule);
            
            // pPoolUtilClass is borrowed
            PyObject *pPoolUtilClass = PyDict_GetItemString(pDict, "PoolUtil");

            if (pPoolUtilClass == NULL || !PyCallable_Check(pPoolUtilClass))
            {
                PyErr_Clear();
                TangoSys_OMemStream o;
                o << "Essencial python class 'pool.PoolUtil' could not be found.";
                o << "\nMake sure the directory were pool.la is located";
                o << " is in your PYTHONPATH and LD_LIBRARY_PATH"<<ends;

                Tango::Except::throw_exception(
                    (const char *)"Pool_CantCreatePythonPoolUtilClass",o.str(),
                    (const char *)"PoolAPI::init()");
                
            }
            else
            {
                pyself = PyObject_CallObject(pPoolUtilClass,NULL);
            }

            _instance = (PoolUtil*)pyself;
            _instance->factory = f;

        }
        else 
        {
            PyErr_Clear();
            TangoSys_OMemStream o;
            o << "Essencial python module 'pool' could not be imported.";
            o << "\nMake sure the directory were pool.la is located";
            o << " is in your PYTHONPATH and LD_LIBRARY_PATH"<<ends;

            Tango::Except::throw_exception(
                    (const char *)"Pool_CantImportPythonModule",o.str(),
                    (const char *)"PoolAPI::init()");
        }
    }		
    return _instance;	
}

void PoolUtil::remove_py_element(string &name)
{
    PyCtrlDevProxyMap::iterator ite1 = py_proxies->begin();
    for(; ite1 != py_proxies->end(); ite1++)
    {
        PyDevProxyMap::iterator ite2 = ite1->second->find(name); 
        if(ite2 != ite1->second->end())
        {
            Py_DECREF(ite2->second);
            ite1->second->erase(ite2);
            break;	
        }	
    }
    
    //Don't remove from the dev_types because this map is shared between the
    //C++ and Python APIs. 
    //dev_types->erase(name);
}


PyObject *PoolUtil::get_py_device_int(string &ctrl_name, string &name)
{
    PyCtrlDevProxyMap::iterator ite1 = py_proxies->find(ctrl_name);

    PyObject *ret = NULL;

    PyDevProxyMap *proxy_map = NULL;

    // If controller is already registered
    if(ite1 != py_proxies->end())
    {
        PyDevProxyMap::iterator ite2 = ite1->second->find(name);
        
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
        proxy_map = new PyDevProxyMap;
        py_proxies->insert(make_pair(ctrl_name,proxy_map));
    }
    
    /* If new device to be added */
    if(proxy_map != NULL)
    {
        ret = factory->get_new_py_device_proxy(name);
        if(ret != NULL && ret != Py_None)
        {
            string device_class = "";
            bool class_known  = false;
            
            PyObject *py_meth_name = PyString_FromString("info");
            PyObject *device_info = 
                PyObject_CallMethodObjArgs(ret,py_meth_name,NULL);
            
            if(device_info == NULL)
            {
                PyErr_Clear();
//
// Possibly the device is not exported. Let's try a Database query instead
//				
                try
                {
                    Tango::Database *database = get_database();
                    
//
// The method get_class_for_device does not accept device alias as parameter so
// do the necessary steps to make sure we have the complete device name
//
                    string dev_name;
                    if(name.find('/') == std::string::npos)
                        database->get_device_alias(name,dev_name);
                    else
                        dev_name = name;
                    
                    device_class = database->get_class_for_device(dev_name);
                    class_known = true;
                }
                catch(Tango::DevFailed &e) {}
            }
            else 
            {
                PyObject *py_dev_class_str = 
                    PyObject_GetAttrString(device_info,"dev_class");
                if(py_dev_class_str == NULL)
                {
                    PyErr_Clear();
                }
                else
                {
                    device_class = PyString_AsString(py_dev_class_str);
                    Py_DECREF(py_dev_class_str);
                    class_known = true;
                }
                Py_DECREF(device_info);
            }
            Py_DECREF(py_meth_name);
            
            proxy_map->insert(make_pair(name,ret));
            
            if(class_known)
                dev_types->insert(make_pair(name,device_class));
        }
    }
    
    if(ret != NULL && ret != Py_None) 
        Py_INCREF(ret);
    
    return ret;
}

PyObject *PoolUtil::get_py_device_int(string &ctrl_name, string &name, const char *type)
{
    
    string name_lower(name);
    transform(name_lower.begin(),name_lower.end(),name_lower.begin(),::tolower);

    PyObject *ret = get_py_device_int(ctrl_name, name_lower);
    
    if(ret != Py_None)
    {
        DevTypeMap::iterator it = dev_types->find(name_lower);	 
        
        if(it == dev_types->end() || it->second != type)
        {
            remove_py_element(name_lower);
            ret = Py_BuildValue("");
        }
    }
    
    return ret;	
}

PyObject *PoolUtil::get_py_device(string &ctrl_name, string &name)
{
    string name_lower(name);
    transform(name_lower.begin(),name_lower.end(),name_lower.begin(),::tolower);
    return get_py_device_int(ctrl_name, name_lower);
}

PyObject *PoolUtil::get_py_motor(string &ctrl_name, string &motor_name)
{
    PyObject *ret = get_py_phy_motor(ctrl_name, motor_name);
    
    if(ret == Py_None)
        ret = get_py_pseudo_motor(ctrl_name, motor_name);

    return ret;	
}

PyObject *PoolUtil::get_py_phy_motor(string &ctrl_name, string &motor_name)
{
    return get_py_device_int(ctrl_name, motor_name, "Motor");
}

PyObject *PoolUtil::get_py_pseudo_motor(string &ctrl_name, string &pseudo_motor_name)
{
    return get_py_device_int(ctrl_name, pseudo_motor_name, "PseudoMotor");
}

PyObject *PoolUtil::get_py_motor_group(string &ctrl_name, string &motor_group_name)
{
    return get_py_device_int(ctrl_name, motor_group_name, "MotorGroup");
}

PyObject *PoolUtil::get_py_exp_channel(string &ctrl_name, string &exp_channel_name)
{
    PyObject *ret = get_py_ct_channel(ctrl_name, exp_channel_name);
    
    if(ret == Py_None)
        ret = get_py_zerod_channel(ctrl_name, exp_channel_name);
        
    if(ret == Py_None)
        ret = get_py_oned_channel(ctrl_name, exp_channel_name);
        
    if(ret == Py_None)
        ret = get_py_twod_channel(ctrl_name, exp_channel_name);

    if(ret == Py_None)
        ret = get_py_pseudo_counter_channel(ctrl_name, exp_channel_name);

    return ret;	
}

PyObject *PoolUtil::get_py_ct_channel(string &ctrl_name, string &exp_channel_name)
{
    return get_py_device_int(ctrl_name, exp_channel_name, "CTExpChannel");	
}

PyObject *PoolUtil::get_py_zerod_channel(string &ctrl_name, string &exp_channel_name)
{
    return get_py_device_int(ctrl_name, exp_channel_name, "ZeroDExpChannel");	
}

PyObject *PoolUtil::get_py_oned_channel(string &ctrl_name, string &exp_channel_name)
{
    return get_py_device_int(ctrl_name, exp_channel_name, "OneDExpChannel");	
}

PyObject *PoolUtil::get_py_twod_channel(string &ctrl_name, string &exp_channel_name)
{
    return get_py_device_int(ctrl_name, exp_channel_name, "TwoDExpChannel");	
}

PyObject *PoolUtil::get_py_pseudo_counter_channel(string &ctrl_name, string &exp_channel_name)
{
    return get_py_device_int(ctrl_name, exp_channel_name, "PseudoCounter");	
}

PyObject *PoolUtil::get_py_measurement_group(string &ctrl_name, string &mnt_grp_name)
{
    return get_py_device_int(ctrl_name, mnt_grp_name, "MeasurementGroup");	
}

PyObject *PoolUtil::get_py_com_channel(string &ctrl_name, string &com_channel_name)
{
    return get_py_device_int(ctrl_name, com_channel_name, "CommunicationChannel");	
}

PyObject *PoolUtil::get_py_ioregister(string &ctrl_name, string &ioregister_name)
{
    return get_py_device_int(ctrl_name, ioregister_name, "IORegister");	
}

}
