#ifndef _CPOOL_H_
#define _CPOOL_H_

#include "CPoolElementContainer.h"
#include <map>
#include <vector>
#include <string>

namespace Pool_ns
{

struct ControllerPool;
struct PoolMoveable;
struct MotorPool;
struct PseudoMotorPool;
struct MotorGroupPool;
struct CTExpChannelPool;
struct ZeroDExpChannelPool;
struct OneDExpChannelPool;
struct TwoDExpChannelPool;
struct PseudoCounterPool;
struct MeasurementGroupPool;
struct CommunicationChannelPool;
struct IORegisterPool;
struct ConstraintPool;
struct InstrumentPool;

class CtrlFiCa;
class CtrlFile;

class DevicePool: public PoolElementContainer
{
protected:
    
    /** last id to be set */
    ElementId                           last_id;

    /** last ghost id to be set */
    ElementId                           last_ghost_id;

    /** last internal element id to be set */
    ElementId                           last_internal_id;
    
    /** Device pool version string */
    std::string                         pool_version_str;
    
    /** Device pool version number */
    int32_t                             pool_version_nb;
    
    /** list of all directories to search for controllers */
    std::vector<std::string>            ctrl_path;
    
    /** a pointer to the single DevicePool object that should exist */
    static DevicePool*                  singleton_instance;
    
public:

    /**
     * Constructor
     */
    DevicePool(PoolThrower *t = NULL);
    
    /**
     * The virtual desctructor
     */
    virtual ~DevicePool();
    
    /**
     * Gives a pointer to the single instance of DevicePool
     *
     * @return a pointer to the single instance of DevicePool
     */
    static DevicePool* get_instance()
    { return singleton_instance; }
    
    static CtrlType str_2_CtrlType(const std::string &);
    
    /**
     * Calculates and gives a new free device pool identifier 
     *
     * @return a new ID
     */
    inline ElementId get_new_id();

    /**
     * Returns the last device pool identifier that was assigned
     *
     * @return the last assigned ID
     */
    inline ElementId get_last_assigned_id();
    
    /**
     * Excludes the given id from the list of free device pool 
     * identifiers. The given id should belong to an existing device pool
     * element
     * 
     * @param[in] id the id to be locked
     */
    inline void reserve_id(ElementId id);

    /**
     * Calculates and gives a new free internal device pool identifier 
     *
     * @return a new ID
     */
    inline ElementId get_new_internal_id();

    /**
     * Returns the last internal device pool identifier that was assigned
     *
     * @return the last assigned ID
     */
    inline ElementId get_last_assigned_internal_id();
    
    /**
     * Excludes the given id from the list of free internal device pool 
     * identifiers. The given id should belong to an existing device pool
     * element
     * 
     * @param[in] id the id to be locked
     */
    inline void reserve_internal_id(ElementId id);

    /**
     * Calculates and gives a new free device pool ghost identifier 
     *
     * @return a new ghost ID
     */
    inline ElementId get_new_ghost_id();

    /**
     * Returns the last device pool ghost identifier that was assigned
     *
     * @return the last assigned ghost ID
     */
    inline ElementId get_last_assigned_ghost_id();
    
    /**
     * Excludes the given ghost id from the list of free device pool 
     * ghost identifiers. The given ghost id should belong to an existing
     * device pool element
     * 
     * @param[in] id the id to be locked
     */
    inline void reserve_ghost_id(ElementId id);
        
    /** 
     * Converts a string containing a version in format 'M.N.R' into a number
     * as M*10000 + N*100 + R
     */
    int32_t to_version_nb(const std::string &);

    /**
     * Gets the pool library version string
     *
     * @return the library version string
     */
    inline const std::string &get_version_str();
    
    /**
     * Gets the pool library version string
     *
     * @return the library version string
     */
    inline int32_t get_version_nb();

    /**
     * Returns the list of directories to search for plugins
     * 
     * @return a list of directories to search for plugins
     */
    virtual std::vector<std::string>& get_pool_path() = 0;

