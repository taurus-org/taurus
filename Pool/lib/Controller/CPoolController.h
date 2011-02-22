#ifndef _CPOOL_CONTROLLER_H_
#define _CPOOL_CONTROLLER_H_

#include "CtrlFiCa.h"
#include "CPoolElement.h"
#include <pool/Ctrl.h>

namespace Pool_ns 
{

/**
 * Controller object
 */
struct ControllerPool: public PoolElement
{
    /** pointer to the controller */
    Controller *                           controller;

    /** pointer to the list of controller properties */
    std::vector<Controller::Properties>    *cpp_ctrl_prop;

    /**
     * <code>true</code> if the ctrl class has been built or <code>false</code>
     * otherwise
     */
    bool                                   ctrl_class_built;

    /** the Controller class reference */
    std::vector<CtrlFiCa *>::iterator      ite_ctrl_class;

    /** controller class name */
    std::string                            ctrl_class_name;

    /** <file name without extension lowecase>/<class name lowecase> */
    std::string                            full_ctrl_class_name;

    /** maximum number of devices */
    int32_t                                MaxDevice;

    /** current number of devices */
    int32_t                                nb_dev;

    /** current error description */
    std::string                            error_status;

    /// Constructor
    ControllerPool():
    PoolElement(), controller(NULL), cpp_ctrl_prop(NULL), 
    MaxDevice(CTRL_MAXDEVICE_NOTDEF), nb_dev(0) 
    { ctrl = this; }

    ~ControllerPool();
    
    inline void set_controller(Controller *controller)
    { this->controller = controller; }

    /**
     * Gets a reference to the controller object
     *
     * @return a reference to the controller object
     */
    inline virtual Controller *get_controller()
    { return controller; }

    /**
     * Obtains a pointer to the CtrlFile
     * @return the CtrlFile pointer
     */
    inline CtrlFile *get_ctrl_file_ptr()
    { return (*ite_ctrl_class)->get_ctrl_file(); }

    /**
     * Obtains a reference to the CtrlFile
     * @return the CtrlFile reference
     */
    inline CtrlFile &get_ctrl_file()
    { return *get_ctrl_file_ptr(); }

    /**
     * Obtains a reference to the monitor
     * @return the PoolLock reference
     */
    inline PoolLock &get_ctrl_class_mon() 
    { return (*ite_ctrl_class)->get_mon(); }

    /**
     * Gets the controller type
     * @return the controller type
     */
    inline CtrlType get_ctrl_obj_type()
    { return (*ite_ctrl_class)->get_obj_type(); }

    /**
     * Obtains class name
     * @return a reference to the class name
     */
    inline std::string &get_class_name()
    { return (*ite_ctrl_class)->get_name(); }

    /**
     * Gets the controller language
     * @return the controller language
     */
    inline Language get_language()
    { return (*ite_ctrl_class)->get_language(); }

    /**
     * Gets the file name
     * @return a reference to the file name
     */
    inline std::string &get_f_name()
    { return get_ctrl_file_ptr()->get_name(); }

    /**
     * Gets the absolute path name
     * @return a reference to the absolute path name
     */
    inline std::string &get_path()
    { return get_ctrl_file_ptr()->get_path(); }

    /**
     * Obtains the library handler
     * @return the controller library handler
     */
    inline lt_dlhandle get_lib_ptr()
    { return (*ite_ctrl_class)->get_lib_ptr(); }

    /**
     * Obtains the intermediate python library handler (if applicable)
     * @return the intermediate python library handler
     */
    inline lt_dlhandle get_py_inter_lib_ptr()
    { return (*ite_ctrl_class)->get_py_inter_lib_ptr(); }

    /**
     * Obtains the python module object (if applicable)
     * @return the python module object
     */
    inline PyObject *get_py_module()
    { return (*ite_ctrl_class)->get_py_module(); }

    /**
     * Reloads the controller code
     */
    inline void reload()
    { get_ctrl_file().reload(); }

    /**
     * Returns the type of element this object represents.
     * @see ElementType
     *
     * @return This element type
     */
    virtual ElementType get_type()
    { return CTRL_ELEM; }

    /**
     * IPoolElementListener interface implementation. Called when an event
     * occurs.
     *
     * @param[in] evt stack of event data elements.
     */
    virtual void pool_elem_changed(PoolElemEventList &);
};

}

#endif //_CPOOL_CONTROLLER_H_
