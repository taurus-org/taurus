#ifndef CPPCTRLFILE_H_
#define CPPCTRLFILE_H_

#include "CtrlFile.h"
#include <tango.h>
#include <ltdl.h>

namespace Pool_ns
{

class PoolClass;
class Pool;

/**
 * @brief The CtrlFile class declaration
 */
class CppCtrlFile : public CtrlFile
{
public:
    CppCtrlFile(const std::string &, const char *);
    CppCtrlFile(CppCtrlFile &, const char *);
    ~CppCtrlFile();

    virtual int32_t get_classes(vector<string> &,vector<string> &);	
    
    virtual void get_info(const std::string &, vector<string> &);
    virtual void get_info(const std::string &, const std::string &, vector<string> &);
    
    virtual void get_info_ex(const std::string &, Tango::DevVarCharArray *);
    virtual void get_info_ex(const std::string &, const std::string &, Tango::DevVarCharArray *);
    
    virtual void get_prop_info(const std::string &, vector<PropertyData*> &);

    lt_dlhandle get_lib_ptr() {return lib_ptr;}
    
    void reload();
    
    virtual int32_t get_MaxDevice(const std::string &);
    
    virtual void get_sequence_value(const std::string &,const char *,vector<string> &);
    virtual void get_extra_attr_dec(const std::string &,const char *,vector<PoolExtraAttr> &);

protected:
    virtual void load_code();
    void get_cpp_elem(const std::string &,const char *,vector<string> &, const char *dft="");
    void get_cpp_doc(const std::string &,vector<string> &);
    void get_cpp_gender(const std::string &,vector<string> &);
    void get_cpp_model(const std::string &,vector<string> &);
    void get_cpp_image(const std::string &,vector<string> &);
    void get_cpp_organization(const std::string &,vector<string> &);
    void get_cpp_logo(const std::string &,vector<string> &);
    void get_cpp_icon(const std::string &,vector<string> &);
    
    bool get_cpp_str_array(const std::string &,const char *,vector<string> &);
    
    virtual void get_particular_info(const std::string &, vector<string> &) {}
    virtual void get_particular_info(const std::string &, const std::string &, vector<string> &) {}
    
    /** a handler to the library */
    lt_dlhandle			lib_ptr;
    bool				close_lib;
    bool				include_MaxDevice;
};

typedef vector<CppCtrlFile *>::iterator v_cpp_ctrl_ite;

} // End of Pool_ns namespace

#endif /*CTRLFILE_H_*/
