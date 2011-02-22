#include "ExternalFile.h"
#include "Pool.h"

namespace Pool_ns
{

ExternalFile::ExternalFile(const std::string& f_name)
:Tango::LogAdapter(Pool::get_pool_instance()), full_name(f_name)
{
//	cout << "In the ExternalFile ctor" << endl;

    std::string::size_type pos = f_name.rfind("/");
    if (pos != std::string::npos)
    {
        path = f_name.substr(0, pos);
        name = f_name.substr(pos + 1);
    }
    else
    {
        name = f_name;
    }
        
    lang = get_language(name);
    
    name_lower = name;
    transform(name_lower.begin(),name_lower.end(),name_lower.begin(),::tolower);
    name_lower.erase(name_lower.find('.'));
}

//+----------------------------------------------------------------------------
//
// method : 		ExternalFile::~ExternalFile()
// 
// description : 	destructor for ExternalFile class
//
//-----------------------------------------------------------------------------

ExternalFile::~ExternalFile()
{
//	cout << "In the ExternalFile dtor" << endl;
}

//+----------------------------------------------------------------------------
//
// method : 		ExternalFile::get_language(string &f_name)
// 
// description : 	Determines the language of the binary file based on its  
//                  extension.
// in : - f_name : The class file name (cpp lib or python module)
//
//-----------------------------------------------------------------------------
Language ExternalFile::get_language(const std::string &f_name)
{
    Language language;
    std::string::size_type pos;
    
    if ((pos = f_name.find(".py")) != string::npos)
        language = PYTHON;
    else
        language = CPP;
    
    return language;
}

}
