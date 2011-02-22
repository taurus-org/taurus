
#include <PoolPluginFiCa.h>

namespace Pool_ns
{

//-----------------------------------------------------------------------------
//
//					The PoolPluginFiCa class
//
//-----------------------------------------------------------------------------

//+----------------------------------------------------------------------------
//
// method : 		PoolPluginFiCa::PoolPluginFiCa()
// 
// description : 	constructor for PoolPluginFiCa class
//
// in : - type : The controller file_class name (crtl_class_name/inst name in lowercase letter)
//      - f_name : The controller class file name (cpp lib or python module)
//		- ctrl_class_name : The controller class name (case dependant)
//      - ob_type : the type of controller. Currently allowed only "Motor"
//		- pool_class : Pointer to the PoolClass object
//
//-----------------------------------------------------------------------------

PoolPluginFiCa::PoolPluginFiCa(string &type,string &f_name,string &ctrl_class_name,string &ob_type,PoolClass *pool_class,Pool *dev)
:ExternalFiCa(type,f_name,ctrl_class_name,pool_class,dev)
{
//	cout << "In PoolPluginFiCa ctor" << endl;
	init(type,f_name,ctrl_class_name,ob_type,pool_class,dev);
}


//+----------------------------------------------------------------------------
//
// method : 		PoolPluginFiCa::~PoolPluginFiCa()
// 
// description : 	destructor for PoolPluginFiCa class
//
//-----------------------------------------------------------------------------

PoolPluginFiCa::~PoolPluginFiCa()
{
//	cout << "In the PoolPluginFiCa dtor for " << name << endl;
}

} // namespace