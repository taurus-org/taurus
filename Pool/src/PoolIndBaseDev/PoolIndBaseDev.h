//=============================================================================
//
// file :        PoolIndBaseDev.h
//
// description : Include for the PoolIndBaseDev class.
//
// project :	Sardana Device Pool
//
// $Author$
//
// $Revision$
//
// $Log$
// Revision 1.1  2007/08/17 13:10:09  tcoutinho
// - pseudo motor restructure
// - pool base dev class restructure
// - initial commit for pseudo counters
//
// Revision 1.8  2007/05/25 12:48:10  tcoutinho
// fix the same dead locks found on motor system to the acquisition system since release labeled for Josep Ribas
//
// Revision 1.7  2007/05/22 13:43:09  tcoutinho
// - added new method
//
// Revision 1.6  2007/02/28 16:22:21  tcoutinho
// - added get_alias method
//
// Revision 1.5  2007/02/22 12:03:04  tcoutinho
// - additional "get extra attribute"  needed by the measurement group
//
// Revision 1.4  2007/02/08 07:55:54  etaurel
// - Changes after compilation -Wall. Handle case of different ctrl for the
// same class of device but with same extra attribute name
//
// Revision 1.3  2007/01/30 15:57:41  etaurel
// - Add a missing data member init
// - Add code to manage case with different controller of the same Tango class
// with extra attribute of the same name but with different data type
//
// Revision 1.2  2007/01/26 08:34:32  etaurel
// - We now have a first release of ZeroDController
//
// Revision 1.1  2007/01/16 14:22:25  etaurel
// - Initial revision
//
//
//
// copyleft :   CELLS/ALBA
//		Edifici Ciences Nord
//		Campus Universitari de Bellaterra
//		Universitat Autonoma de Barcelona
//		08193 Bellaterra, Barcelona, SPAIN
//
//=============================================================================

#pragma once

#define		MAX_EXTRA_ATTRIBUTES		128

#include "PoolBaseDev.h"

class Controller;

/**
 * @author	$Author$
 * @version	$Revision$
 */

namespace Pool_ns
{
    
class Pool;
class CtrlFiCa;
class ControllerPool;
struct SinglePoolElement;

/**
 * A generic individual Device for the Pool
 */
class PoolIndBaseDev: public PoolBaseDev
{
public:
    /** 
     * Constructor
     * 
     * @param cl the pointer to the DeviceClasss
     * @param s the name
     */ 
    PoolIndBaseDev(Tango::DeviceClass *cl,string &s);

    /** 
     * Constructor
     * 
     * @param cl the pointer to the DeviceClasss
     * @param s the name
     */ 
    PoolIndBaseDev(Tango::DeviceClass *cl,const char *s);
    
    /** 
     * Constructor
     * 
     * @param cl the pointer to the DeviceClasss
     * @param s the name
     * @param d
     */ 	
    PoolIndBaseDev(Tango::DeviceClass *cl, const char *c,const char *d);
    
    /// Destructor
    virtual ~PoolIndBaseDev() {}

    /**
     *    Extract real attribute values for SimulationMode acquisition result.
     */
    virtual void read_SimulationMode(Tango::Attribute &attr);
    
    /**
     *    Write SimulationMode attribute.
     */
    virtual void write_SimulationMode(Tango::WAttribute &attr);

    /**
     *    Read/Write allowed for SimulationMode attribute.
     */
    virtual bool is_SimulationMode_allowed(Tango::AttReqType type);

    /**
     *    Extract real attribute values for instrument.
     */
    virtual void read_Instrument(Tango::Attribute &attr);
    
    /**
     *    Write instrument attribute.
     */
    virtual void write_Instrument(Tango::WAttribute &attr);

    /**
     *    Read/Write allowed for instrument attribute.
     */
    virtual bool is_Instrument_allowed(Tango::AttReqType type);
    
    /**
     * Get a reference to the pool element
     *
     * @return a reference to the pool element
     */
    SinglePoolElement &get_single_pool_element();
    
    /**
     * Determines if the AddDevice was successfully done or not
     *
     * @return true if the AddDevice was successfully done or false otherwise
     */
    bool is_add_device_done();
    
    /**
     * Returns if the controller is built
     * @return <code>true</code> if controller is built or
     *         <code>false</code> otherwise
     */
    inline bool is_fica_built()                 { return fica_built; }
    
    /**
     * Sets the controller for this element
     * @param[in] ptr controller pointer
     */
    inline void set_ctrl(Controller *ptr)
    { /*my_ctrl = ptr;*/ fica_built = ptr != NULL; }

    /**
     * Gets the controller
     * @return pointer to the controller
     */
    Controller *get_controller();
    
    /**
     * Gets the controller ID for this element
     * @return the controller ID for this element
     */
    inline ElementId get_ctrl_id()              { return ctrl_id; }

    inline ElementId get_instrument_id()        { return instrument_id; }
    
    /**
     * Gets the axis in the controller for this element
     * @return the controller axis for this element
     */
    inline int32_t get_axis()                   { return axis; }
    
