#pragma once

#include "PyUtils.h"
#include "PyCtrlFile.h"

namespace Pool_ns
{

/**
 * The PyUndefCtrlFile class declaration
 */
class PyUndefCtrlFile: public PyCtrlFile
{
public:
    PyUndefCtrlFile(const string &);
    ~PyUndefCtrlFile();

protected:
    virtual void check_py_methods(PyObject *class_obj);
    virtual const char *get_super_class();
};

/**
 * The PyMotCtrlFile class declaration
 */
class PyMotCtrlFile: public PyCtrlFile
{
public:
    PyMotCtrlFile(const string &);
    PyMotCtrlFile(PyUndefCtrlFile &);
    ~PyMotCtrlFile();

protected:
    virtual void check_py_methods(PyObject *class_obj);
    virtual const char *get_super_class();
};

#define CALC_PHYSICAL_METHOD			"calc_physical"
#define CALC_PSEUDO_METHOD				"calc_pseudo"
#define CALC_ALL_PHYSICAL_METHOD		"calc_all_physical"
#define CALC_ALL_PSEUDO_METHOD			"calc_all_pseudo"

#define MOTOR_ROLES_ATTR				"motor_roles"
#define PSEUDO_MOTOR_ROLES_ATTR			"pseudo_motor_roles"

#define COUNTER_ROLES_ATTR				"counter_roles"
#define PSEUDO_COUNTER_ROLES_ATTR		"pseudo_counter_roles"

#define IOREGISTER_PREDEFINED_VALUES_ATTR "predefined_values"

/**
 * The PyPseudoMotCtrlFile class declaration
 */
class PyPseudoMotCtrlFile: public PyCtrlFile
{
public:

    PyPseudoMotCtrlFile(const string &);
    PyPseudoMotCtrlFile(PyUndefCtrlFile &);
    virtual ~PyPseudoMotCtrlFile();

    virtual void get_info(const string &, vector<string> &);
    virtual void get_info(const string &, const string &, vector<string> &);

protected:

    virtual void check_py_methods(PyObject *);
    virtual const char *get_super_class();

    void get_pseudo_info(const string &,vector<string> &);
};

/**
 * The PyCoTiCtrlFile class declaration
 */
class PyCoTiCtrlFile: public PyCtrlFile
{
public:
    PyCoTiCtrlFile(const string &);
    PyCoTiCtrlFile(PyUndefCtrlFile &);
    ~PyCoTiCtrlFile();

protected:
    virtual void check_py_methods(PyObject *class_obj);
    virtual const char *get_super_class();
};

/**
 * The PyZeroDCtrlFile class declaration
 */
class PyZeroDCtrlFile: public PyCtrlFile
{
public:
    PyZeroDCtrlFile(const string &);
    PyZeroDCtrlFile(PyUndefCtrlFile &);
    ~PyZeroDCtrlFile();

protected:
    virtual void check_py_methods(PyObject *class_obj);
    virtual const char *get_super_class();
};

/**
 * The PyOneDCtrlFile class declaration
 */
class PyOneDCtrlFile: public PyCtrlFile 
{
public:
    PyOneDCtrlFile(const string &);
    PyOneDCtrlFile(PyUndefCtrlFile &);
    ~PyOneDCtrlFile();
            
protected:
    virtual void check_py_methods(PyObject *class_obj);
    virtual const char *get_super_class();
};


/**
 * The PyTwoDCtrlFile class declaration
 */
class PyTwoDCtrlFile: public PyCtrlFile 
{
public:
    PyTwoDCtrlFile(const string &);
    PyTwoDCtrlFile(PyUndefCtrlFile &);
    ~PyTwoDCtrlFile();
            
protected:
    virtual void check_py_methods(PyObject *class_obj);
    virtual const char *get_super_class();
};

#define CALC_METHOD			"calc"
#define COUNTER_ROLES_ATTR	"counter_roles"

/**
 * The PyPseudoCoCtrlFile class declaration
 */
class PyPseudoCoCtrlFile: public PyCtrlFile
{
public:
    PyPseudoCoCtrlFile(const string &);
    PyPseudoCoCtrlFile(PyUndefCtrlFile &);
    ~PyPseudoCoCtrlFile();

    virtual void get_info(const string &, vector<string> &);
    virtual void get_info(const string &, const string &, vector<string> &);

protected:

    virtual void check_py_methods(PyObject *);
    virtual const char *get_super_class();

    void get_pseudo_info(const string &, vector<string> &);
};

/**
 * The PyComCtrlFile class declaration
 */
class PyComCtrlFile: public PyCtrlFile
{
public:
    PyComCtrlFile(const string &);
    PyComCtrlFile(PyUndefCtrlFile &);
    ~PyComCtrlFile();

protected:
    virtual void check_py_methods(PyObject *class_obj);
    virtual const char *get_super_class();
};

/**
 * The PyIORegisterCtrlFile class declaration
 */
class PyIORegisterCtrlFile: public PyCtrlFile
{
public:
    PyIORegisterCtrlFile(const string &);
    PyIORegisterCtrlFile(PyUndefCtrlFile &);
    ~PyIORegisterCtrlFile();

    virtual void get_info(const string &, vector<string> &);
    virtual void get_info(const string &, const string &, vector<string> &);

protected:
    virtual void check_py_methods(PyObject *class_obj);
    virtual const char *get_super_class();
    void get_ioregister_info(const string &,vector<string> &);
};

/**
 * The PyConstraintFile class declaration
 */
class PyConstraintFile: public PyCtrlFile
{
public:
    PyConstraintFile(const string &);
    PyConstraintFile(PyUndefCtrlFile &);
    ~PyConstraintFile();

protected:
    virtual void check_py_methods(PyObject *class_obj);
    virtual const char *get_super_class();
};

} // End of Pool_ns namespace