    /**
     * Receives a list of class properties. It returns the same list filled with
     * updated data at the instance level.
     *
     * @param[in] inst_name the instance name
     * @param[in] class_name the class name
     * @param[in] prop_pairs pairs of (property, value)
     * @param[in, out] prop_data a vector of properties containning information
     *                           about all properties at the class level. It
     *                           will be changed to contain updated information
     *                           at the instance level
     */
    virtual void build_property_data(const std::string &, const std::string &, 
                                     std::vector<std::pair<std::string, std::string> >&,
                                     std::vector<PropertyData*>&) = 0;
    /**
     * Gets the controller with the given ID. Throws exception if
     * no proper controller is found
     *
     * @param[in] id controller ID
     *
     * @return a reference to the controller
     */
    inline ControllerPool &get_controller(ElementId );

    /**
     * Gets the controller with the given name. Throws exception if
     * no proper controller is found
     *
     * @param[in] name controller name
     * @param[in] any_name if <code>false</code> (default) the search will only  
     *                      match elements with the same name (case 
     *                      insensitive). Otherwise all string attributes of the
     *                      element will be compared for a match
     *
     * @return a reference to the controller
     */
    inline ControllerPool &get_controller(const std::string &, 
                                          bool any_name = false);

    /**
     * Gets the controller for the given PoolElement. 
     *
     * @param[in] pe pool element
     *
     * @return a reference to the controller
     */
    inline ControllerPool &get_controller(PoolElement &);
    
    /**
     * Gets the controller for the element with the given ID. 
     *
     * Throws exception if no proper controller is found.
     *
     * @param[in] id element ID
     *
     * @return a reference to the controller
     */    
    inline ControllerPool &get_controller_from_element(ElementId );
    
    /**
     * Get how many controller used the Fica with name passed as parameter
     *
     * @param[in] fica_name controller class name
     *
     * @return number of controller instances for the given class name
     */    
    int32_t get_controller_nb_by_class_name(const std::string &);

    /**
     * Gets the motor object from its ID. Throws exception if no matching 
     * physical motor is found
     *
     * @param[in] mot_id motor ID
     *
     * @return a reference to the motor
     */
    inline MotorPool &get_physical_motor(ElementId ); 

    /**
     * Gets the motor object from its name. 
     
     *Throws exception if no matching physical motor is found
     *
     * @param[in] name motor name
     * @param[in] any_name if <code>false</code> (default) the search will only  
     *                      match elements with the same name (case 
     *                      insensitive). Otherwise all string attributes of the
     *                      element will be compared for a match
     *
     * @return a reference to the motor
     */
    inline MotorPool &get_physical_motor(const std::string &, 
                                         bool any_name = false); 

    inline PseudoMotorPool &get_pseudo_motor(ElementId );

    inline PseudoMotorPool &get_pseudo_motor(const std::string &,
                                             bool any_name = false);

    inline PoolElement &get_motor(ElementId );

    inline PoolElement &get_motor(const std::string &,
                                  bool any_name = false);
    
    inline MotorGroupPool &get_motor_group(ElementId );

    inline MotorGroupPool &get_motor_group(const std::string &, 
                                           bool any_name = false);

    inline CTExpChannelPool &get_countertimer(ElementId );

    inline CTExpChannelPool &get_countertimer(const std::string &,
                                              bool any_name = false);

    inline ZeroDExpChannelPool &get_zerod(ElementId );

    inline ZeroDExpChannelPool &get_zerod(const std::string &,
                                          bool any_name = false);

    inline OneDExpChannelPool &get_oned(ElementId );

    inline OneDExpChannelPool &get_oned(const std::string &,
                                        bool any_name = false);

    inline TwoDExpChannelPool &get_twod(ElementId );

    inline TwoDExpChannelPool &get_twod(const std::string &,
                                        bool any_name = false);
                                        
    inline PseudoCounterPool &get_pseudo_counter(ElementId );

    inline PseudoCounterPool &get_pseudo_counter(const std::string &,
                                                 bool any_name = false);

    inline PoolElement &get_experiment_channel(ElementId );
    
