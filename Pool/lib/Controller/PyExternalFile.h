#ifndef _PYEXTERNALFILE_
#define _PYEXTERNALFILE_

#include "PyUtils.h"
#include "CPoolDefs.h"
#include "CtrlFile.h"
#include <tango.h>

namespace Pool_ns
{

class DevicePool;

#define CLASS_PROP_ATTR		"class_prop"

#define INST_NAME_ATTR		"inst_name"

#define TYPE_KEY		"Type"
#define DESCR_KEY		"Description"
#define DFT_VALUE_KEY		"DefaultValue"

/**
 * The PyExternalFile class declaration
 */
class PyExternalFile:public CtrlFile
{
public:
    PyExternalFile(const string &);
    PyExternalFile(PyExternalFile &);
    ~PyExternalFile();

    int32_t get_classes(vector<string>&,vector<string> &);
    void get_prop_info(const string &, vector<PropertyData*> &);
    
    virtual void get_prop_info(PyObject *, vector<string> &);
    virtual void get_prop_info(PyObject *, vector<PropertyData*> &);
    
    void append_sequence_value(const string &,const char *,vector<string> &);
    void get_sequence_value(const string &,const char *,vector<string> &);
    
    void check_py(const char *);
    void reload();
    PyObject *get_py_module() {return module;}
    void check_py_method(PyObject *,const char *);
    
    void get_py_doc(const string &,vector<string> &);
    
    bool reload_allowed(const string &);
    
protected:
    virtual void check_py_methods(PyObject *class_obj) = 0;
    virtual const char *get_super_class() = 0;
    
    PyObject *load_py_module(const string &);
    void update_py_path();
    
    void throw_dev_failed_from_py();
    void Py_init_dev_error(PyObject *,PyObject *,PyObject *,Tango::DevErrorList &);
    
    PyObject *get_py_class(const char *);
    void check_py_class(PyObject *, PyObject *);

    PyObject *get_py_valid_class(const char *);	
    void check_py(PyObject *);
    
    PyObject            *module;
    bool                mod_dec_ref;
};


} // End of Pool_ns namespace

#endif /*_EXTERNALFILE_*/
