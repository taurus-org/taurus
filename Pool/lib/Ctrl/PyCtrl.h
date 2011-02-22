#ifndef _PYCTRL_H
#define _PYCTRL_H

#include "PyUtils.h"
#include <tango.h>
#include <pool/Ctrl.h>

/**
 * The Python controller base class
 */
class PyController
{
public:

    /** 
     * Constructor
     */
    PyController();
    
    /** 
     * Constructor
     * 
     * @param cl_name [in] python class name
     * @param module [in] the python module.
     */
    PyController(const std::string &, PyObject *);

    /// Destructor
    virtual ~PyController();

    /**
     * Gets the controller python object
     * 
     * @return a pointer to the controller python object
     */
    PyObject *get_ctrl_py_obj() {return py_obj;}

protected:

    /** the controller python object */ 
    PyObject	*py_obj;

    /** the python module */
    PyObject 	*mod;
    
    /** the class name for this controller */
    string		py_class_name;
    
    /** 
     * Set to <code>true</code> when the python controller implements 
     * 'PreStateAll' method
     */
    bool		pre_state_all;

    /** 
     * Set to <code>true</code> when the python controller implements 
     * 'PreStateOne' method
     */
    bool		pre_state_one;

    /** 
     * Set to <code>true</code> when the python controller implements 
     * 'StateAll' method
     */

    bool		state_all;
            
    /** 
     * Set to <code>true</code> when the python controller implements 
     * 'GetExtraAttribute' method
     */
    bool		get_extra_attribute;

    /** 
     * Set to <code>true</code> when the python controller implements 
     * 'SetExtraAttribute' method
     */
    bool		set_extra_attribute;

    /** 
     * Set to <code>true</code> when the python controller implements 
     * 'SendToCtrl' method
     */
    bool		send_to_ctrl;

    /**
     * Gets the controller instance name
     * 
     * @return the controller instance name
     */
    std::string get_name();

    /**
     * This method generates a Tango DevError from a Python exception.
     *
     * @param[in] exec_ptr  The python exception type pbject
     * @param[in] value_ptr The ipython exception value object
     * @param[in] tb_ptr    The python exception traceback object
     * @param[in] dev_err   Reference to the DevError list used by the Tango
     *                      exception. This list is supposed to have at least 
     *                      a size of 1 
     */
    void Py_init_dev_error(PyObject *,PyObject *,PyObject *,Tango::DevErrorList &);

    /**
     * Check if a Python method throws an exception for method returning void
     * data type. In case the method returned an exception, translate it to a 
     * Tango exception
     * 
     * @param[in] res  The method return value
     * @param[in] mesg The Tango exception message
     * @param[in] met  The name of the checked method
     */
    void check_void_return(PyObject *,const char *,const char *);

    /**
     * Throws a tango exception
     * 
     * @param[in] mesg The Tango exception message
     * @param[in] met  The name of the checked method
     */
    void throw_simple_exception(const char *,const char *);

    /**
     * Check which pre-defined methods are implemented in this controller and 
     * set the method flag according to the check result. It is not ncesseray 
     * to check for
     *  - GetState()
     *  - ReadOne()
     * because the pool refuses to load controller code if these methods are not
     * defined
     * 
     * @param[in] obj The python controller object
     */
    void base_check_existing_methods(PyObject *);

    /**
     * Clear all the boolean flags used to memorize which pre-defined method 
     * are implemented in this controller
     */
    void base_clear_method_flag();

    /**
     * Call the controller SetExtraAttributePar method when the input value is 
     * a boolean. There is no way to do this with a simple call to the 
     * PyObject_CallMethod() function of the Python C API. Boolean type is not 
     * supported in the data type
     *
     * @param[in] obj      The python controller object
     * @param[in] axis     The axis number within the controller
     * @param[in] par_name The extra attribute name
     * @param[in] val      The new value
     */
    PyObject *PySetExtraAttributeBool(PyObject *,long,string &,bool);

    /**
     * Helper method to get a double value from a python object.
     * Returns <code>false</code> if the given python object is not a valid 
     * number.
     * 
     * @param[in]  py_ptr the python object to be converted
     * @param[out] number the double which will contain the python value
     */
    bool get_py_number(PyObject *, double &);

    /**
     * Helper method to get a boolean value from a python object.
     * Returns <code>false</code> if the given python object is not a valid
     * boolean.
     * 
     * @param[in]  py_ptr the python object to be converted
     * @param[out] b      the boolean which will contain the python value
     */
    bool get_py_bool(PyObject *, bool &);
    
    /**
     * @brief StateOne.
     * 
     * @param idx         [in] device index (starts with 1).
     * @param ctrl_state [out] pointer to the state object that will contain the
     *                         controller state.  
     */
    void _StateOne(int32_t, Controller::CtrlState *);

};

#endif /* _PYCTRL_H */