    inline PoolElement &get_experiment_channel(const std::string &,
                                               bool any_name = false);

    inline MeasurementGroupPool &get_measurement_group(ElementId );

    inline MeasurementGroupPool &get_measurement_group(const std::string &,
                                                       bool any_name = false);

    inline CommunicationChannelPool &get_communication_channel(ElementId );

    inline CommunicationChannelPool &get_communication_channel(const std::string &,
                                                               bool any_name = false);

    inline IORegisterPool &get_ioregister(ElementId );

    inline IORegisterPool &get_ioregister(const std::string &,
                                          bool any_name = false);

    inline InstrumentPool &get_instrument(ElementId );

    inline InstrumentPool &get_instrument(const std::string &,
                                          bool any_name = false);

    //inline ConstraintPool &get_constraint(ElementId );
    
    //inline ConstraintPool &get_constraint(const std::string &, bool any_name = false);

    inline PoolElement &get_physical_element(ElementId );
    
    inline PoolElement &get_physical_element(const std::string &,
                                             bool any_name = false);

    inline PoolElement &get_pseudo_element(ElementId );
    
    inline PoolElement &get_pseudo_element(const std::string &,
                                           bool any_name = false);

    inline PoolElement &get_group_element(ElementId );
    
    inline PoolElement &get_group_element(const std::string &, 
                                          bool any_name = false);
    
    inline PoolMoveable &get_moveable(ElementId );

    inline PoolMoveable &get_moveable(const std::string &, 
                                      bool any_name = false);

    inline void get_controllers(std::vector<ElementId> &);
    
    inline void get_controllers(std::vector<ControllerPool *> &);
    
    inline void get_controllers(std::vector<std::string> &);


    inline void get_physical_motors(std::vector<ElementId> &);
    
    inline void get_physical_motors(std::vector<MotorPool *> &);
    
    inline void get_physical_motors(std::vector<std::string> &);


    inline void get_all_controller(PoolElementTypeIt &, PoolElementTypeIt &);

    //inline void get_all_motor(PoolElementTypeIt &, PoolElementTypeIt &);

    inline void get_all_physical_motor(PoolElementTypeIt &, PoolElementTypeIt &); 

    inline void get_all_pseudo_motor(PoolElementTypeIt &, PoolElementTypeIt &);

    inline void get_all_motor_group(PoolElementTypeIt &, PoolElementTypeIt &);

    inline void get_all_countertimer(PoolElementTypeIt &, PoolElementTypeIt &);

    inline void get_all_zerod(PoolElementTypeIt &, PoolElementTypeIt &);

    inline void get_all_oned(PoolElementTypeIt &, PoolElementTypeIt &);
    
    inline void get_all_twod(PoolElementTypeIt &, PoolElementTypeIt &);

    inline void get_all_pseudo_counter(PoolElementTypeIt &, PoolElementTypeIt &);

    inline void get_all_measurement_group(PoolElementTypeIt &, PoolElementTypeIt &);

    inline void get_all_communication_channel(PoolElementTypeIt &, PoolElementTypeIt &);

    inline void get_all_ioregister(PoolElementTypeIt &, PoolElementTypeIt &);
    
    inline void get_all_instrument(PoolElementTypeIt &, PoolElementTypeIt &);
        
    //inline ConstraintPool &get_all_constraint(PoolElementTypeIt &, PoolElementTypeIt &);
        
    inline int32_t get_controller_nb();
    
    inline int32_t get_motor_nb();
    
    inline int32_t get_physical_motor_nb();
    
    inline int32_t get_pseudo_motor_nb();
    
    inline int32_t get_motor_group_nb();
    
    inline int32_t get_countertimer_nb();
    
    inline int32_t get_zerod_nb();
    
    inline int32_t get_oned_nb();
    
    inline int32_t get_twod_nb();
    
    inline int32_t get_pseudo_counter_nb();
    
    inline int32_t get_measurement_group_nb();
    
    inline int32_t get_communication_channel_nb();
    
    inline int32_t get_ioregister_nb();
    
    inline int32_t get_instrument_nb();
    
