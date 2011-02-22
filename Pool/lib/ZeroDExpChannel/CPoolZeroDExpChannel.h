#pragma once

#include "CPoolSingleElement.h"

namespace Pool_ns
{

/**
 * 0D experiment channel element
 */
struct ZeroDExpChannelPool: public SinglePoolElement
{
    /**
     * Returns the type of element this object represents.
     * @see ElementType
     *
     * @return This element type
     */
    virtual ElementType get_type()
    { return ZEROD_ELEM; }

    /**
     * IPoolElementListener interface implementation. Called when an event
     * occurs.
     *
     * @param[in] evt stack of event data elements.
     */
    virtual void pool_elem_changed(PoolElemEventList &);
};

}

