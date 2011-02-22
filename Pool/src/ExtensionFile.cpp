#include <ExtensionFile.h>

namespace Pool_ns
{

//+----------------------------------------------------------------------------
//
// method : 		ExtensionFile::ExtensionFile()
// 
// description : 	constructor for ExtensionFile class
//
// in : - f_name : The class file name (cpp lib or python module)
//		- class_name : The class name (case dependant)
//		- pool_class : Pointer to the PoolClass object
//
//-----------------------------------------------------------------------------

ExtensionFile::ExtensionFile(string &f_name,PoolClass *pool_class,Pool *dev)
:ExternalFile(f_name,pool_class,dev)
{
//	cout << "In the ExtensionFile ctor" << endl;
}

//+----------------------------------------------------------------------------
//
// method : 		ExtensionFile::~ExtensionFile()
// 
// description : 	destructor for ExtensionFile class
//
//-----------------------------------------------------------------------------

ExtensionFile::~ExtensionFile()
{
//	cout << "In the ExtensionFile dtor" << endl;
}

void ExtensionFile::load_code()
{
	
}


} // namespace