    //inline int32_t get_constraint_nb();

    inline bool controller_exists(const std::string &, bool any_name = false);
    
    inline bool physical_motor_exists(const std::string &, 
                                      bool any_name = false);
                                      
    inline bool pseudo_motor_exists(const std::string &, bool any_name = false);

    inline bool motor_exists(const std::string &, bool any_name = false);  
                                        
    inline bool motor_group_exists(const std::string &, bool any_name = false);

    /**
     * Check if a motor group with the given elements exists.
     *
     * @param[in]  elems list of motor ids
     * @param[out] name  name of the motor group that matches the description.
     *                   If no motor group exists, the string is unchanged
     *
     * @return <code>true</code> in case the element exists or
     *         <code>false</code> otherwise
     */
    bool motor_group_exists(std::vector<ElementId> &, std::string &);

    /**
     * Check if a motor group with the given elements exists.
     *
     * @param[in]  elems list of motor names
     * @param[out] name  name of the motor group that matches the description.
     *                   If no motor group exists, the string is unchanged
     *
     * @return <code>true</code> in case the element exists or
     *         <code>false</code> otherwise
     */
    bool motor_group_exists(std::vector<std::string> &, std::string &);
        
    inline bool countertimer_exists(const std::string &, 
                                    bool any_name = false);  
    
    inline bool zerod_exists(const std::string &, bool any_name = false);  

    inline bool oned_exists(const std::string &, bool any_name = false);
    
    inline bool twod_exists(const std::string &, bool any_name = false);  

    inline bool pseudo_counter_exists(const std::string &, 
                                      bool any_name = false);  

    /**
     * Check if a measurement group is defined in this pool from its name.
     * The name could be the alias or its tango name. The check is done first
     * by alias
     *
     * @param[in] name element name
     *
     * @return <code>true</code> in case the element exists or
     *         <code>false</code> otherwise
     */
    bool measurement_group_exists(std::vector<std::string> &, std::string &);  

    inline bool communication_channel_exists(const std::string &, 
                                             bool any_name = false);
    
    inline bool ioregister_exists(const std::string &, bool any_name = false);

    inline bool instrument_exists(const std::string &, bool any_name = false);
    
    inline void remove_controller(ElementId );
    
    inline void remove_physical_motor(ElementId );
    
    inline void remove_pseudo_motor(ElementId );
    
    inline void remove_motor_group(ElementId );
    
    inline void remove_countertimer(ElementId );
    
    inline void remove_zerod(ElementId );
    
    inline void remove_oned(ElementId );
    
    inline void remove_twod(ElementId );
    
    inline void remove_pseudo_counter(ElementId );
    
    inline void remove_measurement_group(ElementId );
    
    inline void remove_communication_channel(ElementId );
    
    inline void remove_ioregister(ElementId );
    
    
    inline void remove_controllers();
    
    inline void remove_physical_motors();
    
    inline void remove_pseudo_motors();
    
    inline void remove_motor_groups();
    
    inline void remove_countertimers();
    
    inline void remove_zerods();
    
    inline void remove_oneds();
    
    inline void remove_twods();
    
    inline void remove_pseudo_counters();
    
    inline void remove_measurement_groups();
    
    inline void remove_communication_channels();
    
    inline void remove_ioregisters();

    inline bool is_physical_element(ElementId );

    /**
     * Gets the motor groups which contain the given element.
     *
     * @param[in]  elem_id  element id
     * @param[out] mgs      list of motor group ids that contain the given
     *                       element
     * @return <code>true</code> if there is at least one matching motor group or
     *         <code>false</code> otherwise
     */
    bool get_motor_groups_containing_elt(ElementId, ElemIdVector &);

    /**
     * Gets the motor groups which contain the given element.
     *
     * @param[in]  elem_id  element id
     * @param[out] mgs      list of motor group names that contain the given
     *                       element
     * @return <code>true</code> if there is at least one matching motor group or
     *         <code>false</code> otherwise
     */
    bool get_motor_groups_containing_elt(ElementId, std::vector<std::string> &);
    
