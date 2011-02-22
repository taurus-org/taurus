#ifndef _CPOOL_OBJECT_H_
#define _CPOOL_OBJECT_H_

#include "CPoolDefs.h"
#include <string>

namespace Pool_ns
{

class DevicePool;

struct PoolObject
{
    /** The pool of devices to which this element belongs */
    DevicePool*                 device_pool;

    /** Element identifier */
    ElementId                   id;

    /** Name of the element */
    std::string                 name;

    /** usually a tango device name, but can be anything else. */
    std::string                 full_name;

    /**
     * the full name
     * Generic string for elements:
     * [alias] '('[full_name]')' [class-of_device] [extra_info]
     */
    std::string                 user_full_name;

    /**
     * The default constructor
     */
    PoolObject();

    /**
     * Constructor
     *
     * @param dp the pool of devices to which this element will belong
     * @param identif the element ID
     * @param n the element name
     */
    PoolObject(DevicePool *, ElementId, const std::string &);

    /**
     * The destructor
     */
    virtual ~PoolObject();

    /**
     * Sets this element ID
     *
     * @param[in] id element ID
     */
    inline void set_id(ElementId id)
    { this->id = id; }

    /**
     * Gets the element ID
     *
     * @return the element ID
     */
    inline ElementId get_id() const
    { return this->id; }

    /**
     * Renames this element
     *
     * @param[in] name the new element name
     */
    inline void set_name(const std::string &name)
    { this->name = name; }

    /**
     * Gets the element name
     *
     * @return the element name
     */
    inline const std::string &get_name() const
    { return this->name; }

    /**
     * Renames this element (the full name)
     *
     * @param[in] full_name the new element full name
     */
    inline void set_full_name(const std::string &full_name)
    { this->full_name = full_name; }
    
    /**
     * Gets the element full name
     *
     * @return the element full name
     */
    inline const std::string &get_full_name() const
    { return this->full_name; }

    /**
     * Renames this element user name (the user full name)
     *
     * @param[in] user_full_name the new element user full name
     */
    inline void set_user_full_name(const std::string &user_full_name)
    { this->user_full_name = user_full_name; }

    /**
     * Gets the a user readble name
     *
     * @return the user readble name
     */
    inline const std::string &get_user_full_name() const
    { return this->user_full_name; }
    
    /**
     * Sets the device pool to which this element belongs
     *
     * @param[in] device_pool the pointer to the device pool
     */
    inline void set_device_pool(DevicePool *device_pool)
    { this->device_pool = device_pool; }

    /**
     * Gets the device pool pointer 
     *
     * @return the device pool pointer
     */    
    inline DevicePool *get_device_pool()
    { return this->device_pool; }
};

}

#endif
