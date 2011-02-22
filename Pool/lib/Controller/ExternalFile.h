#ifndef _EXTERNALFILE_
#define _EXTERNALFILE_

#include "PyUtils.h"
#include "CPoolDefs.h"
#include <tango.h>

namespace Pool_ns
{

/**
 * The ExternalFile class declaration
 */
class ExternalFile : public Tango::LogAdapter
{
public:
    ExternalFile(const std::string &);
    virtual ~ExternalFile();
    
    inline std::string& get_name() 
    { return name; }
    
    inline std::string& get_name_lower() 
    { return name_lower; }
    
    inline std::string& get_full_name() 
    { return full_name; }
    
    Language get_language() 
    { return lang; }
    
    static Language get_language(const std::string &);
    
    inline std::string& get_path() 
    { return path; }
            
protected:
    virtual void load_code() = 0;
    
    Language            lang;
    string              name;               ///< filename
    string              name_lower;         ///< filename in lower case
    string              path;               ///< absolute path
    string              full_name;          ///< absolute path + filename
};

typedef vector<ExternalFile *>::iterator vef_ite;

} // End of Pool_ns namespace

#endif /*_EXTERNALFILE_*/