    /**
     * Gets the motor groups which contain the given element.
     *
     * @param[in]  elt_name element name
     * @param[out] mgs      list of motor group names that contain the given
     *                      element
     * @return <code>true</code> if there is at least one matching motor group or
     *         <code>false</code> otherwise
     */
    bool get_motor_groups_containing_elt(std::string &, std::vector<std::string> &);

    /**
     * Gets the motor groups which contain the given element.
     *
     * @param[in]  elem_id  element id
     * @param[out] mgs      list of motor groups that contain the given
     *                      element
     * @return <code>true</code> if there is at least one matching motor group or
     *         <code>false</code> otherwise
     */
    bool get_motor_groups_containing_elt(ElementId, std::vector<MotorGroupPool*> &);

    /**
     * Gets the motor groups which contain the given element.
     *
     * @param[in]  elt_name element name
     * @param[out] mgs      list of motor groups that contain the given
     *                      element
     * @return <code>true</code> if there is at least one matching motor group or
     *         <code>false</code> otherwise
     */
    bool get_motor_groups_containing_elt(std::string &, std::vector<MotorGroupPool*> &);

    /**
     * Gets the measurement groups that contains the given experiment channel.
     *
     * @param[in]  elem_id experiment channel id
     * @param[out] mgs     list of matching measurement group ids
     *
     * @return <code>true</code> if there is at least one matching measurement
     *         group or <code>false</code> otherwise
     */
    bool get_measurement_groups_containing_elt(ElementId, ElemIdVector &mgs);
    
    /**
     * Gets the measurement groups that contains the given experiment channel.
     *
     * @param[in]  elem_id experiment channel id
     * @param[out] mgs     list of matching measurement group names
     *
     * @return <code>true</code> if there is at least one matching measurement
     *         group or <code>false</code> otherwise
     */
    bool get_measurement_groups_containing_elt(ElementId, std::vector<std::string> &);
    
    /**
     * Gets the measurement groups that contains the given experiment channel.
     *
     * @param[in]  ch_name experiment channel name
     * @param[out] mgs     list of matching measurement group names
     *
     * @return <code>true</code> if there is at least one matching measurement
     *         group or <code>false</code> otherwise
     */
    bool get_measurement_groups_containing_elt(std::string &, std::vector<std::string> &);

    /**
     * Gets the measurement groups that contains the given experiment channel.
     *
     * @param[in]  ch_name experiment channel name
     * @param[out] mgs     list of matching measurement group pointers
     *
     * @return <code>true</code> if there is at least one matching measurement
     *         group or <code>false</code> otherwise
     */
    bool get_measurement_groups_containing_elt(std::string &, 
                                               std::vector<MeasurementGroupPool*> &);

    /**
     * Helper method. Translate between a string representation of a controller
     * type to an enumerated
     *
     * @param[in] type string representing the controller type
     *
     * @return the controller type corresponding to the given string
     */
    static CtrlType str_2_CtrlType(std::string &);
    
    /**
     * Helper method. Builds a list of files with the given extension that are
     * present inside the given directory
     *
     * @param[in]  dir   the directory to be inspected
     * @param[in]  f_ext the file extension
     * @param[out] lst   the vector which will contain the list of files that
     *                   match the given extension in the given directory
     */
    static void get_files_with_extension(std::string &, const char *,
                                         std::vector<std::string> &);
    
protected:
    
    /**
     * Adds a new instrument
     *
     * @param[in] name the instrument full name
     * @param[in] id the element id (optional, default is InvalidId meaning a new
                   id will be reserved for it)
     *
     * @return a pointer to the new Pool instrument
     */
    virtual InstrumentPool *add_instrument(const std::string &, 
                                           const std::string &,
                                           ElementId id = InvalidId);
    
    
private:
    
    /**
     * Gets the controller from its instance name. Throws exception if
     * no proper controller is found
     *
     * @param[in] inst_name controller instance name
     *
     * @return a reference to the controller
     */
    ControllerPool &_get_controller_from_inst_name(const std::string &);
};

}

#include <CPool.inl>

#endif  //_CPOOL_H_
