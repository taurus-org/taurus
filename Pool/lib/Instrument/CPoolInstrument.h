#pragma once

#include "CPoolElement.h"

namespace Pool_ns
{

/**
 * The motor object
 */
struct InstrumentPool: public PoolElement
{
    /** instrument type */
    std::string             instrument_type;
    
    /** reference to the parent instrument. Should be NULL for root instruments */
    struct InstrumentPool*  parent_instrument;
    
    /** container for non instrument pool elements */
    ElemIdMap               pool_elements;
    
    /** container for child instruments */
    ElemIdMap               child_instruments;

    /**
     * Constructor
     *
     * @param dp the pool of devices to which this element will belong
     * @param type the instrument type
     * @param full_name the instrument full name
     * @param identif the element ID (optional, default is InvalidId meaning the
     *                element will ask for a new unassigned id to the pool
     */
    InstrumentPool(DevicePool *, const std::string &, const std::string &,
                   ElementId id = InvalidId);

    /**
     * Returns the type of element this object represents.
     * @see ElementType
     *
     * @return This element type
     */
    virtual ElementType get_type()
    { return INSTRUMENT_ELEM; }
    
    inline void set_parent_instrument(InstrumentPool *parent)
    { this->parent_instrument = parent; }

    inline InstrumentPool* get_parent_instrument() const
    { return parent_instrument; }
    
    inline bool has_parent_instrument() const
    { return get_parent_instrument() != NULL; }

    void add_element(ElementId id);
    
    inline void add_element(PoolElement *element)
    { this->pool_elements[element->get_id()] = element; }
    
    inline void remove_element(ElementId id)
    { this->pool_elements.erase(id); }
    
    inline void remove_element(PoolElement *element)
    { this->remove_element(element->get_id()); }
    
    void add_child(ElementId id);

    inline void add_child(InstrumentPool *child)
    { this->child_instruments[child->get_id()] = child; }
    
    inline void remove_child(ElementId id)
    { this->child_instruments.erase(id); }
    
    inline void remove_child(InstrumentPool *child)
    { this->remove_child(child->get_id()); }
    
    inline const ElemIdMap& get_pool_elements()
    { return pool_elements; }
    
    inline const ElemIdMap& get_child_instruments()
    { return child_instruments; }
    
};

} /* namespace Pool_ns */
