#ifndef _PYCTRLFILE_
#define _PYCTRLFILE_

#include "PyUtils.h"
#include "PyExternalFile.h"
#include <ltdl.h>

namespace Pool_ns
{

#define EXT_ATTR_TYPE_KEY		"Type"
#define EXT_ATTR_RWTYPE_KEY		"R/W Type"
    
class PoolClass;
class Pool;

/**
 * The PyCtrlFile class declaration
 */
class PyCtrlFile:public PyExternalFile 
{
public:
    PyCtrlFile(const string &, const char *);
    PyCtrlFile(PyCtrlFile &, const char *);
    ~PyCtrlFile();
    
    virtual void get_info(const string &, vector<string> &);
    virtual void get_info(const string &, const string &, vector<string> &);
    virtual void get_info_ex(const string &, Tango::DevVarCharArray *);
    virtual void get_info_ex(const string &, const string &, Tango::DevVarCharArray *);
    
    virtual int32_t get_MaxDevice(const string &);
    virtual void get_prop_info(const string &,vector<PropertyData*> &);
    virtual void get_extra_attr_dec(const string &,const char *,vector<PoolExtraAttr> &);
    
    lt_dlhandle get_py_inter_lib_ptr() {return py_inter_lib_ptr;}
            
protected:
    void load_code();
    void load_py_inter_lib(const string &);
    string get_py_inter_lib_name(const string &);
    
    void get_py_elem(const string &,const char *,vector<string> &, const char *dft);
    void get_py_gender(const string &,vector<string> &);
    void get_py_model(const string &,vector<string> &);
    void get_py_image(const string &,vector<string> &);
    void get_py_organization(const string &,vector<string> &);
    void get_py_logo(const string &,vector<string> &);
    void get_py_icon(const string &,vector<string> &);
    
    lt_dlhandle		py_inter_lib_ptr;
    bool			include_MaxDevice;
};


} // End of Pool_ns namespace

#endif /*_EXTERNALFILE_*/