    /**
     * Gets the controller FiCa
     * @return pointer to the controller FiCa
     */
    inline CtrlFiCa *get_fica_ptr()             { return fica_ptr; }
    
    /**
     * Informs that the controller is offline
     */
    inline void ctrl_offline()                  { ctrl_code_online = false; }

    /**
     * Informs that the controller is online
     */
    inline void ctrl_online()                   { ctrl_code_online = true; }
    
    
    /** 
     * Inform the device controller that we are dying
     */
    void suicide();
    
    /**
     * Inform the device controller that we now exist
     * param[in] ctrl_id controller id
     */
    void a_new_child(int32_t );
    
    /** 
     * The basic code to be executed in the always_executed_hook method of 
     * Pool based device
     * @param[in] motor boolean set to true if the device is a motor for which 
     *                  the limit switches (with ALARM state) has to be taken 
     *                  into account
     * @param[in] propagate if set to true the ghost group is informed of the
     *            state change
     */
    void base_always_executed_hook(bool motor, bool propagate = true);
    
    /** 
     * Read a single element state from the controller.
     * 
     * @param[in] sta  The structure used to pass object state
     * @param[in] lock A boolean set to true if the method must lock the
     *                 controller
     */
    void read_state_from_ctrl(Controller::CtrlState &,bool);
    
    /**
     * The base dev_status
     */
    void base_dev_status(Tango::ConstDevString);
    
    /**
     * Delete this object from the pool
     */
    virtual void delete_from_pool();
    
    /**
     * Initializes data of the PoolElement
     * @param[out] elem the pool element to be initialized
     */
    virtual void init_pool_element(PoolElement *);
    
    /**
     *	Read the device properties from database
     */
    virtual void get_device_property();
    
    /** 
     * Determines if this object should be in fault
     */
    bool should_be_in_fault();

    /**
     *	Initialize the device
     */
    virtual void init_device();
    
    /**
     *	will be called at device destruction or at init command.
     */
    virtual void delete_device();
    
    /**
     * @name Dynamic attributes
     */
    //@{
    
    /**
     * Create dynamic attributes
     */
    void create_dyn_attr();
    
    /**
     * Create one extra attribute
     * 
     * @param extra_attr Extra attribute information
     */
    void create_one_extra_attr(PoolExtraAttr &);
    
    /**
     * Remove unwanted dynamic attributes from the device
     */
    void remove_unwanted_dyn_attr_from_device();
    
    long ExtraAttrDataType_2_Tango(ExtraAttrDataType &);
    Tango::AttrWriteType ExtraAttrWriteType_2_Tango(ExtraAttrDataWrite &);
        
    map<string,bool>            bool_extra_data;
    map<string,Tango::DevLong>  long_extra_data;
    map<string,double>          double_extra_data;
    map<string,long>            string_extra_index;
    vector<string>              string_extra_data;
    Tango::DevString            string_extra_attr[MAX_EXTRA_ATTRIBUTES];
    long                        sf_index;
    
    bool is_ExtraAttr_allowed(Tango::AttReqType type);
    
    void read_Boo_R_Attr(Tango::Attribute &attr);
    void read_Boo_RW_Attr(Tango::Attribute &attr);
    void write_Boo_RW_Attr(Tango::WAttribute &attr);

    void read_Dou_R_Attr(Tango::Attribute &attr);
    void read_Dou_RW_Attr(Tango::Attribute &attr);
    void write_Dou_RW_Attr(Tango::WAttribute &attr);

    void read_Lo_R_Attr(Tango::Attribute &attr);
    void read_Lo_RW_Attr(Tango::Attribute &attr);
    void write_Lo_RW_Attr(Tango::WAttribute &attr);
    
    void read_Str_R_Attr(Tango::Attribute &attr);
    void read_Str_RW_Attr(Tango::Attribute &attr);
    void write_Str_RW_Attr(Tango::WAttribute &attr);
    
    vector<PoolExtraAttr> &get_extra_attributes();
    //@}
    
protected:

    /**
     * @name Properties
     */
    //@{
        
    /** The controller indentifier for this element */
    ElementId           ctrl_id;

    ElementId           instrument_id;
        
    /** index of this element in the controller */
    int32_t             axis;
    //@}
    
    bool                simulation_mode;
    
    CtrlFiCa 			*fica_ptr;
    
    bool				fica_built;
    bool				ctrl_code_online;
    bool				unknown_state;

//
// For commands, attribute
//
    std::string         ctrl_str;
    std::string         instrument_str;

    /**
     * Gets the pool controller
     * @return reference to the pool controller object
     */
    ControllerPool &get_ctrl();

    /**
     * Gets the controller name. Note that the return is a string copy. This is
     * because this accesses the ControllerPool object to get the name. The
     * controller can be changed at any time so we must protect ourselves from
     * this.
     * @return the controller name
     */
    std::string get_ctrl_name();
    
    virtual void inform_ghost(Tango::DevState,Tango::DevState) = 0;
};

}	// namespace_ns
